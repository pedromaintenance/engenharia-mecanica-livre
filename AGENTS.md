# AGENTS.md — Engenharia Mecânica Livre

Este arquivo é o **contrato permanente** de qualquer agente atuando neste repositório. Consulte também `docs/roadmaps/master.md`, `docs/governanca/curadoria.md`, `docs/governanca/agentes.md` e `docs/ciclos/`.

## Missão

Construir um acervo aberto de **Engenharia Mecânica** em português, rigoroso, útil para estudo, projeto e análise de manutenção. Priorize **evidência material, precisão científica, SI, segurança, licenças, reprodutibilidade e utilidade prática**.

## Regras operacionais

1. **Nunca inventar** fonte, DOI, norma, número de peça, pressão, torque, especificação OEM, resultados de testes ou status de publicação.
2. **Contextualizar o modelo físico:** entradas e saídas em SI, hipóteses, limites, unidades, sinais, equações, verificações e revisão.
3. **Separar categorias:** observação, hipótese, mecanismo, causa imediata, causa raiz e efeito operacional. Diagnóstico não é conclusão sem teste.
4. **Direitos autorais:** acesso aberto não implica permissão para copiar. L0 metadados/link por padrão; L1/L2 somente com direito demonstrado por item.
5. **Segurança:** conteúdo educativo não substitui manual OEM, procedimento local, habilitação, norma atualizada e controles de risco; não recomendar bypass de segurança.
6. **Privacidade:** nunca publicar SAP, dados internos de empregador, equipamentos identificáveis ou informações pessoais sem permissão. Usar dados sintéticos em exemplos.
7. **Arquitetura:** manter `catalogos/*.json`, `docs/`, `src/engmec/`, `tests/` e `.github/` coerentes. Evitar dependência pesada obrigatória.
8. **Qualidade:** executar `engmec validar`, `python -m unittest discover -s tests -v` e `mkdocs build --strict`. CI verde antes de afirmar entrega.
9. **Sem autonomia fictícia:** perfis de agentes/skills são instruções reutilizáveis; não implicam processos agendados ou acesso automático à internet.
10. **Handover:** ao terminar, registrar artefatos, origem das informações, evidências, limitações, falhas e próxima tarefa.

## Fluxo padrão

**Issue → Pesquisa → Curadoria jurídica → Conteúdo/código → Testes → Auditoria independente → PR/commit → CI/Pages → Registro de ciclo.**

## Convenções

Idioma português do Brasil para texto original, nomenclatura de grandezas com notação técnica correta, IDs permanentes em kebab-case, JSON UTF-8 com schema; datas ISO `YYYY-MM-DD`. Não alterar norma ou parâmetro OEM a partir de analogia.

## Como chamar especialistas

Arquivos em `.github/agents/*.agent.md`; skills em `.github/skills/*/SKILL.md`. Use a skill apropriada para a tarefa, mas valide a saída com `verificar-modelo` e curadoria quando aplicável. As ferramentas específicas só podem ser usadas se estiverem disponíveis no ambiente executor.
