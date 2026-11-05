import unittest

from engmec import catalogo


class CatalogoTest(unittest.TestCase):
    def test_catalogo_valido(self):
        self.assertEqual(catalogo.validar(), [])

    def test_busca_com_acentos(self):
        itens = catalogo.buscar("METROLOGIA")
        self.assertTrue(any(x["id"] == "inmetro-metrologia" for x in itens))
        self.assertTrue(any(x["id"] == "nist-webbook" for x in itens))

    def test_restrito_nao_republicavel(self):
        itens = [x for x in catalogo.carregar()["fontes"] if x["acesso"] == "restrito"]
        self.assertGreaterEqual(len(itens), 2)
        self.assertTrue(all(x["redistribuicao"] == "somente-link" for x in itens))

    def test_id_duplicado(self):
        dados = catalogo.carregar()
        dados["fontes"].append(dict(dados["fontes"][0]))
        self.assertTrue(any("repetido" in msg for msg in catalogo.validar(dados)))


if __name__ == "__main__":
    unittest.main()
