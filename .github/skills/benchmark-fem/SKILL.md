---
name: benchmark-fem
description: Desenvolver e revisar benchmarks de elementos finitos com equilíbrio, solução analítica, estudo de malha, tolerâncias e fronteiras de validade, sem confundir verificação numérica com segurança de projeto.
license: MIT
---

# Benchmark FEM

1. Definir problema de valor de contorno, propriedades, carregamento, geometria e sinal.
2. Identificar uma solução analítica independente ou caso publicado verificável.
3. Discretizar e montar o sistema, explicando funções de forma e cargas nodais consistentes.
4. Conferir condições de contorno; evitar sistema singular e sobre-restrição.
5. Comparar deslocamento, esforços/reação, energia e erros físicos por elemento.
6. Fazer refinamento de malha usando grandeza de erro *não identicamente nula*.
7. Incluir cargas em sentidos opostos, dados inválidos, malhas distintas e limites.
8. Registrar tolerâncias, hipótese linearidade, domínio de validade e o que não foi validado.
9. Se integrar solver externo, fixar versão e distribuição, informar ambiente e repetir estudo independentemente.

**Aceite:** resultados reprodutíveis e relatório de erro; nenhuma declaração de projeto certificado.

## Benchmark externo com CalculiX

Se o caso for C3D8, verificar orientação positiva do elemento, cargas nodais equivalentes à tração, remoção mínima dos modos rígidos e extração de `U` e `RF` do `.dat`. Não confundir teste de parser com execução do CalculiX. Guardar artefatos de solver, versão do binário e resultados; aceitar somente com logs reais e tolerâncias.

## Flexão pura e grandezas de erro não triviais (ciclo 07)

Use tensões não uniformes e uma solução de elasticidade independente, compare deslocamentos em ao menos dois nós distintos, calcule taxa de erro em malhas de resoluções crescentes e confira momentos de face e força resultante. A variável `RF` em CalculiX **inclui CLOAD** no mesmo nó: subtraia o carregamento conhecido antes de interpretar reação. C3D8 tem tendência documentada a rigidez excessiva em flexão; registre locking e erro observado, nunca diminua tolerância arbitrariamente para produzir sucesso. Preserve artefatos, dados e revisão de limites antes de fechar o ciclo.

## Evidência real do ciclo 07

O teste de flexão pura em CalculiX C3D8 2.21-1 apresentou erro relativo inicial 29,7457% e final 0,9942% em Uy, taxas aparentes até 1,76, com prova de execução no workflow #42064616852. Ao continuar, usar o JSON `docs/dados/flexao-pura-3d-2026-11-05.json` como baseline sem confundir benchmark C3D8 com referência de projeto; adicionar C3D20R e pós-processamento de tensões antes de ampliar o domínio.
