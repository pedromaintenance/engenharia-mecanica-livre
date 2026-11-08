# Ciclo 13 — Solver FEM externo Elmer e comparação de tensão superficial

**Data:** 07/11/2026. **Versão prevista:** v0.13.0. **Issues:** [#14](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/14) e [#13](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/13).

## Lacuna herdada

O ciclo 12 comparou CalculiX com uma implementação **autoral de Q8 em NumPy/SciPy**. Embora as matrizes e o solucionador fossem independentes, a implementação Python ainda não era um segundo software FEM externo consolidado. Além disso, o Kt recuperado por extrapolação de tensões (CalculiX) e por gradiente nodal (SciPy) envolvia **duas técnicas de recuperação**, confundindo uma parte da diferença dos solvers com a diferença de pós-processamento.

## Objetivo de trabalho

Executar a mesma chapa quadrada finita, com mesmas restrições e tração real, no **Elmer FEM** e no solucionador SciPy. Aplicar o **mesmo operador de gradiente no ponto de contorno** para ambos os campos de deslocamentos e comparar Kt, deslocamentos de referência e tensões normais residuais.

## Artefatos implementados

- \`src/engmec/elmer_chapa.py\` — gera geometria CAD com grupos físicos, converte malha Gmsh via ElmerGrid, identifica dinamicamente os IDs de fronteira, constrói \`case.sif\` com StressSolver em tensão plana, executa Elmer, lê deslocamentos VTU, reconcilia nós por coordenadas, reaplica o operador de recuperação Q8 e compara com SciPy.
- \`src/engmec/fem2d_indep.py\` — inclui deslocamentos nos quatro pontos físicos de referência, permitindo a comparação nodal independente.
- \`tests/test_elmer_chapa.py\` e \`tests/test_aval_ciclo13.py\` — verificam geometria, BCs, parser Elmer e reprovação sem dados externos.
- \`scripts/avaliar_ciclo13.py\` — consolida três malhas em cada uma de duas larguras de chapa, registrando deslocamentos, Kt e resíduos.
- \`.github/workflows/ciclo13-elmer.yml\` — ambiente reproduzível Gmsh/NumPy/SciPy/meshio + Elmer via imagem Docker, com logs e artefatos.

## Critérios de aceite

1. ElmerGrid converte a malha Q8 e preserva quantidade de elementos, grupos físicos e superfícies.
2. ElmerSolver executa de fato com \`Plane Stress\`, material e tração corretos, gerando arquivo VTU de deslocamentos.
3. Os nós VTU são reconciliados com MSH2 por geometria, com tolerância física e sem duplicidade.
4. A recuperação do pico utiliza o **mesmo operador de gradiente** Elmer/SciPy, isolando melhor o efeito da solução de deslocamentos.
5. São comparados três refinamentos por H/a=4 e H/a=8, deslocamentos e Kt com limites observados e sem fabricação de resultados.
6. Hash/digest da imagem, entradas \`.sif\`, \`.geo\`, \`.msh\`, malha convertida, \`.vtu\`, logs e JSON são preservados.
7. CI e publicação MkDocs aprovados. Erros de implantação são relatados e corrigidos no próprio ciclo.

## Ressalvas

Os resultados de Kt na borda seguem sendo **estimativas FEM de um elemento no ponto crítico**; a concordância entre programas com o mesmo recuperador não qualifica esse método superficial. Elmer é um segundo programa FEM consolidado, mas não oferece neste exercício validação experimental de chapa real; Kirsch infinito não é a solução exata da chapa quadrada finita. Nenhum valor obtido é admissível de integridade ou manutenção.

## Pesquisa documental

Manual oficial e exemplos do Elmer, documentação do Gmsh, instalação PPA do Elmer/CSC e documentação do pacote SciPy foram consultados; detalhes e links estão no [laboratório](../laboratorios/elmer-fem-independente.md). O material descritivo e o código do adaptador são autorais, sem redistribuição de fontes de terceiros.

## Execução concluída: resultados e pós-morte

[Workflow Elmer #42428467703](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42428467703): seis modelos resolvidos no Elmer FEM em Docker; seis soluções comparáveis no FEM Q8 SciPy; três refinamentos para W=80 mm e três para W=160 mm.

| W (mm) | Q8 | Kt bruto Elmer | Kt bruto SciPy | σrr/T Elmer |
| ---: | ---: | ---: | ---: | ---: |
| 80 | 128 | 3.618124 | 3.618124 | 11.839% |
| 80 | 512 | 3.588914 | 3.588914 | 1.587% |
| 80 | 1152 | 3.584406 | 3.584406 | 0.288% |
| 160 | 128 | 3.213273 | 3.213273 | 29.930% |
| 160 | 512 | 3.152512 | 3.152512 | 5.519% |
| 160 | 1152 | 3.139032 | 3.139032 | 0.969% |

**Resultado de verificação numérica:** o maior desvio relativo nos deslocamentos de referência entre solucionadores ficou abaixo de 7×10⁻¹³ e a maior diferença absoluta em Kt com o mesmo operador de gradiente ficou abaixo de 7×10⁻¹¹. É um **teste de equivalência da solução discreta** para o problema, não uma validação física da tensão superficial.

**Diagnóstico da fronteira livre:** o erro `σrr/T` na parede diminuiu com o refinamento, mas não é exatamente zero; isso evita confundir coincidência entre solvers com convergência pontual do Kt verdadeiro.

**Falhas documentadas:** a execução inicial encontrou dificuldade em conciliar nós de VTU com MSH2; a saída de visualização podia conter coordenadas deformadas. A primeira correção de arredondamento não resolveu esse efeito, e a versão final usou `Displace Mesh=False` e uma reconciliação robusta que aceita somente coordenadas de referência ou `x_deformado-u` com correspondência espacial bijetiva. A correção foi aprovada em execução externa subsequente.

**Rastreabilidade:** [dataset versionado](../dados/ciclo13-elmer-fem-2026-11-07.json), [artefato de evidências](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42428467703/artifacts/13596965037), ID 13596965037, SHA-256 `5613463a055a45f1c69e22844085bd63364edc29b7afdbd50a45f705bb4caed1`. O digest da imagem Docker Elmer está preservado no arquivo `elmer-image-digest.txt` dentro do artefato.

**Próximo gate:** distinguir erro de solução de erro de recuperação superficial (gradiente direto, projeção e extrapolação) sobre a **mesma malha**; confrontar com literatura de mesma geometria/BC; validar materialmente apenas com ensaio adequado. A issue #14 permanece aberta para esses critérios restantes.
