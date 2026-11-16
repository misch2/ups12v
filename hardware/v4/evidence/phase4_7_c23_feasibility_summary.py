"""Offline evidence summary; no native KiCad or IPC operations."""
from pathlib import Path
import json,hashlib,math,collections
E=Path(__file__).resolve().parent;B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
base=json.loads((E/'c9-apply-phase4-7-batch1-final-ipc.json').read_text())
entry=json.loads((E/'c9-apply-phase4-7-c23-feasibility-entry-ipc.json').read_text())
g=json.loads((E/'phase4-7-c23-feasibility-pad-polygons.json').read_text())
pg=next(p for p in g if p['ref']=='C23' and p['pin']=='2')['polygons']
def pointsegment(a,b,c):
 dx,dy=c[0]-b[0],c[1]-b[1];den=dx*dx+dy*dy
 t=max(0,min(1,((a[0]-b[0])*dx+(a[1]-b[1])*dy)/den)) if den else 0
 return math.hypot(a[0]-b[0]-t*dx,a[1]-b[1]-t*dy)
def xy(p):return [int(p.get(k+'Nm',0))/1e6 for k in ['x','y']]
def edges(q):return list(zip(q,q[1:]+q[:1]))
via_clearance=min(pointsegment([63.8,66.9],a,b) for q in pg for a,b in edges(q))-.35
tracks=[]
for t in base['tracks'].values():
 if t['net']['name']!='BATTERY' or t['layer']!='BL_F_Cu':continue
 a,b=xy(t['start']),xy(t['end'])
 dist=min(min(pointsegment(a,c,d),pointsegment(b,c,d),pointsegment(c,a,b),pointsegment(d,a,b)) for q in pg for c,d in edges(q))
 tracks.append(dict(start=a,end=b,clearance_mm=dist-int(t['width']['valueNm'])/2e6))
hashes={n:hashlib.sha256((B.parent/n).read_bytes()).hexdigest() for n in base['hashes']}
out=dict(entry_exactly_matches_accepted_batch1=entry==base,production_hashes_unchanged=hashes==base['hashes'],hashes=hashes,
 production_counts={n:len(base[n]) for n in ['footprints','pads','tracks','vias','zones']},
 C23_production_position_mm=[71.5,66.3],C23_production_orientation_degrees=90,
 scratch_C23_position_mm=[63,67.6],scratch_C23_orientation_degrees=90,
 scratch_via_clearance_mm=via_clearance,nearest_front_battery_track=min(tracks,key=lambda t:t['clearance_mm']),
 IC1_C23_courtyard_separation_mm=.09,
 hypothetical_pgnd_via_on_C23_pad2_In2_clearance_mm=pointsegment([63,67.12],[63.1,66.9],[63.8,66.9])-.35-.25,
 geometry_basis='Native KiCad copper polygons exported with 0.0001 mm maximum polygon error; preserved Batch 1 IPC track/via geometry. Not pad bounding boxes.',
 verdict='FAILED CANDIDATE: no joint BATP/PGND solution established; no production mutation; STOP',
 limitations=['Two sequential two-layer searches, 0.025 mm grid, 0.15 mm tracks, 0.5/0.3 mm vias, 0.101 mm planning clearance; not exhaustive proof of impossibility.',
 'Scratch board contains both independently found corridors specifically to expose their mutual conflict; crossing is not an accepted routed solution.',
 'ILIM_HIZ, TS and PROG joint escape feasibility not established because BATP/PGND failed first.',
 'Scratch parity unavailable without matching root schematic; library-context warnings differ from production.',
 'No production refill/save/DRC/ERC performed after failure; accepted Batch 1 results retained, not represented as fresh checks.'])
assert out['entry_exactly_matches_accepted_batch1'] and out['production_hashes_unchanged']
(E/'phase4-7-c23-feasibility-summary.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['production_hashes_unchanged','production_counts','scratch_via_clearance_mm','nearest_front_battery_track','hypothetical_pgnd_via_on_C23_pad2_In2_clearance_mm','verdict']}))
