"""Regressões geométricas do ciclo 15: retângulo sob tração em x."""
import math
import unittest
from engmec.gmsh_chapa import gerar_geo
from engmec.elmer_chapa import geo_elmer
from engmec.chapa_retangular import gerar_geo_retangular,kt_peterson_liquido,kt_peterson_bruto


class TestChapaRetangular(unittest.TestCase):
    def test_quadrado_e_identico_bit_a_bit_ao_ciclo14(self):
        a=.01; H=.04
        self.assertEqual(gerar_geo_retangular(a=a,Hy=H,Hx=H,nr=16,nt=32),
                         gerar_geo(raio_m=a,semilargura_m=H,nr=16,nt=32))
        self.assertEqual(geo_elmer(H=H,L=H,a=a,nr=16,nt=32),
                         geo_elmer(H=H,a=a,nr=16,nt=32))

    def test_retangulo_muda_apenas_comprimento_x(self):
        geo=gerar_geo_retangular(a=.01,Hy=.04,Hx=.16,nr=16,nt=32)
        self.assertIn("L = 0.16; H = 0.04;",geo)
        self.assertIn("Point(4) = { L,0,0,1 };",geo)
        self.assertIn("Point(5) = { L,H,0,1 };",geo)
        self.assertIn("Point(6) = { 0,H,0,1 };",geo)
        self.assertIn("Mesh.SecondOrderIncomplete = 1;",geo)
        self.assertIn("Transfinite Surface {1}",geo)
        with_physical=geo_elmer(H=.04,L=.16,a=.01,nr=16,nt=32)
        self.assertIn('Physical Curve("traction_right", 201) = {2};',with_physical)

    def test_tensoes_bruta_liquida_referencias_corretas(self):
        for rho in (.125,.25,.5):
            kn=kt_peterson_liquido(rho)
            kg=kt_peterson_bruto(rho)
            self.assertGreater(kg,kn)
            self.assertAlmostEqual(kg*(1-rho),kn,places=12)
        self.assertAlmostEqual(kt_peterson_liquido(.5),2.155875,places=5)
        self.assertAlmostEqual(kt_peterson_bruto(.25),
                               kt_peterson_liquido(.25)/.75,places=12)

    def test_geometria_invalida_rejeitada(self):
        for hx,hy,a in ((.02,.04,.01),(.04,.02,.01),(.04,.04,0),
                        (math.nan,.04,.01),(.04,math.inf,.01)):
            with self.subTest(hx=hx,hy=hy,a=a):
                with self.assertRaises(ValueError):
                    gerar_geo_retangular(Hx=hx,Hy=hy,a=a)

    def test_kt_peterson_invalido_rejeitado(self):
        for x in (0,1,-.1,math.nan,math.inf):
            with self.assertRaises(ValueError):
                kt_peterson_bruto(x)


if __name__=="__main__":
    unittest.main()
