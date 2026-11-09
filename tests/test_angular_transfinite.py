"""Ciclo 18: distribuição angular conservadora sem alterar CAD físico."""
import unittest
import math
from engmec.elmer_chapa import geo_elmer
from engmec.angular_transfinite import aplicar_distribuicao_angular,q_angular


class TestDistribuicaoAngular(unittest.TestCase):
    def test_padrao_e_identico_ao_ciclo17(self):
        base=geo_elmer(nr=24,nt=48,H=.08,L=.32,a=.01)
        forced=geo_elmer(nr=24,nt=48,H=.08,L=.32,a=.01,angular="uniforme")
        self.assertEqual(base,forced)
        self.assertIn("Transfinite Curve {2,4,5,7} = Na+1;",base)

    def test_alternativa_muda_so_distribuicao_transfinite(self):
        uniform=geo_elmer(nr=48,nt=96,H=.08,L=.32,a=.01,
                          estrategia_progressao="escalonada")
        edited=geo_elmer(nr=48,nt=96,H=.08,L=.32,a=.01,
                         estrategia_progressao="escalonada",
                         angular="ampliada-topo")
        self.assertIn("Transfinite Curve {-5,7} = Na+1 Using Progression qa;",edited)
        self.assertIn("Transfinite Curve {2,4} = Na+1;",edited)
        self.assertIn("Line(3) = {5,2};",edited)
        self.assertNotIn("Spline(3)",edited)
        for required in ('Physical Curve("traction_right", 201)',
                         'Physical Curve("traction_free_hole", 205)',
                         'Point(5) = { L,H,0,1 };'):
            self.assertIn(required,uniform)
            self.assertIn(required,edited)
        self.assertNotEqual(uniform,edited)

    def test_angulo_escalona_ate_limite_fixo(self):
        for nt in (48,64,80,96):
            q=q_angular(nt)
            self.assertAlmostEqual(q**(nt//2),.7,places=10)
            self.assertLess(q,1.)

    def test_rejeita_invalido(self):
        for mode in ("obscuro","spline"):
            with self.assertRaises(ValueError):
                aplicar_distribuicao_angular("foo",modo=mode,nt=48)
        for invalid in (True,3,18,0):
            with self.assertRaises(ValueError):
                q_angular(invalid)


if __name__=="__main__":
    unittest.main()
