# Engenharia Mecânica Livre

Uma base pública para **estudar, pesquisar, calcular, experimentar e resolver problemas mecânicos** sem abandonar o rigor científico.

O projeto está na fase **v0.9**. O portal está publicado, a primeira coleção de cursos/portais/software foi catalogada e os modelos de cálculo didáticos estão submetidos a testes automáticos. A plataforma está em desenvolvimento: referências identificadas não equivalem a obras integralmente analisadas.

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
