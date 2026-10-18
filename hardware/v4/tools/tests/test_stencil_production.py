"""Prove exact reuse of accepted V operation and reject geometry substitutions."""
from pathlib import Path
import unittest
from v4kicad.stencil_production import operation_proof
from v4kicad.safety import ToolError


class ProductionStencilTests(unittest.TestCase):
    def test_native_operation_is_exact_accepted_V(self):
        self.assertTrue(operation_proof()['exact_V_operation_AST'])

    def test_extra_native_change_rejected(self):
        text=Path('hardware/v4/tools/v4kicad/stencil_production.py').read_text(encoding='utf-8')
        text=text.replace('shape.SetParent(fp);fp.Add(shape);added.append(uid)',
                          'shape.SetParent(fp);shape.SetWidth(1);fp.Add(shape);added.append(uid)')
        with self.assertRaises(ToolError):operation_proof(text)

    def test_altered_pad_layer_membership_rejected(self):
        text=Path('hardware/v4/tools/v4kicad/stencil_production.py').read_text(encoding='utf-8')
        text=text.replace('if l!=api.F_Paste','if l!=api.F_Cu')
        with self.assertRaises(ToolError):operation_proof(text)


if __name__=='__main__':unittest.main()
