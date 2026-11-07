import math
import unittest

from engmec.gmsh_chapa import gerar_geo, importar_msh2, executar


class TestGmshChapa(unittest.TestCase):
    def test_geo_duas_superficies_q8(self):
        geo=gerar_geo(nr=24,nt=48,raio_m=.01,semilargura_m=.04)
        for expected in (
            "Mesh.ElementOrder = 2;",
            "Mesh.SecondOrderIncomplete = 1;",
            "Transfinite Surface {1}",
            "Transfinite Surface {2}",
            "Recombine Surface {1,2};",
            "Circle(4) = {2,7,1};",
            "Circle(7) = {3,7,2};",
            "Nr = 24;", "Na = 24;",
        ):
            self.assertIn(expected,geo)

    def test_geometria_duas_larguras(self):
        for H in (.04,.08,.16):
            geo=gerar_geo(nr=16,nt=32,semilargura_m=H)
            self.assertIn(f'H = {H:.12g};',geo)

    def test_parametros_invalidos(self):
        for args in (
            {'nr':3},{'nr':True},{'nt':18},{'nt':6},{'nt':100},
            {'semilargura_m':.02},{'raio_m':0},{'progressao':2},
            {'progressao':-1},{'raio_m':float('nan')}
        ):
            with self.subTest(args=args),self.assertRaises(ValueError):
                gerar_geo(**args)

    def test_msh_incompleto_nao_e_aceito(self):
        with self.assertRaisesRegex(ValueError,"Seção MSH2 ausente: Nodes"):
            importar_msh2("$MeshFormat\n2.2 0 8\n$EndMeshFormat\n",
                          a=.01,H=.04,nr=8,nt=16)

    def test_solver_ausente_nao_gera_resultado(self):
        with self.assertRaises(RuntimeError):
            executar("/tmp/chapa-gmsh-teste-sem-solver",
                     gmsh_exe="__gmsh_missing__",ccx_exe="__ccx_missing__")


if __name__=="__main__":
    unittest.main()
