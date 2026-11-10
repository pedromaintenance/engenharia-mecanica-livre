"""Ciclo 20: CAD experimental com anel circular e DUAS transições Q8.

O domínio e as condições físicas são idênticos aos do ciclo 19.
A interface adicional é um retângulo homotético em escala geométrica,
com X_m=sqrt(2*a*Hx), Y_m=sqrt(2*a*Hy). Não implica aceitação do FEM.
"""
from __future__ import annotations

import math

from .multibloco_anel import verificar_anel_conforme


def parametros_seis_blocos(nr: int, nt: int, *, a: float = .01,
                           Hy: float = .04, Hx: float = .16) -> dict:
    if (isinstance(nr, bool) or isinstance(nt, bool)
            or not isinstance(nr, int) or not isinstance(nt, int)
            or nr not in (16, 24, 32, 40, 48) or nt != 2 * nr):
        raise ValueError("Exigir nr em 16,24,32,40,48 e nt=2*nr")
    if not all(math.isfinite(x) for x in (a, Hy, Hx)):
        raise ValueError("Geometria não finita")
    if not (a > 0 and Hy >= 3 * a and Hx >= Hy):
        raise ValueError("Exigir a>0, Hy>=3a e Hx>=Hy")
    ni = nr // 2
    nm = nr // 4
    no = nr - ni - nm
    rm = 2 * a
    xm = math.sqrt(rm * Hx)
    ym = math.sqrt(rm * Hy)
    if not (rm < ym < Hy and rm < xm < Hx):
        raise ValueError("Retângulo intermediário não interno")
    return {
        "a": a, "H": Hy, "L": Hx, "rm": rm, "xm": xm, "ym": ym,
        "nr": nr, "nt": nt, "ni": ni, "nm": nm, "no": no, "na": nt // 2,
        "politica": "anel uniforme ni; transição uniforme nm; exterior uniforme no",
        "interface_intermediaria": "Xm=sqrt(2a*Hx), Ym=sqrt(2a*Hy)",
    }


def gerar_geo_seis_blocos(*, a: float = .01, Hy: float = .04,
                          Hx: float = .16, nr: int = 24, nt: int = 48) -> str:
    m = parametros_seis_blocos(nr, nt, a=a, Hy=Hy, Hx=Hx)
    return f"""// Ciclo 20 experimental: 2 anulares + 2 intermediários + 2 exteriores
Mesh.MshFileVersion = 2.2;
Mesh.ElementOrder = 2;
Mesh.SecondOrderIncomplete = 1;
Mesh.RecombineAll = 1;
Mesh.Smoothing = 5;
a={a:.14g}; H={Hy:.14g}; L={Hx:.14g};
rm=2*a; Xm={m['xm']:.16g}; Ym={m['ym']:.16g};
Ni={m['ni']}; Nm={m['nm']}; No={m['no']}; Na={m['na']};
// 1-3: furo. 4-6: bordo externo. 7: centro.
// 8-10: anel 2a. 11-13: interface retangular intermediária.
Point(1)={{a,0,0,1}};
Point(2)={{a/Sqrt(2),a/Sqrt(2),0,1}};
Point(3)={{0,a,0,1}};
Point(4)={{L,0,0,1}};
Point(5)={{L,H,0,1}};
Point(6)={{0,H,0,1}};
Point(7)={{0,0,0,1}};
Point(8)={{rm,0,0,1}};
Point(9)={{rm/Sqrt(2),rm/Sqrt(2),0,1}};
Point(10)={{0,rm,0,1}};
Point(11)={{Xm,0,0,1}};
Point(12)={{Xm,Ym,0,1}};
Point(13)={{0,Ym,0,1}};
Circle(11)={{2,7,1}};
Circle(12)={{3,7,2}};
Circle(13)={{9,7,8}};
Circle(14)={{10,7,9}};
// Radiais, comuns às duas superfícies de cada faixa
Line(21)={{1,8}};
Line(22)={{2,9}};
Line(23)={{3,10}};
Line(24)={{8,11}};
Line(25)={{9,12}};
Line(26)={{10,13}};
Line(27)={{11,4}};
Line(28)={{12,5}};
Line(29)={{13,6}};
// Curvas angulares intermediárias e exteriores
Line(30)={{11,12}};
Line(31)={{12,13}};
Line(32)={{4,5}};
Line(33)={{5,6}};
Curve Loop(101)={{21,-13,-22,11}};
Plane Surface(101)={{101}};
Curve Loop(102)={{22,-14,-23,12}};
Plane Surface(102)={{102}};
Curve Loop(103)={{24,30,-25,13}};
Plane Surface(103)={{103}};
Curve Loop(104)={{25,31,-26,14}};
Plane Surface(104)={{104}};
Curve Loop(105)={{27,32,-28,-30}};
Plane Surface(105)={{105}};
Curve Loop(106)={{28,33,-29,-31}};
Plane Surface(106)={{106}};
Transfinite Curve {{21,22,23}} = Ni+1;
Transfinite Curve {{24,25,26}} = Nm+1;
Transfinite Curve {{27,28,29}} = No+1;
Transfinite Curve {{11,12,13,14,30,31,32,33}} = Na+1;
Transfinite Surface {{101}} = {{1,8,9,2}};
Transfinite Surface {{102}} = {{2,9,10,3}};
Transfinite Surface {{103}} = {{8,11,12,9}};
Transfinite Surface {{104}} = {{9,12,13,10}};
Transfinite Surface {{105}} = {{11,4,5,12}};
Transfinite Surface {{106}} = {{12,5,6,13}};
Recombine Surface {{101,102,103,104,105,106}};
Physical Surface("elastic_domain", 101) = {{101,102,103,104,105,106}};
Physical Curve("traction_right", 201) = {{32}};
Physical Curve("symmetry_x_zero", 202) = {{23,26,29}};
Physical Curve("symmetry_y_zero", 203) = {{21,24,27}};
Physical Curve("traction_free_top", 204) = {{33}};
Physical Curve("traction_free_hole", 205) = {{11,12}};
"""


def verificar_seis_blocos(mesh: dict, *, a: float, Hy: float,
                         Hx: float, nr: int, nt: int) -> dict:
    """Verifica interfaces Q8 CONFORMES no anel e no retângulo interno.

    Cada aresta de interface aparece duas vezes, com nó médio ID idêntico.
    Exige contornos físicos e jacobianos positivos obtidos do importador.
    """
    m = parametros_seis_blocos(nr, nt, a=a, Hy=Hy, Hx=Hx)
    annulus = verificar_anel_conforme(mesh, a=a, nr=nr, nt=nt)
    tol = max(1e-10, 1e-8 * max(Hx, Hy))
    edges = {}
    nodes = set()
    for conn in mesh["elements"].values():
        if len(conn) != 8:
            raise ValueError("Apenas Q8")
        for i, mid_i, j in ((0, 4, 1), (1, 5, 2), (2, 6, 3), (3, 7, 0)):
            v1, vm, v2 = conn[i], conn[mid_i], conn[j]
            pts = [mesh["nodes"][idx] for idx in (v1, vm, v2)]
            # Parede direita OU topo da interface retangular parcial.
            vertical = all(abs(x - m["xm"]) < tol and -tol <= y <= m["ym"] + tol
                           for x, y, _ in pts)
            horizontal = all(abs(y - m["ym"]) < tol and -tol <= x <= m["xm"] + tol
                             for x, y, _ in pts)
            if not (vertical or horizontal):
                continue
            key = tuple(sorted((v1, v2)))
            if key in edges:
                count, previous_mid = edges[key]
                if previous_mid != vm:
                    raise ValueError("Nó médio duplicado na interface retangular")
                edges[key] = (count + 1, vm)
            else:
                edges[key] = (1, vm)
            nodes.update((v1, v2))
    if len(edges) != nt or len(nodes) != nt + 1:
        raise ValueError(f"Interface retangular incompleta: {len(edges)} arestas, {len(nodes)} nós")
    if any(count != 2 for count, _ in edges.values()):
        raise ValueError("Interface retangular com hanging edge")
    xy = {(round(mesh["nodes"][i][0], 12), round(mesh["nodes"][i][1], 12))
          for i in nodes}
    if len(xy) != len(nodes):
        raise ValueError("Nós de mesmo ponto físico com IDs distintos")
    if not (len(mesh["right_edges"]) == nt // 2
            and len(mesh["top_edges"]) == nt // 2
            and len(mesh["hole_edges"]) == nt
            and len(mesh["elements"]) == nr * nt):
        raise ValueError("Contornos ou elementos inconsistentes")
    return {
        "anel": annulus,
        "interface_retangular_arestas_conformes": len(edges),
        "interface_retangular_vertices_unicos": len(nodes),
        "incidencias_por_aresta": 2,
        "xm_m": m["xm"], "ym_m": m["ym"],
    }
