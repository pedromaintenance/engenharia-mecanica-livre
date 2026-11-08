import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,"scripts")
from avaliar_ciclo15 import consolidar,BASELINE_SQUARE


class TestCiclo15Resumo(unittest.TestCase):
    def test_baseline_de_six_malhas_preservado(self):
        self.assertEqual(len(BASELINE_SQUARE),6)
        self.assertAlmostEqual(BASELINE_SQUARE[(4,24)],3.584406203951414)

    def test_sem_dados_externos_reprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                consolidar(Path(tmp))


if __name__=="__main__":
    unittest.main()
