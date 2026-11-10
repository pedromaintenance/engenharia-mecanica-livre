# Laboratório 20 — Transição externa Q8 com seis blocos

**Situação:** topologia experimental; não é default e não é autorização de projeto de componente real.  
**Data:** 10/11/2026. **Referência:** [ciclo 19](anel-multibloco-q8.md).  
**Workflow de verificação:** [GitHub Actions do ciclo 20](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/ciclo20-transicao-exterior.yml).

## Problema físico

O ciclo 19 isolou o furo com duas superfícies anulares conformes de Q8, mas a transição direta desse anel para a borda da chapa gerou alongamentos globais de até **33,832**, conforme os 16 modelos executados anteriormente. A tração radial residual `σrr/T` recuperada no ponto crítico do furo também aumentou nos quatro casos de malha mais fina. **A hipótese do ciclo 20** é que adicionar uma interface retangular intermediária pode distribuir melhor as deformações dos elementos no exterior. Esta hipótese deve ser testada, não presumida verdadeira.

## Geometria e parametrização

A chapa completa tem `L=2Hx` na direção da tração, `W=2Hy` transversal e furo de diâmetro `d=2a`. Simula-se o quadrante `x≥0,y≥0`. As dimensões são **as mesmas do ciclo 19**: `a=0,01 m`, `H/a=4 ou 8`, `L/W=2 ou 4` e `d/W=a/Hy=0,25 ou 0,125`.

A geometria possui seis superfícies transfinite com elementos serendipidade Q8:

1. **101–102:** anel `a≤r≤2a`, com `Ni=nr/2` divisões radiais uniformes;
2. **103–104:** transição do anel até `(Xm,Ym)`, com `Nm=nr/4` divisões uniformes, onde `Xm=√(2a·Hx)` e `Ym=√(2a·Hy)`;
3. **105–106:** transição retangular até as faces externas `x=Hx` e `y=Hy`, com `No=nr−Ni−Nm` divisões uniformes.

Em cada setor angular de 45°, são `Na=nt/2` divisões, e `nt=2nr`. O número total é **`nr × nt = 2nr²`** elementos, permitindo comparação nominal de custo com as malhas anteriores. **Igual número de elementos não implica mesma qualidade nem mesmo erro.**

As interfaces compartilham curvas únicas, vértices e nós médios Q8, verificadas por contagem de incidências. A qualidade geométrica inclui jacobianos Q8 positivos nos pontos avaliados, razão de cordas e ângulos mínimos; são indicadores insuficientes isoladamente para certificar o campo de tensões.

## Física conservada

- Material isotrópico linear em **tensão plana**: `E=200 GPa`, `ν=0,30`;
- Tração nominal `T=10 MPa` em `x=Hx`; `y=Hy` e furo livres;
- Restrições de simetria `Ux=0` em `x=0` e `Uy=0` em `y=0`;
- Espessura de referência `t=0,005 m`, resultante integrada do quadrante `F=T·Hy·t`.

O mesmo MSH2 alimenta o Elmer e o solver Q8 independente em Python/SciPy; as estimativas superficiais A/B/C utilizam **um mesmo vetor Elmer** e separam alteração de malha de alteração de método de recuperação.

## Matriz experimental e gates

Quatro geometrias `(H/a,L/W)=(4,2),(4,4),(8,2),(8,4)`, cada qual com `nr=24,32,40,48`: **16 arquivos MSH2 e, condicionados ao smoke CAD, 16 soluções FEM**. Os resultados serão consolidados por `scripts/avaliar_ciclo20.py` e confrontados caso a caso com o [dataset real do ciclo 19](../dados/ciclo19-anel-multibloco-2026-11-09.json).

Os gates independentes são:

- **Integridade do CAD:** elementos Q8, duas interfaces conformes, sem nós duplicados ou arestas pendentes, jacobianos positivos nos pontos testados, contornos físicos e número de elementos preservados;
- **Coerência física:** carregamento, material, simetrias, equilíbrio SciPy e correspondência de deslocamentos Elmer/SciPy;
- **Qualidade geométrica:** pior alongamento de cordas global e na primeira faixa, percentil 95 e menor ângulo; comparar sem seleção favorável;
- **Superfície livre:** `σrr/T` no ponto crítico, especialmente do recuperador C; **um valor pequeno em um ponto não demonstra contorno livre em toda a curva**;
- **Concentração de tensões:** `Kt` bruto e líquido obtidos por A/B/C, com Richardson/GCI **somente** se o verificador identificar ordem e monotonicidade estáveis.

O experimento **não deve promover automaticamente a malha de seis blocos**, mesmo se um gate isolado melhorar. O default segue `--topologia dois-blocos`; `anel-quatro-blocos` e `anel-seis-blocos` são opt-in.

## Reproduzir (dependências externas necessárias)

```bash
python -m pip install -e ".[elmer]"
python -m unittest discover -s tests -p 'test_multibloco_externo.py' -v
python -m engmec.elmer_chapa \
  --nr 48 --nt 96 --raio-m .01 \
  --semilargura-m .08 --semicomprimento-x-m .32 \
  --progressao-radial escalonada --topologia anel-seis-blocos \
  --saida build/ciclo20/ha-8-lw-4-n-48
```

O workflow arquiva `.geo`, `.msh`, configurações Elmer, logs, campos e recuperações, inclusive falhas de execução. O dataset `docs/dados/ciclo20-transicao-externa-2026-11-10.json` **só poderá existir se a auditoria pós-solver encontrar todos os 16 modelos reais**.

## Limites e decisão

O novo desenho não inclui contato pino–furo, soldas, fadiga, plastificação, efeitos 3D, fabricação, incertezas de propriedades ou ensaio experimental. Não usar `Kt` ou GCI isolados para liberar componentes de mineração. O aceite do método deve depender dos resultados externos e de uma referência física apropriada.
