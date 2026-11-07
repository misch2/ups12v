"""Offline authorization/physical-land guards for the paste-only transaction."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from v4kicad.safety import ToolError
from v4kicad.stencil_scratch import validate_proposal, layer_set


class StencilScratchTests(unittest.TestCase):
    def setUp(self):
        self.proposal=json.loads(Path('hardware/v4/evidence/phase4-24s-stencil-audit/final-v2/scratch-only-correction-proposal.json').read_text())

    def test_exact_reviewed_physical_lands(self):
        self.assertEqual(len(validate_proposal(self.proposal)),4)

    def test_small_duplicate_u4_pin_cannot_replace_large_tab(self):
        self.proposal['changes'][-1]['physical_pad_uuid']='7c5185c3-6eef-4baa-ab1b-82cdf0bbe599'
        with self.assertRaises(ToolError):validate_proposal(self.proposal)

    def test_other_or_duplicate_land_is_rejected(self):
        self.proposal['changes'][2]=copy.deepcopy(self.proposal['changes'][1])
        with self.assertRaises(ToolError):validate_proposal(self.proposal)

    def test_unapproved_global_reduction_rejected(self):
        self.proposal['changes'][0]['new_windows'][0]['nominal_width_mm']=.9
        with self.assertRaises(ToolError):validate_proposal(self.proposal)

    def test_old_source_identity_rejected(self):
        self.proposal['current_board_sha256']=self.proposal['accepted_geometry_pcb_sha256']
        with self.assertRaises(ToolError):validate_proposal(self.proposal)

    def test_native_layer_sequence_type_and_membership_preserved(self):
        class LSEQ(list):pass
        def lset(value):
            if type(value) is not LSEQ:raise TypeError('Concrete native LSEQ required')
            return tuple(value)
        self.assertEqual(layer_set(SimpleNamespace(LSEQ=LSEQ,LSET=lset),[0,1,7]),(0,1,7))


if __name__=='__main__':unittest.main()
