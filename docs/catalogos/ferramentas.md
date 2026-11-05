# Ferramentas e bibliotecas

**17 softwares** foram identificados como candidatos para um laboratório computacional integrado. A presença nesta tabela **não significa integração instalada**.

| Projeto | Área | Tipo | Uso previsto |
| --- | --- | --- | --- |
| [FreeCAD](https://www.freecad.org/) | CAD | desktop | Modelos paramétricos e scripts |
| [CalculiX](https://www.calculix.de/) | FEM | desktop | Solver estrutural e testes |
| [Gmsh](https://gmsh.info/) | malhas | desktop-api | Malhas paramétricas |
| [OpenFOAM Foundation](https://openfoam.org/) | CFD | desktop | Simulação de fluidos; distinguir distribuições |
| [OpenFOAM.com Docs](https://www.openfoam.com/documentation/) | CFD | documentação | Guias de distribuição alternativa |
| [OpenModelica](https://openmodelica.org/) | sistemas | desktop | Modelos multiphysics |
| [CoolProp](https://coolprop.org/) | termodinamica | python | Propriedades termo-físicas |
| [Cantera](https://cantera.org/) | combustao | python | Cinética e termodinâmica |
| [NumPy](https://numpy.org/) | numerico | python | Álgebra numérica |
| [SciPy](https://scipy.org/) | numerico | python | Otimização, integração, sinais |
| [Pint](https://pint.readthedocs.io/) | unidades | python | Análise dimensional |
| [SymPy](https://www.sympy.org/) | simbolico | python | Álgebra simbólica |
| [GNU Octave](https://octave.org/) | numerico | desktop | Computação matricial |
| [SALOME](https://www.salome-platform.org/) | FEM | desktop | Geometria, malha e pré-pós |
| [Code_Aster](https://www.code-aster.org/) | FEM | desktop | Análise estrutural avançada |
| [ParaView](https://www.paraview.org/) | visualizacao | desktop | Pós-processamento |
| [FEniCS](https://fenicsproject.org/) | FEM | python | Equações variacionais |

## Princípios de integração

Instalar componentes em ambientes isolados; fixar versões; não incorporar código de terceiros ao repositório; registrar tolerâncias e benchmarks. Para FEM/CFD exigir independência de malha, condições de contorno, balanços e comparação independente. Distinguir OpenFOAM Foundation (`openfoam.org`) da variante OpenFOAM.com, evitando misturar tutorial e sintaxe.

[JSON canônico](https://github.com/pedromaintenance/engenharia-mecanica-livre/blob/main/src/engmec/data/ferramentas.json)
