# Engenharia Mecânica Livre

**Conhecimento verificável, ferramentas abertas e formação técnica em português.**

Este repositório constrói uma base pública de Engenharia Mecânica: referências, conceitos originais, trilhas de aprendizagem, calculadoras verificáveis, metodologias de diagnóstico e pontes para projetos científicos livres.

> **Estado:** fundação v0.1 (05/11/2026). É um catálogo inicial curado — **não** uma cópia da internet inteira ou uma biblioteca já exaustiva. Novas entradas exigem revisão técnica e de direitos.

## O que já existe

- **[Acervo catalogado](src/engmec/data/fontes.json)** — fontes oficiais, acadêmicas e softwares, com idioma, temas, titularidade, política de redistribuição e data de verificação.
- **[Documentação](docs/index.md)** — mapa do conhecimento, método de curadoria, governança e trilhas.
- **[Calculadoras Python](src/engmec/calculadoras.py)** — hidráulica, torque/potência, disponibilidade inerente e flexão simples, com hipóteses declaradas.
- **[CLI](src/engmec/__main__.py)** — pesquisa offline em fontes, validação de catálogo e cálculo estruturado.
- **[Testes](tests/)** — testes de valores de referência, consistência e limitações.
- **[Site MkDocs](mkdocs.yml)** — publicação pesquisável opcional via GitHub Pages.

## Instalação e primeiros comandos

Requer **Python 3.10+**. Na raiz do projeto:

```bash
python -m pip install -e .
engmec fontes --consulta termodinamica
engmec validar
engmec calcular potencia --torque-nm 250 --rpm 1800
engmec calcular cilindro --pressao-bar 180 --diametro-mm 100 --haste-mm 60 --curso retracao
engmec calcular disponibilidade --mtbf-h 100 --mttr-h 5
python -m unittest discover -s tests -v
```

Para o site local:

```bash
python -m pip install -r requirements-docs.txt
mkdocs serve
```

## Organização por áreas

Fundamentos físico-matemáticos; estática, dinâmica e resistência dos materiais; materiais e tribologia; termodinâmica, transferência de calor e fluidos; elementos e projeto de máquinas; fabricação e metrologia; sistemas hidráulicos e diesel; manutenção, confiabilidade e segurança; CAE, CAD, FEM e CFD; métodos computacionais e ciência de dados.

O catálogo é extensível, com prioridade inicial a fontes primárias e abertas. Qualquer especificação de fabricante deve trazer aplicação exata (modelo, número de série, revisão e contexto), não ser generalizada.

## Princípios irrenunciáveis

1. **Fonte e evidência acima da aparência de autoridade.** Diferenciar medição, modelo, hipótese e diagnóstico confirmado.
2. **SI e rastreabilidade.** Toda calculadora informa unidades, limites e pressupostos, com teste.
3. **Licença por item.** Link público não equivale a direito de redistribuição. Conteúdo de ISO, ASME e OEM continua sob seus titulares.
4. **Separação de segurança.** Material educativo não substitui projeto assinado, profissional habilitado, procedimentos oficiais, NR ou manual do fabricante.
5. **Independência institucional.** Nada de documentos internos, dados confidenciais, credenciais, telemetria identificável ou materiais proprietários compartilhados sem autorização.

## Evolução

Veja [arquitetura](docs/arquitetura.md), [roadmap](docs/roadmap.md) e [contribuições](CONTRIBUTING.md). A licença MIT já presente no repositório rege **nosso código e documentação original**; não relicencia nenhuma obra externa catalogada.
