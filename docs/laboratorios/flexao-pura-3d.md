# Laboratório 07 — Flexão pura tridimensional e convergência não trivial

**Objetivo:** superar o *patch test* axial homogêneo da [v0.6](calculix-3d.md), introduzindo um campo de **tensão axial não uniforme na altura**, com solução **exata da elasticidade 3D**, e confrontando os deslocamentos obtidos pelo CalculiX.

**Estado da v0.7:** a implementação e o workflow foram estruturados; resultados numéricos somente serão reportados aqui depois de conferidos nos logs da execução.

## 1. Problema físico e parâmetros

Uma barra prismática de seção quadrada está submetida a **flexão pura** em torno do eixo z. O comprimento está no eixo x, a altura no eixo y e a largura no eixo z. As quatro faces laterais são livres; nas duas faces extremas, impõem-se tração axial linear em y, de sinais opostos, que cria momentos iguais e contrários e força resultante nula.

| Variável | Valor | Significado |
| --- | ---: | --- |
| L | 0,20 m | comprimento em x |
| b | 0,10 m | lado da seção quadrada |
| E | 200 GPa | módulo elástico |
| ν | 0,30 | coeficiente de Poisson |
| κ | 0,01 m⁻¹ | curvatura de referência |
| I_z | b⁴/12 | segundo momento de área |
| M_z | EκI_z ≈ 16.666,67 N·m | momento aplicado em cada extremidade |
| σ_xx | −Eκy | tensão axial, varia linearmente com y |
| |σ_xx|max | 100 MPa | tensão nas fibras extremas |

O momento é equilibrado por um campo de **trações distribuídas**, representadas no arquivo CalculiX `.inp` por forças nodais consistentes calculadas com **quadratura de Gauss 2×2 por face**. Trata-se de aplicação estritamente didática em pequenas deformações.

## 2. Solução da elasticidade — referência independente

Para um sólido homogêneo, isotrópico, elástico linear e sem forças volumétricas, um campo de deslocamentos que satisfaz as equações de equilíbrio e as superfícies laterais livres é:

```text
u_x(x,y,z) = -κ x y

u_y(x,y,z) = κ x²/2 + νκ (y² - z²)/2

u_z(x,y,z) = νκ y z
```

As deformações correspondentes são `ε_xx=-κy`, `ε_yy=ε_zz=νκy`, com deformações cisalhantes nulas. A lei de Hooke isotrópica resulta em `σ_xx=-Eκy` e demais componentes de tensão nulas.

Duas observações de referência, utilizadas como métricas independentes:

- **Deslocamento transversal na linha neutra, centro da ponta:** `u_y(L,0,0)=κL²/2=+0,200 mm`.
- **Deslocamento longitudinal na borda superior da ponta:** `u_x(L,b/2,0)=-κLb/2=-0,100 mm`.

A derivação não usa a solução numérica do CalculiX. A distribuição linear de tensões caracteriza flexão pura; o campo de deslocamentos inclui também as deformações transversais associadas a Poisson.

## 3. Condições de contorno e carregamentos

As trações satisfazem `t_x=σ_xx n_x`. Na face de x=0, `n_x=-1`; na face x=L, `n_x=+1`. A integração consistente gera forças nodais sem substituir a distribuição linear por força concentrada.

O problema é puramente de Neumann, exceto por seis graus de liberdade fixados para remover modos de corpo rígido. Foram escolhidos três nós da face esquerda cujos deslocamentos prescritos **são exatamente nulos no campo analítico**:

- Nó central da raiz: `U1=U2=U3=0`.
- Nó superior da raiz, com z=0: `U1=U3=0`.
- Nó lateral da raiz, com y=0: `U1=0`.

Isso impede translações e rotações rígidas sem impor engaste completo ou bloquear indevidamente a contração transversal de Poisson.

**Atenção à interpretação de RF:** em `*NODE PRINT`, o CalculiX informa forças externas nodais que podem **incluir CLOAD aplicada no mesmo nó**. O parser subtrai essas cargas nos nós de ancoragem antes de calcular a reação resultante. Não confundir o balanço da carga prescrita (conhecido pelo gerador) com a soma das reações obtidas do solver.

## 4. Malha, método e vulnerabilidade conhecida

Elementos hexaédricos lineares **C3D8**, com integração completa. As malhas são `n×n×n` para `n=2,4,8,16`, produzindo 8, 64, 512 e 4.096 elementos.

A [documentação do CalculiX](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node28.html) ressalta que C3D8 **pode ficar excessivamente rígido em flexão**. Portanto, o comportamento da malha é parte da investigação, não algo a esconder ou corrigir arbitrariamente. Se o erro não cair, isso indica limitação do elemento/malha ou um problema da formulação, sujeito a diagnóstico. Um próximo ciclo poderá comparar com C3D20R.

As métricas primárias são os erros relativos em `u_y(L,0,0)` e `u_x(L,b/2,0)`. O relatório inclui taxas aparentes `p=log(e_h/e_{h/2})/log(2)` quando ambos os erros são mensuráveis. A força resultante nas duas faces é zero, e seus momentos opostos são verificados **antes do solver**, independentemente da FEM.

## 5. Executar localmente

Gerar o deck sem instalar o solver:

```bash
python -m engmec.flexao_calculix --nx 4 --ny 4 --nz 4 --somente-gerar --saida build/flexao-calculix/n-4
```

Executar com `calculix-ccx` no PATH:

```bash
python -m engmec.flexao_calculix --nx 4 --ny 4 --nz 4 --saida build/flexao-calculix/n-4
```

O [workflow externo dedicado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/flexao-calculix.yml) instala o CalculiX no Ubuntu 24.04, resolve as quatro malhas e chama:

```bash
python scripts/avaliar_convergencia.py --pasta build/flexao-calculix --malhas 2 4 8 16
```

O relatório `resumo_convergencia.json` exige **erro inicial mensurável**, redução mínima de 25% entre primeiro e último refinamento para ambas as métricas e resíduo relativo de forças abaixo de 1%. Esses são critérios didáticos iniciais e não tolerâncias de projeto industrial.

## 6. Testes, limitações e atividades seguintes

Os testes independentes cobrem referência analítica, soma das forças, equilíbrio de momentos, seis restrições, seleção dos nós e tratamento do arquivo de saída. A execução real do CalculiX e a demonstração de tendência numérica dependem do workflow.

Mesmo que a execução seja aprovada, **verificação computacional não equivale a validação experimental**. Permanecem fora deste problema: concentrações locais, apoio de máquina real, flambagem, juntas, defeitos, soldagem, fadiga, plastificação e geometria não linear.

**Fontes para aprofundar:** [Solução de flexão pura em elasticidade, material MIT 16.20](https://web.mit.edu/16.20/homepage/4_ElasticityBVP/ElasticityBVP_files/module_4_no_solutions.pdf); [Wiley — *Beams in Bending*, solução de elasticidade](https://catalogimages.wiley.com/images/db/pdf/Z0471381527.01.pdf); [Manual CalculiX, C3D8](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node28.html); [`*NODE PRINT` e RF](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node307.html). A dedução, os dados do exemplo e o código são originais do projeto.
