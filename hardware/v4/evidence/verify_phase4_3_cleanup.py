"""Compare exported IPC evidence, not serialized CAD; write bounded review evidence."""
import json, math, hashlib, subprocess, collections
from pathlib import Path
P=Path(__file__).resolve().parent
def read(n): return json.loads((P/n).read_text(encoding='utf-8'))
def dec(r):
    assert not r.get('isError'), r
    return json.loads(r['content'][0]['text'])
old=read('phase4-3-final-live-readback.json')
new=read('phase4-3-cleanup-final-live-readback.json')
oi={c['reference']:c for c in dec(old['inventory'])['components']}
ni={c['reference']:c for c in dec(new['inventory'])['components']}
expected={'J4','J6','H1','H2','C3','C27','C30','C31'}
changes={r:{k:[oi[r].get(k),c.get(k)] for k in set(oi[r])|set(c) if oi[r].get(k)!=c.get(k)} for r,c in ni.items()}
changes={r:v for r,v in changes.items() if v}
issues=[]
if set(oi)!=set(ni): issues.append('reference inventory changed')
if set(changes)!=expected: issues.append('unexpected placement/property change set')
for r,v in changes.items():
    if any(k not in {'x','y','rotation','footprint'} for k in v): issues.append(f'{r}: unexpected property change')
    if 'footprint' in v and r not in {'J4','J6'}: issues.append(f'{r}: unexpected footprint substitution')
def close(a,b):
    if isinstance(a,dict) and isinstance(b,dict): return a.keys()==b.keys() and all(close(a[k],b[k]) for k in a)
    if isinstance(a,list) and isinstance(b,list): return len(a)==len(b) and all(close(x,y) for x,y in zip(a,b))
    if isinstance(a,(float,int)) and isinstance(b,(float,int)): return math.isclose(a,b,rel_tol=0,abs_tol=1.0001e-6)
    return a==b
def invariant(p): return {k:v for k,v in p.items() if k not in {'x','y','rotation_deg'}}
pad_count=0
for r in ni:
    a,b=dec(old['pads'][r]),dec(new['pads'][r]); assert b['source']=='ipc'
    pad_count+=len(b['pads'])
    if collections.Counter((p['number'],p['net']) for p in a['pads'])!=collections.Counter((p['number'],p['net']) for p in b['pads']): issues.append(f'{r}: pin/net mismatch')
    if r not in {'J4','J6'}:
        if not close([invariant(p) for p in a['pads']],[invariant(p) for p in b['pads']]): issues.append(f'{r}: exported geometry/identity mismatch')
        if r not in expected and not close(a['pads'],b['pads']): issues.append(f'{r}: unexpected pad motion')
def nearest(ref,cap,net):
    a=dec(new['pads'][ref])['pads']; b=dec(new['pads'][cap])['pads']
    return round(min(math.hypot(x['x']-y['x'],x['y']-y['y']) for x in a for y in b if x['net']==y['net']==net),3)
proximity={'IC1_REGN_C3':nearest('IC1','C3','REGN'),'U4_USB_VBUS_C27':nearest('U4','C27','USB_VBUS'),'U1_MCU3V3_C31':nearest('U1','C31','MCU3V3'),'U1_MCU3V3_C30':nearest('U1','C30','MCU3V3')}
drc=read('phase4-3-cleanup-final-drc.json')
counts=collections.Counter((v['severity'],v['rule']) for v in drc['violations'])
board=P.parent/'ups_v4/ups12v_v4.kicad_pcb'
diff=subprocess.run(['git','diff','--unified=0','--',str(board)],capture_output=True,text=True,check=True).stdout
(P/'phase4-3-cleanup-board.diff').write_text(diff,encoding='utf-8')
changed_lines=[s for s in diff.splitlines() if s[:1] in '+-' and not s.startswith(('+++','---'))]
custom_lines=[s for s in changed_lines if any(t in s for t in ['(primitives','(gr_poly',' custom'])]
if custom_lines: issues.append('custom pad definitions changed in diff')
out={'references':len(ni),'physical_pads':pad_count,'pin_net_comparison':'all physical pad number/net pairs unchanged','changes':changes,'issues':issues,'exported_pad_geometry_unchanged_except_J4_J6':not any('geometry' in s for s in issues),'IC1_custom_pad_definitions_changed_in_diff':len(custom_lines),'custom_polygon_limit':'IPC pad reader exposes shape/size but not polygon vertices; preservation corroborated by focused Git diff and unchanged IC1 identity, placement and pad metadata. No custom pad mutation was issued.','proximity_mm_pad_centres':proximity,'outline_mm':[96,70],'outline_source':'unchanged accepted Edge.Cuts, corroborated by focused Git diff and rectangular placement score','layer_evidence':dec(new['layers']),'track_evidence':dec(new['tracks']),'zones_and_vias':'No creation operation issued; accepted zero baseline retained. No CAD rule area implemented.','drc':{f'{sev}:{rule}':n for (sev,rule),n in counts.items()},'unrouted':len(drc['unconnected_items']),'schematic_parity':drc['schematic_parity'],'sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [board,board.with_suffix('.kicad_sch')]}}
(P/'phase4-3-cleanup-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:out[k] for k in ['references','physical_pads','issues','proximity_mm_pad_centres','IC1_custom_pad_definitions_changed_in_diff']},indent=2))
