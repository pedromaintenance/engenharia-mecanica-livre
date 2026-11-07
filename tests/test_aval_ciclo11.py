import unittest
import tempfile
from pathlib import Path
import sys
sys.path.insert(0,'scripts')
from avaliar_ciclo11 import consolidar


class TestAvaliacaoCiclo11(unittest.TestCase):
    def test_sem_execucoes_nao_conclui(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                consolidar(temp,Path('docs/dados/chapa-finita-furo-2026-11-07.json'))


if __name__=="__main__":
    unittest.main()
