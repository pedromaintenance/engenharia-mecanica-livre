"""Catálogos versionados de cursos, portais e ferramentas — apenas metadados."""
from __future__ import annotations

from datetime import date
from importlib.resources import files
import json
import re
import unicodedata


TIPOS = ("cursos", "portais", "ferramentas")
CAMPOS = {
    "cursos": {"id", "title", "provider", "url", "domain", "level", "prerequisites", "license_policy", "status", "checked_at"},
    "portais": {"id", "title", "provider", "url", "category", "description", "rights", "status", "checked_at"},
    "ferramentas": {"id", "title", "url", "area", "mode", "use", "license", "integration_status", "checked_at"},
}


def carregar(tipo: str) -> dict:
    if tipo not in TIPOS:
        raise ValueError("tipo deve ser cursos, portais ou ferramentas")
    return json.loads(files("engmec").joinpath("data", f"{tipo}.json").read_text(encoding="utf-8"))


def _normalizar(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in s if not unicodedata.combining(c)).casefold()


def contagem() -> dict[str, int]:
    return {tipo: len(carregar(tipo)["records"]) for tipo in TIPOS}


def validar() -> list[str]:
    erros = []
    ids = set()
    cursos = []
    for tipo in TIPOS:
        try:
            doc = carregar(tipo)
        except (OSError, json.JSONDecodeError) as exc:
            erros.append(f"{tipo}: erro ao carregar: {exc}")
            continue
        if doc.get("type") not in ("curso", "portal", "ferramenta"):
            erros.append(f"{tipo}: tipo do catálogo inválido")
        registros = doc.get("records")
        if not isinstance(registros, list):
            erros.append(f"{tipo}: records não é lista")
            continue
        for i, rec in enumerate(registros):
            tag = f"{tipo}[{i}]"
            if not isinstance(rec, dict):
                erros.append(f"{tag}: objeto esperado")
                continue
            faltando = CAMPOS[tipo] - rec.keys()
            if faltando:
                erros.append(f"{tag}: campos ausentes {sorted(faltando)}")
                continue
            rid = rec["id"]
            if not isinstance(rid, str) or not re.fullmatch(r"[a-z0-9-]+", rid):
                erros.append(f"{tag}: id inválido")
            if rid in ids:
                erros.append(f"{tag}: id duplicado: {rid}")
            ids.add(rid)
            if not isinstance(rec["url"], str) or not rec["url"].startswith("https://"):
                erros.append(f"{tag}: URL deve ser https")
            try:
                date.fromisoformat(rec["checked_at"])
            except (ValueError, TypeError):
                erros.append(f"{tag}: data inválida")
            if tipo == "cursos":
                cursos.append(rec)
                if not isinstance(rec["prerequisites"], list):
                    erros.append(f"{tag}: prerequisites inválido")
    course_ids = {rec["id"] for rec in cursos}
    graph = {}
    for rec in cursos:
        pre = rec["prerequisites"]
        if isinstance(pre, list):
            graph[rec["id"]] = pre
            for dependency in pre:
                if dependency not in course_ids:
                    erros.append(f"{rec['id']}: pré-requisito desconhecido {dependency}")
                if dependency == rec["id"]:
                    erros.append(f"{rec['id']}: autorreferência")
    # Arestas cíclicas não definem um currículo válido.
    def visitar(no: str, visitando: set[str], visitados: set[str]) -> None:
        if no in visitando:
            erros.append(f"grafo: ciclo detectado em {no}")
            return
        if no in visitados:
            return
        visitando.add(no)
        for dep in graph.get(no, []):
            if dep in graph:
                visitar(dep, visitando, visitados)
        visitando.remove(no)
        visitados.add(no)
    visitados: set[str] = set()
    for no in graph:
        if no not in visitados:
            visitar(no, set(), visitados)
    return erros


def buscar(tipo: str = "todos", consulta: str = "", area: str = "", nivel: str = "") -> list[dict]:
    if tipo not in ("todos", *TIPOS):
        raise ValueError("tipo não reconhecido")
    termos = [_normalizar(t) for t in consulta.split()]
    retorno = []
    for nome in (TIPOS if tipo == "todos" else (tipo,)):
        for rec in carregar(nome)["records"]:
            texto = _normalizar(" ".join(str(rec.get(k, "")) for k in
                ("title", "provider", "id", "area", "domain", "category", "description", "use")))
            if termos and not all(termo in texto for termo in termos):
                continue
            campo_area = _normalizar(rec.get("area", rec.get("domain", rec.get("category", ""))))
            if area and _normalizar(area) not in campo_area:
                continue
            if nivel and _normalizar(nivel) != _normalizar(rec.get("level", "")):
                continue
            retorno.append({"tipo_catalogo": nome, **rec})
    return retorno
