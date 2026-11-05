"""Avaliar quantitativamente a convergência do caso de flexão pura 3D."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path


def avaliar(pasta: str | Path, malhas: list[int]) -> dict:
    if len(malhas) < 3 or sorted(set(malhas)) != malhas:
        raise ValueError("Fornecer ao menos três malhas distintas e crescentes")
    data=[]
    for n in malhas:
        p=Path(pasta)/f"n-{n}"/"comparacao.json"
        case=json.loads(p.read_text(encoding="utf-8"))
        x=case["resultado"]
        row={
            "n":n, "elementos":case["entrada"]["elementos"],
            "uy_m":x["uy_centro_ponta_m"],"ux_m":x["ux_borda_ponta_m"],
            "erro_uy":x["erro_uy_rel"], "erro_ux":x["erro_ux_rel"],
            "residuo_forca_rel":x["reacao_norm_max_rel"],
        }
        if any(not math.isfinite(float(v)) for v in row.values()):
            raise ValueError(f"Saída não finita em malha {n}")
        data.append(row)
    results={"modelo":"flexao_pura_3d_convergencia",
             "referencia":"solucao exata da elasticidade isotropica com sigma_xx(y) linear",
             "malhas":data,
             "taxas_uy":[],
             "taxas_ux":[]}
    for field in ("uy","ux"):
        for a,b in zip(data,data[1:]):
            ea,eb=a["erro_"+field],b["erro_"+field]
            if ea > 0 and eb > 0:
                results["taxas_"+field].append(math.log(ea/eb)/math.log(b["n"]/a["n"]))
            else:
                results["taxas_"+field].append(None)
    # Prova mínima de refinamento informativo: erros mensuráveis e malha final
    # significativamente melhor que a inicial. Não exigir monotonicidade estrita
    # quando arredondamento da saída e efeitos de travamento estiverem presentes.
    for field in ("uy","ux"):
        valores=[m["erro_"+field] for m in data]
        if valores[0] < 1e-5:
            raise ValueError(f"Erro inicial de {field} trivial; selecione outro benchmark")
        if valores[-1] >= 0.75 * valores[0]:
            raise ValueError(f"Sem redução >=25% no erro de {field}")
    if max(x["residuo_forca_rel"] for x in data)>0.01:
        raise ValueError("Resíduo relativo de força acima de 1%")
    results["aceite"]={
        "erro_nao_trivial_inicial":True,
        "melhora_relativa_minima_25pct":True,
        "equilibrio_1pct":True,
        "nao_e_validacao_experimental":True,
    }
    return results


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pasta",required=True)
    p.add_argument("--malhas",type=int,nargs="+",required=True)
    args=p.parse_args()
    relatorio=avaliar(args.pasta,args.malhas)
    destino=Path(args.pasta)/"resumo_convergencia.json"
    destino.write_text(json.dumps(relatorio,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(relatorio,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
