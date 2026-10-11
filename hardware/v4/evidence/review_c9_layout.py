"""Read-only KiCad API geometry capture; writes review evidence only."""
from pathlib import Path
import sys, json, hashlib, math
sys.dont_write_bytecode=True
import pcbnew
E=Path(__file__).resolve().parent
B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
paths=[B,B.with_suffix('.kicad_sch'),B.with_suffix('.kicad_pro')]
hashes={str(p.relative_to(E.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
b=pcbnew.LoadBoard(str(B))
def xy(v):return [round(pcbnew.ToMM(v.x),6),round(pcbnew.ToMM(v.y),6)]
def uid(o):return o.m_Uuid.AsString()
def tr(t):return dict(uuid=uid(t),net=t.GetNetname(),layer=b.GetLayerName(t.GetLayer()),start=xy(t.GetStart()),end=xy(t.GetEnd()),width=pcbnew.ToMM(t.GetWidth()))
def via(t):return dict(uuid=uid(t),net=t.GetNetname(),xy=xy(t.GetPosition()),diameter=pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu)),drill=pcbnew.ToMM(t.GetDrillValue()))
def pad(p):return dict(uuid=uid(p),pin=p.GetNumber(),net=p.GetNetname(),xy=xy(p.GetPosition()),size=xy(p.GetSize()),shape=int(p.GetShape()),bbox=[xy(p.GetBoundingBox().GetOrigin()),xy(p.GetBoundingBox().GetEnd())],layers=[b.GetLayerName(l) for l in p.GetLayerSet().Seq()])
tracks=[tr(t) for t in b.GetTracks() if not isinstance(t,pcbnew.PCB_VIA)]
vias=[via(t) for t in b.GetTracks() if isinstance(t,pcbnew.PCB_VIA)]
fps=[dict(ref=f.GetReference(),value=f.GetValue(),xy=xy(f.GetPosition()),angle=f.GetOrientationDegrees(),pads=[pad(p) for p in f.Pads()]) for f in b.GetFootprints()]
art=[]
for f in b.GetFootprints():
 if f.GetReference() not in ['J1','J2','J3','J8','J7']:continue
 for g in f.GraphicalItems():
  if g.GetLayer()!=pcbnew.F_SilkS:continue
  art.append(dict(ref=f.GetReference(),uuid=uid(g),kind=g.GetClass(),start=xy(g.GetStart()),end=xy(g.GetEnd()),width=pcbnew.ToMM(g.GetWidth())))
zones=[]
for z in b.Zones():
 zones.append(dict(uuid=uid(z),net=z.GetNetname(),layers=[b.GetLayerName(l) for l in z.GetLayerSet().Seq()],rule_area=z.GetIsRuleArea(),filled_polygons={b.GetLayerName(l):z.GetFilledPolysList(l).OutlineCount() for l in z.GetLayerSet().Seq()}))
out=dict(kicad=pcbnew.GetBuildVersion(),hashes=hashes,source='Saved pcbnew geometry; live corroboration stored separately',tracks=tracks,vias=vias,footprints=fps,connector_silk=art,zones=zones)
ground=next(z for z in b.Zones() if z.GetNetname()=='PGND' and not z.GetIsRuleArea())
points={'C9_old_ground':[54.68,67.5],'C9_proposed_ground':[57.62,69.5],'existing_local_ground_via':[57.5,68.9],'IC1_ground_via':[59,68.6],'sense_trunk':[55,74]}
out['In1_filled_contains']={n:ground.GetFilledPolysList(pcbnew.In1_Cu).Contains(pcbnew.VECTOR2I(round(x*1e6),round(y*1e6))) for n,(x,y) in points.items()}
out['C9_courtyard']=[dict(start=xy(g.GetStart()),end=xy(g.GetEnd())) for f in b.GetFootprints() if f.GetReference()=='C9' for g in f.GraphicalItems() if g.GetLayer()==pcbnew.F_CrtYd]
assert hashes=={str(p.relative_to(E.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(E/'c9-review-geometry.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(counts=dict(footprints=len(fps),tracks=len(tracks),vias=len(vias)),plane_samples=out['In1_filled_contains'],courtyard=out['C9_courtyard'])))
