# Ciclo 06 — Benchmark externo CalculiX

**Data:** 05/11/2026. **Ramo:** `main`. **Base anterior:** `d84849a`.

## Objetivo

Elevar a verificação do solver 1D autoral a um benchmark cruzado com software de terceiros. Corrigir a lacuna identificada na issue #10: ter um **solver FEM externo realmente executado**, com logs, arquivos e tolerâncias reprodutíveis.

## Entregas planejadas para este commit

- Implementação `src/engmec/calculix.py`: malhas C3D8 originais, restrições mínimas, carga de tração uniforme em face, `*NODE PRINT`, execução `subprocess` e parser de `.dat`.
- `tests/test_calculix.py`: validação estática de malha, soma das forças e parser sintético; não confundir estes testes com execução real.
- `.github/workflows/calculix.yml`: Linux Ubuntu 24.04 com `calculix-ccx` e série de quatro malhas `nx=1,2,4,8`.
- `docs/laboratorios/calculix-3d.md`: hipóteses, comandos, referência analítica e limites.

## Controle de resultado

O caso tridimensional difere do estudo 1D com carga distribuída (`q=1000 N/m`): **aqui q=0**. Portanto, para F=10 kN, L=2 m, E=200 GPa e A=1000 mm², a referência da ponta é 0,1 mm e a reação −10 kN. O objetivo é examinar deslocamentos/reações C3D8 no arquivo `.dat` do solver, não reconstruí-los.

## Evidência requerida

Registrar o commit e workflow de CI + CalculiX + Pages; somente depois afirmar que CalculiX foi executado. Em caso de falha, reter logs, formular hipótese e corrigir com novo commit, sem forçar um resultado.

## Pendências

Revisão de normas/licenças de assets de terceiros, benchmark de convergência não trivial em 3D, 2D/3D com condições não uniformes, integração FreeCAD e validação experimental.
