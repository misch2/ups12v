"""Scratch-only KiCad geometry and candidate routing, based on accepted Batch 1."""
from pathlib import Path
import sys,json,hashlib,shutil
sys.dont_write_bytecode=True
import pcbnew as p
E=Path(__file__).resolve().parent
B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
assert p.GetBuildVersion()=='10.0.7'
base=json.loads((E/'c9-apply-phase4-7-batch1-final-ipc.json').read_text())
h=hashlib.sha256(B.read_bytes()).hexdigest()
assert h==base['hashes'][B.name]
b=p.LoadBoard(str(B))
assert len([t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA)])==252
assert len([t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)])==138
def xy(v):return [v.x/1e6,v.y/1e6]
def v(a):return p.VECTOR2I(*(round(x*1e6) for x in a))
c=next(f for f in b.GetFootprints() if f.GetReference()=='C23')
c.SetPosition(v([63,67.6])); assert c.GetOrientationDegrees()==90
geometry=[]
for f in b.GetFootprints():
 for pad in f.Pads():
  poly=p.SHAPE_POLY_SET()
  pad.TransformShapeToPolygon(poly,p.F_Cu,0,100,p.ERROR_OUTSIDE)
  outlines=[]
  for i in range(poly.OutlineCount()):
   outline=poly.COutline(i)
   outlines.append([xy(outline.CPoint(j)) for j in range(outline.PointCount())])
  geometry.append(dict(ref=f.GetReference(),pin=pad.GetNumber(),net=pad.GetNetname(),xy=xy(pad.GetPosition()),polygons=outlines))
(E/'phase4-7-c23-feasibility-pad-polygons.json').write_text(json.dumps(geometry))
if len(sys.argv)>1:
 plan=json.loads((E/'phase4-7-c23-feasibility-plan.json').read_text())
 for net,layer,width,x1,y1,x2,y2 in plan['tracks']:
  t=p.PCB_TRACK(b);t.SetStart(v([x1,y1]));t.SetEnd(v([x2,y2]));t.SetWidth(round(width*1e6));t.SetLayer(b.GetLayerID(layer));t.SetNetCode(b.FindNet(net).GetNetCode());b.Add(t)
 for net,x,y,diam,drill in plan['vias']:
  t=p.PCB_VIA(b);t.SetPosition(v([x,y]));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
  for layer in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:t.SetWidth(layer,round(diam*1e6))
  t.SetDrill(round(drill*1e6));t.SetNetCode(b.FindNet(net).GetNetCode());b.Add(t)
target=E/'phase4-7-c23-feasibility-trial.kicad_pcb'
p.SaveBoard(str(target),b)
shutil.copy2(B.with_suffix('.kicad_pro'),target.with_suffix('.kicad_pro'))
reloaded=p.LoadBoard(str(target))
assert xy(next(f for f in reloaded.GetFootprints() if f.GetReference()=='C23').GetPosition())==[63,67.6]
assert h==hashlib.sha256(B.read_bytes()).hexdigest()
print(json.dumps(dict(kicad=p.GetBuildVersion(),scratch=str(target),production_unchanged=True,pad_polygons=len(geometry))))
