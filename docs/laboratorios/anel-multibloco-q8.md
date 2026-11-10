# Laboratório 19 — Anel transfinite Q8 com quatro blocos

**Data:** 09/11/2026, Santarém/PA. **Versão:** 0.19.0. [Issue #19](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/19). **Experimento:** 16 novos modelos externos Elmer/SciPy, com auditoria real e dataset permanente.

## 1. Problema herdado

Nos [ciclos 16–18](../ciclos/ciclo-18.md), refinamentos de malha Q8 de dois blocos aproximaram algumas estimativas de Kt, mas revelaram instabilidade da geometria e resíduos de tensão na parede livre do furo. O [ciclo 17](progressao-radial-q8.md) diminuiu a maior razão de cordas global em cerca de 48%, porém a primeira faixa e a tensão radial residual continuaram problemáticas. O [ciclo 18](distribuicao-angular-q8.md) testou uma gradação angular que **piorou ambos os indicadores**; a curvatura da interface dos dois blocos também produziu jacobianos não positivos.

**Hipótese:** um anel próprio, com malha radial e angular regular, pode reduzir o alongamento perto do furo; entretanto, a passagem desse anel ao retângulo alongado poderá deslocar a distorção para o exterior. O teste deve informar **ambos os efeitos**, sem selecionar um Kt favorável.

## 2. Topologia implementada

A chapa completa tem comprimento \`L=2Hx\` na direção da tração, largura \`W=2Hy\`, furo circular de diâmetro \`d=2a\` e simetrias. O quarto positivo \`x≥0,y≥0\` conserva **exatamente a mesma fronteira física** dos ciclos anteriores.

Duas curvas circulares internas de raio \`r_m=2a\` dividem o domínio em quatro superfícies transfinite, todas com quadriláteros isoparamétricos serendipidade de oito nós:

- **Blocos 101 e 102:** anel \`a≤r≤2a\`, subdividido nos setores \`θ=0…45°\` e \`θ=45…90°\`.
- **Blocos 103 e 104:** transição do arco \`r=2a\` às bordas do retângulo, nos mesmos setores.
- **Interface conforme:** cada uma das \`n_t\` arestas de interface é compartilhada por **exatamente dois elementos Q8**, inclusive nó intermediário; a conferência rejeita nós duplicados ou arestas pendentes.
- **Grupos físicos:** todas as quatro superfícies possuem um único material; a face \`x=Hx\` recebe tração, as duas faces de simetria recebem deslocamentos normais nulos, o topo \`y=Hy\` e o furo são livres.

O esquema segue o [manual do Gmsh: malhas transfinite, curvas, superfícies e recombinação](https://gmsh.info/doc/texinfo/gmsh.html); é uma escolha geométrica do projeto, não uma geometria prescrita por norma.

### 2.1 Controle da gradação

O número de divisões radiais \`n_r\` é separado em duas metades iguais \`N_i=N_o=n_r/2\`, com \`n_t=2n_r\`. No anel, a distribuição radial é **uniforme**; no exterior, os segmentos seguem:

\[
q_o=\exp\left(\frac{4}{N_o}\right), \qquad q_o^{N_o}=e^4\approx54,60.
\]

O parâmetro \`β=4\` é **hipótese de malha**, não um ajuste para um valor de Kt. O grande crescimento acumulado no bloco exterior poderá contribuir para os elementos alongados observados; a causalidade exata depende de estudo geométrico adicional.

Em cada malha, o número total de elementos permanece \`n_r n_t=2n_r²\`, distribuídos pelos quatro blocos sem nós pendentes, e a primeira faixa tem \`n_t\` elementos Q8.

## 3. Condições físicas preservadas

- Furo circular livre: \`a=0,01 m\`.
- Relações \`d/W=0,25\` e \`0,125\`; \`L/W=2\` e \`4\`.
- Elasticidade **linear isotrópica em tensão plana**: \`E=200 GPa\`, \`ν=0,30\`.
- Tração na direção x na face direita: \`T=10 MPa\`. Topo e furo livres.
- Simetrias: \`Ux=0\` em x=0 e \`Uy=0\` em y=0.
- Espessura de referência \`t=0,005 m\`; resultante esperada do quadrante \`F=T Hy t\`.
- Resoluções \`n_r=24,32,40,48\`, com **1.152, 2.048, 3.200 e 4.608 Q8**, respectivamente.

O Gmsh gera MSH2 e o ElmerGrid importa malha com os grupos físicos. O ElmerSolver resolve elasticidade; o FEM Q8 SciPy calcula deslocamentos e reações de comparação; os recuperadores A (gradiente direto), B (extrapolação de Gauss) e C (patch local ponderado, **não SPR certificado**) usam o **mesmo deslocamento Elmer**. Os resultados não são ensaio de material nem verificação de segurança de olhais.

## 4. Gates estruturais antes do solver

O [smoke CAD do workflow](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42739742200) gerou e validou as **16 geometrias Q8** antes de autorizar as simulações. Todas passaram os verificadores de jacobianos positivos nos pontos usados, fronteiras físicas e interface circular conforme.

O validador \`src/engmec/multibloco_anel.py\` reconstrói cada aresta Q8 de \`r=2a\`, exige exatamente \`n_t\` arestas, \`n_t+1\` vértices únicos, incidência dois por aresta e coincidência de seu nó intermediário. O importador confere \`n_r n_t\` elementos, \`n_t/2\` arestas na face tracionada e no topo e \`n_t\` no furo.

**Esses controles não certificam a malha como suficientemente precisa:** jacobiano positivo demonstra integridade local nos pontos avaliados, mas não substitui avaliação de forma, condicionamento numérico ou convergência física.

## 5. Resultado numérico com a malha mais fina — n=48

### 5.1 Qualidade de forma: melhora local, piora global

A métrica é a razão entre a maior e a menor **corda dos vértices** em cada Q8, uma proxy geométrica de alongamento. Comparamos sempre os **mesmos d/W, L/W e número de elementos** com a malha de dois blocos e progressão radial escalonada do [ciclo 17](../dados/ciclo17-malha-radial-2026-11-08.json).

| d/W | L/W | Pior razão no furo — anterior | 4 blocos | Pior global — anterior | 4 blocos | Ângulo mínimo — anterior | 4 blocos |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 2.021 | 2.547 | 5.928 | 14.880 | 24.30° | 21.44° |
| 0.250 | 4 | 3.931 | 2.547 | 11.639 | 31.223 | 12.15° | 10.05° |
| 0.125 | 2 | 4.258 | 2.547 | 6.296 | 17.231 | 25.50° | 24.30° |
| 0.125 | 4 | 8.075 | 2.547 | 12.002 | 33.832 | 13.12° | 12.15° |

O anel próprio reduz a pior razão de cordas da primeira faixa **em três de quatro geometrias**. O maior ganho é \`d/W=0,125, L/W=4\`: **8,075→2,547**. No entanto, \`d/W=0,25,L/W=2\` **piora de 2,021→2,547**. Em **todas as quatro chapas**, a pior razão **global aumenta de forma significativa**, atingindo **33,832** para \`d/W=0,125,L/W=4\`. Os **menores ângulos globais também pioram** (por exemplo 13,12°→12,15° no mesmo caso).

**Interpretação:** a qualidade do primeiro anel ficou praticamente independente do comprimento da chapa, mas **as superfícies externas continuam mal condicionadas geometricamente**. Não usar o resultado local para alegar que a malha toda melhorou.

### 5.2 Condição de tração radial livre: piora em todas as chapas

No furo, o vetor de tração deve ser nulo; em particular, \`σrr/T→0\` e \`σrθ/T→0\`. O residual normal no ponto crítico, recuperado pelo método C, foi:

| d/W | L/W | σrr/T anterior | 4 blocos | Fator de aumento |
| ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 1.6869e-4 | 2.1451e-3 | 12.7× |
| 0.250 | 4 | 1.7917e-4 | 2.1414e-3 | 12.0× |
| 0.125 | 2 | 9.7397e-4 | 1.9493e-3 | 2.0× |
| 0.125 | 4 | 1.0204e-3 | 1.9481e-3 | 1.9× |

Em \`d/W=0,25,L/W=2\` a razão entre os resíduos aumentou em **cerca de 12,7 vezes**. Mesmo nos demais casos a nova malha piorou. O aumento pode depender da distribuição de tamanhos perto da interface anular e da própria recuperação superficial; **não foi identificada uma causa raiz com os dados disponíveis**.

### 5.3 Kt líquido e GCI: interpretação limitada

O \`Kt_gross\` é calculado em relação à tração bruta \`T\`; \`Kt_net=(1-d/W)Kt_gross\`. A referência de Peterson vale para **tira suficientemente longa de largura finita**, não como solução exata da chapa retangular finita.

| d/W | L/W | Kt líquido C anterior | 4 blocos | Mudança relativa | GCI condicional C, 4 blocos |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 2.439776 | 2.438025 | -0.0718% | 0.1053% |
| 0.250 | 4 | 2.435855 | 2.434093 | -0.0723% | 0.1053% |
| 0.125 | 2 | 2.675120 | 2.674067 | -0.0394% | 0.1002% |
| 0.125 | 4 | 2.673983 | 2.672922 | -0.0397% | 0.1001% |

As quatro séries n=24/32/40/48 do método C passaram os **gates programados para estimativas condicionais de GCI**; os valores resultantes ficaram da ordem de **0,10–0,105%**, maiores do que os índices condicionais obtidos no ciclo 17. O sucesso desses gates **não certifica erro total**, e muito menos corrige a piora da condição de tração livre.

## 6. Execução, reprodutibilidade e decisão

**Evidências:**

- [Workflow completo com smoke, dois jobs Elmer e consolidação aprovados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42739742200).
- [Dataset integral permanente com os 16 casos](../dados/ciclo19-anel-multibloco-2026-11-09.json), incluindo qualidade por malha, confrontos A/B/C, pressão radial, comparação SciPy, hashes, contornos e GCI condicional.
- [Artefato bruto ~60 MB — MSH2, GEO, SIF, VTU, Gauss CSV e logs](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42739742200/artifacts/13728029675). SHA256 do ZIP: \`845ea858ff3f2093d4dfa0c910d409aa42535fbe1b6240e94f6290577f218af4\`; retenção informada até **10/12/2026**.
- [Gmsh — documentação oficial](https://gmsh.info/doc/texinfo/gmsh.html), para superfícies transfinite com quadriláteros de segunda ordem.

Reproduzir a chapa mais longa:

\`\`\`bash
python -m pip install -e ".[elmer]"
python -m engmec.elmer_chapa \
  --nr 48 --nt 96 --raio-m .01 \
  --semilargura-m .08 --semicomprimento-x-m .32 \
  --progressao-radial escalonada \
  --topologia anel-quatro-blocos \
  --saida build/ciclo19/ha-8-lw-4-n-48
\`\`\`

A interface de linha de comando mantém **\`--topologia dois-blocos\` como padrão**. A variante \`anel-quatro-blocos\` permanece **experimental**, sem promoção.

**Decisão:** o anel é um avanço na **conformidade e no isolamento geométrico do furo**, mas **a estratégia externa e a tensão radial na parede livre não satisfizeram o gate de aceitação**. A issue #19 segue aberta. Próximo ciclo: experimentar transições externas com mais blocos e ajustar a distribuição radial exterior pela qualidade **local e global**, sem otimizar pelo valor de Kt.

**Segurança:** modelos 2D simplificados, sem pino, contato, solda, fadiga, plastificação ou ensaio de peças reais. Não utilizar os fatores Kt como critério de liberação de equipamento, dispositivo de içamento ou componente de manutenção.
