# Ciclo 07 — Flexão pura tridimensional com erro de discretização

**Data:** 05/11/2026. **Motivação:** [issue #11](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/11), pendente do ciclo 06.

## Hipótese física

O teste axial anterior possuía campo de deformações representável exatamente por C3D8; a coincidência dos valores na saída textual, em quatro malhas, não demonstrava convergência numérica em um problema não homogêneo. Este ciclo escolhe **flexão pura com σ_xx=-Eκy**, e um campo 3D de deslocamentos que contém termos quadráticos, não representados exatamente pelo elemento linear.

## Arquivos do ciclo

- `src/engmec/flexao_calculix.py`: malha C3D8, tração de face integrada consistentemente, apoios mínimos, solução da elasticidade, parser de U/RF e execução opcional do CalculiX.
- `tests/test_flexao_calculix.py`: derivação de referência, equilíbrios, malhas, valores de deslocamento e registros de falhas.
- `scripts/avaliar_convergencia.py` e `tests/test_convergencia.py`: resultados de várias malhas, taxas aparentes, critérios de erro não trivial e resíduo de força.
- `.github/workflows/flexao-calculix.yml`: execução real, instalação do solver Ubuntu, validação e arquivo de artefatos.
- `docs/laboratorios/flexao-pura-3d.md`: fundamentação, equações, hipóteses e reprodução.

## Critérios físicos e de aceitação

| Métrica | Referência |
| --- | --- |
| `u_y(L,0,0)` | +0,200 mm |
| `u_x(L,b/2,0)` | −0,100 mm |
| tensão axial máxima em módulo | 100 MPa |
| momento em cada face | ±16.666,67 N·m |
| força resultante em cada face | 0 N |
| malhas C3D8 | 8, 64, 512, 4096 elementos |

O resultado do solver só será declarado **observado** depois da conferência dos logs de workflow, com o reporte de erros reais. O critério de 25% de redução de erro com refinamento impede que um caso de erro constante seja confundido com convergência. Potenciais ressalvas: shear locking C3D8, arredondamento de saída, carga nodal em nós apoiados e exigência de subtração das CLOAD ao calcular reações.

## Fora do escopo

Validação experimental, tensões de um equipamento real, comparação já executada com C3D20R, fadiga, material não linear, publicação de obras externas e aprovação de dimensionamento.

## Handover

**Confirmar status:** novo commit → CI padrão → workflow CalculiX → logs/artefatos → relatório JSON de resultados reais → portal MkDocs. Falhas devem ser registradas e corrigidas com teste de regressão. Manter issue #11 aberta caso falte evidência ou convergência não trivial.


## Execução e aceite reais

O [workflow CalculiX #42064616852](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42064616852) foi concluído com **sucesso**, CalculiX 2.21-1 em Ubuntu 24.04. Foram executadas malhas de 8, 64, 512 e 4096 elementos C3D8, com erros em Uy de **29,7457%; 10,82515%; 3,36765%; 0,9942%** e taxas aparentes **1,4583; 1,6846; 1,7601**.

As quatro saídas foram lidas do arquivo `.dat`, comparadas contra `u_y=0,2 mm` e `u_x=-0,1 mm`, e agregadas no relatório gerado. A implementação desconta `CLOAD` dos nós de apoio antes de calcular o resíduo de reação, conforme o manual do CalculiX. Os resíduos relativos ficaram inferiores a 1%.

**Evidência arquivada:** artifact `flexao-pura-calculix-3d` (ID 13433760622, SHA-256 `186dfedbf70dab4a6bc61d8594abf34e92b687dbdd32465e51213d198ed77a00`), retenção anunciada até 05/12/2026. O sumário de medições permanece em [dados estruturados](../dados/flexao-pura-3d-2026-11-05.json).

**Controles de qualidade:** [CI com 53 testes aprovados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42064616968) e [GitHub Pages publicado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42064616933).

**Estado:** critério de convergência não trivial do ciclo 07 atendido; continuam pendentes comparação de tipos de elementos, extração detalhada de tensões, ensaio físico e aplicações de projeto.
