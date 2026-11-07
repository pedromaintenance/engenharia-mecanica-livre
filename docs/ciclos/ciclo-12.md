# Ciclo 12 — Implementação independente de elasticidade plana Q8

**Data:** 07/11/2026. **Versão pretendida:** v0.12.0. **Issue de referência:** [#14](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/14).

## Motivação

Os ciclos 10 e 11 produziram concentrações de tensão estimadas em chapas quadradas finitas, mas todos os problemas foram resolvidos com **CalculiX CPS8R**. A independência de geradores de malha Gmsh versus autoral não garantia independência do algoritmo FEM.

O ciclo 12 implementa um **segundo solucionador FEM** em Python usando NumPy e SciPy, sem chamar matrizes, solucionadores nem deslocamentos do CalculiX.

## Entregas

- `src/engmec/fem2d_indep.py`: funções Q8, derivadas analíticas, constitutiva de tensão plana, montagem de matrizes `Ke=t∫BᵀDBdA` com quadratura 3×3, forças nodais consistentes, matriz global esparsa, condição de simetria, solução, reações e recuperador de tensão **diretamente no contorno** por gradiente de deslocamentos.
- `tests/test_fem2d_indep.py`: partição de unidade, reprodução de coordenadas, derivadas por diferenças finitas, integração de polinômios, *patch test* de deformação constante, material admissível, propriedades de `D`.
- `scripts/avaliar_ciclo12.py` e `tests/test_aval_ciclo12.py`: cotejam relatórios do par sob **arquivos MSH2 idênticos por SHA-256**, calculam diferença absoluta e relativa e recusam arquivos ausentes, descumprimento de equilíbrio e valores impossíveis.
- `.github/workflows/ciclo12-dois-solvers.yml`: instala CalculiX, Gmsh, NumPy e SciPy com versões registradas e executa quatro pares de malhas H/a=4 e 8, n=16 e 24.
- `docs/laboratorios/dois-solvers-q8.md`: problema físico, método, resultados, bibliografia e limites.
- `docs/dados/ciclo12-solvers-independentes-2026-11-07.json`: dados observados permanentemente versionados.

## Resultado externo

[Workflow de comparação #42423510950](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42423510950) passou com **4 pares/8 simulações** e todos os quatro pares apresentaram hash SHA256 igual para o mesmo arquivo de malha. Ambiente: Ubuntu 24.04, Gmsh 4.12.1, CalculiX 2.21-1, NumPy 2.5.4, SciPy 1.18.1.

| W / elementos | Kt CalculiX (ajuste de Gauss) | Kt SciPy (gradiente FEM direto) | Desvio relativo |
| --- | ---: | ---: | ---: |
| 80 mm / 512 | 3,596799 | 3,588914 | −0,2192% |
| 80 mm / 1.152 | 3,614709 | 3,584406 | −0,8383% |
| 160 mm / 512 | 3,081885 | 3,152512 | +2,2917% |
| 160 mm / 1.152 | 3,153882 | 3,139032 | −0,4708% |

A comparação não separa somente diferenças de solucionador: há **quadratura e recuperação de tensão distintas**. A divergência não cai monotonicamente na chapa de 80 mm. Isso não constitui prova de convergência nem referência exata.

A implementação SciPy verifica reação horizontal com erro relativo inferior a 5,3×10⁻¹⁴; a tensão radial no bordo avaliada no nó crítico é positiva e não nula, decaindo com refinamento para ambos os tamanhos: indicador de discretização ainda presente.

## Falha de CI diagnosticada e corrigida

Na primeira execução do pipeline de **qualidade geral**, `test_rejeita_material_invalido` falhou em ambiente sem NumPy, pois a função constitutiva carregava a dependência opcional **antes** de validar os argumentos. A rotina foi corrigida para validar `E` e `ν` primeiro e importar NumPy apenas depois. Os testes de elasticidade que dependem de SciPy/NumPy são ativados no workflow especializado. **O solver externo já havia concluído com sucesso**, e a revisão também passou na suite geral em execução posterior.

## Condição de aceite e continuidade

A etapa de implementação independente do algoritmo foi realizada; a issue #14 permanece **aberta** se for exigida validação em **segundo software FEM externo** (Elmer/FEniCSx ou equivalente), ensaio comparável e análise de sensibilidade do pico superficial em três ou mais malhas por solver.

Para engenharia de manutenção, o principal avanço foi de **rastreabilidade e verificabilidade do cálculo**, não de habilitação de resultados para projeto ou liberação física de componentes.
