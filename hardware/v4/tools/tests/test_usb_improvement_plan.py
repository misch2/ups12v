"""Export-only regressions for the focused Phase4.12 owner proposal."""
import copy
import unittest
from v4kicad.usb_improvement_plan import (
    load, moved_U2, u2_candidate, combined_proposal, gap_candidate, materialize,
    fallback_with_gap,
)


class USBImprovementPlanTests(unittest.TestCase):
    def test_virtual_placement_preserves_source_and_exact_pad_offsets(self):
        g,c,l=load();before=copy.deepcopy(g)
        moved,courts=moved_U2(g,l,[115,81.4])
        pads={p['pin']:p['position'] for p in moved['pads'].values() if p['ref']=='U2'}
        self.assertEqual(pads,{'1':[115.425,81.75],'2':[115.425,81.05],'3':[114.575,81.4]})
        self.assertEqual(g,before)
        self.assertTrue(courts)

    def test_nearby_through_via_collision_is_rejected(self):
        # The F-only view appears clear, but the return via hits B-side VBUS.
        candidate=u2_candidate([115.3,82],[114.284,82])
        self.assertFalse(candidate['valid'])
        self.assertTrue(candidate['joint_check']['errors'])

    def test_joint_explicit_paths_and_gap_option_remain_clear(self):
        proposal,g=combined_proposal()
        self.assertTrue(proposal['valid'],proposal['joint_check']['errors'])
        gap=gap_candidate()
        self.assertTrue(gap['valid'],gap['joint_check']['errors'])
        fallback=fallback_with_gap()
        self.assertTrue(fallback['valid'],fallback['joint_check']['errors'])
        # Reusing synthetic IDs must fail instead of silently deleting geometry.
        with self.assertRaises(Exception):materialize(g,proposal['proposed_plan'])


if __name__=='__main__':unittest.main()
