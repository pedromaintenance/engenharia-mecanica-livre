import importlib.util
import math
import unittest
from engmec.fem2d_indep import q8_shape,q8_dshape,_gauss_3

NUMPY=importlib.util.find_spec("numpy") is not None
SCIPY=importlib.util.find_spec("scipy") is not None


class TestFEAIndependente(unittest.TestCase):
    def test_particao_unidade_e_interpolacao_q8(self):
        natural=[(-1,-1),(1,-1),(1,1),(-1,1),
                 (0,-1),(1,0),(0,1),(-1,0)]
        for r,s in ((0,0),(-.31,.42),(.57,-.22),(-1,1),(1,0)):
            N=q8_shape(r,s)
            self.assertAlmostEqual(sum(N),1,delta=1e-12)
            self.assertAlmostEqual(sum(n*x for n,(x,y) in zip(N,natural)),r,delta=1e-12)
            self.assertAlmostEqual(sum(n*y for n,(x,y) in zip(N,natural)),s,delta=1e-12)

    def test_derivadas_analiticas_contra_diferencas_finitas(self):
        h=1e-6
        for r,s in ((0,0),(.21,-.19),(-.51,.73),(-1,1)):
            dr,ds=q8_dshape(r,s)
            nrp=q8_shape(r+h,s);nrm=q8_shape(r-h,s)
            nsp=q8_shape(r,s+h);nsm=q8_shape(r,s-h)
            self.assertAlmostEqual(sum(dr),0,delta=1e-12)
            self.assertAlmostEqual(sum(ds),0,delta=1e-12)
            for i in range(8):
                self.assertAlmostEqual(dr[i],(nrp[i]-nrm[i])/(2*h),delta=5e-10)
                self.assertAlmostEqual(ds[i],(nsp[i]-nsm[i])/(2*h),delta=5e-10)

    def test_quadratura_gauss_3(self):
        pts=_gauss_3()
        self.assertAlmostEqual(sum(w for x,w in pts),2)
        self.assertAlmostEqual(sum(w*x*x for x,w in pts),2/3)

    @unittest.skipUnless(NUMPY,"NumPy opcional exigido para teste do B")
    def test_patch_test_tensao_plana_afim(self):
        import numpy as np
        from engmec.fem2d_indep import _b_matrix,_matriz_constitutiva
        E=200e9;nu=.3;eps=2e-4
        xy=np.array([(0,0),(.03,0),(.03,.02),(0,.02),
                     (.015,0),(.03,.01),(.015,.02),(0,.01)],float)
        U=np.array([(eps*x,-nu*eps*y) for x,y in xy]).ravel()
        D=_matriz_constitutiva(E,nu)
        for r,s in ((0,0),(-1,1),(.23,-.37)):
            B,J,pt=_b_matrix(xy,r,s)
            self.assertGreater(J,0)
            sigma=D@(B@U)
            self.assertAlmostEqual(sigma[0],E*eps,delta=.01)
            self.assertAlmostEqual(sigma[1],0,delta=.01)
            self.assertAlmostEqual(sigma[2],0,delta=.01)

    @unittest.skipUnless(NUMPY and SCIPY,"FEA requer NumPy e SciPy opcionais")
    def test_matriz_constitutiva_simetrica_positiva(self):
        import numpy as np
        from engmec.fem2d_indep import _matriz_constitutiva
        D=_matriz_constitutiva(200e9,.3)
        self.assertTrue(np.allclose(D,D.T))
        self.assertTrue(np.all(np.linalg.eigvalsh(D)>0))

    def test_rejeita_material_invalido(self):
        from engmec.fem2d_indep import _matriz_constitutiva
        for E,nu in ((0,.3),(200e9,.5),(200e9,float('nan'))):
            with self.assertRaises(ValueError):
                _matriz_constitutiva(E,nu)


if __name__=="__main__":
    unittest.main()
