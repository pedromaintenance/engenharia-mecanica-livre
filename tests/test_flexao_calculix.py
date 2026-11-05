import math
import unittest
from engmec.flexao_calculix import montar_deck, deslocamento_exato, extrair_dat


class TestFlexaoCalculix(unittest.TestCase):
    def test_solucao_exata_campos(self):
        # A solução exata gera ε_xx=-k*y e σ_xx=-E*k*y.
        k,nu,x,y,z=0.01,0.3,0.2,0.05,0.0
        ux,uy,uz=deslocamento_exato(x,y,z,k,nu)
        self.assertAlmostEqual(ux,-0.0001)
        self.assertAlmostEqual(uy,0.0002+0.00000375)
        self.assertAlmostEqual(uz,0)

    def test_deck_equilibrio_momento(self):
        deck,meta=montar_deck(nx=4,ny=4,nz=4)
        self.assertEqual(meta["elementos"],64)
        self.assertEqual(meta["nos"],125)
        self.assertAlmostEqual(meta["soma_forcas_total_n"],0,delta=1e-6)
        self.assertAlmostEqual(meta["soma_momentos_total_nm"],0,delta=1e-6)
        self.assertAlmostEqual(meta["soma_momentos_face_nm"]["4"],meta["momento_referencia_nm"],delta=1e-6)
        self.assertAlmostEqual(meta["soma_momentos_face_nm"]["0"],-meta["momento_referencia_nm"],delta=1e-6)
        self.assertIn("*NODE PRINT,NSET=TIPCENTER",deck)
        self.assertIn("*NODE PRINT,NSET=TIPEDGE",deck)
        self.assertIn("*EL FILE,ELSET=EALL",deck)

    def test_reservar_graus_rigidos(self):
        deck,meta=montar_deck(nx=2,ny=2,nz=2)
        sec=deck.split("*BOUNDARY\n",1)[1].split("*STEP",1)[0].strip().splitlines()
        self.assertEqual(len(sec),4)
        self.assertEqual(sec[0],f"{meta['anchor_nodes'][0]},1,3")
        self.assertEqual(sec[-1],f"{meta['anchor_nodes'][2]},1,1")

    def test_malhas_e_coordenadas(self):
        for n in (2,4,8):
            deck,m=montar_deck(nx=n,ny=n,nz=n)
            self.assertEqual(m["elementos"],n**3)
            self.assertAlmostEqual(m["u_tipcenter_referencia_m"][1],0.0002)
            self.assertAlmostEqual(m["u_tipedge_referencia_m"][0],-0.0001)
            self.assertAlmostEqual(m["tensao_max_abs_pa"],100e6)
            self.assertEqual(len(m["anchor_nodes"]),3)

    def test_parser_basico(self):
        _,m=montar_deck(nx=2,ny=2,nz=2)
        a,b=m["tip_center_node"],m["tip_edge_node"]
        rx="\n".join(f"{n} {m['anchor_applied_force_x_n'][str(n)]:.9e} 0.0 0.0" for n in m["anchor_nodes"])
        sample=(f" displacements (vx,vy,vz) for set TIPCENTER and time 0.1E+01\n"
                f"{a} 0.0 2.000000E-04 0.0\n"
                f" displacements (vx,vy,vz) for set TIPEDGE and time 0.1E+01\n"
                f"{b} -1.000000E-04 0.0 0.0\n"
                f" forces (fx,fy,fz) for set ANCHORS and time 0.1E+01\n{rx}\n")
        result=extrair_dat(sample,m)
        self.assertAlmostEqual(result["erro_uy_rel"],0)
        self.assertAlmostEqual(result["erro_ux_rel"],0)
        self.assertAlmostEqual(result["reacao_norm_max_rel"],0)

    def test_parser_detecta_falta(self):
        _,m=montar_deck(nx=2,ny=2,nz=2)
        with self.assertRaises(ValueError):
            extrair_dat("",m)

    def test_invalidos(self):
        for args in (
            {"nx":1},{"ny":3},{"nz":1},{"poisson":0.5},
            {"curvatura_m_inv":0},{"e_gpa":0},{"largura_m":-1},
            {"nx":True},{"ny":18},{"comprimento_m":float("nan")}
        ):
            with self.subTest(args=args),self.assertRaises(ValueError):
                montar_deck(**args)


if __name__=="__main__":
    unittest.main()
