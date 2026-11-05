# Laboratório 04 — Número de Reynolds

## Modelo

`Re=ρvD/μ`, com densidade `ρ` (kg/m³), velocidade `v` (m/s), comprimento característico `D` (m) e viscosidade dinâmica `μ` (Pa s). É adimensional.

## Exemplo resolvido

`ρ=1000 kg/m³`, `v=1,5 m/s`, `D=0,05 m`, `μ=0,001 Pa s` produzem `Re=75.000`.

```bash
engmec calcular reynolds --densidade-kg-m3 1000 --velocidade-m-s 1.5 --diametro-m 0.05 --viscosidade-pa-s 0.001
```

## Exercício

Para `ρ=850`, `v=0,7`, `D=0,025`, `μ=0,08` em SI, **gabarito:** `Re≈185,94`.

## Limites

A interpretação do regime depende de geometria, perturbação, temperatura, tipo de fluido e definição da dimensão característica; a ferramenta deliberadamente não classifica o regime.

**Aprofundamento:** [NPTEL Courses](https://www.nptel.ac.in/courses).
