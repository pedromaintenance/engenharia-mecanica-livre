import unittest
from engmec import recursos


class TestRecursos(unittest.TestCase):
    def test_catalogos_tem_registros(self):
        c = recursos.contagem()
        self.assertGreaterEqual(c["cursos"], 10)
        self.assertGreaterEqual(c["portais"], 20)
        self.assertGreaterEqual(c["ferramentas"], 17)

    def test_validacao(self):
        self.assertEqual(recursos.validar(), [])

    def test_busca_acento_e_tipo(self):
        resultados = recursos.buscar("cursos", "CALCULO")
        self.assertTrue(any(x["id"] == "mit-calculo-1" for x in resultados))
        self.assertTrue(all(x["tipo_catalogo"] == "cursos" for x in resultados))

    def test_pre_requisitos(self):
        cursos = recursos.carregar("cursos")["records"]
        base = next(x for x in cursos if x["id"] == "mit-calculo-2")
        self.assertIn("mit-calculo-1", base["prerequisites"])

    def test_bad_type(self):
        with self.assertRaises(ValueError):
            recursos.carregar("../../etc/passwd")

    def test_licencas_referenciadas(self):
        for tipo in recursos.TIPOS:
            for x in recursos.carregar(tipo)["records"]:
                self.assertTrue(x["url"].startswith("https://"))


if __name__ == "__main__":
    unittest.main()
