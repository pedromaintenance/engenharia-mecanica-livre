"""Analisa os resultados independentes Elmer x FEM Q8 autoral no mesmo MSH2."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def consolidar(base:str|Path)->dict:
    root=Path(base)
    rows=[]
    for H in (4,8):
        for n in (8,16,24):
            path=root/"elmer"/f"ha-{H}-n-{n}"/"comparison.json"
            d=json.loads(path.read_text(encoding="utf-8"))
            if not math.isclose(d["H_over_a"],H) or d["nr"]!=n or d["nt"]!=2*n:
                raise ValueError("Geometria/malha nao corresponde ao experimento")
            a=d["recovery"]
            b=d["scipy_reference"]
            dk=a["kt_gross_gradiente_direto"]-b["kt_gross_gradiente_direto"]
            if not all(math.isfinite(x) for x in (dk,a["sigma_rr_sobre_T"],
                b["reacoes_equilibrio_x"],a["kt_gross_gradiente_direto"])):
                raise ValueError("Resultado não finito")
            if b["reacoes_equilibrio_x"]>1e-7:
                raise ValueError("Forcas SciPy sem equilibrio")
            if not 1.5<a["kt_gross_gradiente_direto"]<6 or abs(dk)>.6:
                raise ValueError("Diferenca grosseira entre FEMs no campo superficial")
            node_diffs=[abs(x["diff_rel"]) for x in d["point_displacements"].values()]
            if max(node_diffs)>.3:
                raise ValueError("Discrepancia de deslocamento >30%")
            rows.append({
                "H_over_a":H,"nr":n,"elementos":d["mesh_info"]["elmer_elements"],
                "mesh_sha256":d["mesh_sha256"],
                "kt_gross_elmer_gradiente":a["kt_gross_gradiente_direto"],
                "kt_gross_scipy_gradiente":b["kt_gross_gradiente_direto"],
                "delta_kt_elmer_menos_scipy":dk,
                "erro_rel_kt_mesmo_recuperador":dk/b["kt_gross_gradiente_direto"],
                "sigma_rr_elmer_sobre_T":a["sigma_rr_sobre_T"],
                "sigma_rr_scipy_sobre_T":b["sigma_rr_sobre_T"],
                "max_diferenca_rel_deslocamento":max(node_diffs),
                "deslocamentos_m":d["point_displacements"],
                "duracao_s":d["duration_s"]
            })
    return {
        "ciclo":13,
        "solvers":["Elmer FEM StressSolver EXTERNO (ElmerGrid conversao Gmsh)",
                   "SciPy Q8 independente do CalculiX"],
        "norma":"mesma malha Gmsh, mesma carga E nu estado de tensao plana e mesmo recuperador B direto na parede",
        "casos":rows,
        "status":"comparacao de solvers FEM; nao validacao experimental",
        "limites":[
            "NumPy/SciPy FEM autoral nao possui qualificacao industrial",
            "ElmerGrid pode reordenar os nos; comparacao espacial segue coordenadas originais",
            "Tensao de bordo recuperada por B de um elemento, ainda sujeita a erro",
            "Comparacao com CalculiX de Kt extrapolado requer reconhecer diferença de recuperação",
            "Kirsch infinito nao e referencia exata de chapa finita"
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pasta",required=True)
    a=p.parse_args()
    result=consolidar(a.pasta)
    outfile=Path(a.pasta)/"resumo_ciclo13.json"
    outfile.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
