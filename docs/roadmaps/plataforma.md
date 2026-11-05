# Roadmap da plataforma de dados

## Arquitetura de referência

```text
Fontes oficiais -> Descoberta APIs/OAI-PMH -> Fila de candidatos
        -> Revisão de autoria, identidade e licença
        -> JSON validado + fichas Markdown
        -> Git/PR + CI -> MkDocs/GitHub Pages
        -> CLI/Apps/Estudos/Busca
```

## Evolução prevista

**P0 — Publicação:** GitHub Pages, CI, navegação, testes e site móvel.

**P1 — Contratos:** schemas JSON individuais, vocabulário controlado, auditoria de campos, geração automática de páginas a partir de catálogos, verificação contra duplicatas de IDs.

**P2 — Descoberta:** adaptadores Crossref, OpenAlex, NASA NTRS e OAI-PMH (metadados apenas), cache, backoff, idempotência, quotas, logs e opção dry-run. Chaves somente em variáveis/secret store; nunca no Git.

**P3 — Busca:** lexical + facetamento; vetor opcional apenas de textos com direitos claros, com fonte e passagem. Nunca armazenar documentos de acesso restrito em índice de terceiros sem permissão.

**P4 — API pública:** endpoints de catálogos, trilhas, fichas e cálculos didáticos, com versionamento semântico e limites de uso.

**P5 — Offline:** exportação estática de fichas autorais, catálogos e ferramentas leves; checksum e proveniência.

## Riscos técnicos

Links quebrados, mudanças de domínio, abuso de API, deduplicação imperfeita, dependências pesadas, builds quebrados, falta de revisão e contaminação por dados privados. Todos têm gatilhos para rollback e registro.

## Critérios do sistema

Build reproduzível em Python definido, nenhuma credencial em Git, teste automatizado, documentação de instalação, backup por Git e migração de esquema acompanhada de testes.
