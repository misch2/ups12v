"""Native scratch diagnostic: retain ALL production copper; add combined routes only."""
from pathlib import Path
import sys,json,hashlib,shutil
sys.dont_write_bytecode=True
import pcbnew as p
E=Path(__file__).resolve().parent;B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
base=json.loads((E/'c9-apply-phase4-7-prog-focused-entry-ipc.json').read_text())
def hashes():return {n:hashlib.sha256((B.parent/n).read_bytes()).hexdigest() for n in base['hashes']}
assert hashes()==base['hashes']
assert p.GetBuildVersion()=='10.0.7'
plan=json.loads((E/'phase4-7-prog-focused-0.1-0.01-omit-01ab1eb5-layer-model-front-only-plan.json').read_text())
assert plan['failure'] is None
b=p.LoadBoard(str(B))
def v(a):return p.VECTOR2I(*(round(x*1e6) for x in a))
for net,layer,width,x1,y1,x2,y2 in plan['tracks']:
 t=p.PCB_TRACK(b);t.SetStart(v([x1,y1]));t.SetEnd(v([x2,y2]));t.SetWidth(round(width*1e6));t.SetLayer(b.GetLayerID(layer));t.SetNetCode(b.FindNet(net).GetNetCode());b.Add(t)
for net,x,y,diam,drill in plan['vias']:
 t=p.PCB_VIA(b);t.SetPosition(v([x,y]));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
 for layer in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:t.SetWidth(layer,round(diam*1e6))
 t.SetDrill(round(drill*1e6));t.SetNetCode(b.FindNet(net).GetNetCode());b.Add(t)
target=E/'phase4-7-prog-focused-diagnostic.kicad_pcb'
assert not target.exists()
p.SaveBoard(str(target),b)
for ext in ['.kicad_pro','.kicad_sch']:shutil.copy2(B.with_suffix(ext),target.with_suffix(ext))
r=p.LoadBoard(str(target))
original=next(t for t in r.GetTracks() if t.m_Uuid.AsString()=='01ab1eb5-ab75-462d-9e54-2d6eab529481')
assert original.GetLayer()==p.F_Cu and original.GetWidth()==600000
assert hashes()==base['hashes']
print(json.dumps(dict(kicad=p.GetBuildVersion(),tracks=sum(not isinstance(t,p.PCB_VIA) for t in r.GetTracks()),vias=sum(isinstance(t,p.PCB_VIA) for t in r.GetTracks()),production_unchanged=True,existing_BATTERY_segment_preserved=True)))
