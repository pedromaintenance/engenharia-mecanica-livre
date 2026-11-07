# Laboratório 09 — Concentração de tensões em furo circular (Kirsch)

O objetivo é **verificar numericamente** o campo de tensões em torno de um furo, não projetar a resistência de uma chapa real. O domínio é um **quarto de coroa circular**, modelado em **tensão plana** por elementos isoparamétricos quadráticos **CPS8R** do CalculiX.

> **Status do laboratório:** implementação e rotina de execução preparadas; não declarar erros ou comportamento observado antes da verificação do workflow externo.

## 1. O problema de Kirsch

Uma placa isotrópica, infinita em x e y, com furo de raio \`a\`, suporta uma tensão remota uniforme \`T\` no eixo x, com bordo do furo livre. Em coordenadas polares, com \`θ\` medido do eixo x:

\[
\sigma_{rr}=\frac{T}{2}(1-a^2/r^2)+\frac{T}{2}(1-4a^2/r^2+3a^4/r^4)\cos(2\theta)
\]

\[
\sigma_{\theta\theta}=\frac{T}{2}(1+a^2/r^2)-\frac{T}{2}(1+3a^4/r^4)\cos(2\theta)
\]

\[
\tau_{r\theta}=-\frac{T}{2}(1+2a^2/r^2-3a^4/r^4)\sin(2\theta)
\]

No bordo \`r=a\`, as trações radial e de cisalhamento se anulam. A tensão circunferencial passa a ser:

\[
\sigma_{\theta\theta}(a,\theta)=T[1-2\cos(2\theta)].
\]

Seu máximo ocorre em \`θ=90°\`, com valor \`3T\`. **\(K_t=3\)** é a concentração **teórica da geometria infinita**, em relação à tensão remota, não um número de segurança para olhais e chapas reais.

**Fontes técnicas:** [OpenGeoSys — benchmark Kirsch](https://www.opengeosys.org/6.5.7/docs/benchmarks/small-deformations/kirsch/), [Jönköping University — stress concentration](https://mechanics.ju.se/SolidMechanics/StressConcentration.html) e [PUC-Rio — revisão e derivação](https://www.dbd.puc-rio.br/pergamum/tesesabertas/1011995_2013_completo.pdf). A implementação e a redação são autorais.

## 2. O domínio computacional não é a placa infinita

Para tornar o problema finito, modelamos \`a ≤ r ≤ R\` e \`0 ≤ θ ≤ 90°\`. O trecho externo **não** recebe simplesmente uma força equivalente a tensão remota; em vez disso, a malha recebe os **deslocamentos exatos da solução de Kirsch** no arco \`r=R\`.

Essa condição é decisiva para a interpretação: o campo ideal de Kirsch satisfaz o problema nos limites do domínio, e qualquer discrepância numérica interior surge principalmente de **discretização geométrica, interpolação, integração e arredondamento**. A comparação \`R/a=4\` contra \`R/a=8\` é um estudo de **truncamento computacional com deslocamentos exatos**, e **não mede o efeito de bordas físicas de uma chapa finita tracionada**.

As linhas de simetria recebem \`Ux=0\` na linha \`x=0\` e \`Uy=0\` na linha \`y=0\`. O bordo do furo fica **livre de cargas**.

### Referência exata dos deslocamentos

Para tensão plana, \`μ=E/[2(1+ν)]\`, \`κ=(3−ν)/(1+ν)\` e \`q=a/r\`. Os deslocamentos prescritos no arco externo são:

\`\`\`text
Ux = T*a/(8μ) × [(r/a)(κ+1) cosθ
      + 2q{(κ+1)cosθ+cos3θ} − 2q³cos3θ]

Uy = T*a/(8μ) × [(r/a)(κ−3) sinθ
      + 2q{(1−κ)sinθ+sin3θ} − 2q³sin3θ]
\`\`\`

O algoritmo foi conferido por substituição na lei de Hooke isotrópica em tensão plana, recuperando as tensões de Kirsch. A expressão de deslocamento em **deformação plana**, com \`κ=3−4ν\`, aparece em um [benchmark de elasticidade da Coreform](https://docs.coreform.com/cifa/latest/verification-manual/problems/solid_mechanics/linear_elastic_stress/infinite-plate-with-hole/infinite-plate-with-hole.html); este laboratório usa a constante **de tensão plana**, não a de deformação plana.

## 3. Dimensões e material do experimento

| Parâmetro | Valor |
| --- | ---: |
| Raio do furo \`a\` | 10 mm |
| Arco externo padrão \`R\` | 80 mm (8a) |
| Arco externo comparativo | 40 mm (4a) |
| Tração remota de referência \`T\` | 10 MPa |
| E | 200 GPa |
| ν | 0,30 |
| Espessura de referência | 5 mm |
| Tensão ideal máxima no bordo | 30 MPa |
| Elemento | CPS8R, quadrático de 8 nós |
| Malhas padrões \`nr×nt\` | 4×8, 8×16, 16×32 |

O CalculiX expande internamente CPS8R em elementos sólidos quadráticos, conforme o [manual oficial de elementos](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node263.html). O caso representa um **modelo bidimensional de tensão plana**; não é um modelo tridimensional da espessura e não demonstra efeitos de flexão fora do plano.

## 4. Discretização do furo e qualidade

A malha Q8 é construída diretamente em coordenadas polares, sem depender de licença ou instalação de Gmsh. Cada célula tem quatro vértices e quatro nós de meio de aresta compartilhados; sobre o círculo, os nós médios também permanecem na circunferência.

As camadas radiais obedecem \`r_i=a+(R−a)(i/nr)^2\`, concentrando elementos junto ao bordo do furo. O gerador avalia o **determinante do jacobiano isoparamétrico Q8 nos quatro pontos de Gauss de cada elemento** e recusa malhas invertidas ou degeneradas.

Essa construção é uma aproximação quadrática do arco, não um círculo matematicamente exato entre os nós. Maior precisão geométrica é parte do motivo para refinar a malha.

## 5. O que o pós-processamento mede

O CalculiX escreve \`COORD,S\` com \`*EL PRINT\` no arquivo \`.dat\`. O parser exige um registro de coordenadas e seis componentes de tensão para **cada ponto de integração**; os elementos CPS8R são internamente expandidos, com **oito pontos por elemento** na saída considerada.

As tensões analíticas polares são transformadas para coordenadas cartesianas e confrontadas com \`Sxx\`, \`Syy\` e \`Sxy\`. O erro tensorial na amostra é calculado como:

\[
e^2=(S_{xx}-S_{xx}^{*})^2+(S_{yy}-S_{yy}^{*})^2+2(S_{xy}-S_{xy}^{*})^2.
\]

São divulgados **erro RMS global** e **erro RMS na primeira camada radial próxima do furo**, normalizados por \`T\`. A norma RMS usa pesos iguais na malha estruturada deste estudo; não é uma norma integral de energia, nem serve automaticamente para elementos e volumes diferentes.

A tensão circunferencial é reconstruída nos pontos internos de Gauss e reportada como \`kt_proxy_pontos_integracao\`. **Esse proxy NÃO é \(K_t\) no bordo \`r=a\`.** O valor da solução analítica no bordo permanece 3; para estimar um valor na superfície, seriam necessários extrapolação, interpolação controlada e teste de convergência próprios.

## 6. Executar

Sem solver instalado:

\`\`\`bash
python -m engmec.kirsch --somente-gerar --nr 8 --nt 16 --saida build/kirsch/n-8
\`\`\`

Com \`ccx\` disponível:

\`\`\`bash
python -m engmec.kirsch --nr 8 --nt 16 --raio-externo-m 0.08 --saida build/kirsch/n-8
\`\`\`

O [workflow GitHub Actions](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/kirsch.yml) resolve três malhas \`R=8a\` e mais uma \`R=4a\`, arquiva arquivos \`.inp\`, \`.dat\`, \`.frd\`, logs e JSON. O script \`scripts/avaliar_kirsch.py\` **reprova** convergência ausente, campos incompletos e resultado não finito.

## 7. Aplicação mecânica e limites

Um furo pode elevar a tensão local mesmo quando a seção tem tensão nominal moderada. Essa observação é especialmente relevante na inspeção de suportes, furos de parafusos e chapas com entalhes. Entretanto, **não usar Kt=3 automaticamente** para olhais, furos carregados por pinos, juntas aparafusadas, placas curtas ou chapas danificadas.

O benchmark não considera **carga de apoio do pino (*bearing*)**, atrito, folga, excentricidade, anisotropia, encruamento, escoamento plástico, tensões residuais, falha por fadiga e possíveis trincas. Para uso industrial, são necessários geometria, carregamento, histórico, material, tolerâncias, critério de aceitação e, quando aplicável, ensaios.

**Próximo gate técnico:** tensão de Kirsch no contorno por extrapolação com incerteza, placa retangular realmente finita sob tração uniforme, comparação com Gmsh e cálculo de \`Kt\` com base nominal declarada.
