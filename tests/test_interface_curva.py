import unittest

from engmec.elmer_chapa import geo_elmer
from engmec.interface_curva import transformar_interface


class TestInterfaceCurva(unittest.TestCase):
    def test_default_continua_reta(self):
        geo=geo_elmer(nr=24,nt=48,H=.08,L=.32,a=.01)
        self.assertIn("Line(3) = {5,2};",geo)
        self.assertNotIn("Spline(3)",geo)
        self.assertEqual(geo,geo_elmer(nr=24,nt=48,H=.08,L=.32,a=.01,
                                       interface_interna="reta"))

    def test_spline_somente_interface_compartilhada(self):
        straight=geo_elmer(nr=24,nt=48,H=.08,L=.32,a=.01,
                            estrategia_progressao="escalonada")
        curved=geo_elmer(nr=24,nt=48,H=.08,L=.32,a=.01,
                          estrategia_progressao="escalonada",
                          interface_interna="curva")
        self.assertIn("Spline(3) = {5,8,9,10,2};",curved)
        self.assertNotIn("Line(3) = {5,2};",curved)
        for physical in ('Physical Surface("elastic_domain", 101)',
                         'Physical Curve("traction_right", 201)',
                         'Physical Curve("traction_free_top", 204)',
                         'Physical Curve("traction_free_hole", 205)'):
            self.assertIn(physical,straight)
            self.assertIn(physical,curved)
        for unchanged in ("Point(4) = { L,0,0,1 };",
                          "Point(5) = { L,H,0,1 };",
                          "Point(6) = { 0,H,0,1 };",
                          "Circle(4) = {2,7,1};",
                          "Circle(7) = {3,7,2};",
                          "Transfinite Surface {1}"):
            self.assertIn(unchanged,curved)
        self.assertNotEqual(straight,curved)

    def test_quadrado_tambem_aceita_sem_alterar_contorno(self):
        curved=geo_elmer(nr=16,nt=32,H=.04,a=.01,interface_interna="curva")
        self.assertIn("Spline(3)",curved)
        self.assertIn("Point(8) = { H -",curved)

    def test_estrategia_desconhecida_rejeitada(self):
        with self.assertRaises(ValueError):
            transformar_interface("Line(3) = {5,2};",estrategia="inventada")
        with self.assertRaises(ValueError):
            transformar_interface("malha desconhecida",estrategia="curva",
                                  Hx=.32,Hy=.08,a=.01)


if __name__=="__main__":
    unittest.main()
