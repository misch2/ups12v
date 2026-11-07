"""Phase4.18 exact-delta and complete SDK payload negative controls; no CAD I/O."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from v4kicad.safety import read_json,write_json,ToolError
from v4kicad.f5_migration import reconcile,via_templates,build_transaction,worker


class F5MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=read_json('hardware/v4/evidence/phase4-18-preparation/exact-migration-plan.json')
        cls.before=read_json(Path(cls.p['entry'])/'snapshot.json')
        cls.goal=read_json(Path(cls.p['goal'])/'snapshot.json')

    def test_complete_delta(self):
        self.assertTrue(reconcile(self.before,self.goal,self.p)['complete_delta_equal'])

    def test_missing_or_extra_copper_and_F0_edit_refused(self):
        for kind in ['missing','extra','F0','arc','J8','pad_net']:
            g=copy.deepcopy(self.goal)
            if kind=='missing':g['tracks'].pop(next(iter(self.p['operations']['tracks']['added'])))
            elif kind=='extra':g['vias']['rogue']=copy.deepcopy(next(iter(g['vias'].values())))
            elif kind=='F0':next(iter(g['tracks'].values()))['net']='WRONG'
            elif kind=='arc':next(v for v in g['tracks'].values() if v.get('geometry')=='arc')['width']+=.000001
            elif kind=='J8':next(v for v in g['footprints'].values() if v['ref']=='J8')['position'][0]+=.1
            else:next(v for v in g['pads'].values() if v['ref']=='U7' and v['pin']=='3')['net']='PGND'
            with self.assertRaises(ToolError):reconcile(self.before,g,self.p)

    def test_stopped_worker_never_connects(self):
        with tempfile.TemporaryDirectory() as d:
            write_json(Path(d)/'STOP.json',dict(reason='uncertain result'))
            with self.assertRaisesRegex(ToolError,'stopped'):worker(Path(d),'preflight','must-not-connect')

    def test_native_via_shape_drift_refused(self):
        raw=read_json(Path(self.p['entry'])/'routed-diagnostics.json')['items']
        goal=read_json(Path(self.p['goal'])/'routed-diagnostics.json')['items']
        uid=next(iter(self.p['operations']['vias']['added']))
        bad=copy.deepcopy(goal);bad[uid]['remove_unconnected']=not bad[uid]['remove_unconnected']
        with self.assertRaises(ToolError):via_templates(raw,bad,[uid])
        bad=copy.deepcopy(goal);bad[uid]['copper_widths']['In1.Cu']+=.1
        with self.assertRaises(ToolError):via_templates(raw,bad,[uid])

    def test_polygon_getter_only_used_on_native_polygon_type(self):
        from types import SimpleNamespace
        from v4kicad.geometry import native_polygon_artwork
        class Shape:
            def __init__(self,kind):self.kind=kind;self.m_Uuid=SimpleNamespace(AsString=lambda:'polygon')
            def GetShape(self):return self.kind
            def GetPolyShape(self):
                self_outer=self
                if self_outer.kind!=5:raise RuntimeError('Unsafe non-polygon getter')
                chain=SimpleNamespace(PointCount=lambda:1,CPoint=lambda i:SimpleNamespace(x=1000000,y=2000000))
                return SimpleNamespace(OutlineCount=lambda:1,COutline=lambda i:chain,HoleCount=lambda i:0)
        fp=SimpleNamespace(GetReference=lambda:'U7',GraphicalItems=lambda:[Shape(5),Shape(0),object()])
        result=native_polygon_artwork(SimpleNamespace(GetFootprints=lambda:[fp]),SimpleNamespace(PCB_SHAPE=Shape,SHAPE_T_POLY=5))
        self.assertEqual(result,{'U7':{'polygon':[{'outline':[[1.,2.]],'holes':[]}]}})

    def test_complete_SDK_rotation_and_copper_matches_native_goal(self):
        sys.path.insert(0,str(Path(self.p['production_board']).parent/'.konnect/native-ipc'))
        from kipy.board_types import Track,ArcTrack,Via,FootprintInstance,Net,BoardLayer
        from google.protobuf.json_format import ParseDict,MessageToDict
        source=read_json(self.p['accepted_production_manifest'])
        def objects(section,cls):
            result=[]
            for u,row in source[section].items():
                kind=ArcTrack if section=='tracks' and self.before['tracks'][u].get('geometry')=='arc' else cls
                message=type(kind().proto)();ParseDict(row,message);result.append(kind(message))
            return result
        class Board:
            def get_tracks(self):return objects('tracks',Track)
            def get_vias(self):return objects('vias',Via)
            def get_footprints(self):return objects('footprints',FootprintInstance)
            def get_nets(self):return [Net(name=n) for n in {v['net'] for v in F5MigrationTests.goal['tracks'].values()}]
            def get_layer_by_name(self,n):return BoardLayer.Value('BL_'+n.replace('.','_'))
        raw=read_json(Path(self.p['entry'])/'routed-diagnostics.json')['items']
        goal_raw=read_json(Path(self.p['goal'])/'routed-diagnostics.json')['items']
        templates=via_templates(raw,goal_raw,self.p['operations']['vias']['added'])
        updates,creates,expected=build_transaction(Board(),source,self.p,templates)
        self.assertEqual((len(updates),len(creates)),(18,147))
        for s in ['tracks','vias']:
            for uid in self.before[s]:self.assertEqual(source[s][uid],expected[s][uid])
        for uid,row in self.before['footprints'].items():
            if row['ref'] not in self.p['accepted_routing_plan']['placements']:
                self.assertEqual(source['footprints'][uid],expected['footprints'][uid])
        for item in creates:
            row=self.goal['vias' if isinstance(item,Via) else 'tracks'][item.id.value]
            self.assertEqual(item.net.name,row['net'])
            if isinstance(item,Via):
                self.assertEqual([item.position.x/1e6,item.position.y/1e6],row['position'])
                self.assertEqual(item.diameter,round(row['copper_widths']['F.Cu']*1e6))
                self.assertEqual(item.drill_diameter,round(row['drill']*1e6))
            else:
                self.assertEqual([item.start.x/1e6,item.start.y/1e6],row['start'])
                self.assertEqual([item.end.x/1e6,item.end.y/1e6],row['end'])
                self.assertEqual(item.width,round(row['width']*1e6))
        # All properties/models/graphics remain in complete SDK footprint payloads;
        # compare each graphical endpoint and field with the independent native target.
        audit=read_json(Path(self.p['goal'])/'native-audit.json')['footprint_graphics']
        point=lambda a:[int(a.get('xNm',0))/1e6,int(a.get('yNm',0))/1e6]
        for fp in updates:
            ref=fp.reference_field.text.value
            for field in [fp.reference_field,fp.value_field]:
                native=audit[ref][field.text.id.value]
                self.assertEqual(point(MessageToDict(field.text.position.proto)),native['GetPosition'])
                self.assertEqual(field.text.attributes.angle%360,native['text_angle']%360)
            for item in fp.definition.items:
                row=MessageToDict(item.proto)
                if 'shape' not in row:continue
                n=audit[ref][row['id']['value']];shape=row['shape']
                self.assertEqual(int(shape['attributes']['stroke']['width']['valueNm']),n['GetWidth'])
                if 'segment' in shape:
                    self.assertEqual(point(shape['segment']['start']),n['GetStart'])
                    self.assertEqual(point(shape['segment']['end']),n['GetEnd'])
                elif 'rectangle' in shape:
                    self.assertEqual(point(shape['rectangle']['topLeft']),n['GetStart'])
                    self.assertEqual(point(shape['rectangle']['bottomRight']),n['GetEnd'])
                elif 'polygon' in shape:
                    target=read_json(Path(self.p['goal'])/'polygon-artwork.json')[ref][row['id']['value']]
                    chain=lambda c:[point(v['point']) for v in c['nodes']]
                    actual=[dict(outline=chain(poly['outline']),holes=[chain(h) for h in poly.get('holes',[])])
                            for poly in shape['polygon']['polygons']]
                    self.assertEqual(actual,target)
                elif 'circle' in shape:
                    self.assertEqual(point(shape['circle']['center']),n['GetStart'])
                    self.assertEqual(point(shape['circle']['radiusPoint']),n['GetEnd'])
                else:self.fail('Unverified F5 graphic type: '+str(shape.keys()))


if __name__=='__main__':unittest.main()
