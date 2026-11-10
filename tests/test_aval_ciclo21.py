"""Não aceitar resultados sintéticos, ausentes ou matriz incompleta."""
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, "scripts")
from avaliar_ciclo21 import consolidar
from varrer_ciclo21 import FRACOES, GEOMETRIAS


class TestAvaliadorCiclo21(unittest.TestCase):
    def test_recusa_ausencia_de_solver_real(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                consolidar(Path(d), Path(d) / "varredura.json")

    def test_matriz_e_fracoes_finitas(self):
        self.assertEqual(len(FRACOES), 7)
        self.assertEqual(len(GEOMETRIAS), 4)
        self.assertTrue(all(.45 <= a <= .75 for a in FRACOES))
        self.assertEqual(len(set(FRACOES)), len(FRACOES))

if __name__=="__main__":
    unittest.main()
