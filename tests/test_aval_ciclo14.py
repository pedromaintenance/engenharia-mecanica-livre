import tempfile
import unittest
import sys
sys.path.insert(0,"scripts")
from avaliar_ciclo14 import consolidar


class TestResumoCiclo14(unittest.TestCase):
    def test_sem_execucao_real_nao_conclui(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                consolidar(directory)


if __name__=="__main__":
    unittest.main()
