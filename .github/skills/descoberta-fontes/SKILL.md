---
name: descoberta-fontes
description: "Identificar fontes oficiais, cursos e portais de Engenharia Mecânica e registrar metadados sem copiar material protegido."
license: MIT
---

# descoberta-fontes

## Quando usar
Nova área, nova fonte, atualização de link, expansão do catálogo ou busca de curso institucional.

## Entradas
Área técnica, idioma, nível, instituição preferida, tipo de obra e recorte temporal.

## Procedimento
1. Priorizar portais institucionais, publicadores, órgãos oficiais e obras com DOI.
2. Diferenciar portal, coleção, obra, curso, edição, vídeo e ferramenta. Nunca registrar um portal como se fosse um curso verificado.
3. Consultar URL oficial; confirmar título, autor/instrutor, edição, idioma, nível e finalidade.
4. Pesquisar duplicatas por URL canônica, DOI/ISBN e título normalizado.
5. Classificar estado da evidência: `candidato`, `página-identificada`, `obra-auditada`, `suspenso`.
6. Gerar ficha de metadados e resumo autoral curto; passar à skill `curadoria-licencas` antes de qualquer cópia.
7. Registrar data e limitações; não alegar coleta exaustiva.

## Saída
Registro JSON, URL, evidência de identidade, fonte primária e pendências explicitadas.

## Aceite
Registro único, URL canônica, idioma, área, data e licença em revisão.
