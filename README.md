# Engenharia Mecânica Livre

> Uma infraestrutura pública de conhecimento mecânico: aprender, pesquisar, modelar, verificar e aplicar — com fontes rastreáveis.

[**Acessar o portal**](https://pedromaintenance.github.io/engenharia-mecanica-livre/) · [**Roadmap mestre**](docs/roadmaps/master.md) · [**Agentes e skills**](docs/governanca/agentes.md) · [**Contribuir**](CONTRIBUTING.md)

## Estado: ciclo v0.18 (08/11/2026)

- **Site público** em MkDocs/GitHub Pages, com publicação automatizada.
- **Catálogos estruturados:** 20 fontes gerais anteriores + 10 cursos individuais + 20 portais + 17 ferramentas (67 registros em níveis distintos), além de 5 registros de licença/documentação por obra sem somá-los como novas fontes.
- **Formação:** grade aberta por áreas da Engenharia Mecânica, seis trilhas por objetivo e critérios de avaliação.
- **Ferramental funcional:** oito calculadoras em Python, FEM 1D e um adaptador para benchmark CalculiX 3D C3D8, com geração de malha, execução externa opcional e verificação de resultados.
- **Governança reusável:** [AGENTS.md](AGENTS.md), 8 agentes especializados, 11 skills e roadmaps temáticos.
- **Pesquisa por APIs:** cliente de metadados Crossref/OpenAlex com limite, deduplicação local e revisão obrigatória; candidatos não entram automaticamente no acervo.
- **Auditoria de direitos:** cinco registros documentais de obras/cursos, separando política de portal, obra e exceções de terceiros.
- **Conteúdo autoral:** quatro fichas técnicas (tensão, Hooke, elemento finito 1D, convergência).
- **Próximos passos:** revisar assets específicos, ampliar fichas, comparar o FEM autoral com solver externo e integrar ferramentas opcionais.

**Importante:** descoberta de um portal **não é auditoria de todo seu acervo**; software catalogado **não significa integração concluída**. As referências originais ficam nas instituições e as permissões são verificadas por item.

## Ciclo 14 — três recuperadores de tensão na mesma solução FEM

O [workflow externo aprovado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42502117900) aplicou três métodos de estimativa superficial de Kt bruto ao **mesmo vetor de deslocamentos Elmer** de seis malhas: (A) gradiente direto Q8 na parede do furo, (B) extrapolação de seis coeficientes de Gauss 3×3 e (C) ajuste ponderado local de quatro coeficientes. A amplitude entre recuperadores caiu de **0,2698→0,0034 em W=80 mm** e de **0,6567→0,0126 em W=160 mm**, com refinamento de 128 a 1.152 elementos. **Essa amplitude mede sensibilidade do método, não incerteza física certificada.** [Laboratório](docs/laboratorios/recuperacao-tensoes-furo.md) · [dataset real](docs/dados/ciclo14-recuperacao-tensoes-2026-11-08.json).

## Ciclo 15 — influência de comprimento e largura em chapas perfuradas

A [v0.15](docs/laboratorios/chapa-retangular-comprimento.md) generaliza o problema de chapa quadrada para **retângulos de comprimento L e largura W independentes**, com tração no eixo x, furo central e simetria. Foram executadas [18 simulações FEM externas](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42522437925), com `L/W=1,2,4`, `d/W=0,25 ou 0,125` e 3 malhas. O caso `L/W=1` reproduziu o ciclo 14; os retângulos longos aproximaram a curva de **Peterson em Kt da seção líquida**, sem extrapolar indevidamente a fórmula para chapas quadradas. Para d/W=0,25, L/W=4 e 1152 elementos Q8, Kt líquido foi **2,4345** (Peterson ~**2,4203**). A proximidade ainda não é prova de convergência ou validação física. [Dataset de auditoria](docs/dados/ciclo15-chapas-retangulares-2026-11-08.json).

## Ciclo 16 — convergência fina e qualidade geométrica Q8

A [v0.16](docs/laboratorios/convergencia-fina-retangulo.md) amplia os modelos de chapa perfurada para **2.048, 3.200 e 4.608 elementos Q8**, com [12 simulações externas Elmer/SciPy aprovadas](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42525939565). O Kt líquido do recuperador C variou apenas **0,0011–0,0052%** entre n40 e n48, mas o teste de ordem assintótica **não aprovou GCI para nenhuma das quatro séries C**. Em `L/W=4`, alguns elementos apresentaram razão de cordas de **22–23** e ângulos mínimos de **12–13°** — refinamento sem controle de forma não garante qualidade. [Dados integrais auditados](docs/dados/ciclo16-convergencia-fina-2026-11-08.json), importados automaticamente após validação de SHA256. Nenhuma conclusão habilita dimensionamento ou manutenção de estruturas reais.

## Ciclo 17 — progressão radial Q8 escalonada

A [v0.17](docs/laboratorios/progressao-radial-q8.md) adiciona uma estratégia opcional `q(n)=exp(24 ln(1,12)/n)` de progressão radial às malhas Gmsh Q8. Foram executadas [16 simulações externas Elmer/SciPy](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42546868607), confrontadas com as 16 malhas de progressão fixa dos ciclos anteriores. Na malha n48, **a maior razão de cordas caiu ~48%** nas quatro geometrias, e o **Kt recuperado por C passou o gate condicional de Richardson/GCI nas quatro séries**. Porém, a **qualidade perto do furo piorou em d/W=0,125 e L/W=4** (razão máxima da 1ª faixa 4,57→8,07), e a tensão radial residual na parede livre aumentou. **Melhora global ≠ validação local nem autorização de cálculo estrutural real.** [Dataset integral aprovado](docs/dados/ciclo17-malha-radial-2026-11-08.json).

## Ciclo 18 — experimento angular e resultado negativo

A [v0.18](docs/laboratorios/distribuicao-angular-q8.md) testou dois caminhos para melhorar a qualidade dos Q8 junto a um furo: uma interface interna `Spline`, **bloqueada por jacobianos não positivos**, e uma redistribuição angular conservadora, **executada em 16 modelos reais Elmer/SciPy** e comparada com o ciclo 17. Na malha n48, a nova grade aumentou o alongamento máximo da primeira faixa em aproximadamente **19% nas quatro geometrias**; o resíduo `σrr/T` na parede livre também piorou, embora os Kt líquidos C variassem menos de 0,004%. **A opção angular uniforme continua padrão.** O resultado negativo está [documentado e versionado em JSON](docs/dados/ciclo18-angular-2026-11-08.json); próximo gate é construir malha multibloco com faixa anular independente. [Workflow final aprovado](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42550543935).

## Visitar os acervos

| Acervo | Conteúdo | Local |
| --- | --- | --- |
| Fontes gerais | 20 fontes-base, educação, ciência, normas e software | [JSON](src/engmec/data/fontes.json) |
| Cursos | 10 disciplinas universitárias identificadas por URL | [Catálogo](docs/catalogos/cursos.md) |
| Portais | 20 instituições, bibliotecas, órgãos e APIs | [Catálogo](docs/catalogos/portais.md) |
| Ferramentas | 17 softwares, bibliotecas e simuladores | [Catálogo](docs/catalogos/ferramentas.md) |

## Benchmark numérico de barra axial

Um solver independente de elementos finitos 1D compara deslocamentos, reação e energia à solução analítica, com convergência do **erro RMS de tensão** para malhas de 1 a 32 elementos. Não foi integrado nem validado com CalculiX ou FreeCAD, e não serve para dimensionamento de segurança. [Laboratório completo](docs/laboratorios/benchmark-barra-fem.md).

## Comparação com CalculiX 3D

O ciclo 06 acrescentou geração de malhas C3D8 com força axial distribuída e um workflow Ubuntu 24.04 que instala o CalculiX real. Os resultados do solver são analisados a partir de arquivos `.dat`; **o benchmark externo de tração uniforme foi executado com sucesso em quatro malhas (CalculiX 2.21-1)**, mas não cobre convergência não trivial nem validação experimental. [Evidência](docs/dados/calculix-c3d8-2026-11-05.json). [Laboratório 06](docs/laboratorios/calculix-3d.md).

## Laboratório de flexão pura 3D

O ciclo 07 introduz um caso de elasticidade 3D em que a **tensão axial varia linearmente na seção** e o campo de deslocamento possui termos quadráticos. O adaptador CalculiX C3D8 gera trações nodais consistentes nas duas faces, apoios mínimos, extrai resultados `U/RF` e avalia erros em malhas 2³, 4³, 8³ e 16³. **O workflow externo passou:** CalculiX 2.21-1 executou as quatro malhas; erro de Uy diminuiu de 29,75% para 0,99%. [Evidência permanente](docs/dados/flexao-pura-3d-2026-11-05.json). [Laboratório 07](docs/laboratorios/flexao-pura-3d.md).

## Comparação C3D8 × C3D20R (ciclo 08)

O novo laboratório gera malhas C3D20R com nós de meio de aresta compartilhados, aplica trações de flexão por integração consistente Q8 e extrai **tensões e coordenadas de Gauss no .dat do CalculiX**. O comparador reúne erros RMS das tensões e deslocamentos, DOFs estimados, resíduos de equilíbrio e tempos de execução. A conclusão exige **execução externa verificada**; não se presume superioridade do elemento apenas pela teoria. [Laboratório 08](docs/laboratorios/comparar-elementos-fem.md).

## Benchmark de furo circular — ciclo 09

Foi desenvolvido um gerador de quarto de anel curvo com elementos **CPS8R**, solução analítica de Kirsch em **tensão plana**, controle positivo de jacobianos e leitura de tensões dos pontos de integração. O resultado será considerado **validado somente após a execução externa**: o dado `Kt=3` pertence à solução analítica, e uma tensão calculada no primeiro ponto de Gauss **não é** o pico real na superfície do furo. [Laboratório 09](docs/laboratorios/kirsch-furo.md).

## Chapa finita tracionada — ciclo 10

Novo benchmark de **chapa quadrada com furo central**, elemento CPS8R, tração uniforme efetivamente aplicada na borda e contornos superior/furo livres. O modelo diferencia a tensão nominal **bruta e líquida**, reporta tensões em pontos de integração e introduz **estimativa superficial por extrapolação local**, com aferição do algoritmo usando Kirsch sintético. **Não existe resultado externo certificado antes da execução do workflow**. [Laboratório 10](docs/laboratorios/chapa-finita-furo.md).

## Independência geométrica e verificação de largura — ciclo 11

A v0.11 introduz **malha quadrática Gmsh gerada de forma independente**, importação MSH2, reconstrução física da carga de borda e análise de tensões no CalculiX. Os resultados Gmsh são confrontados com o gerador polar autoral, mantendo mesmo problema físico e solver. Também estão programados novos refinamentos para chapas H/a=8 e 16, cada uma com n=16,24,32. **Não equivale a validação independente do solver ou da integridade estrutural real.** [Laboratório 11](docs/laboratorios/gmsh-chapa.md).

## Dois solvers FEM independentes — ciclo 12

O [Laboratório 12](docs/laboratorios/dois-solvers-q8.md) confronta o CalculiX CPS8R com um **novo solucionador FEM Q8 implementado em Python/NumPy/SciPy**. Ambos resolvem **exatamente a mesma malha Gmsh MSH2** (hashes idênticos) sob tração real. O CalculiX estima Kt por ajuste de tensões de Gauss; a implementação autoral calcula o gradiente do deslocamento **diretamente na parede do furo**. Quatro pares externos foram executados; as diferenças relativas observadas ficaram entre **0,22% e 2,29%**. O código Python ainda é um **protótipo de pesquisa, não um segundo software industrial validado**. [Dataset e limitações](docs/dados/ciclo12-solvers-independentes-2026-11-07.json).

## Solucionador FEM externo Elmer — ciclo 13

A versão 0.13 integra **ElmerGrid e ElmerSolver**, além de Gmsh, CalculiX e o FEM independente em Python/SciPy. O novo laboratório utiliza o **Elmer StressSolver em tensão plana** com a mesma geometria de chapa quadrada finita tracionada e compara deslocamentos e tensões com o SciPy usando **um recuperador de gradiente comum**. A finalidade é separar melhor diferenças do campo de deslocamentos e do pós-processamento. [Laboratório 13](docs/laboratorios/elmer-fem-independente.md). A comparação permanece educativa, não habilita engenharia de componentes reais.

## Grade e ferramentas

[Grade por ciclos](docs/formacao/grade.md) · [Trilhas](docs/formacao/trilhas.md) · [Guia de calculadoras](docs/guia-calculadoras.md) · [Metodologia](docs/metodologia.md)

```bash
git clone https://github.com/pedromaintenance/engenharia-mecanica-livre.git
cd engenharia-mecanica-livre
python -m pip install -e .
engmec validar
engmec recursos --tipo cursos --consulta dinamica
engmec recursos --tipo portais --consulta NASA
engmec recursos --tipo ferramentas --area FEM
engmec descobrir --fonte crossref --consulta "bearing fatigue" --limite 5
engmec fontes --consulta termodinamica
engmec calcular potencia --torque-nm 250 --rpm 1800
engmec direitos --id openstax-univphysics1
engmec fem-barra --comprimento-m 2 --area-mm2 1000 --e-gpa 200 --forca-n 10000 --carga-linear-n-m 1000 --estudo-malha
python -m engmec.calculix --somente-gerar --nx 4 --saida build/calculix/nx-4
python -m engmec.flexao_calculix --nx 4 --ny 4 --nz 4 --somente-gerar --saida build/flexao-calculix/n-4
python -m engmec.comparar_elementos --elemento C3D20R --nx 4 --ny 4 --nz 4 --somente-gerar --saida build/comparacao/c3d20r/n-4
# Para executar o solver, instale CalculiX e remova --somente-gerar
python -m unittest discover -s tests -v
```

Para executar a documentação local:

```bash
python -m pip install -r requirements-docs.txt
mkdocs serve
```

## Padrões de engenharia

- Grandezas e resultados em SI, hipóteses, domínio de validade e testes independentes.
- Separação entre observação, efeito, hipótese, mecanismo, causa imediata e causa raiz.
- Referências oficiais identificadas com versão, autor, URL e data; direitos verificados por obra.
- Conteúdo educativo não substitui projeto, inspeção habilitada, normas atualizadas, procedimentos de segurança nem OEM.
- Dados fictícios para exemplos de equipamentos, sem publicar documentos internos ou informações privadas.

## Agentes e continuidade

Os agentes são perfis versionados em [`.github/agents/`](.github/agents) e as skills são instruções especializadas em [`.github/skills/`](.github/skills). **Não são tarefas agendadas autonomamente**; devem ser invocados por ambientes compatíveis e sempre seguem [AGENTS.md](AGENTS.md).

Para continuar: abra [roadmap mestre](docs/roadmaps/master.md), selecione um [issue](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues), carregue o perfil e a skill adequada, produza mudanças, execute CI e registre em [ciclos](docs/ciclos/ciclo-02.md).

## Licenças

O código e a documentação original deste repositório estão sob a licença MIT existente em [LICENSE](LICENSE). Obras externas conservam seus próprios direitos; uma URL aberta **não autoriza reprodução, tradução ou inclusão em corpus de IA**. O projeto usa links e metadados como padrão conservador.

**Verificação de publicação do ciclo 07:** [CI com 53 testes](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42064616968), [benchmark externo CalculiX](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42064616852), [GitHub Pages](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42064616933). Nenhum resultado indica certificação de projeto.

**Execução do ciclo 08 confirmada:** o [comparativo C3D8/C3D20R no CalculiX](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42411991123) passou com seis simulações reais. [64 testes automatizados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42411991133) passaram. O C3D20R apresentou erro de deslocamento não resolvido pela precisão textual e erro RMS Sxx na faixa de 0,707–10 Pa no campo de flexão estudado, comparado a 1,84–15,9 MPa do C3D8. [Dataset de evidência](docs/dados/comparacao-c3d8-c3d20r-2026-11-07.json).

**Ciclo 09 — verificação Kirsch:** quatro casos [executados no CalculiX 2.21-1](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42415560152). Erro RMS tensorial ponderado por área: **0,521%→0,117%→0,072%** em 32, 128 e 512 elementos; indicador interior junto ao furo de 2,494 a 2,985 contra referência **analítica de bordo** `Kt=3`. [Dataset](docs/dados/kirsch-cps8r-2026-11-07.json). **Não** constitui modelo de placa finita tracionada, nem avaliação de equipamento real.

**Ciclo 10, dados externos:** [cinco casos de chapa quadrada finita realmente tracionada no CalculiX](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42421310615). A estimativa de Kt bruto após refinamento em W=80 mm estabilizou em ~3,6175; com uma malha em W=160/320 mm, deu ~3,1640/~3,0538. **Esses são resultados por extrapolação de tensões de Gauss, não leitura direta de pico nem validação experimental.** [JSON permanente](docs/dados/chapa-finita-furo-2026-11-07.json); [laboratório](docs/laboratorios/chapa-finita-furo.md).

**Ciclo 11 verificado:** [Gmsh 4.12.1 + CalculiX 2.21-1](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42422518394) executaram **9 casos**, incluindo malha CAD externa independente e refinamento H/a=8/16 até 2.048 elementos. Para W=80 mm e 1.152 elementos, Kt bruto por extrapolação: **3,61471 (Gmsh)** contra **3,61745 (gerador autoral)**, diferença de **0,076%**. [Dados JSON](docs/dados/ciclo11-gmsh-chapa-2026-11-07.json). A concordância entre geradores não implica validação independente do solver.
