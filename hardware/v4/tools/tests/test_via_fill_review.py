import unittest

from v4kicad.safety import ToolError
from v4kicad.via_fill_review import classify


class ViaFillClassificationTests(unittest.TestCase):
    def fixture(self, bore=.5):
        via = dict(net='PGND', position=[1, 2], drill=bore, copper_widths={'F.Cu': 1, 'B.Cu': 1})
        pad = dict(ref='J7', pin='A1', net='PGND', position=[3, 4], drill_size=[.4, .4])
        native_via = dict(type='VT_THROUGH', position=dict(xNm='1000000', yNm='2000000'), padStack=dict(drill=dict(shape='DS_CIRCLE',
                          diameter=dict(xNm=str(round(bore*1e6)), yNm=str(round(bore*1e6))))))
        s = dict(vias={'v': via}, pads={'p': pad})
        m = dict(vias={'v': native_via}, pads={'p': dict(type='PT_PTH',
                 padStack=dict(drill=dict(diameter=dict(xNm='400000', yNm='400000'))))})
        return s, m, dict(via_pad_pairs=[])

    def test_boundary050_is_eligible_even_with_large_annulus(self):
        r = classify(*self.fixture())
        self.assertTrue(r['size_screen_pass'])
        self.assertEqual(len(r['holes_at_050']), 1)

    def test_over050_is_reported_not_silently_accepted(self):
        r = classify(*self.fixture(.500001))
        self.assertFalse(r['size_screen_pass'])
        self.assertEqual(len(r['holes_above_050']), 1)

    def test_same_diameter_component_pth_stays_open(self):
        r = classify(*self.fixture(.4))
        self.assertEqual(r['component_holes_keep_open'][0]['proposed_action'], 'KEEP_OPEN_NO_FILL_NO_CAP')
        self.assertEqual(r['via_inventory'][0]['proposed_action'], 'EPOXY_FILL_AND_COPPER_CAP')

    def test_exported_native_drill_disagreement_stops(self):
        s, m, x = self.fixture()
        s['vias']['v']['drill'] = .4
        with self.assertRaises(ToolError):
            classify(s, m, x)

    def test_unknown_exposure_uuid_stops(self):
        s, m, x = self.fixture()
        x['via_pad_pairs'] = [dict(via_uuid='missing', pad_uuid='p')]
        with self.assertRaises(ToolError):
            classify(s, m, x)

    def test_non_circular_via_not_assumed_supported(self):
        s, m, x = self.fixture()
        m['vias']['v']['padStack']['drill']['shape'] = 'DS_OBLONG'
        with self.assertRaises(ToolError):
            classify(s, m, x)

    def test_shifted_via_export_stops(self):
        s, m, x = self.fixture()
        s['vias']['v']['position'] = [1.1, 2]
        with self.assertRaises(ToolError):
            classify(s, m, x)

    def test_component_hole_diameter_drift_stops(self):
        s, m, x = self.fixture()
        s['pads']['p']['drill_size'] = [.3, .3]
        with self.assertRaises(ToolError):
            classify(s, m, x)
