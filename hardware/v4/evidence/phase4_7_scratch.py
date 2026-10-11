"""Bounded native scratch build; production is never saved or overwritten."""
from pathlib import Path
import sys,json,hashlib,shutil
sys.dont_write_bytecode=True
import pcbnew as p
E=Path(__file__).resolve().parent;B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
tag=sys.argv[1];mode=sys.argv[2]
assert tag in ['c23-270','original','local2','local3']
assert p.GetBuildVersion()=='10.0.7'
entry=json.loads((E/f'c9-apply-phase4-7-{tag}-entry-ipc.json').read_text())
hashes={n:hashlib.sha256((B.parent/n).read_bytes()).hexdigest() for n in entry['hashes']}
assert hashes==entry['hashes']
b=p.LoadBoard(str(B));c=next(f for f in b.GetFootprints() if f.GetReference()=='C23')
def v(a):return p.VECTOR2I(*(round(x*1e6) for x in a))
def xy(a):return [a.x/1e6,a.y/1e6]
if tag=='c23-270':c.SetPosition(v([63,67.6]));c.SetOrientationDegrees(270)
if mode=='geometry':
 rows=[]
 for f in b.GetFootprints():
  for pad in f.Pads():
   polygons={}
   for layer in [p.F_Cu,p.B_Cu]:
    if not pad.IsOnLayer(layer):continue
    poly=p.SHAPE_POLY_SET();pad.TransformShapeToPolygon(poly,layer,0,100,p.ERROR_OUTSIDE)
    outlines=[]
    for i in range(poly.OutlineCount()):
     outline=poly.COutline(i);outlines.append([xy(outline.CPoint(j)) for j in range(outline.PointCount())])
    polygons[b.GetLayerName(layer)]=outlines
   rows.append(dict(ref=f.GetReference(),pin=pad.GetNumber(),net=pad.GetNetname(),xy=xy(pad.GetPosition()),polygons=polygons))
 (E/f'phase4-7-{tag}-pad-polygons.json').write_text(json.dumps(rows))
elif mode=='routes':
 plan=json.loads((E/f'phase4-7-{tag}-plan.json').read_text())
 for net,layer,width,x1,y1,x2,y2 in plan['tracks']:
  t=p.PCB_TRACK(b);t.SetStart(v([x1,y1]));t.SetEnd(v([x2,y2]));t.SetWidth(round(width*1e6));t.SetLayer(b.GetLayerID(layer));t.SetNetCode(b.FindNet(net).GetNetCode());b.Add(t)
 for net,x,y,diam,drill in plan['vias']:
  t=p.PCB_VIA(b);t.SetPosition(v([x,y]));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
  for layer in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:t.SetWidth(layer,round(diam*1e6))
  t.SetDrill(round(drill*1e6));t.SetNetCode(b.FindNet(net).GetNetCode());b.Add(t)
else:raise ValueError(mode)
target=E/f'phase4-7-{tag}-trial.kicad_pcb'
p.SaveBoard(str(target),b)
for ext in ['.kicad_pro','.kicad_sch']:shutil.copy2(B.with_suffix(ext),target.with_suffix(ext))
r=p.LoadBoard(str(target));rc=next(f for f in r.GetFootprints() if f.GetReference()=='C23')
assert xy(rc.GetPosition())==xy(c.GetPosition()) and rc.GetOrientationDegrees()==c.GetOrientationDegrees()
assert hashes=={n:hashlib.sha256((B.parent/n).read_bytes()).hexdigest() for n in hashes}
print(json.dumps(dict(tag=tag,mode=mode,kicad=p.GetBuildVersion(),C23=xy(rc.GetPosition()),rotation=rc.GetOrientationDegrees(),tracks=sum(not isinstance(t,p.PCB_VIA) for t in r.GetTracks()),vias=sum(isinstance(t,p.PCB_VIA) for t in r.GetTracks()),production_unchanged=True)))
