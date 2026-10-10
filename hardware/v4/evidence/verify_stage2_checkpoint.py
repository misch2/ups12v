"""Read exported netlists only; never modifies KiCad CAD files."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
CHECKPOINT_SHA256 = '9e24befb0abd0773dc8e0fef906ce1ee626a21169359d601d055aae8a0e5804c'
sch = HERE.parent / 'ups_v4' / 'ups12v_v4.kicad_sch'
source_hash = hashlib.sha256(sch.read_bytes()).hexdigest()
assert source_hash == CHECKPOINT_SHA256, (
    'This script verifies the historical stage 2.2b checkpoint only. '
    'Current CAD differs; export and verify the new stage instead of reusing stale evidence.'
)

def nets(name):
    root = ET.parse(HERE / name).getroot()
    return {n.attrib['name']: {(p.attrib['ref'], p.attrib['pin'])
                              for p in n.findall('node')}
            for n in root.findall('./nets/net')}

before = nets('phase2-f01.net.xml')
ports = nets('phase2-2a-ports.net.xml')
after = nets('phase2-2b-ce.net.xml')
assert {frozenset(v) for v in before.values()} == {frozenset(v) for v in ports.values()}
expected = {
    'CE_N': {('IC1', '13'), ('R9', '1'), ('Q3', '3')},
    'CE_BIAS': {('D3', '1'), ('D4', '1'), ('R9', '2')},
    'CHG_REQ': {('J4', '5'), ('R11', '1')},
    '/CHG_GATE': {('R11', '2'), ('R10', '1'), ('Q3', '1')},
    'MAIN_3V3': {('J4', '1'), ('D4', '2')},
    'VBUS': {('IC1', '2'), ('IC1', '3'), ('IC1', '8'), ('NT4', '1'),
             ('C7', '1'), ('C13', '1'), ('C16', '1')},
}
for net, pins in expected.items():
    assert after[net] == pins, (net, after.get(net))
assert ('D3', '2') in after['REGN']
assert {('Q3', '2'), ('R10', '2')} <= after['GND']
assert ('J2', '2') in after['SYS'] and ('J2', '2') not in after['PMID']
assert ('J4', '1') not in after['PMID']
changed_refs = {'Q3', 'R9', 'R10', 'R11', 'D3', 'D4'}
changed_pins = {('IC1', '13'), ('J2', '2'), ('J4', '1'), ('J4', '5')}
def unaffected(mapping):
    return {frozenset(p for p in pins if p[0] not in changed_refs and p not in changed_pins)
            for pins in mapping.values()} - {frozenset()}
assert unaffected(before) == unaffected(after), 'Unexpected connectivity change outside CE/output ports'
erc = json.loads((HERE / 'phase2-2b-ce-erc.json').read_text(encoding='utf-8'))
assert erc['errors'] == 0 and erc['warnings'] == 2
result = {
    'root_port_cleanup_preserves_all_pin_partitions': True,
    'ce_and_interface_pin_sets': {k: sorted(v) for k, v in expected.items()},
    'output_is_SYS': True,
    'unaffected_pin_partitions_unchanged': True,
    'ground_topology_still_legacy_GND_PGND': True,
    'capacitor_population_still_legacy': True,
    'erc_errors': erc['errors'], 'erc_warnings': erc['warnings'],
    'schematic_sha256': source_hash,
    'scope': 'Saved schematic/export checks only; no live PCB or hardware qualification',
}
(HERE / 'phase2-2b-connectivity.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
