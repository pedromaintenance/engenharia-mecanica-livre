# Esforço normal e tensão axial

**Ficha:** EML-SOL-001 · **Maturidade:** autoral didática; sem revisão por profissional externo · **Escopo:** barra prismática, tração/compressão centrada.

## Função e sistema

Uma barra axial transmite força entre seus extremos. No modelo simplificado, cargas paralelas ao eixo longitudinal geram esforço normal interno `N`, positivo quando se adota tração como positiva. O estado local de tensões de um elemento real pode ser mais complexo devido a contatos, furos e transições geométricas.

## Modelo e unidades

Para força axial uniforme e seção transversal de área `A`:

`σ = N/A`

- `σ`: tensão normal média em Pa = N/m²;
- `N`: esforço axial interno em N;
- `A`: área resistente em m².

Exemplo: barra ideal com `N = 10.000 N` e `A = 1.000 mm² = 0,001 m²`:

`σ = 10.000 / 0,001 = 10.000.000 Pa = 10 MPa`.

## Teste de consistência

A tensão aumenta proporcionalmente à força e inversamente à área. Se a força dobrar mantendo a seção, a tensão média dobra; se a área dobrar sob força igual, a tensão cai à metade. A verificação dimensional é `N/m² = Pa`.

## Limites

A expressão não resolve flexão, torção, contato, flambagem, concentração de tensões, ruptura ou tensões residuais. A tensão média não equivale à máxima tensão local. Em compressão, a estabilidade pode controlar o projeto muito antes do escoamento.

**Fonte para estudo:** [Open Engineering LibreTexts — Axial Loading](https://eng.libretexts.org/Bookshelves/Mechanical_Engineering/Strength_of_Materials/05%3A_Axial_Loading), [MIT — Mechanics & Materials I](https://ocw.mit.edu/courses/2-001-mechanics-materials-i-fall-2006/). Links de referência, sem republicação dos textos originais.
