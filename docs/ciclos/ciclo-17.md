# Ciclo 17 — Progressão radial dependente do refinamento

**Data:** 08/11/2026. **Versão:** 0.17.0. **Issue:** [#18](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/18). **Laboratório:** [Malhas Q8 com progressão escalonada](../laboratorios/progressao-radial-q8.md).

## Premissa e objetivo

O ciclo 16 conseguiu estabilizar estimativas de Kt ao refinar até 4608 Q8, mas encontrou razão de cordas até 23 em L/W=4. A progressão geométrica `q=1,12` era mantida independentemente de `n`, causando uma relação acumulada de tamanhos crescente. A nova estratégia define `q_n=exp(24 ln(1,12)/n)`, conserva `q_n^n=1,12^24`, e foi testada **contra os baselines fixos reais dos ciclos 15 e 16**.

## Entregas

- `src/engmec/progressao_radial.py`: função determinística de progressão `fixa/escalonada` com limites de entrada, mantendo `n=24` igual ao original.
- `src/engmec/chapa_retangular.py` e `src/engmec/elmer_chapa.py`: repassam opcionalmente a nova progressão ao CAD Gmsh; CLI `--progressao-radial`, com padrão histórico **fixa**.
- `tests/test_progressao_radial.py`: igualdade exata da geometria no nível n=24, retrocompatibilidade da opção fixa, constância de `q_n^n` e rejeição de entradas inválidas.
- `scripts/avaliar_ciclo17.py` e testes: exigem 16 casos reais, MSH2 SHA256, coincidência de n24, alteração de malhas n>24, contornos, jacobianos, balanço SciPy e comparabilidade de Kt.
- `.github/workflows/ciclo17-malha-radial.yml`: executa **16 casos Elmer FEM** com n=24/32/40/48 e L/W=2/4, d/W=.25/.125; consolida contra datasets anteriores; publica JSON na branch main **somente após êxito** e arquiva malhas/Vtu/logs/versões.

## Achados quantitativos n48

| d/W | L/W | Razão máxima fixa, geral | Razão máxima escalonada, geral | Redução global | Pior 1ª faixa fixa | Pior 1ª faixa escalonada |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 11.315 | 5.928 | 47.6% | 10.485 | 2.021 |
| 0.250 | 4 | 22.213 | 11.639 | 47.6% | 10.548 | 3.931 |
| 0.125 | 2 | 12.067 | 6.296 | 47.8% | 4.522 | 4.258 |
| 0.125 | 4 | 23.001 | 12.002 | 47.8% | 4.573 | 8.075 |

A razão máxima geral caiu em todas as quatro séries cerca de 48%, mas **a primeira faixa piorou em d/W=.125, L/W=4**. Os ângulos mínimos (12–13° para L/W=4) também **não melhoraram**, dado que dependem da geometria dos blocos.

### Kt líquido C e GCI

| d/W | L/W | Fixo n48 | Escalonado n48 | GCI C condicional | Ordens observadas |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0.250 | 2 | 2.439911 | 2.439776 | 0.0073% | 3.357 → 3.268 |
| 0.250 | 4 | 2.435985 | 2.435855 | 0.0074% | 2.975 → 3.438 |
| 0.125 | 2 | 2.676015 | 2.675120 | 0.0442% | 2.956 → 3.105 |
| 0.125 | 4 | 2.674876 | 2.673983 | 0.0411% | 2.977 → 3.270 |

As **quatro sequências do método C** com progressão escalonada passaram os testes programados para GCI condicional, enquanto **nenhuma das quatro C fixas** os passou. Entretanto, o método B no caso d/W=.25 e L/W=4 **não atingiu os critérios**, e um GCI emitido não elimina erro de modelagem nem fornece limite de integridade de um componente industrial.

### Diagnóstico adverso

Em d/W=.125,L/W=4, a tensão radial residual na parede livre `σrr/T` (método C) aumenta de `1,729×10⁻⁵` para `1,020×10⁻³`. A primeira faixa passa de razão de cordas máxima 4,57 para 8,07, mesmo com a melhora global de 23 para 12. O método alternativo **não está pronto para substituir automaticamente a malha histórica**.

## Testes, publicação e evidências

[Workflow de 16 soluções aprovado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42546868607), [dataset persistente](../dados/ciclo17-malha-radial-2026-11-08.json) publicado automaticamente após consolidação, [artefato completo de aproximadamente 60 MB](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42546868607/artifacts/13644225265) (SHA256 `2c98e50257e25d66a1e80a8eaf90d7fd135c0de6c48a10e32524c66186bb4df5`). Retenção prevista até 09/12/2026.

**Decisão:** a issue #18 permanece aberta para **qualidade local/ângulos mínimos e tensão radial de parede**, e a #17 permanece como guarda-chuva da validação numérica. Próximo ciclo deve trabalhar **topologia CAD e distribuição local de tamanhos**, comparando qualidade global, perto do furo e resíduo de tração livre, sem ajustar a malha para forçar coincidência com Peterson.

**Segurança:** modelo educacional linear-elástico 2D, sem pino/contato, fadiga, solda, plástico ou validação material. Nenhum Kt define tensão admissível, libera reparos ou certifica equipamentos.
