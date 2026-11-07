# Ciclo 10 — Chapa finita: carregamento físico, Kt bruto/líquido e tensão de borda

**Data:** 07/11/2026. **Versão:** 0.10.0. **Issue:** [#13](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/13).

## Lacuna corrigida do ciclo 09

O laboratório Kirsch possuía um domínio anular finito, mas sua fronteira externa era restringida pelos **deslocamentos exatos do problema infinito**. Isso era adequado para **verificação numérica**, porém não reproduzia o comportamento de uma chapa finita sob carga física na borda.

## Entregas

- **Novo solver adapter:** \`src/engmec/chapa_finita.py\`, com malha isoparamétrica Q8 de um quarto de chapa quadrada e furo central, borda direita tracionada por \`*CLOAD\` equivalente, bordo superior e furo livres, simetrias prescritas.
- **Pós-processamento:** leitura integral \`*EL PRINT COORD,S\` dos pontos de Gauss; tensões circunferenciais, extrapolação local de pico no ponto \`r=a,θ=90°\` com resíduos, checagem sintética do mesmo estimador em Kirsch, fatores \`Kt_gross\` e \`Kt_net\`.
- **Testes:** geometria e jacobiano, tração equivalente, carga total física, simetrias sem super-restrição, denominadores bruto/líquido, solução sintética no extrapolador e rejeição de arquivos incompletos.
- **Workflow externo:** CalculiX Ubuntu 24.04 com cinco execuções (3 malhas H/a=4 e 2 larguras maiores), logs e resultados temporários.
- **Documentação:** [Laboratório 10](../laboratorios/chapa-finita-furo.md), roadmap e instruções de benchmark.

## Critérios para declarar avanço

1. Positividade dos jacobianos e geometria de contorno quadrado (sem elementos cruzando a quina).
2. Carregamento aplicado por forças nodais consistentes, \`F_quarto=T·H·t\`.
3. Condições de simetria físicas; lado oposto virtual com força equilibrada e bordas horizontais livres.
4. Solver **real** executado, com \`S\` e \`COORD\` de todos os pontos de Gauss.
5. Tensão superficial somente como **extrapolação explicitamente qualificada**, não medição direta.
6. Relatório de sensibilidade de malha e largura com limites, inclusive falta de convergência.
7. CI, MkDocs e GitHub Pages verdes; arquivar dataset rastreável.

## Fronteiras científicas

A relação de Kirsch \`Kt=3\` é para placa infinita e não é solução exata para a chapa quadrada finita; a comparação é **assintótica e contextual**. Fatores bruto e líquido dependem do denominador. Não há validação experimental nem constituição de critério de aceitação de olhal/estrutura. Integração Gmsh e benchmark contra outras formulações devem permanecer no backlog.

## Evidência e handover

A primeira publicação deste relatório não equivale a solver validado. Registrar links de workflow, commit, número de testes, dataset com origem e, se necessário, falhas e correções de processo ao final da execução. Se qualquer gate falhar, manter issue #13 aberta e expor a falha.


## Execução real, resultados e aceite da etapa

[Workflow CalculiX #42421310615](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42421310615) aprovado, com **cinco execuções** no pacote `calculix-ccx 2.21-1` para Ubuntu 24.04. [CI geral #42421310617](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42421310617): **86 testes passaram**. [GitHub Pages #42421310616](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42421310616): publicado.

### Valores observados

| Relação H/a | Malha | Elementos | Kt bruto por extrapolação | Kt líquido |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 8×16 | 128 | 3,579821 | 2,684866 |
| 4 | 16×32 | 512 | 3,617689 | 2,713267 |
| 4 | 24×48 | 1.152 | 3,617450 | 2,713088 |
| 8 | 24×48 | 1.152 | 3,163999 | 2,768499 |
| 16 | 24×48 | 1.152 | 3,053753 | 2,862893 |

**Distinções decisivas:** os fatores de concentração são **estimativas de tensão superficial por mínimos quadrados em pontos de Gauss**. Não existe leitura direta no bordo, e a solução analítica `Kt=3` vale somente para placa infinita. O estudo de largura preserva uma **chapa quadrada**, variando largura e comprimento simultaneamente, de modo que não reproduz tiras longas de largura finita da literatura. Para `H/a=8,16`, **não existe teste de convergência de malha**.

O algoritmo de ajuste foi independentemente verificado com tensões de Kirsch amostradas nas coordenadas dos pontos de integração: o viés de ajuste em Kirsch foi preservado no dataset, distinto do erro numérico total da placa finita.

### Evidência

- [Dataset permanente](../dados/chapa-finita-furo-2026-11-07.json)
- [Laboratório 10](../laboratorios/chapa-finita-furo.md)
- [Artefato de solver](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42421310615/artifacts/13593462656), ID 13593462656, SHA256 6408e265cb691957b74419dded86127b61f1f213c377f2b32239c0938bb4adb1, retenção até 07/12/2026.
- [Workflow CI geral](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42421310617), 86 testes.
- O código pode ser executado sem CalculiX no modo `--somente-gerar`; a aprovação externa exige o workflow real.

### Handover

A experiência avançou do truncamento do domínio infinito com deslocamentos prescritos para uma **chapa realmente tracionada**. A issue #13 deve permanecer aberta porque ainda são requeridas **malhas independentes**, verificação contra literatura de mesmo aspecto, análise da incerteza da estimativa de tensão na superfície e critérios para eventual aplicação física. O próximo ciclo técnico deve tratar explicitamente esses gates sem tomar estabilização da estimativa como prova de exatidão.
