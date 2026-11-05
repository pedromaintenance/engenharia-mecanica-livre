# Laboratório 03 — Frequência natural massa-mola

## Modelo

Um grau de liberdade, pequenas oscilações lineares e amortecimento desprezado: `mx''+kx=0`; `ω_n=√(k/m)`; `f_n=ω_n/(2π)`.

## Exemplo resolvido

Para `m=25 kg` e `k=10.000 N/m`, `ω_n=20 rad/s`, `f_n≈3,183 Hz` e período `T≈0,314 s`.

```bash
engmec calcular vibracao --massa-kg 25 --rigidez-n-m 10000
```

## Exercício

Com a rigidez mantida, duplique a massa: qual a nova proporção de frequência? **Gabarito:** `1/√2≈0,707` da original.

## Limites

Máquinas possuem múltiplos modos, massa distribuída, amortecimento, rigidez variável e excitações diversas; não inferir aptidão operacional apenas da frequência calculada.

**Fonte didática:** [MIT Engineering Dynamics](https://ocw.mit.edu/courses/2-003sc-engineering-dynamics-fall-2011/).
