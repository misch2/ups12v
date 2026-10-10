"""Read-only CAD verification; writes only the evidence JSON beside this script.

IPC exports establish live pad/net state. Saved CAD/library parsing is a read-only
last resort for custom-pad primitives not exposed by Konnect's geometry reader.
"""
from pathlib import Path
import collections
import csv
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
CAD = HERE.parent / 'ups_v4'
live = json.loads((HERE / 'phase4-2-live-readback.json').read_text())
libs = json.loads((HERE / 'phase4-2-library-readback.json').read_text())
xml = ET.parse(HERE / 'phase3-7-final.net.xml').getroot()
expected = {c.get('ref'): c for c in xml.findall('./components/comp')}
inventory = {c['reference']: c for c in live['inventory']['components']}
expected_nets = {(p.get('ref'), p.get('pin')): n.get('name')
                 for n in xml.findall('./nets/net') for p in n.findall('node')}
issues = []
if len(inventory) != live['inventory']['count']:
    issues.append(['duplicate_reference'])
for ref in sorted(set(expected) ^ set(inventory)):
    issues.append(['reference_set', ref])
checked = 0
for ref, comp in expected.items():
    if ref not in inventory:
        continue
    for key in ['value', 'footprint']:
        if comp.findtext(key) != inventory[ref][key]:
            issues.append(['property', ref, key, comp.findtext(key), inventory[ref][key]])
    readback = live['pads'][ref]
    if readback.get('source') != 'ipc':
        issues.append(['not_live', ref])
    numbered = collections.defaultdict(list)
    for p in readback['pads']:
        if p['number']:
            numbered[p['number']].append(p)
    for (r, pin), net in expected_nets.items():
        if r != ref:
            continue
        checked += 1
        if pin not in numbered:
            issues.append(['missing_pad', ref, pin, net])
        for p in numbered[pin]:
            if p['net'] != net:
                issues.append(['net_mismatch', ref, pin, net, p['net']])
    for pin, pads in numbered.items():
        if (ref, pin) not in expected_nets and any(p['net'] for p in pads):
            issues.append(['extra_connected_pad', ref, pin])

def sexpr(path):
    # General parser for read-only structural comparison. Quoted escapes retained
    # consistently; no writer or normalization of CAD files exists here.
    toks = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', Path(path).read_text(encoding='utf-8-sig'))
    stack, root = [], None
    for t in toks:
        if t == '(':
            a = []
            if stack:
                stack[-1].append(a)
            stack.append(a)
        elif t == ')':
            root = stack.pop()
        else:
            stack[-1].append(t[1:-1] if t.startswith('"') else t)
    assert not stack
    return root

def children(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]

def child(node, key):
    found = children(node, key)
    return found[0] if found else None

def same(a, b):
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    try:
        return math.isclose(float(a), float(b), rel_tol=0, abs_tol=1e-6)
    except (TypeError, ValueError):
        return a == b

def pad_geometry(p):
    keys = {'at', 'size', 'drill', 'layers', 'roundrect_rratio', 'chamfer_ratio',
            'chamfer', 'options', 'primitives', 'rect_delta', 'offset'}
    attrs = []
    for x in p[4:]:
        if not isinstance(x, list) or x[0] not in keys:
            continue
        if x[0] == 'layers':
            x = [x[0]] + sorted(x[1:])
        if x[0] == 'at' and len(x) == 3:
            x = x + ['0']
        attrs.append(x)
    return [p[:4]] + sorted(attrs, key=lambda x: x[0])

def pad_sort(p):
    a = child(p, 'at')
    return (p[1], float(a[1]), float(a[2]))

board_path = CAD / 'ups12v_v4.kicad_pcb'
board = sexpr(board_path)
saved = {}
for fp in children(board, 'footprint'):
    reference = next(p[2] for p in children(fp, 'property') if p[1] == 'Reference')
    saved[reference] = fp
geometry = {}
saved_live_issues = []
for ref, item in inventory.items():
    fp = saved.get(ref)
    if fp is None:
        saved_live_issues.append(['missing_saved_reference', ref])
        continue
    pads = children(fp, 'pad')
    saved_map = collections.Counter((p[1], (child(p, 'net') or ['', ''])[1]) for p in pads)
    # KiCad 10 uses named nets directly in pad net nodes. Older formats also
    # carry numeric codes; handle both explicitly.
    net_table = {n[1]: n[2] for n in children(board, 'net') if len(n) > 2}
    saved_map = collections.Counter((p[1], '' if child(p, 'net') is None else
        child(p, 'net')[-1] if len(child(p, 'net')) > 2 else
        net_table.get(child(p, 'net')[1], child(p, 'net')[1])) for p in pads)
    live_map = collections.Counter((p['number'], p['net']) for p in live['pads'][ref]['pads'])
    if saved_map != live_map:
        saved_live_issues.append(['saved_live_pad_nets', ref])
    lib = json.loads(libs[item['footprint']]['content'][0]['text'])
    lpads = children(sexpr(lib['path']), 'pad')
    equal = len(pads) == len(lpads) and all(same(pad_geometry(a), pad_geometry(b))
        for a, b in zip(sorted(pads, key=pad_sort), sorted(lpads, key=pad_sort)))
    geometry[ref] = {'library': item['footprint'], 'physical_pads': len(pads),
        'unique_numbers': len({p[1] for p in pads if p[1]}),
        'custom_pad_numbers': [p[1] for p in pads if p[3] == 'custom'],
        'geometry_matches_library': equal, 'has_courtyard': lib['has_courtyard']}
    if not equal:
        issues.append(['saved_library_pad_geometry', ref])

population = list(csv.DictReader((HERE / 'phase3-7-population.csv').open()))
f5_only = [r['Reference'] for r in population if r['F0_fitted'] == '0' and r['F5_fitted'] == '1']
missing_f5 = sorted(set(f5_only) - set(inventory))
drc = json.loads((HERE / 'phase4-2-drc.json').read_text())
result = {
    'source': {'pad_nets': 'live_ipc', 'geometry_primitives': 'saved_board_vs_current_libraries',
               'drc': 'saved_board_no_save_no_refill'},
    'references': len(inventory), 'expected_references': len(expected),
    'nets': live['info']['net_count'], 'expected_nets': len(xml.findall('./nets/net')),
    'exported_pin_entries_checked': checked,
    'physical_pad_entries': sum(r['pad_count'] for r in live['pads'].values()),
    'copper_layers': live['layers']['copper_layer_count'],
    'issues': issues, 'saved_live_issues': saved_live_issues, 'geometry': geometry,
    'f5_only_references': f5_only, 'missing_f5': missing_f5,
    'board_items': {k: len(children(board, k)) for k in ['segment', 'arc', 'via', 'zone']},
    'drc_counts': {k: len(v) for k, v in drc.items()},
    'drc_rules': dict(collections.Counter(v['rule'] for v in drc['violations'])),
    'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
        [board_path, CAD / 'ups12v_v4.kicad_sch', HERE / 'phase3-7-final.net.xml']},
}
(HERE / 'phase4-2-verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in ['geometry', 'sha256', 'f5_only_references']}, indent=2))
