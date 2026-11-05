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
