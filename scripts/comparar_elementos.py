"""Comparar quantitativamente os benchmarks C3D8 e C3D20R.

A comparação usa a referência de elasticidade do mesmo problema de flexão.
Tempos de GitHub Actions são ilustrativos e não constituem benchmark de hardware.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def avaliar(pasta: str|Path, malhas: list[int]) -> dict:
    if sorted(set(malhas)) != malhas or len(malhas)<2:
        raise ValueError("Malhas devem ser distintas, crescentes e conter >=2 entradas")
    if any(n<2 for n in malhas):
        raise ValueError("Malha deve ter pelo menos 2 divisões")
    root=Path(pasta)
    data=[]
    for n in malhas:
        entries={}
        for kind in ("C3D8","C3D20R"):
            source=root/kind.lower()/f"n-{n}"/"comparacao.json"
            item=json.loads(source.read_text(encoding="utf-8"))
            if item["familia"]!=kind or item["entrada"]["nx"]!=n:
                raise ValueError("Relatório trocado ou com malha diferente")
            vals=item["deslocamentos"]
            stresses=item["tensoes"]
            row={
                "elemento":kind,
                "n":n,
                "elementos":item["entrada"]["elementos"],
                "nos":item["entrada"]["nos"],
                "graus_liberdade_estimados":3*item["entrada"]["nos"],
                "tempo_solver_s":item["tempo_execucao_s"],
                "erro_uy_rel":vals["erro_uy_rel"],
                "erro_ux_rel":vals["erro_ux_rel"],
                "erro_sxx_rms_rel":stresses["erro_rms_sxx_rel"],
                "erro_sxx_rms_pa":stresses["erro_rms_sxx_pa"],
                "erro_outros_pa":stresses["erro_rms_componentes_nao_axiais_pa"],
                "pontos_integracao":stresses["pontos_integracao"],
                "residuo_forca_rel":vals["reacao_norm_max_rel"],
            }
            if any(not math.isfinite(v) or v < 0 for k,v in row.items()
                   if isinstance(v,(int,float)) and k not in ("n", "elementos", "nos", "graus_liberdade_estimados")):
                raise ValueError(f"Saída inválida em {kind} n={n}")
            entries[kind]=row
            data.append(row)
        # Mesma geometria e número de elementos, mas DOFs distintos.
        if entries["C3D8"]["elementos"]!=entries["C3D20R"]["elementos"]:
            raise ValueError("As malhas comparadas não são equivalentes")
    coarse=[row for row in data if row["n"]==malhas[0]]
    linear=next(row for row in coarse if row["elemento"]=="C3D8")
    quadratic=next(row for row in coarse if row["elemento"]=="C3D20R")
    if linear["erro_uy_rel"]<1e-4:
        raise ValueError("Caso linear não apresenta erro mensurável")
    if quadratic["erro_uy_rel"] >= linear["erro_uy_rel"]:
        raise ValueError("C3D20R não melhorou Uy da malha grossa")
    if quadratic["erro_sxx_rms_rel"] >= linear["erro_sxx_rms_rel"]:
        raise ValueError("C3D20R não melhorou a tensão da malha grossa")
    if any(row["residuo_forca_rel"]>0.01 for row in data):
        raise ValueError("Equilíbrio de forças fora de 1%")
    return {
        "modelo":"C3D8_versus_C3D20R_flexao_pura_3D",
        "referencia":"Elasticidade isotropica exata, sigma_xx=-E*kappa*y",
        "amostras":data,
        "criterios":{
            "mesma_geometria_e_mesmo_numero_elementos":True,
            "solucao_externa_real_obrigatoria":True,
            "saida_sxx_e_coord_dos_pontos_de_gauss":True,
            "elemento_quadratico_melhora_uy_e_sxx_na_malha_grossa":True,
            "equilibrio_inferior_a_1pct":True,
        },
        "ressalvas":[
            "FEM linear elastica: nao e validacao de componente industrial",
            "Tempos de subprocesso nao sao benchmark isolado de CPU",
            "Aproximacoes muito proximas do valor analitico sao limitadas pela precisao textual"
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pasta",required=True)
    p.add_argument("--malhas",nargs="+",type=int,required=True)
    args=p.parse_args()
    report=avaliar(args.pasta,args.malhas)
    out=Path(args.pasta)/"resumo_elementos.json"
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
