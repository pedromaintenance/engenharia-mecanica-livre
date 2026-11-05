---
name: integrar-simulador
description: "Acoplar projetos externos de CAD, CAE e termofluidos de forma modular, auditável e sem vendorização indevida."
license: MIT
---

# integrar-simulador

## Quando usar
FreeCAD, Gmsh, CalculiX, OpenFOAM, OpenModelica, CoolProp, Cantera ou biblioteca adicional.

## Procedimento
1. Identificar distribuição e versão exatas, licença, plataforma e requisitos.
2. Não confundir software listado no catálogo com integração executável.
3. Declarar entrada/saída padronizada em SI e dependência opcional.
4. Criar exemplo inteiramente autoral e benchmark analítico/documentado.
5. Registrar comandos, variáveis de ambiente, seed, versão do solver, critérios de convergência, logs e arquivos gerados.
6. Comparar solução numérica com caso de referência e reportar erro.
7. Evitar copiar modelos ou exemplos de terceiros sem licença verificada.

## Saída
Adaptador/roteiro reproduzível, benchmark e testes independentes.

## Aceite
Outro usuário repete o benchmark sem credencial nem dados internos.
