"""Read exported evidence; CAD parsing is read-only for rule areas/custom geometry."""
from pathlib import Path
import collections, copy, hashlib, json, math, runpy, subprocess
import xml.etree.ElementTree as ET
P = Path(__file__).resolve().parent
def read(n): return json.loads((P/n).read_text(encoding='utf-8'))
def dec(r):
    assert not r.get('isError'), r
    return json.loads(r['content'][0]['text'])
live = read('phase4-4-live-readback.json')
entry = read('phase4-4-entry-readback.json')
previous = read('phase4-3-cleanup-final-live-readback.json')
oldxml = ET.parse(P/'phase3-7-final.net.xml').getroot()
xml = ET.parse(P/'phase4-4.net.xml').getroot()
def nets(root): return {(p.get('ref'),p.get('pin')):n.get('name') for n in root.findall('./nets/net') for p in n.findall('node')}
oldnets, newnets = nets(oldxml), nets(xml)
components = {c.get('ref'):c for c in xml.findall('./components/comp')}
inventory = {c['reference']:c for c in live['inventory']['components']}
issues = []
before={c['reference']:c for c in dec(entry['schematic_inventory'])['components']}
after={c['reference']:c for c in dec(read('phase4-4-final-schematic-readback.json'))['components']}
changed=[r for r in before if before[r]!=after.get(r)]
if changed!=['J7'] or set(after)-set(before)!={'C70','C71'} or set(before)-set(after): issues.append('unexpected schematic component/property changes')
retained = [(k,v,newnets.get(k)) for k,v in oldnets.items() if newnets.get(k)!=v]
if retained: issues.append('retained schematic nets changed')
added = {str(k):v for k,v in newnets.items() if k not in oldnets}
expected = {('C70','1'):'MAIN_3V3',('C70','2'):'PGND',('C71','1'):'USB3V3',('C71','2'):'PGND'}
if {k:v for k,v in newnets.items() if k not in oldnets} != expected: issues.append('unexpected added pin nets')
parity = []
for ref,c in components.items():
    if ref not in inventory:
        parity.append(['missing_footprint',ref]); continue
    for key in ['value','footprint']:
        if c.findtext(key)!=inventory[ref][key]: parity.append([key,ref,c.findtext(key),inventory[ref][key]])
    pads = live['pads'][ref]['pads']
    assert live['pads'][ref]['source']=='ipc'
    for (r,pin),net in newnets.items():
        if r!=ref: continue
        matches = [p for p in pads if p['number']==pin]
        if not matches or any(p['net']!=net for p in matches): parity.append(['pin_net',ref,pin,net])
if sorted((p[0],p[1]) for p in parity) != [('footprint','J7'),('missing_footprint','C70'),('missing_footprint','C71')]: issues.append('unexpected PCB parity differences')
assert live['inventory']['components']==dec(previous['inventory'])['components']
def near(a,b,net):
    return min(math.dist((x['x'],x['y']),(y['x'],y['y'])) for x in live['pads'][a]['pads'] for y in live['pads'][b]['pads'] if x['net']==y['net']==net)
proximity = {f'U5_{r}':round(near('U5',r,net),3) for r,net in [('C35','USB3V3'),('C45','MAIN_3V3'),('C36','MCU3V3')]}
base = runpy.run_path(str(P/'verify_phase4_2.py'))
child,children,sexpr = [base[k] for k in ['child','children','sexpr']]
board_path=P.parent/'ups_v4/ups12v_v4.kicad_pcb'
board=sexpr(board_path)
board_unchanged=subprocess.run(['git','diff','--quiet','--',str(board_path)]).returncode==0
if not board_unchanged: issues.append('board changed from clean entry')
fps={next(p[2] for p in children(f,'property') if p[1]=='Reference'):f for f in children(board,'footprint')}
def normalized(p, rotation):
    q=copy.deepcopy(p); at=child(q,'at')
    if len(at)==3: at.append('0')
    at[3]=str((float(at[3])-rotation)%360)
    primitives=child(q,'primitives')
    if primitives:
        for shape in primitives[1:]:
            pts=child(shape,'pts')
            if pts and len(pts)>2 and base['same'](pts[1],pts[-1]): pts.pop()
    return base['pad_geometry'](q)
def equal(a,b):
    if isinstance(a,list) and isinstance(b,list): return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    try: return math.isclose(float(a),float(b),rel_tol=0,abs_tol=1.0001e-6)
    except (ValueError,TypeError): return a==b
library_geometry={}
for ref,r in read('phase4-4-library-readback.json').items():
    lib=sexpr(dec(r)['path']); angle=float(child(fps[ref],'at')[3]) if len(child(fps[ref],'at'))>3 else 0
    a=sorted(children(fps[ref],'pad'),key=base['pad_sort']); z=sorted(children(lib,'pad'),key=base['pad_sort'])
    ok=len(a)==len(z) and all(equal(normalized(p,angle),normalized(q,0)) for p,q in zip(a,z))
    library_geometry[ref]={'physical_pads':len(a),'all_pad_geometry_matches_library':ok,'custom_pad_numbers':[p[1] for p in a if p[3]=='custom']}
    if not ok: issues.append('library pad geometry differs: '+ref)
ruleareas=[z for z in children(board,'zone') if child(z,'keepout')]
f5=['U7','U8','Q10','L3','R60','R61','R62','R63','C60','C61','C62','C63','C64','C65','C66','C67','C68','C69','J8']
assert all(r in inventory for r in f5)
candidate=dec(entry['j7_candidate'])
j7nets={p['number']:p['net'] for p in live['pads']['J7']['pads'] if p['number']}
assert set(j7nets)==set(p['number'] for p in candidate['pads'])
for n in ['A1','A12','B1','B12','SH']: assert j7nets[n]=='PGND'
for n in ['A4','A9','B4','B9']: assert j7nets[n]=='USB_VBUS'
for n in ['A6','B6']: assert j7nets[n]=='USB_DP'
for n in ['A7','B7']: assert j7nets[n]=='USB_DN'
assert j7nets['A5']=='USB_CC1' and j7nets['B5']=='USB_CC2'
contact=[p for p in candidate['pads'] if p['number']!='SH']
assert len(contact)==16 and all(p['drill']['size']=={'x':.4,'y':.4} for p in contact)
assert all(p['size']=={'x':.7,'y':.7} and p['pad_type']=='thru_hole' for p in contact)
drc=read('phase4-4-drc.json'); erc=read('phase4-4-erc.json')
out={'status':'PARTIAL; native KiCad actions required; not ready for routing',
 'board_unchanged_from_clean_entry':board_unchanged,'live_board':live['board'],
 'schematic_components':len(components),'pcb_footprints':len(inventory),'physical_pads':sum(len(p['pads']) for p in live['pads'].values()),
 'preserved_original_schematic_pin_entries':len(oldnets),'retained_pin_changes':retained,'added_pin_nets':added,
 'existing_schematic_component_property_changes':changed,'new_schematic_refs':sorted(set(after)-set(before)),
 'reference_footprint_pin_parity_differences':parity,'all_existing_pad_net_pairs_unchanged':all(collections.Counter((p['number'],p['net']) for p in live['pads'][r]['pads'])==collections.Counter((p['number'],p['net']) for p in dec(previous['pads'][r])['pads']) for r in inventory),
 'f5_refs_present':f5,'single_shared_pcb':True,'u5_current_pad_distance_mm':proximity,
 'j7_candidate_number_to_net':j7nets,'j7_geometry_mm':{'contact_drill':.4,'contact_land':.7,'pitch':.85,'row_spacing':1.35,'annular_ring_nominal':.15,'adjacent_copper_gap_nominal':.15,'adjacent_hole_to_copper':.30,'adjacent_hole_to_hole':.45,'shell_slot_width':.6,'shell_annular_ring_nominal':.15},
 'native_rf_rule_areas_in_saved_board':len(ruleareas),'tracks':len(children(board,'segment'))+len(children(board,'arc')),'vias':len(children(board,'via')),'zones':len(children(board,'zone')),
 'custom_pad_preservation':'Entire PCB byte-identical to clean entry; prior verified IC1 custom primitives retained',
 'erc':{'errors':erc['errors'],'warnings':erc['warnings']},
 'drc':{'unrouted':len(drc['unconnected_items']),'parity':len(drc['schematic_parity']),'rules':dict(collections.Counter(v['rule'] for v in drc['violations']))},
 'library_mismatch_pad_geometry_review':library_geometry,
 'issues':issues,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [board_path,board_path.with_suffix('.kicad_sch'),P/'phase4-4.net.xml']}}
(P/'phase4-4-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:out[k] for k in ['status','schematic_components','pcb_footprints','preserved_original_schematic_pin_entries','reference_footprint_pin_parity_differences','u5_current_pad_distance_mm','erc','drc','issues']},indent=2))
assert not issues, issues
