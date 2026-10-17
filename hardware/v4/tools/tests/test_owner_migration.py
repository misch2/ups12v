"""Offline exact-delta negative controls for Phase4.16; no native CAD I/O."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from v4kicad.safety import read_json, ToolError, write_json, digest
from v4kicad.owner_migration import reconcile, worker, bindings, native_capture
from v4kicad.owner_migration_proof import compare_profiles


class ExactOwnerMigration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan_path = Path('hardware/v4/evidence/phase4-15-production-proposal/production-migration-plan.json')
        cls.plan = read_json(cls.plan_path)
        cls.before = read_json('hardware/v4/evidence/phase4-13-final-production-native/snapshot.json')
        cls.owner = read_json(Path(cls.plan['native_review'])/'snapshot.json')

    def test_complete_exact_exported_delta(self):
        self.assertTrue(reconcile(self.before,self.owner,self.plan)['complete_delta_equal'])

    def test_reject_missing_deleted_track(self):
        p = copy.deepcopy(self.plan)
        p['operations']['tracks']['remove_with_preimage'].pop(next(iter(p['operations']['tracks']['remove_with_preimage'])))
        with self.assertRaises(ToolError):
            reconcile(self.before,self.owner,p)

    def test_reject_moved_via_preimage(self):
        p = copy.deepcopy(self.plan)
        next(iter(p['operations']['vias']['update_with_preimage'].values()))['before']['position'][0] += .000001
        with self.assertRaises(ToolError):
            reconcile(self.before,self.owner,p)

    def test_reject_arc_flattening_even_if_not_in_whitelist(self):
        owner = copy.deepcopy(self.owner)
        uid = next(u for u,v in owner['tracks'].items() if v.get('geometry')=='arc')
        owner['tracks'][uid]['geometry'] = 'line'
        with self.assertRaises(ToolError):
            reconcile(self.before,owner,self.plan)

    def test_reject_R8_pad_net_or_shape_change(self):
        for field,value in [('net','PGND'),('drill_size',[.1,.1])]:
            owner = copy.deepcopy(self.owner)
            uid = next(iter(self.plan['implicit_pad_translations']))
            owner['pads'][uid][field] = value
            with self.assertRaises(ToolError):
                reconcile(self.before,owner,self.plan)

    def test_reject_added_auxiliary_battery_branch(self):
        owner = copy.deepcopy(self.owner)
        owner['tracks']['unauthorized'] = dict(next(iter(owner['tracks'].values())))
        with self.assertRaises(ToolError):
            reconcile(self.before,owner,self.plan)

    def test_stopped_worker_never_connects(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_json(root/'STOP.json',dict(reason='uncertain transaction'))
            with self.assertRaisesRegex(ToolError,'stopped'):
                worker(root,'preflight','must-not-connect')

    def test_captured_net_code_omission_is_cache_only(self):
        root = Path('hardware/v4/evidence/phase4-16-editor-rehearsal')
        expected = read_json(root/'ipc-expected.json')
        returned = {x['id']['value']:x for x in read_json(root/'returned-items.json')}
        requested = {u:v for s in expected.values() for u,v in s.items() if u in returned}
        self.assertEqual(native_capture(requested),native_capture(returned))
        bad = copy.deepcopy(returned)
        uid = next(u for u,v in bad.items() if 'net' in v)
        bad[uid]['net']['name'] = 'WRONG_ELECTRICAL_NET'
        self.assertNotEqual(native_capture(requested),native_capture(bad))
        bad = copy.deepcopy(returned)
        bad[uid]['width'] = {'valueNm':'999999'}
        self.assertNotEqual(native_capture(requested),native_capture(bad))

    def test_only_valid_named_net_cache_is_normalized(self):
        a = {'x':{'net':{'name':'BATTERY','code':{'value':1}},'code':{'value':9}}}
        b = copy.deepcopy(a); b['x']['net']['code']['value'] = 99
        self.assertEqual(native_capture(a),native_capture(b))
        for edit in ['name','unknown','geometry','code_only','malformed']:
            b = copy.deepcopy(a)
            if edit == 'name': b['x']['net']['name'] = 'PGND'
            elif edit == 'unknown': b['x']['net']['other'] = 1
            elif edit == 'geometry': b['x']['code']['value'] = 10
            elif edit == 'code_only': b['x']['net'].pop('name')
            else: b['x']['net']['code'] = {'other':2}
            self.assertNotEqual(native_capture(a),native_capture(b))

    def test_project_provenance_separate_from_electrical_profile(self):
        owner = read_json(Path(self.plan['native_review'])/'routing-context.json')['profile']
        production = read_json('hardware/v4/evidence/phase4-16-entry-native/routing-context.json')['profile']
        self.assertTrue(compare_profiles(owner,production,self.plan))
        for edit in ['project_sha256','copper_clearance','rules_sha256']:
            bad = copy.deepcopy(production)
            bad[edit] = 'changed' if edit.endswith('sha256') else .099
            with self.assertRaises(ToolError):
                compare_profiles(owner,bad,self.plan)

    def test_original_inputs_bound_and_installed_replay_rejected(self):
        if digest(self.plan['production_board']) == self.plan['expected_production_hashes']['ups12v_v4.kicad_pcb']:
            self.assertEqual(bindings(self.plan_path)['phase'],'4.15')
        else:
            with self.assertRaises(ToolError):
                bindings(self.plan_path)

    def test_native_sdk_build_preserves_arcs_and_translates_complete_R8(self):
        # Pure protobuf construction; there is no KiCad process/connection or CAD save.
        sys.path.insert(0,str(Path(self.plan['production_board']).parent/'.konnect/native-ipc'))
        from kipy.board_types import Track, ArcTrack, Via, FootprintInstance, Net, BoardLayer
        from google.protobuf.json_format import ParseDict
        from v4kicad.owner_migration import build_transaction
        source = read_json(self.plan['accepted_production_manifest'])
        def objects(section, cls):
            rows = []
            for uid,row in source[section].items():
                concrete = ArcTrack if section=='tracks' and self.before['tracks'][uid].get('geometry')=='arc' else cls
                message = type(concrete().proto)()
                ParseDict(row,message)
                rows.append(concrete(message))
            return rows
        class Board:
            def get_tracks(self): return objects('tracks',Track)
            def get_vias(self): return objects('vias',Via)
            def get_footprints(self): return objects('footprints',FootprintInstance)
            def get_nets(self):
                nets = [Net(name=n) for n in {v['net'] for v in ExactOwnerMigration.owner['tracks'].values()}]
                for i,net in enumerate(nets): net.proto.code.value = i+1
                return nets
            def get_layer_by_name(self,name): return BoardLayer.Value('BL_'+name.replace('.','_'))
        raw = read_json('hardware/v4/evidence/phase4-16-entry-native/routed-diagnostics.json')['items']
        target_raw = read_json(Path(self.plan['native_review'])/'routed-diagnostics.json')['items']
        signature = lambda v:{k:x for k,x in v.items() if k not in ['uuid','net','position','position_nm']}
        templates = {u:next(k for k,v in raw.items() if v['kind']=='via' and signature(v)==signature(target_raw[u]))
                     for u in self.plan['operations']['vias']['create']}
        updates,creates,removes,expected = build_transaction(Board(),source,self.plan,templates)
        self.assertEqual((len(updates),len(creates),len(removes)),(6,255,222))
        for section in ['tracks','vias']:
            for op in ['create','update_with_preimage']:
                for uid in self.plan['operations'][section][op]:
                    self.assertNotIn('code',expected[section][uid]['net'])
        for u,v in self.before['tracks'].items():
            if v.get('geometry')=='arc':
                self.assertEqual(source['tracks'][u],expected['tracks'][u])
        for u,row in self.plan['implicit_pad_translations'].items():
            wanted = {k:v for k,v in source['pads'][u].items() if k!='position'}
            self.assertEqual(wanted,{k:v for k,v in expected['pads'][u].items() if k!='position'})
            xy = expected['pads'][u]['position']
            self.assertEqual([int(xy['xNm']),int(xy['yNm'])],
                             [round(v*1e6) for v in row['after']['position']])


if __name__ == '__main__':
    unittest.main()
