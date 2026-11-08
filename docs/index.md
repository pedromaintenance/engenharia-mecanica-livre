# Engenharia Mecânica Livre

Uma base pública para **estudar, pesquisar, calcular, experimentar e resolver problemas mecânicos** sem abandonar o rigor científico.

O projeto está na fase **v0.13**. O portal está publicado, a primeira coleção de cursos/portais/software foi catalogada e os modelos de cálculo didáticos estão submetidos a testes automáticos. A plataforma está em desenvolvimento: referências identificadas não equivalem a obras integralmente analisadas.

## Comece por aqui

| Objetivo | Onde entrar |
| --- | --- |
| Estudar a formação completa | [Grade aberta](formacao/grade.md) |
| Aprender para manutenção, projeto, confiabilidade ou dados | [Seis trilhas](formacao/trilhas.md) |
| Encontrar disciplina universitária | [10 cursos identificados](catalogos/cursos.md) |
| Pesquisar em universidades, bibliotecas e órgãos | [20 portais](catalogos/portais.md) |
| Encontrar CAD/CAE, FEM/CFD e bibliotecas de cálculo | [17 ferramentas](catalogos/ferramentas.md) |
| Descobrir novas referências em bases científicas | [Cliente de metadados Crossref/OpenAlex](governanca/descoberta.md) |
| Aplicar fórmulas e interpretar limitações | [Guia de calculadoras](guia-calculadoras.md) |
| Comparar FEM com equações analíticas | [Barra axial e convergência de malha](laboratorios/benchmark-barra-fem.md) |
| Comparar com software FEM externo | [Benchmark CalculiX C3D8](laboratorios/calculix-3d.md) |
| Estudar flexão pura, erro de malha e travamento C3D8 | [Laboratório 07](laboratorios/flexao-pura-3d.md) |
| Comparar elementos lineares e quadráticos | [Laboratório 08 — C3D8 × C3D20R](laboratorios/comparar-elementos-fem.md) |
| Estudar concentração de tensões em furo circular | [Laboratório 09 — Kirsch](laboratorios/kirsch-furo.md) |
| Estudar chapa finita efetivamente tracionada | [Laboratório 10 — chapa com furo](laboratorios/chapa-finita-furo.md) |
| Comparar malhas independentes e refinar largura | [Laboratório 11 — Gmsh × autoral](laboratorios/gmsh-chapa.md) |
| Conferir outra implementação do solver FEM e tensão de borda | [Laboratório 12 — Dois solvers Q8](laboratorios/dois-solvers-q8.md) |
| Confrontar solver externo Elmer com FEM Q8 autoral | [Laboratório 13 — Elmer FEM](laboratorios/elmer-fem-independente.md) |
| Consultar restrições por obra | [Auditoria documental de direitos](governanca/auditoria-obras.md) |
| Estruturar investigação de falha | [Diagnóstico de manutenção](manutencao/diagnostico.md) |
| Continuar o projeto em novos ciclos | [Roadmap mestre](roadmaps/master.md) e [agentes](governanca/agentes.md) |

## O que ensinamos

Partimos das leis físicas, construímos modelos matemáticos, analisamos fenômenos e traduzimos os resultados em decisões verificáveis. A estrutura progride por matemática e física, sólidos e dinâmica, materiais e fabricação, termofluidos, projeto de máquinas, simulação e manutenção.

## Origem e confiabilidade

- As páginas de cursos e softwares apontam para as instituições, não simulam parcerias ou certificados.
- Cada conteúdo autoral exige referências, unidades, hipóteses, exemplos e verificação.
- O site não fornece autorização de operação, liberação, soldagem, reparo ou mudança de configuração de máquinas.
- O catálogo é expandido progressivamente: **67 registros de tipos distintos até esta fase**, com grande parte ainda aguardando auditoria item a item.

## Como colaborar

Siga [metodologia científica](metodologia.md), [curadoria de direitos](governanca/curadoria.md), [roadmap](roadmaps/master.md) e [CONTRIBUTING.md](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/CONTRIBUTING.md).

## Experimento quantitativo validado no ciclo 07

O [benchmark 3D de flexão pura](laboratorios/flexao-pura-3d.md) comparou dados reais do CalculiX com uma solução da elasticidade: quatro malhas e redução do erro do deslocamento de 29,75% para 0,99%. O resultado confirma convergência numérica desse modelo idealizado, não valida um equipamento real. [Dados auditáveis](dados/flexao-pura-3d-2026-11-05.json).

## Elementos finitos de alta ordem — ciclo 08

O [comparativo C3D8 versus C3D20R](laboratorios/comparar-elementos-fem.md) foi executado em seis malhas no CalculiX, comparando os deslocamentos e tensões de Gauss do solver com uma referência da elasticidade. A solução quadrática apresentou precisão muito superior nesse caso de flexão pura, com maior número de graus de liberdade. [Dados estruturados permanentes](dados/comparacao-c3d8-c3d20r-2026-11-07.json).

## Kirsch: tensões perto do furo — ciclo 09

O [laboratório de Kirsch](laboratorios/kirsch-furo.md) mediu a distribuição de tensões ao redor de um furo em malha curva CPS8R com contorno externo prescrito analiticamente. O [benchmark externo](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42415560152) passou; o erro RMS tensorial ponderado por área diminuiu de 0,521% para 0,072%. O `Kt=3` é referência do problema ideal infinito e **não** parâmetro validado de olhais reais. [Dados numéricos e limitações](dados/kirsch-cps8r-2026-11-07.json).

## Chapa quadrada finita tracionada — ciclo 10

O [Laboratório 10](laboratorios/chapa-finita-furo.md) aplica tração nas bordas externas de uma chapa quadrada finita com furo, usando elementos CPS8R. O [CalculiX executou cinco casos](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42421310615); a estimativa `Kt` superficial vem de uma extrapolação declarada, não é tensão diretamente lida no bordo. A [base de resultados](dados/chapa-finita-furo-2026-11-07.json) distingue a referência bruta da líquida e não apresenta Kirsch infinito como solução exata da placa finita.

## Malha Gmsh independente — ciclo 11

A [comparação de geradores](laboratorios/gmsh-chapa.md) foi executada no [workflow externo aprovado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42422518394). O Gmsh construiu malha quadrática própria, importada e solucionada no CalculiX para a mesma chapa finita do laboratório 10. A maior divergência entre os três pares testados ficou abaixo de 0,58% em Kt bruto estimado, com as ressalvas de extrapolação. [Dataset auditável](dados/ciclo11-gmsh-chapa-2026-11-07.json).
