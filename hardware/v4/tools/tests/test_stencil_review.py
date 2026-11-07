"""Offline checks for stencil geometry measurements and physical-pad ownership."""
import math
import unittest
import tempfile
import json
from pathlib import Path
from shapely.geometry import box
from shapely.affinity import rotate
from v4kicad.stencil_review import associate, closest_gap, indicators, local_intersection, parts, proposal


class StencilReviewTests(unittest.TestCase):
    def test_rectangle_release_and_wet_volume(self):
        r=indicators(box(0,0,.2,.6))
        self.assertAlmostEqual(r['area_ratio'],.75)
        self.assertAlmostEqual(r['aspect_ratio'],2)
        self.assertAlmostEqual(r['nominal_wet_paste_mm3'],.012)

    def test_rotation_does_not_inflate_dimensions(self):
        r=indicators(rotate(box(0,0,.2,.6),37))
        self.assertAlmostEqual(r['width_mm'],.2)
        self.assertAlmostEqual(r['length_mm'],.6)
        self.assertAlmostEqual(r['area_ratio'],.75)

    def test_nonrectangular_shape_uses_actual_area_and_perimeter(self):
        g=box(0,0,1,1).difference(box(.5,.5,1,1))
        r=indicators(g)
        self.assertAlmostEqual(r['area_ratio'],.75/(4*.1))
        self.assertLess(r['area_ratio'],r['rectangular_area_ratio'])

    def test_reference_prevents_nearby_wrong_pad_match(self):
        pads={'a':box(0,0,1,1),'b':box(0,0,2,2)}
        snapshot={'pads':{'a':{'ref':'U1'},'b':{'ref':'U2'}}}
        self.assertEqual(associate(box(.1,.1,.9,.9),'U1',pads,snapshot),'a')

    def test_same_number_physical_lands_stay_separate(self):
        pads={'a':box(0,0,1,1),'b':box(2,0,3,1)}
        snapshot={'pads':{'a':{'ref':'U1','pin':'49'},'b':{'ref':'U1','pin':'49'}}}
        self.assertEqual(associate(box(2.1,.1,2.9,.9),'U1',pads,snapshot),'b')

    def test_ambiguous_match_fails(self):
        pads={'a':box(0,0,1,1),'b':box(0,0,1,1)}
        snapshot={'pads':{'a':{'ref':'U1'},'b':{'ref':'U1'}}}
        with self.assertRaises(ValueError):
            associate(box(.1,.1,.9,.9),'U1',pads,snapshot)

    def test_unowned_paste_is_reported(self):
        self.assertIsNone(associate(box(0,0,1,1),'U1',{}, {'pads':{}}))

    def test_disconnected_windows_are_counted(self):
        g=box(0,0,1,1).union(box(2,0,3,1))
        self.assertEqual(len(parts(g)),2)
        self.assertAlmostEqual(sum(p.area for p in parts(g)),2)

    def test_touching_drain_flashes_form_one_physical_opening(self):
        g=box(0,0,2,2).union(box(.5,1.8,.9,2.4))
        self.assertEqual(len(parts(g)),1)
        self.assertAlmostEqual(g.area,4.16)

    def test_local_clipping_preserves_actual_mask_hole(self):
        pad=box(0,0,2,2)
        mask=box(-100,-100,100,100).difference(box(.5,.5,1,1))
        self.assertTrue(local_intersection(pad,mask).equals(pad.intersection(mask)))

    def test_bounding_box_distance_is_only_lower_bound(self):
        shapes=[box(0,0,1,1),box(1.2,0,2,1),box(10,10,11,11)]
        gap,j=closest_gap(0,shapes,[g.bounds for g in shapes])
        self.assertEqual(j,1)
        self.assertAlmostEqual(gap,.2)

    def test_exact_proposal_retains_drain_fingers_and_stays_inside_land(self):
        pads,shapes,rows=[],[],[]
        for n,ref in enumerate(('Q1','Q2','Q10','U4')):
            x=10*n
            indices=[]
            specs=([('9',x,0,2.45,2)] if ref!='U4' else [('2',x,0,2,3.8)])
            if ref!='U4':
                specs += [(str(i+5),x+dx,1.15,.4,.6) for i,dx in enumerate((-.98,-.32,.32,.98))]
            for pin,cx,cy,w,h in specs:
                uid=ref+pin
                g=box(cx-w/2,cy-h/2,cx+w/2,cy+h/2)
                index=len(shapes)
                shapes.append(g);rows.append(dict(ref=ref,pad_uuid=uid,index=index))
                pads.append(dict(ref=ref,pad=pin,uuid=uid,position_mm=[cx,cy],
                                 exposed_area_mm2=g.area,aperture_indices=[index]))
        result=dict(pad_records=pads,zip_sha256='zip',current_pcb_sha256='board')
        with tempfile.TemporaryDirectory() as path:
            proposal(Path(path),result,shapes,rows,{}, {})
            data=json.loads((Path(path)/'scratch-only-correction-proposal.json').read_text())
        self.assertEqual(len(data['changes']),4)
        self.assertEqual([len(r['new_windows']) for r in data['changes']],[2,2,2,4])
        for change in data['changes']:
            self.assertLess(change['outside_old_paste_mm2'],1e-8)
            self.assertGreaterEqual(change['min_other_paste_gap_mm'],.199999)


if __name__=='__main__':
    unittest.main()
