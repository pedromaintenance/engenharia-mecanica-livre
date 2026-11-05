# Elemento finito de barra axial 1D

**Ficha:** EML-NUM-001 · **Natureza:** método computacional didático · **Estado:** implementação com testes, aguardando revisão externa.

## Problema aproximado

A equação de equilíbrio de uma barra linear sob força axial distribuída por comprimento é:

`-d(EA du/dx)/dx = q`.

Para um trecho de comprimento `h` com módulo `E` e área `A` constantes, aproxima-se o deslocamento por interpolação linear:

`u(x) ≈ N₁(x) u₁ + N₂(x) u₂`.

As derivadas constantes das funções de forma produzem a matriz elemental:

```text
          EA  [  1  -1 ]
k_elemento = --  [        ]
          h   [ -1   1 ]
```

Uma força distribuída uniforme `q`, integrada de modo consistente, produz vetor nodal `f_q = qh/2 [1, 1]`.

## Montagem e contorno

A estrutura é dividida em `n` elementos de tamanho `h=L/n`. As matrizes locais são somadas nas posições globais dos dois nós correspondentes. Impõe-se `u(0)=0` removendo a liberdade prescrita e resolve-se o sistema tridiagonal para `u₁...u_n`. Uma força concentrada `F` é aplicada na extremidade direita.

## Pós-processamento

Cada elemento linear tem deformação axial constante `ε_e = (u_{i+1}-u_i)/h` e tensão `σ_e=Eε_e`. Para `q ≠ 0`, a solução exata apresenta tensão que varia linearmente ao longo da barra; por isso, **a tensão constante por elemento é aproximação**, ainda que os deslocamentos dos nós coincidam com a solução analítica nesse caso específico.

O erro RMS (Pa) entre as tensões por elemento e a solução contínua é medido com quadratura de Gauss de dois pontos:

`erro_RMS = sqrt[(1/L) ∫(σ_FEM - σ_exata)² dx]`.

No problema uniforme de referência, `erro_RMS = |q| h / (A sqrt(12))`. Dobrar o número de elementos reduz esse erro pela metade (convergência de ordem 1).

## Auditoria do modelo

O benchmark verifica simultaneamente deslocamento analítico, reação de apoio, conservação de força, identidade entre trabalho externo e `2U` e convergência das tensões em estudo de malha.

**Limites:** elementos lineares 1D não demonstram validade para tensões tridimensionais, materiais anisotrópicos, contato, não linearidades ou fadiga. O solver é autoral e distinto de FreeCAD/CalculiX.

**Referências para a teoria:** [A. F. Bower — Applied Mechanics of Solids, Capítulo 8](https://solidmechanics.org/Text/Chapter8_1/Chapter8_1.htm); [Engineering LibreTexts — Axial Loading](https://eng.libretexts.org/Bookshelves/Mechanical_Engineering/Strength_of_Materials/05%3A_Axial_Loading).
