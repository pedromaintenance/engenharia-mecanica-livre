# Concentração de tensão em furos e entalhes

## Ideia mecânica

Uma seção nominalmente submetida à tração não apresenta necessariamente tensão uniforme: **geometria, furo, raio de concordância e descontinuidade alteram as trajetórias das tensões**. Para tensão linear-elástica, define-se \`Kt=σmax/σnom\`, especificando sempre **qual tensão nominal** está no denominador.

Na clássica solução de **Kirsch** para chapa infinita com furo circular livre e tração remota \`T\`, o pico de tensão circunferencial no contorno ocorre perpendicularmente à direção da carga: \`σθθ,max=3T\`; portanto \`Kt=3\` **em relação à tensão remota T**. A geometria ideal e sua condição de contorno fazem parte desse resultado.

## Exemplo didático

Adotando \`T=10 MPa\` e furo de 20 mm de diâmetro, a solução ideal dá **30 MPa** no ponto crítico. Dobrar o diâmetro mantendo a placa matematicamente infinita não muda Kt; já alterar a largura finita, o carregamento ou introduzir contato de pino invalida a aplicação literal de Kt=3.

## Aplicação na manutenção

Ao inspecionar uma chapa ou olhal, registrar **geometria real e dimensões**: diâmetro, espessura, afastamento às bordas, eventuais ovalizações, raio de concordância, marcas de desgaste, trincas, esforços e direção de carregamento. Não aprovar solda ou substituição por cálculo baseado exclusivamente em Kirsch. Para fadiga, \`Kt\` elástico também não é automaticamente o fator de concentração efetivo à fadiga \`Kf\`.

## Exercícios

1. Para \`T=8 MPa\`, calcule o pico ideal de Kirsch. **Resposta:** \`24 MPa\`.
2. O valor \`Kt=3\` se aplica sem modificação a um olhal com pino apoiado no furo? **Não**: a condição de contato/carga na borda é diferente.
3. Um modelo FEM informa 2,7 vezes \`T\` no primeiro ponto de Gauss afastado do furo. Podemos declarar \`Kt=2,7\` na borda? **Não**: o ponto está no interior do elemento, e o erro de extrapolação não foi controlado.

Veja o [Laboratório 09](../laboratorios/kirsch-furo.md), o [estudo de Kirsch em OpenGeoSys](https://www.opengeosys.org/6.5.7/docs/benchmarks/small-deformations/kirsch/) e a [discussão de tensão em chapas com furo da Jönköping University](https://mechanics.ju.se/SolidMechanics/StressConcentration.html).
