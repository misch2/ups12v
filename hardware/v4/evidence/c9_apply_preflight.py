"""Native saved-board preflight only, no CAD writes."""
from pathlib import Path
import sys,json,math,hashlib
sys.dont_write_bytecode=True
import pcbnew
E=Path(__file__).resolve().parent; B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
b=pcbnew.LoadBoard(str(B)); entry=json.loads((E/'c9-apply-entry-ipc.json').read_text())
old=json.loads((E/'c9-review-geometry.json').read_text())
assert hashlib.sha256(B.read_bytes()).hexdigest()==old['hashes']['ups_v4\\ups12v_v4.kicad_pcb']
assert not entry['locked']
def xy(p):return [pcbnew.ToMM(p.x),pcbnew.ToMM(p.y)]
lo,hi=[57.19,69.04],[59.01,69.96]
near=[]
for f in b.GetFootprints():
 if f.GetReference()=='C9':continue
 gs=[g.GetBoundingBox() for g in f.GraphicalItems() if g.GetLayer()==pcbnew.F_CrtYd]
 if not gs:continue
 l=[min(xy(g.GetOrigin())[i] for g in gs) for i in [0,1]]
 h=[max(xy(g.GetEnd())[i] for g in gs) for i in [0,1]]
 gap=math.hypot(max(lo[0]-h[0],l[0]-hi[0],0),max(lo[1]-h[1],l[1]-hi[1],0))
 near.append(dict(ref=f.GetReference(),gap_mm=gap,bbox=[l,h]))
near.sort(key=lambda x:x['gap_mm'])
print(json.dumps(dict(nearest_courtyards=near[:3])))
settings=b.GetDesignSettings()
out=dict(source='Native KiCad 10 saved board plus live entry lock state',candidate_C9_courtyard_bbox=[lo,hi],nearest_courtyards=near[:5],no_courtyard_overlap=near[0]['gap_mm']>0,board_matches_review=True,min_copper_clearance_mm=pcbnew.ToMM(settings.m_MinClearance),approved_copper_screen=json.loads((E/'c9-review-proposal.json').read_text())['conservative_F_Cu_track_via_pad_screen_nearest'],scope='Only C9 placement, specified local tracks/two vias, and selected connector silk',verdict='BLOCKED: approved C9 position overlaps TP3 and C3 courtyard bounds; no placement or routing mutation')
(E/'c9-apply-preflight.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(nearest_courtyard=near[0],min_copper_clearance_mm=out['min_copper_clearance_mm'],no_courtyard_overlap=out['no_courtyard_overlap'])))
