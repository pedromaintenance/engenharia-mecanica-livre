import unittest
from engmec import descoberta


class TestDescoberta(unittest.TestCase):
    def test_url_crossref(self):
        url = descoberta.montar_url("crossref", "hydraulic pump", 3, "exemplo@dominio.org")
        self.assertIn("query=hydraulic+pump", url)
        self.assertIn("mailto=exemplo%40dominio.org", url)
        self.assertIn("rows=3", url)

    def test_limites(self):
        with self.assertRaises(ValueError):
            descoberta.montar_url("openalex", "xx", 5)
        with self.assertRaises(ValueError):
            descoberta.montar_url("crossref", "vibrations", 21)
        with self.assertRaises(ValueError):
            descoberta.obter_json("https://notvalid.example/works")

    def test_crossref_metadados(self):
        resposta = {"message": {"items": [
            {"DOI": "10.1234/ABCD", "title": ["Test Article"],
             "URL": "https://example.org/article",
             "author": [{"given": "Ana", "family": "Silva"}],
             "published": {"date-parts": [[2022, 5]]}},
            {"title": [], "URL": "https://example.org/no-title"}
        ]}}
        resultado = descoberta.descobrir("crossref", "pump fatigue", fetcher=lambda _: resposta)
        self.assertEqual(resultado["count"], 1)
        item = resultado["records"][0]
        self.assertEqual(item["url"], "https://doi.org/10.1234/abcd")
        self.assertEqual(item["year"], 2022)
        self.assertEqual(item["authors"], ["Ana Silva"])
        self.assertEqual(item["status"], "candidato-nao-auditado")

    def test_openalex_sem_doi(self):
        resposta = {"results": [{
            "title": "Bearing failure study",
            "id": "https://openalex.org/W1234",
            "publication_year": 2020,
            "authorships": [{"author": {"display_name": "Prof. X"}}]
        }]}
        resultado = descoberta.descobrir("openalex", "bearing failure", fetcher=lambda _: resposta)
        self.assertEqual(resultado["count"], 1)
        self.assertEqual(resultado["records"][0]["url"], "https://openalex.org/W1234")


if __name__ == "__main__":
    unittest.main()
