# Fator de concentração de tensão: seção bruta e seção líquida

## Por que o denominador muda o resultado?

Para uma chapa tracionada com **furo central**, o mesmo pico local pode ser dividido por **duas tensões nominais diferentes**. Isso gera dois fatores de concentração, ambos legítimos, desde que a convenção seja declarada e não misturada.

Se a chapa tem largura \`W\`, espessura \`t\`, furo de diâmetro \`d\` e força axial \`P\`:

\[
\sigma_{\mathrm{bruta}}=\frac{P}{Wt},\qquad
\sigma_{\mathrm{líquida}}=\frac{P}{(W-d)t}.
\]

O pico local de tensão \`σmax\` produz:

\[
K_{t,\mathrm{bruto}}=\frac{\sigma_{\max}}{\sigma_{\mathrm{bruta}}},\qquad
K_{t,\mathrm{líquido}}=\frac{\sigma_{\max}}{\sigma_{\mathrm{líquida}}}.
\]

Eliminando a força \`P\`, resulta:

\[
K_{t,\mathrm{líquido}}=\left(1-\frac dW\right)K_{t,\mathrm{bruto}}.
\]

**Portanto, o fator líquido será menor para a mesma tensão máxima quando existe perda de seção.** Isso não significa que a chapa ficou menos perigosa; é apenas a consequência de dividir por uma tensão nominal líquida maior.

## Exemplo de cálculo

Chapa com largura **80 mm**, espessura **5 mm**, furo central de **20 mm** e tração bruta **10 MPa**.

A área bruta é \`80×5=400 mm²\`; força axial correspondente \`P=10×400=4.000 N\`. A seção líquida tem área \`(80−20)×5=300 mm²\`, gerando \`σnom_liquida=13,333 MPa\`.

Supondo um pico local de 36 MPa, **puramente como exemplo**, resulta:

- \`Kt_bruto = 36/10 = 3,6\`;
- \`Kt_liquido = 36/13,333 = 2,7\`.

Os dois fatores descrevem a **mesma tensão máxima local**. Não escolha um denominador apenas porque ele fornece um fator menor.

## Aplicação em Engenharia de Manutenção

Um olhal, furo de parafuso, pino com contato ou chapa fissurada **não** reproduz automaticamente o contorno livre sob tração uniforme de uma chapa ideal. Antes de utilizar Kt, verificar a forma real da peça, o tipo de esforço, a ação do pino, as folgas, o desgaste, as dimensões e o modo de falha a investigar.

O laboratório [Chapa finita com furo](../laboratorios/chapa-finita-furo.md) apresenta uma simulação de tensão plana com tração efetivamente aplicada, controle de malha e **estimativa de pico por extrapolação**. Não é critério para liberar reparo ou definir carga máxima em equipamento.

## Exercícios

1. Chapa W=100 mm, d=20 mm, t=5 mm, P=5.000 N. Determine tensões nominais. **Resposta:** \`σbruta=10 MPa\`, \`σlíquida=12,5 MPa\`.
2. Se o FEM desse mesmo caso estimar pico de 35 MPa, quais são os dois fatores? **Resposta:** \`Kt_bruto=3,5\` e \`Kt_líquido=2,8\`.
3. O valor \`Kt=3\` de Kirsch é automaticamente válido para uma chapa quadrada finita? **Não.** Kirsch trata uma placa infinita com furo circular livre; as condições de contorno e a relação entre largura e diâmetro alteram o comportamento.

**Leituras:** [Vable, *Mechanics of Materials*, seção C.4.1](https://madhuvable.org/wp-content/uploads/2016/04/Entire%20Book%202018.pdf); [Fracture Mechanics — furo e largura finita](https://www.m.fracturemechanics.org/hole.html).
