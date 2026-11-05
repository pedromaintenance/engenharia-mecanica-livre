# Ciclo 05 — direitos por obra, fundamentos e benchmark numérico

**Data:** 2026-11-05. **Base:** v0.4, commit `bd530cdb`.

## Objetivo

Dar consequência ao roadmap em três vertentes: rastreabilidade de direitos, conteúdo técnico original e verificação quantitativa de modelo por elementos finitos. Nunca confundir pesquisa, implementação e certificação.

## Entregas de curadoria

- `src/engmec/data/direitos.json`: cinco obras/cursos com evidências primárias de licença, categoria de auditoria, restrição de reuso e data.
- `src/engmec/direitos.py` e `engmec direitos`: catálogo consultável e validações.
- `docs/governanca/auditoria-obras.md`: tabela com política MIT OCW, licença OpenStax e Engineering Statics. Materiais individuais de terceiros não auditados.
- `docs/governanca/politica-ia.md`: regras para descoberta bibliográfica, republicação e ingestão em IA.

## Entregas de conteúdo

Quatro fichas autorais: esforço normal, lei de Hooke axial, matriz de rigidez do elemento finito de barra, convergência e diferença entre verificação, validação física e aceitação operacional.

## Entregas computacionais

`fem_barra.py` calcula deslocamentos de barra 1D linear sob força concentrada e carga axial distribuída constante, fixa a extremidade esquerda, monta e resolve um sistema tridiagonal. Verifica solução analítica, tensão RMS, reação, trabalho/energia e conserva o modelo em SI.

O estudo de malha exige uma métrica com erro não nulo: para q uniforme, deslocamentos nodais são exatos, enquanto tensão linear exata é aproximada como constante por elemento e converge `O(h)`.

## Resultados de referência

| Condição | Valor analítico |
| --- | --- |
| L=2m, E=200GPa, A=1000mm², F=10kN, q=0 | deslocamento 0,1 mm |
| q=1000 N/m no mesmo caso | deslocamento 0,11 mm |
| Reação esquerda no caso com q | −12 kN |
| Erro RMS tensão com 1 elemento | ≈ 0,57735 MPa |
| Erro RMS tensão com 4 elementos | ≈ 0,14434 MPa |

## Limites e próximas tarefas

Não houve validação experimental, FEM 3D, execução de CalculiX/OpenFOAM, revisão jurídica exaustiva ou download de texto protegido. Permanecem a auditoria por **arquivo** (imagens e recursos), as fichas restantes e o benchmark cruzado com solver externo.

## Aceite

Commit, `engmec validar`, suíte de testes, compilação MkDocs e workflow Pages devem ser conferidos após implantação. O resultado técnico depende da verificação real do CI e não somente de arquivos escritos.

## Evidências de execução e publicação

- **Implementação:** [commit v0.5](https://github.com/pedromaintenance/engenharia-mecanica-livre/commit/2d9aaf967be0ecbe11814409fc441f60e254aa75).
- **Validação automática:** [workflow Qualidade técnica](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42052167589) concluído com sucesso; **37 testes** aprovados, `engmec validar` e `mkdocs build --strict` sem falha.
- **Publicação:** [workflow Pages](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42052167587) concluído com sucesso.
- **Próximo benchmark:** [issue #10](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/10) para validação cruzada com CalculiX ou equivalente.

**Aceite do ciclo 05:** implementação e publicação aprovadas em CI; revisão humana dos materiais e simulação externa continuam fora do escopo concluído.
