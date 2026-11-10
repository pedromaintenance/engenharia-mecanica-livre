---
name: benchmark-fem
description: Desenvolver e revisar benchmarks de elementos finitos com equilíbrio, solução analítica, estudo de malha, tolerâncias e fronteiras de validade, sem confundir verificação numérica com segurança de projeto.
license: MIT
---

# Benchmark FEM

1. Definir problema de valor de contorno, propriedades, carregamento, geometria e sinal.
2. Identificar uma solução analítica independente ou caso publicado verificável.
3. Discretizar e montar o sistema, explicando funções de forma e cargas nodais consistentes.
4. Conferir condições de contorno; evitar sistema singular e sobre-restrição.
5. Comparar deslocamento, esforços/reação, energia e erros físicos por elemento.
6. Fazer refinamento de malha usando grandeza de erro *não identicamente nula*.
7. Incluir cargas em sentidos opostos, dados inválidos, malhas distintas e limites.
8. Registrar tolerâncias, hipótese linearidade, domínio de validade e o que não foi validado.
9. Se integrar solver externo, fixar versão e distribuição, informar ambiente e repetir estudo independentemente.

**Aceite:** resultados reprodutíveis e relatório de erro; nenhuma declaração de projeto certificado.

## Benchmark externo com CalculiX

Se o caso for C3D8, verificar orientação positiva do elemento, cargas nodais equivalentes à tração, remoção mínima dos modos rígidos e extração de `U` e `RF` do `.dat`. Não confundir teste de parser com execução do CalculiX. Guardar artefatos de solver, versão do binário e resultados; aceitar somente com logs reais e tolerâncias.

## Flexão pura e grandezas de erro não triviais (ciclo 07)

Use tensões não uniformes e uma solução de elasticidade independente, compare deslocamentos em ao menos dois nós distintos, calcule taxa de erro em malhas de resoluções crescentes e confira momentos de face e força resultante. A variável `RF` em CalculiX **inclui CLOAD** no mesmo nó: subtraia o carregamento conhecido antes de interpretar reação. C3D8 tem tendência documentada a rigidez excessiva em flexão; registre locking e erro observado, nunca diminua tolerância arbitrariamente para produzir sucesso. Preserve artefatos, dados e revisão de limites antes de fechar o ciclo.

## Evidência real do ciclo 07

O teste de flexão pura em CalculiX C3D8 2.21-1 apresentou erro relativo inicial 29,7457% e final 0,9942% em Uy, taxas aparentes até 1,76, com prova de execução no workflow #42064616852. Ao continuar, usar o JSON `docs/dados/flexao-pura-3d-2026-11-05.json` como baseline sem confundir benchmark C3D8 com referência de projeto; adicionar C3D20R e pós-processamento de tensões antes de ampliar o domínio.

## Comparação C3D8 × C3D20R (ciclo 08)

Preserve exatamente a mesma solução analítica e condições de contorno; compartilhe midside nodes em arestas comuns, valide conectividade de 20 nós e Q8 com partição da unidade. Integre cargas nodais de faces quadraticamente com Gauss 3×3, sem impor valores iguais por nó. Use *EL PRINT,ELSET=EALL COORD,S e calcule erro da tensão nos pontos de integração (não em nós extrapolados). Compare **erro por DOF e por custo**, reconhecendo variabilidade do hardware e a possibilidade de erros inferiores ao arredondamento da saída textual. A execução externa precisa de logs e artefatos para ser declarada concluída.

## Baseline real do ciclo 08

[Workflow externo aprovado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42411991123) e [JSON com seis medições](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/docs/dados/comparacao-c3d8-c3d20r-2026-11-07.json). Dados por família C3D8/C3D20R: erro de Uy/erro RMS Sxx por ponto de integração, custo em DOFs e tempo de solver. Aprendizados de input: conectividade C3D20R em duas linhas (<=16 entradas por linha); filtrar somente carga Q8 residual de arredondamento, preservando forças/momentos; *EL FILE sem ELSET e *EL PRINT COORD,S. **Não copiar o resultado de desempenho para problemas não lineares**, tensões locais ou materiais diferentes.

## Concentração de tensões — ciclo 09

Quando estudar furo ou entalhe, declarar o **denominador da tensão nominal** de Kt e não confundir tensão em ponto de Gauss interno com pico na superfície. Registrar geometria finita e condições de contorno externas: impor o deslocamento **exato** de Kirsch em arco truncado é útil para verificar discretização, mas **não mede o efeito de largura finita** sob tensão aplicada em uma chapa real. Exigir jacobianos positivos, erro RMS tensorial global e próximo do furo, refinamento local e fonte para a solução. Ao usar CPS8R, respeitar expansão interna do CalculiX, saída de pontos de integração e hipótese de tensão plana.

## Baseline Kirsch CPS8R — ciclo 09

Resultado real em [GitHub Actions](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42415560152); [dados permanentes](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/docs/dados/kirsch-cps8r-2026-11-07.json). Para malha radial graduada, **não tratar média por ponto de Gauss como norma RMS física**: incluir ponderação por área de setor e um anel de geometria fixa para estudar convergência. Guardar a primeira camada como diagnóstico (piorou em n=16). No CalculiX 2.21, quebrar NSET após 16 identificadores, evitar prescrever BC com mantissas muito extensas e **escrever zero exato nos eixos de simetria**, pois resíduos e-18 geraram jacobianos não positivos na expansão CPS8R. Não elevar proxy interior a `Kt` de superfície.

## Benchmark de chapa finita tracionada — ciclo 10

Separar **Kirsch infinito com deslocamento imposto** da **chapa finita com tensão uniforme aplicada nas bordas**. Para estimar Kt, informar os dois denominadores `σnom_bruta=T` e `σnom_liquida=T/(1-d/W)`. Carga de aresta Q8 deve ser integrada consistentemente: `F_ends=F/6`, `F_mid=4F/6`, com soma física `T*t*H` no quadrante. Borda oposta/parte superior/furo livres conforme simetrias. Extrair S e COORD de Gauss e rotular ajustes de tensão na superfície como **extrapolação sujeita a viés**, incluindo comparação do mesmo estimador sobre Kirsch analítico amostrado. Registrar malha/jacobiano, refinamento H/a, custo e falhas reais do CalculiX. Não certificar Kt superficial apenas pelo ajuste.

## Evidências reais do ciclo 10

[Workflow externo #42421310615](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42421310615) e [dataset](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/docs/dados/chapa-finita-furo-2026-11-07.json). Malha n=8/16/24 da placa H/a=4, Kt_gross extrap 3,5798/3,6177/3,6175; outras larguras só n=24 (sem convergência individual). Para cada avanço: registrar geometria, comprimento/largura, tração equivalente, **definição bruta/líquida** e método de extrapolação; não confundir estabilização interna com validação independente de literatura de mesma geometria. Próximo objetivo: malha via Gmsh e comparação de campos de tensão e de concentração com formulação independente.

## Gate de malha independente — ciclo 11

Na comparação Gmsh×autoral, a independência é só de **geração da geometria/malha**; manter física, material, espessura, carga real e element CPS8R no CalculiX. Para `.msh` Gmsh versão 2.2 ASCII, quad8 tem tipo 16 e linha quadrática tipo 8 (nó médio na última posição). Importar com validação de topologia, jacobiano e fronteiras; reindexar elementos no deck `.inp`. O pós-processamento Gauss precisa selecionar amostras geometricamente (IDs Gmsh não preservam ordem polar). Comparar Kt_bruto, Kt_net e viés do extrapolador, sem declarar validação por software FEM independente. Criar logs/artefatos reais e proteger regressões com CI.

## Baseline real Gmsh do ciclo 11

[Workflow aprovado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42422518394), [dados de nove simulações](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/docs/dados/ciclo11-gmsh-chapa-2026-11-07.json). Em iguais 1152 elementos da chapa W=80 mm, Kt bruto extrapolado 3,61471 no Gmsh e 3,61745 no gerador autoral; não zerar artificialmente a diferença. O parser MSH2 exige marcadores literais `$MeshFormat`, `$Nodes` e `$Elements` sem barra invertida; a primeira execução externa mostrou essa falha de serialização e motivou teste de regressão. Gmsh independente de malha não equivale a solver FEM independente. Guardar a família do elemento, espessura, gradiente de malha, contornos e método de pico antes de comparar com resultados de terceiros.

## Baseline ciclo 12 — implementação FEM independente

[Workflow de quatro pares executados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42423510950), [dados auditáveis](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/docs/dados/ciclo12-solvers-independentes-2026-11-07.json). Gmsh MSH2 quad8 idêntico em ambos os solucionadores (SHA256 igual), mesmo problema físico e condição de simetria. O autoral monta B, D e Ke no NumPy/SciPy com 3×3 Gauss e recupera a tensão no contorno por **gradiente de deslocamento**, enquanto o CalculiX usa CPS8R e ajuste dos Gauss. Em cada trabalho exigir teste de partição da unidade, diferenças finitas de derivadas, patch test de campo afim, balanço R+F e diagnóstico de tensão radial livre; não misturar viés de recuperação e erro de solver numa falsa incerteza simples. NumPy/SciPy são extras opcionais; argumentos devem ser validados antes do import para que a suíte básica não dependa deles. **Ainda falta segundo solver FEM externo**, conforme issue #14.

## Gate externo Elmer FEM — ciclo 13

No benchmark FEM da chapa finita, um **segundo solver externo** deve executar a mesma física sob condições de contorno explícitas. No Elmer, `StressSolver` com `Plane Stress = True`, `Force 1=T` em x=H, `Displacement 1=0` em x=0, `Displacement 2=0` em y=0; restante livre. Usar `ElmerGrid 14 2` para MSH2 quad8 e **não presumir que os IDs físicos do Gmsh persistem** na malha convertida: ler `mesh.boundary` e classificar contornos por geometria. Conferir se VTU preserva coordenadas iniciais ou deforma a malha; caso deformado, subtrair deslocamentos e exigir correspondência espacial bijetiva dentro da tolerância, em vez de aumentá-la indiscriminadamente. Comparar com SciPy usando **o mesmo operador B de gradiente**, além de registrar outras técnicas de pós-processamento separadamente. Guarde SIF, VTU, logs, imagem/Docker digest e limites de convergência.

## Recuperação de tensões — ciclo 14, dados reais

[Seis modelos Elmer aprovados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42502117900), [dataset permanente](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/docs/dados/ciclo14-recuperacao-tensoes-2026-11-08.json). Comparação A/B/C somente com **um campo de deslocamentos**, CSV de Gauss completo, jacobianos positivos e controle de condicionamento dos ajustes. B usa seis coeficientes não ponderados; C usa quatro coeficientes com pesos físicos e localidade — **não SPR certificado**. O próprio Kirsch analítico nas posições de Gauss demonstrou viés B/C de −0,474/−0,566 na chapa W160/128 elementos. Manter erro de pós-processamento distinto do erro de discretização e de propriedades físicas. A amplitude de métodos não é incerteza expandida.

## Gate comprimento/largura — ciclo 15

[18 casos Elmer externos](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42522437925) e [dataset real](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/docs/dados/ciclo15-chapas-retangulares-2026-11-08.json). Comparar `L/W=Hx/Hy` com `d/W=a/Hy` constante e tração em x=Hx. Para Peterson/Howland, converter `Kt_bruto→Kt_liquido=(1-d/W)Kt_bruto`; Kirsch infinito **não** equivale a tira de largura finita. Verificar as seis regressões L/W=1, jacobianos e força `T Hy t` constante por série. Em d/W=.125, L/W=4, método C muda **2,9801→3,0477** entre 512 e 1152 elementos, de modo que estar próximo de Peterson **não certifica convergência**.

## Verificação de malha fina — ciclo 16

[12 modelos FEM Elmer](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42525939565), [JSON auditado](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/docs/dados/ciclo16-convergencia-fina-2026-11-08.json). Calcular Kt nos métodos A/B/C sobre **mesmos deslocamentos**, medir jacobianos e forma Q8 nos elementos próximos do furo e no domínio todo, preservar `n24/32/40/48`. Richardson/GCI **somente** com quatro valores, monotonicidade, ordem observada plausível e estabilidade entre dois tripletos; caso contrário gravar `GCI=null` e justificar. A diferença pequena entre n40/48 **não** certifica erro absoluto, especialmente com progressão radial q fixa e razão de cordas até ~23 em L/W=4. Corrigir geometria do modelo antes de extrapolar resultados para olhais reais.

## Ciclo 17 — comparar políticas de progressão Gmsh

[16 execuções Elmer aprovadas](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42546868607) e [dataset integral](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/docs/dados/ciclo17-malha-radial-2026-11-08.json). Política atual `q=1,12`; alternativa `q(n)=exp(24ln(1,12)/n)`, com n24 **idêntico por SHA256** ao legado e contornos inalterados. Calcular métricas **globais e da primeira faixa**, jacobianos, ângulos e tração radial livre. Mesmo com redução global da pior razão de cordas ~48% e GCI condicional C aprovado nas quatro séries, d/W=.125,L/W=4,n48 teve piora da primeira faixa 4,57→8,07 e da tensão residual radial em aproximadamente 59 vezes. **A boa solução global não garante tensão de parede precisa**; registrar divergências A/B/C e manter alternativa como opt-in até redesenhar a distribuição angular/topologia local.

## Ciclo 18 — rejeitar alterações de malha que piorem a parede livre

[16 casos Elmer/SciPy](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42550543935), [dados integrais](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/docs/dados/ciclo18-angular-2026-11-08.json). A alternativa angular `qθ^Na=.7` nas curvas `{-5,7}` aumentou ~19% o alongamento máximo da primeira faixa e piorou `σrr/T` nas quatro geometrias, apesar de preservar jacobianos positivos, Kt quase constante e GCI C condicional. Não promover a opção `ampliada-topo` a default. O ensaio anterior de interface `Spline(3)` foi interrompido na verificação de jacobianos Q8 não positivos: jamais calcular ou divulgar Kt de malha invertida. Registrar falhas, tolerâncias, logs e hashes, e priorizar nova topologia multibloco para a faixa anular de furo.

## Ciclo 19 — malha Q8 multibloco conforme

[Workflow 16 FEM externos aprovado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42739742200) e [dataset de 16 modelos](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/docs/dados/ciclo19-anel-multibloco-2026-11-09.json). Ao criar anéis internos, **validar a conformidade exata das interfaces**: `nt` arestas compartilhadas, `nt+1` vértices, incidência 2 e mesmo nó médio de Q8; verificar grupos físicos únicos e jacobianos positivos. **Não confundir melhora no anel com melhora de todo o domínio**: `a≤r≤2a` reduziu a pior razão perto do furo em 3/4 casos, mas o bloco externo piorou a pior razão global em 4/4 até 33,83 e o resíduo `σrr/T` cresceu em todos. A topologia é opt-in, nunca promover a default sem melhorar global, local, ângulo e parede livre. GCI do Kt não é critério de integridade ou segurança.
