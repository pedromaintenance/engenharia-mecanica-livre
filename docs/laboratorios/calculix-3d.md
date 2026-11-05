# Laboratório 06 — Comparação FEM 1D × CalculiX 3D

**Natureza:** benchmark de verificação do método numérico, não autorização de projeto ou validação experimental. Implementação original e independente do código do CalculiX.

## Objetivo

Executar um modelo tridimensional simplificado com elemento hexaédrico linear de oito nós **C3D8** e confrontar seu deslocamento axial e reação no apoio com a solução analítica `u(L)=FL/(EA)` e nosso solver 1D.

Os elementos C3D8 são de integração completa e o manual do CalculiX alerta para limitações em flexão e materiais quase incompressíveis. Aqui empregamos somente **carregamento axial uniforme**, material homogêneo e linear, com `ν=0,30`. Esta escolha é um *patch test* simples; não equivale a testar malhas de problemas industriais complexos.

## Geometria e material

| Propriedade | Valor |
| --- | ---: |
| Comprimento L | 2 m |
| Área A | 1000 mm² |
| Seção | Quadrada, lado √A |
| Módulo de Young E | 200 GPa |
| Poisson ν | 0,30 |
| Força axial total F | 10000 N |
| Malhas axiais nx | 1, 2, 4 e 8 |
| Divisões laterais ny,nz | 2 × 2 |

### Condições de contorno

- Em toda a face `x=0`: apenas `U1=0`, mantendo livres as contrações transversais de Poisson.
- No centro dessa face: `U2=0`, `U3=0`, removendo translação transversal rígida.
- Em outro nó da face, no plano `z=0`: `U3=0`, para remover giro rígido em torno do eixo x.
- Na face livre `x=L`, aplica-se a força na direção x **por cargas nodais equivalentes à tração uniforme**: os pesos são determinados pelas áreas tributárias de cada elemento da face (não aplica a força toda num único nó).
- Demais superfícies laterais livres. O carregamento aqui é `q=0`; não confundir com o caso com q distribuído do laboratório FEM 1D.

### Solução de referência

```text
u(L) = F L /(E A)
     = (10.000 N × 2 m)/(200×10⁹ Pa × 0,001 m²)
     = 0,0001 m = 0,1 mm

Reação axial total na raiz = −10.000 N
```

A reação é negativa pela convenção do eixo x. Para um material isotrópico livre lateralmente, o campo de deformação axial uniforme é representável por elementos C3D8, desde que cargas e restrições respeitem a hipótese.

## Executar

O Python padrão **gera os arquivos sem o solver**:

```bash
python -m engmec.calculix --somente-gerar --nx 4 --saida build/calculix/nx-4
```

Com CalculiX instalado e disponível em `PATH` (executável `ccx` ou `ccx_2.21`, por exemplo):

```bash
python -m engmec.calculix --nx 4 --saida build/calculix/nx-4 --tolerancia 0.02
```

O módulo gera arquivos `.inp`, `entrada.json`, `solver.log`, `.dat`, `.frd` e `comparacao.json` quando o executável roda. `comparacao.json` é calculado **a partir dos resultados lidos em .dat**, e não contém valores simulados inventados.

Um workflow dedicado em [GitHub Actions](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/calculix.yml) instala o pacote **calculix-ccx** do Ubuntu 24.04 e roda quatro malhas, arquivando entradas, logs e resultados como artefatos.

## Critérios de aceite

- A instalação e execução do **solver real** precisam estar demonstradas nos logs da GitHub Action.
- Cada malha deve ter saída de deslocamento `U1` do nó central da ponta e `RF1` nos nós da raiz.
- Erro relativo de `U1` e erro de equilíbrio de reações inferiores a 2% (tolerância exploratória do benchmark).
- Sem saída ou solver ausente: **falha**, nunca substituir por solução analítica e declarar sucesso.
- A configuração deste caso não demonstra convergência não trivial: solução homogênea pode ser representada exatamente em todas as malhas. A ordem de convergência já testada para tensões sob `q≠0` permanece no [laboratório 05](benchmark-barra-fem.md).

## Limites operacionais e próximos estudos

A geometria é prismaticamente perfeita e o material é contínuo, elástico e homogêneo. Não há contato, flambagem, fadiga, plastificação, interfaces, soldas, furos, ações térmicas ou anisotropia. O benchmark valida apenas consistência mecânica e execução computacional do caso proposto; não substitui avaliação profissional de projeto ou inspeção em máquina real.

Próximo estudo: problema que produz gradientes de tensão com singularidades controladas, elementos quadráticos e convergência de malha (sem concluir apenas por estabilidade de um indicador).

## Literatura e ferramentas

- [CalculiX — C3D8 element manual](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node28.html)
- [CalculiX — *NODE PRINT](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node307.html)
- [Ubuntu — pacote calculix-ccx 2.21-1](https://packages.ubuntu.com/noble/calculix-ccx)
- [Código original do benchmark](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/src/engmec/calculix.py)

**Status:** código e workflow precisam de confirmação de execução no GitHub antes de registrar valores do solver como observados.


### Observação sobre RF no CalculiX

O manual explica que a variável `RF` representa a soma de forças externas nodais, podendo agregar reação e cargas diretamente aplicadas ao nó. Neste benchmark, **os nós ROOT não recebem CLOAD nem DLOAD**, logo seus valores `RF` são equivalentes às reações de apoio. O arquivo `.dat` pode trazer o cabeçalho `forces (fx,fy,fz)` em vez de `reaction forces`; o parser aceita ambas as convenções.


## Resultado real — execução concluída em 05/11/2026

O workflow [CalculiX #42055701419](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42055701419) executou o pacote **calculix-ccx 2.21-1** no Ubuntu 24.04, em quatro malhas, e passou integralmente. Foi verificado o uso real de `/usr/bin/ccx`, a leitura do arquivo `.dat`, o cálculo de reações e a saída do comparador. O artifact `calculix-c3d8-ubuntu2404` (ID `13429701171`) contém os quatro arquivos `.inp`, resultados `.dat`/`.frd`, logs e comparações JSON. A retenção declarada é de 30 dias a partir da execução; preservar no repositório apenas o relatório pequeno de métricas.

| Elementos axiais (nx) | C3D8 totais | Nós | Ux da ponta | Reação axial | Erro relativo informado |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 4 | 18 | 0,1000 mm | −10.000 N | 0,0%* |
| 2 | 8 | 27 | 0,1000 mm | −10.000 N | 0,0%* |
| 4 | 16 | 45 | 0,1000 mm | −10.000 N | 0,0%* |
| 8 | 32 | 81 | 0,1000 mm | −10.000 N | 0,0%* |

*O valor de erro 0,0% representa o que foi informado na precisão **limitada da saída textual** `*NODE PRINT`; não é prova matemática de arredondamento zero, de convergência para problemas não homogêneos ou de correção de hipóteses de projeto.*

O resultado é compatível com a solução fechada `FL/(EA)` e com o solver 1D autoral. Nenhuma carga foi aplicada diretamente na raiz, de modo que `RF` nela coincide com a reação (a variável RF em geral inclui forças externas nodais).

[Dados observados do benchmark em JSON](../dados/calculix-c3d8-2026-11-05.json) · [Execução e artefatos](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42055701419) · [CI geral](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42055701336).

**Estado após o ciclo 06:** benchmark cruzado de **tração uniforme** validado por execução real. O benchmark de **convergência não trivial 3D** permanece pendente.
