# AGENTS.md — Engenharia Mecânica Livre

Este arquivo é o **contrato permanente** de qualquer agente atuando neste repositório. Consulte também `docs/roadmaps/master.md`, `docs/governanca/curadoria.md`, `docs/governanca/agentes.md` e `docs/ciclos/`.

## Missão

Construir um acervo aberto de **Engenharia Mecânica** em português, rigoroso, útil para estudo, projeto e análise de manutenção. Priorize **evidência material, precisão científica, SI, segurança, licenças, reprodutibilidade e utilidade prática**.

## Regras operacionais

1. **Nunca inventar** fonte, DOI, norma, número de peça, pressão, torque, especificação OEM, resultados de testes ou status de publicação.
2. **Contextualizar o modelo físico:** entradas e saídas em SI, hipóteses, limites, unidades, sinais, equações, verificações e revisão.
3. **Separar categorias:** observação, hipótese, mecanismo, causa imediata, causa raiz e efeito operacional. Diagnóstico não é conclusão sem teste.
4. **Direitos autorais:** acesso aberto não implica permissão para copiar. L0 metadados/link por padrão; L1/L2 somente com direito demonstrado por item. Consultar `src/engmec/data/direitos.json` e `auditar-obra` para restrições de IA e exceções de conteúdo.
5. **Segurança:** conteúdo educativo não substitui manual OEM, procedimento local, habilitação, norma atualizada e controles de risco; não recomendar bypass de segurança.
6. **Privacidade:** nunca publicar SAP, dados internos de empregador, equipamentos identificáveis ou informações pessoais sem permissão. Usar dados sintéticos em exemplos.
7. **Descoberta:** usar APIs oficiais com limites; candidatos não são conteúdo aprovado, não importar PDFs ou abstracts protegidos automaticamente.
8. **Arquitetura:** manter `catalogos/*.json`, `docs/`, `src/engmec/`, `tests/` e `.github/` coerentes. Evitar dependência pesada obrigatória.
9. **FEM e simulação:** usar `benchmark-fem`, checar equilíbrio, energia e uma grandeza com erro de discretização efetivamente não nulo.
10. **Qualidade:** executar `engmec validar`, `python -m unittest discover -s tests -v` e `mkdocs build --strict`. CI verde antes de afirmar entrega.
11. **Sem autonomia fictícia:** perfis de agentes/skills são instruções reutilizáveis; não implicam processos agendados ou acesso automático à internet.
12. **Handover:** ao terminar, registrar artefatos, origem das informações, evidências, limitações, falhas e próxima tarefa.

## Fluxo padrão

**Issue → Pesquisa → Curadoria jurídica → Conteúdo/código → Testes → Auditoria independente → PR/commit → CI/Pages → Registro de ciclo.**

## Convenções

Idioma português do Brasil para texto original, nomenclatura de grandezas com notação técnica correta, IDs permanentes em kebab-case, JSON UTF-8 com schema; datas ISO `YYYY-MM-DD`. Não alterar norma ou parâmetro OEM a partir de analogia.

## Como chamar especialistas

Arquivos em `.github/agents/*.agent.md`; skills em `.github/skills/*/SKILL.md`. Use a skill apropriada para a tarefa, mas valide a saída com `verificar-modelo` e curadoria quando aplicável. As ferramentas específicas só podem ser usadas se estiverem disponíveis no ambiente executor.

## Gate do ciclo 08

Modelos FEM com famílias de elementos distintas devem manter mesmo modelo físico e referência. Ao comparar tensões, preferir IP do `.dat` ao valor extrapolado do `.frd`; informar métrica de erro e localização de medição. Uma melhoria em deslocamento não é autorização de projeto: avaliar gradientes, contato e mudanças de hipóteses separadamente. Uma skill atualizada em `.github/skills/benchmark-fem/SKILL.md` descreve o procedimento C3D8/C3D20R.

## Gate científico do ciclo 09

No benchmark de Kirsch, **Kt analítico** e **tensão numérica no interior** são conceitos distintos. Não declarar fator de concentração numérico na borda sem pós-processamento e verificação específica. Para truncamento externo com deslocamentos exatos, não afirmar ter simulado uma placa de largura finita sob tensão remota uniforme. Conservar arquivos brutos de solver, fontes técnicas, geometria e qualidade de malha para replicação. Consulte `docs/laboratorios/kirsch-furo.md` e `.github/skills/benchmark-fem/SKILL.md`.

## Contorno físico finito — ciclo 10

Para uma chapa realmente tracionada, não impor deslocamentos exatos de Kirsch na borda externa nem declarar `Kt=3` solução do domínio finito. Requer-se evidência de *CLOAD* física nos nós da borda, contornos livres no topo e no furo, conversão correta bruto/líquido e estimativa de pico baseada em pós-processamento explicitamente qualificado. Usar `docs/laboratorios/chapa-finita-furo.md` e `src/engmec/chapa_finita.py` como referência do caso.

## Ciclo 11 — verificação de malha independente

Benchmark de chapa quadrada finita com malha externa Gmsh deve manter rigorosamente as cargas físicas, os eixos de simetria e as definições dos fatores de concentração. Acordo de duas malhas usando o mesmo solver **não representa validação completa do FEM**; indicar diferenças de distribuição e jacobiano em cada caso. Não alegar convergência em H/a=8/16 antes de executar três malhas por largura. Consulte `src/engmec/gmsh_chapa.py` e `docs/laboratorios/gmsh-chapa.md`.

## Ciclo 12 — dois solucionadores, níveis distintos de independência

A comparação Python Q8/SciPy × CPS8R/CalculiX exige identidade do `.msh` comprovada por SHA256, mesma tração e D de tensão plana e documentação de diferenças de quadratura e recuperação de tensão. Não declarar o protótipo SciPy como software industrial homologado nem tratar a concordância de Kt como validação física. Conferir `docs/laboratorios/dois-solvers-q8.md` e `src/engmec/fem2d_indep.py` antes de alterar os benchmarks.

## Ciclo 13 — Elmer FEM externo

Na verificação de tensão superficial, reconhecer a diferença entre **solvers independentes** (CalculiX, Elmer e FEM Q8 SciPy) e **pós-processamento compartilhado**. Comparar a mesma malha, propriedades constitutivas, estado plano e carregamento; documentar a conversão Gmsh→ElmerGrid, os IDs de fronteira e coordenadas de referência no VTU. O valor de Kt superficial por `DBu` continua sujeito a erro numérico e não constitui validação experimental. Referências: `docs/laboratorios/elmer-fem-independente.md` e `src/engmec/elmer_chapa.py`.

## Ciclo 14 — três recuperadores de tensão

Exigir o **mesmo vetor nodal Elmer** quando comparar A `D B u` diretamente na borda, B Gauss seis coeficientes e C patch ponderado de quatro coeficientes. O último é **experimental**, não certificado SPR/Zienkiewicz–Zhu. Publicar os vieses observados no campo analítico de Kirsch, especialmente os valores grandes na malha grosseira W160/128, e a tensão radial residual da parede livre. A amplitude entre Kt não fornece limite absoluto do erro real nem autorização de reparo industrial. Ver `docs/laboratorios/recuperacao-tensoes-furo.md`.

## Ciclo 15 — comparação com referências de tiras longas

Distinguir comprimento L na direção x da tração, largura W na direção y e furo d, `L/W=Hx/Hy`, `d/W=a/Hy`. O ajuste Peterson `3−3.14ρ+3.667ρ²−1.527ρ³` usa **seção líquida**, portanto converter fatores FEM de base bruta antes de comparar. O domínio quadrado L/W=1 deve reproduzir o ciclo 14; as outras geometrias devem manter a mesma carga física, material e simetria, mas a mudança de forma dos elementos exige refinamento adicional. Não validar Kt real de olhal de mineração sem ensaio e contato específicos. [Lab15](docs/laboratorios/chapa-retangular-comprimento.md).

## Ciclo 16 — não confundir estabilização aparente com validação

O [dataset integral](docs/dados/ciclo16-convergencia-fina-2026-11-08.json) contém 12 execuções Elmer reais e estudos n24/32/40/48. Diferenças de Kt C entre n40/48 são pequenas (0,0011–0,0052%), **mas GCI C não foi emitido por falta de ordem estável**. Uma série A teve GCI condicionado sob critérios explicitados, sem valor de aceitação industrial. A progressão geométrica fixa da malha Gmsh produziu elementos com razão de cordas ~23 e ângulo mínimo ~12° em L/W=4; próxima tarefa deve tratar **qualidade geométrica** e manter mesmo carregamento e material antes de afirmar convergência. Não transformar GCI em tensão admissível ou certificado de integridade.

## Ciclo 17 — progressão radial e perigo de melhorias parciais

O padrão do código continua **`--progressao-radial fixa`** para não quebrar workflows antigos. A alternativa `escalonada` mantém `q(n)^n=1,12^24` e foi verificada em [16 execuções reais](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42546868607). A pior razão geométrica global n48 caiu ~48% e as quatro séries C passaram GCI condicionado; **isso não certifica melhor qualidade próxima ao furo**. Em d/W=.125 L/W=4, a primeira faixa Q8 piorou 4,57→8,07 e o resíduo `σrr/T` aumentou ~59×. Não elevar estratégia a novo default nem usar Kt para aceitação estrutural sem comparar qualidade de todo o domínio, amostras de Gauss, convergência, tração livre e uma referência física pertinente. [Dados](docs/dados/ciclo17-malha-radial-2026-11-08.json).

## Ciclo 18 — resultado negativo é resultado de engenharia

A nova opção `--distribuicao-angular ampliada-topo` permanece **experimental**, após [16 FEM reais](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42550543935) demonstrarem ~19% de piora da razão máxima de cordas na primeira faixa em n48, com resíduo `σrr/T` também maior; o padrão `uniforme` **não deve ser alterado**. A hipótese de curvar a ligação interna `Line(3)` falhou em testes Gmsh por jacobianos não positivos e foi removida; nenhuma solução FEM inválida foi autorizada. Kt quase igual e GCI C condicionado não demonstram precisão física de tração radial. Próximo passo deve construir anel próprio em torno do furo com transição externa e verificar invariância de carga, simetrias, superfícies livres e qualidade local. [Dataset](docs/dados/ciclo18-angular-2026-11-08.json).

## Ciclo 19 — anel de furo Q8 é experimento, não novo padrão

[16 FEM externos e dataset completo](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/docs/dados/ciclo19-anel-multibloco-2026-11-09.json). A opção `--topologia anel-quatro-blocos` cria um anel `a≤r≤2a` em duas superfícies transfinite e duas externas, com arcos compartilhados e **n_t arestas Q8 verificadas com duas incidências e nó médio único**. Pior alongamento da primeira faixa caiu em 3/4 casos, mas **pior razão global aumentou em 4/4**, chegando a 33,83, e `σrr/T` residual da parede livre piorou 4/4. **Manter `dois-blocos` como default**. Nunca declarar GCI condicionado no Kt como aprovação de tração livre ou qualidade em canto externo. Próxima tarefa: exterior com mais blocos e transição de elementos mais balanceada. Nenhum resultado é critério de segurança industrial.

## Ciclo 20 — interfaces extras não garantem precisão

A variante `--topologia anel-seis-blocos` é experimental. O CAD possui duas superfícies anulares, duas intermediárias e duas externas por pares, com interfaces Q8 conformes nos raios `2a` e no retângulo `Xm=√(2a Hx), Ym=√(2a Hy)`. Não alterar default `dois-blocos`. Exigir smoke CAD de 16 geometrias, conservação dos contornos, jacobianos positivos, carga real, verificação do campo de deslocamentos Elmer × SciPy e comparação de alongamento global/local, ângulos e tração livre com ciclo 19. Não chamar smoke de validação do FEM nem usar Kt/GCI como aprovação industrial. Consulte `docs/laboratorios/transicao-externa-seis-blocos.md` e `docs/ciclos/ciclo-20.md`.

## Ciclo 20 — verificação externa final

[16 modelos reais e dataset com hashes](docs/dados/ciclo20-transicao-externa-2026-11-10.json) e [execução 42780634538](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42780634538) demonstraram melhoria no alongamento global em 4/4 geometrias, mas piora dos ângulos mínimos em 4/4, sem ganho da tensão radial recuperada no furo. As quatro séries C apresentaram GCI condicional ~0,10%, não estimativa completa de erro. Não promover `anel-seis-blocos` nem usar Kt para aceitar reparo estrutural. Próximo gate: reduzir ângulos agudos e conferir resíduo vetorial ao longo de todo o furo.
