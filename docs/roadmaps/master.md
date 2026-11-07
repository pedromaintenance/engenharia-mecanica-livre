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
