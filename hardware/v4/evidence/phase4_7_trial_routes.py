"""Build scratch native board from an explicit routing plan; no live access."""
from pathlib import Path
import sys,json,hashlib,shutil
sys.dont_write_bytecode=True
import pcbnew
E=Path(__file__).resolve().parent;B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
assert pcbnew.GetBuildVersion().startswith('10.0.')
tag=sys.argv[1];plan=json.loads((E/f'phase4-7-{tag}-plan.json').read_text())
h=hashlib.sha256(B.read_bytes()).hexdigest();b=pcbnew.LoadBoard(str(B))
def v(x,y):return pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
for net,layer,width,x1,y1,x2,y2 in plan['tracks']:
 t=pcbnew.PCB_TRACK(b);t.SetStart(v(x1,y1));t.SetEnd(v(x2,y2));t.SetWidth(pcbnew.FromMM(width));t.SetLayer(b.GetLayerID(layer));t.SetNetCode(b.FindNet(net).GetNetCode());b.Add(t)
for net,x,y,diameter,drill in plan['vias']:
 t=pcbnew.PCB_VIA(b);t.SetPosition(v(x,y));t.SetViaType(pcbnew.VIATYPE_THROUGH);t.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu)
 for layer in [pcbnew.F_Cu,pcbnew.In1_Cu,pcbnew.In2_Cu,pcbnew.B_Cu]:t.SetWidth(layer,pcbnew.FromMM(diameter))
 t.SetDrill(pcbnew.FromMM(drill));t.SetNetCode(b.FindNet(net).GetNetCode());b.Add(t)
target=E/f'phase4-7-{tag}-trial.kicad_pcb';pcbnew.SaveBoard(str(target),b)
shutil.copy2(B.with_suffix('.kicad_pro'),target.with_suffix('.kicad_pro'))
assert h==hashlib.sha256(B.read_bytes()).hexdigest()
print(json.dumps(dict(scratch=str(target),added_tracks=len(plan['tracks']),added_vias=len(plan['vias']),production_hash_unchanged=True)))
