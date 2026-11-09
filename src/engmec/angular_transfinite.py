"""Experimento angular sobre curvas transfinite de dois blocos Gmsh Q8.

No segundo bloco, a curva -5 é orientada do topo para o canto,
como Circle(7) do topo do furo para theta=45 graus. Usar Progression
q<1 torna a primeira célula (perto do topo) relativamente maior,
buscando reduzir anisotropia radial/tangencial sem tocar no CAD físico.
"""
from __future__ import annotations
import math


def aplicar_distribuicao_angular(geo:str, *,
                                modo:str="uniforme",nt:int=48,
                                fracao_extremidade:float=.7)->str:
    if modo not in ("uniforme","ampliada-topo"):
        raise ValueError("Distribuicao angular desconhecida")
    if modo=="uniforme":
        return geo
    if (isinstance(nt,bool) or not isinstance(nt,int) or nt<8 or nt%4
        or not math.isfinite(fracao_extremidade)
        or not .5<=fracao_extremidade<1):
        raise ValueError("Fracao angular/n invalido")
    anchor="Transfinite Curve {2,4,5,7} = Na+1;"
    if geo.count(anchor)!=1:
        raise ValueError("Gerador CAD nao corresponde ao modelo 2 blocos")
    # q^Na=frac<1; primeira célula da progressão é maior,
    # compensando parte da primeira camada radial perto de theta=90.
    qa=math.exp(math.log(fracao_extremidade)/(nt//2))
    snippet=f"""// Alternativa angular: curvas 7 e -5 orientadas do topo para theta=45
qa = {qa:.12g};
Transfinite Curve {{2,4}} = Na+1;
Transfinite Curve {{-5,7}} = Na+1 Using Progression qa;"""
    return geo.replace(anchor,snippet)


def q_angular(nt:int,frac:float=.7)->float:
    if isinstance(nt,bool) or not isinstance(nt,int) or nt<8 or nt%4:
        raise ValueError("nt invalido")
    if not math.isfinite(frac) or not .5<=frac<1:
        raise ValueError("fracao invalida")
    return math.exp(math.log(frac)/(nt//2))
