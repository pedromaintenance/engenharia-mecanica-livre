# Laboratório 18 — Testes rejeitados e distribuição angular de elementos Q8

**Data:** 8 de novembro de 2026, horário local de Santarém. **Versão:** v0.18.0. **Estado:** 16 modelos externos Elmer FEM executados, dados versionados e verificados. **Issue:** [#18](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/18).

> **Conclusão do experimento:** a redistribuição angular testada **não melhorou a qualidade local da malha nem a condição de tensão livre no furo**. Por isso, o padrão angular uniforme foi mantido. O resultado negativo é publicado integralmente, sem seleção de casos favoráveis.

## 1. Problema de engenharia e hipóteses

O [ciclo 17](progressao-radial-q8.md) reduziu o alongamento máximo **global** das células Q8 em aproximadamente 48% com uma progressão radial dependente do refinamento, mas verificou degradação dos indicadores de forma junto à parede do furo e aumento do resíduo de tensão normal radial. Além disso, os ângulos mínimos nos cantos externos permaneceram próximos a 12–13° nas chapas longas.

Este ciclo separa duas causas candidatas:

1. **Ligação interna entre dois blocos de malha:** uma linha reta liga o ponto circular de 45° ao canto externo do retângulo. Em chapas muito longas essa ligação atinge o canto sob ângulo raso.
2. **Distribuição dos pontos nas curvas do segundo bloco:** uma distribuição angular uniforme pode gerar aspecto radial/tangencial inadequado na primeira faixa junto ao topo do furo.

Os critérios de aceitação foram definidos pela geometria, pelo equilíbrio, pela condição de parede livre e pelos resultados de três recuperadores **sem selecionar a estratégia pelo valor de Kt próximo de Peterson**.

## 2. Ensaio CAD rejeitado — interface interna em spline

A primeira hipótese foi atacada substituindo apenas a interface interna \`Line(3)\` por \`Spline(3)\` entre as mesmas extremidades. Os pontos externos, o círculo do furo e as condições físicas permaneceram inalterados. Duas variações de curvatura foram testadas; ambas geraram **jacobianos Q8 não positivos** no teste rápido do Gmsh na chapa mais alongada, L/W=4.

A rotina de importação de malha rejeitou esses elementos antes da montagem e resolução FEM. **Nenhum Kt foi produzido para esses modelos inválidos.** O módulo experimental correspondente foi retirado do código publicado. Esse resultado não demonstra que uma malha com interface curva seja impossível: demonstra que as parametrizações testadas sobre os dois blocos atuais foram inadequadas.

Evidências de falha: [primeiro smoke com spline](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42549065820) e [segunda tentativa](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42549260213). O erro conhecido e a mudança de rumo foram preservados no [relatório do ciclo](../ciclos/ciclo-18.md).

## 3. Nova hipótese: distribuição angular alternativa sem alterar os blocos

A segunda intervenção foi executada com o **CAD original de dois blocos**, mantendo a interface reta. O Gmsh aceita \`Transfinite Curve\` com \`Using Progression\` e permite utilizar IDs de curvas negativos para orientar de maneira consistente distribuições graduadas em lados opostos. Veja o [manual oficial do Gmsh](https://gmsh.info/doc/texinfo/gmsh.html).

Na metade angular superior (\`45° ≤ θ ≤ 90°\`), as curvas \`7\` (arco do furo, do topo para 45°) e \`-5\` (borda externa superior, orientada no sentido inverso) recebem:

\[
q_\theta=\exp\left(\frac{\ln(0,7)}{N_a}\right),
\qquad N_a=\frac{n_t}{2}.
\]

Como \`qθ<1\`, a primeira célula da progressão, junto ao topo do furo, fica relativamente maior. O segundo bloco altera seus espaçamentos; o primeiro bloco mantém distribuição angular uniforme. A progressão **radial escalonada do ciclo 17** foi preservada sem modificação:

\[
q_r(n)=\exp\left(\frac{24\ln(1,12)}{n}\right).
\]

A fração 0,7 foi escolhida como ensaio geométrico conservador de redistribuição de tamanhos, **não por otimização para determinado Kt**. A nova configuração é opt-in, via \`--distribuicao-angular ampliada-topo\`; \`uniforme\` permanece o padrão.

## 4. Modelo físico e matriz experimental

Chapa retangular completa \`L×W\`, furo circular de raio \`a=10 mm\`, tração horizontal \`T=10 MPa\` na face \`x=Hx\` do quadrante, topo e furo livres, simetrias \`Ux=0\` em x=0 e \`Uy=0\` em y=0. Elasticidade isotrópica linear em tensão plana, \`E=200 GPa\`, \`ν=0,30\`, espessura de referência 5 mm.

- **Geometrias:** \`d/W=0,25\` e \`0,125\`; \`L/W=2\` e \`4\`.
- **Malhas:** n=24,32,40,48; \`nt=2n\`; respectivamente 1.152, 2.048, 3.200 e 4.608 elementos Q8 por caso.
- **16 soluções FEM novas:** Elmer StressSolver independente com comparação ao solucionador SciPy Q8 na mesma malha; método A de gradiente direto, B de extrapolação Gauss e C de ajuste local ponderado sobre o **mesmo campo Elmer**.

Os baselines foram as **16 malhas com progressão radial escalonada e distribuição angular uniforme** do [ciclo 17](../dados/ciclo17-malha-radial-2026-11-08.json). Portanto, não se altera a física, o material, a tração, o número de elementos, a progressão radial ou as definições de \`Kt\`. Apenas a distribuição angular muda. Os hashes MSH2 distinguem as malhas reais.

## 5. Resultados observados — Q8 n=48

### 5.1 Qualidade geométrica da primeira faixa

A métrica é a razão entre maior e menor corda dos vértices de cada quadrilátero. Ela é um **indicador de forma**, não uma medida completa do condicionamento isoparamétrico Q8. Valores maiores indicam elementos mais alongados.

| d/W | L/W | Pior razão, angular uniforme | Angular alternativa | Piora | Máx. global uniforme | Máx. global alternativa |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 2.021 | 2.407 | 19.1% | 5.93 | 5.93 |
| 0.250 | 4 | 3.931 | 4.706 | 19.7% | 11.64 | 11.64 |
| 0.125 | 2 | 4.258 | 5.097 | 19.7% | 6.30 | 6.30 |
| 0.125 | 4 | 8.075 | 9.666 | 19.7% | 12.00 | 12.00 |

**Todas as quatro geometrias pioraram na primeira faixa** (aproximadamente +19% na razão máxima). A pior razão global permaneceu **numericamente igual**, pois os elementos mais alongados do domínio não eram governados por essas curvas. Os ângulos mínimos nos vértices externos também permaneceram inalterados, na faixa de 12–13° nos domínios \`L/W=4\`. Os jacobianos verificados foram positivos, mas isso não elimina a degradação local observada.

### 5.2 Erro residual da condição de superfície livre

Uma parede de furo sem tração deve ter \`σrr=0\` e \`σrθ=0\`. O recuperador C produziu os seguintes resíduos normais relativos à tração bruta \`T\`:

| d/W | L/W | σrr/T uniforme | σrr/T alternativa | Aumento relativo |
| ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 1.687e-4 | 1.869e-4 | 10.8% |
| 0.250 | 4 | 1.792e-4 | 1.966e-4 | 9.7% |
| 0.125 | 2 | 9.740e-4 | 9.909e-4 | 1.7% |
| 0.125 | 4 | 1.020e-3 | 1.051e-3 | 3.0% |

**O resíduo de tensão radial aumentou nas quatro geometrias**, embora sem inversão de jacobianos. O resultado contraria a hipótese de que alongar a célula angular junto ao topo melhoraria automaticamente a condição local de superfície livre.

### 5.3 Kt quase constante não significa melhor recuperação

O fator bruto é \`Kt_gross=σθθ/T\`; o valor de seção líquida é \`Kt_net=Kt_gross(1-d/W)\`. A curva de Peterson para tira suficientemente longa usa a **base líquida**, mas não é valor exato para esta chapa finita.

| d/W | L/W | Kt líquido C uniforme | Kt líquido C alternativa | Diferença relativa | GCI C condicional, alternativa |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 2.439776 | 2.439739 | -0.0015% | 0.0098% |
| 0.250 | 4 | 2.435855 | 2.435811 | -0.0018% | 0.0095% |
| 0.125 | 2 | 2.675120 | 2.675038 | -0.0031% | 0.0483% |
| 0.125 | 4 | 2.673983 | 2.673896 | -0.0033% | 0.0449% |

O \`Kt\` do método C mudou menos de 0,004% entre as distribuições angulares na malha n48. As quatro séries angulares alternativas passaram os critérios programados para GCI **condicional**, mas o índice aumentou ligeiramente em comparação à malha do ciclo 17. Mesmo concordância e GCI numérico não demonstram menor erro físico, em particular porque a **qualidade da primeira faixa e a condição de tração livre pioraram**.

## 6. Auditoria, códigos e rastreabilidade

Implementações:

- \`src/engmec/angular_transfinite.py\`: modificador opcional de distribuição angular, com orientação de curva e validação de parâmetros.
- \`src/engmec/elmer_chapa.py\`: CLI \`--distribuicao-angular uniforme|ampliada-topo\`, sem alterar o padrão histórico.
- \`scripts/avaliar_ciclo18.py\`: compara cada uma das 16 soluções com o dataset anterior e controla malha, área, equilíbrio, deslocamentos, três tensões e gates.
- \`.github/workflows/ciclo18-angular.yml\`: *smoke* geométrico antes do FEM, execução externa, consolidação e publicação versionada do JSON.

Reproduzir caso n48 da chapa mais longa:

\`\`\`bash
python -m pip install -e ".[elmer]"
python -m engmec.elmer_chapa \
  --nr 48 --nt 96 --raio-m .01 \
  --semilargura-m .08 --semicomprimento-x-m .32 \
  --progressao-radial escalonada \
  --distribuicao-angular ampliada-topo \
  --saida build/ciclo18/ha-8-lw-4-n-48
\`\`\`

Evidências públicas:

- [Execução externa aprovada — 16 casos completos](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42550543935).
- [Dataset integral e permanente](../dados/ciclo18-angular-2026-11-08.json), versionado pelo próprio workflow após aprovação de 16 casos.
- [Artefato bruto com malhas, VTU, SIF, deslocamentos, Gauss e logs](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42550543935/artifacts/13645355866) (aproximadamente 60 MB; hash ZIP SHA-256 \`3ca799137ac676c3f009605b51ca140063ea1089e9926c6fd327c29904973fa1\`; retenção indicada até 09/12/2026).
- [Gmsh — documentação oficial de curvas transfinite e progressão](https://gmsh.info/doc/texinfo/gmsh.html).

## 7. Decisão e próximo experimento

**A distribuição angular alternativa foi rejeitada como estratégia de melhoria.** Ela continua disponível apenas como experimento comparativo; **o padrão uniforme está preservado**. A hipótese de curvar a interface interna com dois blocos também não passou na integridade geométrica.

Próximo gate: construir **uma faixa anular própria em torno do furo, separada dos blocos de transição para o retângulo**, que permita controlar de modo independente orientação dos elementos Q8, gradação radial e qualidade do canto externo. A verificação deverá confrontar alongamento **global e local**, ângulos, jacobianos, tração livre, convergência A/B/C e resultados no mesmo problema físico.

O modelo é educacional e linear-elástico. Não inclui contato do pino, solda, fadiga, plasticidade, folgas, carregamento excêntrico nem validação de componentes reais de equipamentos pesados.
