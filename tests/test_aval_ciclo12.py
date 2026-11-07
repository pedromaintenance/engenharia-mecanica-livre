import tempfile
import unittest
import sys
sys.path.insert(0,"scripts")
from avaliar_ciclo12 import comparar


class TestCiclo12Resumo(unittest.TestCase):
    def test_sem_arquivos_mais_nao_aferido(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                comparar(temp)


if __name__=="__main__":
    unittest.main()
