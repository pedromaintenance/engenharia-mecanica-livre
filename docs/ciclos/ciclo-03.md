# Ciclo 03 — Descoberta controlada de metadados

**Data de implementação:** 2026-11-05. **Objetivo:** reduzir pesquisa manual repetida preservando critérios de licença e revisão humana.

## Implementação

Foi criado cliente leve para consultas individuais Crossref/OpenAlex, sem dependência Python adicional; consulta por tópico, deduplicação interna e geração opcional de JSON de candidatos. O limite padrão é cinco registros, máximo vinte. As respostas externas permanecem candidatas até curadoria.

## Segurança

O fluxo não baixa conteúdos de terceiros nem faz ingestão automática no catálogo. Chaves e e-mails são fornecidos localmente pelo operador e não são incorporados ao JSON de resultados.

## Verificação

Os testes com respostas locais fictícias demonstram normalização e verificação de parâmetros; eles **não demonstram execução bem-sucedida contra a API remota em produção**. Conferir CI após commit.

## Pendências

Cache, rotinas incrementais, licenças por obra, deduplicação interlotes, verificação de disponibilidade do original e integração com fila de revisão.

**Concluído:** [commit f565f264](https://github.com/pedromaintenance/engenharia-mecanica-livre/commit/f565f264e714996264e0f68e518e938e2c5a75d4) com [21 testes aprovados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42047785634) e [Pages publicado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42047785564). Testes são locais simulados; nenhuma consulta remota live certificada.
