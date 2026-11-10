"""Topologia Gmsh Q8 de quatro blocos: anel circular e transição retangular.

Fronteiras físicas idênticas às chapas dos ciclos 15-18.
Divisão radial em duas regiões; transfinite, arcos internos compartilhados
e únicos (sem nós pendentes). NÃO substitui validação de tensão superficial.
"""
from __future__ import annotations
import math


def parametros_anel(nr:int,nt:int,*,a:float=.01,Hy:float=.04,
                    Hx:float=.16,beta_externo:float=4.0)->dict:
    if (isinstance(nr,bool) or isinstance(nt,bool)
        or not isinstance(nr,int) or not isinstance(nt,int)
        or nr<16 or nr>48 or nt!=2*nr or nt%4):
        raise ValueError("Exigir 16<=nr<=48 e nt=2*nr, Q8")
    if not all(math.isfinite(x) for x in (a,Hy,Hx,beta_externo)):
        raise ValueError("Dimensão e beta precisam ser finitos")
    if not (a>0 and Hy>=3*a and Hx>=Hy and 0<beta_externo<=5):
        raise ValueError("Exigir a>0, Hy>=3a, Hx>=Hy e 0<beta<=5")
    ni=nr//2;no=nr-ni
    return {"a":a,"H":Hy,"L":Hx,"rm":2*a,
            "nr":nr,"nt":nt,"ni":ni,"no":no,"na":nt//2,
            "beta_externo":beta_externo,
            "q_externo":math.exp(beta_externo/no),
            "politica_anular":"ni intervalos uniformes entre a e 2a",
            "politica_exterior":"no intervalos geométricos: q_ext^no=exp(beta)"}


def gerar_geo_anel_quatro_blocos(*,a:float=.01,Hy:float=.04,Hx:float=.16,
                                 nr:int=24,nt:int=48,
                                 beta_externo:float=4.)->str:
    m=parametros_anel(nr,nt,a=a,Hy=Hy,Hx=Hx,beta_externo=beta_externo)
    return f"""// Ciclo 19: 2 blocos anulares + 2 externos (QUATRO superfícies físicas)
Mesh.MshFileVersion = 2.2;
Mesh.ElementOrder = 2;
Mesh.SecondOrderIncomplete = 1;
Mesh.RecombineAll = 1;
Mesh.Smoothing = 5;
a = {a:.12g}; H = {Hy:.12g}; L = {Hx:.12g};
rm = 2*a;
Ni = {m['ni']}; No = {m['no']}; Na = {m['na']};
qo = {m['q_externo']:.14g};
// Círculo interno: 1,2,3; exterior: 4,5,6; centro 7
Point(1) = {{ a,0,0,1 }};
Point(2) = {{ a/Sqrt(2),a/Sqrt(2),0,1 }};
Point(3) = {{ 0,a,0,1 }};
Point(4) = {{ L,0,0,1 }};
Point(5) = {{ L,H,0,1 }};
Point(6) = {{ 0,H,0,1 }};
Point(7) = {{ 0,0,0,1 }};
// Anel intermediário r_m = 2a: 8,9,10
Point(8) = {{ rm,0,0,1 }};
Point(9) = {{ rm/Sqrt(2),rm/Sqrt(2),0,1 }};
Point(10) = {{ 0,rm,0,1 }};
// Arcos: Orientações dos limites interiores e intermediários
Circle(11) = {{2,7,1}};
Circle(12) = {{3,7,2}};
Circle(13) = {{9,7,8}};
Circle(14) = {{10,7,9}};
// Raios do anel: de a a 2a
Line(21) = {{1,8}};
Line(22) = {{2,9}};
Line(23) = {{3,10}};
// Radiais externos: de r_m até contorno físico
Line(24) = {{8,4}};
Line(25) = {{9,5}};
Line(26) = {{10,6}};
// Contornos externos: tração direita e topo livre
Line(27) = {{4,5}};
Line(28) = {{5,6}};
// 101 e 102: somente anel próximo ao furo
Curve Loop(101) = {{21,-13,-22,11}};
Plane Surface(101) = {{101}};
Curve Loop(102) = {{22,-14,-23,12}};
Plane Surface(102) = {{102}};
// 103 e 104: transição anel -> retângulo
Curve Loop(103) = {{24,27,-25,13}};
Plane Surface(103) = {{103}};
Curve Loop(104) = {{25,28,-26,14}};
Plane Surface(104) = {{104}};
// Malha Q8 CONFORME: arcos compartilhados 13 e 14 são entidades únicas
Transfinite Curve {{21,22,23}} = Ni+1;
Transfinite Curve {{24,25,26}} = No+1 Using Progression qo;
Transfinite Curve {{11,12,13,14,27,28}} = Na+1;
Transfinite Surface {{101}} = {{1,8,9,2}};
Transfinite Surface {{102}} = {{2,9,10,3}};
Transfinite Surface {{103}} = {{8,4,5,9}};
Transfinite Surface {{104}} = {{9,5,6,10}};
Recombine Surface {{101,102,103,104}};
// ElmerGrid: um único material e cada BC um único Physical Curve tag
Physical Surface("elastic_domain", 101) = {{101,102,103,104}};
Physical Curve("traction_right", 201) = {{27}};
Physical Curve("symmetry_x_zero", 202) = {{23,26}};
Physical Curve("symmetry_y_zero", 203) = {{21,24}};
Physical Curve("traction_free_top", 204) = {{28}};
Physical Curve("traction_free_hole", 205) = {{11,12}};
"""


def verificar_anel_conforme(mesh:dict,*,a:float,nr:int,nt:int)->dict:
    """Checa arestas Q8 compartilhadas exatamente 2 vezes na interface r=2a."""
    radius=2*a
    tol=max(1e-10,1e-7*a)
    seen={}
    ring_nodes=set()
    for conn in mesh["elements"].values():
        if len(conn)!=8:
            raise ValueError("Somente Q8")
        faces=((0,4,1),(1,5,2),(2,6,3),(3,7,0))
        for i,j,k in faces:
            aa,bb,mid=conn[i],conn[k],conn[j]
            coords=[mesh["nodes"][n] for n in (aa,bb,mid)]
            if all(abs(math.hypot(x,y)-radius)<tol for x,y,z in coords):
                key=tuple(sorted((aa,bb)))
                if key in seen:
                    occurrences,mids=seen[key]
                    if mids!=mid:
                        raise ValueError("Nó intermediário Q8 diferente na mesma interface")
                    seen[key]=(occurrences+1,mid)
                else:
                    seen[key]=(1,mid)
                ring_nodes.update((aa,bb))
    if len(seen)!=nt or len(ring_nodes)!=nt+1:
        raise ValueError(f"Arco interno incompleto: {len(seen)} arestas, {len(ring_nodes)} vértices")
    if any(k!=2 for k,mid in seen.values()):
        raise ValueError("Hanging edge ou limite interno exposto: aresta não compartilhada 2 vezes")
    # Gmsh cria arcos convecivamente, sem nós coincidentes separados:
    edges=[(mesh["nodes"][a][0],mesh["nodes"][a][1]) for a in ring_nodes]
    xy=set((round(x,12),round(y,12)) for x,y in edges)
    if len(xy)!=len(edges):
        raise ValueError("Nós geométricos duplicados ao longo da interface circular")
    if mesh["quality"]["min_det_jacobiano_m2"]<=0:
        raise ValueError("Jacobiano Q8 negativo ou nulo")
    return {"raio_intermediario_m":radius,
            "arestas_interface_conformes":len(seen),
            "vertices_interface_unicos":len(ring_nodes),
            "incidencia_por_aresta":2,
            "jacobiano_minimo_m2":mesh["quality"]["min_det_jacobiano_m2"]}
