"""Estratégias radiais controladas para Gmsh transfinite de chapa com furo.

A política escalonada conserva q(n)^n = q_ref^n_ref, impedindo que a
progressão acumulada aumente exponencialmente com o refinamento.
Esta condição não garante por si só qualidade Q8: medir após malhar.
"""
from __future__ import annotations
import math


def razao_progressao(n:int, estrategia:str="fixa", *,
                     q_referencia:float=1.12, n_referencia:int=24)->float:
    if (isinstance(n,bool) or not isinstance(n,int) or n<4 or n>48
        or isinstance(n_referencia,bool) or not isinstance(n_referencia,int)
        or n_referencia<4
        or not math.isfinite(q_referencia)
        or not 1.<=q_referencia<=1.3):
        raise ValueError("n/q_ref/n_ref fora do domínio verificado")
    if estrategia=="fixa":
        return q_referencia
    if estrategia=="escalonada":
        return math.exp(n_referencia*math.log(q_referencia)/n)
    raise ValueError("Estratégia radial desconhecida: fixa ou escalonada")
