"""Geometric planning only; never changes CAD."""
import json, math, runpy
from pathlib import Path
P=Path(__file__).resolve().parent
g=runpy.run_path(str(P/'phase4_3_geometry.py'))
live=json.loads((P/'phase4-4-live-readback.json').read_text())
inv={c['reference']:c for c in live['inventory']['components']}
plan=json.loads((P/'phase4-4-native-placement-plan.json').read_text())
def dec(r): return json.loads(r['content'][0]['text'])
j7=dec(json.loads((P/'phase4-4-entry-readback.json').read_text())['j7_candidate'])
cap=dec(json.loads((P/'phase4-4-cap-footprint.json').read_text()))
def libbox(lib):
    pts=[q for v in lib['graphics'] if v['layer']=='F.CrtYd' for q in [v['start'],v['end']]]
    return [min(p['x'] for p in pts),min(p['y'] for p in pts),max(p['x'] for p in pts),max(p['y'] for p in pts)]
def transform(box,c):
    a=math.radians(c['rotation']); pts=[(c['x']+x*math.cos(a)+y*math.sin(a),c['y']-x*math.sin(a)+y*math.cos(a)) for x in box[::2] for y in box[1::2]]
    return [min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)]
boxes={r:transform(g['box'](r),c) for r,c in inv.items()}
for ref in ['J7','C70','C71','C36']:
    box=libbox(j7) if ref=='J7' else libbox(cap) if ref in ['C70','C71'] else g['box'](ref)
    boxes[ref]=transform(box,plan[ref])
collisions=[]
for r in ['J7','C70','C71','C36']:
    a=boxes[r]
    for s,b in boxes.items():
        if s==r: continue
        if min(a[2],b[2])>max(a[0],b[0])+1e-6 and min(a[3],b[3])>max(a[1],b[1])+1e-6:
            if sorted([r,s]) not in collisions: collisions.append(sorted([r,s]))
out={'status':'Candidate only; verify native DRC and physical mating after placement','courtyard_boxes_mm':{r:boxes[r] for r in ['J7','C70','C71','C36']},'bounding_box_courtyard_collisions':collisions,'J7_front_face_x_mm':round(plan['J7']['x']+8.61,3),'J7_front_courtyard_extends_beyond_board_mm':round(boxes['J7'][2]-126,3),'limit':'Axis-aligned courtyard boxes only; excludes actual mating cable, soldering tooling, 3D enclosure and routed returns.'}
(P/'phase4-4-native-placement-check.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
