"""Exact approved delta and native transaction negative controls; no CAD I/O."""
from pathlib import Path
import copy
import sys
import tempfile
import unittest
from v4kicad.safety import read_json, write_json, ToolError
from v4kicad.j7_migration import (reconcile, build_transaction, worker, OLD, NEW,
                                GOAL, MANIFEST, PRODUCTION, resolve_endpoint, capture_equal)


class J7MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=read_json(GOAL/'before.json')
        cls.after=read_json(GOAL/'final-snapshot.json')

    def test_exact_approved_delta(self):
        ops=reconcile(self.before,self.after)
        self.assertEqual(set(ops['tracks']['removed']),set(OLD))
        self.assertEqual(set(ops['tracks']['added']),set(NEW))

    def test_out_of_scope_delta_and_wrong_geometry_refused(self):
        for kind in ['width','endpoint','corner','layer','net','uuid','arc','via','footprint','pad','zone','extra']:
            g=copy.deepcopy(self.after);t=g['tracks'][NEW[1]]
            if kind=='width':t['width']+=.001
            elif kind=='endpoint':g['tracks'][NEW[0]]['start'][0]+=.001
            elif kind=='corner':t['end'][1]+=.001
            elif kind=='layer':t['layer']='F.Cu'
            elif kind=='net':t['net']='USB_CC1'
            elif kind=='uuid':g['tracks']['rogue']=g['tracks'].pop(NEW[1])
            elif kind=='arc':next(r for r in g['tracks'].values() if r.get('geometry')=='arc')['width']+=.001
            elif kind=='via':next(iter(g['vias'].values()))['drill']+=.001
            elif kind=='footprint':next(iter(g['footprints'].values()))['position'][0]+=.001
            elif kind=='pad':next(iter(g['pads'].values()))['net']='WRONG'
            elif kind=='zone':g['zones']['rogue']={}
            else:g['tracks']['rogue']=copy.deepcopy(t)
            with self.subTest(kind=kind),self.assertRaises(ToolError):reconcile(self.before,g)

    def test_stopped_context_never_connects(self):
        with tempfile.TemporaryDirectory() as d:
            write_json(Path(d)/'STOP.json',dict(reason='uncertain native result'))
            with self.assertRaisesRegex(ToolError,'stopped'):worker(d,'preflight','must-not-connect')

    def test_endpoint_selected_from_current_OS_evidence(self):
        row=dict(processes=[dict(ProcessId=42,Name='pcbnew.exe',CommandLine='pcbnew.exe "'+str(PRODUCTION.resolve())+'"')],
                 pipes=[r'.tmp\kicad\api.sock'])
        self.assertEqual(resolve_endpoint(row,PRODUCTION,42,'auto'),r'ipc://.tmp\kicad\api.sock')
        self.assertEqual(resolve_endpoint(row,PRODUCTION,42,'ipc://.tmp/kicad/api.sock'),r'ipc://.tmp\kicad\api.sock')
        with self.assertRaisesRegex(ToolError,'no IPC attempted'):
            resolve_endpoint(row,PRODUCTION,42,r'ipc://C:\Users\Michal\AppData\Local\Temp\kicad\api.sock')
        for kind in ['pid','document','extra_process','missing_pipe','extra_pipe']:
            bad=copy.deepcopy(row)
            if kind=='pid':bad['processes'][0]['ProcessId']=99
            elif kind=='document':bad['processes'][0]['CommandLine']='pcbnew.exe "wrong-board.kicad_pcb"'
            elif kind=='extra_process':bad['processes'].append(copy.deepcopy(row['processes'][0]))
            elif kind=='missing_pipe':bad['pipes']=[]
            else:bad['pipes'].append(r'C:\Temp\kicad\api.sock')
            with self.subTest(kind=kind),self.assertRaises(ToolError):resolve_endpoint(bad,PRODUCTION,42,'auto')

    def test_runtime_board_parent_does_not_mask_geometry_changes(self):
        expected=dict(tracks={'new':dict(start=dict(xNm='119860000',yNm='76110000'),width='180000')})
        actual=copy.deepcopy(expected);actual['tracks']['new']['parent']=dict(value='runtime-board-uuid')
        self.assertTrue(capture_equal(expected,actual))
        actual['tracks']['new']['width']='181000'
        self.assertFalse(capture_equal(expected,actual))
        actual=copy.deepcopy(expected);actual['tracks']['new']['start']['parent']='unexpected-child-field'
        self.assertFalse(capture_equal(expected,actual))

    def test_stopped_rehearsal_has_only_runtime_parent_difference(self):
        root=Path('hardware/v4/evidence/phase4-21-editor-rehearsal-v2')
        expected=read_json(root/'ipc-expected.json');actual=read_json(root/'ipc-after.json')
        self.assertTrue(capture_equal(expected,actual))
        for u in NEW:
            bad=copy.deepcopy(actual);bad['tracks'][u]['width']='181000'
            self.assertFalse(capture_equal(expected,bad))

    def test_complete_native_transaction_preserves_all_other_payloads(self):
        sys.path.insert(0,str(PRODUCTION.parent.resolve()/'.konnect/native-ipc'))
        from kipy.board_types import Track, ArcTrack, Via, Net, BoardLayer
        from google.protobuf.json_format import ParseDict, MessageToDict
        source=read_json(MANIFEST)
        def objects(section,cls):
            result=[]
            for u,row in source[section].items():
                kind=ArcTrack if section=='tracks' and self.before['tracks'][u].get('geometry')=='arc' else cls
                message=type(kind().proto)();ParseDict(row,message);result.append(kind(message))
            return result
        class Board:
            def get_tracks(self):return objects('tracks',Track)
            def get_vias(self):return objects('vias',Via)
            def get_footprints(self):return []
            def get_nets(self):return [Net(name=n) for n in {r['net'] for r in J7MigrationTests.after['tracks'].values()}]
            def get_layer_by_name(self,n):return BoardLayer.Value('BL_'+n.replace('.','_'))
        creates,removes,expected=build_transaction(Board(),source,dict(operations=reconcile(self.before,self.after)))
        self.assertEqual({x.id.value for x in creates},set(NEW));self.assertEqual({x.id.value for x in removes},set(OLD))
        for s in source:
            if s not in ['tracks','hashes']:self.assertEqual(source[s],expected[s])
        for u,row in source['tracks'].items():
            if u not in OLD:self.assertEqual(row,expected['tracks'][u])
        for x in creates:
            row=self.after['tracks'][x.id.value]
            self.assertEqual(x.net.name,'USB_CC2');self.assertEqual(x.width,180000)
            self.assertEqual([x.start.x/1e6,x.start.y/1e6],row['start'])
            self.assertEqual([x.end.x/1e6,x.end.y/1e6],row['end'])
            self.assertEqual(expected['tracks'][x.id.value],MessageToDict(x.proto))


if __name__=='__main__':unittest.main()
