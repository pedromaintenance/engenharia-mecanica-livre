import math
import unittest

from engmec.calculadoras import (
    cilindro_hidraulico,
    potencia_mecanica,
    disponibilidade_inerente,
    viga_carga_central,
)


class CalculadorasTest(unittest.TestCase):
    def test_cilindro_extensao(self):
        item = cilindro_hidraulico(100, 100, 60, "extensao")
        self.assertAlmostEqual(item["forca_n"], 100 * 1e5 * math.pi * (0.1**2) / 4)

    def test_cilindro_retracao(self):
        item = cilindro_hidraulico(180, 100, 60, "retracao")
        self.assertAlmostEqual(item["forca_kn"], 90.47786842, places=5)

    def test_cilindro_geometria_invalida(self):
        with self.assertRaises(ValueError):
            cilindro_hidraulico(120, 100, 100)
        with self.assertRaises(ValueError):
            cilindro_hidraulico(-5, 100, 30)

    def test_potencia(self):
        item = potencia_mecanica(250, 1800)
        self.assertAlmostEqual(item["potencia_kw"], 15 * math.pi, places=10)

    def test_disponibilidade(self):
        item = disponibilidade_inerente(100, 5)
        self.assertAlmostEqual(item["ai_percentual"], 95.2380952381)
        self.assertEqual(disponibilidade_inerente(20, 0)["ai"], 1)

    def test_viga(self):
        item = viga_carga_central(1000, 2, 200, 50, 100)
        self.assertAlmostEqual(item["momento_maximo_nm"], 500)
        self.assertAlmostEqual(item["momento_inercia_m4"], 0.05 * 0.1**3 / 12)
        self.assertAlmostEqual(item["tensao_flexao_max_mpa"], 6)
        self.assertAlmostEqual(item["flecha_max_mm"], 0.2, places=7)

    def test_viga_nao_fisica(self):
        with self.assertRaises(ValueError):
            viga_carga_central(1000, 2, 0, 50, 100)
        with self.assertRaises(ValueError):
            potencia_mecanica(float("nan"), 100)


if __name__ == "__main__":
    unittest.main()
