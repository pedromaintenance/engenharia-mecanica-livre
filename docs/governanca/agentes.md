# Arquitetura de agentes e skills

Os agentes são **contratos de atuação** versionados, não serviços autônomos permanentemente executados. Precisam ser invocados por uma pessoa ou por um ambiente de execução que suporte perfis personalizados.

## Organização do time

| Perfil | Responsabilidade | Não pode fazer |
| --- | --- | --- |
| Orquestrador | selecionar backlog, decompor escopo, compor entregas e reportar | aprovar ciência/segurança sozinho |
| Pesquisador | localizar fontes primárias e captar metadados | copiar corpo de obra sem direito |
| Curador jurídico | verificar licença, atribuição e acesso | presumir que acesso livre = CC |
| Arquiteto educacional | grade, resultados de aprendizagem, pré-requisitos, exercícios | inventar certificação universitária |
| Especialista mecânico | explicar modelos, hipóteses, mecanismos de falha | tratar hipótese como causa confirmada |
| Engenheiro computacional | bibliotecas, exemplos, CI, benchmarks e números | atribuir cálculo a norma não verificada |
| Auditor de evidências | avaliar fontes, cálculo, citação e limitações | aprovar conteúdo sem teste |
| Editor do portal | navegação, busca, acessibilidade e publicação | publicar sem QA/curadoria |

Os arquivos em [`.github/agents/`](https://github.com/pedromaintenance/engenharia-mecanica-livre/tree/main/.github/agents) definem especialidades reconhecidas pelos ambientes GitHub Copilot compatíveis. [`AGENTS.md`](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/AGENTS.md) guarda regras universais. As skills em [`.github/skills/`](https://github.com/pedromaintenance/engenharia-mecanica-livre/tree/main/.github/skills) explicam procedimentos reutilizáveis.

## Ciclo de entrega

**Intake → triagem → fonte → direitos → engenharia → testes → revisão → publicação → handover.**

Para cada ciclo, produzir: (a) issue com resultado esperado; (b) lista de URLs e licenças; (c) novos arquivos e conteúdo revisado; (d) testes/evidências; (e) decisão de pendências; (f) registro de entrega em `docs/ciclos/`.

## Regras de colaboração

- Pesquisa e licença são tarefas distintas; pode-se pesquisar sem possuir direito para reproduzir.
- Autor do conteúdo não deve ser o único revisor técnico do mesmo conteúdo.
- Toda atividade com potencial de segurança operacional exige revisão humana responsável antes de aplicação.
- PRs pequenos e reversíveis são preferíveis a grandes commits sem QA.
- Falha em CI impede aceite; não contornar teste para aprovar.
- Não executar ações em contas externas sem autorização e trilha de auditoria.

## Como usar

1. Ler `AGENTS.md` e `docs/roadmaps/master.md`.
2. Escolher um issue e um agente especialista, carregar a skill correspondente.
3. Produzir arquivo/commit acompanhado de evidências.
4. Rodar testes e obter revisão; registrar no ciclo.
5. Só então declarar entrega concluída.

Documentação GitHub: [custom agents](https://docs.github.com/en/copilot/concepts/customizations/custom-agents), [agent skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills).
