# Laboratório 13 — Elmer FEM externo versus Q8 autoral e CalculiX

O objetivo deste laboratório é verificar a concentração de tensões ao redor de um furo central em uma **chapa quadrada finita sob tração real**, resolvendo **o mesmo problema em um solver FEM externo adicional, o Elmer**, e confrontando deslocamentos e tensões com o FEM Q8 independente desenvolvido em NumPy/SciPy no [ciclo 12](dois-solvers-q8.md).

**Distinção de método:** o Elmer não reutiliza a matriz global nem o solucionador NumPy/SciPy; a comparação inicial do fator de concentração usa **o mesmo recuperador de gradiente de deslocamentos** para os dois campos de deslocamentos. Isso isola melhor a diferença de solução numérica em relação aos resultados anteriores, que misturavam outro solver com outra técnica de extrapolação de tensões.

**Estado verificado:** seis execuções externas Elmer FEM/ElmerGrid concluídas, confrontadas com seis execuções Q8 NumPy/SciPy sobre as mesmas malhas Gmsh. O workflow e a consolidação foram aprovados em 07/11/2026.

## 1. Problema mecânico

Modelamos um quarto da chapa \`0≤x≤H,0≤y≤H,r≥a\`; a chapa completa é quadrada, com furo central livre. As condições físicas são:

- raio do furo \`a=10 mm\`, meia largura \`H=40 ou 80 mm\` (\`H/a=4\` ou 8);
- tensão plana (\`σzz=0\`), pequenos deslocamentos, \`E=200 GPa\`, \`ν=0,30\`;
- tração \`T=10 MPa\` na borda \`x=H\` do quadrante;
- topo \`y=H\` e furo \`r=a\` sem tração;
- simetria \`Ux=0\` em \`x=0\`, \`Uy=0\` em \`y=0\`.

No FEM autoral, a rigidez é integrada como \`t BᵀDB\` e a carga de borda como \`t T\`; no Elmer, a formulação bidimensional usa a tração nominal \`T\` por unidade de espessura. **A espessura cancela dos deslocamentos lineares elásticos** quando carga de superfície e rigidez recebem a mesma espessura constante. Para igualar o modelo, verificamos os deslocamentos, reações de referência, campos de tensão e condicionamento da malha.

## 2. Origem da geometria e do solver

O arquivo \`.geo\` reutiliza a construção CAD de **duas superfícies Gmsh transfinite** do ciclo 11, contendo exclusivamente quadriláteros serendipidade Q8. Acrescentamos **grupos físicos de contorno identificáveis** (borda tracionada, simetrias, topo livre, furo livre) e um grupo físico para o material.

O Gmsh gera um único arquivo **MSH2 ASCII**. O Elmer recebe esse mesmo arquivo pela conversão \`ElmerGrid 14 2 model.msh -autoclean -out elmermesh\`. Não se presumem IDs de superfície antes da conversão: o script lê \`mesh.nodes\`, \`mesh.elements\` e \`mesh.boundary\` do Elmer e **identifica as etiquetas de fronteira pelas coordenadas reais dos seus nós**. O arquivo resultante \`case.sif\` vincula cada condição ao identificador apurado.

No \`case.sif\`, o \`StressSolver\` do Elmer usa elasticidade linear isotrópica com \`Plane Stress=True\`; a borda direita recebe \`Force 1 = T\`, os dois eixos recebem apenas o deslocamento normal nulo, e as demais superfícies permanecem livres.

Fontes principais:

- [ElmerCSC — repositório oficial do solver](https://github.com/ElmerCSC/elmerfem).
- [Elmer — manual de modelos do módulo de elasticidade linear](https://www.nic.funet.fi/index/elmer/doc/ElmerModelsManual.pdf).
- [Exemplo original StressSolve/StressSolver com força em borda](https://github.com/ElmerCSC/elmerfem/blob/devel/fem/tests/ElastPelem2dPmultg/case.sif).
- [Gmsh — grupos físicos e formato MSH](https://gmsh.info/doc/texinfo/).
- [CSC — Elmer, aplicações e licença](https://docs.csc.fi/apps/elmer/).

## 3. Independência numérica e pós-processamento

O pipeline possui três níveis claramente diferentes:

| Nível | Implementação | Comparação viável |
| --- | --- | --- |
| 1 | CalculiX CPS8R | solução FEM externa e tensão superficial por extrapolação de pontos de Gauss |
| 2 | Python/SciPy Q8, Gauss 3×3 | formulação Q8 autoral, solução esparsa independente do CalculiX |
| 3 | Elmer FEM StressSolver | outro programa FEM externo consolidado com seu próprio código e montagem |

Para comparar Elmer e SciPy em condições homogêneas, **não** usamos \`Kt\` de extrapolação de Gauss neste confronto inicial. Cada programa calcula um vetor de deslocamentos sobre a malha compartilhada. O Elmer escreve um \`VTU\` de deslocamentos, cujos nós são pareados por **proximidade geométrica dentro de tolerância explícita**, necessária porque o VTU pode armazenar coordenadas em precisão inferior à MSH2 original.

Sobre cada vetor, aplicamos **o mesmo recuperador \`σ=DBu\` diretamente no vértice do furo em \`(0,a)\`**. Assim separamos, tanto quanto possível, a contribuição do campo de deslocamentos. Isso também significa que **a incerteza do operador de recuperação continua compartilhada**; mesmo a concordância perfeita de Kt não provaria que o pico superficial é exato.

As grandezas de verificação são:

- \`ux(H,0)\`, \`uy(0,H)\`, \`ux(a,0)\`, \`uy(0,a)\`, cada uma em metros;
- \`Kt_bruto=σθθ(0,a)/T\` pelo mesmo recuperador Q8;
- \`Kt_líquido=(1-a/H)Kt_bruto\`;
- \`σrr/T\` e \`σrθ/T\` na parede, que idealmente se aproximam de zero;
- reação horizontal e resíduo algébrico do solver autoral; integridade do malhamento e da conversão;
- número de elementos, nós, hashes MSH2, versão da imagem de Elmer e arquivos brutos.

A solução analítica \`Kt=3\` de Kirsch vale **para placa infinita**: não constitui solução exata da chapa quadrada finita sob as condições aqui simuladas.

## 4. Reprodutibilidade do ambiente

O workflow usa Ubuntu 24.04, Gmsh, NumPy, SciPy e \`meshio\`. A execução externa de Elmer é realizada por imagem Docker \`ghcr.io/femforge-io/femforge-elmer:0.2.0\` que instala o pacote Elmer da distribuição PPA mantida pela comunidade Elmer/CSC. O pipeline registra o **digest concreto da imagem** e as versões das dependências Python. A dependência Elmer permanece externa ao pacote Python da biblioteca.

O Elmer é software livre com componentes sob GPL e LGPL; a integração aqui utiliza apenas execução do programa de forma separada, sem incorporar código-fonte Elmer ao repositório. [Referência de redistribuição e versão do contêiner](https://docs.femforge.io/user-guide/elmer/).

Exemplo, com Gmsh e ElmerGrid/ElmerSolver no PATH:

\`\`\`bash
python -m pip install -e ".[fem2d]"
python -m pip install "meshio>=5.3,<6"
python -m engmec.elmer_chapa --nr 16 --nt 32 \
  --semilargura-m 0.04 \
  --saida build/ciclo13/elmer/ha-4-n-16
\`\`\`

O [workflow externo do ciclo 13](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/ciclo13-elmer.yml) configura automaticamente os binários de Elmer via Docker e preserva \`.geo\`, \`.msh\`, \`mesh.*\` convertidos, \`.sif\`, \`.vtu\`, logs e comparações \`.json\`. O objetivo são três malhas \`n=8,16,24\` por meia largura.

## 5. Limites científicos e uso em manutenção

O Elmer é um **segundo solver FEM externo**, mas o operador de tensão recuperada foi deliberadamente mantido igual ao usado no SciPy para não contaminar a comparação dos campos. O modelo continua bidimensional, linear-elástico, com furo **livre**, sem apoio de pino, contato, trincas, soldas, plastificação ou fadiga. Tampouco há validação experimental.

Antes de aplicar esse resultado à engenharia de componentes, ainda são necessários estudo de incerteza superficial, segunda técnica de pós-processamento e referência independente ou ensaio da chapa finita nas mesmas condições. **Os números apresentados não são tensão admissível nem autorizam liberação operacional.**

## 6. Resultados observados — execução externa de 07/11/2026

O [workflow #42428467703](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42428467703) concluiu **seis casos Elmer** e **seis soluções SciPy** com três malhas por meia largura, todas com o mesmo arquivo Gmsh de origem. O solucionador externo Elmer FEM executou o módulo `StressSolver`, gerou os VTU de deslocamentos e passou a reconciliação geométrica dos nós.

| W (mm) | Elementos Q8 | Kt bruto Elmer (gradiente) | Kt bruto SciPy (gradiente) | σrr/T na parede, Elmer |
| ---: | ---: | ---: | ---: | ---: |
| 80 | 128 | 3.618124 | 3.618124 | 11.839% |
| 80 | 512 | 3.588914 | 3.588914 | 1.587% |
| 80 | 1152 | 3.584406 | 3.584406 | 0.288% |
| 160 | 128 | 3.213273 | 3.213273 | 29.930% |
| 160 | 512 | 3.152512 | 3.152512 | 5.519% |
| 160 | 1152 | 3.139032 | 3.139032 | 0.969% |

A **maior divergência relativa nos deslocamentos de referência** de todos os casos foi menor que **7×10⁻¹³**. A diferença absoluta máxima em `Kt` entre Elmer e SciPy ficou abaixo de **7×10⁻¹¹**, com o **mesmo recuperador de tensão**. A concordância em nível de arredondamento confirma uma implementação discreta compatível, mas **não valida a precisão de Kt na superfície**, porque malha, interpolação Q8, hipótese material e operador `B` de pós-processamento são compartilhados.

As tensões radiais normalizadas na parede `σrr/T`, que deveriam ser zero para uma parede livre, decaíram de **11,84% para 0,288%** na chapa W=80 mm e de **29,93% para 0,969%** na de W=160 mm entre as malhas 128 e 1.152 elementos. A melhora confirma que a avaliação pontual do gradiente junto ao contorno ainda apresenta erro de discretização. **Não é correto afirmar que todos os indicadores convergiram ao valor físico verdadeiro**, pois não foi obtida referência exata para a chapa quadrada finita.

### Validação dos arquivos e correções de execução

- A primeira execução identificou que a saída VTU do Elmer podia utilizar **coordenadas deformadas**; a correspondência por arredondamento decimal não era adequada.
- O primeiro ajuste, que apenas considerava precisão inferior de coordenadas, ainda falhou quando encontrou deslocamentos de alguns micrômetros. A correção final impõe `Displace Mesh = False` no `case.sif` e também verifica, quando necessário, a transformação `x_ref = x_vtu - u`, exigindo **pareamento bijetivo de todos os nós** dentro de tolerância física, nunca aceitando malha incompatível.
- Os seis casos da execução final foram resolvidos; os logs das tentativas reprovadas permanecem nos respectivos GitHub Actions.

### Evidências e auditoria

- [Workflow aprovado, com Elmer real](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42428467703).
- [Arquivos brutos: MSH, malha ElmerGrid, SIF, VTU, logs e versões](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42428467703/artifacts/13596965037). Retenção prevista até **08/12/2026**.
- [Dataset JSON permanente](../dados/ciclo13-elmer-fem-2026-11-07.json).
- O artefato inclui `elmer-image-digest.txt` e `pip-freeze-elmer.txt`, preservando imagem/versões efetivamente executadas.

## 7. Conclusão científica

O ciclo completou o objetivo de **usar um segundo solver FEM externo** e demonstrou que os dois procedimentos de resolução do problema discreto produzem deslocamentos equivalentes com o mesmo recuperador de tensão. A comparação anterior com CalculiX, cujo `Kt` provém de **outro procedimento de extrapolação de Gauss**, continuará sendo usada para investigar quanto da diferença de Kt se origina na **recuperação superficial**, e não na solução mecânica.

**Pendente:** referência externa específica de chapa quadrada finita, estimativa de incerteza do pico no contorno e comparação com apoio de pino/contato quando houver um problema material apropriado.
