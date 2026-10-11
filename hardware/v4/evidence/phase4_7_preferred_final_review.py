"""Review exported toolkit JSON only; no KiCad imports, CAD access or mutation."""
from pathlib import Path
import collections
import json
import math
from PIL import Image, ImageDraw, ImageFont

E = Path(__file__).resolve().parent
R = E / 'phase4-7-preferred-final-validation'
g = json.loads((R / 'final-snapshot.json').read_text())
old = json.loads((E / 'phase4-7-layer-validation-shorter-scratch-geometry.json').read_text())

def track(t):
    return (t['net'], t['layer'], t['width'], tuple(t['start']), tuple(t['end']))

def via(v, historical=False):
    return (v['net'], tuple(v['xy' if historical else 'position']), v['drill'],
            tuple(sorted(v['widths' if historical else 'copper_widths'].items())))

assert collections.Counter(map(track, g['tracks'].values())) == collections.Counter(map(track, old['tracks']))
assert collections.Counter(via(v) for v in g['vias'].values()) == collections.Counter(via(v, True) for v in old['vias'])
prog = [t for t in g['tracks'].values() if t['net'] == 'PROG']
lengths = {layer: sum(math.dist(t['start'], t['end']) for t in prog if t['layer'] == layer)
           for layer in ['F.Cu', 'B.Cu']}
drc = json.loads((R / 'drc.json').read_text())
prior_drc = json.loads((E / 'phase4-7-layer-validation-shorter-drc.json').read_text())
warnings = lambda report: collections.Counter((v['type'], v['description']) for v in report['violations'] if v['severity'] == 'warning')
assert warnings(drc) == warnings(prior_drc)
result = dict(exact_prior_track_via_geometry=True, identical_prior_drc_warnings=True,
              prog_layer_lengths_mm=lengths, counts={k: len(g[k]) for k in g},
              ground_zone_contours={z['net']: {l: len(p) for l,p in z['layers'].items()} for z in g['zones'].values()})
(R / 'focused-review.json').write_text(json.dumps(result, indent=2))

colors = {'PROG': '#ab00b8', 'BATTERY': '#b57900', 'SW2': '#e00000', 'BTST2': '#0872c9',
          'PGND': '#b5cfb5', 'GND': '#719471'}
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 18)
small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 13)
x0, y0, x1, y1 = 60.5, 63.5, 72.7, 72.6
scale, top = 90, 95
w, h = round((x1-x0)*scale), round((y1-y0)*scale)+top+45
def pt(p):
    return ((p[0]-x0)*scale, (p[1]-y0)*scale+top)

for layer in ['F.Cu', 'B.Cu', 'In2.Cu']:
    im = Image.new('RGB', (w,h), 'white'); d = ImageDraw.Draw(im)
    # Filled contours are contextual silhouettes, not a complete zone-hole model.
    for z in g['zones'].values():
        for poly in z['layers'].get(layer, []):
            d.polygon([pt(p) for p in poly], fill=colors.get(z['net'], '#dddddd'))
    for x in range(math.ceil(x0),math.floor(x1)+1):
        d.line([pt([x,y0]),pt([x,y1])],fill='#e3e8e3')
    for y in range(math.ceil(y0),math.floor(y1)+1):
        d.line([pt([x0,y]),pt([x1,y])],fill='#e3e8e3')
    for t in g['tracks'].values():
        if t['layer'] != layer: continue
        a,b = pt(t['start']),pt(t['end']); r=t['width']*scale/2
        color=colors.get(t['net'],'#bbbbbb')
        d.line([a,b],fill=color,width=max(2,round(2*r)))
        for x,y in [a,b]: d.ellipse([x-r,y-r,x+r,y+r],fill=color)
    for p in g['pads'].values():
        for poly in p['polygons'].get(layer,[]): d.polygon([pt(a) for a in poly],fill=colors.get(p['net'],'#c7c7c7'))
    for v in g['vias'].values():
        x,y=pt(v['position']); r=v['copper_widths'][layer]*scale/2
        d.ellipse([x-r,y-r,x+r,y+r],fill=colors.get(v['net'],'#bbbbbb'),outline='#555555')
        r=v['drill']*scale/2; d.ellipse([x-r,y-r,x+r,y+r],fill='white')
    # Show other-layer PROG as a thin dashed projection, especially on In2.
    for t in prog:
        if t['layer']==layer: continue
        a,b=pt(t['start']),pt(t['end']); n=max(1,round(math.dist(a,b)/7))
        for i in range(0,n,2):
            d.line([(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n),
                    (a[0]+(b[0]-a[0])*min(i+1,n)/n,a[1]+(b[1]-a[1])*min(i+1,n)/n)],fill='#d98bdf',width=2)
    for f in g['footprints'].values():
        x,y=f['position']
        if x0<x<x1 and y0<y<y1: d.text(pt([x,y]),f['ref'],font=small,fill='black')
    d.rectangle([0,0,w,top-4],fill='white')
    d.text((12,8),'Preferred 14.198947 mm PROG — '+layer,font=font,fill='black')
    for i,(net,color) in enumerate(colors.items()):
        d.rectangle([12+i*150,38,28+i*150,51],fill=color)
        d.text((33+i*150,35),net,font=small,fill='black')
    d.text((12,62),'Solid: this layer. Dashed magenta: other-layer PROG projection. Grid: 1 mm.',font=small,fill='black')
    d.rectangle([0,h-40,w,h],fill='white')
    d.text((12,h-34),'Native exported geometry; ground silhouettes omit holes. Not fabrication artwork.',font=small,fill='black')
    im.save(R / ('review-'+layer.replace('.','_')+'.png'))
print(json.dumps(result))
