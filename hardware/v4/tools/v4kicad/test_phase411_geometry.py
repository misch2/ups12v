"""Focused regression tests for the exported Phase 4.11 geometry screen."""
import unittest

from .phase411_analysis import _segment_distance as float_segment_distance
from .usb_review import _segment_distance as integer_segment_distance


class SegmentDistanceTests(unittest.TestCase):
    def test_disjoint_collinear_horizontal_segments(self):
        self.assertAlmostEqual(float_segment_distance((0, 0), (10, 0), (11, 0), (20, 0)), 1.0)
        scale = 1_000_000
        self.assertAlmostEqual(integer_segment_distance((0, 0), (10 * scale, 0),
                                                        (11 * scale, 0), (20 * scale, 0)), 1.0)

    def test_disjoint_collinear_vertical_segments(self):
        self.assertAlmostEqual(float_segment_distance((0, 0), (0, 10), (0, 11), (0, 20)), 1.0)
        scale = 1_000_000
        self.assertAlmostEqual(integer_segment_distance((0, 0), (0, 10 * scale),
                                                        (0, 11 * scale), (0, 20 * scale)), 1.0)

    def test_touching_and_crossing_segments_intersect(self):
        cases = [
            ((0, 0), (10, 0), (10, 0), (20, 0)),
            ((0, 0), (10, 0), (5, -5), (5, 5)),
            ((0, 0), (10, 0), (5, 0), (15, 0)),
        ]
        for a, b, c, d in cases:
            self.assertEqual(float_segment_distance(a, b, c, d), 0.0)
            scale = 1_000_000
            scaled = tuple(tuple(v * scale for v in p) for p in (a, b, c, d))
            self.assertEqual(integer_segment_distance(*scaled), 0.0)


if __name__ == '__main__':
    unittest.main()
