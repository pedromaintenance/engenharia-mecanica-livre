"""Chapas retangulares: separa comprimento x e largura y no benchmark de furo.

A geometria quadrada é idêntica ao ciclo 14 quando Hx=Hy. Para Hx>Hy,
mantém a malha Gmsh de dois blocos transfinite Q8 e move as duas
extremidades externas da face x=Hx mantendo a y=Hy.
"""
from __future__ import annotations

import math
from .gmsh_chapa import gerar_geo


def gerar_geo_retangular(*,a:float=.01,Hy:float=.04,Hx:float=.08,
                         nr:int=16,nt:int=32)->str:
    if (not all(math.isfinite(v) for v in (a,Hy,Hx))
        or a<=0 or Hy<3*a or Hx<Hy):
        raise ValueError("Exigir a>0, Hy>=3a, Hx>=Hy finitos")
    text=gerar_geo(raio_m=a,semilargura_m=Hy,nr=nr,nt=nt)
    if abs(Hx-Hy)<1e-15:
        return text
    square_4="Point(4) = { H,0,0,1 };"
    square_5="Point(5) = { H,H,0,1 };"
    if text.count(square_4)!=1 or text.count(square_5)!=1:
        raise ValueError("Regressao: ponto CAD nao encontrado")
    text=text.replace(square_4,"Point(4) = { L,0,0,1 };")
    text=text.replace(square_5,"Point(5) = { L,H,0,1 };")
    declaration=f"L = {Hx:.12g}; H = {Hy:.12g};"
    text=text.replace(f"H = {Hy:.12g};",declaration)
    return text


def kt_peterson_liquido(rho:float)->float:
    """Ajuste Peterson, CHAPA MUITO LONGA sob tração, base secao liquida.

    rho=d/W=a/Hy (diametro sobre largura total); NAO exato na chapa curta.
    """
    x=float(rho)
    if not 0<x<1 or not math.isfinite(x):
        raise ValueError("d/W precisa estar entre 0 e 1")
    return 3-3.14*x+3.667*x*x-1.527*x*x*x


def kt_peterson_bruto(rho:float)->float:
    """Converte referencia liquida para nominal de secao bruta T."""
    return kt_peterson_liquido(rho)/(1-rho)
