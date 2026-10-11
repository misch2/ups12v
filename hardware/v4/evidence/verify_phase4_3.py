"""Read-only Phase 4.3 verification; writes evidence JSON only, never CAD."""
import collections, copy, hashlib, json, runpy, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
g = runpy.run_path(str(HERE / 'phase4_3_geometry.py'))
b, child, children = g['base'], g['child'], g['children']
raw = json.loads((HERE / 'phase4-3-final-live-readback.json').read_text())
def decode(r):
    assert not r.get('isError'), r
    return json.loads(r['content'][0]['text'])
inv = decode(raw['inventory'])
actual = {x['reference']: x for x in inv['components']}
expected = b['expected']
issues, geometry_issues = [], []
for ref in sorted(set(actual) ^ set(expected)):
    issues.append(['reference', ref])
for ref, e in expected.items():
    for key in ['value', 'footprint']:
        if actual[ref][key] != e.findtext(key):
            issues.append(['property', ref, key])
pads = {ref: decode(r) for ref, r in raw['pads'].items()}
checked = 0
for (ref, pin), net in b['expected_nets'].items():
    checked += 1
    matches = [p for p in pads[ref]['pads'] if p['number'] == pin]
    if not matches or any(p['net'] != net for p in matches):
        issues.append(['pin_net', ref, pin, net])
for ref, read in pads.items():
    if read['source'] != 'ipc':
        issues.append(['source', ref])
    saved = g['fps'][ref]
    saved_nets = collections.Counter((p[1], (child(p, 'net') or ['', ''])[-1]) for p in children(saved, 'pad'))
    live_nets = collections.Counter((p['number'], p['net']) for p in read['pads'])
    if saved_nets != live_nets:
        issues.append(['saved_live_pad_nets', ref])

def normalized(p, rotation):
    q = copy.deepcopy(p)
    at = child(q, 'at')
    if len(at) == 3:
        at.append('0')
    at[3] = str((float(at[3]) - rotation) % 360)
    # KiCad IPC save removes a redundant closing vertex. This does not alter
    # a polygon's geometry, and must not be mistaken for replacing its lands.
    prim = child(q, 'primitives')
    if prim:
        for shape in prim[1:]:
            pts = child(shape, 'pts')
            if pts and len(pts) > 2 and b['same'](pts[1], pts[-1]):
                pts.pop()
    return b['pad_geometry'](q)

def geometry_same(a, z):
    if isinstance(a, list) and isinstance(z, list):
        return len(a) == len(z) and all(geometry_same(x, y) for x, y in zip(a, z))
    try:
        # IPC uses integer nanometres; tolerate one nanometre plus float noise.
        return math.isclose(float(a), float(z), rel_tol=0, abs_tol=1.0001e-6)
    except (TypeError, ValueError):
        return a == z

geometry = {}
for ref, fp in g['fps'].items():
    lib = decode(b['libs'][fp[1]])
    path = Path(lib['path'])
    if fp[1].startswith('easyeda2kicad:'):
        path = HERE.parent / 'ups_v4' / 'ups_v4_external.pretty' / (fp[1].split(':')[1] + '.kicad_mod')
    library = g['sexpr'](path)
    at = child(fp, 'at')
    angle = float(at[3]) if len(at) > 3 else 0
    ps = sorted(children(fp, 'pad'), key=b['pad_sort'])
    ls = sorted(children(library, 'pad'), key=b['pad_sort'])
    equal = len(ps) == len(ls) and all(geometry_same(normalized(p, angle), normalized(q, 0)) for p, q in zip(ps, ls))
    geometry[ref] = {'pad_geometry_matches_library': equal, 'physical_pads': len(ps),
                     'custom_pad_numbers': [p[1] for p in ps if p[3] == 'custom'],
                     'courtyard_present': bool([x for x in fp if isinstance(x, list) and x[0].startswith('fp_') and child(x, 'layer') == ['layer', 'F.CrtYd']])}
    if not equal:
        geometry_issues.append(ref)
drc = json.loads((HERE / 'phase4-3-final-drc.json').read_text())
score = decode(raw['score'])
result = {
    'board': str(HERE.parent / 'ups_v4' / 'ups12v_v4.kicad_pcb'),
    'ipc_open': decode(raw['open']), 'board_info': decode(raw['info']),
    'layers': decode(raw['layers']), 'stackup': decode(raw['stackup']),
    'references': len(actual), 'physical_pads': sum(len(p['pads']) for p in pads.values()),
    'checked_xml_pin_entries': checked, 'connectivity_issues': issues,
    'pad_geometry_issues': geometry_issues, 'geometry': geometry,
    'outline_mm': {'x1': 30, 'y1': 30, 'x2': 126, 'y2': 100, 'width': 96, 'height': 70},
    'tracks': len(children(g['board'], 'segment')), 'vias': len(children(g['board'], 'via')),
    'zones': len(children(g['board'], 'zone')),
    'placement_score': score['score'], 'placement_hard_failures': score['hard_failures'],
    'drc_counts': dict(collections.Counter(v['rule'] for v in drc['violations'])),
    'unconnected_items': len(drc['unconnected_items']), 'schematic_parity': len(drc['schematic_parity']),
    'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE.parent / 'ups_v4' / 'ups12v_v4.kicad_pcb', HERE.parent / 'ups_v4' / 'ups12v_v4.kicad_sch']},
    'notes': ['Custom polygons compared after redundant closing-vertex normalization; no land approximation.',
              'Score only establishes geometric placement checks; RF, thermal and routability qualification remain open.']
}
(HERE / 'phase4-3-verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ['references','physical_pads','checked_xml_pin_entries','connectivity_issues','pad_geometry_issues','tracks','vias','zones','placement_score','placement_hard_failures','drc_counts','unconnected_items','schematic_parity']}))
