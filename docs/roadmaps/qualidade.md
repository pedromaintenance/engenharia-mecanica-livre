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
