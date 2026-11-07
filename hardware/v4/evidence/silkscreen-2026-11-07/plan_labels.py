"""Plan visible reference positions using native glyph extents and physical envelopes."""
from pathlib import Path
import json, math, random
E=Path(__file__).resolve().parent
data=json.loads((E/'before-geometry.json').read_text())
rows=[r for r in data['labels'] if r['visible'] and r['layer']=='F.Silkscreen']
def intersect(a,b,gap=0):
    return a[0]<b[2]+gap-1e-7 and a[2]>b[0]-gap+1e-7 and a[1]<b[3]+gap-1e-7 and a[3]>b[1]-gap+1e-7
def distance(a,b):
    return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def rect(cx,cy,w,h):return [cx-w/2,cy-h/2,cx+w/2,cy+h/2]
def centroid(q):return [(q[0]+q[2])/2,(q[1]+q[3])/2]
edge=[30.15,30.15,125.85,99.85]
obstacles=[(r['ref'],r['body']) for r in data['labels']]+[('STATIC:'+s['text'],s['box']) for s in data['static']]
body_gap=.04
label_gap=.18
pad_gap=.15
pad_obstacles=[p for r in data['labels'] for p in r['pads']]
def clear(q):
    return q[0]>=edge[0] and q[1]>=edge[1] and q[2]<=edge[2] and q[3]<=edge[3] and not any(intersect(q,o,body_gap) for _,o in obstacles) and not any(intersect(q,p,pad_gap) for p in pad_obstacles)
def violations(layout):
    bad=[]
    for i,r in enumerate(rows):
        a=layout[r['ref']]['box']
        for ref,o in obstacles:
            if intersect(a,o,body_gap):bad.append([r['ref'],ref])
        for s in rows[:i]:
            if intersect(a,layout[s['ref']]['box'],label_gap):bad.append([r['ref'],s['ref']])
    return bad
initial={r['ref']:dict(box=r['text_box'],pos=r['pos'],angle=r['angle']) for r in rows}
candidates={}
for r in rows:
    ref=r['ref']; b=r['body']; bx,by=centroid(b); old=r['pos']
    points={}
    def add(cx,cy,angle,keep=False):
        w,h=r['sizes'][str(angle)]
        q=rect(cx,cy,w,h)
        if not clear(q):return
        off=r['offsets'][str(angle)]; pos=[round(cx-off[0],6),round(cy-off[1],6)]
        dist=distance(q,b)
        if dist>1.51:return
        # Strong association, readable direction, low displacement, preserve good examples.
        move=math.hypot(pos[0]-old[0],pos[1]-old[1])
        score=dist*8 + math.hypot(cx-bx,cy-by)*.12 + move*.20 + max(.18-dist,0)*12
        score+=0 if angle==r['angle']%180 else .25
        if keep:score-=1.2
        if ref in ['SW1','SW2','C24'] and keep:score-=20
        key=(round(cx,5),round(cy,5),angle)
        item=dict(pos=pos,angle=angle,box=q,score=score,body_gap=dist)
        if key not in points or score<points[key]['score']:points[key]=item
    for angle in [0,90]:
        w,h=r['sizes'][str(angle)]
        off=r['offsets'][str(angle)]
        add(old[0]+off[0],old[1]+off[1],angle,keep=True)
        for gap in [.04,.08,.12,.18,.28,.45,.65,.9,1.2]:
            for shift in [0]+[s*v for v in [.25,.5,.75,1,1.25,1.5,1.75,2,2.25,2.5,2.75,3,3.5,4,5] for s in [-1,1]]:
                if abs(shift)<=max(2.5,(b[2]-b[0])/2+1.5):
                    add(bx+shift,b[1]-gap-h/2,angle)
                    add(bx+shift,b[3]+gap+h/2,angle)
                if abs(shift)<=max(2.5,(b[3]-b[1])/2+1.5):
                    add(b[0]-gap-w/2,by+shift,angle)
                    add(b[2]+gap+w/2,by+shift,angle)
    candidates[ref]=sorted(points.values(),key=lambda c:c['score'])
    # Keep C14 next to its own capacitor, rather than above the neighbouring C11.
    if ref=='C14':
        candidates[ref]=[c for c in candidates[ref] if c['body_gap']<=.4 and c['pos'][1]>62]

summary=dict(initial_collisions=violations(initial),wrong_angles=[r['ref'] for r in rows if r['angle'] not in [0,90]],candidate_counts={ref:len(v) for ref,v in candidates.items()})
(E/'planning-diagnostic.json').write_text(json.dumps(summary,indent=2)+'\n')
empty=[ref for ref,v in candidates.items() if not v]
if empty:
    print(json.dumps(dict(no_candidates=empty,initial_collisions=len(summary['initial_collisions']))));raise SystemExit(2)

# Minimum-remaining-values backtracking. Candidate cost prefers the current good position.
nodes=0;best_depth=0
def solve(available,chosen):
    global nodes,best_depth
    nodes+=1
    if nodes>40000:return None
    if not available:return chosen
    ref=min(available,key=lambda k:len(available[k]))
    for c in available[ref][:40]:
        rest={k:[d for d in choices if not intersect(c['box'],d['box'],label_gap)] for k,choices in available.items() if k!=ref}
        if any(not v for v in rest.values()):continue
        result=solve(rest,{**chosen,ref:c})
        if result:return result
    return None
layout=solve(candidates,{})
if layout is None:
    print(json.dumps(dict(solved=False,nodes=nodes)));raise SystemExit(3)
assert not violations(layout)
changes={r['ref']:dict(before=initial[r['ref']],after=layout[r['ref']]) for r in rows
         if r['angle']!=layout[r['ref']]['angle'] or math.dist(r['pos'],layout[r['ref']]['pos'])>1e-5}
plan=dict(source='before-ipc.json / before-geometry.json',body_gap_mm=body_gap,label_gap_mm=label_gap,
          layout=layout,changes=changes,collisions=[],nodes=nodes)
(E/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps(dict(solved=True,nodes=nodes,visible=len(rows),changes=len(changes),initial_collisions=len(summary['initial_collisions']),wrong_angles=len(summary['wrong_angles']),fewest=sorted([(r,len(v)) for r,v in candidates.items()],key=lambda x:x[1])[:8],examples={r:layout[r] for r in ['J1','J2','H1','J6','SW1','SW2','C24']})))
