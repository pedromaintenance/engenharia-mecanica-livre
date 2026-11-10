# Roadmap de qualidade, revisão e risco

## Três gates independentes

**G1 — Direitos:** URL canônica, titular, status de acesso, confirmação de licença por item, autorização de republicação quando houver conteúdo alheio. Sem aprovação, apenas link e metadados.

**G2 — Engenharia:** símbolos, SI, modelo, hipóteses, domínio de validade, solução de referência, análise de incerteza e teste de extrapolação. Em falhas: diferenciar sintoma, efeito, mecanismo e causa.

**G3 — Produto:** CI, links relevantes, busca, mobile, contraste, integridade de JSON, versionamento e changelog.

## Classes de conteúdo

- **Referência:** portal ou obra catalogada, sem avaliação integral de precisão.
- **Conteúdo original em revisão:** texto autoral incompleto/testes ausentes.
- **Conteúdo revisado:** fonte, equações e aplicações verificadas.
- **Ferramenta testada:** cobertura de referência e limites; sem certificação industrial.
- **Conteúdo depreciado/suspenso:** mudança de edição, falha ou restrição jurídica.

## Indicadores

Taxa de fonte revisada, aderência ao schema, falhas de CI, regressões numéricas, pendências de direitos, links inválidos, velocidade de revisão e incidentes de segurança/privacidade.

## Escalonamento

Quando houver falha de segurança, dado de cliente, copyright ou valor de referência incorreto: retirar/suspender o item, registrar issue, elaborar análise causal e só publicar novo conteúdo com evidência de correção.

**Não há aprovação automática de projeto de engenharia** por um agente ou calculadora.

## Gate de pós-processamento FEM — ciclo 14

Na recuperação do pico `Kt`, comparar os métodos com **mesmos deslocamentos, malha, material e tensão nominal**, distinguindo alteração de solver de alteração de pós-processamento. Em malha grosseira podem existir vieses relevantes do extrapolador mesmo quando o equilíbrio de forças é satisfeito. Exigir teste analítico separado em Kirsch e diagnóstico da tensão radial na parede; nunca divulgar faixa entre métodos como se fosse uma **incerteza física de medição** ou uma margem de aceitação. [Laboratório](../laboratorios/recuperacao-tensoes-furo.md).

## Verificação de domínio — ciclo 15

Na comparação com Peterson/Howland, usar **Kt de tensão nominal líquida**, `Kt_net=(1-d/W)Kt_bruto`, mantendo `d/W=a/Hy` e `L/W=Hx/Hy`. Um ajuste para tira longa não representa referência exata para uma chapa quadrada, e igual número de elementos em geometrias com diferentes L/W **não garante erro local igual**. Verificar seis regressões do caso quadrado, jacobiano Q8 e saldo de forças. Uma aproximação de 0,2% da curva com 1152 elementos não substitui estudo de convergência se a variação entre malhas ainda supera 2%.

## Gate Q8 e estudo assintótico — ciclo 16

Não aprovar GCI só porque duas malhas consecutivas deram Kt próximo de Peterson. Para `n24/32/40/48`, exigir monotonicidade e ordens observadas coerentes. O ciclo 16 alcançou diferença de 0,0011–0,0052% no método C entre n40/48, **mas nenhum dos quatro casos C passou o gate para GCI**. A progressão radial fixa q=1,12 causou aumento da razão entre cordas de alguns elementos com o refinamento; em L/W=4 foi observada razão ~23 e ângulo ~12°. Medir qualidade espacial em paralelo com o erro de tensão e considerar nova topologia antes de inferir regime assintótico. [Laboratório 16](../laboratorios/convergencia-fina-retangulo.md).

## Gate de qualidade heterogênea — ciclo 17

Uma melhora de **47,6–47,8% na pior razão global de cordas** não autoriza concluir que a malha esteja igualmente melhor **junto ao ponto crítico**. Com progressão escalonada, d/W=.125, L/W=4, n48 apresentou pior razão da primeira faixa **4,57→8,07**, mediana 1,12→7,76, e `σrr/T` de `1,7×10⁻⁵→1,0×10⁻³`. Ângulos mínimos globais ~12–13° continuaram idênticos. O GCI condicional do método C em quatro séries mede somente discretização **sob hipótese de regime assintótico do recuperador**; não cobre erro de parede livre, forma de elemento ou dado de material. Exigir **qualidade global + local + tração radial residual + robustez de A/B/C** antes de promover estratégia ao padrão. [Laboratório 17](../laboratorios/progressao-radial-q8.md).

## Gate negativo do ciclo 18 — não otimizar apenas por Kt

A redistribuição angular moderada `qθ^Na=0,7` foi validada geometricamente (jacobianos positivos) e resolvida com Elmer/SciPy em 16 casos, mas **não melhorou os critérios que justificaram a mudança**: primeira faixa do furo ficou ~19% mais alongada nas quatro geometrias n48 e `σrr/T` aumentou. A pior razão global e ângulos mínimos de canto permaneceram iguais. Os quatro recuperadores C mantiveram GCI condicional, sem que isso significasse melhor tração livre ou erro absoluto menor. Uma spline em dois blocos foi rejeitada antes de resolver FEM por jacobianos Q8 inválidos. Manter ambos os resultados negativos documentados; exigir **qualidade global, local, de canto, tração livre e convergência** simultaneamente para promover uma nova malha. [Laboratório](../laboratorios/distribuicao-angular-q8.md).

## Gate multibloco Q8 — ciclo 19

A [v0.19](../laboratorios/anel-multibloco-q8.md) validou 16 geometrias Gmsh Q8 antes de 16 soluções Elmer e verificou que todos os arcos de interface `r=2a` possuem **exatamente dois elementos vizinhos e um nó médio idêntico**. Esse gate protege a conformidade de discretização. Ainda assim, a qualidade de forma global piorou em 4/4 geometrias (até 33,83 na razão das cordas), os ângulos mínimos externos também pioraram, e o resíduo `σrr/T` da parede livre aumentou em todos os casos. **Uma melhor primeira faixa não certifica a malha como um todo.** A aprovação de GCI condicionado no Kt C deve permanecer separada da verificação da tração livre. O próximo gate exige **melhoria simultânea** da transição externa, da parede livre e da primeira faixa para qualquer promoção de topologia. [Dados reais](../dados/ciclo19-anel-multibloco-2026-11-09.json).
