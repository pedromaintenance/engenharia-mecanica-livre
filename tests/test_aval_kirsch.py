import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0,"scripts")
from avaliar_kirsch import avaliar


class TestAvaliacaoKirsch(unittest.TestCase):
    def test_convergencia_sintetica_passa(self):
        with tempfile.TemporaryDirectory() as p:
            for n,e,h,k in ((4,.2,.3,2.2),(8,.08,.13,2.55),(16,.03,.04,2.8)):
                path=Path(p)/f'n-{n}'
                path.mkdir()
                doc={'entrada':{'nr':n,'nt':2*n,'razao_raios':8,
                      'elementos':2*n*n,'nos':10*n,'qualidade_malha':{'min_det_jacobiano_m2':1e-9}},
                     'tempo_solver_s':.05,
                     'resultado':{'erro_rms_tensor_rel':e,'erro_rms_tensor_ponderado_area_rel':e,
                      'erro_rms_anel_fixo_1_5a_rel':h,'erro_rms_proximo_furo_rel':h,
                      'kt_proxy_pontos_integracao':k,'kt_borda_analitico':3,
                      'pontos_integracao':16*n*n}}
                (path/'comparacao.json').write_text(json.dumps(doc))
            v=avaliar(p,[4,8,16])
            self.assertEqual(len(v['malhas']),3)
            self.assertGreater(v['taxas_aparentes_erro_tensor'][0],0)

    def test_sem_solver_falha(self):
        with tempfile.TemporaryDirectory() as p:
            with self.assertRaises(FileNotFoundError):
                avaliar(p,[4,8,16])


if __name__=='__main__':
    unittest.main()
