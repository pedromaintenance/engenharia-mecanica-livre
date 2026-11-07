# Laboratório 08 — C3D8 versus C3D20R em flexão pura

Este laboratório compara **dois tipos de elemento tridimensional** na mesma solução exata da elasticidade, usando o CalculiX CCX em ambiente reproduzível. As grandezas verificadas são deslocamentos, tensões em pontos de integração, reações e custo aproximado de execução.

**Status do código:** **workflow externo concluído** em 07/11/2026 com CalculiX 2.21-1; seis simulações observadas, parser de tensões de Gauss aprovado e resultados versionados em JSON.

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


## 9. Resultados reais do ciclo 08 — 07/11/2026

O workflow [Comparativo FEM #42411991123](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42411991123) executou seis análises com CalculiX **2.21-1**, versão empacotada no Ubuntu 24.04. O modelo C3D8 e o C3D20R foram submetidos ao mesmo campo analítico, mesmas dimensões e mesmo número de elementos geométricos. O resultado de tensões foi extraído das seções **COORD/S dos pontos de integração** no `.dat`, não de médias nodais.

| Elementos por malha | Erro de Uy C3D8 | Erro de Uy C3D20R* | RMS Sxx C3D8 | RMS Sxx C3D20R |
| ---: | ---: | ---: | ---: | ---: |
| 8 | 29,7457% | 0,0000%* | 15,885 MPa | 10 Pa |
| 64 | 10,8252% | 0,0000%* | 5,455 MPa | 2 Pa |
| 512 | 3,3677% | 0,0000%* | 1,843 MPa | 0,707 Pa |

*Erro de Uy reportado como zero pelo leitor de `.dat` na precisão numérica do texto impresso; não deve ser entendido como uma igualdade exata em aritmética real.*

### Quantidade de nós, graus de liberdade e tempo

| Malha | C3D8: nós / GDL | C3D20R: nós / GDL | Tempo C3D8 | Tempo C3D20R |
| ---: | ---: | ---: | ---: | ---: |
| 8 elementos | 27 / 81 | 81 / 243 | 0,179 s | 0,009 s |
| 64 elementos | 125 / 375 | 425 / 1.275 | 0,012 s | 0,041 s |
| 512 elementos | 729 / 2.187 | 2.673 / 8.019 | 0,069 s | 0,483 s |

Os tempos são **uma única medição de subprocesso em ambiente compartilhado** e não devem ser usados para comparar CPUs ou estabelecer custo relativo universal. O primeiro tempo C3D8 é especialmente sujeito ao custo de inicialização do ambiente.

### Interpretação mecânica

- **C3D8:** o erro do deslocamento caiu de 29,75% para 3,37%, e o erro RMS de Sxx de ~15,9 MPa para 1,84 MPa; indica convergência da discretização trilinear no caso de flexão, com rigidez excessiva nas malhas grosseiras.
- **C3D20R:** representou quase exatamente o campo quadrático idealizado desde a malha grossa. O erro residual RMS de Sxx em torno de 10, 2 e 0,707 Pa deve ser interpretado à luz da precisão textual do arquivo `.dat`. Por essa razão **não estimamos ordem de convergência do quadrático usando esses números**.
- **Esforços:** todos os seis casos apresentaram resíduo relativo de reação inferior a 0,001% e foram confrontados com as cargas aplicadas. Isso confirma o balanço dos resultados produzidos pelo solver nesse problema.
- **Custo:** para 512 elementos, o quadrático teve 8.019 graus de liberdade estimados contra 2.187 do C3D8. Melhor precisão por elemento não é sinônimo de menor memória ou menor tempo.

### Controle de qualidade e rastreabilidade

- **Solver:** `calculix-ccx 2.21-1`, Ubuntu 24.04.
- **CI completo:** [64 testes aprovados](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42411991133).
- **Workflow externo:** [seis execuções aprovadas](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42411991123).
- **Artefatos:** [`comparativo-c3d8-c3d20r`](https://github.com/pedromaintenance/engenharia-mecanica-livre/actions/runs/42411991123/artifacts/13589339664), ID 13589339664, SHA-256 `0d703e0f798fe044049960e45f533153a1710acdb5e7f815ba0936505ea52425`, retenção informada até 07/12/2026.
- **Preservação permanente:** [JSON da experiência](../dados/comparacao-c3d8-c3d20r-2026-11-07.json).

### Falhas diagnosticadas e corrigidas

1. O CalculiX 2.21 limitou a **16 entradas por linha** da conectividade `*ELEMENT`: o gerador passou a escrever uma linha contendo identificador + 15 nós, seguida dos cinco nós restantes.
2. A quadratura Q8 produziu números de força próximos de `10⁻¹² N` nos nós em que a carga deveria ser zero; esses resíduos de arredondamento provocavam rejeição de `*CLOAD`. Agora são descartados com limiar relativo à maior força do problema. Cargas significativas e momentos foram preservados e revalidados.
3. A opção `ELSET=EALL` em `*EL FILE` gerava advertência no solver; foi removida no gerador novo, mantendo `*EL PRINT,ELSET=EALL` para tensões e coordenadas.

O [relatório do ciclo 08](../ciclos/ciclo-08.md) registra a implementação e as decisões de aceite.

**Limite final:** a superioridade observada do C3D20R é específica desse **problema idealizado de flexão pura**. Ela não pode ser automaticamente generalizada para contato, flambagem, soldas, plasticidade, fadiga ou tensões concentradas.
