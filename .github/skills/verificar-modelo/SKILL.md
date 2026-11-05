---
name: verificar-modelo
description: "Verificar numericamente e fisicamente calculadoras, propriedades, equações e simulações."
license: MIT
---

# verificar-modelo

## Quando usar
Novo cálculo, correção de bug, integração numérica, alteração de unidade ou solver.

## Procedimento
1. Declarar função, equação de referência, entradas e saídas SI.
2. Confirmar faixa de validade, invariantes, sinais, conservação e tolerâncias.
3. Criar testes analíticos, casos extremos, entrada não física e comparação independente.
4. Para grandezas estimadas, registrar método, amostra e incerteza.
5. Para FEM/CFD, documentar discretização, malha, condições de contorno, convergência e erro.
6. Corrigir implementação sem reescrever arbitrariamente os resultados de referência para forçar aprovação.
7. Executar `python -m unittest discover -s tests -v` e `engmec validar`.

## Saída
Cálculo, documentação, benchmark, testes e limitações.

## Aceite
Testes verdes, modelo justificável e resultado interpretável.
