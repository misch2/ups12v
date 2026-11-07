"""Negative controls for the bounded Phase4.13 mapping; no native CAD I/O."""
import copy
import tempfile
from pathlib import Path
import unittest
from v4kicad.migration import (delta, validate_delta, RENAMES, semantic_capture,
                              worker, open_net_counts, verify_refilled_capture)
from v4kicad.safety import ToolError


class MigrationGuards(unittest.TestCase):
    def fixture(self):
        before=dict(footprints={},pads={},tracks={},vias={})
        for ref in ['C28','U2','R48']:
            before['footprints'][ref]=dict(ref=ref,position=[1,2],angle=0,value='same')
        before['footprints'].update({str(n):dict(ref=str(n),position=[0,0]) for n in range(151)})
        before['pads']={str(n):dict(ref='U1',net='PGND') for n in range(473)}
        before['tracks']={str(n):dict(geometry='arc') for n in range(8)}
        owner=copy.deepcopy(before)
        for ref in ['C28','U2','R48']:owner['footprints'][ref]['position']=[3,4]
        return before,owner

    def check(self,before,owner):
        return validate_delta({s:delta(before[s],owner[s]) for s in before},before,owner)

    def test_translation_only_scope(self):
        self.assertTrue(self.check(*self.fixture()))

    def test_reject_value_and_rotation_changes(self):
        for field,value in [('value','different'),('angle',90)]:
            a,b=self.fixture();b['footprints']['U2'][field]=value
            with self.assertRaises(ToolError):self.check(a,b)

    def test_reject_pad_loss(self):
        a,b=self.fixture();del b['pads']['0']
        with self.assertRaises(ToolError):self.check(a,b)

    def test_reject_resistor_bypass_net(self):
        a,b=self.fixture();a['pads']['0']['net']=next(iter(RENAMES));b['pads']['0']['net']='USB_DP'
        with self.assertRaises(ToolError):self.check(a,b)

    def test_reject_arc_flattening(self):
        a,b=self.fixture();b['tracks']['0']['geometry']='line'
        with self.assertRaises(ToolError):self.check(a,b)

    def test_complete_preimages(self):
        a={'keep':1,'remove':2,'modify':3};b={'keep':1,'add':4,'modify':5}
        self.assertEqual(delta(a,b),dict(added={'add':4},removed={'remove':2},
                         modified={'modify':dict(before=3,after=5)}))

    def test_only_exact_footprint_item_reordering_is_equivalent(self):
        a={'fp':{'definition':{'items':[{'id':'a','x':1},{'id':'b','x':2}]}}}
        b=copy.deepcopy(a);b['fp']['definition']['items'].reverse()
        self.assertEqual(semantic_capture(a),semantic_capture(b))
        b['fp']['definition']['items'][0]['x']=3
        self.assertNotEqual(semantic_capture(a),semantic_capture(b))

    def test_preservation_stop_refuses_before_any_ipc_or_context_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'ipc-preservation.json').write_text('{"exact_equal": false}')
            # No migration context or KiCad SDK is provided: the stop must
            # trigger before either could be used.
            with self.assertRaisesRegex(ToolError,'STOPPED'):
                worker(root,'observe','unusable-must-not-connect')

    def test_ratsnest_representative_uses_native_net_and_rejects_wrong_net(self):
        native=dict(pads={'p':{'net':'~INT'},'q':{'net':'~INT'}},tracks={'t':{'net':'~INT'}},vias={})
        make=lambda uid:{'unconnected_items':[{'items':[{'uuid':'p'},{'uuid':uid}]}]}
        self.assertEqual(open_net_counts(make('q'),native),open_net_counts(make('t'),native))
        native['tracks']['t']['net']='PGND'
        with self.assertRaises(ToolError):open_net_counts(make('t'),native)

    def test_refill_requires_exact_native_target_and_unchanged_zone_definition(self):
        zone=lambda x:{'name':'PGND','filledPolygons':[{'layer':'BL_In1_Cu','shapes':{'polygons':[
            {'outline':{'nodes':[{'point':{'xNm':str(x),'yNm':'0'}}]}}]}}]}
        before={'zones':{'z':zone(1)},'pads':{'p':{'net':'PGND'}}}
        after=copy.deepcopy(before);after['zones']['z']=zone(2)
        layout={'fills':{'z':{'layers':{'In1.Cu':[{'outline':[[.000002,0]],'holes':[]}]}}}}
        self.assertTrue(verify_refilled_capture(before,after,layout)['live_fill_exact_independent_native'])
        before['zones']['rf']={'name':'RF','filledPolygons':[{'layer':'BL_F_Cu','shapes':{}}]}
        after['zones']['rf']=copy.deepcopy(before['zones']['rf'])
        self.assertTrue(verify_refilled_capture(before,after,layout)['live_fill_exact_independent_native'])
        bad=copy.deepcopy(after);bad['zones']['z']=zone(3)
        with self.assertRaises(ToolError):verify_refilled_capture(before,bad,layout)
        bad=copy.deepcopy(after);bad['zones']['z']['name']='different'
        with self.assertRaises(ToolError):verify_refilled_capture(before,bad,layout)
        bad=copy.deepcopy(after);bad['pads']['p']['net']='different'
        with self.assertRaises(ToolError):verify_refilled_capture(before,bad,layout)


if __name__=='__main__':unittest.main()
