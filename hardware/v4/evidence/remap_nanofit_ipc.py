"""Bounded native IPC pad-net update; no source-file writing or GUI automation."""
from pathlib import Path
import sys, json, copy
E=Path(__file__).resolve().parent
sys.path.insert(0,str(E.parent/'ups_v4/.konnect/native-ipc'))
from kipy import KiCad
from kipy.board_types import Net, Pad
from google.protobuf.json_format import MessageToDict

k=KiCad(socket_path='ipc://C:/Users/Michal/AppData/Local/Temp/kicad/api.sock',client_name='UPS V4 approved NanoFit pad mapping')
b=k.get_board()
assert b.name=='ups12v_v4.kicad_pcb'
assert Path(b.document.project.path).resolve()==(E.parent/'ups_v4').resolve()
refs={f.id.value:f.reference_field.text.value for f in b.get_footprints()}
desired={('J2','1'):'PGND',('J2','2'):'',('J2','3'):'SYS',
         ('J8','1'):'PGND',('J8','2'):'',('J8','3'):'/F5_5V_OUT'}
existing_nets={n.name:n for n in b.get_nets()}
allpads=b.get_pads()
selected={ (refs.get(p.parent.value),p.number):p for p in allpads if p.parent and (refs.get(p.parent.value),p.number) in desired }
assert set(selected)==set(desired)
changes=[{'ref':key[0],'pad':key[1],'before':p.net.name,'after':desired[key]} for key,p in selected.items() if p.net.name!=desired[key]]
if '--apply' not in sys.argv:
    print(json.dumps({'board':b.name,'changes':changes,'selected_pads':len(selected)}))
    sys.exit(0)

before={p.id.value:copy.deepcopy(p.proto) for p in allpads}
def no_net(proto):
    p=copy.deepcopy(proto)
    p.ClearField('net')
    return p.SerializeToString(deterministic=True)
tracks_before=[p.proto.SerializeToString(deterministic=True) for p in b.get_tracks()]
vias_before=[p.proto.SerializeToString(deterministic=True) for p in b.get_vias()]
def strip_net(v):
    if isinstance(v,dict):return {k:strip_net(x) for k,x in v.items() if k!='net'}
    if isinstance(v,list):return [strip_net(x) for x in v]
    return v
fps_before={f.id.value:strip_net(MessageToDict(f.proto)) for f in b.get_footprints()}
update=[]
for key,p in selected.items():
    if p.net.name!=desired[key]:
        p.net=existing_nets[desired[key]] if desired[key] else Net()
        update.append(p)
commit=b.begin_commit()
pushed=False
try:
    result=b.update_items(update)
    assert len(result)==len(update)
    print(json.dumps({'native_update_return':[(p.number,p.net.name) for p in result]}))
    for p in result:
        assert no_net(before[p.id.value])==no_net(p.proto)
    b.push_commit(commit,'Approved NanoFit J2/J8 pin remapping only')
    pushed=True
    after={p.id.value:p for p in b.get_pads()}
    assert set(before)==set(after)
    selected_ids={p.id.value:key for key,p in selected.items()}
    for uid,old in before.items():
        new=after[uid]
        assert no_net(old)==no_net(new.proto), 'Pad geometry/attribute changed'
        if uid in selected_ids:assert new.net.name==desired[selected_ids[uid]], str((selected_ids[uid],new.net.name,desired[selected_ids[uid]]))
        else:assert old.net==new.proto.net, 'Unrelated pad net changed'
    assert tracks_before==[p.proto.SerializeToString(deterministic=True) for p in b.get_tracks()]
    assert vias_before==[p.proto.SerializeToString(deterministic=True) for p in b.get_vias()]
    assert fps_before=={f.id.value:strip_net(MessageToDict(f.proto)) for f in b.get_footprints()}, 'Footprint attributes/artwork changed'
except Exception:
    if pushed:
        restore=b.begin_commit()
        b.update_items([Pad(before[p.id.value]) for p in update])
        b.push_commit(restore,'Restore NanoFit mapping after failed verification')
    else:b.drop_commit(commit)
    raise
(E/'nanofit-ipc-remapping.json').write_text(json.dumps({'changes':changes,'pad_geometry_and_attributes_preserved':True,
    'unrelated_pad_nets_preserved':True,'tracks_vias_and_footprint_artwork_preserved':True,'undo':'one native KiCad undo transaction'},indent=2)+'\n')
print('PASS: native IPC remapping; pad geometry, all other nets, artwork and routing preserved')
