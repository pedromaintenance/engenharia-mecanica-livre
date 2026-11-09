"""O dataset do ciclo18 depende de 16 resoluções FEM realmente produzidas."""
import tempfile
import unittest
import sys
from pathlib import Path
sys.path.insert(0,"scripts")
from avaliar_ciclo18 import consolidar


class TestAvaliacaoCiclo18(unittest.TestCase):
    def test_sem_simulacoes_nao_publica(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                consolidar(Path(tmp))


if __name__=="__main__":
    unittest.main()
