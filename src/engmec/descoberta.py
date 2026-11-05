"""Descoberta **somente de metadados** a partir de APIs oficiais.

Esta camada não lê documentos integrais, não indexa abstracts protegidos nem
promove candidatos automaticamente para conteúdo aceito.
"""
from __future__ import annotations

from datetime import date
from hashlib import sha256
from html import unescape
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
import time


AGENTES = {
    "crossref": "https://api.crossref.org/works",
    "openalex": "https://api.openalex.org/works",
}


def montar_url(fonte: str, consulta: str, limite: int = 5, email: str | None = None,
               api_key: str | None = None) -> str:
    if fonte not in AGENTES:
        raise ValueError("Fonte inválida; use crossref ou openalex")
    if not isinstance(consulta, str) or len(consulta.strip()) < 3:
        raise ValueError("Informe consulta de ao menos 3 caracteres")
    if not isinstance(limite, int) or not 1 <= limite <= 20:
        raise ValueError("Limite deve estar entre 1 e 20")
    if email and ("@" not in email or any(ch.isspace() for ch in email)):
        raise ValueError("E-mail de contato inválido")
    if fonte == "crossref":
        params = {"query": consulta.strip(), "rows": limite}
        if email:
            params["mailto"] = email
    else:
        params = {"search": consulta.strip(), "per_page": limite}
        if api_key:
            params["api_key"] = api_key
    return AGENTES[fonte] + "?" + urlencode(params)


def obter_json(url: str, tentativas: int = 3) -> dict:
    """GET controlado: timeouts, backoff em 429/5xx e identificação do projeto."""
    if urlparse(url).hostname not in ("api.crossref.org", "api.openalex.org"):
        raise ValueError("Host de API não permitido")
    request = Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "EngenhariaMecanicaLivre/0.2 (https://github.com/pedromaintenance/engenharia-mecanica-livre)"
    })
    for attempt in range(tentativas):
        try:
            with urlopen(request, timeout=18) as res:
                return json.load(res)
        except HTTPError as err:
            if err.code not in (429, 500, 502, 503, 504) or attempt == tentativas - 1:
                raise
            retry_after = err.headers.get("Retry-After", "")
            espera = min(10, int(retry_after)) if retry_after.isdigit() else min(8, 2 ** attempt)
            time.sleep(espera)
        except URLError:
            if attempt == tentativas - 1:
                raise
            time.sleep(min(8, 2 ** attempt))
    raise RuntimeError("Sem resposta da API")


def _texto(valor: object) -> str:
    if isinstance(valor, list):
        valor = valor[0] if valor else ""
    return " ".join(unescape(str(valor or "")).split())[:500]


def _candidato(fonte: str, titulo: str, url: str, doi: str | None, ano: object,
               autores: list[str]) -> dict | None:
    titulo = _texto(titulo)
    doi = str(doi or "").strip().lower().removeprefix("https://doi.org/")
    if doi.startswith("http://doi.org/"):
        doi = doi[len("http://doi.org/"):]
    if doi.startswith("10.") and "/" in doi:
        url = f"https://doi.org/{doi}"
    else:
        doi = None
    if not titulo or not isinstance(url, str) or not url.startswith("https://"):
        return None
    chave = (doi or url).casefold()
    return {
        "id": "candidato-" + sha256(chave.encode()).hexdigest()[:14],
        "title": titulo,
        "url": url,
        "doi": doi,
        "year": ano if isinstance(ano, int) and 1500 <= ano <= 2200 else None,
        "authors": [str(a)[:120] for a in autores[:10] if a],
        "source_api": fonte,
        "status": "candidato-nao-auditado",
        "rights": "Somente metadados; conferir obra individual antes de reutilizar conteúdo."
    }


def normalizar_crossref(payload: dict) -> list[dict]:
    retorno = []
    for item in payload.get("message", {}).get("items", []):
        doi = item.get("DOI")
        authors = [(" ".join([a.get("given", ""), a.get("family", "")])).strip()
                   for a in item.get("author", []) if isinstance(a, dict)]
        partes = item.get("published", {}).get("date-parts", [[]])
        ano = partes[0][0] if partes and partes[0] else None
        rec = _candidato("crossref", item.get("title", []), item.get("URL", ""),
                         doi, ano, authors)
        if rec:
            retorno.append(rec)
    return retorno


def normalizar_openalex(payload: dict) -> list[dict]:
    retorno = []
    for item in payload.get("results", []):
        authors = [a.get("author", {}).get("display_name", "") for a in
                   item.get("authorships", []) if isinstance(a, dict)]
        url = item.get("doi") or item.get("id") or ""
        # DOI preferido; URL oficial de obra quando DOI ausente.
        location = item.get("primary_location") or {}
        if not url.startswith("https://"):
            url = location.get("landing_page_url") or ""
        rec = _candidato("openalex", item.get("title", ""), url, item.get("doi"),
                         item.get("publication_year"), authors)
        if rec:
            retorno.append(rec)
    return retorno


def descobrir(fonte: str, consulta: str, limite: int = 5, email: str | None = None,
              fetcher=None) -> dict:
    """Consulta pequena e manual; resultado é fila de revisão, não acervo publicado."""
    url = montar_url(fonte, consulta, limite, email, os.getenv("OPENALEX_API_KEY"))
    resposta = (fetcher or obter_json)(url)
    itens = normalizar_crossref(resposta) if fonte == "crossref" else normalizar_openalex(resposta)
    ids = set()
    unicos = []
    for item in itens:
        if item["id"] not in ids:
            ids.add(item["id"])
            unicos.append(item)
    return {
        "schema_version": "0.1.0",
        "fetched_at": date.today().isoformat(),
        "source": fonte,
        "query": consulta,
        "count": len(unicos),
        "review_required": True,
        "records": unicos,
    }
