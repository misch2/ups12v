"""Exact IPC preparation against accepted native evidence; no native/IPC calls."""
import sys,copy
import unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'hardware/v4/tools'))
sys.path.insert(0,str(ROOT/'hardware/v4/ups_v4/.konnect/native-ipc'))
from v4kicad.ipc_u3 import check_candidate,prepare_footprints,expected_capture,POSITIONS
from v4kicad.safety import read_json,ToolError


class U3IPCTests(unittest.TestCase):
    def test_exact_supported_preparation_preserves_models_and_matches_native(self):
        from google.protobuf.json_format import ParseDict
        from kipy.board_types import FootprintInstance,Footprint3DModel
        from kipy.proto.board.board_types_pb2 import FootprintInstance as FP
        from kipy.geometry import Vector2
        r=ROOT/'hardware/v4/evidence';baseline=read_json(r/'phase4-8-baseline.json')
        plan=check_candidate(r/'phase4-8-u3-proposal-plan.json',r/'phase4-8-u3-proposal-scratch')
        fps=[FootprintInstance(ParseDict(row,FP())) for row in baseline['footprints'].values()]
        models={fp.id.value:[i.proto.SerializeToString() for i in fp.definition.items if isinstance(i,Footprint3DModel)] for fp in fps}
        old_rotate=Vector2.rotate
        updates=prepare_footprints(fps,plan,r/'phase4-8-u3-proposal-scratch')
        self.assertIs(Vector2.rotate,old_rotate)
        self.assertEqual(len(updates),4)
        for fp in updates:
            self.assertEqual(models[fp.id.value],[i.proto.SerializeToString() for i in fp.definition.items if isinstance(i,Footprint3DModel)])
        expected=expected_capture(baseline,updates)
        for key in ['tracks','vias','zones','shapes','texts']:self.assertEqual(expected[key],baseline[key])
        unchanged=set(baseline['footprints'])-{f.id.value for f in updates}
        self.assertTrue(all(expected['footprints'][i]==baseline['footprints'][i] for i in unchanged))
        bad=copy.deepcopy(plan);bad['placements']['L2'][0]+=.1
        with self.assertRaises(ToolError):prepare_footprints(fps,bad,r/'phase4-8-u3-proposal-scratch')
        self.assertIs(Vector2.rotate,old_rotate)

    def test_immutable_plan_hash_guard(self):
        r=ROOT/'hardware/v4/evidence'
        with mock.patch('v4kicad.ipc_u3.digest',return_value='changed'):
            with self.assertRaisesRegex(ToolError,'plan hash differs'):
                check_candidate(r/'phase4-8-u3-proposal-plan.json',r/'phase4-8-u3-proposal-scratch')

if __name__=='__main__':unittest.main()
