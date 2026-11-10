"""Ciclo 20: avaliar seis blocos Q8 com anel e retângulo intermediário.

Não aprovar o novo CAD apenas pelo Kt; verificar simultaneamente
conformidade da interface interna, qualidade, tração livre e equilíbrio.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

from engmec.convergencia_malha import qualidade_geometrica,convergencia_condicionada
from engmec.multibloco_externo import parametros_seis_blocos,verificar_seis_blocos


def consolidar(root:str|Path)->dict:
    root=Path(root)
    old=json.loads(Path("docs/dados/ciclo19-anel-multibloco-2026-11-09.json").read_text(encoding="utf-8"))
    baseline={(r["H_over_a"],int(r["L_over_W"]),r["n"]):r for r in old["cases"]}
    if len(baseline)!=16:
        raise ValueError("Baseline de 16 casos incompleto")
    methods={"A":"A_gradiente_bordo","B":"B_gauss_seis_coef",
             "C":"C_patch_ponderado_quatro_coef"}
    rows=[];series=[]
    for ha in (4,8):
        H=.01*ha;rho=1/ha
        for lw in (2,4):
            L=H*lw
            local=[]
            for n in (24,32,40,48):
                folder=root/f"ha-{ha}-lw-{lw}-n-{n}"
                comp=json.loads((folder/"comparison.json").read_text(encoding="utf-8"))
                rec=json.loads((folder/"recuperacao.json").read_text(encoding="utf-8"))
                if comp.get("topologia")!="anel-seis-blocos" or comp.get("distribuicao_angular")!="uniforme":
                    raise ValueError("Topologia/grade angular diferentes do ensaio")
                if (comp["nr"]!=n or comp["nt"]!=2*n or
                    not math.isclose(comp["H_over_a"],ha) or
                    not math.isclose(comp["L_over_W"],lw) or
                    not math.isclose(comp["d_over_W"],rho)):
                    raise ValueError("Dimensoes fisicas ou malha incompatíveis")
                if comp["q_radial_efetivo"] is not None:
                    raise ValueError("Nao usar q radial de 2 blocos para malha anular")
                if rec["elementos"]!=2*n*n or rec["gauss_total"]!=18*n*n:
                    raise ValueError("Quantidade de elementos ou pontos Gauss errada")
                for file in ("model.geo","model.msh","case.sif","solver.log",
                             "recuperacao.json","gauss_tensoes.csv","deslocamentos_elmer.json"):
                    if not (folder/file).is_file():
                        raise ValueError(f"Evidencia ausente: {folder}/{file}")
                msh=(folder/"model.msh").read_bytes()
                checksum=hashlib.sha256(msh).hexdigest()
                if checksum!=comp["mesh_sha256"]:
                    raise ValueError("MSH2 não coincide com o hash reportado")
                from engmec.gmsh_chapa import importar_msh2
                mesh=importar_msh2(msh.decode("utf-8"),a=.01,H=H,Hx=L,nr=n,nt=2*n)
                conformity=verificar_seis_blocos(mesh,a=.01,Hy=H,Hx=L,nr=n,nt=2*n)
                geo=qualidade_geometrica(folder/"model.msh",a=.01,H=H,L=L,nr=n,nt=2*n)
                if geo["elementos"]!=2*n*n or geo["faixa_mais_interna_elementos"]!=2*n:
                    raise ValueError("Borda interna mal contada")
                if geo["arestas_tracionadas"]!=n or geo["arestas_topo_livre"]!=n or geo["arestas_furo_livre"]!=2*n:
                    raise ValueError("Contornos físicos ausentes")
                meta=parametros_seis_blocos(n,2*n,a=.01,Hy=H,Hx=L)
                em=comp["controle_multibloco"]
                if (em is None or em["parametros"]["ni"]!=meta["ni"] or
                    em["conformidade"]["anel"]["arestas_interface_conformes"]!=2*n or
                    em["conformidade"]["interface_retangular_arestas_conformes"]!=2*n):
                    raise ValueError("Metadados do anel inconsistentes")
                eq=comp["scipy_reference"]["reacoes_equilibrio_x"]
                diff=max(abs(v["diff_rel"]) for v in comp["point_displacements"].values())
                if not math.isfinite(eq) or eq>1e-8 or diff>1e-6:
                    raise ValueError("Equilíbrio ou comparação Elmer/SciPy não passou")
                K={k:rec["metodos"][v]["kt_gross"] for k,v in methods.items()}
                rr=rec["metodos"][methods["C"]]["sigma_rr_sobre_T"]
                if any(not math.isfinite(v) or v<=1.5 or v>=7 for v in K.values()):
                    raise ValueError("Kt não finito ou fora do intervalo de diagnóstico")
                if abs(K["A"]-comp["recovery"]["kt_gross_gradiente_direto"])>1e-8:
                    raise ValueError("Gradiente de bordo A não coincide")
                oldcase=baseline[(ha,lw,n)]
                oq=oldcase["qualidade_nova"]
                current={
                    "H_over_a":ha,"d_over_W":rho,"L_over_W":lw,"n":n,
                    "elementos_Q8":geo["elementos"],"nos":geo["nos"],"dofs":geo["dofs_totais"],
                    "anel":meta,"conformidade_interface":conformity,
                    "qualidade_nova":geo,"qualidade_anterior":oq,
                    "Kt_gross_novo":K,"Kt_net_novo":{k:v*(1-rho) for k,v in K.items()},
                    "Kt_gross_anterior":oldcase["Kt_gross_novo"],
                    "Kt_net_anterior":oldcase["Kt_net_novo"],
                    "sigma_rr_C_novo":rr,
                    "sigma_rr_C_anterior":oldcase["sigma_rr_C_novo"],
                    "spread_Kt_bruto_ABC":rec["sensibilidade"]["amplitude_entre_metodos_Kt_bruto"],
                    "controles_Kirsch":rec["controle_analitico_Kirsch"],
                    "hash_msh2":checksum,
                    "hash_msh2_baseline":oldcase["hash_msh2"],
                    "equilibrio_reacoes_rel":eq,"deslocamentos_elmer_scipy_rel_max":diff,
                    "forca_resultante_quadrante_N":1e7*H*.005,
                    "comparativos":{
                        "melhora_global":geo["razão_max_min_cordas_geral_max"]<oq["razão_max_min_cordas_geral_max"],
                        "melhora_primeira_faixa":geo["razão_max_min_cordas_primeira_faixa_max"]<oq["razão_max_min_cordas_primeira_faixa_max"],
                        "melhora_angulo_minimo":geo["angulo_minimo_vertices_graus_geral"]>oq["angulo_minimo_vertices_graus_geral"]+1e-9,
                        "melhora_tracao_livre_radial":abs(rr)<abs(oldcase["sigma_rr_C_novo"])
                    }
                }
                local.append(current);rows.append(current)
            convergence={m:convergencia_condicionada([(r["n"],r["Kt_gross_novo"][m]) for r in local])
                         for m in methods}
            finest=local[-1]
            series.append({
                "d_over_W":rho,"L_over_W":lw,"fine_n":48,
                "fine_quality_comparison":finest["comparativos"],
                "Kt_net_n48_C_novo":finest["Kt_net_novo"]["C"],
                "Kt_net_n48_C_anterior":finest["Kt_net_anterior"]["C"],
                "sigma_rr_C_n48_novo":finest["sigma_rr_C_novo"],
                "sigma_rr_C_n48_anterior":finest["sigma_rr_C_anterior"],
                "pior_ratio_global_novo":finest["qualidade_nova"]["razão_max_min_cordas_geral_max"],
                "pior_ratio_global_anterior":finest["qualidade_anterior"]["razão_max_min_cordas_geral_max"],
                "pior_ratio_furo_novo":finest["qualidade_nova"]["razão_max_min_cordas_primeira_faixa_max"],
                "pior_ratio_furo_anterior":finest["qualidade_anterior"]["razão_max_min_cordas_primeira_faixa_max"],
                "menor_angulo_novo":finest["qualidade_nova"]["angulo_minimo_vertices_graus_geral"],
                "menor_angulo_anterior":finest["qualidade_anterior"]["angulo_minimo_vertices_graus_geral"],
                "convergencia":convergence
            })
    if len(rows)!=16 or len(series)!=4:
        raise ValueError("Matriz experimental incompleta")
    return {
        "ciclo":20,"version":"0.20.0","num_modelos_elmer":16,
        "physics":"Elmer FEM plane stress; quarter plate, a=.01m, T=10MPa, E=200GPa, nu=.3; top and hole free",
        "topology":"6 transfinite Q8 surfaces: 2 inner annular, 2 rectangular interface, 2 outer blocks; identical physics",
        "baseline":"Ciclo19: same H/a L/W T E nu, 4-block annular mesh, 16 external runs",
        "reference_note":"Peterson long finite-width strip uses Kt_NET; NOT exact finite rectangle benchmark",
        "cases":rows,"series":series,
        "decision":"EXPERIMENTAL: never promote based on Kt or GCI alone; verify global aspect, local aspect, min-angle and free-hole traction.",
        "limitations":[
            "Aspect ratio is proxy based on vertex chords; not full Q8 isoparametric conditioning.",
            "Richardson/GCI calculated only if 4 levels meet order and monotonicity gates.",
            "Local improvement of Kt and radial-free traction requires independent validation.",
            "No pin, welded part, material failure, fatigue, plasticity or real mine components."
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pasta",required=True)
    a=p.parse_args()
    report=consolidar(a.pasta)
    out=Path(a.pasta)/"resumo_ciclo20.json"
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"ciclo":20,"models":len(report["cases"]),"series":[
        {"rho":s["d_over_W"],"lw":s["L_over_W"],
         "gates":s["fine_quality_comparison"],
         "ratio_global":s["pior_ratio_global_novo"],
         "ratio_hole":s["pior_ratio_furo_novo"],
         "sigma_rr":s["sigma_rr_C_n48_novo"],
         "Kt_net_C":s["Kt_net_n48_C_novo"],
         "GCI_C":s["convergencia"]["C"]["GCI_fino_relativo"]}
          for s in report["series"]]},indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
