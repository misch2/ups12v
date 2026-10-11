"""Analysis of native exported copper; no CAD writes. Distances in mm."""
from pathlib import Path
import json,math
import numpy as np
E=Path(__file__).resolve().parent
def load(n):return json.loads((E/n).read_text())
def pointseg(x,a,b):
 a=np.asarray(a);b=np.asarray(b);v=b-a;d=np.dot(v,v)
 f=np.clip(np.sum((x-a)*v,axis=-1)/d,0,1) if d else np.zeros(x.shape[:-1])
 return np.linalg.norm(x-a-f[...,None]*v,axis=-1)
def polydist(x,q):
 inside=np.zeros(x.shape[:-1],bool);d=np.full(x.shape[:-1],np.inf)
 for a,b in zip(q,q[1:]+q[:1]):
  if a[1]!=b[1]:inside^=((a[1]>x[...,1])!=(b[1]>x[...,1]))&(x[...,0]<(b[0]-a[0])*(x[...,1]-a[1])/(b[1]-a[1])+a[0])
  d=np.minimum(d,pointseg(x,a,b))
 return np.where(inside,0,d)
def samples(t,step=.01):
 a=np.array(t['start']);b=np.array(t['end']);length=np.linalg.norm(b-a);n=max(1,math.ceil(length/step))
 return a+(b-a)*((np.arange(n)+.5)/n)[:,None],length/n
def exposure(g,prog_layer=None):
 prog=[t for t in g['tracks'] if t['net']=='PROG' and (prog_layer is None or t['layer']==prog_layer)];out={}
 for net in ['SW1','SW2','BTST1','BTST2','PMID','SYS','BATTERY','REGN']:
  bylayer={}
  for layer in ['F.Cu','In1.Cu','In2.Cu','B.Cu']:
   copper=[t for t in g['tracks'] if t['net']==net and t['layer']==layer]
   pads=[q for p in g['pads'] if p['net']==net for q in p['polygons'].get(layer,[])]
   vias=[v for v in g['vias'] if v['net']==net and layer in v['widths']]
   if not copper and not pads and not vias:continue
   gap=np.inf;close05=close1=parallel05=cross=0.;near=None
   for t in prog:
    x,ds=samples(t);d=np.full(len(x),np.inf);par=np.full(len(x),np.inf)
    v=np.array(t['end'])-t['start'];v=v/np.linalg.norm(v)
    for c in copper:
     cc=pointseg(x,c['start'],c['end'])-c['width']/2-t['width']/2;d=np.minimum(d,cc)
     w=np.array(c['end'])-c['start'];den=np.linalg.norm(w)
     if den and abs(np.dot(v,w/den))>=math.cos(math.radians(15)):par=np.minimum(par,cc)
    for q in pads:d=np.minimum(d,polydist(x,q)-t['width']/2)
    for c in vias:d=np.minimum(d,np.linalg.norm(x-c['xy'],axis=-1)-c['widths'][layer]/2-t['width']/2)
    j=int(d.argmin())
    if d[j]<gap:gap=float(d[j]);near=dict(prog_layer=t['layer'],point=x[j].tolist())
    close05+=float(np.sum(d<.5)*ds);close1+=float(np.sum(d<1)*ds);parallel05+=float(np.sum(par<.5)*ds);cross+=float(np.sum(d<0)*ds)
   bylayer[layer]=dict(min_projected_edge_gap_mm=gap,nearest=near,length_with_projected_gap_under_0_5_mm=close05,length_with_projected_gap_under_1_mm=close1,parallel_track_exposure_under_0_5_mm=parallel05,projected_copper_overlap_length_mm=cross)
  out[net]=bylayer
 return out
production=load('phase4-7-layer-validation-production-geometry.json')
long=load('phase4-7-layer-validation-scratch-geometry.json');short=load('phase4-7-layer-validation-shorter-scratch-geometry.json')
moved=next(t for t in long['tracks'] if t['uuid']=='01ab1eb5-ab75-462d-9e54-2d6eab529481')
step=.0025;X,Y=np.meshgrid(np.arange(62.75,64.2,step)+step/2,np.arange(65.15,67.3,step)+step/2);pts=np.stack([X,Y],axis=-1)
mask=pointseg(pts,moved['start'],moved['end'])<=moved['width']/2
holes=np.zeros(X.shape,bool)
for v in production['vias']:
 holes|=np.linalg.norm(pts-v['xy'],axis=-1)<v['drill']/2
mask&=~holes
def battery_mask(layer):
 result=np.zeros(X.shape,bool)
 for t in production['tracks']:
  if t['net']=='BATTERY' and t['layer']==layer and t['uuid']!=moved['uuid']:result|=pointseg(pts,t['start'],t['end'])<=t['width']/2
 for v in production['vias']:
  if v['net']=='BATTERY':result|=np.linalg.norm(pts-v['xy'],axis=-1)<=v['widths'][layer]/2
 return result&~holes
inner=battery_mask('In2.Cu');front=battery_mask('F.Cu')
area=dict(grid_mm=step,moved_capsule_area_mm2=float(mask.sum()*step**2),overlap_existing_In2_mm2=float((mask&inner).sum()*step**2),added_unique_In2_area_mm2=float((mask&~inner).sum()*step**2),removed_unique_F_Cu_area_mm2=float((mask&~front).sum()*step**2))
out=dict(method='Native exported polygons; 0.01mm midpoint arclength sampling; projected distances across layers are not DRC clearances or field-solver coupling. Parallel means within 15 degrees; 0.5/1mm are comparison bins, not acceptance limits.',long_PROG=exposure(long),short_PROG=exposure(short),short_PROG_F_Cu=exposure(short,'F.Cu'),short_PROG_B_Cu=exposure(short,'B.Cu'),battery_area=area)
(E/'phase4-7-layer-validation-electrical-geometry.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'battery_area':area,'long_SW2':out['long_PROG']['SW2'],'short_SW2':out['short_PROG']['SW2'],'long_BTST2':out['long_PROG']['BTST2'],'short_BTST2':out['short_PROG']['BTST2']}))
