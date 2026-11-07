"""Review images from native exported polygons/tracks, never CAD sources."""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
E=Path(__file__).resolve().parent
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
colors={'PROG':'#a000b5','BATTERY':'#b57900','SW2':'#e00000','SW1':'#f04b00','BTST2':'#0872c9','BATP':'#008060','PGND':'#8ca98c','GND':'#546c54'}
def load(s):return json.loads((E/s).read_text())
def panel(g,layer,bounds,title):
 x0,y0,x1,y1=bounds;scale=62;w=round((x1-x0)*scale);h=round((y1-y0)*scale)
 im=Image.new('RGB',(w,h+60),'white');d=ImageDraw.Draw(im)
 def pt(a):return ((a[0]-x0)*scale,(a[1]-y0)*scale+50)
 for i in range(math.ceil(x0),math.floor(x1)+1):d.line([pt([i,y0]),pt([i,y1])],fill='#eeeeee')
 for j in range(math.ceil(y0),math.floor(y1)+1):d.line([pt([x0,j]),pt([x1,j])],fill='#eeeeee')
 for t in g['tracks']:
  if t['layer']!=layer or t['net']=='PROG':continue
  d.line([pt(t['start']),pt(t['end'])],fill=colors.get(t['net'],'#c0c0c0'),width=max(1,round(t['width']*scale)))
 for p in g['pads']:
  if not x0-2<p['xy'][0]<x1+2 or not y0-2<p['xy'][1]<y1+2:continue
  for q in p['polygons'].get(layer,[]):d.polygon([pt(a) for a in q],fill=colors.get(p['net'],'#cccccc'))
 for v in g['vias']:
  x,y=pt(v['xy']);r=v['widths'][layer]*scale/2
  d.ellipse([x-r,y-r,x+r,y+r],fill=colors.get(v['net'],'#bbbbbb'),outline='#777777')
  r=v['drill']*scale/2;d.ellipse([x-r,y-r,x+r,y+r],fill='white')
 for t in g['tracks']:
  if t['net']=='PROG' and t['layer']==layer:d.line([pt(t['start']),pt(t['end'])],fill=colors['PROG'],width=max(2,round(t['width']*scale)))
 for f in g['footprints']:
  if x0<f['xy'][0]<x1 and y0<f['xy'][1]<y1:d.text(pt(f['xy']),f['ref'],font=small,fill='black')
 d.rectangle([0,0,w,45],fill='white');d.text((10,8),title,font=font,fill='black')
 return im
long=load('phase4-7-layer-validation-scratch-geometry.json');short=load('phase4-7-layer-validation-shorter-scratch-geometry.json');prod=load('phase4-7-layer-validation-production-geometry.json')
bounds=(61,64,78,73)
panels=[panel(long,'F.Cu',bounds,'28.652 mm original proposal — F.Cu'),panel(short,'F.Cu',bounds,'14.199 mm comparison — F.Cu'),panel(short,'B.Cu',bounds,'14.199 mm comparison — B.Cu')]
canvas=Image.new('RGB',(panels[0].width, sum(p.height for p in panels)),'white');at=0
for im in panels:canvas.paste(im,(0,at));at+=im.height
canvas.save(E/'phase4-7-layer-validation-prog-review.png')
bounds=(62.3,64.2,65.5,68.2)
ps=[panel(prod,'F.Cu',bounds,'Production F.Cu'),panel(prod,'In2.Cu',bounds,'Production In2.Cu'),panel(short,'F.Cu',bounds,'Scratch F.Cu'),panel(short,'In2.Cu',bounds,'Scratch In2.Cu')]
canvas=Image.new('RGB',(ps[0].width*4,ps[0].height),'white')
for i,im in enumerate(ps):canvas.paste(im,(i*im.width,0))
canvas.save(E/'phase4-7-layer-validation-battery-review.png')
print('Saved two native-export geometry review images')
