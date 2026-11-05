# Laboratório 02 — Condução de calor em uma placa

## Modelo

Lei de Fourier em condução 1D estacionária, propriedades aproximadamente constantes: `q=kAΔT/L`. O sinal da taxa depende do sentido definido para a diferença térmica.

## Exemplo resolvido

`k=0,8 W/(m K)`, `A=1,2 m²`, `ΔT=30 K` e `L=0,2 m`.

`q=0,8×1,2×30/0,2=144 W`.

```bash
engmec calcular conducao --k-w-mk 0.8 --area-m2 1.2 --delta-t-k 30 --espessura-m 0.2
```

## Exercício

`k=0,04`, `A=2`, `ΔT=20`, `L=0,1`, tudo em SI. **Gabarito:** 16 W.

## Limites

Não inclui resistência de contato, geração interna, convecção, radiação, transientes, propriedades variáveis ou caminhos multidimensionais. Conferir propriedades em fonte apropriada ao material.

**Fontes para aprofundar:** [NPTEL](https://www.nptel.ac.in/courses), [NIST](https://webbook.nist.gov/chemistry/).
