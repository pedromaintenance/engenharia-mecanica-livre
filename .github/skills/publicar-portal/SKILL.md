---
name: publicar-portal
description: "Publicar e verificar conteúdo MkDocs/GitHub Pages com critérios de qualidade e acessibilidade."
license: MIT
---

# publicar-portal

## Quando usar
Alterações em `docs/`, `mkdocs.yml`, workflows, catálogos e navegação.

## Procedimento
1. Atualizar conteúdo Markdown e navegação MkDocs ao mesmo tempo.
2. Executar testes, `mkdocs build --strict` e verificar links e caminhos locais.
3. Confirmar que publicação no GitHub Pages está habilitada via GitHub Actions.
4. Verificar workflow `Publicar documentação` **concluído com sucesso**, não apenas iniciado.
5. Abrir o site, verificar menu, busca, mobile, título e páginas de catálogo, quando possível.
6. Registrar hash de commit, workflow de CI e URL pública; reportar bloqueios reais.

## Saída
Página publicada com evidência e rastreabilidade.

## Aceite
Build verde, deploy verde e navegação validada.
