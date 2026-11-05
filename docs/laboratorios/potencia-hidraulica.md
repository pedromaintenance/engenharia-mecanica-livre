# Laboratório 01 — Potência hidráulica

## Função física

A potência hidráulica transferida por uma bomba em regime aproximadamente permanente é `P_h=ΔpQ`, onde `Δp` é o diferencial de pressão e `Q` a vazão volumétrica real de saída. Para rendimento global `η`, estima-se `P_eixo=P_h/η`.

## Exemplo resolvido

`Δp=180 bar=18 MPa`; `Q=20 L/min=0,0003333 m³/s`; `η=0,85`.

`P_h=18.000.000 × 0,0003333≈6000 W=6 kW` e `P_eixo≈7,06 kW`.

```bash
engmec calcular bomba --pressao-bar 180 --vazao-lpm 20 --eficiencia 0.85
```

## Exercício

100 bar, 30 L/min, eficiência global 0,80. **Gabarito:** potência hidráulica 5 kW; de eixo 6,25 kW.

## Limites e segurança

A aplicação real requer diferencial de pressão medido nos terminais, vazão no ponto, avaliação de rendimento, transientes, temperatura, cavitação, contrapressão e limites OEM. Não usar para autorizar pressurização ou liberação de máquina.

**Fonte didática:** [NPTEL Hydraulic Machines](https://nptel.ac.in/courses/112103249).
