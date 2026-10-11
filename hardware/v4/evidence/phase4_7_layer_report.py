"""Summarize existing native evidence and emit exact geometry tables; no CAD API."""
from pathlib import Path
import json,csv,hashlib,re,collections,difflib,sys
E=Path(__file__).resolve().parent;B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
def load(n):return json.loads((E/n).read_text())
summary={}
for suffix in (['-recovery'] if '--recovery' in sys.argv else ['', '-shorter']):
 tag='phase4-7-layer-validation'+suffix
 r=load(tag+'-drc.json');g=load(tag+'-scratch-geometry.json');build=load(tag+'-build.json')
 counts=collections.Counter((v['severity'],v['type']) for v in r['violations'])
 assert all(v['severity']=='warning' and v['type'].startswith('lib_') for v in r['violations'])
 assert len(r['schematic_parity'])==0
 baseline=load('phase4-7-prog-focused-diagnostic-drc.json')
 assert r['ignored_checks']==baseline['ignored_checks'], 'DRC configuration drift'
 warnings=[v for v in baseline['violations'] if v['severity']=='warning']
 assert warnings==r['violations']
 nets=collections.Counter(re.search(r'\[([^]]+)\]',v['items'][0]['description']).group(1) for v in r['unconnected_items'])
 summary[tag]=dict(non_unconnected_errors=0,unconnected_items=len(r['unconnected_items']),warnings={k[1]:v for k,v in counts.items()},schematic_parity_issues=0,ignored_checks=r['ignored_checks'],same_warnings_as_previous_native_diagnostic=True,unconnected_by_net=dict(nets),native_saved_refilled_scratch_sha256=hashlib.sha256((E/(tag+'.kicad_pcb')).read_bytes()).hexdigest(),prog_length_mm=build['prog_length_mm'],counts=build['counts'])
 with (E/(tag+'-exact-copper.csv')).open('w',newline='') as f:
  writer=csv.writer(f);writer.writerow(['action','kind','uuid','net','layer','width_mm','x1_mm','y1_mm','x2_mm','y2_mm','drill_mm'])
  m=build['moved_track_after'];writer.writerow(['F.Cu to In2.Cu','track',m['uuid'],m['net'],m['layer'],m['width'],*m['start'],*m['end'],''])
  for a in build['added_items']:
   writer.writerow(['add','via' if 'drill' in a else 'track',a['uuid'],a['net'],'F.Cu-B.Cu' if 'drill' in a else a['layer'],a['width'],*a['start'],*a['end'],a.get('drill','')])
 # Diff is evidence only: no parsing/editing of serialized design data.
 diff=difflib.unified_diff(B.read_text().splitlines(True),(E/(tag+'.kicad_pcb')).read_text().splitlines(True),fromfile='accepted-Batch1',tofile=tag)
 (E/(tag+'-native-save.diff')).write_text(''.join(diff))
base=load('c9-apply-phase4-7-batch1-final-ipc.json')
summary['production_hashes_unchanged']=all(hashlib.sha256((B.parent/n).read_bytes()).hexdigest()==v for n,v in base['hashes'].items())
assert summary['production_hashes_unchanged']
(E/('phase4-7-layer-validation'+('-recovery' if '--recovery' in sys.argv else '')+'-summary.json')).write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:({n:v[n] for n in ['non_unconnected_errors','unconnected_items','warnings','schematic_parity_issues','ignored_checks','same_warnings_as_previous_native_diagnostic','prog_length_mm']} if isinstance(v,dict) else v) for k,v in summary.items()}))
