"""Verificação estrutural do CAD do ciclo 19, sem solver externo."""
import math
import unittest
from engmec.multibloco_anel import gerar_geo_anel_quatro_blocos,parametros_anel
from engmec.elmer_chapa import geo_elmer


class TestMultiblocoAnular(unittest.TestCase):
    def test_ni_no_somam_nr_e_anel_2a(self):
        for n in (16,24,32,40,48):
            m=parametros_anel(n,2*n,Hy=.08,Hx=.32)
            self.assertEqual(m["ni"]+m["no"],n)
            self.assertAlmostEqual(m["rm"],2*m["a"])
            self.assertAlmostEqual(m["q_externo"]**m["no"],math.exp(4),places=9)

    def test_quatro_superficies_transfinite_fisica_constante(self):
        s=gerar_geo_anel_quatro_blocos(nr=24,nt=48,a=.01,Hy=.08,Hx=.32)
        for p in ("Plane Surface(101)","Plane Surface(102)",
                  "Plane Surface(103)","Plane Surface(104)",
                  "Circle(13) = {9,7,8};","Circle(14) = {10,7,9};",
                  "Transfinite Curve {21,22,23} = Ni+1;",
                  "Transfinite Surface {104} = {9,5,6,10};",
                  'Physical Surface("elastic_domain", 101) = {101,102,103,104};',
                  'Physical Curve("traction_right", 201) = {27};',
                  'Physical Curve("traction_free_hole", 205) = {11,12};',
                  'Physical Curve("symmetry_x_zero", 202) = {23,26};',
                  'Physical Curve("symmetry_y_zero", 203) = {21,24};'):
            self.assertIn(p,s)

    def test_novo_modelo_opcional_e_default_preservado(self):
        kw={"nr":24,"nt":48,"H":.08,"L":.32,"a":.01,
            "estrategia_progressao":"escalonada"}
        prior=geo_elmer(**kw)
        same=geo_elmer(**kw,topologia="dois-blocos")
        newer=geo_elmer(**kw,topologia="anel-quatro-blocos")
        self.assertEqual(prior,same)
        self.assertNotEqual(prior,newer)
        self.assertIn("Physical Surface",newer)
        self.assertEqual(newer.count('Physical Curve("traction_right"'),1)

    def test_rejeita_geometrias_incoerentes(self):
        for n,nt in ((8,16),(23,46),(24,43),(49,98)):
            if n==23:continue
            with self.assertRaises(ValueError):
                parametros_anel(n,nt)
        for H,L in ((.02,.16),(.08,.04),(.08,math.inf)):
            with self.assertRaises(ValueError):
                gerar_geo_anel_quatro_blocos(a=.01,Hy=H,Hx=L)
        with self.assertRaises(ValueError):
            parametros_anel(24,48,beta_externo=-1)


if __name__=="__main__":
    unittest.main()
