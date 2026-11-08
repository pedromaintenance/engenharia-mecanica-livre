"""Ciclo 15 — efeito de L/W mantendo d/W e carregamento constantes.

NÃO usar tolerância de referência externa como aprovação estrutural.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from engmec.chapa_retangular import kt_peterson_bruto,kt_peterson_liquido

BASELINE_SQUARE={
    (4,8):3.6181243888669803,
    (4,16):3.5889141122768096,
    (4,24):3.584406203951414,
    (8,8):3.2132731775407413,
    (8,16):3.152511558063445,
    (8,24):3.1390315982981494
}


def consolidar(root:str|Path)->dict:
    root=Path(root)
    rows=[]
    for H_over_a in (4,8):
        rho=1/H_over_a
        for length_ratio in (1,2,4):
            for n in (8,16,24):
                folder=root/f"ha-{H_over_a}-lw-{length_ratio}-n-{n}"
                result=json.loads((folder/"comparison.json").read_text(encoding="utf-8"))
                stress=json.loads((folder/"recuperacao.json").read_text(encoding="utf-8"))
                if (not math.isclose(result["H_over_a"],H_over_a)
                    or not math.isclose(result["L_over_W"],length_ratio)
                    or not math.isclose(result["d_over_W"],rho)
                    or result["nr"]!=n or result["nt"]!=2*n):
                    raise ValueError("Divergência de identidade física/geometria")
                if stress["gauss_total"]!=9*n*2*n or stress["elementos"]!=2*n*n:
                    raise ValueError("Gauss 3x3 ou elementos incompletos")
                K=stress["metodos"]
                a=K["A_gradiente_bordo"]["kt_gross"]
                b=K["B_gauss_seis_coef"]["kt_gross"]
                c=K["C_patch_ponderado_quatro_coef"]["kt_gross"]
                if abs(a-result["recovery"]["kt_gross_gradiente_direto"])>1e-9:
                    raise ValueError("Regressão no gradiente Elmer")
                if length_ratio==1 and abs(a-BASELINE_SQUARE[(H_over_a,n)])>1e-7:
                    raise ValueError("Caso quadrado não reproduz ciclo 14")
                if any(not math.isfinite(x) or x<=1 or x>=10 for x in (a,b,c)):
                    raise ValueError("Kt extrapolado fora da faixa de controle")
                if not (folder/"deslocamentos_elmer.json").exists() or not (folder/"gauss_tensoes.csv").exists():
                    raise ValueError("Dados brutos do campo ausentes")
                if not math.isfinite(stress["jacobiano_minimo_m2"]) or stress["jacobiano_minimo_m2"]<=0:
                    raise ValueError("Elemento Q8 degenerado/invertido")
                peterson_net=kt_peterson_liquido(rho)
                peterson_gross=kt_peterson_bruto(rho)
                rows.append({
                    "H_over_a":H_over_a,"d_over_W":rho,
                    "L_over_W":length_ratio,
                    "comprimento_m":result["semicomprimento_x_m"]*2,
                    "largura_m":result["semilargura_y_m"]*2,
                    "n":n,"elementos":stress["elementos"],
                    "mesh_sha256":result["mesh_sha256"],
                    "kt_bruto_A":a,"kt_bruto_B":b,"kt_bruto_C":c,
                    "kt_liquido_A":a*(1-rho),
                    "kt_liquido_B":b*(1-rho),
                    "kt_liquido_C":c*(1-rho),
                    "amplitude_recuperacao":stress["sensibilidade"]["amplitude_entre_metodos_Kt_bruto"],
                    "sigma_rr_A":K["A_gradiente_bordo"]["sigma_rr_sobre_T"],
                    "sigma_rr_B":K["B_gauss_seis_coef"]["sigma_rr_sobre_T"],
                    "sigma_rr_C":K["C_patch_ponderado_quatro_coef"]["sigma_rr_sobre_T"],
                    "vieses_algoritmo_kirsch":stress["controle_analitico_Kirsch"],
                    "peterson_tira_longa_liquido":peterson_net,
                    "peterson_tira_longa_bruto":peterson_gross,
                    "erro_rel_C_vs_peterson_liquido":(c*(1-rho)-peterson_net)/peterson_net,
                    "erro_rel_A_vs_peterson_liquido":(a*(1-rho)-peterson_net)/peterson_net,
                    "residuo_equilibrio_scipy":result["scipy_reference"]["reacoes_equilibrio_x"],
                    "maior_erro_rel_deslocamento_elmer_scipy":max(abs(pt["diff_rel"]) for pt in result["point_displacements"].values()),
                    "rotulo_referencia":"Peterson/Howland aprox. tira longa, NAO exato para retangulo finito"
                })
    if len(rows)!=18:
        raise ValueError("Experimento incompleto")
    comparisons=[]
    for H_over_a in (4,8):
        for n in (8,16,24):
            matched={int(r["L_over_W"]):r for r in rows if r["H_over_a"]==H_over_a and r["n"]==n}
            if set(matched)!={1,2,4}:
                raise ValueError("L/W ausente")
            comparisons.append({
                "H_over_a":H_over_a,"n":n,
                "Kt_C_LW_1":matched[1]["kt_bruto_C"],
                "Kt_C_LW_2":matched[2]["kt_bruto_C"],
                "Kt_C_LW_4":matched[4]["kt_bruto_C"],
                "delta_C_4_menos_1":matched[4]["kt_bruto_C"]-matched[1]["kt_bruto_C"],
                "delta_rel_C_4_vs_peterson_bruto":(matched[4]["kt_bruto_C"]-matched[4]["peterson_tira_longa_bruto"])/matched[4]["peterson_tira_longa_bruto"]
            })
    return {
        "ciclo":15,"num_casos":len(rows),
        "problema":"chapa retangular plana, furo circular, tracao uniforme na direcao x; fronteiras superior/furo livres",
        "definicoes":{"L_over_W":"comprimento total na direcao x / largura total y = Hx/Hy",
                      "d_over_W":"diametro do furo/largura total= a/Hy",
                      "Kt_gross":"sigma_critica/T bruta",
                      "Kt_net":"Kt_gross*(1-d/W)"},
        "referencia_externa":{
            "modelo":"curva Peterson/Howland para tira suficientemente longa",
            "referencia":"https://mapdl.docs.pyansys.com/version/stable/examples/gallery_examples/00-mapdl-examples/2d_plate_with_a_hole.html",
            "fit":"Kt_net=3-3.14*rho+3.667*rho**2-1.527*rho**3",
            "limite":"ajuste para carga remota uniforme e tira longa; não é solução exata do nosso retângulo finito, nem válida para qualquer distribuição de carga"
        },
        "casos":rows,"comparacoes":comparisons,
        "limitacoes":[
            "Elementos Elmer e SciPy da mesma familia Q8: concordancia de deslocamento nao demonstra validação material.",
            "Tres recuperadores A/B/C apresentam erro de extrapolação em malha grosseira.",
            "O modelo de chapa é de tensão plana linear-elástica, sem contato, pino, fadiga, solda ou plastificação.",
            "Ajuste de Peterson usa tensão nominal líquida; converter antes de comparar fatores brutos.",
            "A referência externa de tira longa não é valor exato para L/W=1 ou 2.",
            "Não usar estes Kt para aceitar, modificar ou liberar componentes reais."
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pasta",required=True)
    args=p.parse_args()
    report=consolidar(args.pasta)
    out=Path(args.pasta)/"resumo_ciclo15.json"
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
