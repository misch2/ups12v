"""Read-only XML checks for the owner's minimal emergency-UART correction."""
from pathlib import Path
import csv
import hashlib
import json
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
def read(name):
    root = ET.parse(HERE / name).getroot()
    assert root.findtext('./design/tool').startswith('Eeschema 10.0.7')
    components = {c.get('ref'): c for c in root.findall('./components/comp')}
    pins = {(p.get('ref'), p.get('pin')): n.get('name')
            for n in root.findall('./nets/net') for p in n.findall('node')}
    return root, components, pins

oldroot, old, oldpins = read('phase3-6-final.net.xml')
root, new, pins = read('phase3-7-final.net.xml')
removed = {'TP9', 'TP10', 'TP11', 'TP12'}
assert set(old) - set(new) == removed and not set(new) - set(old)
expected_pins = {p: n for p, n in oldpins.items() if p[0] not in removed}
assert pins == expected_pins, 'Unexpected pin-net change/addition beyond four removed pads'
fields_allowed = {
    'TP5': {'ServiceRole'}, 'TP6': {'ServiceRole'},
    'TP7': {'ServiceRole', 'Parameters'}, 'TP8': {'ServiceRole'},
    'TP13': {'ServiceRole', 'Parameters'}, 'TP14': {'ServiceRole', 'Parameters'},
}
for ref, c in new.items():
    o = old[ref]
    for tag in ['footprint', 'datasheet', 'libsource']:
        a, b = c.find(tag), o.find(tag)
        assert (ET.tostring(a) if a is not None else None) == (ET.tostring(b) if b is not None else None), (ref, tag)
    if ref not in {'TP5', 'TP6'}:
        assert c.findtext('value') == o.findtext('value'), ref
    def fields(component):
        return {f.get('name'): f.text or '' for f in component.findall('./fields/field')}
    of, nf = fields(o), fields(c)
    for f in set(of) | set(nf):
        if f not in fields_allowed.get(ref, set()) | ({'Value'} if ref in {'TP5','TP6'} else set()):
            assert of.get(f) == nf.get(f), (ref, f)

assert new['TP5'].findtext('value') == 'ESP_TX (GPIO21)'
assert new['TP6'].findtext('value') == 'ESP_RX (GPIO20)'
assert pins['TP5','1'] == pins['U1','31'] == 'UART_TX'
assert pins['TP6','1'] == pins['U1','30'] == 'UART_RX'
assert pins['TP7','1'] == 'PGND'
for pin, token in [('31','GPIO21'),('30','GPIO20')]:
    node = next(n for n in root.findall('./nets/net/node') if n.get('ref') == 'U1' and n.get('pin') == pin)
    assert token in node.get('pinfunction','')
for net, refs in [('UART_TX', {'TP5','U1'}), ('UART_RX', {'TP6','U1'})]:
    assert {r for (r,p),n in pins.items() if n == net} == refs, net
assert pins['TP8','1'] == 'MCU3V3' and pins['TP13','1'] == 'MAIN_3V3'
for ref in ['TP5','TP6','TP7','TP8','TP13','TP14','TP15','TP16','TP17']:
    assert new[ref].findtext('footprint') == 'TestPoint:TestPoint_Pad_D1.5mm'
switches = [r for r,c in new.items() if c.find('libsource').get('lib') == 'Switch']
assert switches, 'Expected existing BOOT/RESET buttons'
for net in ['MCU_EN','MCU_BOOT']:
    assert any(r in switches and n == net for (r,p),n in pins.items()), net
f5 = {'U7','U8','Q10','L3','J8'} | {f'R{i}' for i in range(60,64)} | {f'C{i}' for i in range(60,70)}
assert len(f5) == 19
f5nets = {n for (r,p),n in pins.items() if r in f5}
base_nets = {n for (r,p),n in pins.items() if r not in f5 | {'TP17'}}
assert f5nets & base_nets == {'SYS','PGND'}
assert {r for (r,p),n in pins.items() if n == 'F5_5V_OUT'} <= f5 | {'TP17'}
erc = json.loads((HERE / 'phase3-7-final-erc.json').read_text())
assert (erc['errors'],erc['warnings']) == (0,4)
assert {v['description'] for v in erc['violations']} == {
    v['description'] for v in json.loads((HERE / 'phase3-6-final-erc.json').read_text())['violations']}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(HERE / 'phase3-7-entry.kicad_sch') == json.loads((HERE / 'phase3-6-verification.json').read_text())['source_sha256']
report = {
    'status': 'PASS: minimal UART correction; no hardware validation',
    'source_sha256': sha(HERE.parent / 'ups_v4/ups12v_v4.kicad_sch'),
    'components': len(new), 'retained_pin_entries_verified': len(pins),
    'removed': sorted(removed), 'all_remaining_pin_nets_preserved': True,
    'all_power_USB_F5_and_button_properties_preserved': True,
    'uart': {'TP5': 'U1.31 GPIO21 TX', 'TP6': 'U1.30 GPIO20 RX', 'TP7': 'PGND'},
    'separate_voltage_measurements': {'TP8':'MCU3V3','TP13':'MAIN_3V3'},
    'F0_F5_parts': sorted(f5), 'ERC': [erc['errors'],erc['warnings']],
    'PCB_DRC_parity': 'Not applicable: no V4 PCB; mandatory before release',
    'artifact_sha256': {name: sha(HERE / name) for name in [
        'phase3-7-final.net.xml','phase3-7-final-erc.json','phase3-7-final.pdf','phase3-7-final.png']},
}
(HERE / 'phase3-7-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
with (HERE / 'phase3-7-population.csv').open('w',newline='',encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Reference','Value','F0_fitted','F5_fitted','Copper_only'])
    for r in sorted(f5 | {r for r in new if r.startswith('TP')}):
        copper = r.startswith('TP')
        writer.writerow([r,new[r].findtext('value'),0,0 if copper else 1,'yes' if copper else 'no'])
print(json.dumps({k: report[k] for k in ['status','components','retained_pin_entries_verified','removed','ERC']}))
