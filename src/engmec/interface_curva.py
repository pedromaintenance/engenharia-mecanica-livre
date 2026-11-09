"""Experimento CAD com interfaces de blocos internas curvas.

Duas superfícies Gmsh Transfinite (1 e 2) usam a mesma curva interna.
A forma exterior, o furo e as BCs permanecem IDENTICOS. O spline
interpolante pode degradar a qualidade: nenhum ganho e assumido.
"""
from __future__ import annotations
import math


def transformar_interface(geo:str,*,estrategia:str="reta",a:float=.01,
                         Hy:float=.04,Hx:float=.16)->str:
    if estrategia not in ("reta","curva"):
        raise ValueError("Interface deve ser reta ou curva")
    if estrategia=="reta":
        return geo
    if (not all(math.isfinite(v) for v in (a,Hy,Hx))
        or a<=0 or Hy<3*a or Hx<Hy):
        raise ValueError("Dimensoes de dominio invalidas")
    anchor="Line(3) = {5,2};"
    if geo.count(anchor)!=1:
        raise ValueError("A curva de interface Gmsh nao e uma linha unica conhecida")
    # Entrada do spline: sai do canto (Hx,Hy) com tangente ~45 graus,
    # passa pelo interior e chega ao ponto do furo theta=45 graus com
    # tangente ~45 graus. Os pontos 8..10 NAO fazem parte do contorno fisico.
    # O valor .25 é uma hipótese geométrica, não otimização por Kt.
    control="""// Interface de blocos alternativa: spline INTERNO, não limite físico
Point(8) = { L - 0.25*H, H - 0.25*H,0,1 };
Point(9) = { L/2, H/2,0,1 };
Point(10) = { 2*a/Sqrt(2), 2*a/Sqrt(2),0,1 };
"""
    if "L = " not in geo:
        # O caso quadrado usa apenas H, sem declaração L.
        control=control.replace("L - ", "H - ").replace("L/2","H/2")
    if any("Point("+str(k)+")" in geo for k in (8,9,10)):
        raise ValueError("IDs de pontos CAD reservados usados por outra entidade")
    return geo.replace(anchor,control+"Spline(3) = {5,8,9,10,2};")
