# Ciclo 14 — Sensibilidade de Kt à recuperação de tensão superficial

**Data:** 08/11/2026. **Versão alvo:** 0.14.0. **Issue:** [#15](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/15).

## Escopo

Após a equivalência dos deslocamentos Elmer e FEM SciPy no ciclo 13, separar **erro de solução** de **erro de pós-processamento**. **Não trocar os deslocamentos entre métodos:** aplicar gradiente direto (A), ajuste polinomial de seis coeficientes a partir dos Gauss 3×3 (B) e ajuste de patch ponderado em quatro coeficientes (C) sobre **um único campo nodal Elmer**.

A tensão máxima obtida por cada operador é **estimativa de contorno**, não tensão experimental. Os métodos B/C usam três camadas radiais e três células angulares, e suas combinações de base e pesos ficam preservadas no código/documentação.

## Entregas de software

- \`src/engmec/recuperar_tensao.py\`: operadores A/B/C, tensões polares, controles analíticos de Kirsch, qualidade geométrica, condicionamento e exportação de dados de Gauss.
- \`src/engmec/elmer_chapa.py\`: preserva e exporta \`deslocamentos_elmer.json\`, \`gauss_tensoes.csv\` e \`recuperacao.json\` para a **mesma execução real do Elmer**, sem produzir respostas de outro solver como substituto.
- \`tests/test_recuperar_tensao.py\`, \`tests/test_aval_ciclo14.py\`: teste de campos afins, validação de polinômios de diferentes bases, resultados sintéticos, dados incompletos e CSV.
- \`scripts/avaliar_ciclo14.py\`: resume seis casos de H/a=4 e 8, três malhas por largura, com os três recuperadores, amplitudes e desvio de superfície livre.
- \`.github/workflows/ciclo14-recuperacao.yml\`: instala dependências e executa seis casos Elmer FEM com exportação dos dados e artefatos de auditoria.
- [Laboratório 14](../laboratorios/recuperacao-tensoes-furo.md): formulação, referência de literatura técnica, limitações de SPR e procedimento reproduzível.

## Critérios de aceitação

1. O ElmerSolver precisa terminar e gerar seus campos nodais; nenhuma tabela de Kt sem solver externo real.
2. Os três operadores devem receber o **mesmo arquivo de deslocamentos**, a mesma malha e tensão nominal \`T=10 MPa\`.
3. Todos os elementos Q8 devem ter jacobianos positivos; Gauss 3×3 e amostra local devem estar íntegros.
4. Verificar controle analítico em Kirsch **sem declarar Kt=3 como resposta exata da chapa finita**.
5. Comparar as tendências de Kt em três malhas de W=80 e 160 mm e registrar variação entre operadores, mesmo que não monotônica.
6. Exportar CSV de Gauss, deslocamentos, \`.msh\`, \`.sif\`, \`.vtu\`, logs, versões e dataset JSON versionado.
7. Distinguir **amplitude determinística** entre três métodos de uma incerteza estatística/expandida não determinada e de limite de resistência industrial.

## Pesquisa de comparação

- [Zienkiewicz e Zhu, 1992 — recuperação por patches](https://doi.org/10.1002/nme.1620330702).
- [Zienkiewicz e Zhu, 1992 — estimadores *a posteriori*](https://doi.org/10.1002/nme.1620330703).
- [SkyCiv — chapa quadrada com furo](https://skyciv.com/docs/tech-notes/s3d-plate-verification-models/stress-concentration-around-a-hole-in-a-square-plate/). É um benchmark de geometria semelhante, **não igual** no material, carregamento, elementos e condições, e seus números não devem ser transpostos como oráculo de Kt.
- [NASA/NACA — Kirsch e placa infinita](https://ntrs.nasa.gov/citations/19930082747), apenas referência infinita, não de chapa quadrada finita.

## Pendente ao encerrar

Registrar execução com links, erros encontrados e correções, número de testes, valores observados e aprendizado. Ainda haverá necessidade de validação material e tratamento de propriedades reais de estruturas/olhais.

## Execução observada e decisão técnica

| W (mm) | Elementos Q8 | Kt A | Kt B | Kt C | Amplitude |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 80 | 128 | 3,618124 | 3,393224 | 3,348287 | 0,269838 |
| 80 | 512 | 3,588914 | 3,569608 | 3,563842 | 0,025072 |
| 80 | 1.152 | 3,584406 | 3,582520 | 3,581034 | 0,003372 |
| 160 | 128 | 3,213273 | 2,669998 | 2,556529 | 0,656744 |
| 160 | 512 | 3,152512 | 3,065670 | 3,053918 | 0,098594 |
| 160 | 1.152 | 3,139032 | 3,128814 | 3,126387 | 0,012645 |

[Seis soluções Elmer e 18 estimativas aprovadas](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42502117900); [dataset JSON](../dados/ciclo14-recuperacao-tensoes-2026-11-08.json); [artefato externo](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42502117900/artifacts/13625564700) (SHA-256 c89a52b9033b47dc9f4217360266887da632446f981507d9dd8fae214f5c818e).

**Achado central:** a variação entre A/B/C diminui com refinamento, mas o controle de Kirsch demonstra viés grande de B/C na malha grosseira da chapa W=160 mm (−0,4744 e −0,5656). Assim, a concordância numérica por si só **não configura validação do pico físico**. O resíduo de tração radial no furo também diminuiu com o refinamento, permanecendo não nulo.

**Pós-morte de CI:** um teste de campo uniforme foi revisado após reconhecer que a tensão tangencial de um campo cartesiano constante **varia com o ângulo**; os métodos de ajuste devem ser verificados com tolerância explícita, não equivalência literal. Não houve alteração arbitrária da solução FEM para obter aprovação.

**Handover:** estudo de sensibilidade A/B/C concluído. Ainda precisamos de referência de chapa finita com cargas/condições exatamente comparáveis e de experimento físico antes de qualquer aplicação de Kt na liberação ou no dimensionamento de peças reais.
