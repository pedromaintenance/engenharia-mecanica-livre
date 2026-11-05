import json
import tempfile
import unittest
from pathlib import Path
from importlib.machinery import SourceFileLoader
# Exercícios usam módulo Python puro que também pode ser invocado como CLI.
import sys
sys.path.insert(0,"scripts")
from avaliar_convergencia import avaliar


class TestConvergencia(unittest.TestCase):
    def test_reducao_real(self):
        with tempfile.TemporaryDirectory() as temp:
            for n,err in ((2,.1),(4,.03),(8,.009)):
                dest=Path(temp)/f"n-{n}"
                dest.mkdir()
                data={"entrada":{"elementos":n**3},"resultado":{
                    "uy_centro_ponta_m":1,"ux_borda_ponta_m":-1,
                    "erro_uy_rel":err,"erro_ux_rel":err*.5,
                    "reacao_norm_max_rel":0}}
                (dest/"comparacao.json").write_text(json.dumps(data),encoding="utf-8")
            r=avaliar(temp,[2,4,8])
            self.assertEqual(r["aceite"]["melhora_relativa_minima_25pct"],True)
            self.assertGreater(r["taxas_uy"][0],1)

    def test_erro_trivial_reprovado(self):
        with tempfile.TemporaryDirectory() as temp:
            for n in (2,4,8):
                dest=Path(temp)/f"n-{n}";dest.mkdir()
                (dest/"comparacao.json").write_text(json.dumps({
                    "entrada":{"elementos":n**3},"resultado":{
                        "uy_centro_ponta_m":1,"ux_borda_ponta_m":1,
                        "erro_uy_rel":0,"erro_ux_rel":0,"reacao_norm_max_rel":0}
                }),encoding="utf-8")
            with self.assertRaises(ValueError):
                avaliar(temp,[2,4,8])


if __name__=="__main__":
    unittest.main()
