"""Ciclo 21: auditar 16 FEM alinhados e 4 FEM de controle do ciclo 20.

Nenhum número é produzido sem MSH2, logs de solver, campo Elmer,
CSV de tração na parede e identidade física do caso de referência.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from engmec.convergencia_malha import qualidade_geometrica, convergencia_condicionada
from engmec.gmsh_chapa import importar_msh2
from engmec.multibloco_externo import verificar_seis_blocos


def _ler_caso(folder: Path, *, ha: int, lw: int, n: int,
              tipo: str, alpha: float) -> dict:
    files = ("model.geo","model.msh","case.sif","gmsh.log","solver.log",
             "comparison.json","recuperacao.json","deslocamentos_elmer.json",
             "tracao_furo.csv","tracao_furo.json","gauss_tensoes.csv")
    for file in files:
        if not (folder / file).is_file():
            raise FileNotFoundError(f"Evidência externa ausente: {folder / file}")
    c = json.loads((folder/"comparison.json").read_text(encoding="utf-8"))
    r = json.loads((folder/"recuperacao.json").read_text(encoding="utf-8"))
    w = json.loads((folder/"tracao_furo.json").read_text(encoding="utf-8"))
    H,L = .01*ha, .01*ha*lw
    if (c.get("topologia") != tipo or c.get("nr") != n
        or c.get("nt") != 2*n or
        not math.isclose(c.get("fracao_interface"),alpha,abs_tol=1e-12) or
        not math.isclose(c.get("H_over_a"),ha,abs_tol=1e-10) or
        not math.isclose(c.get("L_over_W"),lw,abs_tol=1e-10)):
        raise ValueError(f"Geometria/solução não corresponde à matriz: {folder}")
    msh=(folder/"model.msh").read_bytes()
    digest=hashlib.sha256(msh).hexdigest()
    if digest != c["mesh_sha256"]:
        raise ValueError("SHA256 de MSH2 incompatível")
    mesh=importar_msh2(msh.decode("utf-8"),a=.01,H=H,Hx=L,nr=n,nt=2*n)
    conf=verificar_seis_blocos(
        mesh,a=.01,Hy=H,Hx=L,nr=n,nt=2*n,
        modo_interface="alinhada" if tipo=="anel-seis-blocos-alinhado" else "geometrica",
        fracao_interface=alpha)
    q=qualidade_geometrica(folder/"model.msh",a=.01,H=H,L=L,nr=n,nt=2*n)
    if conf["anel"]["arestas_interface_conformes"] != 2*n or conf["interface_retangular_arestas_conformes"] != 2*n:
        raise ValueError("Falha de conformidade das interfaces")
    if (q["elementos"] != 2*n*n or q["jacobianos_q8"]["min_det_jacobiano_m2"] <= 0
        or q["arestas_furo_livre"] != 2*n or
        w["arestas_furo"] != 2*n or w["amostras"] != 4*n):
        raise ValueError("Malha ou cobertura da parede livre incompleta")
    if not all(math.isfinite(w[k]) and w[k]>=0 for k in (
        "tracao_vetorial_rms_T","tracao_vetorial_max_T",
        "sigma_rr_rms_T","sigma_rtheta_rms_T",
        "desvio_raio_interpolado_max_rel")
               if k!="desvio_raio_interpolado_max_rel"):
        raise ValueError("Resíduo de tração inválido")
    if not math.isfinite(w["desvio_raio_interpolado_max_rel"]):
        raise ValueError("Desvio de raio não finito")
    if (abs(c["tracao_furo_completa"]["tracao_vetorial_rms_T"]
            -w["tracao_vetorial_rms_T"]) > 1e-12):
        raise ValueError("Parede do furo diverge entre relatório e evidência")
    eq=c["scipy_reference"]["reacoes_equilibrio_x"]
    diff=max(abs(float(v["diff_rel"])) for v in c["point_displacements"].values())
    if not math.isfinite(eq) or eq>1e-8 or not math.isfinite(diff) or diff>1e-6:
        raise ValueError("Falha equilíbrio ou comparação Elmer/SciPy")
    methods={"A":"A_gradiente_bordo","B":"B_gauss_seis_coef",
             "C":"C_patch_ponderado_quatro_coef"}
    K={m:float(r["metodos"][key]["kt_gross"]) for m,key in methods.items()}
    if any(not math.isfinite(v) or not 1.5<v<7 for v in K.values()):
        raise ValueError("Kt inválido")
    return {
        "ha":ha,"lw":lw,"n":n,"topologia":tipo,"fracao":alpha,
        "mesh_sha256":digest,"qualidade":q,"conformidade":conf,
        "Kt_bruto":K,"Kt_liquido":{m:k*(1-1/ha) for m,k in K.items()},
        "tracao_furo":w,"equilibrio_rel":eq,"elmer_scipy_diff_rel":diff,
    }


def consolidar(root: str | Path, sweep: str | Path) -> dict:
    root=Path(root)
    sw=json.loads(Path(sweep).read_text(encoding="utf-8"))
    if sw["ciclo"]!=21 or sw["numero_malhas"]!=28 or len(sw["candidatos"])!=7:
        raise ValueError("Varredura CAD incompleta")
    alpha=float(sw["fracao_escolhida"])
    old=json.loads(Path("docs/dados/ciclo20-transicao-externa-2026-11-10.json")
                   .read_text(encoding="utf-8"))
    oldcases={(c["H_over_a"],int(c["L_over_W"]),c["n"]):c for c in old["cases"]}
    if len(oldcases)!=16:
        raise ValueError("Baseline ciclo 20 incompleta")
    rows=[];series=[]
    for ha in (4,8):
        for lw in (2,4):
            local=[]
            for n in (24,32,40,48):
                folder=root/f"ha-{ha}-lw-{lw}-n-{n}"
                c=_ler_caso(folder,ha=ha,lw=lw,n=n,
                            tipo="anel-seis-blocos-alinhado",alpha=alpha)
                oldcase=oldcases[(ha,lw,n)]
                prior=oldcase["qualidade_nova"]
                current=c["qualidade"]
                c["comparacao_ciclo20"]={
                    "ratio_global_novo_sobre_velho":(
                        current["razão_max_min_cordas_geral_max"] /
                        prior["razão_max_min_cordas_geral_max"]),
                    "angulo_min_novo_sobre_velho":(
                        current["angulo_minimo_vertices_graus_geral"] /
                        prior["angulo_minimo_vertices_graus_geral"]),
                    "ratio_furo_novo_sobre_velho":(
                        current["razão_max_min_cordas_primeira_faixa_max"] /
                        prior["razão_max_min_cordas_primeira_faixa_max"]),
                    "Kt_liquido_C_novo_menos_velho":(
                        c["Kt_liquido"]["C"] - oldcase["Kt_net_novo"]["C"]),
                }
                rows.append(c);local.append(c)
            baseline=_ler_caso(root/f"baseline-ha-{ha}-lw-{lw}-n-48",
                ha=ha,lw=lw,n=48,tipo="anel-seis-blocos",alpha=.5)
            prior_case=oldcases[(ha,lw,48)]
            if abs(baseline["Kt_liquido"]["C"]-
                   prior_case["Kt_net_novo"]["C"])>5e-5:
                raise ValueError("Baseline de 20 não foi reproduzida")
            fine=local[-1]
            ratio=fine["comparacao_ciclo20"]["ratio_global_novo_sobre_velho"]
            angle=fine["comparacao_ciclo20"]["angulo_min_novo_sobre_velho"]
            raw=fine["tracao_furo"]["tracao_vetorial_rms_T"]
            raw0=baseline["tracao_furo"]["tracao_vetorial_rms_T"]
            series.append({
                "H_over_a":ha,"d_over_W":1/ha,"L_over_W":lw,
                "lambda":alpha,
                "ratio_global_vs_c20":ratio,
                "angulo_min_vs_c20":angle,
                "furo_ratio_vs_c20":fine["comparacao_ciclo20"]["ratio_furo_novo_sobre_velho"],
                "tracao_parede_rms_novo_T":raw,
                "tracao_parede_rms_controle20_T":raw0,
                "tracao_parede_rms_vs_controle20":raw/max(raw0,1e-14),
                "tracao_parede_max_novo_T":fine["tracao_furo"]["tracao_vetorial_max_T"],
                "tracao_parede_max_controle20_T":baseline["tracao_furo"]["tracao_vetorial_max_T"],
                "Kt_net_C_novo":fine["Kt_liquido"]["C"],
                "Kt_net_C_anterior":prior_case["Kt_net_novo"]["C"],
                "gate_ambas_geometrias":ratio<1 and angle>1,
                "gate_tracao_rms":raw <= raw0,
                "controle_reexecutado":baseline,
                "gci_C":convergencia_condicionada([(r["n"],r["Kt_bruto"]["C"])
                                                  for r in local]),
            })
    if len(rows)!=16 or len(series)!=4:
        raise ValueError("Execução incompleta")
    return {
        "ciclo":21,"versao":"0.21.0",
        "num_modelos_externos_alinhados":16,
        "num_modelos_externos_controle20":4,
        "num_malhas_sweep":sw["numero_malhas"],
        "lambda_escolhida":alpha,
        "selecao_cad":sw,
        "fisica":"Chapa finita quarto, tensão plana, T=10 MPa, E=200 GPa, nu=.3, a=.01m",
        "comparacao":"mesma fisica e n; baseline reexecutada no solver atual",
        "cases":rows,"series":series,
        "gates":{
            "geometria_todos":all(s["gate_ambas_geometrias"] for s in series),
            "tracao_rms_todos":all(s["gate_tracao_rms"] for s in series),
        },
        "decisao":"experimental; não mudar dois-blocos mesmo se gates positivos",
        "limites":[
            "Proxies: razão de cordas e ângulo dos vértices, não condicionamento Q8 completo",
            "Tração forte na aresta por B@U, duas amostras Gauss/aresta; não reproduz automaticamente BC fraca",
            "FEM sem contato, fadiga, 3D, material real e ensaio; não autoriza liberação industrial",
            "Seleção por 7 candidatos não é prova de ótimo global; GCI é condicional",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pasta",required=True)
    p.add_argument("--sweep",required=True)
    args=p.parse_args()
    report=consolidar(args.pasta,args.sweep)
    target=Path(args.pasta)/"resumo_ciclo21.json"
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "ciclo":21,"modelos":len(report["cases"]),
        "gates":report["gates"],"lambda":report["lambda_escolhida"],
        "series":[{k:s[k] for k in ("d_over_W","L_over_W","ratio_global_vs_c20",
            "angulo_min_vs_c20","tracao_parede_rms_vs_controle20",
            "gate_ambas_geometrias","gate_tracao_rms")} for s in report["series"]]},
        ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
