"""Diagnostic layer plot from native geometry; no CAD writes."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
E=Path(__file__).resolve().parent
d=json.loads((E/'phase4-7-geometry.json').read_text())
fig,ax=plt.subplots(figsize=(15,10))
colors={'SW1':'#ef5b20','SW2':'#d10000','REGN':'#00a2a2','VIN1':'#b16ccd','PGND':'#6b986b','BATTERY':'#c09300'}
for t in d['tracks']:
 if t['layer']=='In1.Cu':continue
 ax.plot([t['start'][0],t['end'][0]],[t['start'][1],t['end'][1]],color=colors.get(t['net'],'#888888'),linewidth=t['width']*3,alpha=.75 if t['layer']=='F.Cu' else .35,linestyle='-' if t['layer']=='F.Cu' else '--')
for f in d['footprints']:
 if not 49<f['xy'][0]<83 or not 55<f['xy'][1]<78:continue
 for c in f['courtyard']:
  a,b=c['start'],c['end']
  if c['shape']=='1':ax.add_patch(Rectangle((min(a[0],b[0]),min(a[1],b[1])),abs(b[0]-a[0]),abs(b[1]-a[1]),fill=False,edgecolor='#aaaaaa',lw=.5))
  else:ax.plot([a[0],b[0]],[a[1],b[1]],color='#aaaaaa',lw=.5)
 for p in f['pads']:
  a,b=p['bbox']; ax.add_patch(Rectangle(a,b[0]-a[0],b[1]-a[1],facecolor=colors.get(p['net'],'#d5b5b5'),edgecolor='#555555',lw=.25))
 ax.text(*f['xy'],f['ref'],fontsize=8,ha='center',va='center')
for v in d['vias']:
 ax.add_patch(Circle(v['xy'],v['width']/2,facecolor=colors.get(v['net'],'#888888'),alpha=.6));ax.add_patch(Circle(v['xy'],v['drill']/2,facecolor='white'))
ax.set(xlim=(50,81),ylim=(77,55),xlabel='X mm',ylabel='Y mm',title='Phase 4.7 actual saved/native layout (live-matched)\nF.Cu solid; other routed layers dashed; pad bounding boxes, not custom-pad contours; fills omitted')
ax.set_aspect('equal');ax.grid(alpha=.2);fig.tight_layout();fig.savefig(E/'phase4-7-local-layout.png',dpi=170)
print('Saved diagnostic local layout plot')
