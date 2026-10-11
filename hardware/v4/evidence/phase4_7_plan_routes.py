"""Offline conservative grid corridor planner; output requires scratch DRC."""
from pathlib import Path
import json,heapq,math,sys
import numpy as np
E=Path(__file__).resolve().parent;g=json.loads((E/'phase4-7-geometry.json').read_text());s=json.loads((E/'c9-apply-phase4-7-routing-entry-ipc.json').read_text())
tag=sys.argv[1]
for previous in sys.argv[2:]:
 p=json.loads((E/f'phase4-7-{previous}-plan.json').read_text())
 for n,l,w,x1,y1,x2,y2 in p['tracks']:g['tracks'].append(dict(net=n,layer=l,width=w,start=[x1,y1],end=[x2,y2]))
 for n,x,y,diam,dr in p['vias']:g['vias'].append(dict(net=n,xy=[x,y],width=diam,drill=dr))
step=.05;x0,y0=55,55;nx,ny=561,441
X,Y=np.meshgrid(x0+np.arange(nx)*step,y0+np.arange(ny)*step)
layers=['F.Cu','B.Cu'];newtracks=[];newvias=[];metrics=[]
padindex={(f['ref'],p['pin']):p for f in g['footprints'] for p in f['pads']}
def disk(cx,cy,r):return (X-cx)**2+(Y-cy)**2<=r*r
def line(a,b,r):
 vx,vy=b[0]-a[0],b[1]-a[1];den=vx*vx+vy*vy
 t=np.clip(((X-a[0])*vx+(Y-a[1])*vy)/den,0,1) if den else 0
 return (X-a[0]-t*vx)**2+(Y-a[1]-t*vy)**2<=r*r
def rect(a,b,r):return (X>=a[0]-r)&(X<=b[0]+r)&(Y>=a[1]-r)&(Y<=b[1]+r)
def masks(net):
 blocked=[np.zeros((ny,nx),bool) for _ in layers];vb=np.zeros((ny,nx),bool)
 for f in g['footprints']:
  for p in f['pads']:
   if p['net']==net:continue
   a,b=p['bbox'];vb|=rect(a,b,.401)
   ls=s['pads'][p['uuid']]['padStack']['layers']
   for i,l in enumerate(layers):
    if 'BL_'+l.replace('.','_') in ls:blocked[i]|=rect(a,b,.176)
 for t in g['tracks']:
  if t['net']==net:continue
  if t['layer'] in layers:blocked[layers.index(t['layer'])]|=line(t['start'],t['end'],t['width']/2+.176)
  vb|=line(t['start'],t['end'],t['width']/2+.401)
 for v in g['vias']:
  if v['net']==net:continue
  m=disk(*v['xy'],v['width']/2+.176)
  for b in blocked:b|=m
  vb|=disk(*v['xy'],v['width']/2+.401)
 # Hold the proposed C23 receiver-side pocket, without moving the actual part.
 reserve=rect([62.54,66.69],[63.46,68.51],.02)
 blocked[0]|=reserve;vb|=reserve
 return blocked,vb
def grid(p):return (round((p[0]-x0)/step),round((p[1]-y0)/step),0)
def point(n):return [round(x0+n[0]*step,6),round(y0+n[1]*step,6)]
def route(net,a,b):
 blocks,vblock=masks(net);start,end=grid(a),grid(b)
 assert not blocks[0][start[1],start[0]] and not blocks[0][end[1],end[0]],(net,'blocked endpoint',a,b)
 def heuristic(n):return math.hypot(n[0]-end[0],n[1]-end[1])
 q=[(heuristic(start),0,start)];cost={start:0};parents={};closed=set();moves=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
 while q:
  _,c,n=heapq.heappop(q)
  if n in closed:continue
  if n==end:break
  closed.add(n);x,y,l=n
  for dx,dy in moves:
   xx,yy=x+dx,y+dy
   if not 0<=xx<nx or not 0<=yy<ny or blocks[l][yy,xx]:continue
   if dx and dy and (blocks[l][y,xx] or blocks[l][yy,x]):continue
   nn=(xx,yy,l);cc=c+math.hypot(dx,dy)*(1 if l==0 else 1.2)
   if cc<cost.get(nn,1e20):cost[nn]=cc;parents[nn]=n;heapq.heappush(q,(cc+heuristic(nn),cc,nn))
  if not vblock[y,x] and not blocks[1-l][y,x]:
   nn=(x,y,1-l);cc=c+80
   if cc<cost.get(nn,1e20):cost[nn]=cc;parents[nn]=n;heapq.heappush(q,(cc+heuristic(nn),cc,nn))
 else:raise RuntimeError((net,'no corridor'))
 path=[end]
 while path[-1]!=start:path.append(parents[path[-1]])
 path.reverse();pts=[start]
 for i in range(1,len(path)-1):
  prev,n,nxt=path[i-1:i+2]
  if tuple(n[j]-prev[j] for j in range(3))!=tuple(nxt[j]-n[j] for j in range(3)):pts.append(n)
 pts.append(end)
 def addtrack(l,pa,pb):
  if pa==pb:return
  newtracks.append([net,l,.15,*pa,*pb]);g['tracks'].append(dict(net=net,layer=l,width=.15,start=pa,end=pb))
 addtrack('F.Cu',a,point(start))
 for u,v in zip(pts,pts[1:]):
  if u[2]!=v[2]:
   p=point(u);newvias.append([net,*p,.5,.3]);g['vias'].append(dict(net=net,xy=p,width=.5,drill=.3))
  else:addtrack(layers[u[2]],point(u),point(v))
 addtrack('F.Cu',point(end),b);metrics.append(dict(net=net,visited=len(closed),grid_cost=cost[end]));print(net,'path found',len(pts),flush=True)
def pair(n,r1,p1,r2,p2):route(n,padindex[r1,p1]['xy'],padindex[r2,p2]['xy'])
if tag=='batch2':
 pair('PROG','IC1','20','R5','1')
 pair('ILIM_HIZ','IC1','17','NT2','1')
 pair('TS','IC1','16','R6','2')
 pair('TS','R6','2','R7','2')
elif tag=='batch3':
 pair('REGN','C3','1','NT2','2')
 pair('REGN','NT2','2','R6','1')
 pair('REGN','R6','1','D3','2')
elif tag=='batch4':
 pair('CE_N','IC1','13','R9','1')
 pair('CE_N','R9','1','TP14','1')
 pair('CE_N','TP14','1','Q3','3')
 pair('CE_BIAS','R9','2','D4','1')
 pair('CE_BIAS','D4','1','D3','1')
else:raise ValueError(tag)
(E/f'phase4-7-{tag}-plan.json').write_text(json.dumps(dict(tracks=newtracks,vias=newvias,metrics=metrics),indent=2)+'\n')
print('plan',tag,'tracks',len(newtracks),'vias',len(newvias))
