# Laboratório 17 — Progressão radial escalonada e qualidade dos elementos Q8

**Estado: executado e publicado em 08/11/2026.** [Issue #18](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/18) · [Dataset permanente](../dados/ciclo17-malha-radial-2026-11-08.json) · [Workflow externo aprovado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42546868607).

## 1. Problema material

No [laboratório 16](convergencia-fina-retangulo.md), o refinamento das chapas retangulares gerou malhas Q8 com razão entre cordas dos lados de até 23 e ângulos mínimos na casa de 12°. Os elementos não tiveram jacobianos negativos, mas a política `Transfinite Curve ... Using Progression 1.12` produzia crescimento geométrico radial acumulado cada vez maior com `n`. Ao passar de 24 para 48 divisões, mantinha-se a razão de cada segmento em `q=1,12`, elevando a razão global de segmentos de aproximadamente `q^24≈15,18` para `q^48≈230,39` (aproximação, pois o número de razões sucessivas difere do número de segmentos).

**Hipótese de engenharia:** uma política que preserve a razão acumulada de crescimento da discretização ao refinar pode evitar células excessivamente estreitas e melhorar a estabilidade da estimativa local de tensão. Essa hipótese precisa ser testada; *melhora geométrica global não equivale automaticamente a melhora na representação da tensão da parede livre*.

## 2. Alternativas testadas

A distribuição `Using Progression` é suportada oficialmente no Gmsh para malhas transfinite. Segundo o [manual do Gmsh](https://gmsh.info/doc/texinfo/gmsh.html), a expressão define uma progressão geométrica, enquanto a combinação de curvas transfinite e superfícies define uma malha estruturada.

**Política anterior (fixa):**

\[
q_{\mathrm{fixa}}(n)=1{,}12
\]

**Nova política (escalonada):**

\[
q_{\mathrm{esc}}(n)=\exp\left(\frac{24\ln(1{,}12)}{n}\right),
\qquad q_{\mathrm{esc}}(n)^n=1{,}12^{24}.
\]

| Divisões radiais `n` | Progressão fixa | Progressão escalonada |
| ---: | ---: | ---: |
| 24 | 1,1200 | 1,1200 |
| 32 | 1,1200 | ≈1,0886 |
| 40 | 1,1200 | ≈1,0703 |
| 48 | 1,1200 | ≈1,0583 |

Essa definição é **um controle geométrico proposto no projeto**, não requisito da literatura nem garantia de precisão da solução Q8. O perfil radial escalonado usa o mesmo modelo físico, o mesmo solucionador Elmer FEM e os mesmos operadores de tensão da versão anterior.

## 3. Reprodutibilidade e controle da comparação

O código implementa a política em `src/engmec/progressao_radial.py` e a opção **`--progressao-radial fixa|escalonada`** em `python -m engmec.elmer_chapa`. **O padrão continua `fixa`**, preservando os workflows históricos. O Gmsh do retângulo recebe apenas o valor efetivo de `q` sem modificar coordenadas externas, grupos físicos, ordem Q8 ou contornos.

Foram executados **16 casos novos**, cobrindo:

- diâmetro/largura `d/W=0,25` e `0,125`;
- comprimento/largura `L/W=2` e `4`;
- divisões radiais `n=24,32,40,48`, com `2n²=1.152,2.048,3.200,4.608` elementos Q8.

A tração em x é `T=10 MPa`; material linear isotrópico em tensão plana `E=200 GPa, ν=0,30`, raio do furo `a=10 mm` e espessura de referência `t=5 mm`. O quarto de chapa conserva `F=T H_y t`, simetrias nos eixos x=0/y=0 e bordas livres no topo e no furo. Não há contato de pino ou carregamento excêntrico.

A comparação é **entre dois conjuntos de malhas**: resultados de progressão fixa publicados nos [ciclos 15](../dados/ciclo15-chapas-retangulares-2026-11-08.json) e [16](../dados/ciclo16-convergencia-fina-2026-11-08.json), e novos resultados da progressão escalonada resolvidos no Elmer. O novo `n=24` reproduziu **byte a byte as quatro malhas antigas**, verificado por SHA256. Para `n>24`, a malha mudou. Em todos os casos, o campo de deslocamentos Elmer foi confrontado com um FEM Q8 SciPy e foi recuperada a tensão pelos mesmos métodos A/B/C.

## 4. Resultado geométrico — malha mais fina

A qualidade abaixo é aproximada pela razão entre a **maior e a menor corda formada pelos vértices** de cada elemento, não pela razão de autovalores do jacobiano em todos os pontos. Para avaliar a primeira faixa radial, identificamos os Q8 adjacentes ao furo. **Menor razão costuma ser desejável, mas a métrica não qualifica sozinha um elemento curvo.**

| d/W | L/W | Pior razão geral, fixa | Escalonada | Redução | Pior 1ª faixa, fixa | Escalonada |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 11.315 | 5.928 | 47.6% | 10.485 | 2.021 |
| 0.250 | 4 | 22.213 | 11.639 | 47.6% | 10.548 | 3.931 |
| 0.125 | 2 | 12.067 | 6.296 | 47.8% | 4.522 | 4.258 |
| 0.125 | 4 | 23.001 | 12.002 | 47.8% | 4.573 | 8.075 |

**Achado positivo:** a maior razão de cordas do domínio diminuiu aproximadamente **47,6–47,8% nas quatro geometrias**. O caso mais alongado, d/W=0,125 e L/W=4, caiu de 23,00 para 12,00.

**Falha local que permanece:** em d/W=0,125 e L/W=4, a pior razão da primeira faixa próxima ao furo **aumentou de 4,57 para 8,07**, apesar da melhora global. Na mesma geometria, o indicador **mediano da primeira faixa** mudou de aproximadamente 1,12 para 7,76, mostrando um compromisso desfavorável justamente perto do ponto mais sensível. Os ângulos mínimos de vértice da malha inteira permaneceram perto de **12–13° nas chapas L/W=4**, porque a progressão radial não altera a geometria angular dos blocos.

Todos os jacobianos verificados mantiveram sinal positivo. **Não houve comprovação de regularidade suficiente em toda a malha.**

## 5. Recuperação de tensão e convergência

O método C de recuperação é um **patch polinomial ponderado experimental**, não um SPR certificado. Os métodos A (gradiente direto no vértice) e B (extrapolação dos pontos de Gauss) foram mantidos para comparação. O fator bruto é referenciado em `T`; o fator líquido segue `Kt_net=(1-d/W)Kt_gross`, permitindo comparação *somente indicativa* com Peterson para uma tira suficientemente longa.

| d/W | L/W | Kt líquido C fixo (n48) | Escalonado (n48) | GCI condicional C escalonado | Ordens observadas em dois tripletos |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0.250 | 2 | 2.439911 | 2.439776 | 0.0073% | 3.357 → 3.268 |
| 0.250 | 4 | 2.435985 | 2.435855 | 0.0074% | 2.975 → 3.438 |
| 0.125 | 2 | 2.676015 | 2.675120 | 0.0442% | 2.956 → 3.105 |
| 0.125 | 4 | 2.674876 | 2.673983 | 0.0411% | 2.977 → 3.270 |

Em contraste com a progressão fixa, **as quatro sequências C escalonadas passaram os critérios programados** de quatro malhas, monotonicidade, ordens positivas plausíveis e estabilidade relativa entre dois tripletos. O GCI usa `Fs=1,25` e é um **índice condicional para discretização da grandeza recuperada**, não limite físico de tensão, margem de segurança ou intervalo estatístico de confiança.

**Importante:** as séries A/B têm comportamentos diferentes. Em d/W=0,25, L/W=4, o método B **não superou os gates**, mesmo com a progressão escalonada. Não existe uma aprovação geral de todos os pós-processamentos.

## 6. Controle da parede livre — piora que a melhoria global não esconde

No furo sem carregamento, a componente radial deve tender a `σrr=0`. No método C, n48, os resíduos normalizados observados foram:

| d/W | L/W | σrr/T fixo | σrr/T escalonado | Amplitude Kt bruto A/B/C escalonado |
| ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 8.109e-6 | 1.687e-4 | 4.207e-4 |
| 0.250 | 4 | 9.667e-6 | 1.792e-4 | 3.985e-4 |
| 0.125 | 2 | 1.526e-5 | 9.740e-4 | 1.852e-3 |
| 0.125 | 4 | 1.729e-5 | 1.020e-3 | 1.860e-3 |

Em d/W=0,125, L/W=4, o resíduo `σrr/T` **aumentou de 1,73×10⁻⁵ para 1,02×10⁻³**, aproximadamente 59 vezes, apesar da melhora geométrica global. O mesmo tipo de piora ocorreu nas demais geometrias. O mecanismo exato desse aumento exige separar erro de interpolação e suporte geométrico do patch; os dados atuais **não** demonstram causa raiz.

Essa observação impede concluir que a progressão escalonada seja superior em todos os objetivos de engenharia. Ela resolve uma parte da distribuição de tamanhos, mas **cria ou revela um compromisso local** perto da superfície livre.

## 7. Execução externa, dados e auditoria

- [16 casos Elmer/SciPy e consolidação aprovados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42546868607); executados em duas matrizes paralelas, uma para cada `d/W`.
- [Dataset integral permanentemente versionado](../dados/ciclo17-malha-radial-2026-11-08.json), publicado pelo **próprio workflow após a aprovação do consolidador**.
- [Artefato bruto completo — aproximadamente 60 MB](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42546868607/artifacts/13644225265): `.geo`, `.msh`, malhas Elmer, `.sif`, resultados `.vtu`, deslocamentos nodais, pontos de Gauss `.csv`, logs e versões/digest do contêiner. SHA256 do arquivo ZIP: `2c98e50257e25d66a1e80a8eaf90d7fd135c0de6c48a10e32524c66186bb4df5`. Retenção prevista até **09/12/2026**.
- [Manual Gmsh — transfinite e progressão geométrica](https://gmsh.info/doc/texinfo/gmsh.html), referência primária do gerador de malhas.
- [NIST — verificação, validação e incerteza numérica](https://www.govinfo.gov/content/pkg/GOVPUB-C13-3b234d3edb50d5f632fa1a8b21b911dd/pdf/GOVPUB-C13-3b234d3edb50d5f632fa1a8b21b911dd.pdf), referencial de cuidados com Richardson/GCI.

O dataset contém comparações de cada `n`, hashes de malha, métricas de forma, Kt A/B/C, tensões radiais residuais, diferenças de deslocamentos Elmer×SciPy, balanço de carga e resultados completos dos gates de convergência.

## 8. Próximo gate

A estratégia escalonada **deve ser preservada como alternativa de malha, não promovida ainda a padrão único**. A próxima intervenção precisa controlar a distribuição angular e a vizinhança do furo, possivelmente com blocos externos adicionais, progressão radial por regiões ou novo mapeamento transfinite. A prova de melhora deve incluir **qualidade global e da primeira faixa, tração radial residual e consistência dos três recuperadores**, sem alterar condições físicas nem otimizar diretamente pelo valor de Peterson.

Nenhuma dessas simulações constitui evidência experimental ou critério de aceitação de olhais reais, estruturas soldadas, dispositivos de içamento ou equipamentos da mina.
