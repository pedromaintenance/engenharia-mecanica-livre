# Ciclo 18 — Redistribuição angular Q8 e resultado negativo reproduzível

**Data:** 08/11/2026 (horário de Santarém). **Versão:** 0.18.0. **Issue:** [#18](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/18).

## Questão de engenharia

O ciclo 17 demonstrou melhora da anisotropia global Q8 ao adaptar a progressão radial, mas não obteve a mesma melhora perto do furo. O ciclo 18 procurou atuar na **topologia da interface dos dois blocos** e na **distribuição angular dos nós** mantendo fisicamente idêntica a chapa retangular sob tração.

## Etapa 1: interface spline, rejeitada no teste de malha

Duas alternativas internas de \`Line(3)→Spline(3)\` foram geradas e submetidas ao teste Gmsh. Em chapas alongadas \`L/W=4\`, elementos Q8 apresentaram **jacobianos não positivos**. A rotina de importação bloqueou a execução do solver. A tentativa foi removida do código de produção; nenhum Kt FEM foi publicado para a geometria inválida. [Log da tentativa inicial](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42549065820) · [segunda tentativa](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42549260213).

**Lição:** curvar uma interface dentro do mapeamento transfinite de dois blocos pode exigir revisão da topologia, e não apenas ajuste de coordenadas de pontos de controle.

## Etapa 2: redistribuição angular com interface reta

Implementada opção experimental \`--distribuicao-angular ampliada-topo\`, com distribuição \`q_theta=exp(ln(0,7)/(nt/2))\` nas curvas orientadas \`{-5,7}\` da metade angular superior. O bloco inferior mantém distribuição uniforme e a progressão radial \`q_r(n)=exp(24ln(1,12)/n)\` continua inalterada.

Os **16 modelos externos** (H/a=4/8, L/W=2/4, n24/32/40/48) passaram nos verificadores de jacobiano, integridade das superfícies físicas, equilíbrio SciPy, deslocamentos Elmer×SciPy e recuperação A/B/C. Foi testado o mesmo modelo material sob tensão plana \`E=200 GPa, ν=0,30, T=10 MPa\`.

### Avaliação na malha n=48

| d/W | L/W | Pior alongamento primeira faixa antes | Depois | Piora | Max. global antes | Depois |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 2.021 | 2.407 | 19.1% | 5.93 | 5.93 |
| 0.250 | 4 | 3.931 | 4.706 | 19.7% | 11.64 | 11.64 |
| 0.125 | 2 | 4.258 | 5.097 | 19.7% | 6.30 | 6.30 |
| 0.125 | 4 | 8.075 | 9.666 | 19.7% | 12.00 | 12.00 |

**Em todas as quatro geometrias, a primeira faixa do furo ficou mais alongada, cerca de +19%.** Os ângulos mínimos globais e a pior razão global não melhoraram.

### Condição radial de superfície livre

| d/W | L/W | σrr/T antes | Depois | Piora |
| ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 1.687e-4 | 1.869e-4 | 10.8% |
| 0.250 | 4 | 1.792e-4 | 1.966e-4 | 9.7% |
| 0.125 | 2 | 9.740e-4 | 9.909e-4 | 1.7% |
| 0.125 | 4 | 1.020e-3 | 1.051e-3 | 3.0% |

**O resíduo da tração normal no furo piorou em todas as chapas.** Essa evidência é mais importante que a pequena mudança em Kt, pois a parede deveria estar livre de carregamento radial.

### Recuperação e convergência

| d/W | L/W | Kt líquido C antes | Depois | Δrel | GCI numérico condicional |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 2.439776 | 2.439739 | -0.0015% | 0.0098% |
| 0.250 | 4 | 2.435855 | 2.435811 | -0.0018% | 0.0095% |
| 0.125 | 2 | 2.675120 | 2.675038 | -0.0031% | 0.0483% |
| 0.125 | 4 | 2.673983 | 2.673896 | -0.0033% | 0.0449% |

Os quatro casos passaram os critérios programados para GCI condicionado do recuperador C, mas **isso não demonstra menor erro real**. Os índices também ficaram ligeiramente maiores do que os observados anteriormente. A malha alternativa é válida como discretização, porém **não comprovou benefício para o objetivo do ciclo**.

## Automação e evidência final

- [Workflow final com 16 soluções e consolidação aprovadas](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42550543935).
- [Dataset permanente gerado pelo workflow após testes](../dados/ciclo18-angular-2026-11-08.json), incluindo os 16 casos, GCI A/B/C, qualidade de malha, tensões e equivalência de soluções.
- [Artefato bruto de ~60 MB](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42550543935/artifacts/13645355866), SHA256 \`3ca799137ac676c3f009605b51ca140063ea1089e9926c6fd327c29904973fa1\`, retenção até 09/12/2026.
- O primeiro workflow com simulações aprovadas falhou **apenas na publicação**, devido a um campo \`cases\` em vez de \`casos\`; foi corrigido e repetido integralmente, resultando em workflow final verde. A falha pertence ao pipeline de publicação, não à solução FEM.
- [Laboratório 18](../laboratorios/distribuicao-angular-q8.md) detalha hipótese, procedimento e limites.

## Decisão e handover

- **Aprovação do experimento:** executado, verificado e publicado como **resultado negativo**; fonte de evidência para não adotar a estratégia.
- **Alteração de padrão:** nenhuma. \`uniforme\` continua padrão e \`ampliada-topo\` permanece apenas como comparação experimental.
- **Pendência #18:** ainda falta uma topologia de malha com melhoria simultânea da primeira faixa e canto externo e da tração livre no furo.
- **Próxima trilha:** modelar uma **faixa anular própria em torno do furo** e conectá-la ao exterior por blocos de transição (O-grid/C-grid), com validação de jacobianos e condições de contorno antes de resolver tensões. Nunca adequar a malha exclusivamente para aproximar o Kt de Peterson.

**Segurança:** os resultados não são critérios de resistência ou aceitação de olhais, dispositivos de içamento, chapas soldadas ou componentes de mineração.
