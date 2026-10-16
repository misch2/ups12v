"""Feasibility screen regression: all-layer holes and off-region geometry."""
import copy
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from v4kicad.route_plan import plan_routes
from v4kicad.safety import ToolError


def fixture():
    pads={}
    for ref,x in [('A',.4),('B',2.6)]:
        pads[ref]=dict(ref=ref,pin='1',net='N',position=[x,1.],drill_size=[0,0],
                      polygons={'F.Cu':[[[x-.15,.85],[x+.15,.85],[x+.15,1.15],[x-.15,1.15]]]})
    return dict(pads=pads,tracks={'barrier':dict(net='X',layer='F.Cu',width=.2,start=[1.5,-1],end=[1.5,3]),
                                 'outside':dict(net='X',layer='F.Cu',width=1,start=[-20,-20],end=[-10,-10])},vias={})


class PlannerTests(unittest.TestCase):
    def test_duplicate_physical_pad_numbers_all_remain_obstacles(self):
        g = fixture()
        g['tracks'] = {}
        for key,x in [('shield1',1.5),('shield2',10.)]:
            g['pads'][key] = dict(ref='J',pin='SH',net='G',position=[x,1.],drill_size=[0,0],
                polygons={'F.Cu':[[[x-.2,.7],[x+.2,.7],[x+.2,1.3],[x-.2,1.3]]]})
        p = plan_routes(g, [['N','A','1','B','1']], [0,0,3,2], .15,step=.1)
        # Neither shield pad may be lost when selecting endpoint references.
        self.assertGreater(p['metrics'][0]['length_mm'], 2.3)

    def test_existing_bottom_endpoint_needs_no_spurious_source_via(self):
        g = fixture()
        g['tracks'] = {}
        p = plan_routes(g, [['N','A','1','B','1']], [0,0,3,2], .15,
                        step=.1, source_layer='B.Cu', target_layer='B.Cu')
        self.assertEqual(p['vias'], [])
        self.assertTrue(all(t[1] == 'B.Cu' for t in p['tracks']))

    def test_layer_transition_avoids_barrier_and_outside_geometry(self):
        p=plan_routes(fixture(),[['N','A','1','B','1']],[0,0,3,2],.15,step=.1)
        self.assertEqual(len(p['vias']),2)
        self.assertTrue(any(t[1]=='B.Cu' for t in p['tracks']))
        self.assertTrue(all(0<=v[1]<=3 and 0<=v[2]<=2 for v in p['vias']))

    def test_inner_power_copper_blocks_otherwise_legal_through_vias(self):
        g=fixture()
        g['tracks']['inner']=dict(net='POWER',layer='In2.Cu',width=5,start=[0,0],end=[3,2])
        with self.assertRaises(ToolError):
            plan_routes(g,[['N','A','1','B','1']],[0,0,3,2],.15,step=.1)

    def test_net_mismatch_stops_before_planning(self):
        with self.assertRaises(ToolError):
            plan_routes(fixture(),[['WRONG','A','1','B','1']],[0,0,3,2],.15,step=.1)
