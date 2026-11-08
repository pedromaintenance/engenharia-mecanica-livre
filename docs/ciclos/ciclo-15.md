# Ciclo 15 — Comprimento versus largura de chapas perfuradas

**Data:** 08/11/2026. **Versão:** v0.15.0. **Issue:** [#16](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/16).

## Problema herdado

Os ciclos 10–14 resolviam **chapa quadrada** com furo central. A curva Peterson para chapa de largura finita sob tração é, entretanto, uma referência de **tira suficientemente longa**. A geometria de \`L/W=1\` e a de \`L/W≫1\` não possuem necessariamente o mesmo campo de tensões no furo, mesmo que o diâmetro \`d\`, a largura transversal \`W\` e a carga bruta \`T\` sejam iguais.

## Objetivo e decisões

Generalizar a malha Gmsh de dois blocos para \`L=2Hx\`, \`W=2Hy\`, mantendo tração nas faces \`x=±Hx\` e contornos livres \`y=±Hy\` e no furo. Estudar \`L/W=1,2,4\` com \`d/W=0,25,0,125\` e três refinamentos Q8 (128, 512 e 1.152 elementos). O caso quadrado **precisa reproduzir o baseline anterior** em todos os seis pares de largura/refinamento.

Referenciar a curva Peterson pela **tensão líquida**, e reportar também a base bruta sem misturar denominadores.

## Entregas de código

- \`src/engmec/chapa_retangular.py\`: geometria de duas semidimensões Gmsh, quadrado preservado byte a byte, ajuste Peterson líquido/bruto com validação de entradas.
- \`src/engmec/gmsh_chapa.py\`: importador MSH2 reconhece opcionalmente a face x=Hx e mantém o topo y=Hy, protegendo a detecção da carga física.
- \`src/engmec/fem2d_indep.py\`: o solver SciPy passa a aceitar extensão x independente e mantém a força \`F=T·Hy·t\`.
- \`src/engmec/elmer_chapa.py\`: CAD alternativo, ElmerGrid e BCs da geometria retangular, quatro deslocamentos de referência com \`x=Hx\` e três recuperadores do ciclo 14 sobre o mesmo campo Elmer.
- \`tests/test_chapa_retangular.py\` e \`tests/test_aval_ciclo15.py\`: integridade CAD, regressão quadrada, validação Peterson e falha explícita sem resultados externos.
- \`.github/workflows/ciclo15-retangulo.yml\`: 18 execuções externas com logs/digest e backup de todos os dados brutos.
- \`scripts/avaliar_ciclo15.py\`: exige 18 casos, rejeita falta de arquivos, jacobiano negativo, inconsistência de número de Gauss, Kt inválido, regressão do quadrado e campos sem equilíbrio SciPy; consolida sensibilidade e curvas.
- [Laboratório 15](../laboratorios/chapa-retangular-comprimento.md): fundamentos, resultados, fontes e limites.

## Execução real e resultados

O [workflow externo #42522437925](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42522437925) concluiu com **18 casos aprovados**. Os cinco workflows de comparação histórica (ciclos 11–14 e o 12) também passaram novamente após a mudança de código comum; a suíte de qualidade geral foi aprovada.

### Resultados finos, recuperação C e Kt na seção líquida

| d/W | L/W=1 | L/W=2 | L/W=4 | Referência Peterson — tira longa |
| ---: | ---: | ---: | ---: | ---: |
| 0,25 | 2,685776 | 2,438535 | 2,434541 | 2,420328 |
| 0,125 | 2,735588 | 2,668119 | 2,666769 | 2,661814 |

Em \`L/W=4\`, a diferença relativa com a curva de Peterson foi +0,587% (\`d/W=0,25\`) e +0,186% (\`d/W=0,125\`), usando 1152 elementos Q8 e recuperação C.

**Contraponto importante:** para \`d/W=0,125,L/W=4\`, a estimativa C ainda varia de **2,980114 para 3,047736** (base bruta) entre 512 e 1.152 elementos: **~2,27%**. Essa sensibilidade não permite declarar convergência assintótica ou afirmar exatidão física só porque a curva externa está próxima.

### Regressão e qualidade

Todas as seis combinações \`L/W=1\` reproduziram os respectivos Kt de gradiente direto do ciclo 14 dentro de \`1e-7\`, em sequência geométrica idêntica. Os jacobianos Q8 foram positivos e o equilíbrio do solver autoral permaneceu em resíduos muito pequenos, registrados no dataset.

O refinamento mudou não só a resolução, mas também o formato dos elementos; mesmo \`nr,nt\` não garante idêntico erro em \`L/W=1\` e \`L/W=4\`.

## Fontes e limites de comparabilidade

- [Peterson na documentação Ansys PyMAPDL](https://mapdl.docs.pyansys.com/version/stable/examples/gallery_examples/00-mapdl-examples/2d_plate_with_a_hole.html).
- [Wang et al. 2019, *Materials*](https://pmc.ncbi.nlm.nih.gov/articles/PMC6384607/): relação L/W, referência de tira longa e limitações da comparação.
- [MathWorks — placa com furo, tensão plana e tração remota](https://www.mathworks.com/help/pde/ug/stress-concentration-in-plate-with-circular-hole.html).

Os resultados são **educacionais e numéricos**. A aproximação da tira de Peterson não é ensaio da chapa real nem avaliação de fadiga, pinos ou contato. Próximo ciclo recomendado: **refinamento orientado pela qualidade dos elementos e recuperação superficial nas chapas mais longas**, com estudo de erro de discretização/condição de contorno e referência comparável.
