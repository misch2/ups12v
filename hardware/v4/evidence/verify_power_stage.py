"""Independent pin-partition acceptance for the V4 power stage, from XML exports.

Run only after exporting the saved CAD and running Konnect ERC. This script never
writes KiCad files. The expected source hash binds the checks to a reviewed source.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--export', type=Path, required=True)
parser.add_argument('--erc', type=Path, required=True)
parser.add_argument('--expected-sha256', required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
schematic = HERE.parent / 'ups_v4' / 'ups12v_v4.kicad_sch'
actual_hash = hashlib.sha256(schematic.read_bytes()).hexdigest()
assert actual_hash == args.expected_sha256, 'CAD changed after the reviewed hash was captured'
assert args.export.stat().st_mtime >= schematic.stat().st_mtime, 'XML export predates saved CAD'
assert args.erc.stat().st_mtime >= schematic.stat().st_mtime, 'ERC report predates saved CAD'


def read_nets(path):
    return {net.attrib['name']: {(n.attrib['ref'], n.attrib['pin'])
                                for n in net.findall('node')}
            for net in ET.parse(path).findall('./nets/net')}


before = read_nets(HERE / 'phase2-resume.net.xml')
after = read_nets(args.export)
expected = {name: set(pins) for name, pins in before.items()}
# The legacy four split-corner representations are redundant logical pins;
# the accepted official footprint encodes split copper under logical 1/9/16/24.
for pins in expected.values():
    pins.difference_update({('IC1', str(pin)) for pin in range(30, 34)})
# Only the quiet TS/NTC/PROG returns remain on the local analog GND tie.
system_returns = {('C3', '2'), ('IC1', '10'), ('J4', '2'),
                  ('Q3', '2'), ('R10', '2'), ('TP1', '1')}
assert system_returns <= expected['GND']
expected['GND'].difference_update(system_returns)
expected['PGND'].update(system_returns)
# Fuse is in series with the adapter positive lead, ahead of VAC1/C9/Q1.
expected['VIN1'].remove(('J1', '2'))
expected['VIN1'].add(('F1', '1'))
expected['ADAPTER_RAW'] = {('J1', '2'), ('F1', '2')}


def partitions(nets):
    return {frozenset(pins) for pins in nets.values() if pins}


assert partitions(after) == partitions(expected), {
    'unexpected_pin_partitions': [sorted(s) for s in partitions(after) - partitions(expected)],
    'missing_pin_partitions': [sorted(s) for s in partitions(expected) - partitions(after)],
}
for net in ('VBUS', 'VIN1', 'GND', 'PGND', 'CE_N', 'CE_BIAS', 'SYS', 'BATTERY', 'REGN'):
    assert after[net] == expected[net], (net, sorted(after.get(net, set())))
actual_ic_pins = {pin for pins in after.values() for ref, pin in pins if ref == 'IC1'}
assert actual_ic_pins == {str(pin) for pin in range(1, 30)}, actual_ic_pins
erc = json.loads(args.erc.read_text(encoding='utf-8'))
assert erc['errors'] == 0, erc
assert erc['warnings'] == 0, erc
result = {
    'source_sha256': actual_hash,
    'export_sha256': hashlib.sha256(args.export.read_bytes()).hexdigest(),
    'erc_sha256': hashlib.sha256(args.erc.read_bytes()).hexdigest(),
    'all_pin_partitions_match_explicit_expected_changes': True,
    'charger_logical_pins': sorted(actual_ic_pins, key=int),
    'system_return_migration': sorted(system_returns),
    'input_fuse_precedes_VAC1_and_FETs': True,
    'F01_and_CE_pin_sets_preserved': True,
    'erc_errors': erc['errors'], 'erc_warnings': erc['warnings'],
    'scope': 'Saved schematic electrical partitions only; not package geometry, BOM qualification, PCB or hardware validation',
}
args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
