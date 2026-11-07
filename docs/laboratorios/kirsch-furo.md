# Laboratório 09 — Concentração de tensões em furo circular (Kirsch)

O objetivo é **verificar numericamente** o campo de tensões em torno de um furo, não projetar a resistência de uma chapa real. O domínio é um **quarto de coroa circular**, modelado em **tensão plana** por elementos isoparamétricos quadráticos **CPS8R** do CalculiX.

> **Status do laboratório:** **quatro casos executados no CalculiX 2.21-1**, com logs, tensões nos pontos de Gauss e estudo de erro de malha. Os resultados e ressalvas estão registrados abaixo.

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

São divulgados **erro RMS global** e **erro RMS na primeira camada radial próxima do furo**, normalizados por \`T\`. Uma simples média sem pesos favorece as regiões com mais elementos. Como a malha é **graduada radialmente**, o relatório preserva essa média apenas como diagnóstico e também apresenta erro **ponderado por área aproximada**: para cada elemento, calcula-se a área geométrica do setor polar e reparte-se igualmente entre seus oito pontos de Gauss. Esse procedimento é comparável neste experimento, mas **não constitui norma de energia nem quadratura exata por jacobiano individual**. Para verificar o erro local sem mudar a região física, mede-se também o RMS na faixa fixa **a ≤ r ≤ 1,5a**.

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


## 8. Execução externa confirmada — 07/11/2026

O [workflow CalculiX #42415560152](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42415560152) executou as quatro entradas com `calculix-ccx 2.21-1` no Ubuntu 24.04. O pós-processamento leu as seis componentes do tensor e as coordenadas de **todos os pontos de Gauss**, comparou `Sxx/Syy/Sxy` com Kirsch e passou nos critérios de refinamento por área. [CI geral #42415560148](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42415560148): 76 testes aprovados.

### Erro na malha R/a = 8

| Malha radial × angular | Elementos | Erro global RMS ponderado | Erro RMS na faixa fixa a–1,5a | Proxy interior de concentração |
| ---: | ---: | ---: | ---: | ---: |
| 4 × 8 | 32 | 0,5208% | 2,4393% | 2,4944 |
| 8 × 16 | 128 | 0,1170% | 0,7655% | 2,8652 |
| 16 × 32 | 512 | 0,0723% | 0,4481% | 2,9848 |

A referência `Kt=3` e a tensão máxima `3T=30 MPa` são **analíticas**. Não foi calculado um `Kt` superficial por extrapolação; o indicador apresentado é o **máximo circunferencial observado dentro dos elementos** na primeira banda radial.

Os erros globais e da **faixa fixa** diminuíram. Entretanto, o erro RMS **não ponderado só na primeira camada**, que muda fisicamente de tamanho, foi **2,4393% → 1,0745% → 1,5934%**; portanto **não caiu monotonicamente**. Essa ressalva está preservada no dataset em vez de ser ocultada. A taxa aparente calculada sobre o RMS global ponderado foi ~2,154 e ~0,695. Não há evidência suficiente para declarar uma ordem assintótica única.

### Mudança do raio externo

Com `R/a=4`, a malha 16 × 32 resultou em erro RMS global ponderado de **0,1496%**, erro na faixa a–1,5a de **0,4912%** e proxy interno de **3,0093**. O valor acima de 3 mostra, inclusive, por que esse proxy interior não deve ser promovido a fator de concentração superficial.

**Isso NÃO mede o efeito real da largura de uma chapa.** Os dois arcos externos receberam os respectivos deslocamentos analíticos de Kirsch, e a distribuição da malha mudou. Uma placa finita efetivamente tracionada nas bordas constitui outro problema de contorno e está pendente.

### Execução, arquivos e rastreabilidade

- [Workflow real e logs](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42415560152).
- [Artefato das entradas e saídas](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42415560152/artifacts/13590939560), contendo `.inp`, `.dat`, `.frd`, `solver.log` e relatórios JSON. Retenção informada até **07/12/2026**.
- [Dataset permanente e metodologia dos erros](../dados/kirsch-cps8r-2026-11-07.json).
- [Código autoral](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/src/engmec/kirsch.py).

### Diagnóstico do solver — aprendizados do ciclo

1. O arquivo `*NSET` falhou ao usar mais de 16 números por linha; agora todos os conjuntos são quebrados e testados.
2. As restrições com mantissas longas foram rejeitadas pelo leitor `*BOUNDARY` do CCX 2.21; os deslocamentos são impressos com nove algarismos significativos, preservando a referência em escala de micrômetros.
3. As coordenadas analiticamente nulas nos eixos de simetria eram serializadas como ~1e-18 m. O CCX apontou jacobianos não positivos nos elementos junto ao eixo; **a correção para coordenadas exatamente zero eliminou essa falha**. O gerador também confere positividade do jacobiano 2D Q8, mas o teste interno do solver é indispensável.
4. O erro RMS não ponderado em malha graduada revelou um comportamento ambíguo. Adicionamos erro ponderado por setor e a comparação na faixa fixa, **sem apagar** as métricas originais.

**Estado científico:** verificação numérica do problema de Kirsch com contorno externo analítico, não validação experimental nem solução de chapa finita com carregamento físico.
