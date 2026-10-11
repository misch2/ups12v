"""IPC baseline normalization must preserve electrical differences."""
import copy
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from v4kicad.ipc_install import comparable

class IPCBaselineTests(unittest.TestCase):
    def test_only_runtime_fields_normalized(self):
        a = {'via': {'parent': {'value': 'old'}, 'id': {'value': 'retained'},
                     'copper': {'shape': 'PSS_CIRCLE', 'customAnchorShape': 'PSS_CIRCLE', 'size': 500000}}}
        b = copy.deepcopy(a); b['via']['parent']['value'] = 'new'
        b['via']['copper']['customAnchorShape'] = 'PSS_RECTANGLE'
        self.assertEqual(comparable(a), comparable(b))
        b['via']['copper']['size'] = 700000
        self.assertNotEqual(comparable(a), comparable(b))
        b = copy.deepcopy(a); b['via']['id']['value'] = 'changed'
        self.assertNotEqual(comparable(a), comparable(b))

    def test_custom_anchor_and_nested_parent_not_ignored(self):
        a = {'pad': {'shape': 'PSS_CUSTOM', 'customAnchorShape': 'PSS_CIRCLE',
                     'nested': {'parent': 'one'}}}
        b = copy.deepcopy(a); b['pad']['customAnchorShape'] = 'PSS_RECTANGLE'
        self.assertNotEqual(comparable(a), comparable(b))
        b = copy.deepcopy(a); b['pad']['nested']['parent'] = 'two'
        self.assertNotEqual(comparable(a), comparable(b))
