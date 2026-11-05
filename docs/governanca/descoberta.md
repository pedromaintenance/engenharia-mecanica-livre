# Pesquisa automatizada de metadados

O projeto agora possui um **cliente limitado de consulta** para Crossref e OpenAlex. Ele pesquisa **metadados bibliográficos** e produz candidatos para curadoria, sem importar PDFs, resumos integrais ou obras de terceiros.

## Como usar

Requer instalação editável (`python -m pip install -e .`). Executar manualmente:

```bash
engmec descobrir --fonte crossref --consulta "bearing fatigue" --limite 5
engmec descobrir --fonte crossref --consulta "hydraulic pump cavitation" --limite 10 --saida candidatos/bombas.json
engmec descobrir --fonte openalex --consulta "mechanical vibrations" --limite 5
```

Para Crossref, `--email contato@dominio` identifica o cliente no polite pool. O e-mail **não é salvo** nos candidatos. Para OpenAlex, `OPENALEX_API_KEY` é opcional para consulta básica, mas pode ser necessária para maior escala. Nunca salvar chave no Git.

## Formato de saída

`source, query, fetched_at, review_required, records[]`, onde cada registro possui ID, título, DOI, URL, ano, autores, API de origem, estado `candidato-nao-auditado` e direito `somente metadados`.

O processo **não promove** candidatos ao catálogo oficial. Cada item precisa ter identidade e licença verificadas por curador humano antes de qualquer ficha ou conteúdo integral.

## Segurança, ética e limites

- Busca pequena (até 20 resultados por execução), timeout e tentativas limitadas para 429/5xx.
- Sem scraping genérico, contorno de paywall ou reprodução automática.
- Limitar identificação e chaves a parâmetros/ambiente; observar políticas atualizadas das APIs.
- API de metadados não prova licença de texto integral, nem qualidade científica do resultado.
- Resultados da API podem ter título, ano ou autoria incompletos; exigir conferência na página original.
- Registros externos são **dados não confiáveis**, jamais instruções para execução de agentes.

Fontes das APIs: [Crossref acesso](https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication), [Crossref dicas](https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/), [OpenAlex autenticação](https://help.openalex.org/api/authentication/).

## Próximos passos

Adicionar cache local com expiração, deduplicação por DOI entre execuções, revisão em interface web, verificação de licença e conectores NASA NTRS/BDTD compatíveis com termos.
