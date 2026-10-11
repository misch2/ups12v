"""Focused offline PROG search with accepted combined subset; no production writes."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
E=Path(__file__).resolve().parent
base=json.loads((E/'c9-apply-phase4-7-batch1-final-ipc.json').read_text())
entry=json.loads((E/'c9-apply-phase4-7-prog-focused-entry-ipc.json').read_text())
assert base==entry
width=float(sys.argv[1]);step=float(sys.argv[2]) if len(sys.argv)>2 else .025
prog_first='prog-first' in sys.argv
all_first='all-first' in sys.argv
signal_first='signal-first' in sys.argv
far_batp='far-batp' in sys.argv
omit=sys.argv[sys.argv.index('--omit')+1] if '--omit' in sys.argv else None
dogleg='dogleg' in sys.argv
shift='shift' in sys.argv
layer_model='layer-model' in sys.argv
front_only='front-only' in sys.argv
assert width in [.15,.125,.1,.075]
src=(E/'phase4_7_local_plan.py').read_text().split("if tag in ['c23-270','original']:")[0]
src=src.replace('step=.025;x0,y0=55,55;nx,ny=1121,881',f'step={step};x0,y0=58,62;nx,ny={round(18/step)+1},{round(11/step)+1}')
src=src.replace('.176',str(.101+width/2)).replace('.326',str(.251+width/2))
src=src.replace("[net,l,.15,*a,*b]",f"[net,l,{width},*a,*b]").replace('width=.15',f'width={width}')
src=src.replace("front=[n for n in closed if n[2]==0]", "globals()['reached']=closed;front=[n for n in closed if n[2]==0]")
if far_batp:src=src.replace('return blocks,vb', "\n if net=='BATP':vb|=(X<63.1)&(Y<68.6)\n return blocks,vb")
if front_only:src=src.replace('return blocks,vb', 'vb[:]=True;return blocks,vb')
sys.argv=['focused','original']
ns={'__file__':str(E/'phase4_7_local_plan.py')};exec(compile(src,'focused-search','exec'),ns)
if omit:
 index=list(ns['s']['tracks']).index(omit)
 ns['ts'].pop(index)
 if layer_model:ns['ts'].append(dict(net='BATTERY',layer='In2.Cu',width=.6,start=[63.1,65.5],end=[63.8,66.9]))
 if dogleg:
  for a,b in [([63.1,65.5],[64.0,65.5]),([64.0,65.5],[64.0,66.7]),([64.0,66.7],[63.8,66.9])]:
   ns['ts'].append(dict(net='BATTERY',layer='F.Cu',width=.6,start=a,end=b))
if shift:
 for v in ns['vs']:
  if v['net']=='BATTERY' and v['xy']==[63.8,66.9]:v['xy']=[64.1,66.9]
 for t in ns['ts']:
  for key in ['start','end']:
   if t[key]==[63.8,66.9]:t[key]=[64.1,66.9]
 ns['ts'].extend([dict(net='BATTERY',layer='F.Cu',width=.6,start=[63.1,65.5],end=[64.1,65.5]),dict(net='BATTERY',layer='F.Cu',width=.6,start=[64.1,65.5],end=[64.1,66.9])])
subset=json.loads((E/'phase4-7-original-partial-clean-plan.json').read_text())
if prog_first:
 subset['tracks']=[t for t in subset['tracks'] if t[0]!='BATP']
if all_first or signal_first or far_batp:subset['tracks']=[t for t in subset['tracks'] if t[0]=='PGND']
for net,layer,w,x1,y1,x2,y2 in subset['tracks']:
 ns['ts'].append(dict(net=net,layer=layer,width=w,start=[x1,y1],end=[x2,y2]))
for net,x,y,d,h in subset['vias']:
 ns['vs'].append(dict(net=net,xy=[x,y],width=d,drill=h))
ns['tag']=f'prog-focused-{width}-{step}'
if prog_first:ns['tag']+='-prog-first'
if all_first:ns['tag']+='-all-first'
if signal_first:ns['tag']+='-signal-first'
if far_batp:ns['tag']+='-far-batp'
if omit:ns['tag']+='-omit-'+omit[:8]
if dogleg:ns['tag']+='-dogleg-model'
if shift:ns['tag']+='-shift-model'
if layer_model:ns['tag']+='-layer-model'
if front_only:ns['tag']+='-front-only'
failure=None
try:
 ns['route']('PROG',ns['pad']('IC1','20'),ns['pad']('R5','1'))
 if signal_first:
  ns['route']('ILIM_HIZ',ns['pad']('IC1','17'),ns['pad']('NT2','1'))
  ns['route']('TS',ns['pad']('IC1','16'),ns['pad']('R6','2'))
 if prog_first or all_first or signal_first or far_batp:
  ns['route']('BATP',ns['pad']('IC1','18'),ns['pad']('C23','1'))
  ns['route']('BATP',ns['pad']('C23','1'),ns['pad']('R4','1'))
 if all_first or far_batp:
  ns['route']('ILIM_HIZ',ns['pad']('IC1','17'),ns['pad']('NT2','1'))
  ns['route']('TS',ns['pad']('IC1','16'),ns['pad']('R6','2'))
except (RuntimeError,AssertionError) as ex:failure=str(ex)
out=dict(width_mm=width,step_mm=step,tracks=subset['tracks']+ns['newtracks'],vias=subset['vias']+ns['newvias'],prog_tracks=ns['newtracks'],prog_vias=ns['newvias'],metrics=ns['metrics'],failure=failure,baseline_exact_match=True)
(E/f'phase4-7-{ns["tag"]}-plan.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['width_mm','step_mm','prog_tracks','prog_vias','failure','baseline_exact_match']}))
if failure and 'reached' in ns:
 import numpy as np
 front=[n for n in ns['reached'] if n[2]==0]
 ns['X']=np.array([[ns['point'](n)[0] for n in front]])
 ns['Y']=np.array([[ns['point'](n)[1] for n in front]])
 blockers=[]
 def record(obj,mask):
  if mask.any():blockers.append((obj,mask.ravel()))
 for pad in ns['g']:
  if pad['net']=='PROG':continue
  mask=np.zeros(ns['X'].shape,bool)
  for polys in pad['polygons'].values():
   for q in polys:
    # Native polygon distance, evaluated without rectangular grid cropping.
    inside=np.zeros(ns['X'].shape,bool);edge=inside.copy()
    for a,b in zip(q,q[1:]+q[:1]):
     if a[1]!=b[1]:inside^=((a[1]>ns['Y'])!=(b[1]>ns['Y']))&(ns['X']<(b[0]-a[0])*(ns['Y']-a[1])/(b[1]-a[1])+a[0])
     edge|=ns['line'](a,b,.401)
    mask|=inside|edge
  record(dict(kind='pad',ref=pad['ref'],pin=pad['pin'],net=pad['net'],xy=pad['xy']),mask)
 for i,t in enumerate(ns['ts']):
  if t['net']=='PROG':continue
  record(dict(kind='track',**t,uuid=list(ns['s']['tracks'])[i] if i<len(ns['s']['tracks']) else 'scratch'),ns['line'](t['start'],t['end'],t['width']/2+.401))
 for i,v in enumerate(ns['vs']):
  if v['net']=='PROG':continue
  record(dict(kind='via',**v,uuid=list(ns['s']['vias'])[i] if i<len(ns['s']['vias']) else 'scratch'),ns['line'](v['xy'],v['xy'],max(v['width']/2+.401,v['drill']/2+.501)))
 counts=np.sum([m for _,m in blockers],axis=0)
 best=np.where(counts==counts.min())[0]
 candidates=[]
 for j in best:
  candidates.append(dict(xy=ns['point'](front[j]),blockers=[o for o,m in blockers if m[j]]))
 result=dict(minimum_blocker_count=int(counts.min()),candidate_count=len(best),candidates=candidates)
 (E/f'phase4-7-{ns["tag"]}-via-blockers.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(minimum_via_blockers=int(counts.min()),candidate_count=len(best),examples=candidates[:3])))
