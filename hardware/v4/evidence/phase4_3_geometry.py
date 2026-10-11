"""Read-only helpers for placement evidence; no CAD writes."""
import contextlib
import io
import runpy
import math
import json
from pathlib import Path
with contextlib.redirect_stdout(io.StringIO()):
    base = runpy.run_path(str(Path(__file__).with_name('verify_phase4_2.py')))
child, children, sexpr = [base[k] for k in ['child', 'children', 'sexpr']]
board = sexpr(Path(__file__).parent.parent / 'ups_v4' / 'ups12v_v4.kicad_pcb')
fps = {next(p[2] for p in children(f, 'property') if p[1] == 'Reference'): f for f in children(board, 'footprint')}

def box(ref):
    fp = fps[ref]
    points = []
    for g in fp:
        if not isinstance(g, list) or not child(g, 'layer') or child(g, 'layer')[1] != 'F.CrtYd':
            continue
        if g[0] in ['fp_line', 'fp_rect']:
            points.extend([tuple(map(float, child(g, k)[1:3])) for k in ['start', 'end']])
        elif g[0] == 'fp_poly':
            points.extend(tuple(map(float, p[1:3])) for p in child(g, 'pts')[1:])
        elif g[0] == 'fp_circle':
            a, b = [tuple(map(float, child(g, k)[1:3])) for k in ['center', 'end']]
            radius = math.dist(a, b)
            points.extend([(a[0]-radius, a[1]-radius), (a[0]+radius, a[1]+radius)])
    if not points:
        for p in children(fp, 'pad'):
            a = list(map(float, child(p, 'at')[1:]))
            w, h = map(float, child(p, 'size')[1:3])
            points.extend([(a[0]-w/2-.25, a[1]-h/2-.25), (a[0]+w/2+.25, a[1]+h/2+.25)])
    return [min(p[0] for p in points), min(p[1] for p in points), max(p[0] for p in points), max(p[1] for p in points)]

if __name__ == '__main__':
    plan = json.loads(Path(__file__).with_name('phase4-3-initial-placement-plan.json').read_text())
    print(json.dumps({r: {'box': box(r), 'at': child(f, 'at'), 'group': plan[r]['group']} for r, f in fps.items()}))
