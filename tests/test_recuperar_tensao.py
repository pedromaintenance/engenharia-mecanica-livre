"""Testes para tres operadores de recuperacao sobre um unico campo FEM."""
import importlib.util
import math
import tempfile
import unittest
from pathlib import Path

from engmec.recuperar_tensao import _levels, _rotate, escrever_csv

AVAILABLE=importlib.util.find_spec("numpy") is not None


class TestRecuperacaoTensoes(unittest.TestCase):
    def test_rotacao_de_tensao_em_90_graus(self):
        tt,rr,rt=_rotate((30e6,1e6,2e6),math.pi/2,10e6)
        self.assertAlmostEqual(tt,3)
        self.assertAlmostEqual(rr,.1)
        self.assertAlmostEqual(rt,-.2)

    def test_csv_sem_amostras_nao_publica(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                escrever_csv(Path(directory)/"gauss.csv",[])

    @unittest.skipUnless(AVAILABLE,"Requer dependencia opcional NumPy")
    def test_polynomial_fits_constantes_e_reproduz_ajuste_exato(self):
        from engmec.recuperar_tensao import _fit_patch
        rows=[]
        for u in (.2,.4,.8,1.1,1.6,2.1,2.7,3.0):
            for v in (.2,.5,.8,1.1,1.4):
                rows.append({
                    "u":u,"v":v,"peso_area_m2":1e-6*(1+.1*u),
                    "tt":3+.25*u+.07*u*u-.09*v*v+.025*u*v*v+.003*v**4,
                    "rr":0.0,"rt":0.0,
                })
        fit=_fit_patch(rows,"gauss_seis_coef")
        self.assertAlmostEqual(fit["kt_gross"],3.,places=9)
        self.assertLess(fit["residuo_tt_rms"],1e-9)
        self.assertAlmostEqual(fit["sigma_rr_sobre_T"],0,places=9)
        rows2=[dict(row,tt=2+.2*row["u"]+.01*row["u"]**2-.03*row["v"]**2) for row in rows]
        fit2=_fit_patch(rows2,"patch_ponderado_quatro_coef")
        self.assertAlmostEqual(fit2["kt_gross"],2.,places=9)
        self.assertLess(fit2["residuo_tt_rms"],1e-9)

    @unittest.skipUnless(AVAILABLE,"Requer dependencia opcional NumPy")
    def test_mesmo_campo_de_deslocamento_gera_tres_metodos(self):
        from engmec.chapa_finita import gerar_malha
        from engmec.recuperar_tensao import recuperar
        E=200e9;nu=.3;T=10e6
        mesh=gerar_malha(nr=8,nt=16,raio_m=.01,semilargura_m=.04)
        U={node:(T/E*x,-nu*T/E*y) for node,(x,y,z) in mesh["nodes"].items()}
        result,gauss=recuperar(mesh,U,a=.01,H=.04,T=T,E=E,nu=nu)
        self.assertEqual(result["elementos"],128)
        self.assertEqual(result["gauss_total"],128*9)
        self.assertGreater(result["patch_amostras"],24)
        self.assertTrue(any(x["no_patch"]==1 for x in gauss))
        self.assertTrue(any(x["no_patch"]==0 for x in gauss))
        for method in result["metodos"].values():
            self.assertAlmostEqual(method["kt_gross"],1.,places=6)
            self.assertAlmostEqual(method["sigma_rr_sobre_T"],0.,places=6)
            self.assertAlmostEqual(method["sigma_rt_sobre_T"],0.,places=6)
        self.assertLess(result["sensibilidade"]["amplitude_entre_metodos_Kt_bruto"],1e-6)

    @unittest.skipUnless(AVAILABLE,"Requer dependencia opcional NumPy")
    def test_kirsch_nao_e_verdade_da_chapa_finita(self):
        from engmec.chapa_finita import gerar_malha
        from engmec.kirsch import deslocamentos_kirsch
        from engmec.recuperar_tensao import recuperar
        m=gerar_malha(nr=8,nt=16)
        u={node:deslocamentos_kirsch(x,y,.01,10e6,200e9,.3)
           for node,(x,y,z) in m["nodes"].items()}
        r,_=recuperar(m,u)
        ref=r["controle_analitico_Kirsch"]
        self.assertTrue(math.isfinite(ref["B_bias"]))
        self.assertTrue(math.isfinite(ref["C_bias"]))
        self.assertLess(abs(ref["B_bias"]),1.)
        self.assertLess(abs(ref["C_bias"]),1.)

    @unittest.skipUnless(AVAILABLE,"Requer dependencia opcional NumPy")
    def test_campos_incompletos_nao_passam(self):
        from engmec.chapa_finita import gerar_malha
        from engmec.recuperar_tensao import recuperar
        m=gerar_malha(nr=8,nt=16)
        with self.assertRaises(ValueError):
            recuperar(m,{})

    @unittest.skipUnless(AVAILABLE,"Requer dependencia opcional NumPy")
    def test_csv_pontos_de_gauss_reprodutiveis(self):
        from engmec.chapa_finita import gerar_malha
        from engmec.recuperar_tensao import recuperar
        m=gerar_malha(nr=8,nt=16)
        u={node:(1e-5*x,-3e-6*y) for node,(x,y,z) in m["nodes"].items()}
        _,rows=recuperar(m,u)
        with tempfile.TemporaryDirectory() as folder:
            dest=Path(folder)/"g.csv"
            escrever_csv(dest,rows)
            self.assertEqual(len(dest.read_text().splitlines()),len(rows)+1)


if __name__=="__main__":
    unittest.main()
