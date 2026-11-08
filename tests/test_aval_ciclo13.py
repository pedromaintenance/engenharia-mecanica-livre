import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,"scripts")
from avaliar_ciclo13 import consolidar


class TestCiclo13(unittest.TestCase):
    def test_nao_aprova_sem_solver_externo(self):
        with tempfile.TemporaryDirectory() as p:
            with self.assertRaises(FileNotFoundError):
                consolidar(Path(p))


if __name__=="__main__":
    unittest.main()
