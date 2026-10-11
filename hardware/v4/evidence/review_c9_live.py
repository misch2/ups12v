"""Read-only native IPC corroboration of saved KiCad API capture."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
E=Path(__file__).resolve().parent
sys.path.insert(0,str(E.parent/'ups_v4/.konnect/native-ipc'))
from kipy import KiCad
from google.protobuf.json_format import MessageToDict
k=KiCad(socket_path='ipc://C:/Users/Michal/AppData/Local/Temp/kicad/api.sock',client_name='Read only C9 local review')
b=k.get_board()
assert b.name=='ups12v_v4.kicad_pcb' and Path(b.document.project.path).resolve()==(E.parent/'ups_v4').resolve()
d=json.loads((E/'c9-review-geometry.json').read_text())
tracks=b.get_tracks();vias=b.get_vias();pads=b.get_pads();zones=b.get_zones()
nm={p['uuid']:p for f in d['footprints'] for p in f['pads']}
assert set(nm)=={p.id.value for p in pads}
assert all(nm[p.id.value]['xy']==[round(p.position.x/1e6,6),round(p.position.y/1e6,6)] and nm[p.id.value]['net']==p.net.name for p in pads)
nv={v['uuid']:v for v in d['vias']}
assert set(nv)=={v.id.value for v in vias}
assert all(nv[v.id.value]['xy']==[round(v.position.x/1e6,6),round(v.position.y/1e6,6)] and nv[v.id.value]['net']==v.net.name for v in vias)
nt={t['uuid']:t for t in d['tracks']}
assert set(nt)=={t.id.value for t in tracks}
assert all(nt[t.id.value]['start']==[round(t.start.x/1e6,6),round(t.start.y/1e6,6)] and nt[t.id.value]['end']==[round(t.end.x/1e6,6),round(t.end.y/1e6,6)] and abs(nt[t.id.value]['width']-t.width/1e6)<1e-7 and nt[t.id.value]['net']==t.net.name for t in tracks)
out=dict(board=b.name,project=b.document.project.path,source='Live native IPC; no mutations',pad_positions_nets_match=True,track_positions_widths_nets_match=True,via_positions_nets_match=True,counts=dict(pads=len(pads),tracks=len(tracks),vias=len(vias)),zones=[MessageToDict(z.proto) for z in zones])
(E/'c9-review-live-parity.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({a:v for a,v in out.items() if a!='zones'}))
