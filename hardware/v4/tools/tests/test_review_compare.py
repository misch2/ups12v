"""Negative controls for the owner-review electrical preservation checks."""
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from v4kicad.review_compare import electrical_delta, connectivity_delta
from v4kicad.safety import ToolError


class ElectricalReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        # Export-style two-net resistor topology; expected partition is stated
        # explicitly and independently of the implementation's canonicalizer.
        self.initial = self.directory/'before.xml'
        self.initial.write_text('''<export><components>
          <comp ref="R48"><value>0R</value></comp>
          <comp ref="U1"><value>ESP32-C3</value></comp>
          <comp ref="J7"><value>USB</value></comp></components><nets>
          <net name="USB_DP"><node ref="J7" pin="A6"/><node ref="R48" pin="2"/></net>
          <net name="OLD_MCU"><node ref="R48" pin="1"/><node ref="U1" pin="27"/></net>
          </nets></export>''', encoding='utf-8')

    def modified(self, update):
        tree = ET.parse(self.initial)
        update(tree.getroot())
        output = self.directory/'after.xml'
        tree.write(output, encoding='utf-8')
        return electrical_delta(self.initial, output)

    def test_rename_retains_series_resistor_partition(self):
        result = self.modified(lambda r: r.find('./nets/net[@name="OLD_MCU"]').set('name','/USB_MCU_DP'))
        self.assertTrue(result['partitions_equal'])
        self.assertEqual(result['renamed_nets'][0]['pins'], [('R48','1'),('U1','27')])
        self.assertEqual(result['changed_components'], {})

    def test_hidden_resistor_bypass_is_not_a_rename(self):
        def bypass(root):
            connector, mcu = root.findall('./nets/net')
            for node in list(mcu):
                connector.append(node)
            root.find('./nets').remove(mcu)
        result = self.modified(bypass)
        self.assertFalse(result['partitions_equal'])
        self.assertEqual(len(result['added_partitions']), 1)

    def test_changed_component_value_detected_with_equal_connectivity(self):
        result = self.modified(lambda r: setattr(r.find('./components/comp/value'),'text','22R'))
        self.assertTrue(result['partitions_equal'])
        self.assertEqual(list(result['changed_components']), ['R48'])

    def test_native_island_merge_preserves_old_connectivity(self):
        result = connectivity_delta({'pad_partitions':[['a','b'],['c']]},
                                    {'pad_partitions':[['c','b','a']]})
        self.assertTrue(result['all_previous_pad_connections_preserved'])

    def test_native_island_split_detected_even_with_same_total_island_count(self):
        result = connectivity_delta({'pad_partitions':[['a','b'],['c']]},
                                    {'pad_partitions':[['a','c'],['b']]})
        self.assertFalse(result['all_previous_pad_connections_preserved'])
        self.assertEqual(result['split_old_islands'], [['a','b']])

    def test_missing_pad_coverage_is_not_an_empty_success(self):
        with self.assertRaises(ToolError):
            connectivity_delta({'pad_partitions':[['a','b']]}, {'pad_partitions':[['a']]})


if __name__ == '__main__':
    unittest.main()
