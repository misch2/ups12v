"""Geometric proposal calculations only; no CAD objects edited."""
from pathlib import Path
import json,math,hashlib
E=Path(__file__).resolve().parent
d=json.loads((E/'c9-review-geometry.json').read_text())
def pd(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
 t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
 return math.dist(p,[a[0]+t*dx,a[1]+t*dy])
def sd(a,b,c,e):
 def cross(p,q,r):return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
 if cross(a,b,c)*cross(a,b,e)<0 and cross(c,e,a)*cross(c,e,b)<0:return 0
 return min(pd(a,c,e),pd(b,c,e),pd(c,a,b),pd(e,a,b))
def edges(lo,hi):
 p=[lo,[hi[0],lo[1]],hi,[lo[0],hi[1]]];return [(p[i],p[(i+1)%4]) for i in range(4)]
def rectseg(lo,hi,a,b):
 if any(lo[0]<=p[0]<=hi[0] and lo[1]<=p[1]<=hi[1] for p in [a,b]):return 0
 return min(sd(a,b,c,e) for c,e in edges(lo,hi))
remove_tracks={'022cc896-5315-4378-8593-df2c22644bd7','d6de5254-ca1a-4eed-a4da-4b6e0445d05c','ae6b4623-5619-43c3-8785-7f2a64fd6495','ebab4d13-9849-4343-bd89-f27a215fb486','cb2ffaa5-e463-4060-b2b2-8109ec0dbb82','00bf05f3-44d1-4569-b8ea-1840314bb615','9c77d608-5111-4702-acbb-9a9396bbec1b','2ebd5da6-d7a8-48c0-b454-46176d771dc1'}
segments=[('VIN1',[58.4,68.8],[58.58,69.5],.2),('VIN1',[58.58,69.5],[59.7,69.4],.2),('PGND',[57.62,69.5],[57.5,69.38],.3),('PGND',[57.5,69.38],[57.5,68.9],.3)]
pads=[('VIN1',[58.30,69.19],[58.86,69.81]),('PGND',[57.34,69.19],[57.90,69.81])]
checks=[]
for net,a,b,w in segments:
 for t in d['tracks']:
  if t['uuid'] in remove_tracks or t['layer']!='F.Cu' or t['net']==net:continue
  checks.append((sd(a,b,t['start'],t['end'])-(w+t['width'])/2,'track',t['uuid']))
 for v in d['vias']:
  if v['net']==net or v['uuid']=='df47ff83-e07c-4d1e-8e13-62d6f5fe2c06':continue
  checks.append((pd(v['xy'],a,b)-(w+v['diameter'])/2,'via',v['uuid']))
 for f in d['footprints']:
  if f['ref']=='C9':continue
  for p in f['pads']:
   if p['net']==net or 'F.Cu' not in p['layers']:continue
   checks.append((rectseg(*p['bbox'],a,b)-w/2,'pad',f['ref']+'.'+p['pin']))
for net,lo,hi in pads:
 for f in d['footprints']:
  if f['ref']=='C9':continue
  for p in f['pads']:
   if p['net']==net or 'F.Cu' not in p['layers']:continue
   l,h=p['bbox'];gap=math.hypot(max(lo[0]-h[0],l[0]-hi[0],0),max(lo[1]-h[1],l[1]-hi[1],0))
   checks.append((gap,'pad-to-pad-bounds',f['ref']+'.'+p['pin']))
 for t in d['tracks']:
  if t['uuid'] in remove_tracks or t['layer']!='F.Cu' or t['net']==net:continue
  checks.append((rectseg(lo,hi,t['start'],t['end'])-t['width']/2,'pad-to-track',t['uuid']))
 for v in d['vias']:
  if v['net']==net or v['uuid']=='df47ff83-e07c-4d1e-8e13-62d6f5fe2c06':continue
  checks.append((rectseg(lo,hi,v['xy'],v['xy'])-v['diameter']/2,'pad-to-via',v['uuid']))
old=2.12+1+5.5+8.9+4.6+1.9+math.hypot(.2,.6)+.75+math.hypot(.2,.2)
poly=next(z for z in json.loads((E/'c9-review-live-parity.json').read_text())['zones'] if z['name']=='V4_PGND_REFERENCE')['filledPolygons'][0]['shapes']['polygons'][0]
def nodes(r):return [(int(n['point']['xNm'])/1e6,int(n['point']['yNm'])/1e6) for n in r['nodes']]
def inside(p,ring):
 res=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:res=not res
 return res
def copper(p):return inside(p,nodes(poly['outline'])) and not any(inside(p,nodes(h)) for h in poly.get('holes',[]))
plane={str(p):copper(p) for p in [[57.62,69.5],[57.5,68.9],[59,68.6],[55,74]]}
unchanged={p:hashlib.sha256((E.parent/p).read_bytes()).hexdigest()==h for p,h in d['hashes'].items()}
out=dict(old_C9_to_VAC1_mm=old,old_C9_ground_to_first_via_mm=.5+math.hypot(1.62,.35),proposed_C9=dict(x=58.1,y=69.5,angle=180,pad1=[58.58,69.5],pad2=[57.62,69.5]),proposed_C9_to_VAC1_mm=math.hypot(.2,.2)+.75+math.hypot(.18,.7),proposed_ground_to_via_mm=math.hypot(.12,.12)+.48,remove_track_ids=sorted(remove_tracks),remove_via_ids=['e987acc3-1d47-41e7-b722-e4dab811625d','df47ff83-e07c-4d1e-8e13-62d6f5fe2c06'],new_F_Cu_segments=segments,new_In2_Cu_segment=['VIN1',[59.7,69.4],[60.5,69.4],.2],conservative_F_Cu_track_via_pad_screen_nearest=sorted(checks)[:6],screen_limit='Bounding geometry only, no proposal DRC, no soldermask/courtyard or EM qualification',live_filled_plane_samples=plane,CAD_unchanged=unchanged)
(E/'c9-review-proposal.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k in ['old_C9_to_VAC1_mm','proposed_C9_to_VAC1_mm','conservative_F_Cu_track_via_pad_screen_nearest','live_filled_plane_samples','CAD_unchanged']}))
