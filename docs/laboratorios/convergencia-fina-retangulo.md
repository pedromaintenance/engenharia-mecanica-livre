# Laboratório 16 — Convergência fina de malhas Q8 para chapas perfuradas

**Versão 0.16.0 — 08/11/2026.** Estudo de refinamento para [issue #17](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/17), ampliando o [laboratório 15](chapa-retangular-comprimento.md).

## 1. Por que uma malha aparentemente boa ainda não basta

No ciclo 15, chapas de largura finita e comprimento crescente se aproximaram da curva de Peterson na **tensão nominal líquida**, mas algumas estimativas de pico continuavam variando mais de 2% entre os dois últimos refinamentos. Essa proximidade com um benchmark de tira longa **não prova convergência**, porque uma estimativa numericamente enviesada pode coincidir fortuitamente com a referência.

O ciclo 16 compara os refinamentos **n=24 (histórico), 32, 40 e 48**, com número de elementos Q8 \`2n² = 1152, 2048, 3200, 4608\`, para \`d/W=0,25\` e \`0,125\` com \`L/W=2\` e \`4\`.

As duas principais questões são: (i) a estimativa \`Kt\` estabiliza quando \`h\` diminui? (ii) o **operador de recuperação da tensão** continua criando diferença entre métodos mesmo em malhas finas?

### Definições e modelo

Chapa completa de dimensões \`L×W=2Hx×2Hy\`, com furo central de diâmetro \`d=2a\`. Material linear isotrópico em tensão plana, \`E=200 GPa,ν=0,30\`, \`a=10 mm\`; tração horizontal constante \`T=10 MPa\` aplicada à face \`x=Hx\` do quadrante de simetria; topo e parede do furo livres. Espessura equivalente de \`5 mm\` cancela do campo de tensões em elasticidade 2D plana sob tração uniforme.

\[
\frac{L}{W}=\frac{H_x}{H_y},\qquad \rho=\frac{d}{W}=\frac{a}{H_y},
\qquad K_{t,\text{net}}=(1-\rho)K_{t,\text{gross}}.
\]

Todos os resultados brutos A/B/C são inicialmente calculados com denominador \`T\`; depois, \`Kt_net\` é convertido para comparar com a **tira longa** de Peterson. A fórmula da tira longa é \`Kt_net≈3−3,14ρ+3,667ρ²−1,527ρ³\`, um **ajuste de referência, não valor exato da chapa finita**.

## 2. Verificação da geometria e qualidade dos elementos

O modelo segue sendo gerado no **Gmsh**, em duas superfícies transfinite com elementos quadráticos serendipidade de oito nós (Q8), convertido pelo ElmerGrid em malha Elmer. O Elmer FEM StressSolver resolve o sistema e os campos nodais são confrontados com o solucionador independente SciPy.

Além dos controles já existentes (malha sem inversão de jacobiano, contornos de simetria, carregamento e condições livres), cada caso arquiva:

- número de elementos, nós e DOFs, e a integridade da primeira faixa radial adjacente ao furo;
- qualidade geométrica Q8 calculada no importador e **jacobiano mínimo nos pontos utilizados**;
- **razão entre a maior e a menor corda de aresta** medida nos quatro vértices de cada Q8, para toda a malha e na primeira faixa junto ao furo;
- ângulo mínimo entre lados dos vértices, para toda a malha e para os elementos junto ao furo;
- número de segmentos da face tracionada e dos contornos livres, sem presumir que o comprimento da borda tracionada cresce com \`L\`;
- integridade dos arquivos \`.msh\` por SHA256, bem como o desvio de deslocamento Elmer × SciPy;
- o balanço de cargas do quadrante: \`F=T H_y t\`.

**Limite do indicador:** razão de cordas e ângulos formados pelos vértices **não substituem a medida isoparamétrica da qualidade de um Q8 curvo**. São *proxies* geométricos complementares aos jacobianos.

## 3. Três métodos de recuperação de tensão — mesma solução Elmer

Como no [laboratório 14](recuperacao-tensoes-furo.md), para cada campo de deslocamentos nodais do Elmer:

- **A — gradiente direto:** \`σ=DBu\` no vértice do furo \`(0,a)\`, usando o único elemento adjacente;
- **B — extrapolação local de Gauss:** base polinomial de seis coeficientes sobre tensões internas 3×3 de Q8, sem pesos;
- **C — patch ponderado local:** quatro coeficientes e pesos função do jacobiano, quadratura e proximidade; **não** é uma implementação validada do método SPR de Zienkiewicz–Zhu.

Além de \`Kt_gross\` e \`Kt_net\`, registrar \`σrr/T\` em uma parede que deveria estar livre, amplitude A/B/C, número de amostras, condicionamento dos ajustes e controle analítico com Kirsch (furo em **placa infinita**, não referência exata da chapa finita).

## 4. Identificação conservadora da ordem de convergência e GCI

O [NIST (2020), *A Summary of Industrial Verification, Validation, and Uncertainty Quantification Procedures in CFD*](https://www.govinfo.gov/content/pkg/GOVPUB-C13-3b234d3edb50d5f632fa1a8b21b911dd/pdf/GOVPUB-C13-3b234d3edb50d5f632fa1a8b21b911dd.pdf) sintetiza as condições de extrapolação de Richardson e do *Grid Convergence Index* de Roache. É uma metodologia de **verificação de discretização**; o uso aqui é deliberadamente **condicional**, sem equiparar o índice a um nível estatístico de confiança ou a uma prova de integridade física.

Para uma grandeza \`q_n\` e resolução aproximada \`h_n=1/n\`, o modelo de erro é \`q_n=q_∞+C n^(−p)\`. A diferença de duas malhas consecutivas produz razões:

\[
\frac{q_{n_0}-q_{n_1}}{q_{n_1}-q_{n_2}}=
\frac{n_0^{-p}-n_1^{-p}}{n_1^{-p}-n_2^{-p}}.
\]

O script \`src/engmec/convergencia_malha.py\` tenta obter a ordem positiva \`p\` para os trios **(24,32,40)** e **(32,40,48)**. Somente se houver quatro valores finitos, tendência monotônica em toda a série, ordem fina entre 0,5 e 4 e diferença relativa entre as duas ordens **menor ou igual a 40%**, o programa calcula extrapolação e um **GCI condicional** com fator de segurança \`Fs=1,25\`.

\[
\mathrm{GCI}_{48}=
\frac{1,25\,|q_{48}-q_{40}|}
{|q_{48}|\,[(48/40)^p-1]}.
\]

**Se qualquer gate falhar:** registrar explicitamente \`status=nao_comprovada\`, \`GCI_fino_relativo=null\` e a justificativa. Essa opção é superior a fabricar uma ordem esperada ou um intervalo percentual de confiança. Mesmo um GCI emitido **não cobre** erro de modelo, propriedades materiais, tensão pontual de superfície, contato nem condições reais de operação.

## 5. Comparabilidade e referências

- [ANSYS — MAPDL 2D Plane Stress Concentration Analysis](https://mapdl.docs.pyansys.com/version/stable/examples/gallery_examples/00-mapdl-examples/2d_plate_with_a_hole.html): referência da curva Peterson, elementos de ordem elevada e refinamento junto ao furo;
- [NIST — procedimentos de verificação, validação e quantificação de incerteza](https://www.govinfo.gov/content/pkg/GOVPUB-C13-3b234d3edb50d5f632fa1a8b21b911dd/pdf/GOVPUB-C13-3b234d3edb50d5f632fa1a8b21b911dd.pdf): cautelas no cálculo de ordem observada e GCI;
- [ANSYS Verification Manual — VM142](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/ans_vm/Hlp_V_VM142.html): benchmark de concentração no furo e submodelagem, mas dimensões e recuperação diferentes deste laboratório;
- [Gmsh — documentação oficial](https://gmsh.info/doc/texinfo/): malhas de segunda ordem e superfícies transfinite.

Nenhuma dessas referências substitui **ensaio físico da mesma chapa**; e nenhum valor de \`Kt\` neste projeto pode ser usado para liberação, reparo ou dimensionamento de olhais, chapas de máquinas pesadas ou dispositivos de içamento.

## 6. Reproduzir e auditar

Com ambiente Ubuntu 24.04, Gmsh, Elmer FEM e Python com extras \`elmer\`:

\`\`\`bash
python -m pip install -e ".[elmer]"
python -m engmec.elmer_chapa --nr 48 --nt 96 \
  --semilargura-m .08 --semicomprimento-x-m .32 \
  --saida build/ciclo16/ha-8-lw-4-n-48
\`\`\`

Os demais casos devem ser executados para \`H/a=4/8\`, \`L/W=2/4\` e \`n=32/40/48\`, preservando \`model.geo\`, \`model.msh\`, \`case.sif\`, \`elmermesh/\`, \`*.vtu\`, logs, \`deslocamentos_elmer.json\`, \`gauss_tensoes.csv\` e \`recuperacao.json\`.

O consolidador requer **todos os doze casos**, os seis baselines de n=24 do [dataset do ciclo 15](../dados/ciclo15-chapas-retangulares-2026-11-08.json) e critérios de equilíbrio e integridade dos arquivos.

\`\`\`bash
python scripts/avaliar_ciclo16.py --pasta build/ciclo16/
\`\`\`

[Workflow de cálculo e verificação](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/ciclo16-convergencia.yml). Somente resultados **realmente executados, auditados e consolidados** deverão preencher a seção quantitativa deste laboratório.

## 7. Limitações e próximo gate

Ao comparar L/W=2 e L/W=4, a forma dos elementos na região externa muda; igual número de nós não comprova mesma qualidade local. Se houver degradação geométrica importante, será necessário alterar a topologia/geração da malha, sem mudar a carga física. A série de quatro resoluções não é validação experimental, e nenhuma extrapolação elimina incerteza de condições de contorno do equipamento real.

## 8. Resultados executados e verificações — 08/11/2026

O [workflow externo #42525939565](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42525939565) foi **aprovado em todos os três jobs**: duas execuções de seis casos Elmer/SciPy cada e uma consolidação geométrica. Combinando os níveis n=24 do ciclo 15 e n=32/40/48 do ciclo 16, foram analisadas quatro séries de `d/W` e `L/W`.

### 8.1 Evolução com quatro malhas — Kt da seção líquida, recuperador C

| d/W | L/W | n=24 · 1.152 Q8 | n=32 · 2.048 Q8 | n=40 · 3.200 Q8 | n=48 · 4.608 Q8 | Variação relativa n40→n48 | GCI C aprovado? |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| 0.250 | 2 | 2.438535 | 2.439684 | 2.439871 | 2.439911 | 0.00164% | Não |
| 0.250 | 4 | 2.434541 | 2.435829 | 2.435959 | 2.435985 | 0.00106% | Não |
| 0.125 | 2 | 2.668119 | 2.675191 | 2.675876 | 2.676015 | 0.00517% | Não |
| 0.125 | 4 | 2.666769 | 2.673998 | 2.674773 | 2.674876 | 0.00384% | Não |

A diferença relativa entre **n=40 e n=48** varia de **0,0011% a 0,0052%** no método C. Os Kt apresentam grande **estabilização numérica observada** em relação ao ciclo 15. Entretanto, nenhuma das quatro séries de recuperação C superou o gate de identificação e estabilidade da ordem assintótica definida neste laboratório; por isso, para C **`GCI_fino_relativo=null`** no JSON.

### 8.2 Resultados finais — três métodos e diagnóstico da parede livre

| d/W | L/W | Kt líquido C (n48) | Diferença relativa vs Peterson | Amplitude entre A/B/C (base bruta) | σrr/T, método C |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0,25 | 2 | 2.439911 | 0.809% | 6.834e-5 | 8.109e-6 |
| 0,25 | 4 | 2.435985 | 0.647% | 6.570e-5 | 9.667e-6 |
| 0,125 | 2 | 2.676015 | 0.533% | 1.211e-4 | 1.526e-5 |
| 0,125 | 4 | 2.674876 | 0.491% | 1.066e-4 | 1.729e-5 |

Na malha n48, `σrr/T` próximo ao furo encontra-se da ordem de **10⁻⁵**, embora a condição física de superfície livre exija tensão radial nula. É uma melhora de erro local com o refinamento, não prova de exatidão. Os campos Elmer e SciPy e o equilíbrio também passaram nos limites automatizados, com dados individuais preservados.

### 8.3 Qualidade geométrica — a principal limitação recém-observada

| d/W | L/W | Máx. razão de cordas (toda malha) | Máx. razão de cordas (1ª faixa radial) | Menor ângulo entre vértices | DOFs globais |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0,25 | 2 | 11.31 | 10.48 | 24.30° | 28.226 |
| 0,25 | 4 | 22.21 | 10.55 | 12.15° | 28.226 |
| 0,125 | 2 | 12.07 | 4.52 | 25.50° | 28.226 |
| 0,125 | 4 | 23.00 | 4.57 | 13.12° | 28.226 |

**Diagnóstico:** nas chapas `L/W=4`, os piores elementos chegam a razão de cordas de **22,2–23,0** e ângulos mínimos nos vértices de **12,2–13,1°**. Mesmo com jacobianos Q8 positivos, esses valores indicam que o alongamento do domínio pode degradar significativamente a geometria. Para `d/W=0,25`, na primeira faixa junto ao furo, a razão máxima passa de aproximadamente **2,58 (n32)** para **10,48 (n48)** em `L/W=2`. A progressão radial do CAD Gmsh `q=1,12` permanece fixa enquanto `n` aumenta, criando elementos desproporcionalmente estreitos em algumas regiões.

Essas razões de cordas são **proxies de forma**, não condicionamento espectral completo nem verificação de curva Q8 em todos os pontos. O dado recomenda redesenho da distribuição de malha, com progressão radial adaptada ao número de camadas e possível controle de blocos externos, antes de declarar a sequência universalmente assintótica.

### 8.4 GCI condicional, sem falsa conclusão

A maioria das combinações **não recebeu GCI**, embora a evolução de Kt seja pequena e em geral monotônica. Entre 12 pares `4 geometrias × 3 recuperadores`, **somente o método A em `d/W=0,25; L/W=4`** passou os gates programados de ordem observada e estabilidade relativa: ordem nos tripletos **5,2346 → 3,8887**, diferença relativa entre ordens **34,6%**, extrapolação **Kt bruto ≈ 3,247996** e GCI fino relativo condicional de **0,00190%**. Mesmo esse resultado **não é demonstrativo de convergência assintótica robusta**, pois a ordem no primeiro trio é elevada, os elementos continuam geometricamente distorcidos e o cálculo é de tensão pontual. Deve ser usado apenas como **índice condicionado a pressupostos assumidos**, não como margem de segurança ou intervalo probabilístico.

Os demais 11 conjuntos não superaram os critérios: em alguns a ordem observada excedeu o intervalo conservador definido, em outros houve reversão da monotonicidade, ou não se identificou ordem positiva estável em dois tripletos.

### 8.5 Evidências rastreáveis

- [Workflow externo completo, três jobs aprovados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42525939565).
- [Dataset integral versionado, 12 casos e quatro estudos de convergência](../dados/ciclo16-convergencia-fina-2026-11-08.json); origem verificada por **SHA-256 do `resumo_ciclo16.json`: `cba11d2427c5464ee13757f071a53ac18955abade7390648201023c6bb6784cd`**.
- [Artefato completo de ~54 MB, 209 arquivos](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42525939565/artifacts/13634939407), hash SHA-256 `2555b9de0a36f5bf18f21fdadb7e0337b3f678b5ccb2f259459e4f76c641bde3`, retenção prevista até **08/12/2026**.
- [Job de importação do dataset auditado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42526568150), que recuperou e conferiu o JSON original do workflow aprovado antes de versioná-lo em `docs/dados/`.

**Síntese:** as estimativas Kt estão numericamente estáveis entre as duas malhas mais finas, **mas a qualidade geométrica evolui de forma desigual**, a recuperação superficial ainda tem incertezas metodológicas e o GCI não está demonstrado para o método C. A etapa seguinte precisa modificar a estratégia de progressão e as superfícies transfinite, **não simplesmente aumentar indiscriminadamente `nr`**.
