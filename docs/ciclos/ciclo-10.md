# Ciclo 10 — Chapa finita: carregamento físico, Kt bruto/líquido e tensão de borda

**Data:** 07/11/2026. **Versão:** 0.10.0. **Issue:** [#13](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/13).

## Lacuna corrigida do ciclo 09

O laboratório Kirsch possuía um domínio anular finito, mas sua fronteira externa era restringida pelos **deslocamentos exatos do problema infinito**. Isso era adequado para **verificação numérica**, porém não reproduzia o comportamento de uma chapa finita sob carga física na borda.

## Entregas

- **Novo solver adapter:** \`src/engmec/chapa_finita.py\`, com malha isoparamétrica Q8 de um quarto de chapa quadrada e furo central, borda direita tracionada por \`*CLOAD\` equivalente, bordo superior e furo livres, simetrias prescritas.
- **Pós-processamento:** leitura integral \`*EL PRINT COORD,S\` dos pontos de Gauss; tensões circunferenciais, extrapolação local de pico no ponto \`r=a,θ=90°\` com resíduos, checagem sintética do mesmo estimador em Kirsch, fatores \`Kt_gross\` e \`Kt_net\`.
- **Testes:** geometria e jacobiano, tração equivalente, carga total física, simetrias sem super-restrição, denominadores bruto/líquido, solução sintética no extrapolador e rejeição de arquivos incompletos.
- **Workflow externo:** CalculiX Ubuntu 24.04 com cinco execuções (3 malhas H/a=4 e 2 larguras maiores), logs e resultados temporários.
- **Documentação:** [Laboratório 10](../laboratorios/chapa-finita-furo.md), roadmap e instruções de benchmark.

## Critérios para declarar avanço

1. Positividade dos jacobianos e geometria de contorno quadrado (sem elementos cruzando a quina).
2. Carregamento aplicado por forças nodais consistentes, \`F_quarto=T·H·t\`.
3. Condições de simetria físicas; lado oposto virtual com força equilibrada e bordas horizontais livres.
4. Solver **real** executado, com \`S\` e \`COORD\` de todos os pontos de Gauss.
5. Tensão superficial somente como **extrapolação explicitamente qualificada**, não medição direta.
6. Relatório de sensibilidade de malha e largura com limites, inclusive falta de convergência.
7. CI, MkDocs e GitHub Pages verdes; arquivar dataset rastreável.

## Fronteiras científicas

A relação de Kirsch \`Kt=3\` é para placa infinita e não é solução exata para a chapa quadrada finita; a comparação é **assintótica e contextual**. Fatores bruto e líquido dependem do denominador. Não há validação experimental nem constituição de critério de aceitação de olhal/estrutura. Integração Gmsh e benchmark contra outras formulações devem permanecer no backlog.

## Evidência e handover

A primeira publicação deste relatório não equivale a solver validado. Registrar links de workflow, commit, número de testes, dataset com origem e, se necessário, falhas e correções de processo ao final da execução. Se qualquer gate falhar, manter issue #13 aberta e expor a falha.
