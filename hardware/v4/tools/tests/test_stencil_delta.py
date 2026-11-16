"""Independent mathematical expectations for the composed-CAM verifier."""
import json
import math
from pathlib import Path
import unittest
from v4kicad.stencil_delta import window_polygon


class StencilDeltaTests(unittest.TestCase):
    def test_rounded_rectangle_area_uses_true_corners(self):
        w=dict(nominal_width_mm=.75,nominal_height_mm=1.5,corner_radius_mm=.05,
               center_mm=[111.65,82.1],rotation_deg=0)
        g=window_polygon(w)
        self.assertAlmostEqual(g.area,.75*1.5-(4-math.pi)*.05**2,places=7)
        self.assertLess(g.area,.75*1.5)

    def test_full_precision_q2_center_and_orientation(self):
        p=json.loads(Path('hardware/v4/evidence/phase4-24s-stencil-audit/final-v2/scratch-only-correction-proposal.json').read_text())
        w=next(r for r in p['changes'] if r['ref']=='Q2')['new_windows'][0]
        g=window_polygon(w)
        self.assertAlmostEqual(g.centroid.x,w['center_mm'][0],places=11)
        self.assertAlmostEqual(g.centroid.y,w['center_mm'][1],places=11)
        self.assertGreater(abs(g.centroid.y-round(w['center_mm'][1],6)),1e-8)


if __name__=='__main__':unittest.main()
