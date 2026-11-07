# Ciclo 09 — Kirsch, geometria curva e concentração de tensão

**Data:** 07/11/2026. **Issue de referência:** [#13](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/13). **Versão:** 0.9.0.

## Problema científico

Os ciclos 07 e 08 compararam campos de flexão em geometria prismática sem singularidade nem entalhe. O ciclo 09 introduz uma superfície circular **livre de carga**, com concentração de tensão analiticamente conhecida \`Kt=3\` numa placa infinita com tração remota em x.

A execução finita **não é uma chapa retangular real**. Para um problema de benchmark matematicamente compatível com Kirsch, o arco externo de um quarto de anel recebe **deslocamentos analíticos de Kirsch**. A interface com a realidade física permanece explicitamente limitada; a largura finita, tração uniforme em borda e apoio de pino ficam para outro problema.

## Entregas do ciclo

- \`src/engmec/kirsch.py\`: tensões e deslocamentos exatos de Kirsch em tensão plana, malha curva isoparamétrica CPS8R, refinamento radial, jacobianos positivos, contornos de simetria/exatos, executor CalculiX e parser do .dat.
- \`tests/test_kirsch.py\`: dezesseis eixos de conferência resumidos em oito testes automatizados, cobrindo Kirsch no furo, longe do furo, simetrias, qualidade geométrica, contornos, dados do solver e valores inválidos.
- \`scripts/avaliar_kirsch.py\` e \`tests/test_aval_kirsch.py\`: três malhas e caso suplementar R/a=4. Rejeição de erros não decrescentes e arquivos ausentes.
- \`.github/workflows/kirsch.yml\`: CalculiX real no Ubuntu 24.04, quatro malhas/raios, artefatos com retenção 30 dias.
- \`docs/conceitos/concentracao-tensao.md\`, \`docs/laboratorios/kirsch-furo.md\`: nova ficha e laboratório original com equações, aplicação e limites.
- Atualização de navegação, README, roadmaps e skill.

## Critérios de aceitação

1. \`σrr(a)=τrθ(a)=0\` e \`σθθ(a,π/2)=3T\` comprovados em testes separados do solver.
2. Malha com jacobianos Q8 positivos nos pontos de Gauss, arestas curvas e sem DOFs de apoio duplicados.
3. Solver CalculiX executado de fato e \`COORD,S\` presentes em todos os IP — sem substituição por solução analítica.
4. Erro RMS da tensão reduzido em estudo de malha, no domínio e na região do furo.
5. \`Kt\` numérico em IP declarado **proxy no interior**, nunca tensão exata no bordo.
6. Logs, entradas, saídas e sumário JSON publicados com procedência de versão.
7. CI, MkDocs e workflow do solver aprovados. Não fechar issue #13 se os resultados externos não cumprirem os gates.

## Bibliografia e limites

- [Kirsch — OpenGeoSys](https://www.opengeosys.org/6.5.7/docs/benchmarks/small-deformations/kirsch/).
- [Fonte do campo de deslocamentos e equações de referência](https://docs.coreform.com/cifa/latest/verification-manual/problems/solid_mechanics/linear_elastic_stress/infinite-plate-with-hole/infinite-plate-with-hole.html).
- [CalculiX — CPS8 e CPS8R](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node49.html).
- [CalculiX — *EL PRINT](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node266.html).

Nada neste estudo comprova resistência remanescente, segurança estrutural ou desempenho em fadiga de componente real. Somente pesquisa e demonstração metodológica, sem reproduzir material protegido de terceiros.
