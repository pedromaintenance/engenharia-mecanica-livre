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
