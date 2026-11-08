import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,"scripts")
from avaliar_ciclo16 import consolidar


class TestResumoCiclo16(unittest.TestCase):
    def test_ausencia_de_execucao_reprova(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                consolidar(Path(folder))


if __name__=="__main__":
    unittest.main()
