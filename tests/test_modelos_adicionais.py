import math
import unittest
from engmec.calculadoras import potencia_hidraulica, conducao_plana, frequencia_natural, numero_reynolds


class ModelosAdicionais(unittest.TestCase):
    def test_bomba_180bar_20lpm(self):
        r = potencia_hidraulica(180, 20, 0.85)
        self.assertAlmostEqual(r["potencia_hidraulica_kw"], 6.0)
        self.assertAlmostEqual(r["potencia_entrada_eixo_kw"], 6 / 0.85)

    def test_eficiencia_nao_fisica(self):
        with self.assertRaises(ValueError):
            potencia_hidraulica(180, 20, 1.1)
        with self.assertRaises(ValueError):
            potencia_hidraulica(180, 20, 0)

    def test_conducao(self):
        r = conducao_plana(0.8, 1.2, 30, 0.2)
        self.assertAlmostEqual(r["taxa_calor_w_assinada"], 144)
        self.assertAlmostEqual(conducao_plana(0.8, 1.2, -30, 0.2)["taxa_calor_w_assinada"], -144)

    def test_vibracao(self):
        r = frequencia_natural(25, 10000)
        self.assertAlmostEqual(r["frequencia_natural_hz"], 20 / (2 * math.pi))
        self.assertAlmostEqual(r["periodo_s"], 2 * math.pi / 20)

    def test_reynolds(self):
        r = numero_reynolds(1000, 1.5, 0.05, 0.001)
        self.assertAlmostEqual(r["reynolds"], 75000)

    def test_parametros_invalidados(self):
        for fn, args in [
            (conducao_plana, (0.8, -1, 10, 0.2)),
            (frequencia_natural, (0, 10000)),
            (numero_reynolds, (1000, 2, 0.05, 0)),
        ]:
            with self.assertRaises(ValueError):
                fn(*args)


if __name__ == "__main__":
    unittest.main()
