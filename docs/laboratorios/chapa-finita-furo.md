# Laboratório 10 — Chapa finita com furo submetida a tração real

**Problema distinto do Kirsch analítico:** neste experimento o material é uma **chapa quadrada FINITA** com um furo central, recebendo **tração uniforme real nas bordas verticais** e sem carregamento nas bordas horizontais. O [Laboratório 09](kirsch-furo.md) impunha os *deslocamentos analíticos de Kirsch* no arco externo; logo, não era um teste de bordas finitas. Agora o problema de contorno é fisicamente diferente.

**Estado do trabalho:** software, testes e automação preparados. Qualquer tabela numérica de tensões será preenchida somente após a execução real do CalculiX; os valores analíticos de Kirsch não podem ser apresentados como resultado exato desta chapa.

## 1. Geometria, tensões e unidades

A placa ocupa o plano \`[-H,H]×[-H,H]\` com furo circular \`r<a\`. Resolve-se o primeiro quadrante por simetria (\`0≤x≤H\`, \`0≤y≤H\`), sem deslocamentos prescritos na face carregada. Modelo **CPS8R de tensão plana**, material homogêneo, isotrópico e elástico linear, sem efeitos tridimensionais de espessura.

| Propriedade | Valor |
| --- | ---: |
| Raio do furo \`a\` | 10 mm |
| Meia largura \`H\` | 40, 80 e 160 mm |
| Largura total \`W=2H\` | 80, 160 e 320 mm |
| Relação \`d/W=a/H\` | 0,25; 0,125; 0,0625 |
| Comprimento total da chapa | \`2H\` (quadrada) |
| Módulo de Young | 200 GPa |
| Poisson | 0,30 |
| Espessura | 5 mm |
| Tração aplicada \`T\` | +10 MPa em x=+H e −10 MPa em x=−H |
| Contornos livres | \`y=±H\` e circunferência do furo |
| Malhas do estudo | \`nr×nt\`: 8×16; 16×32; 24×48 |

A carga total em cada face direita **do quarto de placa** é \`F_quarto=T·espessura·H\`; por exemplo, para H=40 mm, \`F_quarto=2.000 N\`. A verificação automática soma as cargas nodais e confirma essa igualdade; as condições de simetria fixam \`Ux=0\` em x=0 e \`Uy=0\` em y=0, **sem engastar a chapa**.

## 2. Por que dois fatores de concentração?

A tensão nominal depende da seção empregada no denominador. Definindo \`d=2a\`, \`W=2H\` e \`P=T·W·t\`:

\[
\sigma_{\mathrm{nom,bruta}}=\frac{P}{Wt}=T,\qquad
\sigma_{\mathrm{nom,líquida}}=\frac{P}{(W-d)t}=\frac{T}{1-d/W}.
\]

Assim:

\[
K_{t,\mathrm{bruto}}=\frac{\sigma_{\mathrm{pico}}}{T},\qquad
K_{t,\mathrm{líquido}}=(1-d/W)K_{t,\mathrm{bruto}}.
\]

Não se deve interpretar uma diferença entre \`Kt_net\` e \`Kt_gross\` como evidência de que a malha ou o material mudou: **muda apenas a referência nominal**. O caso infinito de Kirsch possui \`Kt=3\` baseado na tensão remota. Em chapa finita, o pico físico deve ser investigado por simulação, literatura adequada e refinamento.

**Referências:** [Vable, *Mechanics of Materials*, Seção C.4.1](https://madhuvable.org/wp-content/uploads/2016/04/Entire%20Book%202018.pdf) e [Fracture Mechanics — Stress concentrations at holes](https://www.m.fracturemechanics.org/hole.html). Um [estudo comparativo publicado em 2026](https://dergipark.org.tr/tr/pub/erciyesfen/article/1892532) também destaca dependência de \`d/W\` e formulações de elementos de tensão plana; suas curvas não são tratadas automaticamente como referência exata deste caso.

## 3. Malha curvilínea com borda quadrada

O algoritmo gera uma malha estruturada Q8 mapeando coordenadas polares \`(r,θ)\` ao contorno externo:

\[
R(\theta)=\frac{H}{\max(\cos\theta,\sin\theta)}, \quad
r_i(\theta)=a+[R(\theta)-a](i/n_r)^g,
\]

com \`g=2\` para concentração de camadas perto do furo. A linha angular \`θ=45°\` coincide exatamente com uma linha de nós, impedindo que um elemento cruze a quina do contorno quadrado. Os meios de aresta são compartilhados entre elementos adjacentes. A curvatura do furo é representada quadraticamente.

A qualidade é medida por **jacobiano Q8 positivo nos quatro pontos de Gauss de cada elemento**. Isso não substitui a inspeção de jacobiano do CalculiX, pois o solver expande internamente os CPS8R em elementos sólidos equivalentes.

## 4. Carga real, não deslocamento imposto

Na face \`x=H\`, a tensão \`T\` é convertida em forças nodais por integração exata da tração uniforme em cada segmento de aresta quadrática. Os pesos nas posições \`(extremidade,meio,extremidade)\` são \`(1/6,4/6,1/6)\` do produto \`T·t·comprimento do segmento\`.

As demais superfícies são livres. Em particular, **não** se prescrevem deslocamentos de Kirsch no contorno externo, e não se aplica pressão fictícia diretamente no furo.

## 5. Como estimar o pico junto ao furo

O \`.dat\` do CalculiX contém coordenadas e componentes \`Sxx,Syy,Sxy\` dos **pontos de integração**. Uma amostra interna perto do furo não é, por definição, tensão da superfície.

Para estimar o valor na interseção do furo com \`x=0\`, em \`r=a,θ=90°\`, o código coleta pontos nas três primeiras camadas radiais e três últimas células angulares, transforma as tensões para a componente circunferencial \`Sθθ\` e ajusta um polinômio local por mínimos quadrados:

\[
S_{\theta\theta}/T \approx c_0+c_1u+c_2u^2+c_3v^2+c_4uv^2+c_5v^4
\]

com \`u=(r−a)/Δr₁\` e \`v=(π/2−θ)/Δθ\`. A estimativa da tensão na borda é **\`c0\`**. Essa é uma **extrapolação baseada em pontos internos**, não uma leitura de tensão superficial diretamente do solver. Os efeitos de ajuste, malha e direção da amostragem exigem avaliação de sensibilidade.

**Controle independente do método:** o mesmo algoritmo é aplicado ao **campo analítico de Kirsch amostrado nas coordenadas de Gauss**; o relatório indica o desvio dessa extrapolação analítica em relação a \`Kt=3\`. Isso **verifica o algoritmo de ajuste**, mas não valida a tensão da chapa finita.

## 6. Como reproduzir

Gerar um arquivo CalculiX sem instalar o solver:

\`\`\`bash
python -m engmec.chapa_finita --nr 16 --nt 32 \
  --semilargura-m 0.04 --somente-gerar \
  --saida build/chapa-finita/h-4-n-16
\`\`\`

Executar com \`ccx\` instalado:

\`\`\`bash
python -m engmec.chapa_finita --nr 16 --nt 32 \
  --semilargura-m 0.04 \
  --saida build/chapa-finita/h-4-n-16
\`\`\`

A automação [GitHub Actions — chapa finita](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/chapa-finita.yml) gera e resolve **cinco casos**: \`H/a=4\` nas malhas 8×16, 16×32 e 24×48, e \`H/a=8\` e 16 em 24×48. O arquivo \`resumo_chapa_finita.json\` preserva \`Kt_gross\`, \`Kt_net\`, proxy interno, desvio do extrapolador no campo de Kirsch, carga integrada e custo.

## 7. Critérios, interpretação e limitações

O workflow não aceita valores não finitos, tensão de concentração mecanicamente implausível, incompatibilidade no total de carregamento nem inconsistência entre referências nominal bruta e líquida. A **tendência entre refinamentos** será reportada, mesmo que não seja monotônica; uma execução bem-sucedida, por si só, não prova ordem de convergência.

Esse problema permanece **bidimensional em tensão plana**. Não contempla contato de pino, plastificação, travamento do elemento, ovalização, trinca, fadiga, tensões residuais, efeito de espessura 3D ou ensaio físico. O valor \`Kt\` calculado **não libera operações de solda, montagem ou carregamento de componentes reais**.

Para avançar à aplicação prática, serão necessários: convergência controlada de extrapolação superficial, geometria real, carregamento medido, propriedades verificadas, verificação independente de literatura ou ensaio e revisão profissional.
