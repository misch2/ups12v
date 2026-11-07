"""Verify native owner changes using IPC exports, XML and read-only CAD inspection."""
from pathlib import Path
import collections, copy, hashlib, json, math, re, runpy, subprocess
import xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent
CAD=P.parent/'ups_v4'
def read(n): return json.loads((P/n).read_text(encoding='utf-8'))
def dec(r):
    assert not r.get('isError'), r
    return json.loads(r['content'][0]['text'])
base=runpy.run_path(str(P/'verify_phase4_2.py'))
child,children,sexpr=[base[k] for k in ['child','children','sexpr']]
live=read('phase4-4-native-live-readback.json')
old=read('phase4-4-live-readback.json')
inv={c['reference']:c for c in live['inventory']['components']}
oldinv={c['reference']:c for c in old['inventory']['components']}
xml=ET.parse(P/'phase4-4-native.net.xml').getroot()
oldxml=ET.parse(P/'phase4-4.net.xml').getroot()
comps={c.get('ref'):c for c in xml.findall('./components/comp')}
def nets(x): return {(p.get('ref'),p.get('pin')):n.get('name') for n in x.findall('./nets/net') for p in n.findall('node')}
pin_nets=nets(xml)
issues=[]
if pin_nets!=nets(oldxml): issues.append('schematic pin nets changed since approved schematic')
if set(inv)!=set(comps): issues.append('reference set mismatch')
checked=0
for ref,c in comps.items():
    if ref not in inv: continue
    for key in ['value','footprint']:
        if inv[ref][key]!=c.findtext(key): issues.append([key,ref])
    assert live['pads'][ref]['source']=='ipc'
    for (r,n),net in pin_nets.items():
        if r!=ref: continue
        checked+=1
        pads=[p for p in live['pads'][ref]['pads'] if p['number']==n]
        if not pads or any(p['net']!=net for p in pads): issues.append(['pin_net',ref,n,net])
for r,c in oldinv.items():
    if r not in ['J7','C36'] and c!=inv.get(r): issues.append(['unexpected_inventory_change',r])
plan=read('phase4-4-native-placement-plan.json')
for r in ['J7','C70','C71','C36']:
    c,w=inv[r],plan[r]
    if any(not math.isclose(c[k],w[k],abs_tol=1e-6) for k in ['x','y']) or (c['rotation']-w['rotation'])%360 or c['layer']!=w['layer']: issues.append(['planned_placement',r])
root=sexpr(CAD/'ups12v_v4.kicad_pcb')
fps={next(p[2] for p in children(f,'property') if p[1]=='Reference'):f for f in children(root,'footprint')}
for r,fp in fps.items():
    a=collections.Counter((p[1],(child(p,'net') or ['',''])[-1]) for p in children(fp,'pad'))
    z=collections.Counter((p['number'],p['net']) for p in live['pads'][r]['pads'])
    if a!=z: issues.append(['saved_live_pad_net',r])
    at=child(fp,'at'); theta=math.radians(float(at[3]) if len(at)>3 else 0)
    if any(not math.isclose(float(at[i+1]),inv[r][k],abs_tol=1e-6) for i,k in enumerate(['x','y'])): issues.append(['saved_live_footprint_position',r])
    savedpads={child(p,'uuid')[1]:p for p in children(fp,'pad')}
    for p in live['pads'][r]['pads']:
        q=savedpads[p['uuid']]; local=child(q,'at'); x,y=map(float,local[1:3])
        world=(float(at[1])+x*math.cos(theta)+y*math.sin(theta),float(at[2])-x*math.sin(theta)+y*math.cos(theta))
        if any(not math.isclose(a,b,abs_tol=1.0001e-6) for a,b in zip(world,(p['x'],p['y']))): issues.append(['saved_live_pad_position',r,p['number']])
def normal(p,angle):
    q=copy.deepcopy(p); at=child(q,'at')
    if len(at)==3: at.append('0')
    at[3]=str((float(at[3])-angle)%360)
    prim=child(q,'primitives')
    if prim:
        for shape in prim[1:]:
            pts=child(shape,'pts')
            if pts and len(pts)>2 and base['same'](pts[1],pts[-1]): pts.pop()
    return base['pad_geometry'](q)
def equal(a,b):
    if isinstance(a,list) and isinstance(b,list): return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    try: return math.isclose(float(a),float(b),rel_tol=0,abs_tol=1.0001e-6)
    except (ValueError,TypeError): return a==b
def angle(fp):
    a=child(fp,'at'); return float(a[3]) if len(a)>3 else 0
libs=read('phase4-4-library-readback.json')
candidate=dec(read('phase4-4-entry-readback.json')['j7_candidate'])
cap=dec(read('phase4-4-cap-footprint.json'))
geometry={}
for r,info in {**{r:dec(v) for r,v in libs.items()},'J7':candidate,'C70':cap,'C71':cap}.items():
    library=sexpr(info['path'])
    a=sorted(children(fps[r],'pad'),key=base['pad_sort']); z=sorted(children(library,'pad'),key=base['pad_sort'])
    ok=len(a)==len(z) and all(equal(normal(p,angle(fps[r])),normal(q,0)) for p,q in zip(a,z))
    geometry[r]=ok
    if not ok: issues.append(['library_pad_geometry',r])
def parse_text(text):
    stack=[]; root=None
    for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text):
        if t=='(':
            a=[]
            if stack: stack[-1].append(a)
            stack.append(a)
        elif t==')': root=stack.pop()
        else: stack[-1].append(t[1:-1] if t.startswith('"') else t)
    assert not stack
    return root
head=parse_text(subprocess.run(['git','show','HEAD:hardware/v4/ups_v4/ups12v_v4.kicad_pcb'],capture_output=True,text=True,encoding='utf-8',check=True).stdout)
headfps={next(p[2] for p in children(f,'property') if p[1]=='Reference'):f for f in children(head,'footprint')}
retained_geometry=[]
for r,fp in headfps.items():
    if r=='J7': continue
    a=sorted(children(fp,'pad'),key=base['pad_sort']); z=sorted(children(fps[r],'pad'),key=base['pad_sort'])
    if len(a)!=len(z) or not all(equal(normal(p,angle(fp)),normal(q,angle(fps[r]))) for p,q in zip(a,z)): retained_geometry.append(r)
if retained_geometry: issues.append(['retained_pad_geometry_changed',retained_geometry])
def strip_uuid(x):
    if not isinstance(x,list): return x
    return [strip_uuid(v) for v in x if not (isinstance(v,list) and v and v[0]=='uuid')]
courtyards={}
for r in ['Q1','Q2','Q10','C20','C22']:
    def graphics(fp): return [strip_uuid(g) for g in fp if isinstance(g,list) and g[0].startswith('fp_') and child(g,'layer')==['layer','F.CrtYd']]
    courtyards[r]=bool(graphics(fps[r])) and equal(graphics(fps[r]),graphics(headfps[r]))
    if not courtyards[r]: issues.append(['corrected_courtyard_not_preserved',r])
outline=[q for q in root if isinstance(q,list) and child(q,'layer')==['layer','Edge.Cuts']]
points=[child(q,k)[1:3] for q in outline for k in ['start','end'] if child(q,k)]
outline_box=[min(float(p[0]) for p in points),min(float(p[1]) for p in points),max(float(p[0]) for p in points),max(float(p[1]) for p in points)]
if outline_box!=[30,30,126,100]: issues.append('outline changed')
enabled={p['name'] for p in live['layers']['layers'] if p['copper']}
if enabled!={'F.Cu','In1.Cu','In2.Cu','B.Cu'} or live['board']['source']!='ipc': issues.append('live board/layer mismatch')
rf=[z for z in children(root,'zone') if child(z,'name')==['name','U1_RF_ANTENNA']]
if len(rf)!=1: issues.append('expected one named RF rule area')
z=rf[0]
layers=child(z,'layers')[1:]
if set(layers)!={'F.Cu','In1.Cu','In2.Cu','B.Cu'}: issues.append('RF layers incorrect')
keepout={p[0]:p[1] for p in child(z,'keepout')[1:]}
if any(keepout.get(k)!='not_allowed' for k in ['tracks','vias','pads','copperpour']) or keepout.get('footprints')!='allowed': issues.append('RF keepout flags incorrect')
pts=[list(map(float,p[1:])) for p in child(child(z,'polygon'),'pts')[1:]]
expected_pts=[[75.4,99.2],[88.6,99.2],[88.6,104.6],[75.4,104.6]]
if pts!=expected_pts: issues.append('RF polygon differs from dimensioned plan')
rules=(CAD/'ups12v_v4.kicad_dru').read_text(encoding='utf-8-sig')
project=json.loads((CAD/'ups12v_v4.kicad_pro').read_text(encoding='utf-8-sig'))
rf_severity=project['board']['design_settings']['rule_severities'].get('items_not_allowed')
if rf_severity!='error': issues.append('RF disallow violations not configured as errors')
expected_condition="A.Type == 'Footprint' && A.Reference != 'U1' && A.intersectsArea('U1_RF_ANTENNA')"
if expected_condition not in rules or '(constraint disallow footprint)' not in rules: issues.append('RF component exclusion rule missing/different')
intruding=[]
for r,pads in live['pads'].items():
    for p in pads['pads']:
        a=math.radians(p['rotation_deg']); w,h=p['size']['x'],p['size']['y']
        hx=(abs(math.cos(a))*w+abs(math.sin(a))*h)/2; hy=(abs(math.sin(a))*w+abs(math.cos(a))*h)/2
        if p['x']+hx>75.4 and p['x']-hx<88.6 and p['y']+hy>99.2 and p['y']-hy<104.6: intruding.append([r,p['number']])
if intruding: issues.append(['pads_intruding_RF_area',intruding])
field=next(p for p in children(fps['U1'],'property') if p[1]=='Reference')
local=child(field,'at'); x,y=map(float,local[1:3]); a=math.radians(angle(fps['U1'])); pos=child(fps['U1'],'at')
world=[float(pos[1])+x*math.cos(a)+y*math.sin(a),float(pos[2])-x*math.sin(a)+y*math.cos(a)]
if not equal(world,[90.5,98.0]) or float(local[3])%360!=0: issues.append('U1 reference position/angle incorrect')
metadata={}
for r,key in [('J4','PopulationGroup'),('J6','Bought'),('J7','MPN'),('J7','Manufacturer')]:
    boardfields={p[1]:p[2] for p in children(fps[r],'property')}
    schfields={p.get('name'):p.text or '' for p in comps[r].findall('./fields/field')}
    metadata[r+'.'+key]={'pcb':boardfields.get(key),'schematic':schfields.get(key)}
    if boardfields.get(key)!=schfields.get(key): issues.append(['metadata',r,key])
f5=['U7','U8','Q10','L3','R60','R61','R62','R63','C60','C61','C62','C63','C64','C65','C66','C67','C68','C69','J8']
if not all(r in inv for r in f5): issues.append('F5 references missing')
def near(a,b,net):
    return round(min(math.dist((x['x'],x['y']),(y['x'],y['y'])) for x in live['pads'][a]['pads'] for y in live['pads'][b]['pads'] if x['net']==y['net']==net),3)
proximity={r:near('U5',r,n) for r,n in [('C70','MAIN_3V3'),('C71','USB3V3'),('C36','MCU3V3')]}
drc=read('phase4-4-native-drc.json'); erc=read('phase4-4-native-erc.json')
counts=dict(collections.Counter((v['severity']+':'+v['rule']) for v in drc['violations']))
if drc['schematic_parity']: issues.append('DRC parity findings')
if any(v['severity']=='error' for v in drc['violations']): issues.append('DRC geometric errors')
track_count=len(children(root,'segment'))+len(children(root,'arc')); via_count=len(children(root,'via'))
copper_count=sum(not child(q,'keepout') for q in children(root,'zone'))
if track_count or via_count or copper_count: issues.append('routing/copper present outside phase boundary')
out={'status':'Verified pre-routing checkpoint' if not issues else 'Incomplete; findings require review',
 'live_board':live['board'],'schematic_components':len(comps),'pcb_footprints':len(inv),'physical_pads':sum(len(p['pads']) for p in live['pads'].values()),
 'checked_xml_pin_entries':checked,'schematic_pin_nets_preserved_since_phase4_4':pin_nets==nets(oldxml),'reference_value_footprint_pad_net_parity':'PASS' if not issues else 'see issues',
 'intended_positions':{r:inv[r] for r in ['J7','C70','C71','C36','U1']},'u5_supply_pad_distances_mm':proximity,'metadata':metadata,
 'pad_geometry_matches_current_library':geometry,'retained_pad_geometry_differences_vs_HEAD':retained_geometry,'IC1_custom_pads_preserved':not retained_geometry,
 'corrected_courtyards_preserved':courtyards,'outline_bounds_mm':outline_box,'all_saved_live_pad_positions_match':not any(isinstance(i,list) and i[0]=='saved_live_pad_position' for i in issues),
 'rf':{'saved_native_area':True,'layers':layers,'keepout':keepout,'polygon_mm':pts,'other_components_rule':expected_condition,'disallow_violation_severity':rf_severity,'pads_intruding_area':intruding,'U1_reference_world_mm':world,'zone_fill_check':'Native copperpour exclusion flags verified on all four layers; no copper zones exist, so no physical refill experiment performed.','external_metal_clearance':'Owner-reported manual completion; enclosure/wires not represented in CAD, not measured.'},
 'F5_refs_retained':f5,'single_PCB':True,'tracks':track_count,'vias':via_count,'copper_zones':copper_count,'native_rule_areas':len(rf),
 'erc':{'errors':erc['errors'],'warnings':erc['warnings']},'drc':{'unrouted':len(drc['unconnected_items']),'parity':len(drc['schematic_parity']),'counts':counts},'issues':issues,
 'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [CAD/'ups12v_v4.kicad_sch',CAD/'ups12v_v4.kicad_pcb',CAD/'ups12v_v4.kicad_dru',P/'phase4-4-native.net.xml']}}
(P/'phase4-4-native-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:out[k] for k in ['status','schematic_components','pcb_footprints','physical_pads','checked_xml_pin_entries','u5_supply_pad_distances_mm','erc','drc','issues']},indent=2))
assert not issues, issues
