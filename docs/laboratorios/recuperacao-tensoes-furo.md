# Laboratório 14 — Recuperação de tensões e incerteza numérica de Kt

**Status:** seis casos reais Elmer executados em 08/11/2026 com todos os recuperadores avaliados sobre o mesmo vetor nodal. A metodologia está abaixo e os resultados auditáveis foram preservados em JSON e CSV.

## 1. Questão de engenharia

Na chapa quadrada finita com furo central, as implementações Elmer FEM e SciPy do [ciclo 13](elmer-fem-independente.md) chegaram a deslocamentos praticamente idênticos quando aplicada a mesma malha Q8. Isso demonstrou concordância na solução discreta, mas não assegurou que o valor do pico de tensão estimado **no contorno** estivesse correto.

Em elementos finitos, uma tensão pontual recuperada do gradiente de deslocamentos não é idêntica à tensão extrapolada a partir de pontos de Gauss. Um ajuste por região (*patch*) é uma terceira técnica possível. A literatura clássica de Zienkiewicz e Zhu discute as oportunidades e as limitações desses procedimentos; **o ajuste ponderado deste laboratório não é uma implementação verificada do SPR de Zienkiewicz–Zhu**.

**Referências técnicas:**

- Zienkiewicz, O. C.; Zhu, J. Z. (1992). [*The superconvergent patch recovery and a posteriori error estimates. Part 1*](https://doi.org/10.1002/nme.1620330702).
- Zienkiewicz, O. C.; Zhu, J. Z. (1992). [*Part 2: Error estimates and adaptivity*](https://doi.org/10.1002/nme.1620330703).
- [Gmsh — documentação oficial de malhas e elementos de segunda ordem](https://gmsh.info/doc/texinfo/).
- [SkyCiv — estudo de concentração de tensões em chapa quadrada](https://skyciv.com/docs/tech-notes/s3d-plate-verification-models/stress-concentration-around-a-hole-in-a-square-plate/). **Atenção:** a geometria, o material, a distribuição de carga e o tipo de elemento desse exemplo **não são integralmente os mesmos** do nosso caso. Serve como referência de abordagem, não como valor de Kt exato para aprovar o modelo.
- [Kirsch — tensão de placa infinita com furo, registro NASA/NACA](https://ntrs.nasa.gov/citations/19930082747). A referência analítica **Kt = 3** não é o resultado exato da chapa quadrada finita aqui estudada.

## 2. Problema físico, mantido idêntico

Usa-se a mesma malha de quadriláteros isoparamétricos Q8, gerada com Gmsh e convertida para Elmer, com primeiro quadrante da chapa \`0 ≤ x,y ≤ H\`, furo \`r=a\` e elasticidade isotrópica em tensão plana:

| Parâmetro | Valor |
| --- | --- |
| Raio \`a\` do furo | 10 mm |
| Meia largura \`H\` da chapa quadrada | 40 ou 80 mm (largura total 80 ou 160 mm) |
| Módulo \`E\` | 200 GPa |
| Coeficiente \`ν\` | 0,30 |
| Espessura equivalente | 5 mm |
| Tração bruta \`T\` | 10 MPa na borda externa \`x=H\` |
| Fronteiras livres | furo e \`y=H\` |
| Simetria | \`Ux=0\` em \`x=0\`, \`Uy=0\` em \`y=0\` |
| Refinamentos | 8×16, 16×32, 24×48; 128, 512, 1.152 elementos Q8 |
| Campo de deslocamentos | **um único resultado nodal Elmer, sem re-solver para cada recuperador** |

Todas as tensões adimensionais são normalizadas pela **tração bruta** \`T\`, não pela tensão nominal da seção líquida. O fator líquido pode ser calculado de forma inequívoca como \`Kt_net=Kt_gross(1−a/H)\`.

## 3. Três formas de estimar a tensão no topo do furo

### A — Gradiente direto no vértice

O elemento Q8 adjacente à interseção \`(x,y)=(0,a)\` fornece \`ε=B u_e\` e \`σ=Dε\`. Nesse ponto \`θ=π/2\`, a tensão tangencial é \`σθθ=σxx\`. Assim \`Kt_A=σxx/T\`. A avaliação **usa a derivada de um único elemento no contorno**. É sensível ao erro do gradiente FE, mesmo quando os deslocamentos de vários solvers coincidem.

### B — Extrapolação de seis coeficientes dos pontos de Gauss

São consideradas três camadas radiais e três células angulares contíguas ao ponto crítico. Em cada elemento, o mesmo vetor de deslocamentos Elmer é diferenciado com \`B\` nos **nove pontos de Gauss Q8 (quadratura 3×3)**. As componentes são convertidas para \`σθθ/T\`, \`σrr/T\` e \`σrθ/T\` e ajustadas com pesos iguais:

\[
s(u,v)=c_0+c_1u+c_2u^2+c_3v^2+c_4uv^2+c_5v^4,
\quad
u=\frac{r-a}{\Delta r_1},\quad
v=\frac{\pi/2-\theta}{\Delta\theta}.
\]

O valor estimado de contorno é \`c0\`. Esse operador não é o mesmo dado de tensão de Gauss impresso anteriormente pelo CalculiX: embora a ideia de extrapolação seja semelhante, o presente estudo usa **todos os Gauss 3×3 calculados a partir dos próprios deslocamentos Elmer**.

### C — Ajuste local de *patch* ponderado

Usa as mesmas amostras geométricas do método B, mas troca a base por quatro termos \`1,u,u²,v²\` e utiliza pesos relacionados ao **jacobiano isoparamétrico, pesos da quadratura e distância ao ponto crítico**:

\[
w_i=\frac{J_i w_{\xi,i}w_{\eta,i}}{1+0{,}15u_i^2+0{,}15v_i^2}.
\]

A estimativa de bordo é também o intercepto do polinômio. Esse procedimento **não é uma projeção L2 global**, não é uma implementação formal do **ZZ-SPR** e não garante superconvergência. O objetivo é verificar como escolhas locais de base e ponderação alteram o pico.

## 4. Verificação analítica sem usar Kirsch como chapa finita

O sistema diferencia dois controles:

- O gradiente direto A é aplicado a **deslocamentos de Kirsch amostrados e interpolados nos nós Q8**. A diferença em relação a 3 mede erro de representação/interpolação sobre o campo infinito conhecido.
- Os operadores B e C são aplicados também às tensões **analíticas de Kirsch nas mesmas coordenadas dos pontos de Gauss**. Isso mede o viés do polinômio sobre uma distribuição conhecida. Não mede o erro total da solução da chapa quadrada finita.

Os operadores são verificados adicionalmente num **campo afim de deslocamentos com tensão cartesiana constante**. Depois de convertida para coordenadas polares, essa tensão constante varia com o ângulo: um ajuste local não deve ser exigido com erro literalmente zero para a tensão circunferencial em todos os pontos.

## 5. Critérios de cálculo e rastreabilidade

O código \`src/engmec/recuperar_tensao.py\` exige campo de deslocamentos completo, integridade da malha, jacobianos Q8 positivos e quantidade mínima de amostras. Rejeita matrizes de regressão sem posto completo ou mal condicionadas e valores não finitos. O banco bruto inclui \`gauss_tensoes.csv\` (coordenadas, tensões cartesianas, tensões polares normalizadas, pesos físicos e marcação de patch) e \`deslocamentos_elmer.json\`.

O dataset consolidado apresenta, por caso, o valor \`Kt\` de cada operador e a diferença entre o mínimo e o máximo:

\[
\Delta K_t=\max(K_{t,A},K_{t,B},K_{t,C})-\min(K_{t,A},K_{t,B},K_{t,C}).
\]

**Essa amplitude não é intervalo de confiança, incerteza expandida, limite físico do erro nem critério de segurança operacional.** É exclusivamente uma análise determinística de **sensibilidade ao pós-processamento** para os três operadores escolhidos.

Registra-se também \`σrr/T\` e \`σrθ/T\` estimados na parede livre e os resíduos dos ajustes. O desvio \`σrr/T≠0\` é um diagnóstico de qualidade do campo recuperado; não se deve confundi-lo com desequilíbrio global das reações.

## 6. Reproduzir

Com Gmsh, ElmerGrid/ElmerSolver, Python 3.12 e os extras \`fem2d\`/\`elmer\`:

\`\`\`bash
python -m pip install -e ".[elmer]"
python -m engmec.elmer_chapa --nr 16 --nt 32 \
  --semilargura-m .04 --saida build/ciclo14/elmer/ha-4-n-16
\`\`\`

O comando preserva a execução externa e escreve, além dos arquivos dos ciclos anteriores, o resumo \`recuperacao.json\`, o CSV dos pontos de Gauss e o JSON de **todos os deslocamentos nodais** do Elmer. Para consolidação, após completar todos os seis casos:

\`\`\`bash
python scripts/avaliar_ciclo14.py --pasta build/ciclo14/elmer
\`\`\`

A automação [ciclo14-recuperacao.yml](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/ciclo14-recuperacao.yml) reproduz o procedimento no Ubuntu 24.04, registrando imagem Elmer e \`pip freeze\`.

## 7. Limitações

O estudo permanece uma chapa quadrada finita de **tensão plana linear-elástica**, sem contato de pino, fadiga, trinca, solda, plasticidade ou validação experimental. O valor **Kt=3** de Kirsch é apenas controle analítico de algoritmo em placa infinita, não prova da solução para a geometria finita. A amplitude de três recuperadores não representa, por si, um limite absoluto da tensão verdadeira. Não utilizar qualquer um desses fatores para liberar manutenção, dimensionar olhais ou aceitar componentes de equipamentos pesados sem um caso material e uma validação apropriada.

## 8. Resultados observados — execução externa 08/11/2026

O [workflow #42502117900](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42502117900) foi **aprovado**. Em seis simulações reais com Elmer FEM, cada solução de deslocamentos foi utilizada sem alteração pelos três recuperadores A/B/C, resultando em 18 estimativas superficiais e todos os dados de Gauss preservados.

| W (mm) | Elementos Q8 | Kt A | Kt B | Kt C | Amplitude |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 80 | 128 | 3,618124 | 3,393224 | 3,348287 | 0,269838 |
| 80 | 512 | 3,588914 | 3,569608 | 3,563842 | 0,025072 |
| 80 | 1.152 | 3,584406 | 3,582520 | 3,581034 | 0,003372 |
| 160 | 128 | 3,213273 | 2,669998 | 2,556529 | 0,656744 |
| 160 | 512 | 3,152512 | 3,065670 | 3,053918 | 0,098594 |
| 160 | 1.152 | 3,139032 | 3,128814 | 3,126387 | 0,012645 |

A amplitude cai **0,269838→0,003372** na chapa W=80 mm e **0,656744→0,012645** na de W=160 mm conforme o número de elementos vai de 128 a 1.152. A redução da dispersão dos métodos com o refinamento é um **diagnóstico de sensibilidade do pós-processamento**, e não um intervalo de confiança, limite de erro absoluto ou demonstração de tensão admissível.

### Viés dos métodos contra Kirsch analítico

O próprio ajuste pode introduzir erro. Na malha grosseira W=160 mm/128 elementos, quando alimentados com as **tensões exatas de Kirsch amostradas nos mesmos Gauss**, os métodos B e C retornaram vieses **−0,474418** e **−0,565631** em Kt. No caso refinado W=160 mm/1.152 elementos, os vieses diminuíram para **−0,007032** e **−0,008965**. Em W=80 mm/1.152 elementos, para B/C foram **−0,000694** e **−0,001740**.

O gradiente A usa **deslocamentos analíticos de Kirsch interpolados em Q8**; os métodos B/C usam **tensões analíticas de Kirsch diretamente nas coordenadas Gauss**. Portanto, o viés de A não é da mesma natureza que o de B/C. Nenhum destes testes reproduz exatamente o campo de uma chapa quadrada finita, nem autoriza corrigir seus fatores por simples subtração do viés.

### Parede livre e discretização

As componentes `σrr/T` deveriam se aproximar de zero na parede livre. Em W=160 mm/128 elementos, A/B/C forneceram aproximadamente **0,2993 / 0,2814 / 0,2713**, e em 1.152 elementos **0,00969 / 0,00703 / 0,00648**. Isso evidencia a presença de erros locais em malha grosseira, apesar da resolução global do sistema de forças.

### Aprendizado de testes

A primeira execução reprovou um teste que exigia valor exato para `σθθ` após conversão de tensão cartesiana uniforme para coordenadas polares, embora o campo varie angularmente. O teste foi corrigido para exigir a reprodução exata no gradiente direto e tolerâncias explícitas para os dois ajustes polinomiais. A execução seguinte passou.

### Evidências brutas

- [Solver e testes especializados aprovados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42502117900).
- [Artefato completo com dados nodais, CSV de Gauss, malhas, VTU e logs](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42502117900/artifacts/13625564700), ID 13625564700; SHA-256 `c89a52b9033b47dc9f4217360266887da632446f981507d9dd8fae214f5c818e`; retenção indicada até **08/12/2026**.
- [Dataset permanente com todos os números e controles](../dados/ciclo14-recuperacao-tensoes-2026-11-08.json).

O benchmark [SkyCiv de chapa quadrada com furo](https://skyciv.com/docs/tech-notes/s3d-plate-verification-models/stress-concentration-around-a-hole-in-a-square-plate/) usa material, malha e distribuição de carregamento diferentes, logo **não é referência numérica exata comparável** para estes valores. A literatura Zienkiewicz–Zhu sustenta a importância da recuperação por patches, mas o método C deste ciclo continua um **ajuste exploratório**, não uma implementação validada de SPR.
