"""Ciclo 21: testes de tração livre completa e malha alinhada."""
import math
import unittest
from importlib.util import find_spec

from engmec.tracao_livre import medir_parede_furo
from engmec.multibloco_externo import parametros_seis_blocos
from engmec.elmer_chapa import geo_elmer


def elemento_quarto_anel(a=.01):
    """Um Q8 isoparamétrico CCW, com arco interno e nós médios em círculo."""
    nodes={
        1:(a,0.,0.), 2:(2*a,0.,0.), 3:(0.,2*a,0.), 4:(0.,a,0.),
        5:(1.5*a,0.,0.), 6:(math.sqrt(2)*a,math.sqrt(2)*a,0.),
        7:(0.,1.5*a,0.), 8:(a/math.sqrt(2),a/math.sqrt(2),0.),
    }
    return {"nodes":nodes,"elements":{1:(1,2,3,4,5,6,7,8)},
            "hole_edges":[(4,8,1)]}


@unittest.skipUnless(find_spec("numpy"), "Requer NumPy opcional (perfil FEM)")
class TestTraçãoParedeCompleta(unittest.TestCase):
    def test_deslocamentos_zerados_sem_residuo(self):
        mesh=elemento_quarto_anel()
        disp={n:(0.,0.) for n in mesh["nodes"]}
        summary,rows=medir_parede_furo(mesh,disp,a=.01,T=1e7,E=2e11,nu=.3)
        self.assertEqual(summary["amostras"],2)
        self.assertEqual(summary["arestas_furo"],1)
        self.assertEqual(summary["tracao_vetorial_max_T"],0.)
        self.assertTrue(all(0 < p["theta_rad"] < math.pi/2 for p in rows))

    def test_tensao_hidrostatica_conhecida(self):
        mesh=elemento_quarto_anel()
        E,T,nu=2e11,1e7,.3
        eps=T*(1-nu)/E
        disp={n:(eps*x,eps*y) for n,(x,y,z) in mesh["nodes"].items()}
        summary,rows=medir_parede_furo(mesh,disp,a=.01,T=T,E=E,nu=nu)
        for p in rows:
            self.assertAlmostEqual(p["sigma_rr_T"],1.,places=10)
            self.assertAlmostEqual(p["sigma_rtheta_T"],0.,places=10)
        self.assertAlmostEqual(summary["tracao_vetorial_rms_T"],1.,places=10)

    def test_rotacao_rigida_nao_gera_tracao(self):
        mesh=elemento_quarto_anel()
        disp={n:(-1e-5*y,1e-5*x) for n,(x,y,z) in mesh["nodes"].items()}
        summary,_=medir_parede_furo(mesh,disp,a=.01,T=1e7,E=2e11,nu=.3)
        self.assertLess(summary["tracao_vetorial_max_T"],1e-8)

    def test_detecta_aresta_incorreta_e_campo_incompleto(self):
        mesh=elemento_quarto_anel()
        disp={n:(0.,0.) for n in mesh["nodes"]}
        with self.assertRaises(ValueError):
            medir_parede_furo(mesh,{1:(0.,0.)},a=.01,T=1e7,E=2e11,nu=.3)
        mesh["hole_edges"]=[(4,7,1)]
        with self.assertRaises(ValueError):
            medir_parede_furo(mesh,disp,a=.01,T=1e7,E=2e11,nu=.3)


class TestInterfaceAlinhada(unittest.TestCase):
    def test_default_do_ciclo20_preservado(self):
        kw=dict(nr=24,nt=48,a=.01,Hy=.08,Hx=.32)
        base=parametros_seis_blocos(**kw)
        idem=parametros_seis_blocos(**kw,modo_interface="geometrica")
        self.assertEqual(base,idem)
        self.assertAlmostEqual(base["xm"],.08)
        aligned=parametros_seis_blocos(**kw,modo_interface="alinhada")
        self.assertNotEqual(aligned["xm"],base["xm"])
        diag=.02/math.sqrt(2)
        self.assertAlmostEqual((aligned["xm"]-diag)/(.32-diag),
                               (aligned["ym"]-diag)/(.08-diag))
        kwmesh=dict(nr=24,nt=48,H=.08,L=.32,a=.01,
                    estrategia_progressao="escalonada")
        self.assertEqual(geo_elmer(**kwmesh,topologia="anel-seis-blocos"),
                         geo_elmer(**kwmesh,topologia="anel-seis-blocos",
                                   fracao_interface=.5))
        self.assertNotEqual(geo_elmer(**kwmesh,topologia="anel-seis-blocos"),
                            geo_elmer(**kwmesh,topologia="anel-seis-blocos-alinhado"))

    def test_fracao_limites(self):
        for alpha in (.45,.5,.55,.6,.65,.7,.75):
            p=parametros_seis_blocos(48,96,Hy=.04,Hx=.16,
                                    modo_interface="alinhada",fracao_interface=alpha)
            self.assertTrue(p["rm"]<p["ym"]<p["H"])
        for alpha in (-1.,.3,.8,1.,float("nan"),True):
            with self.assertRaises(ValueError):
                parametros_seis_blocos(24,48,modo_interface="alinhada",
                                      fracao_interface=alpha)


if __name__=="__main__":
    unittest.main()
