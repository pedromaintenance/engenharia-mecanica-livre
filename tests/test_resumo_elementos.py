import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,"scripts")
from comparar_elementos import avaliar


class TestComparacaoElementos(unittest.TestCase):
    def test_dois_elementos_tres_malhas(self):
        with tempfile.TemporaryDirectory() as p:
            for n in (2,4,8):
                for family,scale in (("C3D8",0.2),("C3D20R",0.001)):
                    path=Path(p)/family.lower()/f"n-{n}"
                    path.mkdir(parents=True)
                    data={"familia":family,"entrada":{"nx":n,"elementos":n**3,"nos":n**3*(3 if family=="C3D20R" else 1)},
                          "tempo_execucao_s":1.0,
                          "deslocamentos":{"erro_uy_rel":scale/n,"erro_ux_rel":scale/n,
                                           "reacao_norm_max_rel":0.00001},
                          "tensoes":{"erro_rms_sxx_rel":scale/n,"erro_rms_sxx_pa":1e5,
                                     "erro_rms_componentes_nao_axiais_pa":2e3,
                                     "pontos_integracao":8*n**3}}
                    (path/"comparacao.json").write_text(json.dumps(data),encoding="utf-8")
            report=avaliar(p,[2,4,8])
            self.assertEqual(len(report["amostras"]),6)

    def test_falta_de_resultado_reprova(self):
        with tempfile.TemporaryDirectory() as p:
            with self.assertRaises(FileNotFoundError):
                avaliar(p,[2,4,8])


if __name__=="__main__":
    unittest.main()
