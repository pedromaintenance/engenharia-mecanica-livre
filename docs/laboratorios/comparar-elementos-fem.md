# Laboratório 08 — C3D8 versus C3D20R em flexão pura

Este laboratório compara **dois tipos de elemento tridimensional** na mesma solução exata da elasticidade, usando o CalculiX CCX em ambiente reproduzível. As grandezas verificadas são deslocamentos, tensões em pontos de integração, reações e custo aproximado de execução.

**Status do código:** implementação e workflow preparados; tabela de resultados só pode ser preenchida a partir da execução real. Não se deve substituir erros observados por estimativas teóricas.

## 1. Hipótese mecânica comum

Reutilizamos a barra homogênea sob momentos puros opostos do [Laboratório 07](flexao-pura-3d.md):

- L = 0,20 m; seção quadrada de 0,10 m de lado;
- E = 200 GPa; ν = 0,30; κ = 0,01 m⁻¹;
- referência σxx(y) = −Eκy; tensão máxima em módulo 100 MPa;
- referência Uy(L,0,0) = +0,200 mm; Ux(L,b/2,0) = −0,100 mm.

O campo exato de deslocamentos é quadrático: Ux = −κxy; Uy = κx²/2 + νκ(y²−z²)/2; Uz = νκyz. O modelo continua restrito à elasticidade linear isotrópica e às pequenas deformações.

## 2. Diferenças entre elementos

| Característica | C3D8 | C3D20R |
| --- | --- | --- |
| Nós por elemento | 8, vértices | 20, vértices e meios de arestas |
| Interpolação | Trilinear | Quadrática serendipidade |
| Integração de Gauss volumétrica | 2×2×2 | 2×2×2 (reduzida em relação ao elemento quadrático de 27 pontos) |
| Em flexão | Pode ficar excessivamente rígido (*locking*) | Tende a representar melhor deslocamentos quadráticos |
| Elementos analisados | 2³, 4³ e 8³ | 2³, 4³ e 8³ |
| Risco interpretativo | Concordância em força não comprova precisão da tensão | Boa precisão em flexão não valida contato, plasticidade ou tensão superficial concentrada |

As observações de comportamento provêm do [manual CalculiX — C3D20R](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node32.html) e [manual — C3D8](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node28.html). O manual aponta limitações específicas na representação de tensões de superfície por integração reduzida.

## 3. Malha quadrática e continuidade

Para C3D20R, cada aresta dos elementos C3D8 recebe um nó médio. As arestas comuns são cadastradas com chave ordenada pelos dois vértices; por isso, **duas células vizinhas compartilham o mesmo nó médio**. A ordem dos nós é a prescrita no CalculiX: 8 vértices, 4 mids da face inferior, 4 mids da face superior e 4 arestas verticais.

A condição de contorno remove somente os seis graus de corpo rígido identificados no laboratório anterior. Ambos os tipos de elemento usam **mesma geometria, material, curvatura, momentos e valores analíticos**, porém números distintos de nós e graus de liberdade.

## 4. Aplicação consistente das trações

Em cada face extrema, a tração na direção axial é tₓ = −Eκy·nₓ. Para C3D8 usamos a integração consistente com funções Q4; para C3D20R, **funções quadráticas Q8 de face**, integradas com Gauss 3×3. A força nodal de cada nó é a integral Nᵢ·tₓ sobre sua área tributária.

**Não distribua a carga igualmente por nó em uma face quadrática.** As funções Q8 podem atribuir cargas nodais de sinais contrários nos vértices, mesmo sob pressão de sinal fixo. Isso é consequência da interpolação e não constitui, por si só, falha de montagem. A prova correta é a soma de forças e o momento de face.

As cargas aplicadas nos nós de apoio devem ser **subtraídas de RF** para recuperar a reação propriamente dita, conforme o comportamento da variável RF registrado no [Laboratório 07](flexao-pura-3d.md).

## 5. Tensões em pontos de integração, não extrapoladas

Cada modelo solicita, dentro de `*STEP`:

```text
*EL PRINT,ELSET=EALL,GLOBAL=YES
COORD,S
```

Isso produz coordenadas físicas e componentes de tensões nos pontos de Gauss no `.dat` (e não tensões extrapoladas/averaged nos nós do `.frd`). O código associa os valores por par `(elemento, ponto de integração)` e rejeita a comparação se faltarem registros, houver duplicidade ou surgirem valores não finitos. <https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node266.html>

Para cada ponto, a tensão de referência é `σxx,exata(y) = −Eκ·y`, com y retirada das coordenadas impressas pelo próprio solver. As demais cinco componentes devem tender a zero no problema ideal.

**Métricas:**

```text
erro_RMS_Sxx = sqrt( Σ (Sxx_num - Sxx_exata(y_IP))² / N_IP )

erro_rel_Sxx = erro_RMS_Sxx / |σxx,max|

erro_RMS_outras = sqrt(Σ (Syy²+Szz²+Sxy²+Sxz²+Syz²)/(5*N_IP))
```

Essa é uma **norma RMS não ponderada sobre pontos de integração**. Como a malha é estruturada em prismas de volume uniforme e os dois elementos usam oito pontos com pesos iguais, a medida é comparável neste experimento específico. Não a extrapole para malhas distorcidas ou elementos com pesos variáveis sem reponderar por jacobiano, peso e volume.

## 6. Reproduzir

A geração do arquivo de entrada é independente da instalação do CalculiX:

```bash
python -m engmec.comparar_elementos --elemento C3D20R --nx 4 --ny 4 --nz 4 --somente-gerar --saida build/comparacao/c3d20r/n-4
```

Com CalculiX instalado:

```bash
python -m engmec.comparar_elementos --elemento C3D8 --nx 4 --ny 4 --nz 4 --saida build/comparacao/c3d8/n-4

python -m engmec.comparar_elementos --elemento C3D20R --nx 4 --ny 4 --nz 4 --saida build/comparacao/c3d20r/n-4
```

O [workflow GitHub Actions](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/workflows/comparar-elementos.yml) executa seis problemas (famílias C3D8 e C3D20R × malhas 2, 4 e 8), valida os arquivos `.dat`, calcula erros e publica `resumo_elementos.json` como artefato temporário.

## 7. Critérios de aceite e limites

O teste reprova se faltar saída de tensões ou coordenadas em qualquer ponto de integração. Também verifica igualdade de malha geométrica, equilíbrio de reações e exige que **C3D20R tenha menor erro de Uy e Sxx na malha mais grosseira**. Essa expectativa é específica para o caso de flexão pura escolhido, não um teorema de superioridade universal.

Tempos de execução são medidos pelo relógio do subprocesso e dependem do sistema operacional, carga e hardware compartilhado. Servem como observação deste workflow, **não como benchmark de CPU**.

Um resultado de erro quase nulo no quadrático indica sua capacidade de representar esse campo polinomial e a precisão numérica/textual do solver; nesse limite, não é apropriado estimar uma ordem de convergência usando quocientes entre erros próximos do arredondamento.

**Fora do domínio:** tensões em concentrações geométricas, contato, não linearidade, fratura, soldas, estabilidade, fadiga, anisotropia e validação com ensaio real.

## 8. Evidências e literatura

- [Código original do gerador e comparador](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/src/engmec/comparar_elementos.py)
- [Script de análise dos dois elementos](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/scripts/comparar_elementos.py)
- [CalculiX C3D20R — descrição e ressalvas](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node32.html)
- [CalculiX *EL PRINT — coordenadas e tensões](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node266.html)
- [CalculiX — variáveis em pontos de integração e saída nodal](https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node211.html)

Ao final da execução, registrar aqui tabela de erros, versionamento do solver, logs e metadados do artefato. O laboratório não substitui projeto executivo assinado.
