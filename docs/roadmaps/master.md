# Roadmap mestre de longo prazo

## Missão

Construir uma base pública, pesquisável e tecnicamente verificável de Engenharia Mecânica em português, relacionando fundamentos, literatura, cursos externos, experimentos, softwares, simulação, diagnóstico e aplicação. A métrica de êxito não é volume bruto de arquivos, mas **cobertura, rastreabilidade, rigor e reprodutibilidade**.

## Ondas de entrega e gates

| Onda | Horizonte indicativo* | Resultado | Critério de passagem |
| --- | --- | --- | --- |
| F0 — Fundação | concluído 2026-11-05 | site, código base, CI, 4 calculadoras e 20 fontes | site publicado, CI verde |
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
