"""Ciclo 16: diagnostico de qualidade Q8 e convergencia condicionada.

Sem validacao experimental nem extrapolacao Richardson/GCI automatica se
nao houver evidencia de tendencia monotona e estabilidade da ordem observada.
"""
from __future__ import annotations

import math
from pathlib import Path

from .gmsh_chapa import importar_msh2


def qualidade_geometrica(path:str|Path, *, a:float,H:float,L:float,
                         nr:int,nt:int)->dict:
    """Métricas dos lados definidos pelos vértices Q8 (proxies geometricos).

    Jacobiano verdadeiro Q8 ja calculado na importação Gmsh. Razão entre
    cordas de arestas não equivale à qualidade do elemento curvo completo.
    """
    mesh=importar_msh2(Path(path).read_text(encoding="utf-8"),a=a,H=H,Hx=L,
                      nr=nr,nt=nt)
    all_ratios=[]
    near_ratios=[]
    all_angles=[]
    near_angles=[]
    near_count=0
    for conn in mesh["elements"].values():
        ps=[mesh["nodes"][n][:2] for n in conn[:4]]
        edges=[(ps[(i+1)%4][0]-ps[i][0],
                ps[(i+1)%4][1]-ps[i][1]) for i in range(4)]
        lengths=[math.hypot(*v) for v in edges]
        if min(lengths)<=0:
            raise ValueError("Lado Q8 de comprimento nulo")
        ratio=max(lengths)/min(lengths)
        all_ratios.append(ratio)
        corners=[]
        for i in range(4):
            p=ps[i]
            l=ps[(i-1)%4];r=ps[(i+1)%4]
            a0=(l[0]-p[0],l[1]-p[1])
            b0=(r[0]-p[0],r[1]-p[1])
            cosa=(a0[0]*b0[0]+a0[1]*b0[1])/(math.hypot(*a0)*math.hypot(*b0))
            corners.append(math.degrees(math.acos(max(-1.,min(1.,cosa)))))
        all_angles.append(min(corners))
        near=sum(abs(math.hypot(*p)-a)<a*1e-7 for p in ps)>=2
        if near:
            near_count+=1
            near_ratios.append(ratio)
            near_angles.append(min(corners))
    if near_count!=nt or len(all_ratios)!=nr*nt:
        raise ValueError(f"Primeira faixa junto ao furo incompleta: {near_count} vs nt={nt}")
    all_ratios.sort();near_ratios.sort()
    return {
        "elementos":len(mesh["elements"]),
        "nos":len(mesh["nodes"]),
        "dofs_totais":2*len(mesh["nodes"]),
        "faixa_mais_interna_elementos":near_count,
        "jacobianos_q8":mesh["quality"],
        "razão_max_min_cordas_geral_max":all_ratios[-1],
        "razão_max_min_cordas_geral_p95":all_ratios[int(.95*(len(all_ratios)-1))],
        "razão_max_min_cordas_primeira_faixa_max":near_ratios[-1],
        "razão_max_min_cordas_primeira_faixa_mediana":near_ratios[len(near_ratios)//2],
        "angulo_minimo_vertices_graus_geral":min(all_angles),
        "angulo_minimo_vertices_graus_primeira_faixa":min(near_angles),
        "arestas_tracionadas":len(mesh["right_edges"]),
        "arestas_topo_livre":len(mesh["top_edges"]),
        "arestas_furo_livre":len(mesh["hole_edges"]),
        "observacao":"Aspect ratio por cordas dos quatro vertices; nao mede curvatura das arestas Q8"
    }


def _fator_de_reducao(n0:int,n1:int,n2:int,p:float)->float:
    return (n0**(-p)-n1**(-p))/(n1**(-p)-n2**(-p))


def convergencia_condicionada(pontos:list[tuple[int,float]], *,
                              estabilidade_tolerancia:float=.40)->dict:
    """Quatro malhas para checar monotonicidade e consistencia de ordens.

    Extrapolacao + GCI (fator 1.25) somente se os dois tripletos observados
    apresentarem ordem positiva plausivel e relativa estabilidade.
    O GCI e uma estimativa de discretizacao condicionada, NAO limite fisico.
    """
    p=sorted((int(n),float(s)) for n,s in pontos)
    if len(p)!=4 or [n for n,_ in p]!=[24,32,40,48]:
        raise ValueError("Exigir quatro resultados: n=24,32,40,48")
    ns=[n for n,_ in p]
    ys=[y for _,y in p]
    if any(not math.isfinite(y) for y in ys):
        raise ValueError("Kt nao finito")
    deltas=[ys[i+1]-ys[i] for i in range(3)]
    relative_change=abs(deltas[-1])/max(abs(ys[-1]),1e-12)
    result={
      "n":ns,"valores":ys,"incrementos":deltas,
      "variacao_relativa_duas_mais_finas":relative_change,
      "monotonicidade":all(d>0 for d in deltas) or all(d<0 for d in deltas),
      "status":"nao_comprovada",
      "ordem_observada":None,
      "extrapolacao_richardson":None,
      "GCI_fino_relativo":None,
      "GCI_fator_seguranca":None,
      "razões_refinamento_n24_32_40_48":[32/24,40/32,48/40],
      "alertas":[]
    }
    if not result["monotonicidade"]:
        result["alertas"].append("Convergencia nao monotona: nao calcular GCI")
        return result

    def order(n0,n1,n2,y0,y1,y2):
        d0=y0-y1
        d1=y1-y2
        if d0*d1<=0 or abs(d1)<1e-14:
            return None
        target=d0/d1
        low=.05;hi=6.
        if not (_fator_de_reducao(n0,n1,n2,low)
                <target<_fator_de_reducao(n0,n1,n2,hi)):
            return None
        for _ in range(100):
            m=(low+hi)/2
            if _fator_de_reducao(n0,n1,n2,m)<target:low=m
            else:hi=m
        return (low+hi)/2
    order_coarse=order(ns[0],ns[1],ns[2],ys[0],ys[1],ys[2])
    order_fine=order(ns[1],ns[2],ns[3],ys[1],ys[2],ys[3])
    result["ordem_observada"]={"24_32_40":order_coarse,"32_40_48":order_fine}
    if order_coarse is None or order_fine is None:
        result["alertas"].append("Ordem positiva nao identificada nos dois tripletos")
        return result
    if not .5<=order_fine<=4:
        result["alertas"].append("Ordem fina fora da faixa conservadora 0.5..4")
        return result
    stability=abs(order_coarse-order_fine)/max(abs(order_fine),.1)
    result["estabilidade_ordem_relativa"]=stability
    if stability>estabilidade_tolerancia:
        result["alertas"].append("Ordens observadas instaveis entre dois tripletos")
        return result
    pval=order_fine
    h2=ns[2]**(-pval);h3=ns[3]**(-pval)
    extrap=(ys[3]*h2-ys[2]*h3)/(h2-h3)
    gci=1.25*abs(ys[3]-ys[2])/(abs(ys[3]) * ((ns[3]/ns[2])**pval-1.))
    if not math.isfinite(extrap) or not math.isfinite(gci):
        result["alertas"].append("Extrapolacao mal condicionada")
        return result
    result.update({
        "status":"estimativa_condicionada_ordem_estavel",
        "extrapolacao_richardson":extrap,
        "GCI_fino_relativo":gci,
        "GCI_fator_seguranca":1.25,
        "alertas":["GCI e indice numerico condicional, nao incerteza fisica ou experimental"]
    })
    return result
