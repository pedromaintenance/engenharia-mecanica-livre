"""Ciclo 21: resíduo de tração na parede COMPLETA do furo Q8.

Usa o mesmo campo nodal de deslocamentos do Elmer, em pontos de Gauss
nas arestas internas Q8. Calcula sigma*n (normal e tangencial) no referencial
radial e documenta desvio geométrico do círculo interpolado.

A tração livre é condição natural do FEM em forma FRACA: resíduos fortes
ponto a ponto não são critérios de aceitação industrial nem erro certificado.
"""
from __future__ import annotations

import math
from .fem2d_indep import _b_matrix, _matriz_constitutiva


_FACES = ((0, 4, 1), (1, 5, 2), (2, 6, 3), (3, 7, 0))


def _natural(face: int, xi: float) -> tuple[float, float]:
    # Q8: lados na orientação positiva dos vértices CCW.
    return ((xi, -1.), (1., xi), (-xi, 1.), (-1., -xi))[face]


def medir_parede_furo(mesh: dict, deslocamentos: dict, *, a: float,
                      E: float, nu: float, T: float) -> tuple[dict, list[dict]]:
    """Duas amostras Gauss por aresta, em todo o quarto de furo [0, pi/2].

    Não usa extrapolação de patch e não reivindica `sigma_n=0` exato.
    """
    import numpy as np

    if not (a > 0 and T > 0 and E > 0 and
            all(math.isfinite(v) for v in (a, T, E, nu))):
        raise ValueError("Parâmetros físicos inválidos")
    if set(deslocamentos) != set(mesh["nodes"]):
        raise ValueError("Campo nodal incompleto")
    D = _matriz_constitutiva(E, nu)
    raw = mesh.get("hole_edges")
    if not raw:
        raise ValueError("Sem arestas de furo")
    hole = {}
    for n1, nm, n2 in raw:
        key = tuple(sorted((n1, n2)))
        if key in hole:
            raise ValueError("Aresta de furo duplicada")
        pts = [mesh["nodes"][n] for n in (n1, nm, n2)]
        if not all(abs(math.hypot(x, y) - a) <= max(1e-10, a * 1e-7)
                   for x, y, _ in pts):
            raise ValueError("Nó da parede do furo fora do círculo")
        hole[key] = nm
    adjacent = {}
    for eid, conn in mesh["elements"].items():
        if len(conn) != 8:
            raise ValueError("Somente Q8")
        for side, (i, m, j) in enumerate(_FACES):
            key = tuple(sorted((conn[i], conn[j])))
            if key not in hole:
                continue
            if conn[m] != hole[key] or key in adjacent:
                raise ValueError("Parede não conforme, duplicada ou com nó médio errado")
            adjacent[key] = (eid, conn, side)
    if set(adjacent) != set(hole):
        raise ValueError("Arestas do furo sem exatamente um elemento adjacente")

    rows = []
    for eid, conn, side in adjacent.values():
        xy = np.asarray([mesh["nodes"][n][:2] for n in conn], dtype=float)
        u = np.asarray([deslocamentos[n][:2] for n in conn], dtype=float)
        if not np.all(np.isfinite(u)):
            raise ValueError("Deslocamentos não finitos")
        u = u.reshape(16)
        for xi in (-1. / math.sqrt(3.), 1. / math.sqrt(3.)):
            r, s = _natural(side, xi)
            B, det, p = _b_matrix(xy, r, s)
            x, y = float(p[0]), float(p[1])
            radius = math.hypot(x, y)
            if radius <= 0:
                raise ValueError("Ponto de amostra degenerado")
            nx, ny = x / radius, y / radius
            # n=+er ou -er fornece a mesma sigma_rr e |t|.
            sx, sy, txy = map(float, D @ (B @ u))
            rr = (sx * nx * nx + sy * ny * ny + 2 * txy * nx * ny) / T
            rt = ((sy - sx) * nx * ny + txy * (nx * nx - ny * ny)) / T
            if not all(math.isfinite(v) for v in (rr, rt, det)):
                raise ValueError("Tensão do furo não finita")
            rows.append({
                "eid": eid, "face": side, "xi": xi,
                "theta_rad": math.atan2(y, x),
                "x_m": x, "y_m": y,
                "raio_interpolado_m": radius,
                "desvio_raio_rel": (radius - a) / a,
                "jacobiano_q8_m2": float(det),
                "sigma_rr_T": rr,
                "sigma_rtheta_T": rt,
                "tracao_resultante_T": math.hypot(rr, rt),
            })
    rows.sort(key=lambda v: v["theta_rad"])
    if len(rows) != 2 * len(hole):
        raise ValueError("Densidade de amostras incompleta")
    if rows[0]["theta_rad"] < -1e-10 or rows[-1]["theta_rad"] > math.pi / 2 + 1e-10:
        raise ValueError("Pontos fora do arco do quadrante")
    def rms(key):
        return math.sqrt(sum(v[key] ** 2 for v in rows) / len(rows))
    def mx(key):
        return max(abs(v[key]) for v in rows)
    magnitudes = sorted(v["tracao_resultante_T"] for v in rows)
    summary = {
        "metodo": "Q8 gradiente direto na aresta, Gauss 2 pontos por aresta, mesmo vetor u",
        "arestas_furo": len(hole), "amostras": len(rows),
        "tracao_vetorial_rms_T": rms("tracao_resultante_T"),
        "tracao_vetorial_max_T": max(magnitudes),
        "tracao_vetorial_p95_T": magnitudes[int(.95 * (len(magnitudes) - 1))],
        "sigma_rr_rms_T": rms("sigma_rr_T"),
        "sigma_rtheta_rms_T": rms("sigma_rtheta_T"),
        "sigma_rr_max_abs_T": mx("sigma_rr_T"),
        "sigma_rtheta_max_abs_T": mx("sigma_rtheta_T"),
        "desvio_raio_interpolado_max_rel": mx("desvio_raio_rel"),
        "jacobiano_min_amostras_m2": min(v["jacobiano_q8_m2"] for v in rows),
        "limites": "Resíduo FORTE amostrado, não forma fraca e não mede incerteza física",
    }
    return summary, rows
