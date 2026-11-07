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


## Evidência final — ciclo 08 encerrado

**Execução externa:** [GitHub Actions #42411991123](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42411991123), CalculiX 2.21-1, seis execuções C3D8/C3D20R n=2/4/8. [Artefato e arquivos de solver](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42411991123/artifacts/13589339664). [Dataset permanente](../dados/comparacao-c3d8-c3d20r-2026-11-07.json).

**Resultado essencial:** C3D8 apresentou erros Uy de 29,7457%, 10,82515%, 3,36765% e RMS Sxx de 15,885/5,455/1,843 MPa. C3D20R apresentou Uy coincidente com referência na precisão da saída e RMS Sxx de 10/2/0,707 Pa; custos de DOF em n=8: 2.187 (C3D8) versus 8.019 (C3D20R).

**Validação automática:** [64 testes aprovados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42411991133), além de build estrito da documentação.

**Postmortem:** duas falhas de interface com CalculiX corrigidas com testes de regressão. Primeiro, `*ELEMENT` de 20 nós precisava de continuação em linha adicional (máximo 16 entradas por linha). Depois, valores de carga nodal de ruído numérico quase nulo geravam erro ao ler `*CLOAD`; agora são descartados por limiar relativo e o equilíbrio permanece monitorado. Terceiro ajuste: opção inválida `ELSET` retirada de `*EL FILE`.

**Conclusão:** para esta geometria e carregamento, o elemento quadrático reproduz o campo polinomial com erro próximo ao limite de precisão do relatório, enquanto o linear requer refinamento. Isso não é validação experimental, nem evidência universal de superioridade em quaisquer modos de falha.

**Próximo ciclo recomendado:** caso com gradiente de tensões concentrado, contorno curvo e comparação com solução de elasticidade de domínio conhecido, integrando também resultados de custos e incerteza.
