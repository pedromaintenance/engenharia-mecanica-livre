import tempfile
import unittest
from pathlib import Path
from engmec.calculix import montar_deck, extrair_dat


class TestCalculixBenchmark(unittest.TestCase):
    def test_malha_e_carregamento(self):
        txt, meta = montar_deck(nx=4)
        self.assertEqual(meta["nos"], 45)
        self.assertEqual(meta["elementos"], 16)
        self.assertAlmostEqual(meta["total_forca_aplicada_n"], 10000)
        self.assertAlmostEqual(meta["deslocamento_analitico_m"], 0.0001, delta=1e-15)
        self.assertIn("*ELEMENT,TYPE=C3D8", txt)
        self.assertIn("*NODE PRINT,NSET=ROOT", txt)
        self.assertIn("*NODE PRINT,NSET=TIPCENTER", txt)

    def test_fixas_sem_superrestricao_transversal(self):
        txt, meta = montar_deck(nx=2, ny=2, nz=2)
        b = txt.split("*BOUNDARY\n", 1)[1].split("*STEP", 1)[0]
        self.assertIn("ROOT,1,1", b)
        self.assertNotIn("ROOT,1,3", b)
        self.assertEqual(sum(x.count(",2,3") for x in b.splitlines()), 1)

    def test_deck_varia_malha(self):
        for n in (1, 3, 8):
            d, m = montar_deck(nx=n, ny=4, nz=2, forca_n=15000)
            self.assertEqual(m["elementos"], 8*n)
            self.assertEqual(m["nos"], (n+1)*15)
            self.assertAlmostEqual(m["total_forca_aplicada_n"], 15000)

    def test_parser_completo_e_equilibrado(self):
        _, meta = montar_deck(nx=1, ny=2, nz=2)
        tip = meta["tip_node"]
        reacoes = "\n".join(f" {n} {-10000/9:.6e} 0.000000E+00 0.000000E+00" for n in meta["root_nodes"])
        txt = (f" displacements (vx,vy,vz) for set TIPCENTER and time 0.1E+01\n"
               f" {tip} 1.000000E-04 0.000000E+00 0.000000E+00\n\n"
               f" reaction forces (rfx,rfy,rfz) for set ROOT and time 0.1E+01\n"
               + reacoes + "\n")
        r = extrair_dat(txt, meta)
        self.assertLess(r["erro_equilibrio_relativo"], 1e-6)
        self.assertEqual(r["erro_deslocamento_relativo"], 0)

    def test_parser_legado_rf_forces(self):
        _, meta = montar_deck(nx=1)
        tip = meta["tip_node"]
        reacoes = "\\n".join(f" {n} {-10000/9:.6e} 0.000000E+00 0.000000E+00"
                              for n in meta["root_nodes"])
        txt = (f" displacements (vx,vy,vz) for set TIPCENTER and time 0.1E+01\\n"
               f" {tip} 1.000000E-04 0.000000E+00 0.000000E+00\\n\\n"
               " forces (fx,fy,fz) for set ROOT and time 0.1E+01\\n"
               + reacoes + "\\n")
        self.assertLess(extrair_dat(txt, meta)["erro_equilibrio_relativo"], 1e-6)

    def test_parser_rejeita_silencio(self):
        _, meta = montar_deck()
        with self.assertRaises(ValueError):
            extrair_dat("", meta)

    def test_rejeita_entradas(self):
        for kwargs in (
            {"nx": 0}, {"ny": 3}, {"nz": 1},
            {"poisson": 0.5}, {"area_mm2": -100}, {"forca_n": float("nan")}
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                montar_deck(**kwargs)


if __name__ == "__main__":
    unittest.main()
