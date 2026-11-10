# Roadmap mestre de longo prazo

## Missão

Construir uma base pública, pesquisável e tecnicamente verificável de Engenharia Mecânica em português, relacionando fundamentos, literatura, cursos externos, experimentos, softwares, simulação, diagnóstico e aplicação. A métrica de êxito não é volume bruto de arquivos, mas **cobertura, rastreabilidade, rigor e reprodutibilidade**.

## Ondas de entrega e gates

| Onda | Horizonte indicativo* | Resultado | Critério de passagem |
| --- | --- | --- | --- |
| F0 — Fundação | concluído 2026-11-05 | site, código base, CI, 4 calculadoras iniciais e 20 fontes | site publicado, CI verde |
| F1 — Curadoria editorial | ciclos 2–5 | 100 itens verificados por obra, grade e 50 fichas autorais | links, direitos, fonte e revisão |
| F2 — Formação | ciclos 3–8 | 6 trilhas completas, avaliações e laboratório didático | pré-requisitos, exercícios e rubricas |
| F3 — Laboratório | ciclos 4–10 | 15 modelos numéricos, CAD/FEM/CFD e benchmarks | convergência, teste analítico e documentação |
| F4 — Pesquisa | ciclos 7–14 | API bibliográfica, busca semântica e grafo | proveniência, segurança, termos e benchmark |
| F5 — Comunidade | contínuo | governança comunitária e revisão científica | contribuidores, revisões e histórico público |

*Um ciclo é uma rodada verificável de trabalho e não representa prazo cronológico obrigatório.

## Eixos paralelos

1. **Fontes e direitos:** inventário por obra, licença por item e alterações.
2. **Conhecimento:** taxonomia coerente, definições, deduções, casos e material autoral.
3. **Educação:** unidades, trilhas, progressão e exercícios resolvidos.
4. **Ferramentas:** código testado, SI, modelos físicos e benchmarks.
5. **Infraestrutura:** site, CI, catálogo, ingestão e acessibilidade.
6. **Governança:** agentes, skills, issues, PRs e aceite explícito.

## Métricas de qualidade

- Completude de metadados (% com autor, URL, idioma, data, licença e status).
- Revisão de direitos (nº de obras auditadas individualmente / total).
- Cobertura por área (nº de fichas aprovadas / tópicos definidos).
- Testes de física (benchmarks e casos-limite verificados / modelos).
- Atualização das fontes (URLs válidas e fontes oficiais ainda aplicáveis).
- Reprodutibilidade (experimentos repetidos por segundo executor).
- Segurança (0 vazamentos de dados internos / 0 afirmações OEM sem modelo-série).

## Backlog priorizado

**P0:** publicação do portal, CI, instruções e contratos de dados.

**P1:** catálogo brasileiro/estrangeiro revisado, 50 fichas, 10 unidades aprofundadas e 15 casos genéricos de manutenção.

**P2:** novo pacote numérico com Pint/CoolProp, experimentos FreeCAD/Gmsh/CalculiX e revisão de limites físicos.

**P3:** conectores Crossref/OpenAlex/NASA e busca com citações; índices somente de dados permitidos.

**P4:** avaliações, contribuições externas, internacionalização opcional e métricas públicas.

## Riscos e respostas

- **Caos taxonômico:** IDs estáveis, dicionário de domínios, schema, deduplicação.
- **Volume sem qualidade:** publicação em fases com checklist e revisão.
- **Copyright:** somente link sem direito comprovado.
- **IA alucinando especificação:** fonte primária, teste, estado de incerteza e revisão.
- **Dívida tecnológica:** dependências opcionais, formatos abertos, interoperabilidade.
- **Concentração de manutenção:** documentação de operação, agentes e skills reusáveis.

## Critérios de encerramento de cada ciclo

Uma entrega concluída possui commit, arquivo(s) versionados, link de prova, testes verdes, lista de falhas e próximos issues. O registro de cada ciclo não deve afirmar execução de itens apenas planejados.

Detalhes: [conteúdo](conteudo.md), [formação](formacao.md), [ferramentas](ferramentas.md), [plataforma](plataforma.md), [qualidade](qualidade.md).

## Ciclo 05 — progresso

Cinco registros de auditoria documental de direitos com fonte primária (não cinco obras integralmente licenciadas para espelhamento), quatro fichas autorais e benchmark FEM 1D de barra axial com estudo do erro de tensão. Gates restantes: revisão humana de licenças de arquivos isolados, comparação com solver FEM externo e validação experimental. O ciclo de publicação deve ter testes e Pages verdes antes do aceite.

**Aceite do ciclo 05:** [CI](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42052167589) com 37 testes aprovados; [GitHub Pages](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42052167587) publicado. Próxima integração numérica externalizada em [issue #10](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/10).

## Ciclo 06 — escopo e critérios

Integração com CalculiX por malha 3D autoral C3D8 e comparação com barra 1D para tração uniforme. Separar estritamente os testes do gerador/parser da **execução física no solver**. Meta de aceite: CI + workflow dedicado CalculiX com arquivos `.inp/.dat/.frd` arquivados, erro axial/equilíbrio menor que 2% em quatro malhas, Pages verde. Avançar só depois a problemas de gradiente e convergência não trivial.

**Ciclo 06 validado externamente:** GitHub Actions [#42055701419](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42055701419) executou CalculiX 2.21-1, quatro malhas C3D8, deslocamento 0,1 mm e reação −10 kN, com equilíbrio conforme tolerância. A evidência está em [JSON](../dados/calculix-c3d8-2026-11-05.json); isso não encerra o objetivo maior de convergência 3D não trivial.

## Ciclo 07 — erro não trivial de flexão pura

Problema novo: solução exata da elasticidade 3D sob flexão pura, tensões lineares `σxx(y)`, deslocamentos quadráticos, 6 graus de liberdade rigidamente eliminados, forças nodais de face integradas por Gauss, verificação independente de momentos e comparação com CalculiX C3D8 em quatro malhas. O critério só é atendido se houver erro inicial mensurável, redução de erro na malha fina e equilíbrio. Validar workflow antes de declarar concluído; acompanhar limitações de shear locking e futuras comparações C3D20R.

**Ciclo 07 verificado externamente:** [CalculiX C3D8](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42064616852) executado com gradiente de tensão em flexão pura. Erro de Uy caiu de 29,75% em 8 elementos a 0,99% em 4096 elementos; taxas aparentes chegaram a ~1,76. [Evidência JSON](../dados/flexao-pura-3d-2026-11-05.json). Próximos gates: C3D20R, erros de tensões, benchmarks com outras condições de carregamento e validação experimental.

## Ciclo 08 — verificação FEM com elemento quadrático

Comparar C3D8 e C3D20R no benchmark autoral de flexão pura, com malha geométrica equivalente e tensões provenientes de `COORD,S` nos pontos de Gauss do `.dat` do CalculiX. O gate contempla teste de interpolação Q8, integração de tração, balanço de forças/momento, erro RMS Sxx e custo em DOFs/tempo, com workflow de seis execuções reais. Conclusões devem acompanhar dados observados, limites físicos e licença dos softwares.

**Ciclo 08 aceito por solver:** [comparação CalculiX 2.21-1](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42411991123) executada em 6 malhas; [64 testes verdes](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42411991133). C3D20R reproduziu a solução quadrática com Uy na precisão textual e RMS de Sxx entre 10 Pa e 0,707 Pa, contra C3D8 de 15,9 MPa a 1,84 MPa. [Dados observados](../dados/comparacao-c3d8-c3d20r-2026-11-07.json). Próximo gate: geometria não prismática/contato ou concentração de tensões, sem abandonar a curadoria de fontes e cursos.

## Ciclo 09 — geometria curva e concentração de tensões

Novo laboratório de Kirsch: raio interno `a`, arco externo `R`, malha curva CPS8R em quarto de anel, deslocamentos analíticos no contorno externo, furo livre, simetria e extração de tensões de Gauss. O ciclo visa medir erro RMS no domínio e na primeira camada junto ao furo, com três malhas e comparação `R/a=4`/8. **Separar rigorosamente** `Kt=3` analítico, proxy interno do FEM e casos de **chapa finita fisicamente tracionada**, que ainda dependem de investigação.

**Ciclo 09 entregue como benchmark analítico:** [workflow real](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42415560152), 4 modelos CPS8R, erro RMS global ponderado por área **0,521%→0,117%→0,072%**, faixa física até 1,5a **2,439%→0,766%→0,448%**. O indicador interior de tensão circunferencial aproximou o Kt analítico de 3, sem medi-lo na superfície. [Dataset permanente](../dados/kirsch-cps8r-2026-11-07.json). **Issue #13 continua parcialmente aberta:** efeito físico de borda em chapa finita, validação do Kt superficial e possível Gmsh.

## Ciclo 10 — chapa quadrada finita com furo e tração aplicada

Novo benchmark independente do contorno prescrito do Kirsch: chapa finita 2D CPS8R, carga de tração `T` nas faces externas x=±H, y=±H/furo livres, condições de simetria, carregamento nodal integrado Q8, malha curva até a borda quadrada e extrapolação local das tensões de Gauss para o contorno do furo. Denominadores Kt bruto/líquido explícitos. Plano: três malhas em H/a=4 e largura H/a=8/16 com n=24. **Meta:** revisão de malha, solver real e sensibilidade, sem tratar Kirsch infinito como solução exata da chapa finita. Gmsh e ensaio físico permanecem pendentes.

**Ciclo 10 executado:** [CalculiX real](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42421310615), cinco modelos de chapa quadrada finita com furo, tração nas bordas e estimação de Kt bruto/líquido. Para W=80 mm, 128/512/1152 elementos deram Kt_bruto por extrapolação 3,5798/3,6177/3,6175; para W=160 e 320 mm, uma malha cada resultou 3,1640 e 3,0538. [Dataset](../dados/chapa-finita-furo-2026-11-07.json) e [limitações](../laboratorios/chapa-finita-furo.md). **Próximo gate:** malha independente, estudos de refinamento para outras larguras e referência de geometria/contornos equivalentes.

## Ciclo 11 — estudo de refinamento complementar e gerador Gmsh

A partir da v0.10, ampliar o refinamento da chapa quadrada finita tracionada nas larguras H/a=8 e H/a=16 (n=16,24,32). Comparar, com **mesmo CalculiX CPS8R e mesmo método de extrapolação**, malhas quadráticas oriundas do gerador polar autoral e do Gmsh CAD, em duas superfícies transfinite. Gerar e arquivar `.geo`, `.msh`, `.inp`, `.dat`, logs e JSON; exigir controle de jacobianos, forças, cargas e diferenças entre resultados. Independência de malha não substitui validação em segundo software ou ensaio. **Issue #13** permanece o controle da validade externa e da extrapolação.

**Ciclo 11 concluído como comparação geométrica:** [workflow de nove simulações](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42422518394), Gmsh 4.12.1, CalculiX 2.21-1, [92 testes aprovados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42422586573). Diferença de Kt entre Gmsh e autoral: −0,58%, −0,076%, −0,32% nos três pares. H/a=8/16 refinados com n 16,24,32. [Dataset](../dados/ciclo11-gmsh-chapa-2026-11-07.json). Próximo gate técnico: **segundo solver ou referência de chapa quadrada finita de mesmas condições**, além de análise rigorosa de incerteza da extrapolação superficial e pesquisa de geometria de olhal com contato, sem antecipar aplicação industrial.

## Ciclo 12 — Duas implementações FEM (executado)

O [Laboratório 12](../laboratorios/dois-solvers-q8.md) apresenta um solucionador Q8 em **NumPy/SciPy** com elasticidade isotrópica em tensão plana, rigidez `Ke=t∫BᵀDBdA` com quadratura Gauss 3×3, montagem esparsa, cargas Q8 e recuperação de tensão por gradiente diretamente no vértice do furo. **Quatro pares de simulações reais** foram confrontados com CalculiX CPS8R nas **mesmas malhas Gmsh, SHA256 coincidente**, sob carga nominal e material iguais. Diferenças de Kt entre −0,84% e +2,29%, sem convergência monotônica de todas as métricas; [dataset](../dados/ciclo12-solvers-independentes-2026-11-07.json). **Próximo gate obrigatório:** outro solver FEM externo validado (Elmer/FEniCSx), geometria quadrada finita de referência comparável e convergência da recuperação superficial por técnicas distintas. Issue #14 permanece aberta.

## Ciclo 13 — Segundo solver externo: Elmer FEM

A biblioteca adicionou adaptação do **Elmer FEM StressSolver** para a mesma chapa quadrada finita com furo e tração real, preservando grupos físicos, estado de **tensão plana** e malha Q8 exportada por Gmsh e convertida com ElmerGrid. Para comparar Elmer com o FEM SciPy, avalia o **mesmo recuperador de gradiente `σ=DBu`** sobre os deslocamentos independentes. O parser confere `mesh.boundary`, grupos de carregamento e geometria VTU e arquiva evidências. A decisão sobre a precisão do pico superficial ainda depende da análise de convergência dos campos e de referência independente de chapa finita. [Laboratório 13](../laboratorios/elmer-fem-independente.md).

## Ciclo 14 — Sensibilidade do pico superficial ao pós-processamento (concluído)

No [Laboratório 14](../laboratorios/recuperacao-tensoes-furo.md), seis modelos Elmer FEM externos foram processados com **três recuperadores de tensão no mesmo vetor nodal**: gradiente Q8 na parede, extrapolação de Gauss 3×3 (seis coeficientes) e patch ponderado (quatro coeficientes). A amplitude `max(Kt)-min(Kt)` decaiu de **0,26984 para 0,00337** em W=80 mm e de **0,65674 para 0,01264** em W=160 mm, entre 128 e 1152 elementos. O controle analítico Kirsch demonstra viés relevante dos métodos B/C na malha grosseira (W160 n8: −0,474/−0,566). [Evidências reais](../dados/ciclo14-recuperacao-tensoes-2026-11-08.json). Próximo gate: referência comparável de chapa quadrada finita, teste de tensão superficial com medição independente e **não aplicar coeficientes a componentes industriais sem essa validação**.

## Ciclo 15 — Efeito do domínio retangular (concluído)

O [Laboratório 15](../laboratorios/chapa-retangular-comprimento.md) gerou 18 análises em **Elmer FEM externo** para `d/W=0,25/0,125`, `L/W=1,2,4`, três malhas Q8. O comprimento está na direção da tração, a largura é transversal e as tensões bruta/líquida são diferenciadas. A geometria quadrada reproduziu seis baselines, e a tira `L/W=4` teve Kt líquido no recuperador C de **2,4345** para `d/W=0,25` (Peterson **2,4203**) e **2,6668** para `d/W=0,125` (Peterson **2,6618**), ambos com 1152 elementos. Entretanto, a variação entre 512 e 1152 elementos ainda pode ser relevante, notadamente **~2,27%** em `d/W=0,125,L/W=4`; não declarar convergência nem validação física. [Dataset](../dados/ciclo15-chapas-retangulares-2026-11-08.json), [workflow](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42522437925). Próximo gate: malhas mais refinadas e métrica de qualidade local, referência física idêntica e condições industriais reais.

## Ciclo 16 — Refinamento fino e diagnóstico de geometria (executado)

[12 casos Elmer/SciPy reais](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42525939565) ampliaram quatro séries de chapas retangulares para n32/40/48 (2048/3200/4608 Q8), usando o n24 do ciclo 15 como quarto ponto. O método C apresentou Δrel entre últimas duas malhas de **0,0011–0,0052%**, mas não superou os gates de ordem para GCI nas quatro séries. A **qualidade da malha preocupa**: em L/W=4, razão máxima de cordas de 22–23 e ângulo mínimo de 12–13° nos vértices, embora jacobianos Q8 positivos. **Não equiparar estabilização de Kt a prova de erro absoluto**; próximo gate é melhorar progressão radial e distribuição de tamanho/topologia externa, isolando o efeito da geometria. [Laboratório 16](../laboratorios/convergencia-fina-retangulo.md) e [dataset real](../dados/ciclo16-convergencia-fina-2026-11-08.json). Nenhuma aplicação industrial é autorizada.

## Ciclo 17 — Correção parcial da distorção Q8 por progressão escalonada

A [v0.17](../laboratorios/progressao-radial-q8.md) adicionou estratégia **alternativa e opt-in** `q(n)=exp(24ln(1,12)/n)`, mantendo `n24` bit-a-bit idêntico e preservando o padrão fixo histórico. Em [16 simulações Elmer/SciPy aprovadas](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42546868607), a maior razão de cordas da malha n48 caiu de 11,31→5,93 e 22,21→11,64 (d/W=.25) e de 12,07→6,30 e 23,00→12,00 (d/W=.125). **Quatro séries de Kt C escalonadas passaram o gate condicional de GCI** (0,0073–0,0442%), contra nenhuma com q fixo. **Limitação material:** a pior razão local junto ao furo em d/W=.125 L/W=4 subiu 4,57→8,07, e `σrr/T` residual aumentou em todas as chapas; ângulos mínimos globais ficaram inalterados (~12–13° em L/W=4). Próximo gate: **topologia e gradação local perto do furo**, sem promover a progressão escalonada a padrão. [Dados integrais](../dados/ciclo17-malha-radial-2026-11-08.json).

## Ciclo 18 — hipótese angular rejeitada por evidência (concluído como experimento)

A [v0.18](../laboratorios/distribuicao-angular-q8.md) registra duas tentativas de melhoria local. Spline na interface dos dois blocos: **jacobianos Q8 não positivos em L/W=4, ensaio interrompido antes do FEM**. Redistribuição angular moderada `qθ^Na=0,7`: **16 simulações externas Elmer/SciPy aprovadas**, mas todas as quatro geometrias n48 apresentaram pior razão de cordas da primeira faixa do furo (+~19%) e aumento de `σrr/T` na superfície livre; pior razão global e ângulos mínimos externos não melhoraram. Kt líquido C quase inalterado (<0,004%), reforçando que estabilidade de Kt não é prova de boa discretização local. [Dataset real](../dados/ciclo18-angular-2026-11-08.json); [workflow aprovado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42550543935). **Estratégia angular uniforme continua padrão.** Próximo gate: topologia multibloco com faixa anular de furo e transição externa, testando qualidade global, faixa crítica, tração livre e três recuperadores.

## Ciclo 19 — Faixa anular Q8 multibloco, resultado parcial e gates abertos

A [v0.19](../laboratorios/anel-multibloco-q8.md) criou 4 superfícies transfinite, 2 do anel `a≤r≤2a` e 2 do exterior, com verificação de **n_t arestas de interface compartilhadas por exatamente dois Q8** e mesmos nós médios. [16 novas simulações Elmer/SciPy](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42739742200) passaram; o número Q8 permaneceu 1152–4608 por malha. Com n48, a pior razão perto do furo caiu de **8,075→2,547** em d/W=.125,L/W=4; porém **a pior razão global piorou nas quatro chapas**, de 12,00→33,83 no mesmo caso, e a tensão radial residual livre também aumentou em **4/4** (cerca de 0,00102→0,00195 nesse caso). Os menores ângulos também pioraram. **GCI condicionado do recuperador C não invalida o fracasso nos gates físicos/geométricos.** Próximo gate: **mais blocos externos e melhor transição de tamanhos**, com auditoria de `σrr/T` e A/B/C. A [issue #19](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/19) permanece aberta. [Dataset](../dados/ciclo19-anel-multibloco-2026-11-09.json).

## Ciclo 20 — transição externa com seis blocos (experimental)

A topologia Q8 foi estendida por uma interface retangular intermediária entre o anel circular conforme e as faces da chapa, mantendo os mesmos quatro problemas físicos e níveis de refinamento do ciclo 19. O [laboratório 20](../laboratorios/transicao-externa-seis-blocos.md) descreve os controles e limites. Aceite condicionado a **16 malhas conformes, 16 simulações externas com evidências, comparação de qualidade local/global, tração superficial livre e CI verde**; sem promoção automática a padrão ou alegação de validação experimental. Registrar resultados negativos, caso ocorram.

**Resultado do ciclo 20:** [16 modelos externos executados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42780634538), [dataset](../dados/ciclo20-transicao-externa-2026-11-10.json). A transição de seis blocos diminuiu o pior alongamento global em 4/4 geometrias (−26,6% a −52,9%), mas degradou os ângulos mínimos em 4/4 e não reduziu a tração radial residual recuperada. A implementação experimental entra no acervo, **sem substituir a topologia padrão**. Próxima investigação: melhorar ângulos da transição externa e examinar tração livre ao longo do contorno.

## Ciclo 21 — interfaces e resíduos vetoriais no furo

A [varredura Gmsh de 28 geometrias](../laboratorios/interface-alinhada-tracao-parede.md) testa uma interface alinhada que conecta o anel 2a ao canto externo em 7 posições. O gate de melhoria simultânea de alongamento/ângulo **não passou** na varredura completa das quatro chapas; `λ=0,45` foi selecionada apenas como menor pior penalização, para investigação. Próximo gate: 16 FEM Elmer/SciPy + 4 controles reexecutados, leitura das duas componentes de tração em toda a parede, comparação de recuperação de Kt, ângulos, jacobianos e equilíbrio. Resultados positivos e negativos devem ser versionados. **Não transformar ganho de proxy em autorização de projeto ou mudança do default.**

**Resultado externo do ciclo 21:** [28 CADs e 20 FEM auditados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42856063314), com [dataset JSON completo](../dados/ciclo21-interface-tracao-2026-11-10.json). A versão alinhada melhorou ângulo mínimo em quatro geometrias (+14,9% a +55,6%), mas piorou alongamento global (+8,0% a +47,4%); a auditoria nova de tração vetorial na parede inteira não revelou ganho material. A variante alinhada permanece opt-in; o default dois-blocos fica preservado. Próximo gate: melhorar ângulo e alongamento em conjunto e confrontar `σn` com a normal isoparamétrica exata, não transformar RMS forte em índice de segurança.
