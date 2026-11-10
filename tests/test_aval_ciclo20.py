"""O avaliador do ciclo 20 não aceita ausência de simulações nem substitutos."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, "scripts")
from avaliar_ciclo20 import consolidar


class TestAvaliacaoCiclo20(unittest.TestCase):
    def test_proibe_publicar_dataset_sem_resultados_reais(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                consolidar(Path(d))

    def test_baseline_referencia_sempre_ciclo19(self):
        from pathlib import Path
        text = Path("scripts/avaliar_ciclo20.py").read_text(encoding="utf-8")
        self.assertIn("ciclo19-anel-multibloco-2026-11-09.json", text)
        self.assertIn('"anel-seis-blocos"', text)
        self.assertIn("verificar_seis_blocos", text)


if __name__ == "__main__":
    unittest.main()
