"""Read-only preservation check of geometry not fully exposed by MCP readers.

Full live queries, native sync, ERC and DRC are saved separately. Never writes CAD.
"""
from pathlib import Path
import collections, hashlib, json, math, re, subprocess

P = Path(__file__).resolve().parent
B = P.parent / 'ups_v4/ups12v_v4.kicad_pcb'

def parse(text):
    stack = []
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
        if token == '(':
            node = []
            if stack: stack[-1].append(node)
            stack.append(node)
        elif token == ')': root = stack.pop()
        else: stack[-1].append(token[1:-1] if token.startswith('"') else token)
    assert not stack
    return root

def many(n, key): return [x for x in n if isinstance(x, list) and x and x[0] == key]
def one(n, key): return next(iter(many(n, key)), None)
def ref(f): return next(p[2] for p in many(f, 'property') if p[1] == 'Reference')
def geom(f): return [[x for x in p if not (isinstance(x, list) and x and x[0] in ('at', 'uuid'))] for p in many(f, 'pad')]
def is_edge(n): return isinstance(n, list) and one(n, 'layer') == ['layer', 'Edge.Cuts']

base = parse(subprocess.check_output(['git', 'show', 'HEAD:hardware/v4/ups_v4/ups12v_v4.kicad_pcb'], text=True, encoding='utf-8'))
now = parse(B.read_text(encoding='utf-8'))
old = {ref(f): f for f in many(base, 'footprint')}
new = {ref(f): f for f in many(now, 'footprint')}
moved = {r: {'before': one(old[r], 'at')[1:], 'after': one(new[r], 'at')[1:]} for r in old if one(old[r], 'at') != one(new[r], 'at')}
native_rf = lambda b: [z for z in many(b, 'zone') if one(z, 'name') == ['name', 'U1_RF_ANTENNA']]
work = json.loads((P/'phase4-6-work-state.json').read_text(encoding='utf-8'))
old_drc = json.loads((P/'phase4-5-final-drc.json').read_text(encoding='utf-8'))
drc = json.loads((P/'phase4-6-final-drc.json').read_text(encoding='utf-8'))
key = lambda v: (v.get('type', v.get('rule')), v['description'], tuple(sorted(i['description'] for i in v['items'])))
unchanged_unrouted = set(map(key, old_drc['unconnected_items'])) == set(map(key, drc['unconnected_items']))
def net_counts(report):
    return dict(collections.Counter(re.search(r'\[([^\]]+)\]', u['items'][0]['description']).group(1) for u in report['unconnected_items']))
unrouted_counts_equal = net_counts(old_drc) == net_counts(drc)
unchanged_warnings = set(map(key, old_drc['violations'])) == set(map(key, drc['violations']))
planned = work['plan']
observed = {c['reference']: c for c in work['after_components']['components']}
live_moves = {r: all(abs(a-b)<.00001 for a,b in zip(p, (observed[r]['x'], observed[r]['y'], observed[r]['rotation']))) for r,p in planned.items()}
before = work['before_traces']['traces']
after = work['final_traces']['traces']
length = lambda t: math.hypot(t['x1']-t['x2'], t['y1']-t['y2'])
sw = {}
for net in ('SW1', 'SW2'):
    # Same IC-side junction to the L1 land centre, excluding retained package fanout.
    old_main = [t for t in before if t['net']==net and t['width'] >= (1.2 if net=='SW1' else 2.2)]
    new_main = [t for t in after if t['net']==net and t['width'] >= 1.2]
    a = sum(map(length, old_main)) + (.8 if net=='SW1' else 0)
    b = sum(map(length, new_main)) + (.45 if net=='SW1' else 0)
    sw[net] = {'main_centreline_before_mm': a, 'main_centreline_after_mm': b, 'reduction_percent': 100*(a-b)/a}

plane = next(z for z in many(now,'zone') if one(z,'name') == ['name','V4_PGND_REFERENCE'])
filled = many(plane, 'filled_polygon')
polys = [[list(map(float, p[1:3])) for p in many(one(f,'pts'),'xy')] for f in filled]
def inside(poly,x,y):
    result=False
    for i,(a,b) in enumerate(poly):
        c,d=poly[i-1]
        if (b>y)!=(d>y) and x<(c-a)*(y-b)/(d-b)+a: result=not result
    return result
bad_rf = sum(any(inside(poly,75.4+(ix+.5)*.02,99.2+(iy+.5)*.02) for poly in polys) for ix in range(660) for iy in range(40))
sch = B.with_suffix('.kicad_sch')
sch_head = subprocess.check_output(['git','show','HEAD:hardware/v4/ups_v4/ups12v_v4.kicad_sch'])
result = {
    'board_sha256': hashlib.sha256(B.read_bytes()).hexdigest(),
    'baseline_commit': subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
    'reference_sets_equal': old.keys()==new.keys(), 'footprint_count':len(new),
    'moved_footprints':moved, 'live_moves_verified':live_moves,
    'property_changes':[r for r in old if {p[1]:p[2] for p in many(old[r],'property')}!={p[1]:p[2] for p in many(new[r],'property')}],
    'population_changes':[r for r in old if many(old[r],'attr')!=many(new[r],'attr')],
    'pad_geometry_changes_excluding_placement':[r for r in old if geom(old[r])!=geom(new[r])],
    'IC1_full_custom_pads_unchanged':many(old['IC1'],'pad')==many(new['IC1'],'pad'),
    'RF_rule_area_unchanged':native_rf(base)==native_rf(now),
    'outline_unchanged':[n for n in base if is_edge(n)]==[n for n in now if is_edge(n)],
    'schematic_byte_identical_to_HEAD':sch.read_bytes()==sch_head,
    'tracks':len(many(now,'segment')), 'vias':len(many(now,'via')),
    'retained_vias_unchanged':all(v == next((n for n in many(now,'via') if one(n,'uuid')==one(v,'uuid')),None) for v in many(base,'via') if one(v,'uuid') in [one(n,'uuid') for n in many(now,'via')]),
    'removed_via_count':len({one(v,'uuid')[1] for v in many(base,'via')}-{one(v,'uuid')[1] for v in many(now,'via')}),
    'added_via_count':len({one(v,'uuid')[1] for v in many(now,'via')}-{one(v,'uuid')[1] for v in many(base,'via')}),
    'live_saved_track_uuids_agree':{t['uuid'] for t in after}=={one(t,'uuid')[1] for t in many(now,'segment')},
    'PGND_filled_polygon_count':len(filled), 'RF_unexpected_samples':bad_rf,
    'remaining_unrouted_identical_to_before':unchanged_unrouted,
    'remaining_unrouted_counts_per_net_unchanged':unrouted_counts_equal,
    'unrouted_counts_per_net':net_counts(drc),
    'airwire_tree_note':'Four representative edges changed as copper geometry changed: PMID C20/C22/C24, SYS C61 and deferred REGN NT2 fanout. Same per-net counts; exact nearest-item/MST edge identity is not a connectivity invariant.',
    'unrouted_removed_edges':[v for v in old_drc['unconnected_items'] if key(v) not in set(map(key,drc['unconnected_items']))],
    'unrouted_added_edges':[v for v in drc['unconnected_items'] if key(v) not in set(map(key,old_drc['unconnected_items']))],
    'warnings_identical_to_before':unchanged_warnings,
    'drc':{'unrouted':len(drc['unconnected_items']), 'other_errors':sum(v['severity']=='error' for v in drc['violations']), 'warnings':sum(v['severity']=='warning' for v in drc['violations']), 'parity':len(drc.get('schematic_parity',[]))},
    'switch_main_routing':sw,
    'width_screen_A':{str(w):.048*30**.44*((w/.0254)*(.035/.0254))**.725 for w in (1.2,1.5,1.6,2.2)},
    'screening_assumptions':'IPC-2221 relation, external35um copper, illustrative30C rise; not owner acceptance limits, fabrication confirmation or thermal measurement',
    'scope':'Bounded power-stage improvement; not a completed board or fabrication/power-up approval',
}
(P/'phase4-6-checkpoint-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
assert set(moved)==set(planned)
assert all(live_moves.values())
assert not result['property_changes'] and not result['population_changes']
assert not result['pad_geometry_changes_excluding_placement']
assert all(result[k] for k in ('reference_sets_equal','IC1_full_custom_pads_unchanged','RF_rule_area_unchanged','outline_unchanged','schematic_byte_identical_to_HEAD','live_saved_track_uuids_agree','remaining_unrouted_counts_per_net_unchanged','warnings_identical_to_before'))
assert len(filled)==1 and bad_rf==0 and result['drc']['other_errors']==0 and result['drc']['parity']==0
assert result['retained_vias_unchanged'] and result['removed_via_count']==24 and result['added_via_count']==28
print(json.dumps({k:result[k] for k in ('tracks','vias','footprint_count','drc','switch_main_routing','remaining_unrouted_identical_to_before','warnings_identical_to_before')}))
