import unittest
from engmec import direitos


class DireitosTest(unittest.TestCase):
    def test_auditoria_valida(self):
        self.assertEqual(direitos.validar(), [])

    def test_licenca_nao_e_conteudo_licenciado_automaticamente(self):
        a = direitos.carregar()["records"]
        self.assertGreaterEqual(len(a), 5)
        self.assertTrue(all(r["permitted_repository_use"].startswith("L0") for r in a))
        self.assertTrue(any(r["id"] == "openstax-univphysics1" and "IA" in r["known_limitations"] for r in a))

    def test_mit_diferencia_politica_e_asset(self):
        mit = [r for r in direitos.carregar()["records"] if r["provider"] == "MIT OpenCourseWare"]
        self.assertGreaterEqual(len(mit), 3)
        self.assertTrue(all(r["audit_level"] == "politica-geral-verificada" for r in mit))


if __name__ == "__main__":
    unittest.main()
