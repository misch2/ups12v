"""Read-only omitted-metadata coverage and scratch-only scope rejection."""
import copy
from pathlib import Path
import unittest
from v4kicad.safety import ToolError
from v4kicad.stencil_native_proof import native_units,require_units_equal,scratch_target,PRODUCTION,UROOT


class NativePasteProofTests(unittest.TestCase):
    def setUp(self):
        self.text='''(kicad_pcb
 (footprint "library:test" (uuid "abc")
  (property "Reference" "Q1")
  (property "Description" "quoted (units fake) and \\"escape\\"")
  (units (unit (name "A") (pins "1" "2" "9"))))
 (footprint "library:test" (uuid "def") (property "Reference" "Q10")))'''

    def test_complete_units_and_explicit_absence(self):
        result=native_units(self.text)
        self.assertEqual(result['Q1']['units'],'(units (unit (name "A") (pins "1" "2" "9")))')
        self.assertEqual(result['Q1']['uuid'],'abc')
        self.assertIsNone(result['Q10']['units'])

    def test_units_loss_is_not_normalized_away(self):
        original=native_units(self.text);changed=copy.deepcopy(original)
        changed['Q1']['units']=None
        with self.assertRaises(ToolError):require_units_equal(original,changed)

    def test_pin_order_and_content_are_preserved(self):
        original=native_units(self.text);changed=copy.deepcopy(original)
        changed['Q1']['units']=changed['Q1']['units'].replace('"1" "2"','"2" "1"')
        with self.assertRaises(ToolError):require_units_equal(original,changed)

    def test_original_identity_is_preserved(self):
        original=native_units(self.text);changed=copy.deepcopy(original)
        changed['Q1']['uuid']='other'
        with self.assertRaises(ToolError):require_units_equal(original,changed)

    def test_incomplete_coverage_rejected(self):
        with self.assertRaises(ToolError):native_units(self.text[:-1])

    def test_production_and_rejected_target_refused(self):
        for path in (PRODUCTION,PRODUCTION.parent/'other.kicad_pcb',UROOT/'new/board.kicad_pcb'):
            with self.assertRaises(ToolError):scratch_target(path)

    def test_real_source_metadata_coverage_and_t_candidate(self):
        source=native_units(PRODUCTION.read_text(encoding='utf-8'))
        self.assertEqual(len(source),154)
        for ref in ('Q1','Q2','U4'):self.assertIsNotNone(source[ref]['units'])
        candidate=Path('hardware/v4/evidence/phase4-24t-stencil-scratch/candidate-v3/ups12v_v4.kicad_pcb')
        require_units_equal(source,native_units(candidate.read_text(encoding='utf-8')))


if __name__=='__main__':unittest.main()
