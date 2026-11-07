# Laboratório 12 — Dois solucionadores FEM independentes para uma chapa com furo

**Estado:** quatro pares de simulações executados no CI com **CalculiX 2.21-1** e **uma implementação autoral de elementos Q8 em Python/NumPy/SciPy**; a igualdade da malha foi comprovada, caso a caso, pelo SHA-256 do arquivo `.msh`. Resultados e limitações a seguir.

Este laboratório amplia a verificação numérica do [Laboratório 11](gmsh-chapa.md). Já não se trata apenas de comparar **geradores de malha** diferentes: há **duas implementações independentes de montagem e resolução de equações FEM**, ainda que a implementação Python seja uma ferramenta didática nova, **não qualificada industrialmente**.

## 1. Problema de elasticidade compartilhado

Uma chapa quadrada finita tem furo circular central de raio `a=10 mm`. O problema é reduzido ao primeiro quadrante por simetria. Consideram-se **tensão plana**, pequenos deslocamentos e material isotrópico linear com `E=200 GPa` e `ν=0,30`. A espessura é `t=5 mm`.

A face `x=H` recebe tração horizontal uniforme `T=10 MPa`, que representa a condição de tração nas faces `x=±H` da chapa completa. O furo e a borda `y=H` são livres; nos eixos de simetria são impostos `Ux=0` em `x=0` e `Uy=0` em `y=0`. A resultante externa do quadrante deve ser `F=T H t`, igual em módulo à soma das reações horizontais.

Com `H/a=4`, a chapa completa mede **80 mm** de largura; com `H/a=8`, **160 mm**. O fator de concentração nominal bruto é `Kt_gross=σpico/T`, enquanto `Kt_net=(1−a/H)Kt_gross`. **O Kt=3 analítico de Kirsch não é a solução exata da chapa quadrada finita**.

## 2. Formulações FEM comparadas

| Característica | CalculiX (externo) | Python/SciPy (autoral) |
| --- | --- | --- |
| Tipo | CalculiX CPS8R, com expansão interna conforme OEM | elemento isoparamétrico serendipidade Q8 plano, 8 nós, 2 DOFs por nó |
| Matriz global | montada e resolvida internamente pelo CalculiX | matriz construída por `BᵀDB`, em formato esparso SciPy |
| Estado físico | tensão plana | tensão plana |
| Integração | representação CPS8R do CalculiX | quadratura Gauss **3×3** no elemento Q8 |
| Tração na borda | forças equivalentes Q8 | pesos `1/6,4/6,1/6` de força por segmento Q8 |
| Contorno do furo | livre | livre |
| Recuperação da tensão máxima | extrapolação por ajuste de seis coeficientes sobre pontos de Gauss internos | **gradiente do campo FE diretamente no nó de contorno `(x=0,y=a)`**, sem ajuste de Gauss |
| Malha | Gmsh MSH2 quad8 (tipo 16) | **exatamente o mesmo arquivo MSH2** de cada caso |
| Validação externa | software FEM existente | **protótipo de pesquisa**, sujeito a revisão independente |

O mesmo Gmsh 4.12.1 foi empregado para gerar a chapa. Os arquivos `.msh` de cada par foram confrontados **byte a byte por hash SHA-256** antes de a comparação ser aceita. Isso evita confundir uma alteração geométrica com uma diferença entre solucionadores.

**Importante:** o experimento não isola *somente* a diferença de implementação: a integração volumétrica e, sobretudo, a recuperação de tensão máxima também são diferentes. A comparação de Kt inclui **essas duas fontes de variação**.

## 3. Formulação numérica do solucionador autoral

A elasticidade isotrópica em tensão plana é representada pela matriz constitutiva:

\[
D=\frac{E}{1-\nu^2}
\begin{bmatrix}
1 & \nu & 0\\
\nu & 1 & 0\\
0 & 0 & (1-\nu)/2
\end{bmatrix}.
\]

A partir das funções de forma serendipidade `N_i(ξ,η)`, o jacobiano isoparamétrico transforma as derivadas naturais para derivadas espaciais. A matriz `B` relaciona os **16 deslocamentos nodais** às deformações `εxx, εyy, γxy`.

A rigidez de cada elemento é integrada por Gauss 3×3:

\[
K_e=t\int_{-1}^{1}\int_{-1}^{1}B^TDB\,|\det J|\,d\xi\,d\eta.
\]

Após a montagem de todas as matrizes elementares numa matriz esparsa global, os DOFs de simetria são eliminados e o sistema `Kff·uf=ff` é resolvido com `scipy.sparse.linalg.spsolve`. Os DOFs restantes são reconstruídos, e as reações são avaliadas por `R=Ku−f`.

A fonte da formulação Q8 é a interpolação serendipidade padrão; a implementação foi confrontada por **diferenças finitas das derivadas**, **partição da unidade**, **reprodução de campo afim de deslocamentos e tensão uniforme**, simetria/positividade de `D` e **equilíbrio de forças no problema resolvido**.

**Fontes primárias de software:** [SciPy — spsolve](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.spsolve.html), [SciPy — montagem COO](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.coo_matrix.html) e [Gmsh — documentação oficial](https://gmsh.info/doc/texinfo/).

NumPy/SciPy são **dependências opcionais do benchmark**, não da biblioteca básica. Seus testes mais avançados são executados no workflow dedicado, em que essas dependências são instaladas explicitamente.

## 4. Recuperar a tensão diretamente no contorno

O método externo já existente extrapola `σθθ/T` para `r=a,θ=90°` por um ajuste local polinomial usando pontos internos de Gauss. No solver novo, a avaliação é **diferente**:

1. Identificar o único nó geométrico do quarto de chapa com `x=0,y=a` e o elemento Q8 adjacente ao ponto.
2. Avaliar a matriz `B` desse elemento **exatamente na coordenada natural do vértice**, sem extrapolar a partir de tensões em Gauss.
3. Calcular `σ=D B u_e`; na posição `θ=90°`, a tensão tangencial da parede coincide com `σxx`.
4. Reportar também `σrr/T` e `σrθ/T` nesse ponto. Para a superfície livre ideal, essas componentes deveriam tender a zero com refinamento.

É um método de **gradiente FE de um único elemento na borda**, sujeito à qualidade geométrica e à precisão da solução de deslocamentos. Não constitui medição experimental nem necessariamente uma estimativa mais confiável que a extrapolação: recuperações nodais podem ter viés e descontinuidade entre elementos.

Como controle adicional do algoritmo, o código aplica a mesma operação `D B u_e` a **deslocamentos exatos de Kirsch amostrados nos oito nós** do elemento; o valor deve tender a 3 à medida que a discretização fica mais fina. Isso verifica a representação/interpolação, mas **não torna Kirsch uma solução exata para a chapa finita**.

## 5. Execuções reais — 07/11/2026

[Workflow GitHub Actions #42423510950](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42423510950): Gmsh **4.12.1+ds1-1.1build2**, CalculiX **2.21-1**, NumPy **2.5.4**, SciPy **1.18.1**, Ubuntu 24.04. Quatro pares de simulações foram executados (8 resoluções de modelo). Os arquivos de malha em cada par são idênticos por SHA-256.

| Largura W | Elementos | Kt bruto CalculiX (extrapolado) | Kt bruto SciPy (gradiente direto) | Diferença relativa |
| ---: | ---: | ---: | ---: | ---: |
| 80 mm | 512 | 3,596799 | 3,588914 | −0,2192% |
| 80 mm | 1.152 | 3,614709 | 3,584406 | −0,8383% |
| 160 mm | 512 | 3,081885 | 3,152512 | +2,2917% |
| 160 mm | 1.152 | 3,153882 | 3,139032 | −0,4708% |

A **maior diferença observada de Kt bruto é ~2,29%**. Não há diminuição monotônica da diferença nos dois pares de refinamento: para a chapa de 80 mm, a divergência de Kt entre métodos cresce na malha mais refinada. Portanto, **não se pode usar este experimento para alegar ordem de convergência global ou incerteza total de Kt**.

### 5.1 Equilíbrio e diagnóstico da parede livre

| Largura | Elementos | Resíduo equilíbrio horizontal | σrr/T na parede (SciPy) |
| ---: | ---: | ---: | ---: |
| 80 mm | 512 | 4,81 × 10⁻¹⁴ | +0,01587 |
| 80 mm | 1.152 | 5,30 × 10⁻¹⁴ | +0,00288 |
| 160 mm | 512 | 5,26 × 10⁻¹⁴ | +0,05519 |
| 160 mm | 1.152 | 1,41 × 10⁻¹⁴ | +0,00969 |

As reações e cargas estão equilibradas em todas as malhas com precisão algébrica alta; a **condição de tensão radial livre não é satisfeita exatamente pelo gradiente nodal** e constitui outro indicador de erro de discretização. O resultado da chapa de 160 mm e 512 elementos, com `σrr/T≈0,055`, merece atenção antes de aceitar a tensão tangencial estimada na mesma região.

### 5.2 O que os números permitem concluir

- Há **concordância razoável** entre duas implementações de elasticidade plana para o problema idealizado, com diferenças observadas entre **0,22% e 2,29%** no indicador superficial recuperado.
- Não há concordância perfeita nem convergência monotônica de todos os indicadores; a diferença de recuperação de tensão é material no resultado.
- As duas implementações compartilham a malha, a física idealizada e características da família Q8. A implementação SciPy é nova e **não possui qualificação industrial independente**.
- Não existe aqui uma referência exata para o pico de tensão **da chapa quadrada finita**, nem um ensaio experimental. O valor de Kirsch `Kt=3` serve somente como contexto de domínio infinito.

## 6. Reproduzir

Gmsh 4.12.1 e CalculiX 2.21 podem ser instalados no Ubuntu 24.04; o solucionador autoral usa Python 3.12 com dependências opcionais `numpy` e `scipy`.

```bash
python -m pip install -e .
python -m pip install "numpy>=1.26,<3" "scipy>=1.12,<2"

python -m engmec.gmsh_chapa --nr 24 --nt 48 \
  --semilargura-m .04 --saida build/ciclo12/calculix/ha-4-n-24

python -m engmec.fem2d_indep --nr 24 --nt 48 \
  --semilargura-m .04 --saida build/ciclo12/scipy/ha-4-n-24

python scripts/avaliar_ciclo12.py --pasta build/ciclo12
```

O script de consolidação exige os **quatro pares**, verifica hashes de entrada, equilíbrio e faixa de plausibilidade das tensões, e reprova dados incompletos ou divergência absoluta de Kt superior a um limiar operacional explícito de 0,35. **Esse limiar de execução é um gate de detecção de falha grosseira, não uma tolerância de aprovação industrial**.

**Evidências:** [dados permanentes](../dados/ciclo12-solvers-independentes-2026-11-07.json), [relatório do ciclo](../ciclos/ciclo-12.md), [workflow](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/ciclo12-dois-solvers.yml) e [código Python](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/src/engmec/fem2d_indep.py).

## 7. Horizonte de validação

Próximos gates: um **solver FEM externo com histórico independente**, como Elmer (com `ElmerGrid 14 2` para Gmsh), ou outro implementador independente; estudos mais finos de malha em **ambos** os solvers; referência de geometria quadrada finita comparável; comparação de gradiente nodal, projeção de tensão e extrapolação com uma análise de sensibilidade sistemática.

A recomendação prática permanece: **não dimensionar nem liberar olhal, chapa ou máquina usando esses valores de Kt**. O estudo mede comportamento de implementações numéricas sob hipóteses simplificadas e não a segurança de um componente industrial.
