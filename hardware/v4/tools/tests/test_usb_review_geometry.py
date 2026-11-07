"""Regressions for false clearance findings from collinear routing."""
import unittest
from v4kicad.usb_review import _segment_distance, _point
from v4kicad.phase411_analysis import _segment_distance as millimetre_distance
from v4kicad.usb_review import geometric_path
from v4kicad.phase411_analysis import local_fill_comparison


class USBGeometryTests(unittest.TestCase):
    def check_distance(self, points, expected):
        self.assertAlmostEqual(_segment_distance(*map(_point,points)),expected, places=9)
        self.assertAlmostEqual(millimetre_distance(*points),expected,places=9)

    def test_real_SYS_bootstrap_separation(self):
        self.check_distance([(48.26,79.25),(48.95,79.25),(49.74,79.25),(50.35,79.25)],.79)

    def test_disjoint_vertical_segments(self):
        self.check_distance([(1,1),(1,2),(1,3),(1,4)],1)

    def test_overlapping_collinear_segments(self):
        self.check_distance([(1,1),(3,1),(2,1),(4,1)],0)

    def test_end_touch_and_cross(self):
        self.check_distance([(0,0),(1,1),(1,1),(2,0)],0)
        self.check_distance([(0,0),(2,2),(0,2),(2,0)],0)

    def test_zero_length_point_outside_and_on_segment(self):
        self.check_distance([(0,0),(1,0),(2,0),(2,0)],1)
        self.check_distance([(0,0),(2,0),(1,0),(1,0)],0)

    def test_duplicate_connector_bottom_crossover_counts_both_barrels(self):
        def pad(pin,x):
            return dict(ref='J7',pin=pin,net='USB_DP',position=[x,0],
                        polygons={'F.Cu':[],'B.Cu':[]},drill_size=[.7,.7])
        snapshot=dict(tracks={'track':dict(net='USB_DP',layer='B.Cu',width=.2,
                                           start=[0,0],end=[5,0])},vias={},
                      pads={'a':pad('A6',0),'b':pad('B6',5)})
        result=geometric_path(snapshot,'USB_DP','J7.A6','J7.B6',{'F.Cu':0,'B.Cu':1.5})
        self.assertTrue(result['connected'])
        self.assertAlmostEqual(result['length_mm'],8)

    def test_actual_plane_hole_change_is_detected(self):
        def layout(hole):
            return {'fills':{'zone':{'net':'PGND','layers':{'In1.Cu':[
                {'outline':[[0,0],[10,0],[10,10],[0,10]],'holes':hole}]}}}}
        original=layout([[[4,4],[6,4],[6,6],[4,6]]])
        changed=layout([])
        result=local_fill_comparison(original,changed,[1,1,9,9],1)
        self.assertFalse(result['all_sampled_fill_occupancy_equal'])
        self.assertGreater(result['changed_samples'],0)

    def test_equal_native_plane_polygons_preserve_grid(self):
        layout={'fills':{'zone':{'net':'PGND','layers':{'In1.Cu':[
            {'outline':[[0,0],[10,0],[10,10],[0,10]],'holes':[]}]}}}}
        result=local_fill_comparison(layout,layout,[1,1,9,9],1)
        self.assertTrue(result['all_sampled_fill_occupancy_equal'])
        self.assertEqual(result['changed_samples'],0)


if __name__=='__main__':
    unittest.main()
