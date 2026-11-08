# Laboratório 15 — Efeito do comprimento e da largura na concentração de tensões

**Versão 0.15.0 · 08/11/2026 · 18 modelos Elmer FEM externos executados com sucesso.**

Este laboratório avança em relação ao [ciclo 14](recuperacao-tensoes-furo.md): mantém **diâmetro do furo, largura resistente e tensão nominal constantes** dentro de uma série e altera **somente o comprimento na direção da tração**. O objetivo é compreender por que a chapa quadrada não deve ser comparada diretamente com a fórmula de **tira muito longa** com furo central.

## 1. Definição rigorosa da geometria e dos fatores

A chapa completa tem um furo circular central e dimensões \`L×W=2Hx×2Hy\`; o carregamento atua ao longo de **x**, nas faces \`x=±Hx\`. A largura \`W\` é a dimensão transversal (eixo y). O diâmetro do furo é \`d=2a\`.

\[
\frac{L}{W}=\frac{H_x}{H_y},\qquad
\frac{d}{W}=\frac{a}{H_y},\qquad
K_{t,\mathrm{bruto}}=\frac{\sigma_{\theta\theta,\mathrm{furo}}}{T},
\qquad
K_{t,\mathrm{líquido}}=(1-d/W)K_{t,\mathrm{bruto}}.
\]

A tensão nominal bruta \`T\` é a tração aplicada à borda; a tensão nominal líquida equivalente é \`T/(1-d/W)\`. *Não comparar Kt bruto com referência definida sobre seção líquida.*

Modelamos só o quarto \`x≥0,y≥0,r≥a\`, com **simetria** \`Ux=0\` no eixo x=0 e \`Uy=0\` no eixo y=0. A borda externa \`x=Hx\` recebe tração \`T=10 MPa\`; o topo \`y=Hy\` e o furo \`r=a\` são livres. Material isotrópico, linear, tensão plana, \`E=200 GPa\`, \`ν=0,30\`; espessura de referência \`t=5 mm\`.

Parâmetros executados:

| Parâmetro | Níveis |
| --- | --- |
| Raio \`a\` | 10 mm, fixo |
| Largura \`W\` | 80 mm ou 160 mm |
| Razão furo/largura \`d/W\` | 0,25 ou 0,125 |
| Razão comprimento/largura \`L/W\` | 1, 2 e 4 |
| Malhas estruturadas Q8 | 128, 512, 1.152 elementos |
| Número de combinações | **18 execuções Elmer** |

## 2. Malha e resolução: o que foi alterado

O [CAD Gmsh de dois blocos](https://gmsh.info/doc/texinfo/) dos ciclos anteriores foi estendido pela nova rotina \`src/engmec/chapa_retangular.py\`. Para \`Hx>Hy\`, somente as posições dos pontos exteriores da face x e do canto superior direito são alteradas. As superfícies são recompostas por **interpolação transfinite** e quadriláteros serendipidade Q8; os contornos do furo conservam o raio a, e a tração continua aplicada à face x=Hx.

\`src/engmec/gmsh_chapa.py\` reconhece a borda tracionada em x=Hx sem confundi-la com o topo livre y=Hy. O adaptador \`src/engmec/elmer_chapa.py\` passa a identificar as superfícies do ElmerGrid em coordenadas distintas \`Hx\`/\`Hy\` e a exigir integridade dos contornos. O solucionador autoral SciPy acompanha o comprimento de referência, mantendo a resultante do quarto \`F=T·Hy·t\`: **essa força não aumenta com o comprimento**, porque a borda tracionada permanece da mesma altura.

Cada execução calcula a tensão por três recuperadores já testados no [laboratório 14](recuperacao-tensoes-furo.md), sobre o **mesmo vetor de deslocamentos Elmer**:

- **A:** derivada de um Q8 no nó superior do furo;
- **B:** extrapolação local de tensões de Gauss 3×3 por seis coeficientes;
- **C:** ajuste local de *patch* ponderado, quatro coeficientes, **exploratório e não SPR certificado**.

As malhas são de mesma família e têm igual número de elementos nos pares comparados, mas seus elementos **mudam de forma com L/W**. Portanto, a escolha de \`nr,nt\` idênticos **não garante a mesma precisão local**, especialmente nas chapas longas.

## 3. Referência externa: Peterson/Howland, tensão líquida

O ajuste clássico para chapa de **largura finita, mas comprimento suficientemente grande** e furo central sob tração remota é:

\[
K_{t,\mathrm{líquido}}\approx
3-3{,}14\rho+3{,}667\rho^2-1{,}527\rho^3,\quad \rho=d/W.
\]

Não é a solução exata da chapa quadrada. Fontes de verificação e limites:

- [ANSYS PyMAPDL — 2D Plane Stress Concentration Analysis](https://mapdl.docs.pyansys.com/version/stable/examples/gallery_examples/00-mapdl-examples/2d_plate_with_a_hole.html): geometria retangular longa, elementos PLANE183 e ajuste de Peterson; a aplicação do método usa **tensão nominal líquida**.
- [Wang et al., *Materials*, 2019, DOI 10.3390/ma12030422](https://pmc.ncbi.nlm.nih.gov/articles/PMC6384607/): compara resultados de chapas com \`L/W=1…5\` e a aproximação de tira longa, observando estabilização em seus modelos quando \`L/W>3\`. Seu material homogêneo é comparável qualitativamente; malha, dimensões e pós-processamento **não são idênticos** aos nossos.
- [MathWorks — Stress Concentration in Plate with Circular Hole](https://www.mathworks.com/help/pde/ug/stress-concentration-in-plate-with-circular-hole.html): destaca a necessidade de afastar as extremidades tracionadas para recuperar a condição de tração remota.
- [Gmsh — Transfinite Surface e Recombine](https://gmsh.info/doc/texinfo/): documentação oficial de construção de elementos quadrilaterais.

A referência de Kirsch \`Kt=3\` representa uma placa infinita **também em largura**, e portanto não deve substituir a fórmula de Peterson para a tira de **largura finita**.

## 4. Resultados reais: malha de 1.152 Q8

O [workflow #42522437925](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42522437925) executou todos os 18 modelos no Elmer e no solucionador Q8 SciPy de comparação, com recuperação A/B/C e testes de integridade. O **caso quadrado L/W=1 reproduziu os seis baselines numéricos do ciclo 14** em todos os tamanhos de malha.

### 4.1 Kt líquido estimado pelo método C

| d/W | L/W=1 | L/W=2 | L/W=4 | Peterson, tira longa |
| ---: | ---: | ---: | ---: | ---: |
| 0,25 | 2,685776 | 2,438535 | 2,434541 | 2,420328 |
| 0,125 | 2,735588 | 2,668119 | 2,666769 | 2,661814 |

Em \`d/W=0,25\`, o resultado \`L/W=4\` difere da curva Peterson em **+0,587%**. Em \`d/W=0,125\`, difere em **+0,186%**. As diferenças são pequenas para esse **refinamento e recuperador**, mas **não equivalem a demonstração de exatidão**, porque os resultados ainda mudam com a malha e com o método de recuperação.

### 4.2 Valores brutos e recuperação no mesmo campo

| d/W | L/W | Kt bruto A | Kt bruto B | Kt bruto C | Diferença entre recuperadores |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0,25 | 1 | 3,584406 | 3,582520 | 3,581034 | 0,003372 |
| 0,25 | 2 | 3,254295 | 3,252410 | 3,251380 | 0,002915 |
| 0,25 | 4 | 3,248941 | 3,247364 | 3,246055 | 0,002886 |
| 0,125 | 1 | 3,139032 | 3,128814 | 3,126387 | 0,012645 |
| 0,125 | 2 | 3,061816 | 3,051669 | 3,049278 | 0,012538 |
| 0,125 | 4 | 3,060731 | 3,051216 | 3,047736 | 0,012995 |

Os três estimadores concordam relativamente bem nessas malhas finas, mas compartilham o campo FEM e podem possuir erro comum. A amplitude A/B/C mede **sensibilidade ao pós-processamento**, não limite máximo de erro físico.

### 4.3 Efeito do refinamento ainda relevante

Para \`d/W=0,25,L/W=4\`, o Kt bruto C evolui **3,040429 → 3,229938 → 3,246055** (128→512→1152 elementos). Para \`d/W=0,125,L/W=4\`, evolui **2,462854 → 2,980114 → 3,047736**. Em particular, a segunda série ainda varia **cerca de 2,27% entre 512 e 1.152 elementos** no método C. Portanto, a proximidade da curva Peterson no último nível pode ser parcialmente fortuita: *não se demonstrou convergência assintótica*.

### 4.4 O que a experiência permite concluir

1. Para os níveis ensaiados, **aumentar L/W de 1 para 2 reduz muito mais Kt do que passar de 2 para 4**, com \`d/W\` e tração constantes.
2. As chapas longas se aproximam da curva da tira de largura finita, confirmando uma **tendência física qualitativa prevista na literatura**, sem provar igualdade exata.
3. Os casos \`L/W=1\` reproduziram o baseline anterior e protegem contra mudanças inadvertidas na geometria e nos contornos.
4. As malhas grosseiras, especialmente para \`d/W=0,125\`, **ainda são inadequadas para estimar o pico superficial com precisão defensável**.
5. O erro de solução, o erro de pós-processamento e a escolha do domínio não devem ser confundidos.

## 5. Reproduzir os resultados

Requer Gmsh CLI, ElmerGrid, ElmerSolver e Python com extras \`elmer\`. O workflow instala o Elmer externo via imagem Docker com digest registrado e preserva a versão dos pacotes Python.

\`\`\`bash
python -m pip install -e ".[elmer]"
python -m engmec.elmer_chapa \
  --nr 24 --nt 48 --raio-m .01 \
  --semilargura-m .04 \
  --semicomprimento-x-m .16 \
  --saida build/ciclo15/elmer/ha-4-lw-4-n-24

python scripts/avaliar_ciclo15.py --pasta build/ciclo15/elmer
\`\`\`

O último comando consolida **somente após todos os 18 casos** estarem presentes e verificados.

**Evidências:**

- [Workflow Elmer externo com 18 casos](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42522437925)
- [Dataset permanente](../dados/ciclo15-chapas-retangulares-2026-11-08.json), incluindo três refinamentos, tensões brutas/líquidas, recuperação, erros relativos e diagnósticos
- [Artefato bruto com 15 MB de arquivos](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42522437925/artifacts/13633972465) — \`.geo\`, \`.msh\`, \`.sif\`, \`.vtu\`, \`mesh.*\`, \`deslocamentos_elmer.json\`, \`gauss_tensoes.csv\`, logs e arquivo de digest do Docker; retenção até **08/12/2026**

## 6. Limites e aplicação à manutenção

A comparação é uma **verificação didática de domínio em elasticidade 2D**, não medição nem validação experimental. Não inclui pino, contato unilateral, folga, solda, carregamento excêntrico, plastificação, trincas, fadiga ou características do aço efetivamente empregado em equipamento pesado.

Em uma análise real de olhal, suporte ou chapa de fixação de mina, é obrigatório obter geometria real, cargas, apoios, estados limite, fabricação, histórico de dano e critérios de aceitação. **Não utilizar os Kt desta série como valores admissíveis de segurança ou autorização de operação.**
