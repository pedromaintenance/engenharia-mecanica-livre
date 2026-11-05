# Política de curadoria científica e jurídica

## Unidade de catalogação

**Portal ≠ curso ≠ obra ≠ aula ≠ versão.** IDs distintos para instituições, cursos, documentos, softwares e releases. Metadados de portal nunca autorizam automaticamente republicação de todo o conteúdo.

## Pipeline e estados

```text
Candidato -> Encontrado -> Identidade verificada -> Direitos revisados
          -> Analisado tecnicamente -> Publicado -> Revalidado/Retirado
```

Cada transição requer evidência documentada. **Verificar identidade** significa confirmar título/autoria e URL institucional; não equivale a revisão do conteúdo integral ou dos direitos.

## Campos obrigatórios para obra

ID estável, título original, autores, instituição, URL canônica, DOI/ISBN quando existente, idioma, edição/versão, tipo, domínio, área, acesso, direito de redistribuição, fonte dessa informação, data de consulta, estado de revisão, nota de escopo e link alternativo quando obsoleto.

## Três níveis de armazenamento

- **L0 — somente referência:** URL, título, autor, tema e resumo autoral. Padrão de qualquer origem.
- **L1 — metadados e trechos estritamente autorizados:** incluir apenas dentro dos direitos comprovados.
- **L2 — conteúdo integral:** somente quando licença e condições permitirem, com atribuição, versão, licença e registro de origem.

Para artigos com copyright, usar metadados e texto autoral independente; não mascarar cópia como resumo. Material privado e manuais de fabricantes não são fontes de republicação automática.

## Critérios de qualidade

Hierarquia contextual de evidência: aplicação OEM adequada ao número de série e revisão; requisitos legais/normativos vigentes; dados calibrados e validáveis; literatura acadêmica; referências didáticas; explicações secundárias. Não transferir parâmetros entre modelos de máquinas sem justificativa.

Toda fórmula deve ter símbolo, unidade, hipótese, domínio de validade, caso de teste e referência. Em análise de falhas, separar observação de inferência e causa confirmada.

## Riscos de indexação automática

APIs têm quotas e termos. Crossref recomenda User-Agent identificado e cache. OpenAlex tem limites e restrições de paginação; NTRS diferencia citações de documentos. Evitar descarga em massa, contornar login/paywall, ignorar robots.txt e ingerir conteúdos sem licença.

## Auditoria e retirada

Uma denúncia de licença gera suspensão do conteúdo e revisão, sem apagar o histórico decisório. Links quebrados são marcados, não substituídos por URL adivinhada. Cadência proposta: metadados voláteis trimestral, normativos por revisão oficial, software por release; publicação técnica por alteração substancial.
