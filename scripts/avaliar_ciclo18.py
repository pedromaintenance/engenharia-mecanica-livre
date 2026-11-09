"""Ciclo 18: spline interno em dois blocos vs interface reta, MESMA fisica FEM.

Auditoria separada para qualidade de forma, tracao radial livre,
recuperacao de Kt e convergencia; nao promover geometria por GCI apenas.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from engmec.convergencia_malha import qualidade_geometrica,convergencia_condicionada
from engmec.progressao_radial import razao_progressao


def consolidar(root:str|Path)->dict:
    root=Path(root)
    old=json.loads(Path("docs/dados/ciclo17-malha-radial-2026-11-08.json").read_text(encoding="utf-8"))
    fixed={(r["ha"],int(r["L_over_W"]),r["n"]):r for r in old["cases"]}
    if len(fixed)!=16:
        raise ValueError("Faltam baselines reais de interface reta do ciclo17")
    cases=[];series=[]
    for ha in (4,8):
        H=ha*.01;rho=1/ha
        for lw in (2,4):
            L=H*lw
            local=[]
            for n in (24,32,40,48):
                folder=root/f"ha-{ha}-lw-{lw}-n-{n}"
                comp=json.loads((folder/"comparison.json").read_text(encoding="utf-8"))
                recover=json.loads((folder/"recuperacao.json").read_text(encoding="utf-8"))
                if (comp.get("interface_interna")!="curva" or
                    comp.get("estrategia_progressao_radial")!="escalonada"):
                    raise ValueError(f"Modelo CAD/estrategia diferente: {folder}")
                if comp["nr"]!=n or comp["nt"]!=2*n:
                    raise ValueError("Resolucao diferente")
                if not math.isclose(comp["H_over_a"],ha) or not math.isclose(comp["L_over_W"],lw) or not math.isclose(comp["d_over_W"],rho):
                    raise ValueError("Geometria fisica alterada")
                if not math.isclose(comp["q_radial_efetivo"],razao_progressao(n,"escalonada"),rel_tol=1e-10):
                    raise ValueError("Progressao radial alterada")
                if recover["elementos"]!=2*n*n or recover["gauss_total"]!=9*2*n*n:
                    raise ValueError("Elementos e pontos de Gauss incorretos")
                for required in ("model.geo","model.msh","solver.log","case.sif","deslocamentos_elmer.json","gauss_tensoes.csv"):
                    if not (folder/required).is_file():
                        raise ValueError(f"Arquivo de auditoria ausente: {folder/required}")
                digest=hashlib.sha256((folder/"model.msh").read_bytes()).hexdigest()
                if digest!=comp["mesh_sha256"]:
                    raise ValueError("Hash MSH2 nao confere")
                base=fixed[(ha,lw,n)]
                if digest==base["mesh_sha256_escalonada"]:
                    raise ValueError("Interface alternativa nao mudou a malha")
                quality=qualidade_geometrica(folder/"model.msh",a=.01,H=H,L=L,nr=n,nt=2*n)
                if (quality["elementos"]!=2*n*n or quality["arestas_tracionadas"]!=n or
                    quality["arestas_topo_livre"]!=n or quality["arestas_furo_livre"]!=2*n):
                    raise ValueError("Contornos de carga/furo incompletos")
                equilibrium=comp["scipy_reference"]["reacoes_equilibrio_x"]
                maxdis=max(abs(x["diff_rel"]) for x in comp["point_displacements"].values())
                if not math.isfinite(equilibrium) or equilibrium>1e-8 or maxdis>1e-6:
                    raise ValueError("Violacao de equilibrio ou discrepancia Elmer x SciPy")
                method_map={"A":"A_gradiente_bordo","B":"B_gauss_seis_coef","C":"C_patch_ponderado_quatro_coef"}
                K={m:recover["metodos"][name]["kt_gross"] for m,name in method_map.items()}
                if any(not math.isfinite(v) or not (1.5<v<7) for v in K.values()):
                    raise ValueError("Tensao fora do dominio de teste")
                if abs(K["A"]-comp["recovery"]["kt_gross_gradiente_direto"])>1e-8:
                    raise ValueError("Recuperador direto nao confere")
                rr=recover["metodos"][method_map["C"]]["sigma_rr_sobre_T"]
                oq=base["qualidade_escalonada"]
                row={
                    "H_sobre_a":ha,"d_sobre_W":rho,"L_sobre_W":lw,"n":n,
                    "q_escalonado":comp["q_radial_efetivo"],
                    "elementos_Q8":quality["elementos"],"nos":quality["nos"],"dofs":quality["dofs_totais"],
                    "nova_qualidade":quality,"anterior_qualidade":oq,
                    "max_ratio_global_novo":quality["razão_max_min_cordas_geral_max"],
                    "max_ratio_global_antigo":oq["razão_max_min_cordas_geral_max"],
                    "max_ratio_primeira_faixa_novo":quality["razão_max_min_cordas_primeira_faixa_max"],
                    "max_ratio_primeira_faixa_antigo":oq["razão_max_min_cordas_primeira_faixa_max"],
                    "angulo_min_global_novo_grau":quality["angulo_minimo_vertices_graus_geral"],
                    "angulo_min_global_antigo_grau":oq["angulo_minimo_vertices_graus_geral"],
                    "angulo_min_primeira_faixa_novo_grau":quality["angulo_minimo_vertices_graus_primeira_faixa"],
                    "angulo_min_primeira_faixa_antigo_grau":oq["angulo_minimo_vertices_graus_primeira_faixa"],
                    "Kt_bruto_novo":K,"Kt_liquido_novo":{k:v*(1-rho) for k,v in K.items()},
                    "Kt_bruto_anterior":base["Kt_gross_escalonada"],
                    "Kt_liquido_anterior":base["Kt_liquido_escalonada"],
                    "sigma_rr_sobre_T_novo":rr,
                    "sigma_rr_sobre_T_anterior":base["sigma_rr_C_escalonada"],
                    "amplitude_recuperadores_Kt_bruto":recover["sensibilidade"]["amplitude_entre_metodos_Kt_bruto"],
                    "reacoes_equilibrio_rel":equilibrium,
                    "deslocamento_max_desvio_rel":maxdis,
                    "resultante_x_quadrante_N":1e7*H*.005,
                    "mesh_sha256":digest,
                    "controle_kirsch":recover["controle_analitico_Kirsch"],
                    "comparacao":{
                        "melhora_alongamento_global":quality["razão_max_min_cordas_geral_max"]<oq["razão_max_min_cordas_geral_max"],
                        "melhora_alongamento_primeira_faixa":quality["razão_max_min_cordas_primeira_faixa_max"]<oq["razão_max_min_cordas_primeira_faixa_max"],
                        "melhora_angulo_min_global":quality["angulo_minimo_vertices_graus_geral"]>oq["angulo_minimo_vertices_graus_geral"]+1e-9,
                        "melhora_tracao_radial_livre":abs(rr)<abs(base["sigma_rr_C_escalonada"])
                    }
                }
                cases.append(row);local.append(row)
            conv={}
            for method in "ABC":
                vals=[(r["n"],r["Kt_bruto_novo"][method]) for r in local]
                conv[method]=convergencia_condicionada(vals)
            fine=local[-1]
            series.append({
                "d_sobre_W":rho,"L_sobre_W":lw,
                "Kt_liquido_n48_C_novo":fine["Kt_liquido_novo"]["C"],
                "Kt_liquido_n48_C_anterior":fine["Kt_liquido_anterior"]["C"],
                "geo_n48":{"novo_ratio_global":fine["max_ratio_global_novo"],
                          "antigo_ratio_global":fine["max_ratio_global_antigo"],
                          "novo_ratio_furo":fine["max_ratio_primeira_faixa_novo"],
                          "antigo_ratio_furo":fine["max_ratio_primeira_faixa_antigo"],
                          "novo_angulo_min":fine["angulo_min_global_novo_grau"],
                          "antigo_angulo_min":fine["angulo_min_global_antigo_grau"]},
                "sigma_rr_n48_novo":fine["sigma_rr_sobre_T_novo"],
                "sigma_rr_n48_anterior":fine["sigma_rr_sobre_T_anterior"],
                "gates_n48":fine["comparacao"],
                "convergencia":conv
            })
    if len(cases)!=16 or len(series)!=4:
        raise ValueError("Conjunto experimental incompleto")
    return {
        "ciclo":18,"modelos_externos":16,"versao":"0.18.0",
        "alteracao_unica":"interface interna entre dois blocos Gmsh Line(3) -> Spline(3), 3 pontos de controle interpolantes; mesmo CAD fisico e progressao radial escalonada",
        "malhas":["n24","n32","n40","n48"],
        "descricao_fisica":"quarto de chapa retangular perfurada, carga bruta T=10 MPa na face x=Hx, topo/furo livres, simetrias; elastico linear isotropico, tensao plana E=200GPa nu=0.3",
        "gates_reais":"qualidade global e junto ao furo, angulo minimo, sigma_rr livre, Kt A/B/C e convergencia condicionada",
        "cases":cases,"series":series,
        "caveats":[
            "Mudança de interface Gmsh interior não equivale a mudança do contorno exterior ou da física.",
            "A qualidade proxy de cordas nao descreve toda curvatura Q8 nem erro total de discretizacao.",
            "Um menor Kt ou menor GCI nao garante maior exatidao na parede livre.",
            "Sem contato de pino, fadiga, solda, plastificacao ou ensaio de material real."
        ]
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pasta",required=True)
    args=parser.parse_args()
    d=consolidar(args.pasta)
    target=Path(args.pasta)/"resumo_ciclo18.json"
    target.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"ciclo":18,"modelos":len(d["cases"]),"series":[
        {"rho":s["d_sobre_W"],"lw":s["L_sobre_W"],
         "gates_n48":s["gates_n48"],
         "geo_n48":s["geo_n48"],
         "rr_new":s["sigma_rr_n48_novo"],"rr_old":s["sigma_rr_n48_anterior"],
         "Kt_net_C_new":s["Kt_liquido_n48_C_novo"],"Kt_net_C_old":s["Kt_liquido_n48_C_anterior"],
         "GCI_C":s["convergencia"]["C"]["GCI_fino_relativo"]
        } for s in d["series"]]},indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
