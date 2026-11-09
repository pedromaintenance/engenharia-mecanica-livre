"""Ciclo 17: comparacao de duas distribuicoes radiais no MESMO problema FEM.

Nao escolher o metodo pelo Kt proximo de Peterson; priorizar qualidade
geometrica e convergencia, sem substituir validacao de projeto real.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from engmec.convergencia_malha import qualidade_geometrica,convergencia_condicionada
from engmec.progressao_radial import razao_progressao


N_VALUES=(24,32,40,48)
METHODS={"A":"A_gradiente_bordo",
         "B":"B_gauss_seis_coef",
         "C":"C_patch_ponderado_quatro_coef"}


def _load_old() -> dict:
    data15=json.loads(Path("docs/dados/ciclo15-chapas-retangulares-2026-11-08.json").read_text(encoding="utf-8"))["experiment"]["casos"]
    data16=json.loads(Path("docs/dados/ciclo16-convergencia-fina-2026-11-08.json").read_text(encoding="utf-8"))["casos"]
    result={}
    for r in data15:
        if r["L_over_W"] not in (2,4) or r["n"]!=24:
            continue
        key=(int(r["H_over_a"]),int(r["L_over_W"]),int(r["n"]))
        result[key]={
            "Kt_gross_A":r["kt_bruto_A"],
            "Kt_gross_B":r["kt_bruto_B"],
            "Kt_gross_C":r["kt_bruto_C"],
            "sigma_rr_C":r["sigma_rr_C"],
            "mesh_sha256":r["mesh_sha256"],
            "qualidade_malha":None
        }
    for r in data16:
        key=(int(r["ha"]),int(r["L_over_W"]),int(r["n"]))
        if key in result:
            raise ValueError("Duplicacao entre datasets de baseline")
        result[key]=r
    if len(result)!=16:
        raise ValueError(f"16 baselines necessarios, obtidos={len(result)}")
    return result


def consolidar(root:str|Path)->dict:
    root=Path(root)
    fixed=_load_old()
    cases=[]
    series=[]
    for ha in (4,8):
        H=.01*ha
        rho=1/ha
        for lw in (2,4):
            L=H*lw
            local=[]
            for n in N_VALUES:
                folder=root/f"ha-{ha}-lw-{lw}-n-{n}"
                a=json.loads((folder/"comparison.json").read_text(encoding="utf-8"))
                b=json.loads((folder/"recuperacao.json").read_text(encoding="utf-8"))
                if (a["nr"]!=n or a["nt"]!=2*n or
                    not math.isclose(a["H_over_a"],ha) or
                    not math.isclose(a["L_over_W"],lw) or
                    not math.isclose(a["d_over_W"],rho)):
                    raise ValueError("Malha/geometria diferente do plano")
                if a["estrategia_progressao_radial"]!="escalonada":
                    raise ValueError("Estratégia do solver diferente")
                q=razao_progressao(n,"escalonada")
                if not math.isclose(a["q_radial_efetivo"],q,rel_tol=1e-12):
                    raise ValueError("Progressão geometricamente inconsistente")
                old=fixed[(ha,lw,n)]
                if n==24 and a["mesh_sha256"]!=old["mesh_sha256"]:
                    raise ValueError("n24 deve preservar identidade de malha SHA256 do ciclo15")
                if n>24 and a["mesh_sha256"]==old["mesh_sha256"]:
                    raise ValueError("Refino escalonado deve alterar distribuicao dos nos")
                if b["elementos"]!=2*n*n or b["gauss_total"]!=9*b["elementos"]:
                    raise ValueError("Contagem Gauss/elementos invalida")
                for file in ("deslocamentos_elmer.json","gauss_tensoes.csv","model.geo","model.msh","solver.log"):
                    if not (folder/file).is_file():
                        raise ValueError(f"Evidencia ausente: {folder/file}")
                calculated_sha=hashlib.sha256((folder/"model.msh").read_bytes()).hexdigest()
                if calculated_sha!=a["mesh_sha256"]:
                    raise ValueError("Hash real do arquivo MSH nao confere")
                geom=qualidade_geometrica(folder/"model.msh",a=.01,H=H,L=L,nr=n,nt=2*n)
                if geom["elementos"]!=2*n*n or geom["arestas_tracionadas"]!=n:
                    raise ValueError("Malha/contorno de carga incompletos")
                if geom["arestas_topo_livre"]!=n or geom["arestas_furo_livre"]!=2*n:
                    raise ValueError("Contorno superior/furo incompleto")
                residual=a["scipy_reference"]["reacoes_equilibrio_x"]
                if not math.isfinite(residual) or residual>1e-8:
                    raise ValueError("Equilibrio de forcas inadmissivel")
                disp=max(abs(d["diff_rel"]) for d in a["point_displacements"].values())
                if disp>1e-6:
                    raise ValueError("Solucao Elmer/SciPy nao confere")
                stress=b["metodos"]
                K={k:stress[v]["kt_gross"] for k,v in METHODS.items()}
                if any(not math.isfinite(v) or v<1.8 or v>5 for v in K.values()):
                    raise ValueError("Kt recuperado nao finito/plausivel")
                if abs(K["A"]-a["recovery"]["kt_gross_gradiente_direto"])>1e-8:
                    raise ValueError("Borda direta divergente")
                comparable_quality=old.get("qualidade_malha")
                result={
                  "ha":ha,"d_over_W":rho,"L_over_W":lw,"n":n,
                  "q_radial_efetivo":q,"q_radial_acumulado":q**n,
                  "elementos":b["elementos"],"nos":geom["nos"],"dofs":geom["dofs_totais"],
                  "Kt_gross_escalonada":K,
                  "Kt_liquido_escalonada":{k:v*(1-rho) for k,v in K.items()},
                  "Kt_gross_fixa_historica":{k:old[f"Kt_gross_{k}"] for k in METHODS},
                  "delta_Kt_C_escalonada_menos_fixa":K["C"]-old["Kt_gross_C"],
                  "amplitude_recuperadores_gross":b["sensibilidade"]["amplitude_entre_metodos_Kt_bruto"],
                  "sigma_rr_C_escalonada":stress[METHODS["C"]]["sigma_rr_sobre_T"],
                  "sigma_rr_C_fixa_historica":old["sigma_rr_C"],
                  "qualidade_escalonada":geom,
                  "qualidade_fixa_historica":comparable_quality,
                  "mudanca_razao_geral_max":(
                    geom["razão_max_min_cordas_geral_max"]-comparable_quality["razão_max_min_cordas_geral_max"]
                    if comparable_quality else None),
                  "mudanca_razao_primeira_faixa_max":(
                    geom["razão_max_min_cordas_primeira_faixa_max"]-comparable_quality["razão_max_min_cordas_primeira_faixa_max"]
                    if comparable_quality else None),
                  "mudanca_angulo_minimo_geral":(
                    geom["angulo_minimo_vertices_graus_geral"]-comparable_quality["angulo_minimo_vertices_graus_geral"]
                    if comparable_quality else None),
                  "mesh_sha256_escalonada":a["mesh_sha256"],
                  "mesh_sha256_fixa_historica":old["mesh_sha256"],
                  "equilibrio_scipy":residual,
                  "max_rel_diff_deslocamento_scipy_elmer":disp,
                  "F_quadrante_N":1e7*H*.005,
                  "controles_Kirsch":b["controle_analitico_Kirsch"]
                }
                cases.append(result);local.append(result)
            conv={}
            for method in METHODS:
                points_scaled=[(r["n"],r["Kt_gross_escalonada"][method]) for r in local]
                points_fixed=[(r["n"],r["Kt_gross_fixa_historica"][method]) for r in local]
                conv[method]={"escalonada":convergencia_condicionada(points_scaled),
                              "fixa":convergencia_condicionada(points_fixed)}
            series.append({
              "ha":ha,"d_over_W":rho,"L_over_W":lw,
              "Kt_net_n48_escalonada_C":local[-1]["Kt_liquido_escalonada"]["C"],
              "Kt_net_n48_fixa_C":local[-1]["Kt_gross_fixa_historica"]["C"]*(1-rho),
              "qualidade_n48_escalonada":local[-1]["qualidade_escalonada"],
              "qualidade_n48_fixa":local[-1]["qualidade_fixa_historica"],
              "convergencia_comparada":conv
            })
    if len(cases)!=16 or len(series)!=4:
        raise ValueError("16 casos e 4 series exigidos")
    return {
      "ciclo":17,"versao":"0.17.0",
      "cases":cases,"series":series,
      "strategies":{
        "fixa":"q(n)=1.12, n=24,32,40,48; baseline execucoes ciclos 15 e 16",
        "escalonada":"q(n)=exp(24*ln(1.12)/n); q(n)^n=1.12^24; nova execucao Elmer",
        "malha":"Gmsh transfinite duas superficies Q8, fisica identica e mesmo nt=2*n"
      },
      "assumptions":"2D plane stress, circular free hole, elastic isotropic E200GPa nu0.3, T10MPa, x traction, y top free",
      "reference":"Peterson somente para Kt NET de tira longa, nao referencia exata do retangulo",
      "gci_note":"GCI nao validacao fisica; emitir somente com monotonicidade/ordens conforme gate",
      "quality_note":"As razoes de cordas são indicadores proxy da forma Q8; nao substituem qualidade de curvas e jacobianos",
      "limits":[
        "Os baselines fixos são reproduções históricas dos mesmos parâmetros, versões e workflows publicados nos ciclos 15/16.",
        "Melhora do indicador geometrico nao certifica menor erro absoluto em Kt.",
        "N24 escalonado deve ser identico a n24 fixo por hash MSH.",
        "Estudo não contempla pino, contato, falhas por fadiga ou propriedades reais."
      ]
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pasta",required=True)
    args=parser.parse_args()
    result=consolidar(args.pasta)
    target=Path(args.pasta)/"resumo_ciclo17.json"
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
      "ciclo":17,"novos_modelos":len(result["cases"]),
      "n48":[{
         "ha":s["ha"],"lw":s["L_over_W"],
         "kt_net_C_scaled":s["Kt_net_n48_escalonada_C"],
         "kt_net_C_fixed":s["Kt_net_n48_fixa_C"],
         "max_edge_ratio_scaled":s["qualidade_n48_escalonada"]["razão_max_min_cordas_geral_max"],
         "max_edge_ratio_fixed":s["qualidade_n48_fixa"]["razão_max_min_cordas_geral_max"],
         "max_inner_ratio_scaled":s["qualidade_n48_escalonada"]["razão_max_min_cordas_primeira_faixa_max"],
         "max_inner_ratio_fixed":s["qualidade_n48_fixa"]["razão_max_min_cordas_primeira_faixa_max"],
         "min_angle_scaled":s["qualidade_n48_escalonada"]["angulo_minimo_vertices_graus_geral"],
         "min_angle_fixed":s["qualidade_n48_fixa"]["angulo_minimo_vertices_graus_geral"],
         "gci_C_scaled":s["convergencia_comparada"]["C"]["escalonada"]["status"],
         "gci_C_fixed":s["convergencia_comparada"]["C"]["fixa"]["status"]
       } for s in result["series"]]
    },ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
