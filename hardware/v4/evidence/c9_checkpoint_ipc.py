"""Read-only exact-document IPC checkpoint, full evidence on disk."""
from pathlib import Path
import sys,json,hashlib,shutil
sys.dont_write_bytecode=True
E=Path(__file__).resolve().parent
sys.path.insert(0,str(E.parent/'ups_v4/.konnect/native-ipc'))
from kipy import KiCad
from google.protobuf.json_format import MessageToDict
k=KiCad(socket_path='ipc://C:/Users/Michal/AppData/Local/Temp/kicad/api.sock',client_name='C9 approved checkpoint evidence')
b=k.get_board();B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
assert b.name==B.name and Path(b.document.project.path).resolve()==B.parent.resolve()
tag=sys.argv[1]
def rows(items):return {i.id.value:MessageToDict(i.proto) for i in items}
fps=b.get_footprints()
out=dict(board=b.name,project=b.document.project.path,footprints=rows(fps),pads=rows(b.get_pads()),tracks=rows(b.get_tracks()),vias=rows(b.get_vias()),zones=rows(b.get_zones()),shapes=rows(b.get_shapes()),texts=rows(b.get_text()),hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [B,B.with_suffix('.kicad_sch'),B.with_suffix('.kicad_pro')]},locked=[f.reference_field.text.value for f in fps if f.locked])
(E/f'c9-apply-{tag}-ipc.json').write_text(json.dumps(out,indent=2)+'\n')
if tag=='entry':
 target=E/'c9-apply-entry.kicad_pcb'
 assert not target.exists(),'Entry backup already exists; do not overwrite'
 shutil.copy2(B,target)
print(json.dumps(dict(counts={n:len(out[n]) for n in ['footprints','pads','tracks','vias','zones']},locked=out['locked'],C9=next({'xy':[f.position.x/1e6,f.position.y/1e6],'angle':f.orientation.degrees} for f in fps if f.reference_field.text.value=='C9'))))
