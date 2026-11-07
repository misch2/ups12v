"""Offline two-layer routing candidate from native pad polygons and latest IPC copper."""
from pathlib import Path
import sys,json,heapq,math
import numpy as np
E=Path(__file__).resolve().parent
g=json.loads((E/'phase4-7-c23-feasibility-pad-polygons.json').read_text())
s=json.loads((E/'c9-apply-phase4-7-c23-feasibility-entry-ipc.json').read_text())
def xy(p):return [int(p.get(k+'Nm',0))/1e6 for k in ['x','y']]
ts=[dict(net=t['net']['name'],layer=t['layer'].removeprefix('BL_').replace('_','.'),width=int(t['width']['valueNm'])/1e6,start=xy(t['start']),end=xy(t['end'])) for t in s['tracks'].values()]
vs=[dict(net=t['net']['name'],xy=xy(t['position']),width=max(int(z['size']['xNm']) for z in t['padStack']['copperLayers'])/1e6) for t in s['vias'].values()]
step=.025;x0,y0=55,55;nx,ny=1121,881
X,Y=np.meshgrid(x0+np.arange(nx)*step,y0+np.arange(ny)*step)
layers=['F.Cu','B.Cu'];newtracks=[];newvias=[];metrics=[]
def line(a,b,r):
 vx,vy=b[0]-a[0],b[1]-a[1];den=vx*vx+vy*vy
 t=np.clip(((X-a[0])*vx+(Y-a[1])*vy)/den,0,1) if den else 0
 return (X-a[0]-t*vx)**2+(Y-a[1]-t*vy)**2<=r*r
def poly(q,r):
 global X,Y
 ox,oy=X,Y
 ix=max(0,int((min(a[0] for a in q)-r-x0)/step)-1);ex=min(nx,int((max(a[0] for a in q)+r-x0)/step)+2)
 iy=max(0,int((min(a[1] for a in q)-r-y0)/step)-1);ey=min(ny,int((max(a[1] for a in q)+r-y0)/step)+2)
 result=np.zeros(ox.shape,bool)
 if ix>=ex or iy>=ey:return result
 X,Y=ox[iy:ey,ix:ex],oy[iy:ey,ix:ex]
 inside=np.zeros(X.shape,bool);edge=inside.copy()
 for a,b in zip(q,q[1:]+q[:1]):
  if a[1]!=b[1]:inside^=((a[1]>Y)!=(b[1]>Y))&(X<(b[0]-a[0])*(Y-a[1])/(b[1]-a[1])+a[0])
  edge|=line(a,b,r)
 result[iy:ey,ix:ex]=inside|edge
 X,Y=ox,oy
 return result
def masks(net):
 blocks=[np.zeros(X.shape,bool) for _ in layers];vb=np.zeros(X.shape,bool)
 for p in g:
  if p['net']==net:continue
  for q in p['polygons']:
   blocks[0]|=poly(q,.176);vb|=poly(q,.351)
 for t in ts:
  if t['net']==net:continue
  if t['layer'] in layers:blocks[layers.index(t['layer'])]|=line(t['start'],t['end'],t['width']/2+.176)
  vb|=line(t['start'],t['end'],t['width']/2+.351)
 for v in vs:
  if v['net']==net:continue
  for z in blocks:z|=line(v['xy'],v['xy'],v['width']/2+.176)
  vb|=line(v['xy'],v['xy'],v['width']/2+.351)
 return blocks,vb
def grid(p):return (round((p[0]-x0)/step),round((p[1]-y0)/step),0)
def point(n):return [round(x0+n[0]*step,6),round(y0+n[1]*step,6)]
def route(net,a,b):
 blocks,vb=masks(net);start,end=grid(a),grid(b)
 assert not blocks[0][start[1],start[0]] and not blocks[0][end[1],end[0]],(net,'blocked endpoint')
 def heuristic(n):return math.hypot(n[0]-end[0],n[1]-end[1])
 q=[(heuristic(start),0,start)];cost={start:0};parents={};closed=set()
 while q:
  _,c,n=heapq.heappop(q)
  if n in closed:continue
  if n==end:break
  closed.add(n);x,y,l=n
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
   xx,yy=x+dx,y+dy
   if not 0<=xx<nx or not 0<=yy<ny or blocks[l][yy,xx]:continue
   if dx and dy and (blocks[l][y,xx] or blocks[l][yy,x]):continue
   nn=(xx,yy,l);cc=c+math.hypot(dx,dy)*(1 if l==0 else 1.15)
   if cc<cost.get(nn,1e20):cost[nn]=cc;parents[nn]=n;heapq.heappush(q,(cc+heuristic(nn),cc,nn))
  if not vb[y,x] and not blocks[1-l][y,x]:
   nn=(x,y,1-l);cc=c+100
   if cc<cost.get(nn,1e20):cost[nn]=cc;parents[nn]=n;heapq.heappush(q,(cc+heuristic(nn),cc,nn))
 else:raise RuntimeError((net,'no corridor',len(closed)))
 path=[end]
 while path[-1]!=start:path.append(parents[path[-1]])
 path.reverse();pts=[start]
 for i in range(1,len(path)-1):
  prev,n,nxt=path[i-1:i+2]
  if tuple(n[j]-prev[j] for j in range(3))!=tuple(nxt[j]-n[j] for j in range(3)):pts.append(n)
 pts.append(end)
 def add(l,a,b):
  if a==b:return
  newtracks.append([net,l,.15,*a,*b]);ts.append(dict(net=net,layer=l,width=.15,start=a,end=b))
 add('F.Cu',a,point(start))
 for u,v in zip(pts,pts[1:]):
  if u[2]!=v[2]:
   p=point(u);newvias.append([net,*p,.5,.3]);vs.append(dict(net=net,xy=p,width=.5))
  else:add(layers[u[2]],point(u),point(v))
 add('F.Cu',point(end),b)
 metrics.append(dict(net=net,visited=len(closed),cost=cost[end]))
 print(net,'candidate',len(pts),'vertices',flush=True)
def pad(r,p):return next(a['xy'] for a in g if a['ref']==r and a['pin']==p)
tasks=[('BATP',pad('IC1','18'),pad('C23','1')),('BATP',pad('C23','1'),pad('R4','1')),('PGND',pad('C23','2'),[61.9,69.1]),('ILIM_HIZ',pad('IC1','17'),pad('NT2','1')),('TS',pad('IC1','16'),pad('R6','2')),('PROG',pad('IC1','20'),pad('R5','1'))]
if len(sys.argv)>1 and sys.argv[1]=='ilim-first':tasks=tasks[3:4]+tasks[:3]+tasks[4:]
if len(sys.argv)>1 and sys.argv[1]=='pgnd-first':tasks=tasks[2:3]+tasks[:2]+tasks[3:]
failure=None
try:
 for args in tasks:route(*args)
except (RuntimeError,AssertionError) as ex:failure=str(ex);print('STOP CANDIDATE',failure,flush=True)
(E/'phase4-7-c23-feasibility-plan.json').write_text(json.dumps(dict(tracks=newtracks,vias=newvias,metrics=metrics,failure=failure),indent=2)+'\n')
