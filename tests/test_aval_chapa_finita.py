import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,"scripts")
from avaliar_chapa_finita import avaliar


class TestResumoFinito(unittest.TestCase):
    def test_consolida_cinco_casos(self):
        with tempfile.TemporaryDirectory() as temp:
            for H,n in ((4,8),(4,16),(4,24),(8,24),(16,24)):
                d=Path(temp)/f'h-{H}-n-{n}'
                d.mkdir()
                data={'entrada':{
                    'razao_semilargura_raio':H,'nr':n,'nt':2*n,
                    'relacao_diametro_largura':1/H,
                    'elementos':2*n*n,'nos':3*n*n,
                    'carregamento_borda_quarto_n':500*H},
                    'resultado':{
                        'kt_gross_estimado_superficie':3.1,
                        'kt_net_estimado_superficie':3.1*(1-1/H),
                        'kt_interiores_primeira_camada':2.9,
                        'bias_extrapolador_sobre_campo_kirsch_exato':0.001,
                        'residuo_ajuste_real':0.003},
                    'tempo_solver_s':0.2}
                (d/'comparacao.json').write_text(json.dumps(data))
            result=avaliar(temp)
            self.assertEqual(len(result['casos']),5)

    def test_sem_solver_falha(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                avaliar(temp)


if __name__=="__main__":
    unittest.main()
