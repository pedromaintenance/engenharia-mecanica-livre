# Ciclo 20 — Transição externa de malha Q8

**Data:** 10/11/2026. **Natureza:** experimento de pesquisa numérica. **Estado:** implementação e CI básica; validação externa sob workflow independente.

## Herança e hipótese

O ciclo 19 construiu anel circular conforme `a≤r≤2a` e verificou 16 FEM Elmer/SciPy. A qualidade junto ao furo melhorou em 3/4 configurações, mas o pior alongamento global **piorou em 4/4** e a condição de tração radial livre `σrr/T` estimada piorou em todas. A hipótese agora é que **duas transições exteriores por setor**, com retângulo intermediário, reduzam essa concentração de distorção, sem mudar o problema físico.

## Entregas de código

- `src/engmec/multibloco_externo.py`: CAD Q8 de seis superfícies, partição radial `ni+nm+no=nr`, retângulo intermediário em escala geométrica e teste de conformidade das interfaces anular e retangular;
- `src/engmec/elmer_chapa.py`: variante `--topologia anel-seis-blocos` opt-in, mantendo `dois-blocos` como padrão;
- `tests/test_multibloco_externo.py` e `tests/test_aval_ciclo20.py`: testes unitários de geometria/retrocompatibilidade e de recusa a resultados ausentes;
- `scripts/avaliar_ciclo20.py`: comparação com o dataset real do ciclo 19 e verificação das evidências de solver e de malha;
- `.github/workflows/ciclo20-transicao-exterior.yml`: smoke CAD de 16 casos, seguido condicionalmente por 16 simulações Elmer/SciPy, relatório de convergência e retenção dos arquivos brutos.

## Evidência e status

- [Workflow específico](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/ciclo20-transicao-exterior.yml).
- [Laboratório 20](../laboratorios/transicao-externa-seis-blocos.md).
- [Baseline íntegra do ciclo 19](../dados/ciclo19-anel-multibloco-2026-11-09.json).

**Não há neste registro afirmação de 16 novas soluções concluídas nem melhoria física confirmada.** Quando as execuções externas passarem, os valores observados, os gates favoráveis e os negativos deverão ser documentados e o dataset rastreado por hash. Se o CAD falhar ou degradar o problema, registrar o resultado negativo sem mudar o default.

## Critério de encerramento

CI verde, 16 geometrias verificadas, 16 resultados independentes presentes, comparação da qualidade global/local e dos resíduos de superfície livre com o ciclo 19, arquivo bruto auditável e decisão argumentada. **Nenhuma destas métricas constitui certificado de segurança industrial.**
