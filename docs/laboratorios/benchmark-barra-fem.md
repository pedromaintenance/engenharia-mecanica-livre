# Laboratório 05 — Barra axial: solução analítica × elementos finitos

**Status:** benchmark didático implementado e testável com Python puro, sem bibliotecas científicas obrigatórias. **Não é um benchmark externo de CalculiX/FreeCAD ainda.**

## Objetivo

Comparar a análise exata de uma barra de área constante com uma discretização em elementos finitos lineares. O modelo admite tração/compressão axial, carga distribuída uniforme `q` (N/m), força na extremidade `F` e extremidade esquerda fixa.

## Dados de referência

| Variável | Valor |
| --- | ---: |
| Comprimento `L` | 2 m |
| Área `A` | 1000 mm² |
| Módulo `E` | 200 GPa |
| Força de ponta `F` | 10.000 N |
| Carga distribuída `q` | 1.000 N/m |

Pela solução analítica `u(L)=[FL+qL²/2]/EA`, a ponta se desloca **0,11 mm**; a reação calculada no apoio deve ser **−12 kN** pela convenção adotada.

## Executar

```bash
python -m pip install -e .
engmec fem-barra --comprimento-m 2 --area-mm2 1000 --e-gpa 200 --forca-n 10000 --carga-linear-n-m 1000 --elementos 4
```

Para verificar **convergência do erro de tensão** (e não apenas deslocamento da ponta):

```bash
engmec fem-barra --comprimento-m 2 --area-mm2 1000 --e-gpa 200 --forca-n 10000 --carga-linear-n-m 1000 --estudo-malha
```

## O que deverá aparecer

| Elementos | Erro RMS teórico da tensão |
| ---: | ---: |
| 1 | ≈ 0,57735 MPa |
| 2 | ≈ 0,28868 MPa |
| 4 | ≈ 0,14434 MPa |
| 8 | ≈ 0,07217 MPa |
| 16 | ≈ 0,03608 MPa |

O erro cai com `h=L/n`; a razão entre erros em malhas sucessivas deve ser aproximadamente 2. Os deslocamentos nodais são exatos para este carregamento simples, logo não são uma métrica convincente de convergência.

A implementação também apresenta `erro_equilibrio_forcas_n`, `erro_trabalho_energia_j` e `erro_nodal_max_m`. Esses resíduos devem ser compatíveis com a precisão numérica da solução.

## Perguntas para estudo

1. Por que refinar de 1 para 8 elementos não melhora significativamente o deslocamento na ponta nesse caso?
2. Se `q=0`, qual deve ser o erro de tensão? **Resposta:** aproximadamente zero, limitado ao arredondamento.
3. Se `A` for duplicada, como se alteram o alongamento da ponta e as tensões? **Resposta:** pela metade no modelo elástico axial.
4. O que mudaria ao introduzir variação de `E(x)`, apoios elásticos ou contato? **Resposta:** mudam as hipóteses e o sistema discreto; é necessário novo modelo e testes.

## Aplicação e segurança

Não usar como análise de resistência real, dimensionamento de eixo, tirante, haste ou componente de equipamento sem avaliação de concentração de tensão, compressão/flambagem, ligação, material, geometria e critérios normativos aplicáveis. Modelos FEM 3D e validação experimental continuam pendentes.

[Implementação Python](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/src/engmec/fem_barra.py) · [Testes](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/tests/test_fem_barra.py) · [Teoria](../conceitos/rigidez-elemento-finito.md).
