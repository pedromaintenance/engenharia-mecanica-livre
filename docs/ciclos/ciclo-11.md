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


## Evidências de execução e resultados reais

O [workflow de solver #42422518394](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42422518394) foi concluído com sucesso, usando Gmsh 4.12.1 e CalculiX CCX 2.21-1 no Ubuntu 24.04. **Nove execuções**: seis autorais (H/a 8 e 16 × n 16/24/32), três Gmsh (H/a 4 × n 16/24, H/a 8 × n 24). [CI final #42422586573](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42422586573): **92 testes** aprovados, `mkdocs build --strict` aprovado.

**Comparação externa:** Gmsh contra malha autoral, mesmo número de elementos e mesmo solver:
- H/a=4, n=16: Kt bruto 3,596799 vs 3,617689, diferença relativa −0,5775%.
- H/a=4, n=24: Kt bruto 3,614709 vs 3,617450, diferença relativa −0,0758%.
- H/a=8, n=24: Kt bruto 3,153882 vs 3,163999, diferença relativa −0,3198%.

**Refinamento de largura:** H/a=8 n=16/24/32: 3,156600 → 3,163999 → 3,164491. H/a=16: 3,013888 → 3,053753 → 3,059526. Alteração relativa final n24→n32: **0,0155%** e **0,1887%** respectivamente, ainda sem prova de convergência assintótica.

**Postmortem:** primeira execução falhou porque os marcadores `$MeshFormat` no parser tinham barra invertida literal introduzida na geração do código. Substituídos por marcadores reais de seção MSH2, com teste de regressão, e workflow posterior aprovado.

**Auditoria:** [JSON permanente](../dados/ciclo11-gmsh-chapa-2026-11-07.json), [artefato do workflow](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42422518394/artifacts/13594415077), com `.geo`, `.msh`, `.inp`, `.dat`, `.frd`, logs Gmsh/CCX e comparações. SHA256 do arquivo ZIP do artefato: `4f3b99cd9de775682d05259d25acf44f76d824324d143e87789f7fc40d14a4f0`.

**Conclusão:** evolução de verificação geométrica e de refinamento **com o mesmo solver**, não validação por dois programas FEM independentes. Sem aprovação para projeto de máquinas reais. A issue #13 permanece aberta para evidência externa de integridade e incerteza superficial.
