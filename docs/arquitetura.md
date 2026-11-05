# Arquitetura técnica

## Camadas

```text
Fontes primárias, OER, artigos, dados, software, normas (links)
        |
        v
Descoberta -> revisão jurídica -> revisão técnica -> deduplicação
        |
        v
Catálogo versionado JSON + fichas originais em Markdown
        |
        +--> busca lexical (CLI e MkDocs)
        +--> glossário, relações entre temas e trilhas
        +--> biblioteca Python de cálculo e testes
        +--> casos de diagnóstico e modelos de planejamento
        |
        v
GitHub -> Actions (validação e publicação) -> GitHub Pages
```

## Decisões de arquitetura

- **Git como fonte de verdade.** Conteúdo textual e metadados revisados em PR, com histórico de edições.
- **Dados legíveis por máquinas.** JSON e schema; IDs estáveis, data de verificação, link canônico e política de licença explícitos.
- **Conteúdo autoral separado de terceiros.** Não indexar textos completos de origem restrita nem disponibilizar corpora privados à IA.
- **Camada de aplicações desacoplada.** CLI Python sem dependências obrigatórias; MkDocs para leitura; extensões futuras para API, busca semântica e banco de dados.
- **Software instalado por dependência, não incorporado.** FreeCAD, OpenFOAM, CalculiX e CoolProp continuam projetos independentes sob respectivas licenças.
- **Versionamento do conteúdo técnico.** Fórmulas acompanhadas de hipóteses, versão de norma/fabricante, caso de teste e data de revisão.
- **Observabilidade de qualidade.** CI testa o catálogo e os cálculos; futura auditoria de links sem sobrecarregar servidores.

## Pipeline proposto de expansão

Descobrir por índices autorizados (OAI-PMH, APIs públicas, sitemaps, catálogos institucionais) -> normalizar DOI/URL/ISBN -> atribuir ID e domínio -> revisar licença individual -> incorporar **metadados** -> produzir síntese autoral com fontes -> revisão técnica por pares -> publicação.

Não implementar scraping indiscriminado: respeitar robots.txt, termos, limites e direitos; não inferir permissão de redistribuição de uma URL aberta.

## Estrutura

```text
src/engmec/         # biblioteca de cálculo, catálogo e interface CLI
src/engmec/data/    # fontes JSON canônicas
schemas/            # contratos de dados
docs/               # base de conhecimento editorial
templates/          # padrão de ficha técnica
tests/              # regressão e consistência
.github/workflows/  # CI e publicação opcional
```

## Futuro

Fase 2: enriquecimento com DOI, ORCID, termos, idiomas e histórico de disponibilidade; busca por domínio/nível; grafo de conceitos. Fase 3: notebooks reproduzíveis, FreeCAD parametrizado, benchmarks FEM/CFD, simulações de confiabilidade e portal interativo. Fase 4: conectores de dados públicos, RAG com evidência de trecho e bloqueio de material não licenciado.
