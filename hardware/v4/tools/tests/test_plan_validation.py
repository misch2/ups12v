"""No native KiCad required: exact scratch5 failures and valid physical junctions."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from v4kicad.plan_validation import check_plan,drill,separation,shape
from v4kicad.safety import digest


def fixture():
    g=dict(tracks={},vias={},pads={})
    c=dict(profile=dict(copper_clearance=.1,hole_clearance=.25,hole_to_hole=.25,
        edge_clearance=1.,min_via_diameter=.5,min_drill=.3,min_annular=.1,min_track_width=0),
        pads={},copper_graphics=[],zones={},reservations=[],board_outline=[])
    return g,c


def plan(tracks=(),vias=()):return dict(failure=None,tracks=list(tracks),vias=list(vias))


class PlanValidationTests(unittest.TestCase):
    def test_existing_same_net_path_cannot_be_reemitted_at_another_width(self):
        g,c=fixture()
        g['tracks']['old']=dict(net='N',layer='F.Cu',width=.5,start=[0,0],end=[1,1])
        result=check_plan(g,plan([['N','F.Cu',.6,1,1,0,0]]),c)
        self.assertTrue(result['valid'])
        warning=result['warnings'][0]
        self.assertEqual(warning['type'],'duplicate_track')
        self.assertEqual(warning['existing_count'],1)

    def test_duplicate_path_at_different_width_is_flagged(self):
        g,c=fixture()
        result=check_plan(g,plan([['N','F.Cu',.5,0,0,1,1],
            ['N','F.Cu',.6,1,1,0,0]]),c)
        self.assertTrue(result['valid'])
        self.assertEqual([w['type'] for w in result['warnings']],['duplicate_track'])

    def test_producer_does_not_reemit_existing_or_reversed_track_objects(self):
        from v4kicad.f0_plan import incremental_tracks
        g,c=fixture();g['tracks']['old']=dict(net='N',layer='F.Cu',width=.2,start=[0,0],end=[1,0])
        p=plan([['N','F.Cu',.2,1,0,0,0],['N','F.Cu',.2,1,0,2,0],['N','F.Cu',.2,2,0,1,0]])
        q=incremental_tracks(g,p)
        self.assertEqual(q['reused_track_objects'],2)
        self.assertEqual(q['tracks'],[['N','F.Cu',.2,1,0,2,0]])

    def test_oversized_plane_request_fails_before_mutation_instead_of_bypassing_guard(self):
        from v4kicad.safety import ToolError
        g,c=fixture();p=plan([['N','F.Cu',.2,0,0,1,0]])
        p['review_bounds']=[31,69,123,99]
        with self.assertRaises(ToolError):check_plan(g,p,c)

    def test_native_unit_equality_preserves_single_nanometre_and_net_differences(self):
        from v4kicad.plan_validation import route_key
        a=['PGND','F.Cu',.4,42.12,96,47.879999999999995,96]
        b=['PGND','F.Cu',.4,42.12,96,47.88,96]
        self.assertEqual(route_key(a,'track'),route_key(b,'track'))
        c=b.copy();c[5]=47.880001
        self.assertNotEqual(route_key(a,'track'),route_key(c,'track'))
        c=b.copy();c[0]='USB_DP'
        self.assertNotEqual(route_key(a,'track'),route_key(c,'track'))
        self.assertNotEqual(route_key(['PGND',1,2,.5,.3],'via'),route_key(['PGND',1,2,.500001,.3],'via'))

    def test_invalid_bound_plan_never_reaches_scratch_preparation_or_native(self):
        import tempfile,io,contextlib
        from v4kicad import cli
        from v4kicad.safety import write_json
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);board=root/'fixture.kicad_pcb'
            for ext in ['.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_dru']:
                board.with_suffix(ext).write_bytes(b'unit-test fixture; never loaded as CAD')
            g,c=fixture();c.update(snapshot=g,board_sha256=digest(board))
            c['profile'].update(project_sha256=digest(board.with_suffix('.kicad_pro')),
                rules_sha256=digest(board.with_suffix('.kicad_dru')))
            write_json(root/'context.json',c);write_json(root/'plan.json',
                plan([['S','B.Cu',.18,0,0,2,0]],[['PGND',1,.1,.5,.3]]))
            args=['validate','--board',str(board),'--baseline-manifest',str(root/'unused.json'),
                '--output-dir',str(root/'fresh'),'--native-python',sys.executable,
                '--kicad-cli',sys.executable,'--plan',str(root/'plan.json'),
                '--validation-context',str(root/'context.json'),'--add-only']
            with mock.patch.object(cli,'native') as native,mock.patch.object(cli,'prepare_scratch') as prepare,contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(cli.main(args),2)
                native.assert_not_called();prepare.assert_not_called()

    def test_micro_cleanup_removes_only_pad_internal_redundancy(self):
        from v4kicad.plan_validation import clean_microlegs
        g,c=fixture();g['pads']['p']=dict(uuid='p',net='N',position=[0,0],
            polygons={'F.Cu':[[[-.3,-.3],[.3,-.3],[.3,.3],[-.3,.3]]]},drill_size=[0,0])
        c['snapshot']=g;p=plan([['N','F.Cu',.2,0,0,.1,0],['N','F.Cu',.2,.1,0,1,0]])
        cleaned,actions=clean_microlegs(p,c)
        self.assertEqual(len(cleaned['tracks']),1)
        self.assertEqual(len(p['tracks']),2)
        self.assertEqual(actions[0]['pad'],'p')

    def test_large_review_domain_is_covered_by_guard_compliant_tiles(self):
        from v4kicad.plan_validation import review_regions
        p=plan([['N','F.Cu',.2,32,40,122,98]])
        regions=review_regions(p)
        self.assertTrue(all(0<r[2]-r[0]<=30 and 0<r[3]-r[1]<=30 for r in regions))
        self.assertEqual(min(r[0] for r in regions),31)
        self.assertEqual(max(r[2] for r in regions),123)
        self.assertAlmostEqual(sum((r[2]-r[0])*(r[3]-r[1]) for r in regions),92*60)

    def test_exact_three_scratch5_pgnd_collisions_before_native(self):
        p=Path(__file__).resolve().parents[2]/'evidence/phase4-9-usb-plan-v5.json'
        self.assertEqual(digest(p),'d8ce75bdb4fef153d48e843be9685c421713e64dce7ff35f12c1a39f95a1aacd')
        invalid=json.loads(p.read_text());g,c=fixture()
        with mock.patch('subprocess.Popen',side_effect=AssertionError('Native launch forbidden')):
            result=check_plan(g,invalid,c)
        self.assertFalse(result['valid'])
        failures=[e for e in result['errors'] if e['type']=='copper_clearance']
        self.assertTrue(all(any(e['object']=='via:'+str(i) and e['other_net']==net for e in failures)
            for i,net in [(13,'USB_DP'),(14,'USB_DN'),(15,'Net-(U1-USB_D-_{slash}_GPIO18)')]))
        # Each demonstrated overlap must independently fail as well.
        for i,net in [(13,'USB_DP'),(14,'USB_DN'),(15,'Net-(U1-USB_D-_{slash}_GPIO18)')]:
            subset=plan([t for t in invalid['tracks'] if t[0]==net],[invalid['vias'][i]])
            self.assertFalse(check_plan(g,subset,c)['valid'])

    def test_joint_check_is_independent_of_producer_order(self):
        g,c=fixture();p=plan([['S','B.Cu',.18,0,0,2,0]],[['PGND',1,.1,.5,.3]])
        self.assertFalse(check_plan(g,p,c)['valid'])
        g['tracks']['old']=dict(net='S',layer='B.Cu',width=.18,start=[0,0],end=[2,0])
        self.assertFalse(check_plan(g,plan(vias=p['vias']),c)['valid'])

    def test_distinct_layer_crossings_and_clear_through_via_are_valid(self):
        g,c=fixture()
        p=plan([['A','F.Cu',.2,0,0,4,0],['B','B.Cu',.2,2,-2,2,2]], [['A',.5,0,.5,.3]])
        self.assertTrue(check_plan(g,p,c)['valid'])
        # A through via occupies B.Cu too; layer labels must not hide a collision.
        p['vias'][0][1]=2
        self.assertFalse(check_plan(g,p,c)['valid'])

    def test_legal_same_net_junction_and_pgnd_stitching(self):
        g,c=fixture();g['tracks']['a']=dict(net='PGND',layer='F.Cu',width=.4,start=[0,0],end=[3,0])
        p=plan([['PGND','F.Cu',.3,1,0,1,1]],[['PGND',1,1,.6,.3]])
        self.assertTrue(check_plan(g,p,c)['valid'])
        g['tracks']['other']=dict(net='S',layer='In2.Cu',width=.2,start=[0,3],end=[3,3])
        self.assertTrue(check_plan(g,p,c)['valid'])

    def test_same_net_holes_still_need_hole_to_hole_clearance(self):
        g,c=fixture();g['vias']['v']=dict(net='PGND',position=[0,0],drill=.3,copper_widths={l:.5 for l in ['F.Cu','In1.Cu','In2.Cu','B.Cu']})
        r=check_plan(g,plan(vias=[['PGND',.4,0,.5,.3]]),c)
        self.assertTrue(any(e['type']=='hole_to_hole' for e in r['errors']))

    def test_pad_clearance_and_reserved_regions(self):
        g,c=fixture();g['pads']['p']=dict(net='N',position=[0,0],polygons={'F.Cu':[[[-.5,-.5],[.5,-.5],[.5,.5],[-.5,.5]]]},drill_size=[0,0])
        self.assertFalse(check_plan(g,plan([['S','F.Cu',.2,-1,.65,1,.65]]),dict(c,pads={'p':dict(clearances={'F.Cu':.2})}))['valid'])
        c['reservations']=[dict(name='RF',layers=['F.Cu'],polygon=[[2,-1],[3,-1],[3,1],[2,1]])]
        self.assertFalse(check_plan(g,plan([['N','F.Cu',.2,0,0,4,0]]),c)['valid'])

    def test_rotated_oblong_drill_uses_actual_capsule(self):
        h=drill('h','', [0,0],[2,.5],90)
        near=shape('t','S','B.Cu',[[-1,.8],[1,.8]],.1)
        far=shape('t','S','B.Cu',[[-1,1.6],[1,1.6]],.1)
        self.assertLess(separation(h,near),0)
        self.assertGreater(separation(h,far),.25)

    def test_duplicate_same_net_tracks_are_flagged_not_false_shorts(self):
        g,c=fixture();t=['N','F.Cu',.2,0,0,1,0]
        r=check_plan(g,plan([t,t]),c)
        self.assertTrue(r['valid'])
        self.assertTrue(any(w['type']=='duplicate_track' for w in r['warnings']))


if __name__=='__main__':unittest.main()
