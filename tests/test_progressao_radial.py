"""Ciclo 17: regressao CAD e estrategia de progressao de tamanho radial."""
import math
import unittest
from engmec.progressao_radial import razao_progressao
from engmec.elmer_chapa import geo_elmer
from engmec.chapa_retangular import gerar_geo_retangular


class TestProgressaoRadial(unittest.TestCase):
    def test_n24_identico(self):
        self.assertAlmostEqual(razao_progressao(24,"escalonada"),1.12,places=12)
        self.assertEqual(
          geo_elmer(nr=24,nt=48,H=.04,L=.16,a=.01,
                    estrategia_progressao="escalonada"),
          geo_elmer(nr=24,nt=48,H=.04,L=.16,a=.01,
                    estrategia_progressao="fixa")
        )

    def test_escala_crescimento_total_nao_explode(self):
        base=1.12**24
        for n in (24,32,40,48):
            q=razao_progressao(n,"escalonada")
            self.assertGreaterEqual(q,1.)
            self.assertLess(q,1.3)
            self.assertAlmostEqual(q**n,base,places=9)
        self.assertAlmostEqual(razao_progressao(48,"escalonada"),
                               math.sqrt(1.12),places=12)

    def test_fixa_preserva_documento_geometrico(self):
        for n in (8,16,24,32,40,48):
            a=geo_elmer(nr=n,nt=2*n,H=.08,L=.32,a=.01)
            b=geo_elmer(nr=n,nt=2*n,H=.08,L=.32,a=.01,
                        estrategia_progressao="fixa")
            self.assertEqual(a,b)
        self.assertNotEqual(geo_elmer(nr=48,nt=96,H=.08,L=.32,
                                     estrategia_progressao="escalonada"),
                            geo_elmer(nr=48,nt=96,H=.08,L=.32))

    def test_retangulo_recebe_q_sem_alterar_fisica(self):
        fixed=gerar_geo_retangular(a=.01,Hy=.04,Hx=.16,nr=48,nt=96)
        scaled=gerar_geo_retangular(a=.01,Hy=.04,Hx=.16,nr=48,nt=96,
               progressao=razao_progressao(48,"escalonada"))
        self.assertIn("q = 1.12;",fixed)
        self.assertIn("Point(5) = { L,H,0,1 };",scaled)
        self.assertNotEqual(fixed,scaled)

    def test_entrada_invalida_rejeitada(self):
        for n,strategy in ((0,"escalonada"),(49,"fixa"),(24,"inexistente"),(True,"fixa")):
            with self.subTest(n=n,strategy=strategy):
                with self.assertRaises(ValueError):
                    razao_progressao(n,strategy)
        for q in (0.9,1.31,math.nan,math.inf):
            with self.assertRaises(ValueError):
                razao_progressao(24,"escalonada",q_referencia=q)


if __name__=="__main__":
    unittest.main()
