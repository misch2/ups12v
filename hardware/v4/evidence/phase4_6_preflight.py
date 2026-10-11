"""Read only saved native fill/via geometry unavailable from Konnect readers.

Run after synchronized live-board refill/save. Writes evidence only, never CAD.
"""
from pathlib import Path
import hashlib, json, re

P = Path(__file__).resolve().parent
B = P.parent / 'ups_v4/ups12v_v4.kicad_pcb'

def parse(text):
    stack = []
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
        if token == '(':
            node = []
            if stack:
                stack[-1].append(node)
            stack.append(node)
        elif token == ')':
            root = stack.pop()
        else:
            stack[-1].append(token[1:-1] if token.startswith('"') else token)
    assert not stack
    return root

def many(n, key):
    return [x for x in n if isinstance(x, list) and x and x[0] == key]

def one(n, key):
    return next(iter(many(n, key)), None)

def points(n):
    return [list(map(float, xy[1:3])) for xy in many(one(n, 'pts'), 'xy')]

def inside(poly, x, y):
    result = False
    for i, (a, b) in enumerate(poly):
        c, d = poly[i-1]
        if (b > y) != (d > y) and x < (c-a)*(y-b)/(d-b)+a:
            result = not result
    return result

board = parse(B.read_text(encoding='utf-8'))
plane = next(z for z in many(board, 'zone') if one(z, 'name') == ['name', 'V4_PGND_REFERENCE'])
rf = next(z for z in many(board, 'zone') if one(z, 'name') == ['name', 'U1_RF_ANTENNA'])
polys = [points(f) for f in many(plane, 'filled_polygon')]
rfpts = points(one(rf, 'polygon'))
vias = []
for v in many(board, 'via'):
    net = one(v, 'net')
    if net and net[-1] in ('SW1', 'SW2'):
        vias.append({'uuid': one(v, 'uuid')[1], 'net': net[-1],
                     'xy_mm': list(map(float, one(v, 'at')[1:3])),
                     'diameter_mm': float(one(v, 'size')[1]),
                     'drill_mm': float(one(v, 'drill')[1])})

# A dense strip screen supplements the actual native-fill SVG, not a proof of RF performance.
unexpected = []
for ix in range(660):
    x = 75.4 + (ix + .5) * .02
    for iy in range(40):
        y = 99.2 + (iy + .5) * .02
        if any(inside(poly, x, y) for poly in polys):
            unexpected.append([x, y])
cross_sections = {}
for x in (75.0, 76.0, 82.0, 88.0, 89.0):
    edges = []
    for poly in polys:
        for i, (a, b) in enumerate(poly):
            c, d = poly[i-1]
            if (a > x) != (c > x):
                edges.append(b + (d-b)*(x-a)/(c-a))
    cross_sections[str(x)] = sorted(round(y, 6) for y in edges)

result = {
    'source': 'saved native geometry after Konnect live IPC refill and synchronized DRC save',
    'board_sha256': hashlib.sha256(B.read_bytes()).hexdigest(),
    'rf_rule_vertices_mm': rfpts,
    'rf_keepout_rules': one(rf, 'keepout'),
    'plane_layer': one(plane, 'layer'),
    'filled_polygon_count': len(polys),
    'RF_board_intersection_mm': {'x': [75.4, 88.6], 'y': [99.2, 100.0]},
    'strip_sample_pitch_mm': .02,
    'strip_sample_count': 660 * 40,
    'unexpected_filled_sample_count': len(unexpected),
    'unexpected_filled_samples': unexpected,
    'filled_polygon_vertical_intersections_mm': cross_sections,
    'switch_vias': vias,
    'inductor_land_vias_requiring_native_removal': [v for v in vias if v['xy_mm'][1] < 53],
    'limitation': 'Geometric evidence and a native filled-zone SVG; no RF/thermal/hardware qualification. No CAD routing or placement changed.',
}
(P / 'phase4-6-preflight-geometry.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: result[k] for k in ('filled_polygon_count', 'unexpected_filled_sample_count', 'filled_polygon_vertical_intersections_mm') }))
print(json.dumps({'switch_vias': len(vias), 'inductor_land_vias_requiring_native_removal': len(result['inductor_land_vias_requiring_native_removal'])}))
