import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from v4kicad.u3_review import area,route_path,plane_path


class ReviewTests(unittest.TestCase):
    def test_loop_area_and_route_graph(self):
        self.assertEqual(area([[0,0],[2,0],[2,1],[0,1]]),2)
        p={'tracks':[['N','F.Cu',.5,0,0,1,0],['N','F.Cu',.5,1,0,1,1],['OTHER','F.Cu',.5,0,0,1,1]]}
        self.assertEqual(route_path(p,'N',[0,0],[1,1])['length_mm'],2)
        with self.assertRaises(ValueError):route_path(p,'N',[0,0],[2,2])

    def test_plane_path_respects_native_clearance_and_drill(self):
        layout={'plane_samples':{'bounds':[0,0,1,1],'step':.1,'rows':['1'*11]*11}}
        g={'vias':{'hole':{'position':[.5,.5],'drill':.3}},'pads':{}}
        result=plane_path(g,layout,[.1,.5],[.9,.5])
        self.assertGreater(result['length_mm'],.8)
        self.assertTrue(all((x-.5)**2+(y-.5)**2>(.15+.015)**2 for x,y in result['path']))
        layout['plane_samples']['rows']=['11111011111']*11
        with self.assertRaises(ValueError):plane_path(g,layout,[.1,.5],[.9,.5])

if __name__=='__main__':unittest.main()
