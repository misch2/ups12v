"""Offline comparison of assertion-safe IPC protobuf captures."""
from pathlib import Path
import sys,json,collections
E=Path(__file__).resolve().parent;tag=sys.argv[1]
before=json.loads((E/f'c9-apply-{sys.argv[2]}-ipc.json').read_text());after=json.loads((E/f'c9-apply-{sys.argv[3]}-ipc.json').read_text())
plan=json.loads((E/f'phase4-7-{tag}-plan.json').read_text())
def xy(p):return tuple(round(int(p.get(k+'Nm',0))/1e6,6) for k in ['x','y'])
def nm(t):return t.get('net',{}).get('name','')
unchanged={n:all(k in after[n] and v==after[n][k] for k,v in before[n].items()) and set(before[n])<=set(after[n]) for n in ['footprints','pads','tracks','vias','shapes','texts','zones']}
ts=[v for k,v in after['tracks'].items() if k not in before['tracks']];vs=[v for k,v in after['vias'].items() if k not in before['vias']]
actual=collections.Counter((nm(t),t['layer'],int(t['width']['valueNm'])/1e6,*xy(t['start']),*xy(t['end'])) for t in ts)
expected=collections.Counter((n,'BL_'+l.replace('.','_'),w,x1,y1,x2,y2) for n,l,w,x1,y1,x2,y2 in plan['tracks'])
remaining=list(actual.elements());deltas=[]
for target in expected.elements():
 found=next((i for i,row in enumerate(remaining) if row[:3]==target[:3] and max(abs(a-b) for a,b in zip(row[3:],target[3:]))<=0.0000011),None)
 if found is None:break
 row=remaining.pop(found);deltas.append(max(abs(a-b) for a,b in zip(row[3:],target[3:])))
track_match=len(deltas)==len(plan['tracks']) and not remaining
vexpected=collections.Counter((n,x,y,diam,drill) for n,x,y,diam,drill in plan['vias'])
vactual=collections.Counter((nm(v),*xy(v['position']),int(v['padStack']['copperLayers'][0]['size']['xNm'])/1e6,int(v['padStack']['drill']['diameter']['xNm'])/1e6) for v in vs)
out=dict(retained_objects_unchanged=unchanged,tracks_match=track_match,track_coordinate_tolerance_mm=0.0000011,max_track_coordinate_delta_mm=max(deltas,default=0),vias_match=vactual==vexpected,added_tracks=len(ts),added_vias=len(vs),new_track_ids=[t['id']['value'] for t in ts],new_via_ids=[v['id']['value'] for v in vs])
out['passed']=all(unchanged.values()) and out['tracks_match'] and out['vias_match']
(E/f'phase4-7-{tag}-live-preservation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if not k.endswith('_ids')}))
assert out['passed'], 'STOP: live mismatch; no automatic recovery'
