# Convergência, verificação e validação em FEM

**Ficha:** EML-NUM-002 · **Natureza:** metodologia de verificação de cálculo · **Estado:** didático.

## Verificação não é validação

- **Verificação numérica:** o algoritmo resolve corretamente as equações discretizadas? Examina montagem, erro algorítmico, condições de contorno, resíduo e convergência de malha.
- **Validação física:** as equações e condições idealizadas representam adequadamente a situação física real? Exige dados observacionais, hipótese experimental, incerteza e comparação de campo.
- **Aceitação de engenharia:** verifica critérios normativos, materiais reais, modos de falha e responsabilidade técnica; não resulta automaticamente dos dois passos anteriores.

## O que medir

Ao refinar `h`, acompanhar pelo menos uma grandeza cujo erro **não seja identicamente nulo** no problema de referência. No benchmark de barra uniforme com `q` distribuído, o deslocamento dos nós já é exato com elementos lineares; por isso usá-lo isoladamente geraria uma falsa impressão de evidência de convergência.

A tensão é constante em cada elemento FEM, enquanto a solução analítica é linear. O erro RMS de tensão escala como `O(h)`.

## Roteiro de diagnóstico de convergência

1. Definir grandezas de interesse e solução analítica de comparação.
2. Fixar hipóteses físicas e condições de contorno.
3. Resolver malhas progressivamente mais finas.
4. Comparar erros absolutos e relativos, não só gráficos visualmente suaves.
5. Confirmar equilíbrio e energia; analisar sinais e ordem de convergência.
6. Documentar hipóteses que permanecem fora do modelo.
7. Quando houver ensaio real, comparar com incerteza e critérios independentes.

## Critério de reprovação

O refinamento que muda drasticamente resultado crítico sem tendência compreensível impede validação. Um resultado estacionário entre malhas não prova modelo físico correto; pode haver erro sistemático de hipótese ou condição de contorno.

**Referência:** [A.F. Bower — Theory and Implementation of FEA](https://solidmechanics.org/Text/Chapter8_1/Chapter8_1.htm). A seleção do erro RMS para barra sob `q` uniforme é derivada do benchmark autoral.
