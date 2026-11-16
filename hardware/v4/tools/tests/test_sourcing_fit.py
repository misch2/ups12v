"""Focused offline geometry regressions. No native APIs."""
import unittest
from v4kicad.sourcing_fit import terminals, world, other_net_clearances


class SourcingFitTests(unittest.TestCase):
    def test_kicad_negative_90_keeps_pin_one_at_top(self):
        a,b = [world(t,(49.65,85),-90) for t in terminals(2.3,1.1,4.3)]
        self.assertLess(a.centroid.y,85)
        self.assertGreater(b.centroid.y,85)
        self.assertAlmostEqual(a.centroid.x,49.65)

    def test_coilank_minimum_depth_is_not_nominal_overlap(self):
        from shapely.geometry import box
        land = box(1.065,-2.35,2.245,2.35)
        nominal = terminals(2.3,1.1,4.3)[1].intersection(land).area
        corner = terminals(2.0,.8,4.3)[1].intersection(land).area
        self.assertAlmostEqual(nominal,4.7085)
        self.assertAlmostEqual(corner,3.1605)
        self.assertLess(corner,nominal)

    def test_terminal_gap_survives_maximum_depth(self):
        a,b=terminals(2.0,1.4,4.3)
        self.assertAlmostEqual(a.distance(b),2.0)

    def test_opposite_inductor_net_is_not_excluded(self):
        from shapely.geometry import box
        a,b=terminals(2.0,1.4,4.3)
        # An opposite-net trace under terminal A must be reported as a short.
        wrong=box(-2,-1,-1.5,1)
        areas,clearances=other_net_clearances(
            [{'net':'SW'},{'net':'OUT'}],[[a],[b]],
            {'SW':[a],'OUT':[b,wrong]},box(-10,-10,10,10))
        self.assertAlmostEqual(areas[0],1.0)
        self.assertEqual(clearances[0],0)
        self.assertEqual(areas[1],0)

    def test_masked_foreign_copper_is_not_exposed(self):
        from shapely.geometry import box
        a,b=terminals(2.0,1.4,4.3)
        areas,_=other_net_clearances(
            [{'net':'SW'},{'net':'OUT'}],[[a],[b]],
            {'SW':[a],'OUT':[b],'GND':[box(-2,-1,-1.5,1)]},
            box(1,-3,3,3))
        self.assertEqual(areas,[0,0])


if __name__=='__main__':
    unittest.main()
