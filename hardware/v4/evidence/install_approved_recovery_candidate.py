"""Guarded installation of native-saved CAD while PCB Editor is closed.

Owner approved C9 (61.1,69.1)/0 and confirmed editor closed 2026-10-11.
Never use while an editor is open; never modifies serialized CAD content.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess
E=Path(__file__).resolve().parent
B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
C=E/'recovery-approved-combined-candidate.kicad_pcb'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
entry=json.loads((E/'c9-apply-entry-ipc.json').read_text())['hashes']
proof=json.loads((E/'recovery-approved-combined-candidate-verification.json').read_text())
assert proof['all_non_target_silk_source_objects_equal'] and proof['native_save_reload']
assert digest(C)==proof['candidate_hash']
for name,h in entry.items():assert digest(B.parent/name)==h,name+' changed since entry'
process=subprocess.run(['tasklist','/FI','IMAGENAME eq pcbnew.exe','/FO','CSV','/NH'],capture_output=True,text=True,check=True)
assert 'pcbnew.exe' not in process.stdout.lower(),'PCB Editor process is running'
locks=list(B.parent.glob('*kicad_pcb.lck'))
assert not locks,repr(locks)
shutil.copyfile(C,B)
assert digest(B)==proof['candidate_hash']
for name,h in entry.items():
    if name!=B.name:assert digest(B.parent/name)==h
(E/'approved-recovery-installation.json').write_text(json.dumps({
    'owner_C9_approval':True,'owner_editor_closed_confirmation':True,
    'PCB_editor_process_absent':True,'PCB_lock_absent':True,
    'entry_hashes_verified':True,'installed_native_candidate':C.name,
    'installed_hash':digest(B),'schematic_and_project_unchanged':True,
    'general_routing':False,'failed_IPC_operation_reused':False},indent=2)+'\n')
print('Installed verified native candidate; schematic/project unchanged.')
