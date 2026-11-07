"""Ciclo 12 — compara 2 implementacoes FEM Q8 sobre malha Gmsh identica."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def comparar(base:str|Path)->dict:
    root=Path(base)
    samples=[]
    for H,n in ((4,16),(4,24),(8,16),(8,24)):
        key=f"ha-{H}-n-{n}"
        native_dir=root/"scipy"/key
        ccx_dir=root/"calculix"/key
        a=json.loads((native_dir/"resultado.json").read_text(encoding="utf-8"))
        b=json.loads((ccx_dir/"comparacao.json").read_text(encoding="utf-8"))
        report=a["resultado"]
        ccx=b["resultado"]
        if a["H_sobre_a"]!=H or a["nr"]!=n or b["entradas"]["nr"]!=n:
            raise ValueError(f"Metradados de malha/caso divergentes: {key}")
        if b["entradas"]["razao_semilargura_raio"]!=H:
            raise ValueError("Mesma geometria nao confirmada")
        hashes=[]
        for p in (native_dir/"model.msh",ccx_dir/"chapa_gmsh.msh"):
            hashes.append(hashlib.sha256(p.read_bytes()).hexdigest())
        if hashes[0]!=hashes[1]:
            raise ValueError(f"Arquivos .msh divergentes no par {key}")
        kt=report["kt_gross_gradiente_direto_bordo"]
        ref=ccx["kt_gross_estimado_superficie"]
        if not math.isfinite(kt) or not 2<kt<5:
            raise ValueError(f"Kt do solver independente invalido: {key}: {kt}")
        if not math.isfinite(ref) or not 2<ref<5:
            raise ValueError("CCX retornou pico extrapolado invalido")
        if abs(kt-ref)>.35:
            raise ValueError(f"Divergencia Q8/CCX >0.35 em Kt bruto: {key}, independente={kt}, CalculiX={ref}")
        if report["residuo_equilibrio_x_rel"]>1e-5 or report["residuo_algebraico_livre_rel"]>1e-6:
            raise ValueError("Equilibrio de forcas do solver independente insuficiente")
        samples.append({
            "caso":key,"H_sobre_a":H,"nr":n,"elementos":report["elementos"],
            "malha_sha256":hashes[0],
            "solver_independente":"NumPy/SciPy Q8 3x3 plane stress",
            "solver_referencia":"CalculiX CCX CPS8R",
            "Kt_gross_gradiente_direto_scipy":kt,
            "Kt_net_gradiente_direto_scipy":report["kt_net_gradiente_direto_bordo"],
            "Kt_gross_extrapolado_CCX":ref,
            "Kt_net_extrapolado_CCX":ccx["kt_net_estimado_superficie"],
            "diferenca_absoluta_Kt":kt-ref,
            "diferenca_relativa_Kt":(kt-ref)/ref,
            "Kt_Kirsch_amostrado_interpolacao":report["kt_kirsch_analitico_amostrado_interpolacao"],
            "Kt_proxy_Gauss_SciPy":report["kt_proxy_max_gauss_proximo_furo"],
            "Kt_proxy_Gauss_CCX":ccx["kt_interiores_primeira_camada"],
            "sigma_radial_parede_normalizada":report["s_rr_normalizada_no_bordo"],
            "sigma_cisalhamento_parede_normalizada":report["s_rt_normalizada_no_bordo"],
            "equilibrio_x_rel":report["residuo_equilibrio_x_rel"],
            "residuo_solver_livre_rel":report["residuo_algebraico_livre_rel"],
            "tempo_solver_independente_s":report["tempo_montagem_e_solve_s"],
            "DOF":report["graus_liberdade"]
        })
    return {
        "ciclo":12,
        "metodo":"Q8 autoral de elasticidade plana; matriz global esparsa SciPy, quadratura 3x3, resposta comparada a CPS8R/CalculiX",
        "mesma_malha_comprovada_por_hash_sha256":True,
        "mesmo_problema_fisico":True,
        "respostas":samples,
        "limitacoes":[
            "Dois solucionadores com implementacoes independentes, mas solver Q8 SciPy e prototipo educacional sem qualificacao externa",
            "Metodos de avaliacao de Kt diferentes: gradiente FE direto no contorno versus ajuste de seis coeficientes de tensoes de Gauss",
            "Nao isola somente diferenca de solver: inclui diferenca de quadratura (Q8 3x3 versus expansao interna CPS8R) e recuperacao de tensao",
            "A concordancia de Kt nao e validacao experimental; nao implica seguranca em chapas, olhais e manutencao industrial",
            "Solucao Kirsch infinita nao fornece valor exato da chapa quadrada finita",
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pasta",required=True)
    args=p.parse_args()
    result=comparar(args.pasta)
    dest=Path(args.pasta)/"resumo_ciclo12.json"
    dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
