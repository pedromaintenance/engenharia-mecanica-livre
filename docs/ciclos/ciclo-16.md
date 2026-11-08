# Ciclo 16 — Convergência fina e qualidade geométrica Q8

**Data:** 08/11/2026. **Versão alvo:** 0.16.0. **Issue:** [#17](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/17).

## Problema herdado

O [ciclo 15](ciclo-15.md) resolveu 18 modelos de chapa retangular em três malhas, mostrando que o efeito de comprimento aproxima a solução do modelo de tira longa de Peterson. Mas uma das séries \`d/W=0,125,L/W=4\` variou 2,27% entre as duas malhas mais refinadas, impedindo concluir que o valor próximo à referência estivesse numericamente estabilizado.

## Objetivo

Prosseguir para três refinamentos novos \`n=32,40,48\` (2048/3200/4608 elementos Q8), em \`d/W=0,25/0,125\` e \`L/W=2/4\`, total **12 simulações Elmer novas**. Reutilizar o nível n=24 já publicado como **quarta amostra numérica** para avaliar monotonicidade, ordem observada e, apenas sob condições restritas, GCI.

## Modificações implementadas

- \`src/engmec/convergencia_malha.py\` — avaliação de qualidade de elementos Q8 por jacobiano, razão de cordas e ângulos dos vértices, contagens de fronteiras e DOFs; \`convergencia_condicionada\` exige quatro malhas e ordens observadas estáveis.
- \`tests/test_convergencia_malha.py\` — convergência sintética conhecida de ordem 2, rejeição de séries oscilantes, dados inválidos e ausência de malha real.
- \`scripts/avaliar_ciclo16.py\` e \`tests/test_aval_ciclo16.py\` — 12 casos mandatórios, confronto com baseline n=24 e Peterson líquido, verificação de cargas, arquivo MSH2 SHA256, jacobiano e compatibilidade de deslocamentos Elmer×SciPy.
- \`.github/workflows/ciclo16-convergencia.yml\` — execução de duas matrizes **em paralelo**, com 6 casos para d/W=0,25 e 6 para d/W=0,125, seguido de consolidação e armazenamento completo dos arquivos brutos.
- [Laboratório 16](../laboratorios/convergencia-fina-retangulo.md) — hipóteses, fórmulas, limites científicos, referência externa e reprodução.

## Critérios de aceite

O pipeline deve produzir 12 campos Elmer FEM completos, preservar malhas de 2048/3200/4608 elementos, três recuperações A/B/C com mesmo deslocamento, qualidade de elemento, carga física e balanço de reações, e calcular dados comparáveis por três refinamentos novos. **Não extrapolar automaticamente GCI**: primeiro exigir a monotonicidade e a consistência de ordem entre (24,32,40) e (32,40,48).

A comparação Peterson é apenas uma **referência de tira muito longa**, não o valor exato do retângulo finito. Nem a concordância entre operadores FEM nem uma pequena diferença em relação à curva constituem validação experimental de componente real.

## Material complementar

- [ANSYS PyMAPDL — placa com furo](https://mapdl.docs.pyansys.com/version/stable/examples/gallery_examples/00-mapdl-examples/2d_plate_with_a_hole.html).
- [NIST — VVUQ e Richardson/GCI](https://www.govinfo.gov/content/pkg/GOVPUB-C13-3b234d3edb50d5f632fa1a8b21b911dd/pdf/GOVPUB-C13-3b234d3edb50d5f632fa1a8b21b911dd.pdf).
- [ANSYS VM142 — concentração num furo](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/ans_vm/Hlp_V_VM142.html).

A avaliação do ciclo deve publicar também **falhas de implantação** e o diagnóstico de qualidade local, jamais apenas valores que pareçam confirmar Peterson.

## Execução externa confirmada — 08/11/2026

[Workflow #42525939565](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42525939565) **aprovado:** dois jobs de solução Elmer/SciPy, com seis modelos cada, e job de consolidação; 12 novos modelos e três recuperações sobre cada solução externa.

### Kt líquido no método C, com n24 histórico + n32/40/48 novos

| d/W | L/W | n24 | n32 | n40 | n48 | Δrel n40→n48 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.250 | 2 | 2.438535 | 2.439684 | 2.439871 | 2.439911 | 0.00164% |
| 0.250 | 4 | 2.434541 | 2.435829 | 2.435959 | 2.435985 | 0.00106% |
| 0.125 | 2 | 2.668119 | 2.675191 | 2.675876 | 2.676015 | 0.00517% |
| 0.125 | 4 | 2.666769 | 2.673998 | 2.674773 | 2.674876 | 0.00384% |

A diferença relativa entre as duas malhas mais finas caiu a **0,0011–0,0052%**, mas os quatro estudos do método C foram explicitamente classificados como **`nao_comprovada`** na ordem assintótica, sem emissão de GCI. Um único grupo de método A, d/W=.25 L/W=4, recebeu **GCI condicional** de 0,00190% (ordens 5,23 e 3,89; estabilidade relativa 34,6%). Isso **não equivale a prova robusta de erro absoluto**.

### Qualidade dos elementos

| d/W | L/W | Máx. razão de cordas total (n48) | Máx. na faixa do furo (n48) | Mín. ângulo vértice |
| ---: | ---: | ---: | ---: | ---: |
| 0,25 | 2 | 11.31 | 10.48 | 24.30° |
| 0,25 | 4 | 22.21 | 10.55 | 12.15° |
| 0,125 | 2 | 12.07 | 4.52 | 25.50° |
| 0,125 | 4 | 23.00 | 4.57 | 13.12° |

**Risco numérico relevante:** L/W=4 produz elementos com razão de cordas de até ~23 e ângulos de ~12°. Na malha mais fina, a primeira faixa radial para d/W=.25 chega a ~10,5 na razão de cordas; progressão radial fixa do Gmsh `q=1,12` não garante qualidade progressivamente melhor. Os jacobianos ainda foram positivos, mas não basta refinar sem reconsiderar a topologia e a distribuição de tamanhos.

### Rastreabilidade

[Dataset original completo com 12 casos e métricas](../dados/ciclo16-convergencia-fina-2026-11-08.json), importado do artefato real após validação de SHA256: `cba11d2427c5464ee13757f071a53ac18955abade7390648201023c6bb6784cd`. [Artefato bruto com 209 arquivos](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42525939565/artifacts/13634939407) (SHA256 `2555b9de0a36f5bf18f21fdadb7e0337b3f678b5ccb2f259459e4f76c641bde3`). [Importação por GitHub Actions validada](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42526568150).

### Decisão do ciclo

**Concluído:** três malhas finas por combinação, 12 modelos FEM reais, comparação de três recuperadores, diagnóstico de qualidade geométrica, balanço de força e emissão condicionada de GCI. **Não concluído:** independência de geração de malha mais saudável, evidência física da exatidão de Kt ou validação de um olhal real.

Handover: próximo ciclo deve construir **progressão radial dependente de n, controle da qualidade dos blocos externos e comparação explícita da tendência dos recuperadores** sem mudar a carga física. A [issue #17](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/17) permanece aberta para a mitigação da distorção geométrica; uma issue adicional pode detalhar o projeto da nova malha.
