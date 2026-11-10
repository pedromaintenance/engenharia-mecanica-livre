"""Avaliação só publica resultados se 16 FEM Elmer existirem."""
import tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,"scripts")
from avaliar_ciclo19 import consolidar


class TestAvaliacaoCiclo19(unittest.TestCase):
    def test_nao_aceita_dados_fabricados_ou_ausentes(self):
        with tempfile.TemporaryDirectory() as path:
            with self.assertRaises(FileNotFoundError):
                consolidar(Path(path))


if __name__=="__main__":
    unittest.main()
