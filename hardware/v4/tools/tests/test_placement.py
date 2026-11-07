"""Four-reference placement authorization and native hole-export regressions."""
import copy
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from v4kicad.geometry import verify_placement_geometry,polygons_with_holes
from v4kicad.safety import ToolError


class PlacementTests(unittest.TestCase):
    def test_scope_and_unrelated_geometry_fail_closed(self):
        old={s:{} for s in ['footprints','pads','tracks','vias','zones']}
        placements={ref:[1.,2.,-90.] for ref in ['L2','C37','C33','C45']}
        for ref in [*placements,'U3']:
            old['footprints'][ref]=dict(ref=ref,position=[0.,0.],angle=0.,value='fixed')
            old['pads'][ref]=dict(ref=ref,pin='1',net='PGND',position=[1.,0.],polygons={'F.Cu':[[[1.,0.]]]},drill_size=[0,0])
        new=copy.deepcopy(old)
        for ref in placements:
            new['footprints'][ref].update(position=[1.,2.],angle=-90.)
            new['pads'][ref].update(position=[1.,3.],polygons={'F.Cu':[[[1.,3.]]]})
        self.assertTrue(verify_placement_geometry(old,new,placements)['only_four_rigid_placements'])
        for section,key,field,value in [('pads','U3','position',[2,3]),('pads','L2','net','SYS'),
                                         ('footprints','U3','angle',90.),('pads','L2','polygons',{'F.Cu':[[[9,9]]]})]:
            bad=copy.deepcopy(new);bad[section][key][field]=value
            with self.assertRaises(ToolError):verify_placement_geometry(old,bad,placements)
        with self.assertRaises(ToolError):verify_placement_geometry(old,new,dict(placements,U3=[1,2,3]))
        bad=copy.deepcopy(new);bad['tracks']['new']={'net':'SW'}
        with self.assertRaises(ToolError):verify_placement_geometry(old,bad,placements)

    def test_native_holes_are_not_flattened(self):
        def chain(x):return SimpleNamespace(PointCount=lambda:1,CPoint=lambda j:SimpleNamespace(x=x,y=2000000))
        p=SimpleNamespace(OutlineCount=lambda:1,COutline=lambda i:chain(1000000),
                          HoleCount=lambda i:2,CHole=lambda i,j:chain(3000000+j*1000000))
        self.assertEqual(polygons_with_holes(p),[dict(outline=[[1.,2.]],holes=[[[3.,2.]],[[4.,2.]]])])

if __name__=='__main__':unittest.main()
