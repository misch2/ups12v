"""Compare the fresh read-only IPC snapshot with the authoritative entry."""
import ast, copy, hashlib, json
from pathlib import Path
E=Path(__file__).resolve().parent
ns={'json':json,'diff':[]}
tree=ast.parse((E/'verify_c9_recovery.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<existing normalization>','exec'),ns)
a=json.loads((E/'c9-apply-entry-ipc.json').read_text())
b=json.loads((E/'c9-apply-recovery-confirmed-ipc.json').read_text())
sections=['footprints','pads','tracks','vias','zones','shapes','texts']
for key in sections:
    ns['walk'](ns['norm'](a[key],set(a['footprints'])),ns['norm'](b[key],set(b['footprints'])),key)
diff=ns['diff']
# Four custom-pad primitive UUIDs are regenerated on native reload. Only their
# IDs differ; geometry, pad stacks and owner pad UUIDs remain checked above.
runtime_only=all('/customShapes/' in p and p.endswith('/id/value') for p,old,new in diff)
assert runtime_only, 'Unexpected geometry/attribute difference: inspect evidence'
assert a['hashes']==b['hashes'], 'Saved checkpoint hash changed'
B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
assert hashlib.sha256(B.read_bytes()).hexdigest()==hashlib.sha256((E/'c9-apply-entry.kicad_pcb').read_bytes()).hexdigest()
out={'saved_pcb_schematic_project_hashes_match':True,'saved_PCB_matches_entry_backup':True,
     'all_geometry_connectivity_attributes_match':True,'sections':sections,
     'normalization':'List ordering; runtime board-parent UUID; generated standard-field UUIDs; only the four regenerated IC1 custom-pad primitive UUIDs (8 occurrences, full geometry preserved)',
     'custom_primitive_id_differences':diff,'live_counts':{k:len(b[k]) for k in sections},
     'hashes':b['hashes'],'source':'Fresh exact-document IPC read, after owner discarded transaction and reopened'}
(E/'reopened-checkpoint-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['custom_primitive_id_differences','hashes','sections','normalization']}))
