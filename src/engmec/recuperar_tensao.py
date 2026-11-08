"""Ciclo 14: três recuperações de tensão no MESMO campo Q8 de deslocamentos.

A) B@u diretamente no único elemento adjacente ao topo do furo.
B) mínimos quadrados de 6 parâmetros sobre pontos de Gauss 3x3 (sem pesos).
C) patch de 4 parâmetros ponderado por jacobiano físico e proximidade.

O método C é um ajuste experimental de patch, NÃO implementação certificada
de SPR/Zienkiewicz-Zhu ou projeção L2 global.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

from .fem2d_indep import _b_matrix, _gauss_3, _matriz_constitutiva
from .kirsch import tensoes_kirsch, deslocamentos_kirsch


def _levels(mesh:dict, *, a:float,H:float):
    corners={n for conn in mesh["elements"].values() for n in conn[:4]}
    nodes=mesh["nodes"]
    radial=sorted({round(nodes[n][1],12) for n in corners
                   if abs(nodes[n][0])<1e-11 and nodes[n][1]>=a-1e-11})
    angles=sorted({round(math.atan2(nodes[n][1],nodes[n][0]),12)
                   for n in corners if abs(math.hypot(*nodes[n][:2])-a)<1e-10})
    if len(radial)<5 or len(angles)<9 or radial[0]<=0:
        raise ValueError("Niveis angulares/radiais insuficientes no contorno")
    if not math.isclose(radial[0],a,abs_tol=1e-10):
        raise ValueError("Raio do furo incompatível")
    if abs(angles[-1]-math.pi/2)>1e-9:
        raise ValueError("Ponto de topo do furo ausente")
    dr=radial[1]-a
    dtheta=angles[-1]-angles[-2]
    if dr<=0 or dtheta<=0:
        raise ValueError("Passos de malha inválidos")
    return radial,angles,dr,dtheta


def _rotate(sig,theta:float,T:float):
    """(σtt, σrr, σrθ), adimensionais, em coordenadas polares."""
    sxx,syy,sxy=(float(sig[0]),float(sig[1]),float(sig[2]))
    sn,cs=math.sin(theta),math.cos(theta)
    tt=(sxx*sn*sn+syy*cs*cs-2*sxy*sn*cs)/T
    rr=(sxx*cs*cs+syy*sn*sn+2*sxy*sn*cs)/T
    rt=((syy-sxx)*sn*cs+sxy*(cs*cs-sn*sn))/T
    return tt,rr,rt


def _fit_patch(rows:list[dict],kind:str):
    """Fit independente por componente, com matriz de amostras igual."""
    import numpy as np
    u=np.asarray([row["u"] for row in rows],float)
    v=np.asarray([row["v"] for row in rows],float)
    if len(rows)<24:
        raise ValueError("Patch com amostras insuficientes")
    if kind=="gauss_seis_coef":
        X=np.column_stack((np.ones_like(u),u,u*u,v*v,u*v*v,v**4))
        weights=np.ones_like(u)
    elif kind=="patch_ponderado_quatro_coef":
        X=np.column_stack((np.ones_like(u),u,u*u,v*v))
        area=np.asarray([row["peso_area_m2"] for row in rows],float)
        # 3x3 Gauss: jacobiano geométrico * pesos quadratura.
        # Localiza patch sem fingir que se trata de projecao L2 global.
        weights=area/(1+0.15*u*u+0.15*v*v)
        weights=weights/max(weights)
    else:
        raise ValueError(f"Recuperador inexistente: {kind}")
    if not np.all(np.isfinite(weights)) or np.any(weights<=0):
        raise ValueError("Pesos de patch invalidos")
    W=np.sqrt(weights)
    Xw=X*W[:,None]
    cond=float(np.linalg.cond(Xw))
    if not math.isfinite(cond) or cond>1e10:
        raise ValueError(f"Patch numericamente mal condicionado: cond={cond:g}")
    observations={}
    for column in ("tt","rr","rt"):
        y=np.asarray([row[column] for row in rows],float)
        coef,res,rank,s=np.linalg.lstsq(Xw,y*W,rcond=None)
        if rank<X.shape[1]:
            raise ValueError("Patch sem posto completo")
        rms=float(np.sqrt(np.mean((X@coef-y)**2)))
        wrms=float(np.sqrt(np.sum(weights*(X@coef-y)**2)/np.sum(weights)))
        observations[column]={"contorno":float(coef[0]),
                              "rms":rms,"rms_ponderado":wrms}
    return {
        "kt_gross":observations["tt"]["contorno"],
        "sigma_rr_sobre_T":observations["rr"]["contorno"],
        "sigma_rt_sobre_T":observations["rt"]["contorno"],
        "residuo_tt_rms":observations["tt"]["rms"],
        "residuo_tt_rms_ponderado":observations["tt"]["rms_ponderado"],
        "amostras":len(rows),"numero_coeficientes":X.shape[1],
        "condicao_matriz":cond,"metodo":kind
    }


def _stress_at_boundary(mesh,disp,*,a:float,E:float,nu:float,T:float):
    import numpy as np
    nodes=mesh["nodes"]
    target=[n for n,(x,y,z) in nodes.items()
            if abs(x)<1e-10 and abs(y-a)<1e-10]
    if len(target)!=1:
        raise ValueError("Topo do furo não único")
    adjacent=[conn for conn in mesh["elements"].values() if target[0] in conn[:4]]
    if len(adjacent)!=1:
        raise ValueError("Furo sem elemento de contorno único")
    conn=adjacent[0]
    corner_idx=conn.index(target[0])
    natural=[(-1,-1),(1,-1),(1,1),(-1,1)][corner_idx]
    xy=np.asarray([nodes[n][:2] for n in conn])
    displacement=np.asarray([disp[n] for n in conn],float).reshape(16)
    B,det,point=_b_matrix(xy,*natural)
    stress=_matriz_constitutiva(E,nu)@(B@displacement)
    v=_rotate(stress,math.pi/2,T)
    return {"kt_gross":v[0],"sigma_rr_sobre_T":v[1],"sigma_rt_sobre_T":v[2],
            "jacobiano_vertice_m2":float(det),
            "metodo":"gradiente_elementar_no_vertice_Q8"}


def recuperar(mesh:dict,deslocamentos:dict,*,a:float=.01,H:float=.04,
              T:float=10e6,E:float=200e9,nu:float=.3):
    """3 métodos calculados sobre o mesmo vetor u. Retorna resumo, CSV auditável."""
    import numpy as np
    if not (a>0 and H>=3*a and T>0 and E>0 and math.isfinite(nu)):
        raise ValueError("Parametros fisicos invalidos")
    if set(deslocamentos)!=set(mesh["nodes"]):
        raise ValueError("Campo de deslocamento não cobre todos os nós")
    if not all(np.asarray(x).shape[0]>=2 and np.all(np.isfinite(x))
               for x in deslocamentos.values()):
        raise ValueError("Deslocamentos inválidos")
    radial,angular,dr,dt=_levels(mesh,a=a,H=H)
    patch_r=radial[3]
    patch_theta=angular[-4]
    alpha_max=(patch_r-a)/(H-a)
    D=_matriz_constitutiva(E,nu)
    direct=_stress_at_boundary(mesh,deslocamentos,a=a,E=E,nu=nu,T=T)
    kirsch_disp={n:deslocamentos_kirsch(x,y,a,T,E,nu)
                 for n,(x,y,z) in mesh["nodes"].items()}
    direct_kirsch=_stress_at_boundary(mesh,kirsch_disp,a=a,E=E,nu=nu,T=T)
    patch=[]
    analytical_patch=[]
    raw=[]
    jac_min=float("inf")
    for element,conn in mesh["elements"].items():
        xy=np.asarray([mesh["nodes"][n][:2] for n in conn],float)
        U=np.asarray([deslocamentos[n] for n in conn],float).reshape(16)
        for natural_r,wr in _gauss_3():
            for natural_s,ws in _gauss_3():
                B,det,pt=_b_matrix(xy,natural_r,natural_s)
                jac_min=min(jac_min,det)
                x,y=map(float,pt)
                rad=math.hypot(x,y);theta=math.atan2(y,x)
                sig=D@(B@U)
                tt,rr,rt=_rotate(sig,theta,T)
                weight=det*wr*ws
                alpha=(rad-a)/(H/max(math.cos(theta),math.sin(theta))-a)
                loc=(theta>=patch_theta-1e-9 and alpha<=alpha_max+1e-9)
                raw.append({"elemento":element,"xi":natural_r,"eta":natural_s,
                            "x_m":x,"y_m":y,"raio_m":rad,"theta_rad":theta,
                            "sxx_pa":float(sig[0]),"syy_pa":float(sig[1]),
                            "sxy_pa":float(sig[2]),"kt_tt":tt,
                            "sigma_rr_sobre_T":rr,"sigma_rt_sobre_T":rt,
                            "peso_area_m2":weight,"no_patch":int(loc)})
                if loc:
                    u=(rad-a)/dr
                    v=(math.pi/2-theta)/dt
                    entry={"u":u,"v":v,"tt":tt,"rr":rr,"rt":rt,
                           "peso_area_m2":weight}
                    patch.append(entry)
                    ana=tensoes_kirsch(x,y,a,T)
                    att,arr,art=_rotate((ana["sigma_xx_pa"],
                                       ana["sigma_yy_pa"],
                                       ana["sigma_xy_pa"]),theta,T)
                    analytical_patch.append({"u":u,"v":v,
                                             "tt":att,"rr":arr,"rt":art,
                                             "peso_area_m2":weight})
    if jac_min<=0 or len(patch)<24:
        raise ValueError(f"Malha insuficiente: jac={jac_min:g},amostras={len(patch)}")
    Bfit=_fit_patch(patch,"gauss_seis_coef")
    Cfit=_fit_patch(patch,"patch_ponderado_quatro_coef")
    refB=_fit_patch(analytical_patch,"gauss_seis_coef")
    refC=_fit_patch(analytical_patch,"patch_ponderado_quatro_coef")
    methods={"A_gradiente_bordo":direct,
             "B_gauss_seis_coef":Bfit,
             "C_patch_ponderado_quatro_coef":Cfit}
    vals=[m["kt_gross"] for m in methods.values()]
    if any(not math.isfinite(v) or abs(v)>20 for v in vals):
        raise ValueError("Recuperação fisicamente implausível")
    summary={
        "modelo":"mesma_malha_mesmos_deslocamentos_3_recuperacoes_de_tensao",
        "H_sobre_a":H/a,"elementos":len(mesh["elements"]),
        "nos":len(mesh["nodes"]),"gauss_total":len(raw),
        "patch_amostras":len(patch),"jacobiano_minimo_m2":jac_min,
        "passo_radial_primeira_camada_m":dr,"passo_angular_rad":dt,
        "patch_raio_limite_no_eixo_m":patch_r,
        "patch_angulo_inicial_rad":patch_theta,
        "metodos":methods,
        "sensibilidade":{
            "intervalo_minimo_Kt_bruto":min(vals),
            "intervalo_maximo_Kt_bruto":max(vals),
            "amplitude_entre_metodos_Kt_bruto":max(vals)-min(vals),
            "amplitude_relativa_media":(max(vals)-min(vals))/(sum(vals)/len(vals)),
            "tipo_intervalo":"amplitude deterministica de tres operadores; nao intervalo de confianca"
        },
        "controle_analitico_Kirsch":{
            "A_Kt_gradiente_em_deslocamentos_Kirsch_interpolados":direct_kirsch["kt_gross"],
            "B_Kt_ajuste_tensoes_Kirsch_exatas_amostradas":refB["kt_gross"],
            "C_Kt_ajuste_tensoes_Kirsch_exatas_amostradas":refC["kt_gross"],
            "B_bias":refB["kt_gross"]-3.,
            "C_bias":refC["kt_gross"]-3.,
            "A_bias":direct_kirsch["kt_gross"]-3.,
            "referencia_Kt":3.,
            "observacao":"Kirsch infinito controla algoritmos, nao resolve chapa quadrada finita"
        },
        "advertencias":[
            "Metodo A usa derivada FEM dentro de um unico elemento na parede livre.",
            "Metodo B extrapola 3x3 celulas locais com nove Gauss por elemento; seis coeficientes e pesos iguais.",
            "Metodo C ajusta quatro coeficientes, ponderando por jacobiano fisico, Gauss e distancia; nao e SPR Zienkiewicz-Zhu certificado.",
            "A amplitude entre tres estimativas nao e incerteza expandida nem tolerancia de projeto."
        ]
    }
    return summary,raw


def escrever_csv(path:str|Path,rows:list[dict])->None:
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        raise ValueError("Nenhum dado Gauss gerado")
    with p.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
