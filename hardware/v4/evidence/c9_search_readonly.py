"""Find clearance-safe proposals, entirely in memory on accepted backup."""
import json,math,ast,sys
from pathlib import Path
sys.dont_write_bytecode=True
import pcbnew
E=Path(__file__).resolve().parent
tree=ast.parse((E/'analyze_c9_proposal.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['pd','sd','edges','rectseg']],type_ignores=[]),'<distance>','exec'))
d=json.loads((E/'c9-review-geometry.json').read_text());old=json.loads((E/'c9-review-proposal.json').read_text());rm=set(old['remove_track_ids']);rv=set(old['remove_via_ids'])
b=pcbnew.LoadBoard(str(E/'c9-apply-entry.kicad_pcb'));c=next(f for f in b.GetFootprints() if f.GetReference()=='C9')
others=[]
for f in b.GetFootprints():
 if f.GetReference()=='C9':continue
 f.BuildCourtyardCaches();p=f.GetCourtyard(pcbnew.F_CrtYd)
 if p.OutlineCount():others.append((f.GetReference(),p))
ts=[t for t in d['tracks'] if t['uuid'] not in rm and t['layer']=='F.Cu' and min(t['start'][0],t['end'][0])<65 and max(t['start'][0],t['end'][0])>52 and min(t['start'][1],t['end'][1])<75 and max(t['start'][1],t['end'][1])>60]
vs=[v for v in d['vias'] if v['uuid'] not in rv and 52<v['xy'][0]<65 and 60<v['xy'][1]<75]
ps=[p for f in d['footprints'] if f['ref']!='C9' for p in f['pads'] if 'F.Cu' in p['layers'] and 52<p['xy'][0]<65 and 60<p['xy'][1]<75]
def gap(net,lo,hi):
 vals=[]
 for p in ps:
  if p['net']==net:continue
  l,h=p['bbox'];v=math.hypot(max(lo[0]-h[0],l[0]-hi[0],0),max(lo[1]-h[1],l[1]-hi[1],0));vals.append(v)
  if v<.2:return v
 for v in vs:
  if v['net']==net:continue
  z=rectseg(lo,hi,v['xy'],v['xy'])-v['diameter']/2;vals.append(z)
  if z<.2:return z
 for t in ts:
  if t['net']==net:continue
  z=rectseg(lo,hi,t['start'],t['end'])-t['width']/2;vals.append(z)
  if z<.2:return z
 return min(vals)
found=[]
for angle in [0,180,90,270]:
 rad=math.radians(angle)
 for xi in range(535,636):
  x=xi/10
  for yi in range(620,741):
   y=yi/10
   if math.dist([x,y],[54.2,67.5])<.5:continue
   pads=[];gaps=[]
   for sign,net in [(-1,'VIN1'),(1,'PGND')]:
    pt=[x+sign*.48*math.cos(rad),y-sign*.48*math.sin(rad)]
    hw,hh=(.28,.31) if angle in [0,180] else (.31,.28)
    z=gap(net,[pt[0]-hw,pt[1]-hh],[pt[0]+hw,pt[1]+hh]);gaps.append(z);pads.append(pt)
    if z<.2:break
   if len(gaps)<2 or min(gaps)<.2:continue
   c.SetOrientationDegrees(angle);c.SetPosition(pcbnew.VECTOR2I(round(x*1e6),round(y*1e6)));c.BuildCourtyardCaches();court=c.GetCourtyard(pcbnew.F_CrtYd)
   if any(court.Collide(p,pcbnew.FromMM(.05)) for ref,p in others):continue
   gv=min((math.dist(pads[1],v['xy']),v['xy']) for v in vs if v['net']=='PGND')
   score=math.dist(pads[0],[58.6,67.85])+gv[0]
   found.append({'xy':[x,y],'angle':angle,'pads':pads,'pad_clearance_mm':min(gaps),'nearest_ground_via':gv,'score':score})
found.sort(key=lambda r:r['score']);(E/'c9-search-candidates.json').write_text(json.dumps(found,indent=2)+'\n');print(json.dumps({'count':len(found),'best':found[:12]}))
