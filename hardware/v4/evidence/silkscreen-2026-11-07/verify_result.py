"""Independent saved/native evidence comparison for the reference-only change."""
from pathlib import Path
import json,copy,hashlib,re,subprocess,math
E=Path(__file__).resolve().parent
read=lambda n:json.loads((E/n).read_text(encoding='utf-8-sig'))
before=read('before-ipc.json'); after=read('after-ipc.json');plan=read('plan.json')
def protected(d):
    d=copy.deepcopy(d)
    for f in d['footprints'].values():
        if f['referenceField']['text']['text']['text'] in plan['changes']:
            t=f['referenceField']['text']['text'];t.pop('position',None);t['attributes'].pop('angle',None)
    return d
assert protected(before)==protected(after)
geometry=read('after-geometry.json')
rows=[r for r in geometry['labels'] if r['visible'] and r['layer']=='F.Silkscreen']
def intersects(a,b,gap=0):
    return a[0]<b[2]+gap-2e-6 and a[2]>b[0]-gap+2e-6 and a[1]<b[3]+gap-2e-6 and a[3]>b[1]-gap+2e-6
overlaps=[];margins=[]
for i,r in enumerate(rows):
    q=r['text_box'];c=plan['layout'][r['ref']]
    assert r['angle'] in [0,90]
    assert math.dist(r['pos'],c['pos'])<.000002
    assert max(abs(x-y) for x,y in zip(q,c['box']))<.00001
    assert q[0]>=30.15 and q[1]>=30.15 and q[2]<=125.85 and q[3]<=99.85
    for f in geometry['labels']:
        if intersects(q,f['body'],.04):overlaps.append([r['ref'],f['ref'],'body'])
        for p in f['pads']:
            if intersects(q,p,.15):overlaps.append([r['ref'],f['ref'],'pad'])
    for s in geometry['static']:
        if intersects(q,s['box'],.04):overlaps.append([r['ref'],s['text'],'static'])
    for s in rows[:i]:
        if intersects(q,s['text_box'],.18):overlaps.append([r['ref'],s['ref'],'reference'])
assert not overlaps,overlaps
for h in read('protected-file-hashes.json'):
    assert hashlib.sha256(Path(h['Path']).read_bytes()).hexdigest().upper()==h['Hash']
def drc_ids(name):
    d=read(name)
    return sorted(json.dumps(dict(rule=v['rule'],severity=v['severity'],description=v['description'],items=sorted(i['uuid'] for i in v['items'])),sort_keys=True) for v in d['violations'])
assert drc_ids('baseline-project-drc.json')==drc_ids('final-project-drc.json')
report=read('final-project-drc.json')
assert not report['unconnected_items'] and not report['schematic_parity']
assert not [v for v in report['violations'] if v['severity']=='error']
patch=subprocess.check_output(['git','diff','--unified=0','--','hardware/v4/ups_v4/ups12v_v4.kicad_pcb'],text=True)
changed_lines=[line for line in patch.splitlines() if line[:1] in ['+','-'] and not line.startswith(('+++','---'))]
assert len(changed_lines)==242
assert all(re.fullmatch(r'[+-]\s+\(at [-\d.]+ [-\d.]+(?: [-\d.]+)?\)',line) for line in changed_lines)
result=dict(visible_references_checked=len(rows),modified_references=len(plan['changes']),
            orientations_degrees=[0,90],reference_overlaps=0,body_overlaps=0,pad_overlaps=0,
            actual_saved_geometry_matches_plan=True,native_protected_geometry_unchanged=True,
            schematic_project_rules_hashes_unchanged=True,git_diff_only_121_reference_at_lines=True,
            drc=dict(errors=0,unconnected=0,schematic_parity=0,existing_warnings=len(report['violations']),warning_identities_unchanged=True),
            checks=dict(body_envelope_clearance_mm=.04,pad_bounding_box_clearance_mm=.15,reference_clearance_mm=.18),
            limitations=['No hardware verification; silkscreen-only change.','Mounting-hole envelopes use the physical NPTH hole, not the screw courtyard.','No ERC rerun because schematic is hash-identical; no design release.'])
(E/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
