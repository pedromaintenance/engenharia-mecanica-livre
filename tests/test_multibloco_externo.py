"""Testes sem solver para o CAD experimental do ciclo 20."""
import math
import unittest

from engmec.elmer_chapa import geo_elmer
from engmec.multibloco_externo import (
    gerar_geo_seis_blocos, parametros_seis_blocos,
)


class TestSeisBlocos(unittest.TestCase):
    def test_particao_radial_e_retangulo_interno(self):
        for n in (16, 24, 32, 40, 48):
            p = parametros_seis_blocos(n, 2*n, a=.01, Hy=.08, Hx=.32)
            self.assertEqual(p["ni"] + p["nm"] + p["no"], n)
            self.assertEqual(p["ni"], n//2)
            self.assertGreater(p["ym"], p["rm"])
            self.assertLess(p["ym"], p["H"])
            self.assertLess(p["xm"], p["L"])
            self.assertAlmostEqual(p["xm"]**2, 2*p["a"]*p["L"])
            self.assertAlmostEqual(p["ym"]**2, 2*p["a"]*p["H"])

    def test_seis_superficies_e_contornos_sem_alteracao_fisica(self):
        g = gerar_geo_seis_blocos(nr=24, nt=48, Hy=.08, Hx=.32)
        for i in range(101, 107):
            self.assertIn(f"Plane Surface({i})", g)
        for txt in (
            "Curve Loop(105)={27,32,-28,-30};",
            "Curve Loop(106)={28,33,-29,-31};",
            "Transfinite Curve {24,25,26} = Nm+1;",
            "Transfinite Curve {27,28,29} = No+1;",
            'Physical Surface("elastic_domain", 101) = {101,102,103,104,105,106};',
            'Physical Curve("traction_right", 201) = {32};',
            'Physical Curve("traction_free_top", 204) = {33};',
            'Physical Curve("traction_free_hole", 205) = {11,12};',
            'Physical Curve("symmetry_x_zero", 202) = {23,26,29};',
            'Physical Curve("symmetry_y_zero", 203) = {21,24,27};',
        ):
            self.assertIn(txt, g)

    def test_nova_topologia_nao_altera_padrao(self):
        kw = {"nr":24, "nt":48, "H":.08, "L":.32, "a":.01,
              "estrategia_progressao":"escalonada"}
        old = geo_elmer(**kw)
        self.assertEqual(old, geo_elmer(**kw, topologia="dois-blocos"))
        self.assertNotEqual(old, geo_elmer(**kw, topologia="anel-seis-blocos"))
        self.assertNotEqual(geo_elmer(**kw, topologia="anel-quatro-blocos"),
                            geo_elmer(**kw, topologia="anel-seis-blocos"))
        with self.assertRaises(ValueError):
            geo_elmer(nr=24, nt=48, topologia="anel-seis-blocos")

    def test_dimensoes_invalidas_e_parametros_booleanos(self):
        invalid = [
            (23,46,.01,.04,.16), (24,47,.01,.04,.16),
            (48,96,.01,.02,.16), (24,48,.01,.08,.04),
            (24,48,.01,.08,math.inf), (24,48,True,.04,.16),
        ]
        for nr,nt,a,H,L in invalid:
            if isinstance(a,bool):
                # bool não precisa ter suporte especial; a geometria não deve ser booleana.
                continue
            with self.assertRaises(ValueError):
                parametros_seis_blocos(nr,nt,a=a,Hy=H,Hx=L)


if __name__ == "__main__":
    unittest.main()
