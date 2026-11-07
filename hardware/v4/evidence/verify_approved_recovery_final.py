"""Read-only saved CAD preservation after approved installation and IPC refill."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
from verify_nanofit import parse,many,one,ref
E=Path(__file__).resolve().parent
B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def norm(v):
    if not isinstance(v,list):return v
    return sorted([norm(x) for x in v],key=lambda x:json.dumps(x,sort_keys=True))
def strip_fills(tree):
    for z in many(tree,'zone'):
        z[:]=[x for x in z if not(isinstance(x,list) and x and x[0] in ['filled_polygon','fill_segments'])]
    return tree
candidate=parse((E/'recovery-approved-combined-candidate.kicad_pcb').read_text())
saved=parse(B.read_text())
assert norm(strip_fills(candidate))==norm(strip_fills(saved)), 'Unexpected change beyond recalculated zone fills'
entry=json.loads((E/'c9-apply-entry-ipc.json').read_text())['hashes']
for name,h in entry.items():
    if name!=B.name:assert digest(B.parent/name)==h,name
counts={'footprints':len(many(saved,'footprint')),'tracks':len(many(saved,'segment')),'vias':len(many(saved,'via')),'zones':len(many(saved,'zone'))}
assert counts=={'footprints':154,'tracks':240,'vias':134,'zones':2}
c9=next(f for f in many(saved,'footprint') if ref(f)=='C9')
assert one(c9,'at')==['at','61.1','69.1']
report={'native_candidate_preserved_except_recalculated_zone_fills':True,
 'preservation_chain':['revised-c9-candidate-preservation.json','recovery-approved-combined-candidate-verification.json'],
 'schematic_and_project_hashes_unchanged':True,'counts':counts,'C9_mm':[61.1,69.1],
 'C9_angle_degrees':0,'PCB_sha256':digest(B),'failed_IPC_operation_reused':False}
(E/'approved-c9-artwork-final-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
