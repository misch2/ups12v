"""Independent retained-pin/property/freshness check on true KiCad XML only."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

here = Path(__file__).resolve().parent
source = here.parent / 'ups_v4/ups12v_v4.kicad_sch'
baseline = here / 'phase3-2-pre-simplification-baseline.net.xml'
final = here / 'phase3-3-simplified.net.xml'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(source) == '9e35f7545424b1885a91c5742e38fe2b9884143f6b2a36cf0438da44647c83bd'

def read(path):
    root = ET.parse(path).getroot()
    comps = {c.attrib['ref']: c for c in root.findall('./components/comp')}
    pins = {(n.attrib['ref'], n.attrib['pin'])
            for n in root.findall('./nets/net/node')}
    return comps, pins

before, old_pins = read(baseline)
after, new_pins = read(final)
removed = set(before) - set(after)
retained_pins = {p for p in old_pins if p[0] not in removed}
assert retained_pins <= new_pins, sorted(retained_pins - new_pins)
for ref in set(before) & set(after):
    for field in ('value', 'footprint'):
        if ref == 'R23' and field == 'value':
            continue
        assert before[ref].findtext(field) == after[ref].findtext(field), (ref, field)
for name in ('phase3-3-simplified.net.xml', 'phase3-3-simplified-erc.json',
             'phase3-3-simplified.png'):
    assert (here / name).stat().st_mtime_ns >= source.stat().st_mtime_ns, name
result = {
    'status': 'PASS', 'source_sha256': digest(source),
    'final_xml_sha256': digest(final),
    'retained_exported_pins_present': len(retained_pins),
    'retained_component_values_and_footprints_unchanged_except_R23_value': True,
    'xml_erc_render_not_older_than_source': True,
    'scope': 'XML pin presence and retained property preservation, not hardware qualification',
}
(here / 'phase3-3-final-independent-review.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
