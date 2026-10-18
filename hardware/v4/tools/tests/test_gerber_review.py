"""Offline independent CAM checks; no native KiCad or production writes."""
import math
from types import SimpleNamespace
import unittest

from v4kicad.gerber_review import compose, difference, drill_key, match_holes, native_hole_key, primitive_shape


class CamReviewTests(unittest.TestCase):
    def test_decimal_excellon_quantization_is_bounded(self):
        from collections import Counter
        key=(.3,(35.6,65.9625),(35.6,65.9625))
        rows=[dict(uuid='via',kind='VIA',key=key)]
        actual={'PTH':Counter({(.3,(35.6,65.962),(35.6,65.962)):1})}
        self.assertTrue(match_holes(rows,actual)['PTH']['pass_geometry'])
        actual={'PTH':Counter({(.3,(35.6,65.961),(35.6,65.961)):1})}
        self.assertFalse(match_holes(rows,actual)['PTH']['pass_geometry'])

    def test_wrong_drill_diameter_never_quantized(self):
        from collections import Counter
        rows=[dict(uuid='via',kind='VIA',key=(.3,(1,2),(1,2)))]
        actual={'PTH':Counter({(.4,(1,2),(1,2)):1})}
        self.assertFalse(match_holes(rows,actual)['PTH']['pass_geometry'])

    def test_round_drill_registration_and_size(self):
        Flash = type('Flash', (), {})
        o = Flash()
        o.x, o.y, o.aperture = 92.456, -91.4, SimpleNamespace(diameter=.5)
        self.assertEqual(drill_key(o), (.5, (92.456,91.4), (92.456,91.4)))
        o.x += .01
        self.assertNotEqual(drill_key(o), (.5, (92.456,91.4), (92.456,91.4)))

    def test_oval_slot_rotation_and_endpoints(self):
        Line = type('Line', (), {})
        o = Line()
        o.x1, o.y1, o.x2, o.y2 = 42.925, -33.2, 43.075, -33.2
        o.aperture = SimpleNamespace(diameter=1.6)
        p = dict(position=[43,33.2], drill_size=[1.6,1.75])
        self.assertEqual(drill_key(o), native_hole_key(p,90))
        self.assertNotEqual(drill_key(o), native_hole_key(p,0))

    def test_missing_copper_and_mask_are_failures(self):
        from shapely.geometry import box
        a=box(0,0,1,1)
        self.assertTrue(difference(a,a)['pass_geometry'])
        self.assertFalse(difference(a,box(0,0,.9,1))['pass_geometry'])
        self.assertFalse(difference(a,box(0,0,1.1,1))['pass_geometry'])

    def test_rotated_rectangle_is_not_bounding_box(self):
        Rectangle = type('Rectangle', (), {})
        p=Rectangle()
        p.x, p.y, p.w, p.h, p.rotation = 3,-4,2,1,math.pi/4
        shape=primitive_shape(p)
        self.assertAlmostEqual(shape.area,2)
        self.assertAlmostEqual(shape.centroid.x,3)
        self.assertAlmostEqual(shape.centroid.y,4)

    def test_unknown_primitive_refused(self):
        with self.assertRaises(ValueError):
            primitive_shape(SimpleNamespace())

    def test_legend_arc_width_equals_diameter(self):
        from gerbonara.graphic_primitives import Arc
        # The stock arc-outline approximation divides by zero at the inner radius.
        a=Arc(38.621,-44,38.421,-44,38.521,-44,True,.2)
        shape=primitive_shape(a)
        self.assertTrue(shape.is_valid)
        self.assertAlmostEqual(shape.area, math.pi*.1*.1 + math.pi*.1*.2, places=5)

    def test_clear_polarity_removes_copper(self):
        from gerbonara.graphic_primitives import Circle
        a=SimpleNamespace(to_primitives=lambda:iter([Circle(0,0,1,polarity_dark=True)]))
        b=SimpleNamespace(to_primitives=lambda:iter([Circle(0,0,.5,polarity_dark=False)]))
        result=compose(SimpleNamespace(objects=[a,b]))
        from shapely.geometry import Point
        self.assertFalse(result.contains(Point(0,0)))
        self.assertAlmostEqual(result.area, math.pi*.75, places=5)


if __name__=='__main__':
    unittest.main()
