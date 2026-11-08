import tempfile
import unittest
from pathlib import Path

from engmec.elmer_chapa import geo_elmer,_sif,_parse_elmer_mesh


class TestElmerChapa(unittest.TestCase):
    def test_grupos_fisicos_corretos(self):
        text=geo_elmer(nr=16,nt=32,H=.04,a=.01)
        expected=(
            'Physical Surface("elastic_domain", 101) = {1,2};',
            'Physical Curve("traction_right", 201) = {2};',
            'Physical Curve("symmetry_x_zero", 202) = {6};',
            'Physical Curve("symmetry_y_zero", 203) = {1};',
            'Physical Curve("traction_free_top", 204) = {5};',
            'Physical Curve("traction_free_hole", 205) = {4,7};',
        )
        for line in expected:self.assertIn(line,text)

    def test_sif_condicoes_contorno_material_plane_stress(self):
        info={"body":7,"bc":{"right":11,"sym_x":12,"sym_y":13,"top":14,"hole":15}}
        sif=_sif(info)
        self.assertIn("Plane Stress = Logical True",sif)
        self.assertIn("Procedure = \"StressSolve\" \"StressSolver\"",sif)
        self.assertIn("Target Boundaries(1) = 11\n  Force 1 = Real 10000000",sif)
        self.assertIn("Target Boundaries(1) = 12\n  Displacement 1 = Real 0",sif)
        self.assertIn("Target Boundaries(1) = 13\n  Displacement 2 = Real 0",sif)
        self.assertNotIn("Displacement 1 = Real 0\n  Displacement 2 = Real 0",sif)

    def test_converter_metadata_sintetico(self):
        with tempfile.TemporaryDirectory() as p:
            d=Path(p)
            # Elmer line format: id -1 x y z; boundary: id bc body other type node1 node2...
            nodes=[
                (1,0,.01),(2,.04,0),(3,.04,.04),(4,0,.04),
                (5,0,0),(6,.01,0),(7,.0,.0),
                (8,.04,.02),(9,.02,.04),(10,0,.02),(11,.02,0),
                (12,.01,0),(13,0,.01)
            ]
            (d/"mesh.nodes").write_text("\n".join(
                f"{n} -1 {x} {y} 0" for n,x,y in nodes)+"\n")
            (d/"mesh.elements").write_text("1 9 408 1 2 3 4 8 9 10 11\n")
            (d/"mesh.boundary").write_text(
                "1 31 1 0 203 2 3 8\n"
                "2 32 1 0 203 4 1 10\n"
                "3 33 1 0 203 6 2 11\n"
                "4 34 1 0 203 3 4 9\n"
                "5 35 1 0 203 1 13 12\n"
            )
            # synthetic demo intentionally same node for hole's mid; distinct BC valid
            result=_parse_elmer_mesh(d,H=.04,a=.01)
            self.assertEqual(result["body"],9)
            self.assertEqual(result["bc"]["right"],31)
            self.assertEqual(result["bc"]["hole"],35)
            self.assertEqual(result["elmer_elements"],1)

    def test_nao_aceita_ausencia_de_malha(self):
        with tempfile.TemporaryDirectory() as p:
            with self.assertRaises(FileNotFoundError):
                _parse_elmer_mesh(Path(p),H=.04,a=.01)


if __name__=="__main__":
    unittest.main()
