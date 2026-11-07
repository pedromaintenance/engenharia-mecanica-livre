# Laboratório 11 — Malhas independentes Gmsh × autoral

**Objetivo:** confrontar dois **geradores de malha diferentes** aplicados ao mesmo problema físico — chapa quadrada de tensão plana com furo central e tração uniforme nas bordas — usando o **mesmo solver CalculiX**. Paralelamente, ampliar o estudo de refinamento para as chapas mais largas H/a=8 e 16, que tinham uma única malha no ciclo 10.

> Estado inicial: implementação preparada, à espera de saída observada do CalculiX/Gmsh. A comparação não é uma validação por dois códigos FEM independentes, pois o solver, os elementos CPS8R e o estimador de pico continuam iguais.

## 1. Hipóteses físicas compartilhadas

- Chapa quadrada, primeiro quadrante calculado: \`0≤x≤H\`, \`0≤y≤H\`, furo de raio \`a=10 mm\` no centro.
- Elasticidade isotrópica linear, **tensão plana**, \`E=200 GPa\`, \`ν=0,30\`, \`t=5 mm\`.
- \`T=10 MPa\` nas faces externas verticais (no quarto de chapa: apenas \`x=+H\`). Borda superior \`y=H\` e furo livres; \`Ux=0\` em \`x=0\`, \`Uy=0\` em \`y=0\`.
- Tração convertida em cargas nodais consistentes nos segmentos de aresta Q8 com pesos **1/6,4/6,1/6**.
- Contorno do furo de raio \`a\` e borda externa \`x=H\`/\`y=H\`. A carga do quarto é sempre \`F=T·H·t\`.
- **CalculiX CPS8R** em ambas as origens de malha; picos calculados por extrapolação de tensões nos pontos de Gauss, não diretamente sobre o contorno.

O [Laboratório 10](chapa-finita-furo.md) traz a derivação dos fatores de concentração baseados em seção bruta e líquida. A solução \`Kt=3\` de Kirsch infinito não é solução exata desta chapa quadrada finita.

## 2. Os dois geradores

| Propriedade | Gerador autoral (ciclo 10) | Gerador independente Gmsh (ciclo 11) |
| --- | --- | --- |
| Geometria | malha Q8 mapeada por coordenadas polares até o quadrado | duas superfícies CAD, separadas na diagonal \`θ=45°\` |
| Campo da malha | fórmula autoral \`r_i=a+(R(θ)−a)(i/nr)^2\` | algoritmo **Transfinite Surface**, superfícies recombinadas |
| Concentração radial | potência radial \`g=2\` | progressão geométrica do Gmsh, padrão \`q=1,12\` |
| Nós de ordem superior | mids de aresta autorais | nós de ordem 2 emitidos pelo Gmsh |
| Elemento final | CalculiX CPS8R | **Gmsh quad8 tipo 16** → CalculiX CPS8R |
| Qualidade | jacobiano isoparamétrico Q8 verificado | importador MSH2 verifica Q8 em todas as células |
| Condição física | tração na borda externa | **mesma carga física e mesma elasticidade** |

A divisão em duas superfícies CAD evita que elementos de ordem 2 cruzem a mudança brusca de direção do contorno quadrado. O arquivo original \`.geo\`, a malha \`.msh\`, o \`.inp\` e os arquivos de solução são guardados como artefatos do workflow.

**Documentação oficial do Gmsh:** [algoritmo transfinite, recombinação e progressão de curva](https://gmsh.info/doc/texinfo/); [opção \`Mesh.SecondOrderIncomplete\` para quadriláteros de oito nós](https://gmsh.info/doc/texinfo/gmsh.html). O formato escolhido é MSH2 ASCII para permitir leitura independente da API Gmsh em Python.

## 3. Importação e verificação

O importador \`src/engmec/gmsh_chapa.py\` lê os nós, os segmentos quadráticos (tipo 8) e os quadriláteros de oito nós (tipo 16). Rejeita elementos de outra família, malha com número incorreto de elementos ou contornos incompletos; normaliza resíduos de coordenadas próximas de zero nos eixos, comportamento observado no ciclo 09.

A malha deve conter apenas elementos Q8 de ordem 2. As arestas de tração são detectadas por \`x=H\` para todos seus três nós (extremos e mid); a aresta superior é reconhecida por \`y=H\`. O gerador exige **qualidade positiva** nos pontos de Gauss dos elementos quadráticos.

## 4. Controle da tensão máxima extrapolada

O pós-processamento usa **o mesmo ajuste polinomial local de seis coeficientes** do ciclo 10. Como as numerações dos elementos Gmsh e autoral são diferentes, os pontos de integração são selecionados por coordenadas, considerando:

- primeiras três camadas radiais, determinadas pelos níveis das arestas de simetria da própria malha Gmsh;
- últimas três células angulares próximas de \`θ=90°\` a partir do bordo do furo;
- extrapolação do campo \`σθθ/T\` até \`r=a,θ=90°\`.

A origem da malha **não** determina o valor de tensão: são os resultados de \`S\` e \`COORD\` calculados pelo mesmo CalculiX, e o ajuste deve ser identificado como estimativa.

Uma verificação de software aplica esse extrapolador a pontos obtidos do **campo analítico Kirsch**, e reporta seu desvio de \`Kt=3\`. Isso não mede o erro da chapa finita. Os fatores bruto e líquido são apresentados como:

\[
K_{t,\mathrm{bruto}}=\sigma_{\mathrm{pico,estimada}}/T,\qquad
K_{t,\mathrm{líquido}}=(1-d/W)K_{t,\mathrm{bruto}}.
\]

## 5. Execução do experimento

Instalar \`gmsh\` e \`calculix-ccx\` em Ubuntu 24.04. Sem nenhum desses softwares, ainda é possível criar o arquivo CAD externo:

\`\`\`bash
python -m engmec.gmsh_chapa --nr 24 --nt 48 --saida build/ciclo11/gmsh/ha-4-n-24 --somente-geo
\`\`\`

Com ambos instalados:

\`\`\`bash
python -m engmec.gmsh_chapa --nr 24 --nt 48 --semilargura-m .04 --saida build/ciclo11/gmsh/ha-4-n-24
\`\`\`

O [workflow do ciclo 11](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/ciclo11-gmsh.yml) prevê **nove casos**: seis malhas autorais (H/a=8 e 16; n=16,24,32) e três malhas Gmsh (H/a=4 n=16 e 24; H/a=8 n=24). O consolidado usa dados reais do ciclo 10 como baseline para comparar a nova execução.

O script de análise \`scripts/avaliar_ciclo11.py\` registra as diferenças brutas/líquidas, o refinamento por largura e o controle analítico do extrapolador. Se a diferença entre geradores exceder o critério preliminar ou o Gmsh falhar, **o pipeline reprova**: isso exige investigação, não mudança arbitrária da tolerância para forçar sucesso.

## 6. Limitações e próximos passos

A independência deste ciclo é **do gerador de malha**, não das equações constitutivas, formulação CPS8R, solver ou pós-processamento. Portanto, concordância numérica não substitui verificação em software FEM diferente, solução analítica adequada à geometria finita ou validação por ensaios.

As malhas têm distribuição distinta de nós junto ao furo: o mesmo número de elementos não garante mesmo erro ou mesmo custo. A comparação deve apresentar não só a diferença entre Kt como também a qualidade mínima dos elementos, os nós e os resíduos de ajuste.

Mesmo com bons resultados, a aplicação a olhais ou chapas reais depende de carga, material, contato, plasticidade, fadiga e geometria concreta. **Nenhum resultado deste laboratório autoriza reparo, solda, modificação ou liberação de máquina.**
