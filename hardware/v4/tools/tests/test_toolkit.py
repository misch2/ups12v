"""Small regression suite; fake native objects deliberately enforce KiCad's API contract."""
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
import copy
import importlib
import json
import sys
import subprocess
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from v4kicad.geometry import inventory_row, identify, preservation, pad_row
from v4kicad.checks import parse_check
from v4kicad.safety import (ToolError, digest, prepare_review_scratch,
                            prepare_scratch, run_monitored, verify_context,
                            verify_review_context)


class Track:
    m_Uuid = SimpleNamespace(AsString=lambda: 'track-uuid')
    def GetNetname(self): return 'BATTERY'
    def GetLayer(self): return 0
    def GetWidth(self): return 600000
    def GetStart(self): return SimpleNamespace(x=63100000, y=65500000)
    def GetEnd(self): return SimpleNamespace(x=63800000, y=66900000)


class Via(Track):
    m_Uuid = SimpleNamespace(AsString=lambda: 'via-uuid')
    def __init__(self): self.layers = []
    def GetWidth(self, *args):
        if not args:
            raise AssertionError('PCB_VIA::GetWidth called without a layer argument')
        self.layers.append(args[0])
        return [700000, 800000, 900000, 1000000][args[0]]
    def GetPosition(self): return SimpleNamespace(x=63100000, y=65500000)
    def GetDrillValue(self): return 400000
    def GetStart(self): raise AssertionError('Via must use GetPosition')
    def GetEnd(self): raise AssertionError('Via must use GetPosition')


API = SimpleNamespace(PCB_TRACK=Track, PCB_VIA=Via, F_Cu=0, In1_Cu=1, In2_Cu=2, B_Cu=3)
BOARD = SimpleNamespace(GetLayerName=lambda layer: ['F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu'][layer])


class GeometryTests(unittest.TestCase):
    def test_diagnostic_reports_net_change_without_accepting_it(self):
        from v4kicad.scratch_diagnostic import compare,overlaps
        via=dict(kind='via',ordinal=0,net='PGND',position=[1.,.1],drill=.3,
            copper_widths={'F.Cu':.5,'In1.Cu':.5,'In2.Cu':.5,'B.Cu':.5})
        track=dict(kind='track',ordinal=0,net='S',layer='B.Cu',width=.18,start=[0.,0.],end=[2.,0.])
        actual=[dict(via,uuid='v',net='S',native_diagnostics={}),dict(track,uuid='t',native_diagnostics={})]
        result=compare([track,via],actual)
        self.assertFalse(result['exact_equal'])
        self.assertTrue(result['exact_geometry_equal_ignoring_net'])
        self.assertEqual(result['changed_objects'][0]['field_differences'],
            {'net':dict(expected='PGND',actual='S')})
        self.assertAlmostEqual(overlaps([track,via])[0]['copper_edge_gap_mm'],-.24)

    def test_diagnostic_counts_existing_duplicate_tracks_exactly(self):
        from v4kicad.scratch_diagnostic import compare
        track=dict(kind='track',ordinal=0,net='S',layer='F.Cu',width=.18,start=[0.,0.],end=[.1,.1])
        result=compare([track,dict(track,ordinal=1)],
            [dict(track,uuid='a'),dict(track,uuid='b')])
        self.assertTrue(result['exact_equal'])
        self.assertEqual(result['expected_duplicates'][0]['count'],2)
        self.assertEqual(result['actual_duplicates'][0]['count'],2)

    def test_read_only_route_diagnostics_keeps_raw_units_and_per_layer_padstack(self):
        from v4kicad.geometry import routed_diagnostics
        class DiagnosticVia(Via):
            def Padstack(self):
                return SimpleNamespace(Mode=lambda:0,DrillShape=lambda:1,
                    Shape=lambda layer:2,Size=lambda layer:SimpleNamespace(
                        x=[700000,800000,900000,1000000][layer],
                        y=[700000,800000,900000,1000000][layer]))
            def GetViaType(self):return 3
            def TopLayer(self):return 0
            def BottomLayer(self):return 3
            def GetRemoveUnconnected(self):return False
            def GetKeepStartEnd(self):return True
        via=DiagnosticVia()
        board=SimpleNamespace(GetTracks=lambda:[Track(),via],GetLayerName=BOARD.GetLayerName)
        api=SimpleNamespace(**vars(API),GetBuildVersion=lambda:'10.test',VIATYPE_THROUGH=3,PAD_SHAPE_CIRCLE=2)
        d=routed_diagnostics(board,api)['items']
        self.assertEqual(d['track-uuid']['start_nm'],[63100000,65500000])
        self.assertEqual(d['via-uuid']['layer_pair'],['F.Cu','B.Cu'])
        self.assertEqual(d['via-uuid']['padstack_layers']['In2.Cu']['width_nm'],900000)
        self.assertEqual(via.layers,[0,1,2,3,0,1,2,3])

    def test_native_addition_mismatch_keeps_exact_diagnostics_and_stops(self):
        from v4kicad.native import verify_added
        before=dict(tracks={'old':dict(width=.2)},vias={})
        after=dict(tracks={'old':dict(width=.2),'new':dict(width=.19)},vias={})
        expected={'new':dict(width=.2)}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'mismatch.json'
            with self.assertRaises(ToolError):verify_added(before,after,expected,path)
            result=json.loads(path.read_text())
            self.assertEqual(result['changed'],['new'])
            self.assertEqual(result['actual']['new']['width'],.19)
            self.assertEqual(result['expected'],expected)

    def test_exact_previous_failure_and_safe_mixed_inventory(self):
        via = Via()
        with self.assertRaisesRegex(AssertionError, 'without a layer'):
            via.GetWidth()  # Reproduce the API contract without asserting in real KiCad.
        rows = identify(inventory_row(item, BOARD, API) for item in [Track(), via])
        self.assertEqual(rows['track-uuid']['width'], .6)
        self.assertEqual(rows['via-uuid']['position'], [63.1, 65.5])
        self.assertEqual(rows['via-uuid']['drill'], .4)
        self.assertEqual(rows['via-uuid']['copper_widths'],
                         {'F.Cu': .7, 'In1.Cu': .8, 'In2.Cu': .9, 'B.Cu': 1.0})
        self.assertEqual(via.layers, [0, 1, 2, 3])
        self.assertNotIn('start', rows['via-uuid'])

    def test_unknown_type_and_duplicate_identity_fail(self):
        with self.assertRaises(ToolError): inventory_row(SimpleNamespace(m_Uuid=Track.m_Uuid, GetNetname=lambda: ''), BOARD, API)
        with self.assertRaises(ToolError): identify([{'uuid': 'x'}, {'uuid': 'x'}])
        class Arc(Track): pass
        arc_api = SimpleNamespace(**vars(API), PCB_ARC=Arc)
        with self.assertRaisesRegex(ToolError, 'Arc native APIs missing'):
            inventory_row(Arc(), BOARD, arc_api)

    def test_pad_only_queries_present_copper_layers(self):
        class Poly:
            def OutlineCount(self): return 0
        api = SimpleNamespace(**vars(API), SHAPE_POLY_SET=Poly, ERROR_OUTSIDE=1)
        calls = []
        pad = SimpleNamespace(m_Uuid=Track.m_Uuid, IsOnLayer=lambda l: l in [0, 3],
                              TransformShapeToPolygon=lambda poly, layer, *args: calls.append(layer),
                              GetNumber=lambda: '1', GetNetname=lambda: 'PROG',
                              GetDrillSize=lambda: SimpleNamespace(x=600000, y=1000000),
                              GetDrillShape=lambda: 1,
                              GetPosition=lambda: SimpleNamespace(x=1000000, y=2000000))
        row = pad_row(pad, SimpleNamespace(GetReference=lambda: 'R5'), BOARD, api)
        self.assertEqual(calls, [0, 3])
        self.assertEqual(set(row['polygons']), {'F.Cu', 'B.Cu'})
        self.assertEqual(row['drill_size'], [.6, 1.0])

    def test_preservation_rejects_net_width_missing_via_and_pad_changes(self):
        before = dict(tracks=identify([inventory_row(Track(), BOARD, API)]),
                      vias=identify([inventory_row(Via(), BOARD, API)]), pads={}, footprints={}, zones={})
        after = copy.deepcopy(before); after['tracks']['track-uuid']['layer'] = 'In2.Cu'
        self.assertTrue(preservation(before, after, ('track-uuid', 'F.Cu', 'In2.Cu'))['original_geometry_preserved'])
        for section, uid, field, value in [('tracks', 'track-uuid', 'width', .7),
                                         ('tracks', 'track-uuid', 'net', 'PGND'),
                                         ('vias', 'via-uuid', 'drill', .3)]:
            bad = copy.deepcopy(after); bad[section][uid][field] = value
            with self.assertRaises(ToolError): preservation(before, bad, ('track-uuid', 'F.Cu', 'In2.Cu'))
        bad = copy.deepcopy(after); bad['vias'].clear()
        with self.assertRaises(ToolError): preservation(before, bad, ('track-uuid', 'F.Cu', 'In2.Cu'))
        bad = copy.deepcopy(after); bad['pads']['new'] = {}
        with self.assertRaises(ToolError): preservation(before, bad, ('track-uuid', 'F.Cu', 'In2.Cu'))


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.source = self.root / 'production'; self.source.mkdir()
        self.board = self.source / 'board.kicad_pcb'; self.board.write_bytes(b'accepted-board-fixture')
        self.board.with_suffix('.kicad_pro').write_bytes(b'project-fixture')
        self.manifest = self.root / 'hashes.json'
        self.manifest.write_text(json.dumps({'hashes': {self.board.name: digest(self.board)}}))
    def tearDown(self): self.tmp.cleanup()

    def test_hash_mismatch_refused_before_output_created(self):
        self.board.write_bytes(b'changed')
        with self.assertRaises(ToolError): prepare_scratch(self.board, self.manifest, self.root / 'scratch')
        self.assertFalse((self.root / 'scratch').exists())

    def test_production_alias_and_existing_destination_refused(self):
        for target in [self.source, self.source / 'child', self.root]:
            with self.assertRaises(ToolError): prepare_scratch(self.board, self.manifest, target)

    def test_scratch_copy_lock_and_source_drift(self):
        target = prepare_scratch(self.board, self.manifest, self.root / 'scratch')
        self.assertEqual(digest(target / self.board.name), digest(self.board))
        lock = target / '~board.kicad_pcb.lck'; lock.touch()
        with self.assertRaises(ToolError): verify_context(target)
        lock.unlink(); self.board.write_bytes(b'drift')
        with self.assertRaises(ToolError): verify_context(target)

    def test_scratch_sidecar_mutation_refused(self):
        target = prepare_scratch(self.board, self.manifest, self.root / 'scratch')
        (target / 'board.kicad_pro').write_bytes(b'changed')
        with self.assertRaises(ToolError): verify_context(target)

    def review_fixture(self):
        owner = self.root / 'owner'; owner.mkdir()
        owner_board = owner / self.board.name
        owner_board.write_bytes(b'owner-edit-differs-from-accepted')
        owner_board.with_suffix('.kicad_pro').write_bytes(b'owner-project')
        owner_board.with_suffix('.kicad_sch').write_bytes(b'owner-schematic')
        return owner_board

    def test_owner_review_allows_source_diff_but_binds_copy_hash(self):
        owner_board = self.review_fixture()
        target = prepare_review_scratch(owner_board, self.manifest,
                                        self.root / 'review', self.board)
        self.assertNotEqual(digest(owner_board), digest(self.board))
        self.assertEqual(digest(target / owner_board.name), digest(owner_board))
        (target / owner_board.name).write_bytes(b'tampered-before-native-read')
        with self.assertRaises(ToolError): verify_review_context(target)

    def test_owner_review_rejects_source_or_production_drift(self):
        owner_board = self.review_fixture()
        target = prepare_review_scratch(owner_board, self.manifest,
                                        self.root / 'review', self.board)
        owner_board.write_bytes(b'owner-drift')
        with self.assertRaises(ToolError): verify_review_context(target)

        # Recreate the isolated review because the first failure intentionally
        # leaves the source drifted; production drift is independently guarded.
        owner_board.write_bytes(b'owner-edit-differs-from-accepted')
        target = prepare_review_scratch(owner_board, self.manifest,
                                        self.root / 'review2', self.board)
        self.board.write_bytes(b'production-drift')
        with self.assertRaises(ToolError): verify_review_context(target)

    def test_owner_review_rejects_output_overlap_and_auxiliary_mutation(self):
        owner_board = self.review_fixture()
        with self.assertRaises(ToolError):
            prepare_review_scratch(owner_board, self.manifest,
                                   owner_board.parent / 'child', self.board)
        target = prepare_review_scratch(owner_board, self.manifest,
                                        self.root / 'review', self.board)
        (target / 'board.kicad_pro').write_bytes(b'changed-project')
        with self.assertRaises(ToolError): verify_review_context(target)

    def test_assertion_monitor_stops_only_its_worker_before_later_write(self):
        marker = self.root / 'must-not-exist'
        # Simulated assertion text, not an assertion in KiCad or the PCB Editor.
        code = 'import sys,time,pathlib;sys.stderr.write(\'assert "false" failed in GetWidth():\');sys.stderr.flush();time.sleep(3);pathlib.Path(sys.argv[1]).touch()'
        with self.assertRaisesRegex(ToolError, 'owner approval'):
            run_monitored([sys.executable, '-u', '-c', code, marker], self.root / 'native.log', timeout=10)
        self.assertFalse(marker.exists())
        self.assertIn('GetWidth', (self.root / 'native.log').read_text())

    def test_ipc_failure_and_nonzero_exit_are_not_success(self):
        for code in ["print('IPC connection failed')", "print('Failed to connect to KiCad: Connection refused')", 'raise SystemExit(7)']:
            with self.assertRaises(ToolError):
                run_monitored([sys.executable, '-c', code], self.root / 'failed.log')


class ReportAndImportTests(unittest.TestCase):
    def test_drc_distinguishes_unconnected_parity_and_physical_errors(self):
        report = dict(violations=[{'severity': 'error'}, {'severity': 'warning'}],
                      unconnected_items=[{}] * 3, schematic_parity=[{}], ignored_checks=[])
        self.assertEqual(parse_check(report, 'drc'), dict(errors=1, warnings=1, unconnected=3, parity=1, ignored_checks=[]))
        with self.assertRaises(ToolError): parse_check({}, 'drc')

    def test_erc_collects_sheets_and_rejects_missing_results(self):
        self.assertEqual(parse_check({'sheets': [{'violations': [{'severity': 'warning'}]}]}, 'erc'),
                         dict(sheets=1, errors=0, warnings=1))
        with self.assertRaises(ToolError): parse_check({'sheets': [{}]}, 'erc')
        with self.assertRaises(ToolError): parse_check({'sheets': []}, 'erc')

    def test_imports_do_not_load_native_code_or_access_files(self):
        code = '''import sys,importlib
from unittest import mock
sys.path.insert(0,sys.argv[1])
with mock.patch('pathlib.Path.read_text',side_effect=AssertionError('IO on import')),mock.patch('subprocess.Popen',side_effect=AssertionError('process on import')):
 for name in ['v4kicad.geometry','v4kicad.safety','v4kicad.checks','v4kicad.native','v4kicad.cli','v4kicad.usb_review','v4kicad.ipc_install','v4kicad.ipc_u3','v4kicad.route_plan','v4kicad.review','v4kicad.u3_review','v4kicad.post_batch','v4kicad.f0_plan','v4kicad.scratch_diagnostic','v4kicad.plan_validation','kicad_v4']:
  importlib.import_module(name)
 from pathlib import Path
 for filename in ['phase4_7_layer_validation.py','phase4_7_layer_geometry.py','phase4_7_native_width_smoke.py']:
  spec=importlib.util.spec_from_file_location(filename[:-3],Path(sys.argv[1]).parent/'evidence'/filename)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
assert 'pcbnew' not in sys.modules
'''
        subprocess.run([sys.executable, '-B', '-c', code, str(Path(__file__).resolve().parents[1])], check=True)


if __name__ == '__main__': unittest.main()
