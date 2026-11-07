"""Read-only preservation/filled-plane inspection for the partial routing checkpoint.

Saved CAD is read only for custom pads, native keepout and filled-zone geometry
not exposed by installed Konnect readers. This script never writes CAD.
"""
from pathlib import Path
import ast, collections, hashlib, json, math, re, subprocess

P = Path(__file__).resolve().parent
B = P.parent / 'ups_v4/ups12v_v4.kicad_pcb'
def parse(text):
    stack = []
    for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
        if t == '(':
            a = []
            if stack: stack[-1].append(a)
            stack.append(a)
        elif t == ')': root = stack.pop()
        else: stack[-1].append(t[1:-1] if t.startswith('"') else t)
    assert not stack
    return root
def many(n, k): return [x for x in n if isinstance(x, list) and x and x[0] == k]
def one(n, k): return next(iter(many(n, k)), None)
def ref(f): return next(x[2] for x in many(f, 'property') if x[1] == 'Reference')
base = parse(subprocess.check_output(['git', 'show', 'HEAD:hardware/v4/ups_v4/ups12v_v4.kicad_pcb'], text=True, encoding='utf-8'))
now = parse(B.read_text(encoding='utf-8'))
old = {ref(f): f for f in many(base, 'footprint')}
new = {ref(f): f for f in many(now, 'footprint')}
moved = {r: {'before': one(old[r], 'at')[1:], 'after': one(new[r], 'at')[1:]} for r in old if one(old[r], 'at') != one(new[r], 'at')}
def pad_geometry(f):
    # Positions/angles may legitimately differ only on the named moved set.
    return [[x for x in p if not (isinstance(x, list) and x and x[0] in ['at', 'uuid', 'tstamp'])] for p in many(f, 'pad')]
pad_changes = [r for r in old if pad_geometry(old[r]) != pad_geometry(new[r])]
property_changes = [r for r in old if {p[1]:p[2] for p in many(old[r],'property')} != {p[1]:p[2] for p in many(new[r],'property')}]
population_changes = [r for r in old if many(old[r],'attr') != many(new[r],'attr')]
property_deltas = {}
for r in property_changes:
    a = {p[1]:p[2] for p in many(old[r],'property')}
    b = {p[1]:p[2] for p in many(new[r],'property')}
    property_deltas[r] = {k:{'before':a.get(k),'after':b.get(k)} for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
native_rf = [z for z in many(now, 'zone') if one(z, 'name') and one(z, 'name')[1] == 'U1_RF_ANTENNA']
old_rf = [z for z in many(base, 'zone') if one(z, 'name') and one(z, 'name')[1] == 'U1_RF_ANTENNA']
plane = next(z for z in many(now, 'zone') if one(z, 'name') and one(z, 'name')[1] == 'V4_PGND_REFERENCE')
filled = many(plane, 'filled_polygon')
rf_intersections = []
def point_in(poly, x, y):
    inside = False
    for i, (a,b) in enumerate(poly):
        c,d = poly[i-1]
        if (b > y) != (d > y) and x < (c-a)*(y-b)/(d-b)+a: inside = not inside
    return inside
polygons = [[tuple(map(float, xy[1:3])) for xy in many(one(f, 'pts'), 'xy')] for f in filled]
for x in [75.4+i*.2 for i in range(67)]:
    for y in [99.2+i*.05 for i in range(7)]:
        if any(point_in(poly,x,y) for poly in polygons): rf_intersections.append([x,y])
def capacity(w, t, k): return k * 30**.44 * ((w/.0254)*(t/.0254))**.725
drc = json.loads((P/'phase4-5-final-drc.json').read_text())
v = drc['violations']
unrouted = drc['unconnected_items']
ic_unrouted = sorted({int(m.group(1)) for u in unrouted for it in u['items'] for m in [re.search(r'Pad (\d+) .* of IC1\b', it['description'])] if m})
critical_ic_pins = {2,3,4,5,8,9,10,11,19,22,23,24,25,26,27,28,29}
out = {
 'status': 'INITIAL CHARGER ROUTING - owner review; remaining board circuitry unrouted; not a release',
 'baseline_commit': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 'board_sha256': hashlib.sha256(B.read_bytes()).hexdigest(),
 'footprint_count': len(new), 'reference_sets_equal': set(old)==set(new),
 'component_property_changes': property_changes, 'population_attribute_changes': population_changes,
 'component_property_deltas': property_deltas,
 'moved_footprints': moved, 'pad_geometry_changes_excluding_placement': pad_changes,
 'unmoved_footprint_full_pad_changes': [r for r in old if r not in moved and many(old[r],'pad') != many(new[r],'pad')],
 'IC1_full_custom_pads_unchanged': many(old['IC1'],'pad')==many(new['IC1'],'pad'),
 'native_RF_rule_area_unchanged': native_rf==old_rf,
 'outline_unchanged': [x for x in base if isinstance(x,list) and one(x,'layer')==['layer','Edge.Cuts']]==[x for x in now if isinstance(x,list) and one(x,'layer')==['layer','Edge.Cuts']],
 'tracks': len(many(now,'segment')), 'vias': len(many(now,'via')),
 'PGND_plane_filled_polygon_count': len(filled),
 'RF_fill_test': {'method':'point-in-filled-polygon sampling in board-intersecting RF strip; not a physical RF test', 'unexpected_points':rf_intersections},
 'drc': {'unrouted_before':345,'unrouted_after':len(unrouted), 'other_errors':sum(x['severity']=='error' for x in v), 'warnings':sum(x['severity']=='warning' for x in v), 'schematic_parity':len(drc.get('schematic_parity',[]))},
 'critical_IC1_power_pins_with_unrouted_findings': sorted(critical_ic_pins & set(ic_unrouted)),
 'critical_pin_findings_note': 'Pin 5 REGN still has deferred bias fanout to NT2/R6/R8/D3; IC1-to-C3 bypass is routed. A finding on a multi-terminal net does not imply every terminal is disconnected.',
 'deferred_IC1_pins_with_unrouted_findings': ic_unrouted,
 'screening': {'method':'IPC-2221 empirical screening; not qualification or IPC-2152 simulation','temperature_rise_assumption_C':30,'outer_copper_mm':.035,'inner_copper_mm':.035,'via_plating_assumption_mm':.025,'outer_2p2mm_A':capacity(2.2,.035,.048),'inner_2p2mm_A':capacity(2.2,.035,.024),'inner_3mm_A':capacity(3,.035,.024),'via_0p3mm_barrel_screen_A':.024*30**.44*(math.pi*.3*.025/.0254**2)**.725,'via_0p4mm_barrel_screen_A':.024*30**.44*(math.pi*.4*.025/.0254**2)**.725,'limitations':'Via barrel formula is a conservative area screening analogy, not a validated via thermal model. Copper/plating and ambient/load require fabrication and hardware confirmation.'}
}
(P/'phase4-5-checkpoint-verification.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ['status','footprint_count','moved_footprints','pad_geometry_changes_excluding_placement','IC1_full_custom_pads_unchanged','native_RF_rule_area_unchanged','outline_unchanged','tracks','vias','PGND_plane_filled_polygon_count','RF_fill_test','drc']},indent=2))
