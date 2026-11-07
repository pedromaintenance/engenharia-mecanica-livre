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


## Resultados e aceite reais — fechamento técnico do ciclo 09

Execução [CalculiX #42415560152](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42415560152), `calculix-ccx 2.21-1` em Ubuntu 24.04. Foram executados **4 casos**: malhas CPS8R 4×8, 8×16 e 16×32 com R/a=8 e mais uma malha 16×32 com R/a=4. O [CI geral com 76 testes](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42415560148) também passou.

| Elementos | Erro global ponderado | RMS faixa física a–1,5a | Proxy interno |
| ---: | ---: | ---: | ---: |
| 32 | 0,5208% | 2,4393% | 2,4944 |
| 128 | 0,1170% | 0,7655% | 2,8652 |
| 512 | 0,0723% | 0,4481% | 2,9848 |

**Advertência obrigatória:** o erro da primeira camada radial, de extensão variável, caiu de 2,4393% para 1,0745% e depois aumentou para 1,5934%. Isso não invalida automaticamente o comportamento das métricas globais e do anel físico fixo, mas impede caracterizar todas as medidas locais como monotonicamente convergentes. Taxa aparente do erro global ponderado: ~2,154 no primeiro refinamento e ~0,695 no segundo. A região das medidas deve ser informada sempre.

Caso R/a=4, nr=16: erro global ponderado 0,1496%, faixa física 0,4912% e proxy 3,0093 — **não** é resultado de uma chapa finita sob tração uniforme em borda.

### Pós-morte das falhas

- CCX rejeitou linhas `*NSET` com mais de 16 entradas. Corrigido e testado.
- CCX rejeitou formato de `*BOUNDARY` com números excessivamente longos. Agora nove algarismos significativos, com teste.
- Elementos junto ao eixo x=0 receberam mensagens `nonpositive jacobian` após expandir os CPS8R em elementos sólidos; a origem foi uma coordenada praticamente zero (~1e-18) em vez de zero exato. Após normalização dos eixos, a malha foi aceita pelo solver. Sem eliminar os testes do jacobiano 2D.
- A média do erro por ponto de Gauss super-representava elementos pequenos da malha graduada; agora o workflow também avalia ponderação por área e um anel físico fixo, mantendo alerta da primeira camada.

**Evidências:** [dataset versionado](../dados/kirsch-cps8r-2026-11-07.json); [laboratório](../laboratorios/kirsch-furo.md); [artefato completo do workflow](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42415560152/artifacts/13590939560), ID 13590939560, SHA-256 `7a9c1c45f216ef219a90bd7d2f158912c485db815eb8e9a0e50e5fc94f6a3e07`, retenção até 07/12/2026.

**Status:** ciclo 09 entregue para *verificação de Kirsch em domínio anular com contorno analítico*. Issue #13 deve permanecer **aberta** quanto à chapa retangular finita fisicamente tracionada, efeito das bordas, estimativa superficial de Kt e integração Gmsh opcional.
