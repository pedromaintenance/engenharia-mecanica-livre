import math
import unittest

from engmec.chapa_finita import (gerar_malha, montar_deck, _parse_dat,
                                  analisar_tensoes, _extrapolar_superficie,
                                  _solve_linear)
from engmec.kirsch import tensoes_kirsch


class TestChapaFinita(unittest.TestCase):
    def test_geometria_contorno_real_e_jacobianos(self):
        m=gerar_malha(nr=8,nt=16,semilargura_m=.04)
        self.assertEqual(len(m["elements"]),128)
        self.assertEqual(len(m["nodes"]),(8+1)*(16+1)+8*(16+1)+(8+1)*16)
        self.assertGreater(m["quality"]["min_det_jacobiano_m2"],0)
        for trip in m["right_segments"]:
            self.assertTrue(all(abs(m['nodes'][n][0]-.04)<1e-12 for n in trip))
        for trip in m["top_segments"]:
            self.assertTrue(all(abs(m['nodes'][n][1]-.04)<1e-12 for n in trip))
        for n in m["hole"]:
            self.assertAlmostEqual(math.hypot(*m["nodes"][n][:2]),.01,delta=1e-13)

    def test_carregamento_real_uniforme(self):
        txt,meta=montar_deck(nr=8,nt=16,semilargura_m=.04,
                            tensao_pa=10e6,espessura_m=.005)
        self.assertEqual(meta["condicao_contorno"],"tracao_T_uniaxial_borda_x_H_topo_livre")
        self.assertIn("*CLOAD\n",txt)
        self.assertNotIn("deslocamentos_analiticos_kirsch",txt)
        self.assertAlmostEqual(meta["carregamento_borda_quarto_n"],2000)
        self.assertEqual(meta["segmentos_borda_direita"],8)
        self.assertEqual(meta["segmentos_borda_superior_livre"],8)
        block=txt.split("*CLOAD\n",1)[1].split("*EL PRINT")[0]
        values=[float(line.split(",")[-1]) for line in block.strip().splitlines()]
        self.assertAlmostEqual(sum(values),2000,delta=.01)
        self.assertAlmostEqual(meta["tensao_liquida_nominal_pa"],10e6/.75)
        # Todas as cargas agem em X e seus nós estão na aresta direita.
        mesh=gerar_malha(nr=8,nt=16,semilargura_m=.04)
        for line in block.strip().splitlines():
            ident,axis,value=line.split(",")
            self.assertEqual(axis.strip(),"1")
            self.assertAlmostEqual(mesh["nodes"][int(ident)][0],.04,delta=1e-12)

    def test_ausencia_de_engaste_artificial(self):
        txt,_=montar_deck(nr=4,nt=8)
        bounds=txt.split("*BOUNDARY\n",1)[1].split("*CLOAD",1)[0]
        constraints=[line.split(",") for line in bounds.splitlines()]
        self.assertTrue(all(v[3].strip()=="0" for v in constraints))
        self.assertFalse(any(int(v[1])==3 for v in constraints))
        self.assertEqual(len({(int(v[0]),int(v[1])) for v in constraints}),len(constraints))

    def test_malha_refinada_e_razoes(self):
        for H in (.03,.04,.08,.16):
            _,m=montar_deck(nr=12,nt=24,semilargura_m=H)
            self.assertEqual(m["elementos"],288)
            self.assertEqual(m["relacao_diametro_largura"],.01/H)
            self.assertGreater(m["qualidade_malha"]["min_det_jacobiano_m2"],0)

    def test_rejeita_parametros(self):
        for args in ({"nr":2},{"nt":6},{"nt":14},{"raio_m":-.01},
                     {"semilargura_m":.02},{"poisson":.5},{"graduacao":5},
                     {"nr":True},{"tensao_pa":float('nan')}):
            with self.subTest(args=args),self.assertRaises(ValueError):
                montar_deck(**args)

    def test_extrapolador_polynomial(self):
        a=.01;dr=.001;dt=.02
        pts=[]
        for x in (.2,.5,.8,1.2,1.5,1.8,2.2,2.5):
            for y in (.2,.5,.8,1.2,1.5,1.8):
                val=3.+.2*x+.03*x*x-.1*y*y+.02*x*y*y+.006*y**4
                pts.append((a+dr*x,math.pi/2-dt*y,val))
        r=_extrapolar_superficie(pts,raio_m=a,delta_r=dr,delta_theta=dt)
        self.assertAlmostEqual(r["valor_extrapolado"],3.,places=8)
        self.assertLess(r["residuo_ajuste"],1e-8)

    def test_parser_kirsch_sintetico(self):
        n=12;nt=24;a=.01;H=.04;T=10e6
        _,meta=montar_deck(nr=n,nt=nt,semilargura_m=H)
        coords=[];stresses=[]
        for elem in range(1,meta["elementos"]+1):
            i=(elem-1)//nt;j=(elem-1)%nt
            for ip in range(1,9):
                fr=(.25 if (ip-1)%2==0 else .75)
                ft=(.25 if ((ip-1)//2)%2==0 else .75)
                th=math.pi*(j+ft)/(2*nt)
                rmax=H/max(math.sin(th),math.cos(th))
                r=a+(rmax-a)*((i+fr)/n)**2
                x,y=r*math.cos(th),r*math.sin(th)
                stress=tensoes_kirsch(x,y,a,T)
                coords.append(f'{elem} {ip} {x:.14e} {y:.14e} 0.0')
                stresses.append(f'{elem} {ip} {stress["sigma_xx_pa"]:.14e} '
                                f'{stress["sigma_yy_pa"]:.14e} 0 '
                                f'{stress["sigma_xy_pa"]:.14e} 0 0')
        dat=('coordinates (elem, integ.pnt.,x,y,z) for set EALL and time 0.1E+01\n'
            +'\n'.join(coords)+'\n'
            +'stresses (elem, integ.pnt.,sxx,syy,szz,sxy,sxz,syz) for set EALL and time 0.1E+01\n'
            +'\n'.join(stresses)+'\n')
        result=analisar_tensoes(dat,meta)
        self.assertEqual(result["pontos_integracao_total"],8*meta["elementos"])
        self.assertAlmostEqual(result["bias_extrapolador_sobre_campo_kirsch_exato"],0,delta=.05)
        self.assertAlmostEqual(result["kt_gross_estimado_superficie"],3,delta=.05)
        self.assertAlmostEqual(result["kt_net_estimado_superficie"],2.25,delta=.05)

    def test_parser_sem_dados_nao_aprova(self):
        _,m=montar_deck(nr=4,nt=8)
        with self.assertRaises(ValueError):
            analisar_tensoes("",m)


if __name__=="__main__":
    unittest.main()
