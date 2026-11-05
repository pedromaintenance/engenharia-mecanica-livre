# Engenharia Mecânica Livre

> Uma infraestrutura pública de conhecimento mecânico: aprender, pesquisar, modelar, verificar e aplicar — com fontes rastreáveis.

[**Acessar o portal**](https://pedromaintenance.github.io/engenharia-mecanica-livre/) · [**Roadmap mestre**](docs/roadmaps/master.md) · [**Agentes e skills**](docs/governanca/agentes.md) · [**Contribuir**](CONTRIBUTING.md)

## Estado: ciclo v0.6 (05/11/2026)

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
