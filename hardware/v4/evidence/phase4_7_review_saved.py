"""Offline evidence analysis only. No KiCad imports, IPC, or CAD writes."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
E=Path(__file__).resolve().parent
g=json.loads((E/'phase4-7-geometry.json').read_text())
s=json.loads((E/'c9-apply-phase4-7-post-assertion-approved-ipc.json').read_text())
assert all(hashlib.sha256((E.parent/'ups_v4'/n).read_bytes()).hexdigest()==v for n,v in s['hashes'].items())
root=ET.parse(E/'phase4-7-preflight.net.xml').getroot()
pin_nets={(p.get('ref'),p.get('pin')):n.get('name') for n in root.findall('./nets/net') for p in n.findall('node')}
assert all(pin_nets.get((f['ref'],p['pin']),p['net'])==p['net'] for f in g['footprints'] for p in f['pads'])
nets=['REGN','ILIM_HIZ','TS','BATP','PROG','CE_N','CE_BIAS','/CHG_GATE','CHG_REQ','GND','ACDRV1','BTST1','BTST2','SDRV','STAT','~INT','I2C_SCL','I2C_SDA']
out={}
for n in nets:
 pads=[dict(ref=f['ref'],value=f['value'],**p) for f in g['footprints'] for p in f['pads'] if p['net']==n]
 out[n]=dict(pads=pads,tracks=[t for t in g['tracks'] if t['net']==n],vias=[v for v in g['vias'] if v['net']==n])
(E/'phase4-7-affected-connectivity.json').write_text(json.dumps(out,indent=2)+'\n')
print('Related nets:',[(n,len(v['pads']),len(v['tracks']),len(v['vias'])) for n,v in out.items()])
drc=json.loads((E/'phase4-7-preflight-drc.json').read_text())
print('DRC example',drc['unconnected_items'][0])
W,H=1600,950;x0,y0=52,60;scale=55
im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im)
def pos(p):return ((p[0]-x0)*scale+30,(p[1]-y0)*scale+30)
colors={'SW1':'#ff6a00','SW2':'#d00000','REGN':'#008d8d','VIN1':'#ae50b0','PGND':'#6b986b','BATTERY':'#c09300'}
for t in g['tracks']:
 a,b=pos(t['start']),pos(t['end'])
 d.line([a,b],fill=colors.get(t['net'],'#aaaaaa') if t['layer']=='F.Cu' else '#bbbbdd',width=max(1,int(t['width']*scale)))
for f in g['footprints']:
 if not 52<f['xy'][0]<80 or not 60<f['xy'][1]<76:continue
 for c in f['courtyard']:
  a,b=pos(c['start']),pos(c['end'])
  if c['shape']=='1':d.rectangle([min(a[0],b[0]),min(a[1],b[1]),max(a[0],b[0]),max(a[1],b[1])],outline='#888888')
  else:d.line([a,b],fill='#888888')
 for p in f['pads']:
  a,b=map(pos,p['bbox']);d.rectangle([*a,*b],fill=colors.get(p['net'],'#dfbaba'),outline='#444444')
  if f['ref']!='IC1':d.text(pos(p['xy']),p['pin'],fill='black')
 d.text(pos(f['xy']),f['ref'],fill='black')
for v in g['vias']:
 a,b=pos(v['xy']);r=v['width']*scale/2;dr=v['drill']*scale/2
 if -10<a<W+10 and -10<b<H+10:d.ellipse([a-r,b-r,a+r,b+r],fill=colors.get(v['net'],'#999999'));d.ellipse([a-dr,b-dr,a+dr,b+dr],fill='white')
for x in range(52,81,2):d.text(pos([x,60]),str(x),fill='black')
for y in range(60,77,2):d.text(pos([52,y]),str(y),fill='black')
d.text((30,H-35),'Actual evidence geometry; F.Cu colored, other routed layers pale blue; pad bounding boxes; copper fills omitted.',fill='black')
im.save(E/'phase4-7-local-layout.png')
print('Hashes unchanged; exported pin nets match; offline plot saved.')
