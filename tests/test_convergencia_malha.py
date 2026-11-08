import math
import tempfile
import unittest
from pathlib import Path
from engmec.convergencia_malha import convergencia_condicionada,qualidade_geometrica


class TestConvergenciaFina(unittest.TestCase):
    def test_convergencia_sintetica_ordem_dois(self):
        points=[(n,3.2+2/n**2) for n in (24,32,40,48)]
        a=convergencia_condicionada(points)
        self.assertEqual(a["status"],"estimativa_condicionada_ordem_estavel")
        self.assertAlmostEqual(a["ordem_observada"]["32_40_48"],2.,places=7)
        self.assertAlmostEqual(a["extrapolacao_richardson"],3.2,places=10)
        self.assertGreater(a["GCI_fino_relativo"],0)

    def test_nao_monotonica_bloqueia_gci(self):
        a=convergencia_condicionada([(24,3.),(32,3.05),(40,3.03),(48,3.04)])
        self.assertIsNone(a["GCI_fino_relativo"])
        self.assertEqual(a["status"],"nao_comprovada")

    def test_mais_que_tres_malhas_requeridas(self):
        with self.assertRaises(ValueError):
            convergencia_condicionada([(24,3.),(40,3.),(48,3.)])

    def test_nao_finitos_rejeitados(self):
        with self.assertRaises(ValueError):
            convergencia_condicionada([(24,3.),(32,math.nan),(40,3.),(48,3.)])

    def test_sem_malha_real_nao_aceita(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                qualidade_geometrica(Path(tmp)/"inexistente.msh",
                                     a=.01,H=.04,L=.16,nr=32,nt=64)


if __name__=="__main__":
    unittest.main()
