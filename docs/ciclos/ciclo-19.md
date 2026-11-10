# Ciclo 19 — Anel interno Q8 com quatro blocos

**Data:** 09/11/2026. **Versão:** v0.19.0. **Issue:** [#19](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/19). **Laboratório:** [Anel Q8 multibloco](../laboratorios/anel-multibloco-q8.md).

## Problema do ciclo anterior

O ciclo 18 rejeitou a curvatura da interface interna por **jacobianos não positivos** e a distribuição angular de nós por **piora do alongamento junto ao furo e do resíduo de tração livre**. As malhas de dois blocos também apresentavam geometria desfavorável nos cantos externos.

## Arquitetura entregue

\`src/engmec/multibloco_anel.py\` gera **quatro superfícies transfinite** em dois setores angulares e duas regiões radiais: anel \`a≤r≤2a\` e transição até o retângulo. Os arcos intermediários são compartilhados; \`verificar_anel_conforme\` comprova \`n_t\` arestas Q8 de interface com **exatamente duas incidências e o mesmo nó central**, \`n_t+1\` vértices e jacobianos positivos nos pontos avaliados. \`Ni=No=n_r/2\`; anel interno radial uniforme e exterior \`q_o=exp(4/No)\`.

\`src/engmec/elmer_chapa.py\` recebe nova opção opt-in \`--topologia anel-quatro-blocos\`, mantendo \`dois-blocos\` como padrão. Os grupos físicos da face tracionada, topo livre, furo livre e dois eixos de simetria permanecem preservados. A opção experimental exige \`--progressao-radial escalonada\` e distribuição angular uniforme, mas a malha de quatro blocos possui sua **própria lei radial interna e externa**, explicitamente registrada, não devendo reutilizar incorretamente \`q\` da geometria de dois blocos.

\`scripts/avaliar_ciclo19.py\` verifica **16 modelos reais** (d/W=0,25/0,125; L/W=2/4; n=24/32/40/48), Kt A/B/C, jacobianos, geometria, hash MSH2, contornos, equilíbrio SciPy e deslocamentos Elmer×SciPy. A inferência Richardson/GCI continua **condicional**, conforme lógica de quatro níveis do ciclo 16.

## Execução externa

O [workflow #42739742200](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42739742200) concluiu com **todos os jobs aprovados**: *smoke* Gmsh de 16 geometrias Q8, 16 resoluções Elmer em dois grupos e consolidação/publicação do dataset. Não houve elementos Q8 invertidos nas verificações dos pontos de Gauss nem interfaces com nós pendentes.

| d/W | L/W | Máx. 1ª faixa anterior | Novo anel | Máx. global anterior | Novo anel | σrr/T anterior | Novo |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 2.021 | 2.547 | 5.928 | 14.880 | 1.687e-4 | 2.145e-3 |
| 0.250 | 4 | 3.931 | 2.547 | 11.639 | 31.223 | 1.792e-4 | 2.141e-3 |
| 0.125 | 2 | 4.258 | 2.547 | 6.296 | 17.231 | 9.740e-4 | 1.949e-3 |
| 0.125 | 4 | 8.075 | 2.547 | 12.002 | 33.832 | 1.020e-3 | 1.948e-3 |

**Resultado:** melhora do alongamento junto ao furo em **3/4 casos**, sobretudo no retângulo \`d/W=.125,L/W=4\` (8,075→2,547); piora **global em 4/4**, com razões até 33,83. A tensão radial residual \`σrr/T\` também piorou nas **quatro** geometrias, chegando a aproximadamente 12,7 vezes no caso d/W=.25,L/W=2. Os ângulos mínimos externos não foram corrigidos e também pioraram ligeiramente.

O Kt C líquido mudou menos que 0,08% entre malhas de mesmo n. As quatro séries C passaram os gates programados para GCI **condicionado** em torno de 0,10–0,105%, maiores que os do ciclo 17. Portanto, **nem GCI nem estabilidade de Kt justificam promover a malha**.

## Evidências e decisão

- [Dataset permanente](../dados/ciclo19-anel-multibloco-2026-11-09.json), incluindo os 16 modelos FEM, todas as tensões recuperadas e verificadores.
- [Workflow real aprovado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42739742200).
- [Artefato de aproximadamente 60 MB](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42739742200/artifacts/13728029675), ZIP SHA-256 \`845ea858ff3f2093d4dfa0c910d409aa42535fbe1b6240e94f6290577f218af4\`, retenção até 10/12/2026.
- [Manual Gmsh — transfinite surface, quadriláteros recombinados e fronteiras físicas](https://gmsh.info/doc/texinfo/gmsh.html).

**Estado da issue #19:** parcialmente atendida. Topologia anular de quatro blocos, fronteiras, conformidade e 16 FEM reais foram demonstrados; **não** foram atendidos os gates simultâneos de qualidade global, local e superfície livre. Manter aberta. O padrão do programa permanece \`dois-blocos\`.

**Próxima intervenção:** redistribuir blocos externos (6–8 superfícies ou outra estratégia com estudo geométrico de β externo) para evitar concentração do gradiente de tamanhos; manter o anel e avaliar a reação dos três recuperadores e o desvio radial de tração na parede antes de qualquer alteração do default.

**Segurança:** nenhuma evidência física ou autorização de dimensionamento/aceite de estruturas de mina foi obtida.
