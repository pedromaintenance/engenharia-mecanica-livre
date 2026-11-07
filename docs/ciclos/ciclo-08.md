# Ciclo 08 — Elementos lineares versus quadráticos na flexão tridimensional

**Data:** 07/11/2026. **Issue de referência:** [#12](https://github.com/pedromaintenance/engenharia-mecanica-livre/issues/12). **Linha de base:** v0.7 `d87683cf`.

## Pergunta mecânica

No ciclo 07, elementos C3D8 mostraram erro elevado em flexão, reduzido por refinamento. Elementos de 20 nós com interpolação quadrática podem reproduzir melhor o campo de deslocamentos quadrático da solução de elasticidade. É necessário provar a diferença com **resultado externo** e não com expectativa de manual.

## Implementação

- `src/engmec/comparar_elementos.py`: converte malha C3D8 para C3D20R preservando vértices e criando midside nodes compartilhados, aplica forças consistentes Q8 com quadratura Gauss 3×3 e gera *EL PRINT COORD,S.
- `tests/test_comparar_elementos.py`: verifica funções Q8, soma de forças e momentos, conectividade, exemplo de parser e tratamentos de erro.
- `scripts/comparar_elementos.py`: agrega resultados por família e malha, mede deslocamentos, erro RMS Sxx nos pontos de Gauss, tensões não axiais e custo de execução.
- `tests/test_resumo_elementos.py`: garante reprovação por ausência de resultado e comparação consistente.
- `.github/workflows/comparar-elementos.yml`: executa seis casos (2³,4³,8³ de ambas as famílias), valida logs e arquiva resultados.
- `docs/laboratorios/comparar-elementos-fem.md`: fundamentação mecânica, roteiro de execução e limites.

## Critério técnico

Referencia fixa: `Uy(L,0,0)=0,2mm`, `Ux(L,b/2,0)=-0,1mm`, `σxx=-Eκy`; equilíbrio por momentos opostos e forças resultantes nulas. Comparar valores de stress no **mesmo sistema global** e nas coordenadas de Gauss provenientes do .dat.

Critérios: parser deve exigir 8 IP por elemento, erro e contornos rastreáveis; C3D20R menor erro de deslocamento e tensão na malha grossa; reação de equilíbrio dentro de 1%. Sem execução real, **não publicar números observados**.

## Handover

Conferir commit, CI geral, workflow de benchmark e publicação. Registrar números realmente medidos no repositório com proveniência, sem confundir tempos de execução com benchmark de hardware. Se a execução externa revelar falhas, manter issue #12 aberta e documentar diagnóstico.

## Limites

A análise é um teste de verificação numérica em flexão elástica idealizada. Não valida resistência de equipamento pesado, materiais reais, fadiga ou carga de contato.
