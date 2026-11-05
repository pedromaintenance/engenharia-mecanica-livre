# Lei de Hooke e alongamento elástico

**Ficha:** EML-SOL-002 · **Maturidade:** didática, com validação analítica · **Escopo:** pequenas deformações e comportamento linear elástico uniaxial.

## O fenômeno

Sob carga axial centrada, uma barra de comprimento inicial `L` sofre alongamento `ΔL`. A deformação longitudinal média é `ε = ΔL/L`, adimensional. No regime linear elástico uniaxial, a relação constitutiva é `σ = E ε`.

Da tensão média `σ = F/A` resulta:

`ΔL = F L / (E A)`

Onde `F` é força axial em N; `L` comprimento em m; `E` módulo de Young em Pa; `A` área em m². O sinal de `ΔL` depende de convenção de tração/compressão.

## Exemplo independente

Use `F = 10 kN`, `L=2 m`, `E=200 GPa` e `A=1000 mm²`.

`ΔL = 10.000 × 2 / (200·10^9 × 0,001) = 0,0001 m = 0,1 mm`.

A rigidez axial equivalente é `K = EA/L = 100 MN/m`, de modo que `F = K ΔL`.

## Efeito de uma carga distribuída

Se houver força distribuída uniforme por comprimento `q` (N/m), barra engastada em `x=0` e força `F` aplicada em `x=L`, o equilíbrio dá:

`N(x) = F + q(L-x)`

e, para `E,A` constantes, deslocamento exato:

`u(x) = [(F+qL)x - qx²/2] / (EA)`.

Logo `u(L) = [FL + qL²/2] / (EA)`.

**Teste:** tomando `q=0`, recuperamos o alongamento linear clássico. Com `F=10 kN`, `q=1000 N/m`, `L=2 m`, `E=200 GPa`, `A=1000 mm²`, obtemos `u(L)=0,11 mm` e reação no apoio `-12 kN`.

## Exclusões

Não prevê elasticidade não linear, dilatação térmica, plasticidade, flambagem, dano, perda de seção, grandes deformações ou deformação por contato e ligações. A aplicação industrial precisa de critérios específicos de projeto e segurança.

**Fonte conceitual:** [Engineering LibreTexts — Axial Deformation](https://eng.libretexts.org/Bookshelves/Mechanical_Engineering/Strength_of_Materials/05%3A_Axial_Loading) e [MIT — Unified Engineering, Materials & Structures](https://ocw.mit.edu/courses/16-001-unified-engineering-materials-and-structures-fall-2021/). Formulação e exemplo redigidos originalmente para o projeto.
