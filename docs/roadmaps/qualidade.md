# Roadmap de qualidade, revisão e risco

## Três gates independentes

**G1 — Direitos:** URL canônica, titular, status de acesso, confirmação de licença por item, autorização de republicação quando houver conteúdo alheio. Sem aprovação, apenas link e metadados.

**G2 — Engenharia:** símbolos, SI, modelo, hipóteses, domínio de validade, solução de referência, análise de incerteza e teste de extrapolação. Em falhas: diferenciar sintoma, efeito, mecanismo e causa.

**G3 — Produto:** CI, links relevantes, busca, mobile, contraste, integridade de JSON, versionamento e changelog.

## Classes de conteúdo

- **Referência:** portal ou obra catalogada, sem avaliação integral de precisão.
- **Conteúdo original em revisão:** texto autoral incompleto/testes ausentes.
- **Conteúdo revisado:** fonte, equações e aplicações verificadas.
- **Ferramenta testada:** cobertura de referência e limites; sem certificação industrial.
- **Conteúdo depreciado/suspenso:** mudança de edição, falha ou restrição jurídica.

## Indicadores

Taxa de fonte revisada, aderência ao schema, falhas de CI, regressões numéricas, pendências de direitos, links inválidos, velocidade de revisão e incidentes de segurança/privacidade.

## Escalonamento

Quando houver falha de segurança, dado de cliente, copyright ou valor de referência incorreto: retirar/suspender o item, registrar issue, elaborar análise causal e só publicar novo conteúdo com evidência de correção.

**Não há aprovação automática de projeto de engenharia** por um agente ou calculadora.
