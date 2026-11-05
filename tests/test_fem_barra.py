import math
import unittest
from engmec.fem_barra import barra_axial, estudo_refinamento


class FemBarraTest(unittest.TestCase):
    def test_tracao_simples_exata(self):
        for n in (1, 2, 4, 16):
            r = barra_axial(2, 1000, 200, 10000, 0, n)
            self.assertAlmostEqual(r["resultados_si"]["deslocamento_ponta_m"], 1e-4, delta=1e-15)
            self.assertAlmostEqual(r["resultados_si"]["reacao_apoio_n"], -10000, delta=1e-6)
            for t in r["resultados_si"]["tensoes_elementos_pa"]:
                self.assertAlmostEqual(t, 10e6, delta=0.1)

    def test_carga_distribuida(self):
        r = barra_axial(2, 1000, 200, 10000, 1000, 4)
        self.assertAlmostEqual(r["resultados_si"]["deslocamento_ponta_m"], 0.00011, delta=1e-15)
        self.assertAlmostEqual(r["resultados_si"]["reacao_apoio_n"], -12000, delta=1e-6)
        self.assertLess(r["verificacao"]["erro_nodal_max_m"], 1e-12)
        self.assertLess(r["verificacao"]["erro_trabalho_energia_j"], 1e-8)

    def test_convergencia_rms_tensao(self):
        out = estudo_refinamento(2, 1000, 200, 10000, 1000, (1, 2, 4, 8))
        rms = [m["erro_tensao_rms_pa"] for m in out["malhas"]]
        self.assertAlmostEqual(rms[0], 1000 * 2 / (math.sqrt(12) * 0.001), delta=0.01)
        for a, b in zip(rms, rms[1:]):
            self.assertAlmostEqual(a / b, 2, delta=1e-7)

    def test_compressao_e_reacao(self):
        r = barra_axial(1, 500, 100, -10000, 0, 8)
        self.assertLess(r["resultados_si"]["deslocamento_ponta_m"], 0)
        self.assertAlmostEqual(r["resultados_si"]["reacao_apoio_n"], 10000, delta=1e-6)

    def test_sem_carregamento(self):
        r = barra_axial(1, 200, 100, 0, 0, 3)
        self.assertEqual(r["resultados_si"]["deslocamento_ponta_m"], 0)
        self.assertEqual(r["verificacao"]["erro_tensao_rms_pa"], 0)

    def test_validacoes(self):
        casos = [(0, 1000, 200, 10, 0, 2), (1, 0, 200, 10, 0, 2),
                 (1, 1000, float("nan"), 10, 0, 2),
                 (1, 1000, 200, 10, 0, 0), (1, 1000, 200, 10, 0, 2001)]
        for args in casos:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    barra_axial(*args)

    def test_mesmo_estado_de_malha(self):
        r = barra_axial(2, 1000, 200, 10000, 1000, 16)
        self.assertEqual(len(r["resultados_si"]["posicoes_nos_m"]), 17)
        self.assertEqual(len(r["resultados_si"]["tensoes_elementos_pa"]), 16)


if __name__ == "__main__":
    unittest.main()
