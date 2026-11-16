"""Physical hole/net/layer and real fill preservation regression coverage."""
import copy
import unittest
from v4kicad.j7_dfm_review import selected_screen, physical_fill_equal


class J7ScreenTests(unittest.TestCase):
    def context(self):
        track=dict(net='CC2',kind='track',layer='In2.Cu',width=.18,
                   start=[119.86,76.11],end=[119.86,78.605])
        pad=dict(ref='J7',pin='S',net='PGND',position=[118.37,76.675],
                 drill_size=[.6,2.1],polygons={'In2.Cu':[
                     [[117.17,76.225],[119.57,76.225],[119.57,77.125],[117.17,77.125]]]})
        return dict(snapshot=dict(tracks={'t':track},vias={},pads={'shell':pad}),
                    pads={'shell':dict(orientation=90)})

    def test_rotated_slot_is_physical_capsule_not_copper_or_drill_bbox(self):
        c=self.context(); result=selected_screen(c,{'t'},'shell')
        self.assertAlmostEqual(result['shell_min_gap_mm'],.35)
        c['snapshot']['tracks']['t']['start'][0]=119.8
        c['snapshot']['tracks']['t']['end'][0]=119.8
        self.assertAlmostEqual(selected_screen(c,{'t'},'shell')['shell_min_gap_mm'],.29)

    def test_same_net_join_does_not_hide_different_net_drill_on_other_layer(self):
        c=self.context(); c['snapshot']['vias']={
            'join':dict(net='CC2',position=[119.86,78.605],drill=.4,copper_widths={'In2.Cu':.6}),
            'other':dict(net='VBUS',position=[120.3,77],drill=.3,copper_widths={'F.Cu':.6})}
        row=selected_screen(c,{'t'},'shell')['selected'][0]
        self.assertLess(row['physical_drill']['gap_mm'],0)
        self.assertEqual(row['different_net_drill']['uuid'],'other')
        self.assertAlmostEqual(row['different_net_drill']['gap_mm'],.2)

    def test_actual_fill_hole_change_is_rejected(self):
        a=dict(fills={'z':dict(net='PGND',layers={'In1.Cu':[
            dict(outline=[[0,0],[2,0],[2,2]],holes=[[[.2,.2],[.3,.2],[.3,.3]]])]})})
        b=copy.deepcopy(a)
        self.assertTrue(physical_fill_equal(a,b))
        b['fills']['z']['layers']['In1.Cu'][0]['holes'][0][0][0]+=.001
        self.assertFalse(physical_fill_equal(a,b))


if __name__=='__main__':unittest.main()
