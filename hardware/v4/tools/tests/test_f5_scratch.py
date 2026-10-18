"""F5 authorization, rigid geometry and negative preservation controls."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from v4kicad.f5_scratch import transformed, compare_placed, scope, BASELINE
from v4kicad.safety import ToolError


class F5Tests(unittest.TestCase):
    def fixture(self):
        g = {s: {} for s in ['footprints', 'pads', 'tracks', 'vias', 'zones']}
        for ref in ['U7', 'U3']:
            g['footprints'][ref] = dict(ref=ref, position=[0., 0.], angle=0., value='fixed')
            g['pads'][ref] = dict(ref=ref, pin='1', net='PGND', position=[1., 0.],
                                 polygons={'F.Cu': [[[1., 0.], [1., 1.], [0., 1.]]]}, drill_size=[0, 0])
        return g

    def test_exact_quarter_turn_and_metadata(self):
        g = self.fixture(); p = {'U7': [10., 20., 90.]}
        a = transformed(g, p)
        self.assertEqual(a['pads']['U7']['position'], [10., 19.])
        self.assertEqual(a['pads']['U3'], g['pads']['U3'])
        self.assertTrue(compare_placed(g, a, p)['F0_exact'])
        for section, uid, key, value in [('pads', 'U3', 'net', 'SYS'),
                 ('pads', 'U7', 'net', 'SYS'), ('footprints', 'U3', 'angle', 90.)]:
            bad = copy.deepcopy(a); bad[section][uid][key] = value
            with self.assertRaises(ToolError): compare_placed(g, bad, p)
        bad = copy.deepcopy(a); bad['tracks']['rogue'] = {'net': 'SYS'}
        with self.assertRaises(ToolError): compare_placed(g, bad, p)
        bad = copy.deepcopy(a); bad['pads']['U7']['polygons']['F.Cu'][0][0][0] += .000001
        with self.assertRaises(ToolError): compare_placed(g, bad, p)

    def test_no_F0_or_probe_move(self):
        for ref in ['U3', 'TP17']:
            with self.assertRaises(ToolError): transformed(self.fixture(), {ref: [1, 2, 0]})

    def test_scope_fails_closed(self):
        c = dict(board_sha256=BASELINE, snapshot=self.fixture(), reservations=[], pads={})
        p = dict(baseline_sha256=BASELINE, mode='F5-scratch-only', failure=None,
                 tracks=[], vias=[], placements={})
        self.assertEqual(scope(c, p)[0], c['snapshot'])
        for change in [dict(baseline_sha256='wrong'), dict(mode='production'),
                       dict(remove_tracks={'u': {}}), dict(tracks=[['USB_DP', 'F.Cu', .2, 0, 0, 1, 1]]),
                       dict(tracks=[['SYS', 'In1.Cu', 1., 0, 0, 1, 1]])]:
            with self.assertRaises(ToolError): scope(c, dict(p, **change))

    def test_review_resistance_and_unproven_leg(self):
        from v4kicad.f5_review import path_metrics
        p=dict(tracks=[['SYS','F.Cu',1.,0.,0.,10.,0.]])
        r=path_metrics(p,'SYS',[[0.,0.],[10.,0.]])
        self.assertAlmostEqual(r['R20_ohm'],.004925714285714286)
        with self.assertRaises(ToolError):path_metrics(p,'SYS',[[0.,0.],[10.,1.]])

    def test_actual_fill_holes_are_not_ground(self):
        from v4kicad.f5_review import plane_window
        p=dict(outline=[[0.,0.],[2.,0.],[2.,2.],[0.,2.]],
               holes=[[[.5,.5],[1.5,.5],[1.5,1.5],[.5,1.5]]])
        l=dict(fills={'z':dict(net='PGND',layers={'In1.Cu':[p]})})
        r=plane_window(l,[.25,.25,1.75,1.75],.25)
        self.assertEqual(r['rows'][3][3],'0')
        self.assertEqual(r['rows'][0][0],'1')

    def test_full_footprint_proof_preserves_properties_and_local_geometry(self):
        from v4kicad.f5_review import normalized_footprint
        a=['footprint','SOT', ['at','1','2','90'],
           ['property','MPN','exact'], ['pad','1',['at','-.74','0','90']]]
        b=copy.deepcopy(a);b[2]=['at','10','20','180'];b[4][2][3]='180'
        self.assertEqual(normalized_footprint(a),normalized_footprint(b))
        bad=copy.deepcopy(b);bad[3][2]='wrong'
        self.assertNotEqual(normalized_footprint(a),normalized_footprint(bad))
        bad=copy.deepcopy(b);bad[4][1]='2'
        self.assertNotEqual(normalized_footprint(a),normalized_footprint(bad))
        bad=copy.deepcopy(b);bad[4][2][1]='-.75'
        self.assertNotEqual(normalized_footprint(a),normalized_footprint(bad))
        a.extend([['fp_line',['start','0','1'],['uuid','a']],['fp_line',['start','1','0'],['uuid','b']]])
        b.extend([copy.deepcopy(a[-1]),copy.deepcopy(a[-2])])
        self.assertEqual(normalized_footprint(a),normalized_footprint(b))
        b[-1][2][1]='wrong-uuid'
        self.assertNotEqual(normalized_footprint(a),normalized_footprint(b))


if __name__ == '__main__': unittest.main()
