"""Consolidacao do ciclo 14: mesmos deslocamentos Elmer, 3 metodos de Kt."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def consolidar(root:str|Path)->dict:
    root=Path(root)
    cases=[]
    for H in (4,8):
        for n in (8,16,24):
            folder=root/f"ha-{H}-n-{n}"
            r=json.loads((folder/"recuperacao.json").read_text(encoding="utf-8"))
            pair=json.loads((folder/"comparison.json").read_text(encoding="utf-8"))
            if not math.isclose(r["H_sobre_a"],H) or r["elementos"]!=n*2*n:
                raise ValueError("Resultado associado a geometria/malha incorreta")
            if pair["H_over_a"]!=H or pair["nr"]!=n:
                raise ValueError("Campo Elmer nao corresponde ao mesmo caso")
            if r["gauss_total"]!=r["elementos"]*9:
                raise ValueError("Ausencia de pontos de Gauss Q8 3x3")
            if r["patch_amostras"]<24:
                raise ValueError("Patch insuficiente")
            records=r["metodos"]
            if sorted(records)!=[
                "A_gradiente_bordo","B_gauss_seis_coef","C_patch_ponderado_quatro_coef"
            ]:
                raise ValueError("Três recuperadores obrigatorios ausentes")
            a=records["A_gradiente_bordo"]["kt_gross"]
            if abs(a-pair["recovery"]["kt_gross_gradiente_direto"])>1e-9:
                raise ValueError("Gradiente direto nao preservou baseline Elmer")
            values=[item["kt_gross"] for item in records.values()]
            if any(not math.isfinite(x) or x<=1 or x>9 for x in values):
                raise ValueError("Kt nao finito ou fora de escala mecanica plausivel")
            if r["jacobiano_minimo_m2"]<=0:
                raise ValueError("Malha invertida")
            for key in ("B_bias","C_bias","A_bias"):
                if not math.isfinite(r["controle_analitico_Kirsch"][key]):
                    raise ValueError("Controle Kirsch nao finito")
            if not (folder/"gauss_tensoes.csv").exists():
                raise ValueError("Pontos brutos Gauss não arquivados")
            if not (folder/"deslocamentos_elmer.json").exists():
                raise ValueError("Deslocamentos integrais não arquivados")
            cases.append({
                "H_sobre_a":H,"largura_mm":20*H,"n":n,"elementos":r["elementos"],
                "kt_A_gradiente":values[0],
                "kt_B_gauss_extrapolacao":values[1],
                "kt_C_patch_ponderado":values[2],
                "amplitude_metodos_kt":r["sensibilidade"]["amplitude_entre_metodos_Kt_bruto"],
                "faixa_valores_kt":[min(values),max(values)],
                "condicao_patch_B":records["B_gauss_seis_coef"]["condicao_matriz"],
                "condicao_patch_C":records["C_patch_ponderado_quatro_coef"]["condicao_matriz"],
                "sigma_rr_A":records["A_gradiente_bordo"]["sigma_rr_sobre_T"],
                "sigma_rr_B":records["B_gauss_seis_coef"]["sigma_rr_sobre_T"],
                "sigma_rr_C":records["C_patch_ponderado_quatro_coef"]["sigma_rr_sobre_T"],
                "residuo_tt_B":records["B_gauss_seis_coef"]["residuo_tt_rms"],
                "residuo_tt_C":records["C_patch_ponderado_quatro_coef"]["residuo_tt_rms"],
                "kirsch_bias":r["controle_analitico_Kirsch"],
                "amostras_patch":r["patch_amostras"],
                "gauss_total":r["gauss_total"],
                "mesh_sha256":pair["mesh_sha256"],
                "fonte_deslocamentos":"mesmo VTU real gerado pelo ElmerSolver"
            })
    return {
        "ciclo":14,"casos":cases,
        "material":"elasticidade isotropica linear, tensao plana",
        "mesmo_solver_e_campo":"Elmer FEM em todos os metodos, 3x3 Gauss Q8",
        "metodos":{
            "A":"gradiente B@u no vertice de contorno",
            "B":"seis coeficientes, ajuste local por pontos Gauss sem peso",
            "C":"quatro coeficientes, patch ponderado pelo jacobiano Gauss e pela proximidade"
        },
        "incerteza":"faixa deterministica de variacao do pos-processamento, nao intervalo de confianca nem limite superior fisico",
        "restricoes":[
            "A regra de recuperacao C e exploratoria, nao SPR Zienkiewicz-Zhu garantido.",
            "Dois ajustes de tensao com pesos/base diferentes nao estabelecem exatidao.",
            "Referencia Kirsch infinito controla algoritmos, nao a solucao da chapa finita.",
            "Nao pode ser usada para dimensionar/inspecionar olhais ou liberar equipamento."
        ]
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pasta",required=True)
    args=parser.parse_args()
    report=consolidar(args.pasta)
    path=Path(args.pasta)/"resumo_ciclo14.json"
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
