import unittest

from v4kicad.manufacturing_screen import mask_assumptions, trace_screen, via_pad_rows
from v4kicad.safety import ToolError


class ViaOpeningTests(unittest.TestCase):
    def model(self, x, mask=True):
        poly = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
        s = dict(pads={'p': dict(ref='U7', pin='2', net='PGND', polygons={'F.Cu': [poly]})},
                 vias={'v': dict(net='PGND', position=[x, 0], drill=.3, copper_widths={'F.Cu': .5})})
        m = dict(pads={'p': dict(padStack=dict(layers=['BL_F_Mask'] if mask else []))})
        return s, m

    def test_center_inside_open_pad(self):
        r = via_pad_rows(*self.model(0))[0]
        self.assertTrue(r['via_center_in_opening'])
        self.assertTrue(r['bore_intersects_opening'])

    def test_partial_bore_exposure_center_outside(self):
        r = via_pad_rows(*self.model(1.1))[0]
        self.assertFalse(r['via_center_in_opening'])
        self.assertTrue(r['bore_intersects_opening'])

    def test_nearby_annulus_not_open_bore(self):
        r = via_pad_rows(*self.model(1.5))[0]
        self.assertFalse(r['bore_intersects_opening'])
        self.assertAlmostEqual(r['annulus_edge_to_opening_mm'], .25)
        self.assertAlmostEqual(r['bore_edge_to_opening_mm'], .35)

    def test_outside_threshold(self):
        self.assertEqual(via_pad_rows(*self.model(1.7)), [])

    def test_no_mask_opening_no_exposure_inference(self):
        self.assertEqual(via_pad_rows(*self.model(0, mask=False)), [])

    def test_intentional_net_tie_artwork_is_not_foreign_net(self):
        snapshot = dict(tracks={'t': dict(uuid='t', net='PGND', layer='F.Cu', width=.1,
                                          start=[0, 0], end=[1, 0])}, vias={}, pads={})
        context = dict(snapshot=snapshot, copper_graphics=[dict(uuid='nt', ref='NT1', layer='F.Cu',
                         polygons=[[[-.1, -.1], [1.1, -.1], [1.1, .1], [-.1, .1]]])])
        r = trace_screen(context)
        self.assertEqual(r['trace_to_other_fixed_copper_below_010'], [])
        self.assertEqual(r['accepted_net_tie_artwork_separately_adjudicated'], {'nt': 'NT1'})

    def test_actual_foreign_trace_gap_still_fails(self):
        tracks = {n: dict(uuid=n, net=n, layer='F.Cu', width=.1, start=[0, y], end=[1, y])
                  for n, y in [('a', 0), ('b', .19)]}
        r = trace_screen(dict(snapshot=dict(tracks=tracks, vias={}, pads={}), copper_graphics=[]))
        self.assertEqual(len(r['trace_to_other_fixed_copper_below_010']), 1)
        self.assertAlmostEqual(r['trace_to_other_fixed_copper_below_010'][0]['gap_mm'], .09)

    def test_unknown_copper_artwork_cannot_be_excluded(self):
        context = dict(snapshot=dict(tracks={}, vias={}, pads={}),
                       copper_graphics=[dict(uuid='x', ref='OTHER', layer='F.Cu', polygons=[])])
        with self.assertRaises(ToolError):
            trace_screen(context)

    def test_nonzero_mask_expansion_requires_real_mask_export(self):
        with self.assertRaises(ToolError):
            mask_assumptions({}, dict(setup_metadata=[['pad_to_mask_clearance', '.05']]))
