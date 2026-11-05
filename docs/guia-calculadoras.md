# Ferramentas de cálculo

Os resultados são **ideais ou modelos simplificados**, não dados de projeto certificado.

## Cilindro hidráulico (força ideal)

`F = Δp × A`, em newtons; `A_ext = πD²/4`; `A_ret = π(D²-d²)/4`. Pressão de entrada em **bar** (1 bar = 100000 Pa); diâmetros em **mm**. O modelo desconsidera contrapressão, atrito, perdas volumétricas, flambagem, resistência do conjunto e eficiência.

```bash
engmec calcular cilindro --pressao-bar 180 --diametro-mm 100 --haste-mm 60 --curso extensao
```

## Potência mecânica

`P = τ ω`, com `ω = 2π × rpm / 60`. Potência saída em kW. Torque constante e velocidade instantânea conhecida; não é potência elétrica consumida, nem contempla eficiência.

```bash
engmec calcular potencia --torque-nm 250 --rpm 1800
```

## Disponibilidade inerente

`Ai = MTBF/(MTBF+MTTR)`, sob o modelo de tempos médios coerentes de operação e reparo. **Não** equivale automaticamente à disponibilidade física de uma frota com esperas, logística, preventiva e outras paradas.

```bash
engmec calcular disponibilidade --mtbf-h 100 --mttr-h 5
```

## Viga simplesmente apoiada com carga central

`Mmax = FL/4`, `I = bh³/12`, `σmax = Mmax(h/2)/I`, `δmax = FL³/(48EI)`. Supõe viga prismática, material homogêneo, comportamento linear elástico, pequenas deformações, seção retangular, carregamento estático concentrado central e apoios ideais. Não avalia flambagem lateral, cisalhamento, fadiga, ligações ou peso próprio.

```bash
engmec calcular viga --carga-n 1000 --vao-m 2 --e-gpa 200 --largura-mm 50 --altura-mm 100
```

Todas as ferramentas rejeitam parâmetros geométricos não físicos. Unidades e testes estão no código.
