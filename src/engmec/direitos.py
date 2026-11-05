"""Auditoria documental de direitos por obra; nenhum conteúdo externo é importado."""
from __future__ import annotations
from importlib.resources import files
from datetime import date
import json


def carregar() -> dict:
    return json.loads(files("engmec").joinpath("data", "direitos.json").read_text(encoding="utf-8"))


def validar() -> list[str]:
    doc = carregar()
    erros: list[str] = []
    registros = doc.get("records")
    if not isinstance(registros, list):
        return ["direitos: records deve ser lista"]
    ids = set()
    campos = {"id","title","url","license","license_evidence_url",
              "audit_level","permitted_repository_use","conditions",
              "known_limitations","reviewed_at","review_status"}
    for i, item in enumerate(registros):
        tag = f"direitos[{i}]"
        if not isinstance(item, dict):
            erros.append(f"{tag}: objeto esperado")
            continue
        faltando = campos - item.keys()
        if faltando:
            erros.append(f"{tag}: faltando {sorted(faltando)}")
            continue
        if item["id"] in ids:
            erros.append(f"{tag}: ID duplicado")
        ids.add(item["id"])
        if any(not str(item[key]).startswith("https://") for key in ("url", "license_evidence_url")):
            erros.append(f"{tag}: URL inválida")
        if item["audit_level"] not in ("politica-geral-verificada","obra-licenca-verificada"):
            erros.append(f"{tag}: nível de auditoria inválido")
        if not str(item["permitted_repository_use"]).startswith("L0"):
            erros.append(f"{tag}: uso além de L0 sem autorização")
        try:
            date.fromisoformat(item["reviewed_at"])
        except (TypeError, ValueError):
            erros.append(f"{tag}: data inválida")
    return erros
