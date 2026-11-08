"""Ciclo 16: 12 novos FEM Elmer, qualidade Q8 e GCI sob gates."""
from __future__ import annotations
import argparse
import json
import math
import hashlib
from pathlib import Path
from engmec.convergencia_malha import qualidade_geometrica,convergencia_condicionada
from engmec.chapa_retangular import kt_peterson_liquido


def consolidar(root:str|Path)->dict:
    root=Path(root)
    old=json.loads(Path("docs/dados/ciclo15-chapas-retangulares-2026-11-08.json").read_text(encoding="utf-8"))["experiment"]["casos"]
    baseline={(int(r["H_over_a"]),int(r["L_over_W"]),int(r["n"])):r for r in old}
    rows=[];series=[]
    for ha in (4,8):
        H=ha*.01
        rho=1/ha
        for lw in (2,4):
            L=H*lw
            local=[]
            for n in (32,40,48):
                folder=root/f"ha-{ha}-lw-{lw}-n-{n}"
                b=json.loads((folder/"comparison.json").read_text(encoding="utf-8"))
                d=json.loads((folder/"recuperacao.json").read_text(encoding="utf-8"))
                if (int(b["H_over_a"])!=ha or not math.isclose(b["L_over_W"],lw)
                    or not math.isclose(b["d_over_W"],rho)
                    or int(b["nr"])!=n or int(b["nt"])!=2*n):
                    raise ValueError(f"Metadados geometria divergentes: {folder}")
                if d["elementos"]!=2*n*n or d["gauss_total"]!=9*d["elementos"]:
                    raise ValueError("Problema de elementos/Gauss")
                if not (folder/"deslocamentos_elmer.json").exists() or not (folder/"gauss_tensoes.csv").exists():
                    raise ValueError("Campos Elmer ou Gauss ausentes")
                raw=(folder/"model.msh").read_bytes()
                hashval=hashlib.sha256(raw).hexdigest()
                if hashval!=b["mesh_sha256"]:
                    raise ValueError("Hash MSH2 inconsistente")
                q=qualidade_geometrica(folder/"model.msh",a=.01,H=H,L=L,nr=n,nt=2*n)
                K=d["metodos"]
                A=K["A_gradiente_bordo"]["kt_gross"]
                B=K["B_gauss_seis_coef"]["kt_gross"]
                C=K["C_patch_ponderado_quatro_coef"]["kt_gross"]
                if not all(math.isfinite(x) and 1.8<x<5 for x in (A,B,C)):
                    raise ValueError("Pico de tensao implausivel")
                if abs(A-b["recovery"]["kt_gross_gradiente_direto"])>1e-8:
                    raise ValueError("Gradiente A nao corresponde a baseline Elmer")
                if b["scipy_reference"]["reacoes_equilibrio_x"]>1e-8:
                    raise ValueError("Equilibrio SciPy fora do critério")
                maxdisp=max(abs(x["diff_rel"]) for x in b["point_displacements"].values())
                if maxdisp>1e-6:
                    raise ValueError("Elmer e SciPy divergentes no deslocamento")
                if q["arestas_tracionadas"]!=n:
                    raise ValueError("Borda tracionada incompleta")
                if q["arestas_topo_livre"]!=n or q["arestas_furo_livre"]!=2*n:
                    raise ValueError("Contornos livres incompletos")
                if q["dofs_totais"]<=0:
                    raise ValueError("DOFs invalidos")
                F=1e7*H*.005
                r={"ha":ha,"d_over_W":rho,"L_over_W":lw,"n":n,
                   "elementos":2*n*n,"nodes":q["nos"],"dofs":q["dofs_totais"],
                   "Kt_gross_A":A,"Kt_gross_B":B,"Kt_gross_C":C,
                   "Kt_net_A":A*(1-rho),"Kt_net_B":B*(1-rho),"Kt_net_C":C*(1-rho),
                   "spread_Kt_gross":d["sensibilidade"]["amplitude_entre_metodos_Kt_bruto"],
                   "sigma_rr_A":K["A_gradiente_bordo"]["sigma_rr_sobre_T"],
                   "sigma_rr_B":K["B_gauss_seis_coef"]["sigma_rr_sobre_T"],
                   "sigma_rr_C":K["C_patch_ponderado_quatro_coef"]["sigma_rr_sobre_T"],
                   "peterson_Kt_net":kt_peterson_liquido(rho),
                   "peterson_relative_C":(C*(1-rho)-kt_peterson_liquido(rho))/kt_peterson_liquido(rho),
                   "F_quadrante_N":F,
                   "equilibrio_x_rel":b["scipy_reference"]["reacoes_equilibrio_x"],
                   "max_rel_disp_elmer_scipy":maxdisp,
                   "mesh_sha256":hashval,"qualidade_malha":q,
                   "amostras_patch":d["patch_amostras"],
                   "kirsch_bias_B":d["controle_analitico_Kirsch"]["B_bias"],
                   "kirsch_bias_C":d["controle_analitico_Kirsch"]["C_bias"]}
                local.append(r);rows.append(r)
            baseline24=baseline[(ha,lw,24)]
            conv={}
            for met,prior in [("A","kt_bruto_A"),("B","kt_bruto_B"),("C","kt_bruto_C")]:
                pts=[(24,baseline24[prior])]+[(r["n"],r[f"Kt_gross_{met}"]) for r in local]
                conv[met]=convergencia_condicionada(pts)
            series.append({
                "H_over_a":ha,"d_over_W":rho,"L_over_W":lw,
                "casos_novos":[r["n"] for r in local],
                "baseline_n24":{
                    "Kt_gross_A":baseline24["kt_bruto_A"],
                    "Kt_gross_B":baseline24["kt_bruto_B"],
                    "Kt_gross_C":baseline24["kt_bruto_C"],
                    "fonte":"docs/dados/ciclo15-chapas-retangulares-2026-11-08.json"
                },
                "convergencia":conv,
                "Kts_n48":{m:local[-1][f"Kt_net_{m}"] for m in ("A","B","C")},
                "difference_n40_n48_C_abs":local[-1]["Kt_gross_C"]-local[-2]["Kt_gross_C"],
                "difference_n40_n48_C_rel":abs(local[-1]["Kt_gross_C"]-local[-2]["Kt_gross_C"])/abs(local[-1]["Kt_gross_C"])
            })
    if len(rows)!=12 or len(series)!=4:
        raise ValueError("Conjunto de dados incompleto; 12 casos/4 series exigidos")
    return {
      "ciclo":16,"novos_casos":len(rows),
      "malhas_n":[32,40,48],"elementos_por_malha":[2048,3200,4608],
      "problema":"retângulo perfurado, 2D elasticidade plana sob tração; Elmer solver com recuperação A B C",
      "comparacao_Peterson":"Curva de tira longa baseada em secao liquida; nao solucao exata da chapa finita",
      "recomendacao_GCI":"Somente com 4 pontos monotônicos, ordem positiva plausivel e estabilidade da ordem observada entre dois tripletos. Index de discretizacao condicional; NAO validacao física.",
      "series":series,"casos":rows,
      "limites":[
        "O próprio GCI condicionado não inclui erro de forma Q8, variacao do método de recuperacao, erro de modelagem ou dados físicos.",
        "Mesmo numero de elementos entre diferentes L/W nao garante igual qualidade de malha.",
        "Peterson aproxima tira longa de largura finita; não é oráculo exato do retângulo finito.",
        "Elementos Q8 de tensão plana não representam contato com pino, solda, trinca ou fadiga.",
        "Nenhum Kt deste estudo é critério de liberação/aceitação em mina."
      ]
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pasta",required=True)
    args=parser.parse_args()
    report=consolidar(args.pasta)
    out=Path(args.pasta)/"resumo_ciclo16.json"
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"ciclo":16,"novos_casos":report["novos_casos"],
         "series":[{"ha":s["H_over_a"],"lw":s["L_over_W"],"Kts_n48":s["Kts_n48"],
          "diff_C_fino":s["difference_n40_n48_C_rel"],
          "GCI_C":s["convergencia"]["C"]} for s in report["series"]]},
         ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
