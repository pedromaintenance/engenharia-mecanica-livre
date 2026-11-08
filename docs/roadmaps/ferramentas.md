# Roadmap de ferramentas computacionais

## T0 — Base verificada

Já existem calculadoras didáticas: potência de eixo, força ideal de cilindro, disponibilidade inerente e viga biapoiada. Não são memórias de cálculo de projeto final.

## T1 — Garantias numéricas

Introduzir Pint (conversão e dimensões), testagem de sinais, infinidades, unidades, casos-limite e tolerâncias. Padronizar respostas JSON com `modelo`, `entradas_si`, `resultados_si`, `hipoteses`, `limites` e `referencias`.

## T2 — Máquinas e materiais

Novos módulos: vazão e potência hidráulica; Reynolds e perdas distribuídas; condução 1D; flexão/torção; vibração SDOF; engrenagens (cinemática); confiabilidade e Weibull, separando parâmetros estimados e medidos.

## T3 — Propriedades e simulação

CoolProp como extra opcional com validação de estado termodinâmico; FreeCAD + Gmsh + CalculiX como pipeline estrutural; OpenFOAM em ambiente isolado para casos de referência; OpenModelica para dinâmica. Nenhum solver incorporado sem análise de licença.

## T4 — Validação experimental e quantitativa

Benchmarks com solução analítica e referências públicas; erros absolutos/relativos, critérios de convergência e relatório reproduzível. Resultados de CAE sem convergência e condições de contorno verificadas ficam marcados como demonstração.

## T5 — Interface

CLI estável, notebooks didáticos e visualizações web acessíveis. APIs sempre versionadas e independentes de execução externa desnecessária.

**Gate:** cada módulo precisa de definição matemática, fonte, teste independente, unidades, exceções, limitações e indicação de não uso para liberação de segurança.

**Progresso ciclo 04:** modelos didáticos de potência hidráulica, condução plana, frequência natural SDOF e número de Reynolds foram adicionados. Não são simuladores multifísicos nem dimensionamento industrial certificado.

## Ciclo 05 — primeiro benchmark FEM

Foi implementado solver tridiagonal 1D para barra elástica, carga de ponta e força distribuída; inclui comparação com solução fechada, reações, energia e erro RMS de tensão com refinamento `O(h)`. O caso possui deslocamento nodal exato, portanto essa variável isolada não comprova convergência. Pendente integração com CalculiX (ou equivalente), benchmarks 2D/3D, avaliação de condições de contorno reais e estudo de convergência independente.

## Ciclo 06 — Conexão com CalculiX externo

Adaptador C3D8 gerado: malha estruturada 3D, restrições mínimas para manter contração de Poisson, força de face distribuída, parser `.dat` e comparação com solução analítica/solver 1D. Workflow separado instala a versão do pacote `calculix-ccx` disponível no Ubuntu 24.04 e testa quatro malhas. A integração externa deve ser marcada **validada** apenas após workflow e logs do solver reais aprovados. Pendência principal depois disso: benchmark 3D com gradiente não trivial e estudo de malha, não só patch test homogêneo.

**Confirmação do ciclo 06:** workflow [CalculiX](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42055701419) passou com o binário 2.21-1 e gerou resultados reais para 4 malhas. [Relatório](../laboratorios/calculix-3d.md) e [evidência JSON](../dados/calculix-c3d8-2026-11-05.json). Ferramenta agora integrada como adaptador de benchmark **opcional**; FreeCAD, Gmsh e casos não lineares continuam planejados.

## Ciclo 07 — flexão não homogênea

Novo benchmark de elasticidade tridimensional: tensão axial proporcional à coordenada transversal, carga de face variável e referência de deslocamentos quadráticos. A comparação com CalculiX é estruturada para medir erro **não trivial** e taxa aparente de convergência, evitando que um patch test exato seja interpretado como validação geral. O manual do CalculiX alerta para rigidez excessiva do C3D8 em flexão; se a convergência for ruim, relatar o problema em vez de forçar a tolerância ou esconder malhas. Próximo passo: elementos quadráticos e comparação de tensões com dados analíticos de pontos de integração.

**Resultados do ciclo 07:** fluxo de flexão 3D C3D8 validado em CalculiX 2.21-1. Na solução analítica adotada, o erro de Uy da ponta caiu de 29,7457% (8 elementos) para 0,9942% (4096 elementos), com melhora consistente e erro numérico não trivial. Reações corrigidas por cargas concentradas nos nós de apoio. [Resultado e metodologia](../laboratorios/flexao-pura-3d.md). Próximo benchmark: C3D20R e tensões por elemento.

## Ciclo 08 — precisão de campo e custo numérico

C3D8 com funções trilineares e C3D20R com funções serendipidade quadráticas são comparados no mesmo domínio de flexão. Desenvolvido gerador de midside nodes compartilhados e tração nodal consistente via Gauss 3×3 para face Q8; o pós-processamento solicita tensões `S` e coordenadas `COORD` em IP pelo `*EL PRINT`, em vez de extrapolação nodal. São métricas de comparação o erro relativo de deslocamentos, RMS das tensões axiais e das outras componentes, número de nós/DOFs, resíduo de reação e tempo medido do solver. Nenhum aumento de fidelidade elimina a necessidade de validação em campo.

**Comparativo ciclo 08 confirmado:** C3D8 × C3D20R no mesmo domínio de flexão; tensões de Gauss extraídas por `COORD,S`. O erro RMS Sxx do C3D8 decaiu de 15,885 MPa para 1,843 MPa com 8→512 elementos; no C3D20R foi ~10 Pa→0,707 Pa, limitado pela precisão numérica/textual. C3D20R usa mais nós/DOFs. [Análise detalhada](../laboratorios/comparar-elementos-fem.md). Implementação de geometria com furos/entalhes e avaliação de gradientes locais continua aberta.

## Ciclo 09 — geometria e pós-processamento de furo

Gerador Q8 polar independente de Gmsh, jacobiano positivo em quatro pontos por elemento, arcadas quadráticas e refinamento radial para furo livre; aplicação exata de deslocamentos Kirsch em arco externo e leitura de `COORD,S` nos Gauss de CPS8R. Workflow dedicado em Ubuntu 24.04 executa 3 malhas e um raio externo alternativo. As métricas de erro tensorial e aproximação interior de tensão circunferencial não se confundem com Kt superficial. Próximos gates: geometria retangular finita, tensão remota aplicada fisicamente, extrapolação controlada e ferramenta Gmsh opcional.

**Ciclo 09, verificação real:** CPS8R + malha polar Q8 curva executados no CalculiX 2.21-1; as regras de formatação de NSET, prescrição de deslocamento e coordenadas em eixos foram incorporadas como aprendizados. [Resultados observados](../dados/kirsch-cps8r-2026-11-07.json) incluem RMSE global ponderado por área, faixa física fixa e o alerta de não monotonicidade no erro da primeira camada. Próximos gates: norma de erro com jacobianos integrais por ponto, distribuição física real de carregamento em chapa finita e pós-processamento superficial controlado.

## Ciclo 10 — aplicação física de tração e estimativa superficial

Malha quadrática mapeada de coroa radial a quadrado externo; canto alinhado com uma linha angular. Borda x=H recebe força equivalente de tração constante T: pesos Q8 de 1/6,4/6,1/6 por segmento. Em `*EL PRINT COORD,S`, o parser recupera tensões em Gauss e ajusta σθθ/T por mínimos quadrados em três camadas radiais e três células angulares para estimar o valor em (a,90°). Avalia viés do estimador no campo analítico Kirsch; o contorno físico de chapa finita é distinto. Estudo de cinco casos automatizado com workflow CalculiX separado.

**Ciclo 10 — implementação verificada:** modelo CPS8R de chapa quadrada finita sob tração real `*CLOAD` na borda, contornos livres e simetrias, com análise de influência `d/W`. [Dados observados](../dados/chapa-finita-furo-2026-11-07.json). A tensão máxima é **extrapolada** com polinômio local, não obtida diretamente no bordo; o ajuste foi testado separadamente com Kirsch analítico. Integração Gmsh e validação independente da malha permanecem como próximas atividades.

## Ciclo 11 — Gmsh em comparação auditável

Integração CLI Gmsh opcional para gerar duas superfícies transfinite, recombinadas em quadriláteros com oito nós (MSH2 tipo 16), preservando curva de furo e quina do quadrado. Importação checa nós, contornos, jacobiano Q8; tração real mantém carregamento Q8, simetrias e material do modelo autoral. O mesmo CalculiX resolve as malhas. Converter tensões nos pontos Gauss para estimação de Kt bruto e líquido; apresentar sensibilidade a n e largura. Próximas ferramentas: independência de solver, contato e qualidade de tensão superficial.

**Workflow de Gmsh validado:** [9 casos externos no CCX](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42422518394) e [dados permanentes](../dados/ciclo11-gmsh-chapa-2026-11-07.json). A implementação importa MSH2 quad8 e segmentos de borda quadráticos, verifica jacobianos e força integrada, compara Kt por extrapolação com o gerador autoral, e registra divergências não nulas. O próximo passo em ferramentas é independência de **solver** e comparação de técnicas de recuperação de tensão superficial, não apenas outra malha.

## Ciclo 12 — Segundo solucionador FEM e recuperação independente

Implementado `src/engmec/fem2d_indep.py` com Q8 serendipidade, derivadas analíticas verificadas numericamente, `D` de tensão plana, montagem COO/CSR SciPy, resolução com `spsolve`, reações, tensão radial/cisalhante e recuperação direta `σ=D B u_e` no nó de parede do furo. Em quatro pares H/a=4/8 e n=16/24, as malhas `.msh` **coincidiram em SHA256** com os arquivos do CalculiX; [workflow](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/ciclo12-dois-solvers.yml) e [dataset](../dados/ciclo12-solvers-independentes-2026-11-07.json) registram os resultados, sem inferir exatidão. Próximo estágio: Elmer ou solver independente já estabelecido e pós-processamento de gradiente/superfície com análise de incerteza.

## Ciclo 13 — Integração Elmer FEM/ElmerGrid

Novo adaptador `src/engmec/elmer_chapa.py`: atribui grupos físicos ao CAD Gmsh, converte MSH2 Q8 por ElmerGrid, reconcilia IDs de contorno **pelas coordenadas** e gera `case.sif` do StressSolve em tensão plana. O ElmerSolver resolve independentemente, salva `VTU`; o pós-processamento reconcilia nós com tolerância física e corrige eventual geometria deformada, identificando essa transformação no JSON. Confronto de **deslocamentos de quatro pontos e Kt por gradiente direto comum** ao FEM SciPy. Executa em contêiner externo [Elmer 0.2.0](https://docs.femforge.io/user-guide/elmer/) com digest registrado. A compatibilidade de outra implementação não certifica fator de concentração para componente real.

## Ciclo 14 — três estimadores sobre a mesma solução Elmer

`src/engmec/recuperar_tensao.py` implementa gradiente direto (A), ajuste local de tensões nos pontos Gauss (B) e patch ponderado por quadratura/jacobiano/proximidade (C); exporta os deslocamentos nodais `deslocamentos_elmer.json` e os pontos `gauss_tensoes.csv`. É crucial **não re-solver o FEM** entre A/B/C. A amplitude entre resultados não é intervalo estatístico de confiança ou erro absoluto físico. [Workflow externo aprovado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42502117900) · [dataset permanente](../dados/ciclo14-recuperacao-tensoes-2026-11-08.json).
