"""Read-only final checkpoint summary; full raw artifacts remain alongside."""
from pathlib import Path
import sys,json,re,collections,xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
import pcbnew
from verify_nanofit import parse,many,ref
E=Path(__file__).resolve().parent
B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
S=B.with_suffix('.kicad_sch')
old_symbols={ref(s):s for s in many(parse((E/'nanofit-native-entry.kicad_sch').read_text()),'symbol')}
new_symbols={ref(s):s for s in many(parse(S.read_text()),'symbol')}
assert old_symbols.keys()==new_symbols.keys()
assert all(old_symbols[r]==new_symbols[r] for r in old_symbols if r not in ('J1','J2','J3','J8'))
def nodes(path):
    root=ET.parse(path).getroot()
    return {(n.attrib['ref'],n.attrib['pin']):net.attrib['name'] for net in root.findall('./nets/net') for n in net.findall('node')}
old,new=nodes(E/'nanofit-entry.net.xml'),nodes(E/'nanofit-final.net.xml')
changed=[{'ref':k[0],'pin':k[1],'before':old.get(k),'after':new.get(k)} for k in sorted(old.keys()|new.keys()) if old.get(k)!=new.get(k)]
assert { (c['ref'],c['pin']) for c in changed}=={('J2','2'),('J2','3'),('J8','1'),('J8','2'),('J8','3')}
d=json.loads((E/'nanofit-final-drc.json').read_text())
baseline=json.loads((E/'phase4-6-final-drc.json').read_text())
def unrouted_nets(report):
    c=collections.Counter()
    for v in report['unconnected_items']:
        names=set(n for i in v['items'] for n in re.findall(r'\[([^]]*)\]',i['description']))
        c[' / '.join(sorted(names))]+=1
    return c
before,after=unrouted_nets(baseline),unrouted_nets(d)
differences={n:[before[n],after[n]] for n in before.keys()|after.keys() if before[n]!=after[n]}
assert not differences,differences
assert len(d['unconnected_items'])==262
assert len(d['schematic_parity'])==0
assert not [v for v in d['violations'] if v['severity']=='error']
b=pcbnew.LoadBoard(str(B))
ground=[z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='PGND']
assert len(ground)==1 and ground[0].IsFilled()
assert ground[0].GetFilledPolysList(pcbnew.In1_Cu).OutlineCount()==1
baseline_board=parse((E/'nanofit-before-native-remapping.kicad_pcb').read_text())
current_board=parse(B.read_text())
fields_before={ref(f):{p[1]:p[2] for p in many(f,'property')} for f in many(baseline_board,'footprint')}
field_changes=[]
for f in many(current_board,'footprint'):
    r=ref(f)
    if r not in ('J1','J2','J3','J8'):continue
    for p in many(f,'property'):
        if fields_before[r].get(p[1])!=p[2]:field_changes.append({'ref':r,'field':p[1],'before':fields_before[r].get(p[1]),'after':p[2]})
report={'manufacturer':'SD-105313-100 Rev J1, 2025-06-26, sheet1 recommended PCB connector-side view independently rendered and checked','native_library_save_reload':'nanofit-native-correction.json','native_net_remap_save_reload':'nanofit-native-remapping.json','unrelated_schematic_instances_preserved':len(old_symbols)-4,'netlist_changed_pin_keys':changed,'unexpected_netlist_changes':0,'connector_field_updates':field_changes,'drc':{'unrouted':262,'other_errors':0,'warnings':len(d['violations']),'parity':0,'warning_rules':dict(collections.Counter(v['rule'] for v in d['violations'])),'unrouted_per_net_counts_unchanged':True},'erc':{'errors':0,'unchanged_warnings':4},'PGND_native_refill_single_polygon':True,'placement_limit':'six connector silk-edge warnings remain, four more than baseline; body face nominally flush at Y30 with latch overhang; enclosure/harness physical fit unqualified','phase_boundary':'STOP; no general routing, fabrication, purchasing, commit or push; existing electrical safety gates OPEN'}
(E/'nanofit-final-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k in ('unrelated_schematic_instances_preserved','unexpected_netlist_changes','drc','erc','PGND_native_refill_single_polygon')}))
