# Ciclo 11 — Malha Gmsh independente e sensibilidade de Kt à largura

**Data:** 07/11/2026. **Versão:** v0.11.0. **Issue-mãe:** [#13](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/13).

## Problema herdado

A v0.10 passou na execução real de cinco chapas finitas, mas só H/a=4 possuía estudo de refinamento. H/a=8 e 16 tinham uma malha cada, e somente o gerador geométrico autoral havia sido utilizado. A estimativa de Kt bruto por extrapolação se aproximava de Kirsch com o aumento da largura, mas era necessário isolar o efeito do refinamento e usar **outra implementação de geometria**.

## Novas entregas

1. \`src/engmec/gmsh_chapa.py\`: gerador de geometria \`.geo\` de duas superfícies CAD, interface para \`gmsh\` CLI, leitura de \`.msh\` v2 ASCII de quad8 (tipo 16) e arestas quadráticas (tipo 8), validação geométrica e física, montagem do deck CPS8R para CalculiX e pós-processamento de tensões a partir das coordenadas de Gauss.
2. \`tests/test_gmsh_chapa.py\`: valida conteúdo da geometria, opções de elemento Q8, entradas inválidas e falha explícita quando o executável do Gmsh não está presente.
3. \`scripts/avaliar_ciclo11.py\`: dados estruturados de largura, malha, Kt bruto/líquido e diferença entre Gmsh e gerador nativo, confrontando o baseline permanente do ciclo 10.
4. \`tests/test_aval_ciclo11.py\`: não aprovar ausência de dados reais.
5. \`.github/workflows/ciclo11-gmsh.yml\`: instalação dos executáveis de Gmsh e CalculiX, testes, nove execuções externas, consolidação e arquivamento dos dados brutos.
6. \`docs/laboratorios/gmsh-chapa.md\`: explicação matemática/física, comparações e instruções para reprodução.

## Critérios de aceitação

- Gmsh precisa realmente gerar .msh com **somente CPS8R equivalentes** e elementos corretos, positivos.
- A chapa efetivamente recebe tração na borda; carregamento da borda do quarto igual a \`T·H·t\`; demais bordas permanecem livres/simetria.
- Dado de tensão superficial é **estimativa de extrapolação** com desvio controlado no campo analítico, não tensão direta no furo.
- Mesmas grandezas de Kt nominal bruto/líquido e mesmo solver são usados para comparar malhas de fontes diferentes.
- A série H/a=8 e 16 deve ter n=16/24/32 com variação documentada, sem afirmar automaticamente convergência.
- A automação deve aprovar CI, solver externo e publicação estrita; falhas precisam ser relatadas com causa e correção, não omitidas.

## Limite

Comparação entre geradores Gmsh e código autoral não constitui verificação de código independente do **solver**. A assimetria entre distribuições de elementos não deve ser ocultada. A issue #13 só será fechada se as demais pendências de referência física, contorno e incerteza estiverem sustentadas; caso contrário, registrar avanço parcial com handover técnico.
