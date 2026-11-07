import math
import unittest

from engmec.kirsch import (tensoes_kirsch, deslocamentos_kirsch, montar_deck,
                           criar_malha, jacobianos_q8, extrair_dat)


class TestKirsch(unittest.TestCase):
    def test_anel_tensoes_exatas(self):
        T=10e6;a=.01
        top=tensoes_kirsch(0,a,a,T)
        right=tensoes_kirsch(a,0,a,T)
        self.assertAlmostEqual(top['sigma_tt_pa'],3*T)
        self.assertAlmostEqual(right['sigma_tt_pa'],-T)
        for e in (top,right):
            self.assertAlmostEqual(e['sigma_rr_pa'],0,delta=.001)
            self.assertAlmostEqual(e['sigma_rt_pa'],0,delta=.001)

    def test_longe_do_furo_tensao_uniforme(self):
        s=tensoes_kirsch(1000*.01,0,.01,10e6)
        self.assertAlmostEqual(s['sigma_xx_pa']/10e6,1,delta=1e-5)
        self.assertAlmostEqual(s['sigma_yy_pa']/10e6,0,delta=1e-5)

    def test_deslocamentos_simetria(self):
        for r in (.01,.08):
            ux,uy=deslocamentos_kirsch(r,0,.01,10e6,200e9,.3)
            self.assertAlmostEqual(uy,0,delta=1e-18)
            ux,uy=deslocamentos_kirsch(0,r,.01,10e6,200e9,.3)
            self.assertAlmostEqual(ux,0,delta=1e-18)

    def test_malha_quadratica_e_qualidade(self):
        m,_=criar_malha(nr=4,nt=8)
        self.assertEqual(len(m['elements']),32)
        self.assertEqual(len(m['nodes']),121)
        self.assertEqual(len(m['hole']),17)
        self.assertTrue(all(len(set(c))==8 for c in m['elements'].values()))
        quality=jacobianos_q8(m)
        self.assertGreater(quality['min_det_jacobiano_m2'],0)
        self.assertEqual(quality['pontos_jacobiano'],128)
        for n in m['hole']:
            self.assertAlmostEqual(math.hypot(*m['nodes'][n][:2]),.01,delta=1e-13)

    def test_deck_contorno_sem_dupla_restricao(self):
        inp,meta=montar_deck(nr=4,nt=8)
        self.assertIn('*ELEMENT,TYPE=CPS8R,ELSET=EALL',inp)
        self.assertIn('*EL PRINT,ELSET=EALL,GLOBAL=YES\nCOORD,S',inp)
        lines=inp.split('*BOUNDARY\n',1)[1].split('*EL PRINT')[0].strip().splitlines()
        constraints=[(int(s.split(',')[0]),int(s.split(',')[1])) for s in lines]
        self.assertEqual(len(constraints),len(set(constraints)))
        self.assertEqual(len(lines),meta['restricoes_dof'])
        self.assertEqual(meta['kt_exato_borda'],3)
        self.assertAlmostEqual(meta['razao_raios'],8)

    def test_nset_nao_excede_16_campos(self):
        for nr,nt in ((4,8),(8,16),(16,32)):
            deck,_=montar_deck(nr=nr,nt=nt)
            for section in ('OUTER','HOLE'):
                part=deck.split(f'*NSET,NSET={section}\n',1)[1].split('*',1)[0].strip()
                self.assertTrue(all(1<=len(line.split(','))<=16 for line in part.splitlines()))

    def test_boundary_tamanho_numerico_compativel_ccx(self):
        deck,_=montar_deck(nr=16,nt=32)
        lines=deck.split('*BOUNDARY\n',1)[1].split('*EL PRINT')[0].strip().splitlines()
        self.assertTrue(all(len(line.strip())<35 for line in lines))
        self.assertTrue(all(len(line.split(',')[-1].strip())<=16 for line in lines))

    def test_parser_sintetico_exato(self):
        _,meta=montar_deck(nr=3,nt=6)
        cs=[];ss=[]
        for e in range(1,meta['elementos']+1):
            for k in range(1,9):
                r=meta['raio_m']+meta['primeira_camada_m']*.5
                theta=0.1+1.2*k/9
                x=r*math.cos(theta);y=r*math.sin(theta)
                st=tensoes_kirsch(x,y,meta['raio_m'],meta['tensao_remota_pa'])
                cs.append(f'{e} {k} {x:.12e} {y:.12e} 0.0')
                ss.append(f"{e} {k} {st['sigma_xx_pa']:.12e} {st['sigma_yy_pa']:.12e} 0 {st['sigma_xy_pa']:.12e} 0 0")
        dat=('coordinates (elem, integ.pnt.,x,y,z) for set EALL and time 0.1E+01\n'+'\n'.join(cs)+
             '\nstresses (elem, integ.pnt.,sxx,syy,szz,sxy,sxz,syz) for set EALL and time 0.1E+01\n'+'\n'.join(ss))
        r=extrair_dat(dat,meta)
        self.assertEqual(r['pontos_integracao'],meta['elementos']*8)
        self.assertLess(r['erro_rms_tensor_rel'],1e-10)
        self.assertLess(r['erro_rms_tensor_ponderado_area_rel'],1e-10)
        self.assertLess(r['erro_rms_anel_fixo_1_5a_rel'],1e-10)
        self.assertGreater(r['pontos_perto_furo'],0)
        self.assertLess(r['kt_proxy_pontos_integracao'],3)

    def test_parser_sem_dados_deve_falhar(self):
        _,meta=montar_deck(nr=3,nt=6)
        with self.assertRaises(ValueError):
            extrair_dat('',meta)

    def test_invalidos(self):
        for p in ({'nr':2},{'nt':5},{'raio_m':-.01},
                  {'raio_externo_m':.02},{'poisson':.5},
                  {'graduacao':6},{'nr':True}):
            with self.subTest(p=p),self.assertRaises(ValueError):
                montar_deck(**p)


if __name__=='__main__':
    unittest.main()
