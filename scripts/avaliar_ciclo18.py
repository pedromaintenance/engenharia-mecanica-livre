"""Ciclo 18 — efeito da distribuição angular em chapas com furo.

Compara novo Gmsh Q8 a baseline radial-escalonado/angulo uniforme do ciclo 17.
Não confunde qualidade geométrica global, tração livre e erro do pico Kt.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from engmec.convergencia_malha import qualidade_geometrica,convergencia_condicionada
from engmec.angular_transfinite import q_angular
from engmec.progressao_radial import razao_progressao


def consolidar(root:str|Path)->dict:
    root=Path(root)
    old=json.loads(Path("docs/dados/ciclo17-malha-radial-2026-11-08.json").read_text(encoding="utf-8"))
    prior={(r["ha"],int(r["L_over_W"]),r["n"]):r for r in old["cases"]}
    if len(prior)!=16:
        raise ValueError("Dataset anterior sem 16 baselines")
    result=[];series=[]
    fields={"A":"A_gradiente_bordo","B":"B_gauss_seis_coef","C":"C_patch_ponderado_quatro_coef"}
    for ha in (4,8):
        H=.01*ha;rho=1/ha
        for lw in (2,4):
            L=H*lw
            cases=[]
            for n in (24,32,40,48):
                folder=root/f"ha-{ha}-lw-{lw}-n-{n}"
                c=json.loads((folder/"comparison.json").read_text(encoding="utf-8"))
                stress=json.loads((folder/"recuperacao.json").read_text(encoding="utf-8"))
                if c.get("distribuicao_angular")!="ampliada-topo" or c.get("estrategia_progressao_radial")!="escalonada":
                    raise ValueError("Regime de geometria da nova malha incorreto")
                if c["nr"]!=n or c["nt"]!=2*n or not math.isclose(c["H_over_a"],ha) or not math.isclose(c["L_over_W"],lw) or not math.isclose(c["d_over_W"],rho):
                    raise ValueError("Geometria fisica, malha ou denominador incorreto")
                if not math.isclose(c["q_radial_efetivo"],razao_progressao(n,"escalonada"),rel_tol=1e-10):
                    raise ValueError("A politica radial anterior nao foi preservada")
                if stress["elementos"]!=2*n*n or stress["gauss_total"]!=18*n*n:
                    raise ValueError("Elementos Q8 / Gauss 3x3 incompletos")
                for file in ("model.geo","model.msh","case.sif","solver.log","deslocamentos_elmer.json","gauss_tensoes.csv","recuperacao.json"):
                    if not (folder/file).is_file():
                        raise ValueError(f"Falta evidencia: {file}")
                mbytes=(folder/"model.msh").read_bytes()
                digest=hashlib.sha256(mbytes).hexdigest()
                if digest!=c["mesh_sha256"]:
                    raise ValueError("SHA256 da malha nao reproduzido")
                oldr=prior[(ha,lw,n)]
                if digest==oldr["mesh_sha256_escalonada"]:
                    raise ValueError("Distribuição angular não alterou a malha")
                qual=qualidade_geometrica(folder/"model.msh",a=.01,H=H,L=L,nr=n,nt=2*n)
                if qual["arestas_tracionadas"]!=n or qual["arestas_topo_livre"]!=n or qual["arestas_furo_livre"]!=2*n:
                    raise ValueError("Fronteiras fisicas nao preservadas")
                eq=c["scipy_reference"]["reacoes_equilibrio_x"]
                du=max(abs(v["diff_rel"]) for v in c["point_displacements"].values())
                if not math.isfinite(eq) or eq>1e-8 or du>1e-6:
                    raise ValueError("Divergencia de equilibrio / FEM Elmer e SciPy")
                K={k:stress["metodos"][tag]["kt_gross"] for k,tag in fields.items()}
                if any(not math.isfinite(v) or not 1.5<v<6. for v in K.values()):
                    raise ValueError("Kt invalido")
                if abs(K["A"]-c["recovery"]["kt_gross_gradiente_direto"])>1e-8:
                    raise ValueError("Gradiente direto inconsistente")
                rr=stress["metodos"][fields["C"]]["sigma_rr_sobre_T"]
                oq=oldr["qualidade_escalonada"]
                row={
                    "H_sobre_a":ha,"d_sobre_W":rho,"L_sobre_W":lw,"n":n,
                    "elementos":qual["elementos"],"nos":qual["nos"],"dofs":qual["dofs_totais"],
                    "q_radial":c["q_radial_efetivo"],"q_angular":q_angular(2*n),
                    "Kt_gross":K,"Kt_net":{k:v*(1-rho) for k,v in K.items()},
                    "Kt_gross_old":oldr["Kt_gross_escalonada"],
                    "Kt_net_old":oldr["Kt_liquido_escalonada"],
                    "sigma_rr_C":rr,"sigma_rr_C_old":oldr["sigma_rr_C_escalonada"],
                    "spread_ABC":stress["sensibilidade"]["amplitude_entre_metodos_Kt_bruto"],
                    "qualidade_nova":qual,"qualidade_antiga":oq,
                    "mesh_sha256":digest,"mesh_sha256_old":oldr["mesh_sha256_escalonada"],
                    "equilibrio_rel":eq,"diff_deslocamento_elmer_scipy":du,
                    "resultante_N":1e7*H*.005,
                    "k_controles_kirsch":stress["controle_analitico_Kirsch"],
                    "gates_qualidade":{
                       "melhora_ratio_global":qual["razão_max_min_cordas_geral_max"]<oq["razão_max_min_cordas_geral_max"],
                       "melhora_ratio_proximo_furo":qual["razão_max_min_cordas_primeira_faixa_max"]<oq["razão_max_min_cordas_primeira_faixa_max"],
                       "melhora_angulo_global":qual["angulo_minimo_vertices_graus_geral"]>oq["angulo_minimo_vertices_graus_geral"]+1e-9,
                       "melhora_sigma_rr":abs(rr)<abs(oldr["sigma_rr_C_escalonada"])
                    }
                }
                cases.append(row);result.append(row)
            conv={}
            for met in fields:
                conv[met]=convergencia_condicionada([(row["n"],row["Kt_gross"][met]) for row in cases])
            r=cases[-1]
            series.append({
                "d_sobre_W":rho,"L_sobre_W":lw,
                "Kt_net_C_n48_novo":r["Kt_net"]["C"],"Kt_net_C_n48_antigo":r["Kt_net_old"]["C"],
                "qualidade_n48":{"nova":r["qualidade_nova"],"antiga":r["qualidade_antiga"]},
                "sigma_rr_n48_novo":r["sigma_rr_C"],"sigma_rr_n48_antigo":r["sigma_rr_C_old"],
                "gates_n48":r["gates_qualidade"],"convergencia":conv
            })
    if len(result)!=16 or len(series)!=4:
        raise ValueError("Experimento incompleto")
    return {
        "ciclo":18,"modelos_externos":16,"versao":"0.18.0",
        "hipotese":"Alargar a primeira celula angular na metade superior da parede do furo pode reduzir anisotropia local; deve ser verificado",
        "politica":{ "radial":"escalonada, q^n=1.12^24",
          "angular":"ampliada-topo, q_ang^(nt/2)=0.7; curvas -5 e 7, primeiro segmento maior perto de theta=90",
          "interface_blocos":"reta (sem mudança da topologia CAD)" },
        "modelo_fisico":"chapa retangular elastica 2D tensao plana, H/a=4,8, L/W=2,4, a=0.01m, E=200GPa, nu=0.3, T=10MPa",
        "diagnosticos":"aspect ratio por cordas global e primeira faixa, angulos nos vertices, residuo sigma_rr/T, Kt bruto e liquido A/B/C, GCI condicional, equilibrio, hash MSH",
        "casos":result,"series":series,
        "tentativa_rejeitada":{
            "descricao":"alterar Line(3) interna para uma Spline com pontos de controle",
            "motivo":"malhas n24 de L/W=4 com jacobianos Q8 nao positivos em smoke Gmsh; nao se executou FEM nesses casos",
            "conclusao":"nao publicar esta geometria como opcao FEM; necessita redesenho multibloco ou restricoes CAD"
        },
        "limites":["Uma malha menos anisotropica nao prova menor erro no Kt verdadeiro.",
                  "GCI condicional nao inclui erro de tracao superficial, propriedades reais ou plasticidade.",
                  "Comparacao permanece educacional; sem pino, contato, fadiga, solda ou validacao fisica."]
    }


def main():
    p=argparse.ArgumentParser();p.add_argument("--pasta",required=True);a=p.parse_args()
    d=consolidar(a.pasta)
    target=Path(a.pasta)/"resumo_ciclo18.json"
    target.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"ciclo":18,"modelos":len(d["casos"]),
        "series":[{"rho":s["d_sobre_W"],"lw":s["L_sobre_W"],
          "Kt_C_n48_new":s["Kt_net_C_n48_novo"],
          "Kt_C_n48_old":s["Kt_net_C_n48_antigo"],
          "ratio_near_new":s["qualidade_n48"]["nova"]["razão_max_min_cordas_primeira_faixa_max"],
          "ratio_near_old":s["qualidade_n48"]["antiga"]["razão_max_min_cordas_primeira_faixa_max"],
          "angle_min_new":s["qualidade_n48"]["nova"]["angulo_minimo_vertices_graus_geral"],
          "angle_min_old":s["qualidade_n48"]["antiga"]["angulo_minimo_vertices_graus_geral"],
          "rr_new":s["sigma_rr_n48_novo"],"rr_old":s["sigma_rr_n48_antigo"],
          "gates":s["gates_n48"],"GCI_C":s["convergencia"]["C"]["GCI_fino_relativo"]}
          for s in d["series"]]},indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
