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


## Execução confirmada — encerramento do ciclo

- [Commit corrigido e submetido](https://github.com/pedromaintenance/engenharia-mecanica-livre/commit/9138697fd64d7b501674c9685a5b6059172ff96a)
- [CI de qualidade](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42055701336): concluído com sucesso.
- [Workflow externo CalculiX](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42055701419): concluído com sucesso. Ubuntu 24.04, pacote calculix-ccx **2.21-1**, executável **/usr/bin/ccx**.
- 7 testes do gerador/parser aprovados. CalculiX **executou quatro casos reais**, com n=1,2,4,8 elementos no comprimento e 2×2 elementos transversais.
- Cada caso retornou `Ux=0,0001 m` e soma de reações `Rx=-10000 N`. Os erros relativos reportados no JSON foram `0,0` na precisão de impressão do `.dat`.
- Artefato arquivado no GitHub Actions: `calculix-c3d8-ubuntu2404` (ID 13429701171, sha256 f500611f6c8016e8cd8e187086c6dffdef9f2870bf48dcaadc4783c1f4e64004), retenção até 05/12/2026.
- [Dados estruturados observados](../dados/calculix-c3d8-2026-11-05.json) e [laboratório publicado](../laboratorios/calculix-3d.md).

### Distinção essencial

O patch test de tração uniforme pode ser reproduzido exatamente na discretização C3D8, portanto o aumento de malha **não produz medida informativa da ordem de convergência**. Isso valida execução e consistência para um caso simples, não um método universal para qualquer geometria, contato, flexão ou fadiga. A próxima fase deve usar gradiente não trivial e referência analítica/experimental.

**Status:** entregue e verificado, com ressalvas físicas e limitação de precisão de saída explicitadas.
