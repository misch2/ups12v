"""Exact accepted footprint-child delta and production adoption preimages."""
import copy
from pathlib import Path
import unittest
from v4kicad.safety import read_json,ToolError
from v4kicad.stencil_adoption import reconcile


class StencilAdoptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path('hardware/v4/evidence/phase4-24u-production-paste-adoption')
        cls.source=read_json(root/'production-identity-v2/capture.json')
        cls.goal=read_json(root/'accepted-candidate-capture/capture.json')

    def test_exact_native_accepted_delta(self):
        result=reconcile(self.source,self.goal)
        self.assertEqual(len(result['footprint_ids']),4)
        self.assertEqual(len(result['pad_ids']),4)
        self.assertEqual(len(result['graphic_ids']),10)

    def test_pad_copper_layer_removal_rejected(self):
        goal=copy.deepcopy(self.goal)
        goal['pads']['e4ac9e85-c811-4bc1-8b0f-fb744a86e69b']['padStack']['layers'].remove('BL_F_Cu')
        with self.assertRaises(ToolError):reconcile(self.source,goal)

    def test_small_duplicate_u4_pin_change_rejected(self):
        goal=copy.deepcopy(self.goal)
        goal['pads']['7c5185c3-6eef-4baa-ab1b-82cdf0bbe599']['padStack']['layers'].remove('BL_F_Paste')
        with self.assertRaises(ToolError):reconcile(self.source,goal)

    def test_unrelated_track_geometry_change_rejected(self):
        goal=copy.deepcopy(self.goal)
        track=next(iter(goal['tracks'].values()))
        track['width']['valueNm']=str(int(track['width']['valueNm'])+1)
        with self.assertRaises(ToolError):reconcile(self.source,goal)

    def test_original_footprint_child_removal_rejected(self):
        goal=copy.deepcopy(self.goal)
        fp=next(f for f in goal['footprints'].values() if any(i.get('id',{}).get('value')=='e4ac9e85-c811-4bc1-8b0f-fb744a86e69b' for i in f['definition']['items']))
        fp['definition']['items'].pop(0)
        with self.assertRaises(ToolError):reconcile(self.source,goal)

    def test_unrelated_footprint_property_change_rejected(self):
        goal=copy.deepcopy(self.goal)
        fp=next(f for f in goal['footprints'].values() if any(i.get('id',{}).get('value')=='e4ac9e85-c811-4bc1-8b0f-fb744a86e69b' for i in f['definition']['items']))
        fp['position']['xNm']=str(int(fp['position']['xNm'])+1)
        with self.assertRaises(ToolError):reconcile(self.source,goal)


if __name__=='__main__':unittest.main()
