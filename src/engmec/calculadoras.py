"""Calculadoras didáticas com entradas e saídas SI explícitas.

Nenhuma função autoriza dimensionamento de segurança ou liberação de equipamentos.
"""
from __future__ import annotations

from math import pi


def _positivo(nome: str, valor: float, *, zero: bool = False) -> float:
    valor = float(valor)
    import math
    if not math.isfinite(valor) or valor < 0 or (valor == 0 and not zero):
        raise ValueError(f"{nome} deve ser finito e {'não negativo' if zero else 'positivo'}")
    return valor


def cilindro_hidraulico(
    pressao_bar: float, diametro_mm: float, haste_mm: float, curso: str = "extensao"
) -> dict:
    """Força teórica sem contrapressão/atrito; pressão interpretada como Δp.

    No caso real, pressões de ambas as câmaras podem gerar forças opostas.
    """
    p = _positivo("pressao_bar", pressao_bar) * 100_000
    D = _positivo("diametro_mm", diametro_mm) / 1000
    d = _positivo("haste_mm", haste_mm, zero=True) / 1000
    if d >= D:
        raise ValueError("Diâmetro de haste deve ser menor que o de pistão")
    if curso not in ("extensao", "retracao"):
        raise ValueError("curso deve ser extensao ou retracao")
    area = pi * (D**2 - (d**2 if curso == "retracao" else 0)) / 4
    return {
        "modelo": "forca_ideal_delta_p_area",
        "curso": curso,
        "area_m2": area,
        "pressao_diferencial_pa": p,
        "forca_n": p * area,
        "forca_kn": p * area / 1000,
        "aviso": "Ignora contrapressão independente, atrito, eficiência, flambagem e resistência estrutural.",
    }


def potencia_mecanica(torque_nm: float, rpm: float) -> dict:
    """Potência mecânica instantânea de eixo, P = torque × ω."""
    torque = _positivo("torque_nm", torque_nm, zero=True)
    rotacao = _positivo("rpm", rpm, zero=True)
    omega = 2 * pi * rotacao / 60
    return {
        "modelo": "potencia_de_eixo",
        "velocidade_angular_rad_s": omega,
        "potencia_w": torque * omega,
        "potencia_kw": torque * omega / 1000,
        "aviso": "Não inclui eficiência, fator de serviço, aquecimento ou potência elétrica.",
    }


def disponibilidade_inerente(mtbf_h: float, mttr_h: float) -> dict:
    """Ai = MTBF / (MTBF + MTTR); medidas de tempo coerentes e reparável."""
    mtbf = _positivo("mtbf_h", mtbf_h)
    mttr = _positivo("mttr_h", mttr_h, zero=True)
    ai = mtbf / (mtbf + mttr)
    return {
        "modelo": "disponibilidade_inerente",
        "ai": ai,
        "ai_percentual": 100 * ai,
        "aviso": "Não incorpora espera por peças, logística, preventivas e tempo administrativo.",
    }


def viga_carga_central(
    carga_n: float, vao_m: float, e_gpa: float, largura_mm: float, altura_mm: float
) -> dict:
    """Viga simplesmente apoiada, seção retangular, carga pontual central e Euler-Bernoulli."""
    F = _positivo("carga_n", carga_n)
    L = _positivo("vao_m", vao_m)
    E = _positivo("e_gpa", e_gpa) * 1e9
    b = _positivo("largura_mm", largura_mm) / 1000
    h = _positivo("altura_mm", altura_mm) / 1000
    I = b * h**3 / 12
    M = F * L / 4
    sigma = M * (h / 2) / I
    flecha = F * L**3 / (48 * E * I)
    return {
        "modelo": "viga_biapoiada_carga_central_euler_bernoulli",
        "momento_inercia_m4": I,
        "momento_maximo_nm": M,
        "tensao_flexao_max_pa": sigma,
        "tensao_flexao_max_mpa": sigma / 1e6,
        "flecha_max_m": flecha,
        "flecha_max_mm": flecha * 1000,
        "aviso": "Sem peso próprio, cisalhamento, flambagem lateral, escoamento, fadiga ou concentração de tensões.",
    }


def potencia_hidraulica(pressao_bar: float, vazao_lpm: float, eficiencia: float = 1.0) -> dict:
    """Potência hidráulica e potência ideal de acionamento da bomba.

    Modelo: P_h = Δp Q, P_eixo = P_h / η; η é eficiência global especificada
    para a operação e não deve ser confundida com rendimento volumétrico isolado.
    """
    delta_p = _positivo("pressao_bar", pressao_bar) * 100_000
    vazao = _positivo("vazao_lpm", vazao_lpm) / 60_000
    eta = _positivo("eficiencia", eficiencia)
    if eta > 1:
        raise ValueError("eficiencia deve estar entre 0 (exclusivo) e 1")
    pot = delta_p * vazao
    return {
        "modelo": "potencia_hidraulica_delta_p_vazao",
        "vazao_m3_s": vazao, "pressao_diferencial_pa": delta_p,
        "potencia_hidraulica_w": pot, "potencia_hidraulica_kw": pot / 1000,
        "potencia_entrada_eixo_kw": pot / eta / 1000,
        "aviso": "Modelo permanente: Δp real nos terminais da bomba, Q na saída e rendimento global aplicável; perdas térmicas e transientes exigem análise adicional."
    }


def conducao_plana(k_w_mk: float, area_m2: float, delta_t_k: float, espessura_m: float) -> dict:
    """Lei de Fourier 1D em placa homogênea, regime estacionário."""
    import math
    k = _positivo("k_w_mk", k_w_mk)
    area = _positivo("area_m2", area_m2)
    esp = _positivo("espessura_m", espessura_m)
    dT = float(delta_t_k)
    if not math.isfinite(dT):
        raise ValueError("delta_t_k deve ser finito")
    taxa = k * area * dT / esp
    return {
        "modelo": "conducao_plana_1d_estacionaria",
        "taxa_calor_w_assinada": taxa, "taxa_calor_modulo_w": abs(taxa),
        "aviso": "Ignora resistência de contato, geração interna, convecção, radiação e condução multidimensional; sinal depende do sentido definido para ΔT."
    }


def frequencia_natural(massa_kg: float, rigidez_n_m: float) -> dict:
    """Frequência natural não amortecida de sistema massa-mola com um grau de liberdade."""
    import math
    m = _positivo("massa_kg", massa_kg)
    k = _positivo("rigidez_n_m", rigidez_n_m)
    omega = math.sqrt(k / m)
    return {
        "modelo": "oscilador_linear_sistema_1gdl_nao_amortecido",
        "frequencia_natural_rad_s": omega,
        "frequencia_natural_hz": omega / (2 * math.pi),
        "periodo_s": 2 * math.pi / omega,
        "aviso": "Modelo linear e sem amortecimento, válido para pequenas oscilações; não substitui análise modal de máquinas reais."
    }


def numero_reynolds(densidade_kg_m3: float, velocidade_m_s: float,
                    diametro_m: float, viscosidade_pa_s: float) -> dict:
    """Re = ρ v D / μ, usando velocidade média e dimensão característica informada."""
    rho = _positivo("densidade_kg_m3", densidade_kg_m3)
    v = _positivo("velocidade_m_s", velocidade_m_s, zero=True)
    d = _positivo("diametro_m", diametro_m)
    mu = _positivo("viscosidade_pa_s", viscosidade_pa_s)
    return {
        "modelo": "reynolds_numero_adimensional",
        "reynolds": rho * v * d / mu,
        "aviso": "A interpretação do regime depende da geometria, rugosidade e perturbações. Não classificar escoamento só pelo número em aplicações externas."
    }
