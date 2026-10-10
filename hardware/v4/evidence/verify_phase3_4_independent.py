"""Parent review of saved KiCad XML, explicit U4 replacement and preservation."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

here = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--expected-sha256', required=True)
args = parser.parse_args()
source = here.parent / 'ups_v4/ups12v_v4.kicad_sch'
before_path = here / 'phase3-4-pre-ldo-baseline.net.xml'
after_path = here / 'phase3-4-usb-ldo.net.xml'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(source) == args.expected_sha256

def read(path):
    root = ET.parse(path).getroot()
    comps = {c.attrib['ref']: c for c in root.findall('./components/comp')}
    pins = {}
    for net in root.findall('./nets/net'):
        for node in net.findall('node'):
            key = (node.attrib['ref'], node.attrib['pin'])
            assert key not in pins, key
            pins[key] = net.attrib['name'].lstrip('/')
    return comps, pins

before, old = read(before_path)
after, new = read(after_path)
removed = {'C34', 'C38', 'C44', 'C46', 'L3', 'R34', 'R38', 'R39'}
assert set(before) - set(after) == removed
assert not set(after) - set(before)
changes = {('C40', '1'): ('USB_SS', 'USB3V3'),
           ('R35', '1'): ('USB_FB', 'USB3V3')}
checked = 0
for pin, net in old.items():
    if pin[0] in removed or pin[0] == 'U4':
        continue
    assert pin in new, ('lost retained pin', pin)
    if pin in changes:
        assert (net, new[pin]) == changes[pin], pin
    else:
        assert new[pin] == net, (pin, net, new[pin])
    checked += 1
for pin, net in {('U4','1'):'USB_VBUS', ('U4','2'):'PGND',
                 ('U4','3'):'USB3V3'}.items():
    assert new[pin] == net
assert {pin for pin in new if pin[0] == 'U4'} == {('U4','1'),('U4','2'),('U4','3')}
for ref in set(before) & set(after):
    for field in ('value', 'footprint'):
        if ref == 'U4' or (field == 'value' and ref in {'C27','C40','R35'}):
            continue
        assert before[ref].findtext(field) == after[ref].findtext(field), (ref, field)
fields = {f.attrib['name']:f.text for f in after['U4'].findall('./fields/field')}
assert fields['MPN'] == 'AP7361C-33E-13'
for name in ('phase3-4-usb-ldo.net.xml','phase3-4-usb-ldo-erc.json','phase3-4-usb-ldo.png'):
    assert (here/name).stat().st_mtime_ns >= source.stat().st_mtime_ns, name
result = {'status':'PASS', 'source_sha256':digest(source),
          'baseline_xml_sha256':digest(before_path), 'final_xml_sha256':digest(after_path),
          'retained_exported_pin_nets_checked':checked,
          'removed_references':sorted(removed), 'added_references':[],
          'explicit_rewires':['C40.1 USB_SS -> USB3V3','R35.1 USB_FB -> USB3V3',
                             'U4 replaced: 1 USB_VBUS / 2 PGND / 3 USB3V3'],
          'all_other_retained_values_footprints_and_pin_nets_preserved':True,
          'xml_erc_render_not_older_than_source':True,
          'scope':'Independent exported connectivity/property preservation, not hardware qualification'}
(here/'phase3-4-independent-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
