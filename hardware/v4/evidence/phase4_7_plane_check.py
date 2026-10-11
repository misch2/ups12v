"""Read-only native filled-ground check along both scratch PROG candidates."""
from pathlib import Path
import sys,json,math
sys.dont_write_bytecode=True
import pcbnew as p
E=Path(__file__).resolve().parent
result={}
for tag in ['phase4-7-layer-validation','phase4-7-layer-validation-shorter']:
 b=p.LoadBoard(str(E/(tag+'.kicad_pcb')))
 ground=next(z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='PGND')
 fill=ground.GetFilledPolysList(p.In1_Cu)
 totals={}
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA) or t.GetNetname()!='PROG':continue
  a=t.GetStart();z=t.GetEnd();dx=(z.x-a.x)/1e6;dy=(z.y-a.y)/1e6;length=math.hypot(dx,dy)
  n=max(1,math.ceil(length/.02));ds=length/n
  r=totals.setdefault(b.GetLayerName(t.GetLayer()),dict(length_mm=0.,centre_without_In1_ground_mm=0.,corridor_0_3mm_not_fully_ground_mm=0.))
  r['length_mm']+=length
  for j in range(n):
   x=a.x/1e6+dx*(j+.5)/n;y=a.y/1e6+dy*(j+.5)/n
   tests=[fill.Contains(p.VECTOR2I(round((x-dy/length*d)*1e6),round((y+dx/length*d)*1e6))) for d in [0,-.3,.3]]
   if not tests[0]:r['centre_without_In1_ground_mm']+=ds
   if not all(tests):r['corridor_0_3mm_not_fully_ground_mm']+=ds
 result[tag]=totals
(E/'phase4-7-layer-validation-plane-screen.json').write_text(json.dumps(dict(method='Native filled In1 PGND Contains, midpoint sampling <=0.02mm, centre and +/-0.3mm offsets. Ground presence screen, not RF shielding/impedance simulation.',results=result),indent=2)+'\n')
print(json.dumps(result))
