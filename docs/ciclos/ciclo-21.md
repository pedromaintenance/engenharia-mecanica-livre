# Ciclo 21 — Transição externa alinhada e auditoria de tração

**Data:** 10/11/2026. **Natureza:** pesquisa de malha Q8 e pós-processamento. **Situação:** implementação experimental, critérios de aceitação separados.

## Herança

O ciclo 20 demonstrou redução de até 52,9% no pior alongamento global, mas deteriorou os ângulos mínimos e não melhorou a tensão radial no ponto crítico. O problema agora exige testar outra colocação da interface e medir a tração `σ·n` em **toda a parede**, não apenas em um ponto.

## Entregas da versão experimental

- `multibloco_externo.py`: modo `alinhada` com fração explícita `λ∈[0,45;0,75]`; preserva `geometrica` como padrão do ciclo 20;
- `elmer_chapa.py`: topologia opt-in `anel-seis-blocos-alinhado`, parâmetro CLI e rastreio de tração completa para as duas variantes de seis blocos;
- `tracao_livre.py`: dois pontos por aresta Q8, `σrr/T`, `σrθ/T`, resultante, RMS, máximo e verificação de conformidade;
- `varrer_ciclo21.py`: sweep CAD de **28 malhas** e seleção minimax prévia ao solver;
- `avaliar_ciclo21.py`: auditoria de **16 novos FEM + 4 controles reais** frente ao ciclo 20;
- testes de invariância numérica (tração uniforme, deslocamento zero, rotação rígida, campo incompleto), nova CI e documentação.

## Primeiro resultado verificado

A varredura real Gmsh de 28 malhas (7 frações × 4 chapas) foi aprovada pelo gate de conformidade. A fração `λ=0,45` apresentou a menor pior penalização geométrica entre as frações testadas. **Nenhuma** melhorou simultaneamente alongamento e ângulo mínimo em todas as chapas. Não promover topologia por força desse resultado.

## Evidências e próximos gates

[Laboratório 21](../laboratorios/interface-alinhada-tracao-parede.md) · [workflow do ciclo](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/ciclo21-interface-alinhada.yml)

A publicação de resultados físicos exige MSH2, logs Elmer, vetores de deslocamento, arquivos `tracao_furo.csv/json`, equilíbrio, concordância SciPy e quatro reexecuções de controle. Se a melhoria física falhar, publicar o resultado negativo com causas plausíveis e preservar `dois-blocos` como default. **Nenhuma saída é critério de aprovação estrutural industrial.**

## Resultado final da execução externa

A [execução 42856063314](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42856063314) passou: **28 CADs, 16 FEM alinhados, quatro FEM de controle, auditoria e dataset completo**. [Dados JSON com hash](../dados/ciclo21-interface-tracao-2026-11-10.json). A posição selecionada foi `λ=0,45`.

**Contradições comprovadas (n=48):** ângulo mínimo melhora de **14,93% a 55,56%** nas quatro chapas; alongamento máximo global piora de **8,03% a 47,35%** nas quatro. A tração vetorial RMS na parede inteira é praticamente idêntica ao ciclo 20 (variações de −0,000013% a −0,0246%); o máximo amostrado sobe marginalmente nos quatro casos. Os Kt C líquidos variaram menos de ~0,0034% e os GCI C continuam condicionais.

**Decisão:** publicar experimento com **gate geométrico reprovado**, sem promover `anel-seis-blocos-alinhado`; manter `dois-blocos` como padrão. O laboratório avançou metodologicamente por medir `σrr` e `σrθ` sobre toda a parede, mas não encontrou melhoria estrutural demonstrada. Próximo ciclo: curva/interface externa e métrica combinada de qualidade geométrica + condição livre, sem aplicação direta a olhais reais.
