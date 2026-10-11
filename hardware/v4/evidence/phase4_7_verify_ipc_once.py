"""Owner-approved single read-only kipy snapshot; no native pcbnew imports."""
from pathlib import Path
import hashlib,json,runpy,sys
sys.dont_write_bytecode=True
E=Path(__file__).resolve().parent
B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
tag='phase4-7-post-assertion-approved'
target=E/f'c9-apply-{tag}-ipc.json'
report=E/'phase4-7-post-assertion-verification.json'
assert not target.exists() and not report.exists(), 'One-shot evidence exists; do not repeat IPC'
base=json.loads((E/'c9-apply-approved-final-ipc.json').read_text())
def hashes():
 return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [B,B.with_suffix('.kicad_sch'),B.with_suffix('.kicad_pro')]}
before=hashes()
# Snapshot script only queries item protos; this tag never enters its backup branch.
sys.argv=[str(E/'c9_checkpoint_ipc.py'),tag]
runpy.run_path(sys.argv[0],run_name='__main__')
live=json.loads(target.read_text())
identity=live['board']==B.name and Path(live['project']).resolve()==B.parent.resolve()
matches={n:live[n]==base[n] for n in ['footprints','pads','tracks','vias','zones','shapes','texts']}
after=hashes()
baseline_hashes={n:after[n]==base['hashes'][n] for n in after}
out=dict(source='one read-only kipy IPC protobuf snapshot; ordinary file SHA256 reads',
 exact_identity_match=identity,board=live['board'],project=live['project'],
 object_matches=matches,counts={n:len(live[n]) for n in matches},
 hashes_before=before,hashes_after=after,hashes_unchanged=before==after==live['hashes'],
 approved_checkpoint_hash_matches=baseline_hashes,
 passed=identity and all(matches.values()) and before==after==live['hashes'] and all(baseline_hashes.values()),
 operations_excluded=['pcbnew','LoadBoard','native geometry getters','save','refill','DRC','routing','revert','close','restart'],
 assertion_observed_in_command_output=False)
report.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['exact_identity_match','object_matches','counts','hashes_unchanged','approved_checkpoint_hash_matches','passed']}))
if not out['passed']: raise SystemExit('STOP: verification differs; no retry or recovery')
