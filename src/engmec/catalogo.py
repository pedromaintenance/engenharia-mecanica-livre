"""Catálogo de metadados verificáveis; não contém materiais protegidos."""
from __future__ import annotations

from datetime import date
from importlib.resources import files
import json
import re
import unicodedata


def carregar() -> dict:
    return json.loads(files("engmec").joinpath("data/fontes.json").read_text(encoding="utf-8"))


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c)).casefold()


def validar(dados: dict | None = None) -> list[str]:
    """Validar campos e regras locais sem dependências de terceiros."""
    dados = dados if dados is not None else carregar()
    erros: list[str] = []
    if not isinstance(dados, dict) or not isinstance(dados.get("fontes"), list):
        return ["Catálogo precisa ser um objeto com array 'fontes'"]
    ids = set()
    obrigatorios = {
        "id", "titulo", "organizacao", "url", "dominios", "tipo", "idioma",
        "acesso", "licenca", "redistribuicao", "nota_licenca", "verificado_em", "status"
    }
    tipos = {"curso", "livro", "pesquisa", "base-dados", "repositorio", "software", "regulacao", "padrao"}
    for i, fonte in enumerate(dados["fontes"]):
        tag = f"fonte[{i}]"
        if not isinstance(fonte, dict):
            erros.append(f"{tag}: objeto esperado")
            continue
        faltando = obrigatorios - set(fonte)
        if faltando:
            erros.append(f"{tag}: campos ausentes {sorted(faltando)}")
            continue
        sid = fonte["id"]
        if not isinstance(sid, str) or not re.fullmatch(r"[a-z0-9-]+", sid):
            erros.append(f"{tag}: ID inválido")
        if sid in ids:
            erros.append(f"{tag}: ID repetido {sid}")
        ids.add(sid)
        if not isinstance(fonte["url"], str) or not fonte["url"].startswith("https://"):
            erros.append(f"{tag}: URL deve começar com https://")
        if fonte["tipo"] not in tipos:
            erros.append(f"{tag}: tipo não reconhecido")
        if fonte["acesso"] not in ("aberto", "misto", "restrito"):
            erros.append(f"{tag}: acesso inválido")
        if fonte["redistribuicao"] not in ("somente-link", "avaliar-item", "permitido-com-atribuicao"):
            erros.append(f"{tag}: redistribuição inválida")
        if fonte["status"] not in ("catalogado", "auditado", "suspenso"):
            erros.append(f"{tag}: status inválido")
        if not isinstance(fonte["dominios"], list) or not fonte["dominios"] or not all(isinstance(x, str) and x for x in fonte["dominios"]):
            erros.append(f"{tag}: domínios inválidos")
        try:
            date.fromisoformat(fonte["verificado_em"])
        except (TypeError, ValueError):
            erros.append(f"{tag}: data inválida")
        if fonte["acesso"] == "restrito" and fonte["redistribuicao"] != "somente-link":
            erros.append(f"{tag}: restrito não deve ter material para redistribuição")
    return erros


def buscar(consulta: str = "", dominio: str = "", tipo: str = "") -> list[dict]:
    dados = carregar()["fontes"]
    termos = [_normalizar(t) for t in consulta.split() if t.strip()]
    resultados = []
    for item in dados:
        texto = _normalizar(" ".join([
            item["titulo"], item["organizacao"], item["id"],
            " ".join(item["dominios"]), item["tipo"], item["idioma"]
        ]))
        if termos and not all(termo in texto for termo in termos):
            continue
        if dominio and _normalizar(dominio) not in _normalizar(" ".join(item["dominios"])):
            continue
        if tipo and item["tipo"] != tipo:
            continue
        resultados.append(item)
    return resultados
