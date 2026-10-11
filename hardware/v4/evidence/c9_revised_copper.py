"""Conservative all-board copper screen using accepted native geometry export."""
from pathlib import Path
import json,math,ast
E=Path(__file__).resolve().parent
# Reuse geometry-distance definitions only; do not execute previous proposal writer.
tree=ast.parse((E/'analyze_c9_proposal.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['pd','sd','edges','rectseg']],type_ignores=[]),'<geometry-functions>','exec'))
d=json.loads((E/'c9-review-geometry.json').read_text());old=json.loads((E/'c9-review-proposal.json').read_text())
remove=set(old['remove_track_ids'])-{'00bf05f3-44d1-4569-b8ea-1840314bb615','cb2ffaa5-e463-4060-b2b2-8109ec0dbb82'};rv=set(old['remove_via_ids'])
segments=[('VIN1',[60.62,69.1],[59.7,69.4],.2),('PGND',[61.58,69.1],[61.9,69.1],.3)]
# VAC1 escape retained through (58.4,68.8); source via retained at (59.7,69.4).
# Use an orthogonal VAC1 branch avoiding the ground via at (59,68.6).
newvia=('PGND',[61.9,69.1],.7,.3)
pads=[('VIN1',[60.34,68.79],[60.90,69.41]),('PGND',[61.30,68.79],[61.86,69.41])]
checks=[]
for net,a,b,w in segments:
 for t in d['tracks']:
  if t['uuid'] in remove or t['layer']!='F.Cu' or t['net']==net:continue
  checks.append((sd(a,b,t['start'],t['end'])-(w+t['width'])/2,'segment-track',t['uuid']))
 for v in d['vias']:
  if v['net']==net or v['uuid'] in rv:continue
  checks.append((pd(v['xy'],a,b)-(w+v['diameter'])/2,'segment-via',v['uuid']))
 for f in d['footprints']:
  if f['ref']=='C9':continue
  for p in f['pads']:
   if p['net']==net or 'F.Cu' not in p['layers']:continue
   checks.append((rectseg(*p['bbox'],a,b)-w/2,'segment-pad',f['ref']+'.'+p['pin']))
for net,lo,hi in pads:
 for f in d['footprints']:
  if f['ref']=='C9':continue
  for p in f['pads']:
   if p['net']==net or 'F.Cu' not in p['layers']:continue
   l,h=p['bbox'];checks.append((math.hypot(max(lo[0]-h[0],l[0]-hi[0],0),max(lo[1]-h[1],l[1]-hi[1],0)),'pad-pad',f['ref']+'.'+p['pin']))
 for t in d['tracks']:
  if t['uuid'] in remove or t['layer']!='F.Cu' or t['net']==net:continue
  checks.append((rectseg(lo,hi,t['start'],t['end'])-t['width']/2,'pad-track',t['uuid']))
 for v in d['vias']:
  if v['net']==net or v['uuid'] in rv:continue
  checks.append((rectseg(lo,hi,v['xy'],v['xy'])-v['diameter']/2,'pad-via',v['uuid']))
net,pt,dia,drill=newvia
for t in d['tracks']:
 if t['uuid'] in remove or t['net']==net:continue
 checks.append((pd(pt,t['start'],t['end'])-(dia+t['width'])/2,'new-via-track-all-layers',t['uuid']))
for v in d['vias']:
 if v['uuid'] in rv or v['net']==net:continue
 checks.append((math.dist(pt,v['xy'])-(dia+v['diameter'])/2,'new-via-via',v['uuid']))
for f in d['footprints']:
 if f['ref']=='C9':continue
 for p in f['pads']:
  if p['net']==net or not any(l.endswith('.Cu') for l in p['layers']):continue
  checks.append((rectseg(*p['bbox'],pt,pt)-dia/2,'new-via-pad-all-layers',f['ref']+'.'+p['pin']))
for n,a,b,w in segments:
 if n!=net:checks.append((pd(pt,a,b)-(dia+w)/2,'new-via-new-track','VIN1'))
for n,lo,hi in pads:
 if n!=net:checks.append((rectseg(lo,hi,pt,pt)-dia/2,'new-via-new-pad','VIN1'))
for i,(n,a,b,w) in enumerate(segments):
 for m,c,e,z in segments[i+1:]:
  if n!=m:checks.append((sd(a,b,c,e)-(w+z)/2,'new-track-new-track',''))
 for m,lo,hi in pads:
  if n!=m:checks.append((rectseg(lo,hi,a,b)-w/2,'new-track-new-pad',''))
source=('VIN1',[59.7,69.4],[60.5,69.4],.2)
# Short replacement In2 source branch: screen all cross-net In2 copper and vias.
net,a,b,w=source
for t in d['tracks']:
 if t['uuid'] in remove or t['net']==net or t['layer']!='In2.Cu':continue
 checks.append((sd(a,b,t['start'],t['end'])-(w+t['width'])/2,'source-In2-track',t['uuid']))
for v in d['vias']:
 if v['uuid'] in rv or v['net']==net:continue
 checks.append((pd(v['xy'],a,b)-(w+v['diameter'])/2,'source-In2-via',v['uuid']))
out={'segments':segments,'source_In2_segment':source,'new_PGND_via':newvia,'nearest_clearances_mm':sorted(checks)[:12],'screen_pass_0p2_mm':min(x[0] for x in checks)>=.2,'C9_to_VAC1_mm':math.dist([60.62,69.1],[59.7,69.4])+1.1+math.hypot(.2,.6)+.75+math.hypot(.2,.2),'ground_escape_mm':.32,'remove_tracks':sorted(remove),'remove_vias':sorted(rv),'expected_counts':{'footprints':154,'tracks':240,'vias':134},'notes':'Conservative pad bounding boxes; all existing tracks, vias, pads screened, proposed cross-net geometry included. Via all layers checked. PGND is the sole copper zone; RF keepout must be separately unchanged.'}
(E/'c9-revised-copper.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['nearest_clearances_mm','screen_pass_0p2_mm','C9_to_VAC1_mm','ground_escape_mm']}))
