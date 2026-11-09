import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,"scripts")
from avaliar_ciclo17 import consolidar,_load_old


class TestResumoCiclo17(unittest.TestCase):
    def test_baseline_integral_16_casos(self):
        self.assertEqual(len(_load_old()),16)

    def test_sem_simulacao_externa_nao_publica(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                consolidar(Path(d))

if __name__=="__main__":
    unittest.main()
