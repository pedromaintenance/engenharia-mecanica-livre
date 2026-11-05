"""Benchmark didático FEM 1D: barra elástica linear, área e E constantes.

Equação de equilíbrio: -(EAu')'=q, u(0)=0 e EA u'(L)=F.
Não implementa instabilidade, plasticidade, geometria 3D nem restrições industriais.
"""
from __future__ import annotations
from math import isfinite, sqrt


def _numero(nome: str, valor: float, positivo: bool = False) -> float:
    try:
        v = float(valor)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{nome} inválido") from exc
    if not isfinite(v) or (positivo and v <= 0):
        raise ValueError(f"{nome}: valor finito {'positivo' if positivo else 'necessário'}")
    return v


def barra_axial(
    comprimento_m: float, area_mm2: float, e_gpa: float,
    forca_n: float = 0.0, carga_linear_n_m: float = 0.0, elementos: int = 4
) -> dict:
    """Resolve FEM com elementos lineares e força distribuída nodal consistente.

    Solver tridiagonal Thomas; sem biblioteca externa. Resultados em unidades SI.
    """
    L = _numero("comprimento_m", comprimento_m, True)
    A = _numero("area_mm2", area_mm2, True) * 1e-6
    E = _numero("e_gpa", e_gpa, True) * 1e9
    F = _numero("forca_n", forca_n)
    q = _numero("carga_linear_n_m", carga_linear_n_m)
    if isinstance(elementos, bool) or not isinstance(elementos, int) or not (1 <= elementos <= 2000):
        raise ValueError("elementos deve ser inteiro entre 1 e 2000")
    n = elementos
    h = L / n
    k = E * A / h
    if not isfinite(k) or k <= 0:
        raise ValueError("rigidez não finita: escale os parâmetros")
    # Nós 0...n; nó 0 prescrito, incógnitas 1...n.
    diagonal = [2 * k] * (n - 1) + [k]
    superior = [-k] * (n - 1)
    cargas = [q * h] * (n - 1) + [q * h / 2 + F]
    if not all(isfinite(v) for v in cargas):
        raise ValueError("Carregamento não finito: escale os parâmetros")

    # Eliminação para matriz tridiagonal simétrica SPD.
    for i in range(1, n):
        fator = -k / diagonal[i - 1]
        diagonal[i] -= fator * superior[i - 1]
        cargas[i] -= fator * cargas[i - 1]
        if not isfinite(diagonal[i]) or diagonal[i] <= 0:
            raise ValueError("Sistema mal condicionado numericamente")
    deslocamentos = [0.0] * (n + 1)
    deslocamentos[n] = cargas[n - 1] / diagonal[n - 1]
    for i in range(n - 2, -1, -1):
        deslocamentos[i + 1] = (cargas[i] + k * deslocamentos[i + 2]) / diagonal[i]

    def u_exato(x: float) -> float:
        return ((F + q * L) * x - 0.5 * q * x * x) / (E * A)

    def sigma_exata(x: float) -> float:
        return (F + q * (L - x)) / A

    tensoes = []
    somatorio_erro = 0.0
    energia = 0.0
    trabalho = F * deslocamentos[-1]
    for i in range(n):
        du = deslocamentos[i + 1] - deslocamentos[i]
        sigma = E * du / h
        tensoes.append(sigma)
        energia += 0.5 * k * du * du
        trabalho += q * h * (deslocamentos[i] + deslocamentos[i + 1]) / 2
        # Quadratura de Gauss 2 pontos: integral exata do erro linear².
        meio = (i + 0.5) * h
        d = h / (2 * sqrt(3))
        erro1 = sigma - sigma_exata(meio - d)
        erro2 = sigma - sigma_exata(meio + d)
        somatorio_erro += h * (erro1 * erro1 + erro2 * erro2) / 2

    reacao = -k * deslocamentos[1] - q * h / 2
    deslocamento_exato = u_exato(L)
    erro_nodal = max(abs(v - u_exato(i * h)) for i, v in enumerate(deslocamentos))
    return {
        "modelo": "barra_axial_fem_1d_linear_elastico",
        "entradas_si": {
            "comprimento_m": L, "area_m2": A, "e_pa": E,
            "forca_ponta_n": F, "carga_distribuida_n_m": q,
            "elementos": n
        },
        "resultados_si": {
            "deslocamento_ponta_m": deslocamentos[-1],
            "deslocamento_ponta_analitico_m": deslocamento_exato,
            "reacao_apoio_n": reacao,
            "posicoes_nos_m": [i * h for i in range(n + 1)],
            "deslocamentos_nos_m": deslocamentos,
            "tensoes_elementos_pa": tensoes,
            "energia_deformacao_j": energia,
            "trabalho_externo_j": trabalho
        },
        "verificacao": {
            "erro_ponta_absoluto_m": abs(deslocamentos[-1] - deslocamento_exato),
            "erro_nodal_max_m": erro_nodal,
            "erro_equilibrio_forcas_n": abs(reacao + F + q * L),
            "erro_trabalho_energia_j": abs(2 * energia - trabalho),
            "erro_tensao_rms_pa": sqrt(somatorio_erro / L),
            "referencia_tensao_apoiada_pa": sigma_exata(0),
            "referencia_tensao_na_ponta_pa": sigma_exata(L)
        },
        "hipoteses": [
            "Pequenas deformações, elasticidade linear, seção e módulo constantes",
            "Barra unidimensional de tração/compressão com deslocamento u(0)=0",
            "Força axial concentrada na ponta e força distribuída q em N/m",
            "Elementos lineares, carregamento consistente e integração analítica",
            "Sem peso próprio salvo se modelado explicitamente em q"
        ],
        "aviso": "Modelo acadêmico. Não verifica flambagem, fadiga, plasticidade, tensões locais, conexões ou segurança de equipamento."
    }


def estudo_refinamento(
    comprimento_m: float, area_mm2: float, e_gpa: float,
    forca_n: float, carga_linear_n_m: float,
    malhas: tuple[int, ...] = (1, 2, 4, 8, 16, 32)
) -> dict:
    """Estudo de h: com q uniforme os deslocamentos nodais já são exatos.

    O erro RMS de tensão é uma grandeza não trivial que converge como O(h).
    """
    if not malhas or any(not isinstance(n, int) or n < 1 or n > 2000 for n in malhas):
        raise ValueError("malhas inválidas")
    resultados = []
    for n in malhas:
        r = barra_axial(comprimento_m, area_mm2, e_gpa, forca_n, carga_linear_n_m, n)
        resultados.append({
            "elementos": n,
            "deslocamento_ponta_m": r["resultados_si"]["deslocamento_ponta_m"],
            **r["verificacao"]
        })
    return {
        "modelo": "refinamento_malha_fem_1d",
        "notas": "Para q uniforme, deslocamento nodal linear é exato; verificar convergência das tensões, não apenas da ponta.",
        "malhas": resultados
    }
