# Ciclo 20 — Transição externa de malha Q8

**Data:** 10/11/2026. **Natureza:** experimento de pesquisa numérica. **Estado:** 16 geometrias e 16 FEM Elmer/SciPy verificados; resultado geométrico parcial, topologia não promovida.

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

**Execução concluída:** [workflow #42780634538](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42780634538) com 16/16 FEM externos, 16/16 smoke CAD, auditoria de arquivos e [dataset integral](../dados/ciclo20-transicao-externa-2026-11-10.json) versionado. Em n=48, o pior alongamento global caiu de 14,880→7,505; 31,223→14,721; 17,231→12,652; 33,832→24,331 nos quatro casos. Entretanto, **o menor ângulo piorou em 4/4** (mínimo 6,46°) e o resíduo radial superficial C não melhorou. Os Kt C líquidos variaram muito pouco; quatro GCI C condicionados foram da ordem de 0,10%. **Resultado: ganho parcial, sem promoção de topologia a padrão.**

## Critério de encerramento

Os 16 casos passaram auditoria e os logs brutos foram preservados nos artefatos do workflow. **Nenhuma destas métricas constitui certificado de segurança industrial.** Próximo gate: combater ângulos agudos sem degradar a interface do furo e verificar o vetor de tração sobre toda a parede livre.
