import math
import unittest

from engmec.comparar_elementos import forma_q8, montar_deck, extrair_tensoes_dat


class TestCompararElementos(unittest.TestCase):
    def test_interpolacao_q8_e_particao_unidade(self):
        for r, s in ((0, 0), (0.2, -0.4), (-1, -1), (1, 1), (1/3, 1/2)):
            n=forma_q8(r,s)
            self.assertAlmostEqual(sum(n),1,delta=1e-12)
            coords=[(-1,-1),(1,-1),(1,1),(-1,1),
                    (0,-1),(1,0),(0,1),(-1,0)]
            self.assertAlmostEqual(sum(v*x for v,(x,y) in zip(n,coords)),r,delta=1e-12)
            self.assertAlmostEqual(sum(v*y for v,(x,y) in zip(n,coords)),s,delta=1e-12)

    def test_deck_quad_malha_2(self):
        deck,meta=montar_deck("C3D20R",2,2,2)
        self.assertIn("*ELEMENT,TYPE=C3D20R,ELSET=EALL",deck)
        self.assertIn("*EL PRINT,ELSET=EALL,GLOBAL=YES\nCOORD,S",deck)
        self.assertEqual(meta["nos"],81)
        self.assertEqual(meta["elementos"],8)
        self.assertEqual(meta["familia"],"C3D20R")
        self.assertAlmostEqual(meta["soma_forcas_total_n"],0,delta=1e-6)
        self.assertAlmostEqual(meta["soma_momentos_total_nm"],0,delta=1e-6)
        self.assertAlmostEqual(meta["soma_momentos_face_nm"]["2"],meta["momento_referencia_nm"],delta=1e-6)
        self.assertAlmostEqual(meta["soma_momentos_face_nm"]["0"],-meta["momento_referencia_nm"],delta=1e-6)

    def test_carga_quadratica_sem_residuos_quase_nulos(self):
        deck, meta=montar_deck("C3D20R",2,2,2)
        linhas=deck.split("*CLOAD\n",1)[1].split("*NODE PRINT",1)[0].strip().splitlines()
        valores=[float(line.split(",")[2]) for line in linhas]
        self.assertTrue(valores)
        self.assertGreater(min(abs(f) for f in valores),1e-5)
        self.assertNotIn("*EL FILE,ELSET=EALL",deck)
        self.assertIn("*EL FILE\nS",deck)

    def test_conn_20_e_mids_compartilhados(self):
        deck,meta=montar_deck("C3D20R",4,2,2)
        part=deck.split("*ELEMENT,TYPE=C3D20R,ELSET=EALL\n")[1].split("*NSET,")[0]
        lines=part.strip().splitlines()
        self.assertEqual(len(lines),32)
        conn=[
            [int(n) for n in lines[i].split(",")] + [int(n) for n in lines[i+1].split(",")]
            for i in range(0,len(lines),2)
        ]
        self.assertEqual(len(conn),16)
        self.assertTrue(all(len(lines[i].split(","))==16 and len(lines[i+1].split(","))==5
                            for i in range(0,len(lines),2)))
        self.assertTrue(all(len(c)==21 for c in conn))
        edges={(min(a,b),max(a,b)) for x in conn
               for a,b in zip(x[1:9], x[2:10])}
        self.assertGreater(len(edges),0)
        self.assertTrue(all(len(set(c[1:]))==20 for c in conn))
        self.assertTrue(all(len({mid for mid in c[9:]})==12 for c in conn))

    def test_linhas_de_conectividade_nao_excedem_16_entradas(self):
        deck,_=montar_deck("C3D20R",8,8,8)
        part=deck.split("*ELEMENT,TYPE=C3D20R,ELSET=EALL\n")[1].split("*NSET,")[0]
        lines=part.strip().splitlines()
        self.assertEqual(len(lines),2*8**3)
        self.assertTrue(all(len(line.split(","))<=16 for line in lines))
        self.assertTrue(all(len(lines[i].split(","))==16 and len(lines[i+1].split(","))==5
                            for i in range(0,len(lines),2)))

    def test_deck_linear_com_saida_tensao(self):
        deck,meta=montar_deck("C3D8",2,2,2)
        self.assertIn("*ELEMENT,TYPE=C3D8,ELSET=EALL",deck)
        self.assertIn("COORD,S",deck)
        self.assertEqual(meta["nos"],27)

    def test_tensao_sintetica_rms(self):
        _,meta=montar_deck("C3D8",2,2,2)
        coords=[]
        stress=[]
        for e in range(1,meta["elementos"]+1):
            for ip in range(1,9):
                y=(ip-4.5)*0.005
                sx=-meta["e_pa"]*meta["curvatura_m_inv"]*y
                coords.append(f"{e} {ip} 0.05 {y:.10g} 0.01")
                stress.append(f"{e} {ip} {sx:.10g} 0 0 0 0 0")
        data=(
            "coordinates (elem, integ.pnt.,x,y,z) for set EALL and time 0.1E+01\n"
            +"\n".join(coords)+"\n\n"
            +"stresses (elem, integ.pnt.,sxx,syy,szz,sxy,sxz,syz) for set EALL and time 0.1E+01\n"
            +"\n".join(stress)+"\n"
        )
        s=extrair_tensoes_dat(data,meta)
        self.assertEqual(s["pontos_integracao"],64)
        self.assertAlmostEqual(s["erro_rms_sxx_rel"],0,delta=1e-13)
        self.assertAlmostEqual(s["erro_rms_componentes_nao_axiais_pa"],0,delta=1e-13)

    def test_rejeitar_resultado_incompleto(self):
        _,m=montar_deck("C3D20R",2,2,2)
        with self.assertRaises(ValueError):
            extrair_tensoes_dat("stresses for set EALL and time 1\n",m)

    def test_rejeitar_parametros(self):
        for kwargs in ({"familia":"ABC"},{"nx":1},{"ny":3},{"e_gpa":-5},{"poisson":0.5}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                montar_deck(**kwargs)


if __name__=="__main__":
    unittest.main()
