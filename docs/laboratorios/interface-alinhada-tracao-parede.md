# Laboratório 21 — Transição alinhada e tração vetorial na parede do furo

**Data:** 10/11/2026. **Estado:** variante experimental, sem promoção automática.  
[Referência anterior: Laboratório 20](transicao-externa-seis-blocos.md) · [Workflow externo](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/ciclo21-interface-alinhada.yml)

## Problema e hipótese

O ciclo 20 reduziu o pior alongamento global dos Q8, mas reduziu os ângulos mínimos em todas as quatro chapas e deixou a tração radial residual no furo praticamente invariável. O estudo anterior só avaliava `σrr/T` em um ponto crítico usando recuperador de tensões C. Uma interface externa diferente pode redistribuir a distorção; para avaliar a condição livre, entretanto, é preciso observar **todo o arco de parede** e também a parcela cisalhante `σrθ/T`.

## Dois experimentos distintos

### Experimento A — Interface alinhada, pesquisa discreta em CAD

Na topologia com **seis blocos Q8**, duas superfícies têm um anel interior `a≤r≤2a`, duas superfícies fazem a transição e duas terminam nas faces da chapa. O novo ponto intermediário `(Xm,Ym)` fica colinear com o ponto circular `(2a/√2, 2a/√2)` e com o canto externo `(Hx,Hy)`, conforme:

```text
b  = 2a / sqrt(2)
Xm = b + λ·(Hx-b)
Ym = b + λ·(Hy-b)
```

A pesquisa cobre `λ = 0,45; 0,50; 0,55; 0,60; 0,65; 0,70; 0,75`, nas quatro geometrias `(H/a,L/W)=(4,2),(4,4),(8,2),(8,4)`. Cada tentativa usa `nr=48`, `nt=96` e **4.608 elementos Q8**. São **28 malhas CAD efetivas**; fração de interface não é probabilidade nem propriedade física.

As métricas são alongamento máximo global `R`, menor ângulo dos vértices `θmin` e jacobianos Q8. A seleção experimental minimiza, nos quatro casos, o maior valor de `max(R21/R20, θ20/θ21)`, com desempate pela média. Esse critério minimax é **heurística declarada**: não garante ótimo geométrico, não é minimização de energia e não valida tensões.

**Resultado do smoke CAD:** as 28 geometrias passaram verificações de nós médios compartilhados, contornos físicos e jacobianos positivos nos pontos avaliados. O minimax escolheu `λ=0,45`, mas **nenhum dos sete candidatos melhorou simultaneamente o alongamento e o ângulo em todas as quatro geometrias**. Logo, a escolha é provisória para testes de campo numérico e não constitui aceitação da nova malha.

### Experimento B — Tração na parede completa

A condição mecânica ideal para um furo livre é o vetor `t=σ·n=0`. O projeto usa a decomposição em `σrr/T` e `σrθ/T` e reporta `||t||/T = sqrt((σrr/T)^2+(σrθ/T)^2)`. A partir do vetor nodal **Elmer**, calcula `σ=DBu` em **dois pontos de Gauss por aresta Q8 da parede**. Em cada modelo com `nt=96`, há **192 amostras distribuídas** no arco do quadrante, com rms, máximo, percentil 95, componentes isoladas e desvio radial da geometria interpolada.

As arestas do furo são localizadas pelos três nós (dois vértices + nó médio), devem ter exatamente **um elemento adjacente**, e precisam corresponder ao círculo de raio `a`. O cálculo usa o vetor radial da coordenada geométrica interpolada em cada amostra e guarda coordenadas/ângulos para auditoria.

**Limitação conceitual importante:** no FEM deslocamental, a tração livre é uma condição natural satisfeita na forma fraca. Valores `σn` calculados por gradientes dentro dos elementos podem não anular-se ponto a ponto — isso não equivale automaticamente a violação da condição fraca nem é erro de projeto certificado. A normal geométrica do arco quadrático é aproximada pelo vetor radial; o desvio do círculo é reportado separadamente. Este teste **não** equivale a uma avaliação de fluxo equilibrado em H(div).

## Física e referências conservadas

- Chapa retangular finita em um quadrante, `a=0,01 m`, `H/a=4,8`, `L/W=2,4`;
- Material linear, isotrópico, estado plano de tensões: `E=200 GPa`, `ν=0,30`;
- Tração `T=10 MPa` na face `x=Hx`; topo e furo livres; simetrias `Ux=0` em `x=0`, `Uy=0` em `y=0`;
- Espessura de referência `t=0,005 m` e força resultante do quadrante `F=T·Hy·t`;
- Soluções de deslocamentos independentes pelo Elmer FEM e FEM autoral Q8/SciPy; mesmas recuperações A/B/C anteriores.

**Matriz FEM:** 16 casos da interface alinhada (4 geometrias × n=24,32,40,48), **mais 4 controles da topologia ciclo 20 reexecutados no mesmo ambiente** para comparar `σn` e `σrθ` em toda a parede. Dados e hashes ficam em `docs/dados/ciclo21-interface-tracao-2026-11-10.json` somente após execução e auditoria reais.

## Procedimento reproduzível

```bash
python -m pip install -e ".[elmer]"
python -m unittest discover -s tests -p 'test_tracao_livre_ciclo21.py' -v
python scripts/varrer_ciclo21.py --pasta build/ciclo21-smoke
python -m engmec.elmer_chapa --nr 48 --nt 96 \
  --semilargura-m .08 --semicomprimento-x-m .32 --raio-m .01 \
  --progressao-radial escalonada --topologia anel-seis-blocos-alinhado \
  --fracao-interface .45 --saida build/ciclo21/exemplo
```

O default `--topologia dois-blocos` permanece intocado. A variante `anel-seis-blocos-alinhado` só existe como opção explícita. Em caso de instabilidade, não ocultar resultados negativos nem alterar o parâmetro para forçar um Kt próximo ao de Peterson.

## Condições para decisão

Um ganho de ângulo só interessa se o alongamento, o jacobiano, a consistência Elmer/SciPy, a tração livre forte e a concentração de tensões não piorarem materialmente. Usar a malha mais fina, a série de quatro refinamentos e a medição integral da superfície; reportar resultados **favoráveis e desfavoráveis**. Mesmo um GCI condicionado não autoriza o dimensionamento de olhais de mineração sem geometria 3D, contato, pinagem, fadiga, propriedades reais e ensaio.

## Resultado real — 28 CADs e 20 FEM concluídos

O [workflow 42856063314](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42856063314) concluiu todos os jobs: **28 geometrias Gmsh** (sete posições × quatro chapas), **16 soluções FEM Q8 alinhadas** e **quatro controles do ciclo 20 reexecutados no mesmo ambiente**. A auditoria confrontou 16 hashes MSH2, conformidade das duas interfaces, equilíbrio, deslocamentos Elmer/SciPy, Kt e amostras de tração na superfície inteira. O [JSON real versionado](../dados/ciclo21-interface-tracao-2026-11-10.json) contém 16 casos completos, os controles e a matriz de varredura.

Na malha fina `n=48`, 4.608 elementos e 192 amostras de parede em cada configuração:

| d/W | L/W | Ângulo mín.: variação relativa | Alongamento máx.: variação relativa | RMS tração `||σn||/T` anterior → novo |
| ---: | ---: | ---: | ---: | ---: |
| 0,250 | 2 | +31,31% (melhora) | +8,03% (piora) | 0,003425882 → 0,003425882 |
| 0,250 | 4 | +55,56% (melhora) | +15,31% (piora) | 0,003415154 → 0,003415116 |
| 0,125 | 2 | +14,93% (melhora) | +44,95% (piora) | 0,003169587 → 0,003169557 |
| 0,125 | 4 | +28,42% (melhora) | +47,35% (piora) | 0,003167222 → 0,003166442 |

A redução relativa de RMS no contorno é apenas **0,000013% a 0,0246%**; a **tração máxima amostrada aumentou marginalmente nas quatro chapas**. Portanto, a existência do campo vetorial completo amplia o diagnóstico, mas **não sustenta melhoria física relevante da superfície livre**. Em todas as chapas, `Kt` líquido C variou pouco (no máximo aproximadamente 0,0034% relativo). Os quatro índices GCI C são condicionais e não incluem erro de modelagem nem validação experimental.

O desvio radial máximo do Q8 interpolado em relação ao círculo foi aproximadamente `2,0×10⁻⁹` em fração do raio nas 16 simulações; isso justifica o uso radial neste exemplo, mas **não equivale a usar exatamente a normal geométrica da curva isoparamétrica em todo caso**. A máxima diferença relativa de deslocamentos de referência entre Elmer e SciPy foi `4,54×10⁻¹²`; é concordância numérica, não validação independente da tensão real.

**Decisão:** melhoria de ângulo mínimo em **4/4**, piora do alongamento global em **4/4**, sem ganho material de tração livre. O experimento é reproduzível e os resultados devem ser públicos, mas a variante `anel-seis-blocos-alinhado` permanece **experimental opt-in**. A topologia padrão `dois-blocos` fica inalterada. Próximo gate: estudar topologia externa que reduza **ambos** os riscos geométricos; conferir a tração conforme a normal isoparamétrica e o resíduo da condição fraca sem substituir por um único critério de pico.
