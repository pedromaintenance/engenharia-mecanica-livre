"""Ciclo 21: sweep geométrico ANTES da resolução FEM.

Varia posição da interface alinhada, usa Gmsh real, checa duas interfaces
Q8 conformes e compara a qualidade com o dataset verificável do ciclo 20.
O seletor é piloto de amostragem discreta, não otimizador certificado.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

from engmec.elmer_chapa import geo_elmer
from engmec.gmsh_chapa import importar_msh2
from engmec.multibloco_externo import verificar_seis_blocos
from engmec.convergencia_malha import qualidade_geometrica

FRACOES = (.45, .50, .55, .60, .65, .70, .75)
GEOMETRIAS = ((4, 2), (4, 4), (8, 2), (8, 4))


def varrer(root: str | Path) -> dict:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    prior = json.loads(Path("docs/dados/ciclo20-transicao-externa-2026-11-10.json")
                       .read_text(encoding="utf-8"))
    baseline = {(int(s["d_over_W"] ** -1), int(s["L_over_W"])): s
                for s in prior["series"]}
    if len(baseline) != 4:
        raise ValueError("Baseline geométrica de 4 séries ausente")
    candidates = []
    for alpha in FRACOES:
        cases = []
        for ha, lw in GEOMETRIAS:
            H, L = .01 * ha, .01 * ha * lw
            path = root / f"lambda-{alpha:.2f}" / f"ha-{ha}-lw-{lw}"
            path.mkdir(parents=True, exist_ok=True)
            (path / "model.geo").write_text(geo_elmer(
                nr=48, nt=96, H=H, L=L, a=.01,
                estrategia_progressao="escalonada",
                topologia="anel-seis-blocos-alinhado",
                fracao_interface=alpha), encoding="utf-8")
            cmd = ["gmsh", "model.geo", "-2", "-order", "2", "-format", "msh2",
                   "-o", "model.msh"]
            p = subprocess.run(cmd, cwd=path, capture_output=True,
                               text=True, timeout=150)
            (path / "gmsh.log").write_text(p.stdout + "\n" + p.stderr,
                                          encoding="utf-8")
            if p.returncode:
                raise RuntimeError(f"Gmsh lambda={alpha} ha={ha} lw={lw}: {p.stderr[-1600:]}")
            msh = (path / "model.msh").read_bytes()
            mesh = importar_msh2(msh.decode("utf-8"),
                                 a=.01, H=H, Hx=L, nr=48, nt=96)
            conform = verificar_seis_blocos(
                mesh, a=.01, Hy=H, Hx=L, nr=48, nt=96,
                modo_interface="alinhada", fracao_interface=alpha)
            q = qualidade_geometrica(path / "model.msh", a=.01, H=H,
                                    L=L, nr=48, nt=96)
            if q["elementos"] != 4608 or conform["interface_retangular_arestas_conformes"] != 96:
                raise ValueError("Contagem CAD inválida")
            if q["jacobianos_q8"]["min_det_jacobiano_m2"] <= 0:
                raise ValueError("Jacobiano não positivo")
            old = baseline[(ha, lw)]
            relative_ratio = q["razão_max_min_cordas_geral_max"] / old["pior_ratio_global_novo"]
            relative_angle = old["menor_angulo_novo"] / q["angulo_minimo_vertices_graus_geral"]
            cases.append({
                "H_over_a": ha, "L_over_W": lw,
                "fracao_interface": alpha,
                "sha256_msh2": hashlib.sha256(msh).hexdigest(),
                "quality": q, "conformidade": conform,
                "ratio_vs_ciclo20": relative_ratio,
                "angle_penalty_vs_ciclo20": relative_angle,
                "melhora_ratio": relative_ratio < 1.,
                "melhora_angulo": relative_angle < 1.,
            })
        worst = max(max(c["ratio_vs_ciclo20"], c["angle_penalty_vs_ciclo20"])
                    for c in cases)
        mean = sum(c["ratio_vs_ciclo20"] + c["angle_penalty_vs_ciclo20"]
                   for c in cases) / (2 * len(cases))
        candidates.append({
            "fracao_interface": alpha, "cases": cases,
            "pontuacao_minimax": worst,
            "pontuacao_media": mean,
            "passa_ambos_4_em_4": all(
                c["melhora_ratio"] and c["melhora_angulo"] for c in cases),
        })
    best = min(candidates, key=lambda c: (
        c["pontuacao_minimax"], c["pontuacao_media"], c["fracao_interface"]))
    result = {
        "ciclo": 21, "kind": "CAD sweep before FEM",
        "geometrias": 4, "fracoes": list(FRACOES), "n_por_caso": 48,
        "numero_malhas": len(FRACOES) * len(GEOMETRIAS),
        "criterio": "minimax: max(ratio_novo/ratio20, angulo20/angulo_novo) nas 4 chapas; desempate média",
        "referencia": "docs/dados/ciclo20-transicao-externa-2026-11-10.json",
        "fracao_escolhida": best["fracao_interface"],
        "gate_geom_ambos_4_em_4": best["passa_ambos_4_em_4"],
        "candidatos": candidates,
        "alerta": "Se o gate for falso, a escolha só dirige ensaio FEM; NÃO aprova geometria",
    }
    (root / "varredura.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "escolha.json").write_text(
        json.dumps({"fracao_interface": best["fracao_interface"],
                    "gate_geom_ambos_4_em_4": best["passa_ambos_4_em_4"],
                    "pontuacao_minimax": best["pontuacao_minimax"]},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "fracao_escolhida": best["fracao_interface"],
        "gate_geom_ambos_4_em_4": best["passa_ambos_4_em_4"],
        "candidatos": [{
            "fracao": c["fracao_interface"],
            "max": c["pontuacao_minimax"],
            "media": c["pontuacao_media"],
            "gates": c["passa_ambos_4_em_4"]
        } for c in candidates]}, indent=2))
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--pasta", required=True)
    args = p.parse_args()
    varrer(args.pasta)
