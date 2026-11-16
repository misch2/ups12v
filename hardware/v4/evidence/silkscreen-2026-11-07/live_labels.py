"""Reference-label-only native KiCad IPC workflow; never overwrites live CAD files."""
from pathlib import Path
import sys, json, hashlib, copy
sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
PROJECT = E.parent.parent / 'ups_v4'
sys.path.insert(0, str(PROJECT / '.konnect/native-ipc'))
from kipy import KiCad
from kipy.geometry import Vector2
from kipy.board_types import BoardLayer
from google.protobuf.json_format import MessageToDict
from kipy.proto.common.commands.editor_commands_pb2 import UpdateItems,UpdateItemsResponse
from kipy.util import pack_any

def write(name, data):
    (E/name).write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')

def connect():
    k = KiCad(socket_path='ipc://C:/Users/Michal/AppData/Local/Temp/kicad/api.sock', client_name='UPS V4 reference labels only')
    b = k.get_board()
    assert b.name == 'ups12v_v4.kicad_pcb'
    assert Path(b.document.project.path).resolve() == PROJECT.resolve()
    return k,b

def inventory(b):
    return {name: {i.id.value: MessageToDict(i.proto) for i in getattr(b, getter)()}
            for name,getter in [('footprints','get_footprints'),('pads','get_pads'),('tracks','get_tracks'),('vias','get_vias'),('zones','get_zones'),('shapes','get_shapes'),('texts','get_text')]}

def capture(tag):
    k,b = connect()
    inv = inventory(b)
    write(tag+'-ipc.json', inv)
    # Native IPC export, not a hand-edited CAD source or live-board replacement.
    (E/(tag+'.kicad_pcb')).write_text(b.get_as_string(), encoding='utf-8')
    rows=[]
    for f in b.get_footprints():
        t=f.reference_field.text
        rows.append(dict(ref=t.value, footprint_id=f.id.value, field_id=t.id.value,
                         pos=[t.position.x/1e6,t.position.y/1e6], angle=t.attributes.angle,
                         size=[t.attributes.size.x/1e6,t.attributes.size.y/1e6],
                         visible=f.reference_field.visible, layer=BoardLayer.Name(t.layer),
                         footprint_pos=[f.position.x/1e6,f.position.y/1e6]))
    write(tag+'-labels.json', rows)
    print(json.dumps(dict(captured=tag, version=str(k.get_version()), counts={n:len(v) for n,v in inv.items()},
                         examples=[r for r in rows if r['ref'] in ['SW1','SW2','C24','J1','J2','H1','J6']])))

def apply():
    k,b=connect()
    baseline=json.loads((E/'before-ipc.json').read_text())
    before=inventory(b)
    assert before==baseline, 'Live board changed after baseline capture; no mutation made'
    plan=json.loads((E/'plan.json').read_text())
    assert not plan['collisions']
    fps={f.reference_field.text.value:f for f in b.get_footprints()}
    changed=set(plan['changes'])
    expected=copy.deepcopy(before)
    updates=[]
    for ref in sorted(changed):
        f=fps[ref]; c=plan['layout'][ref]
        assert f.reference_field.visible and f.reference_field.layer==BoardLayer.BL_F_SilkS
        assert c['angle'] in [0,90]
        f.reference_field.text.position=Vector2.from_xy_mm(*c['pos'])
        f.reference_field.text.attributes.angle=c['angle']
        updates.append(f)
        expected['footprints'][f.id.value]=MessageToDict(f.proto)
    # Independently enforce that the outgoing payload changes only position / angle.
    def protected(inv):
        inv=copy.deepcopy(inv)
        for f in inv['footprints'].values():
            t=f['referenceField']['text']['text']
            if t['text'] in changed:
                t.pop('position',None)
                t['attributes'].pop('angle',None)
        return inv
    assert protected(before)==protected(expected), 'Outgoing payload exceeds label-only scope'
    commit=b.begin_commit();pushed=False
    try:
        returned=[]
        for f in updates:
            command=UpdateItems()
            command.header.document.CopyFrom(b.document)
            command.header.container.CopyFrom(f.id)
            command.items.append(pack_any(f.reference_field.proto))
            response=k._client.send(command,UpdateItemsResponse)
            returned.extend(response.updated_items)
        assert len(returned)==len(updates), 'Incomplete native field update'
        after=inventory(b)
        write('applied-ipc.json',after)
        assert after==expected, 'Live readback differs from exact expected reference-only result'
        assert protected(before)==protected(after), 'Protected geometry changed'
        b.push_commit(commit,'Improve reference label readability: positions and 0/90 degree angles only')
        pushed=True
        b.save()
        write('apply-result.json',dict(applied=True,source='live_native_ipc',saved_through_editor=True,
                                      changed_references=sorted(changed),changed_count=len(changed),
                                      exact_expected_readback=True,protected_geometry_unchanged=True))
        print(json.dumps(dict(applied=True,changed=len(changed),protected_geometry_unchanged=True,saved=True)))
    except Exception as e:
        result=dict(error=repr(e),commit_pushed=pushed)
        if not pushed:
            try:
                b.drop_commit(commit)
                result['rollback_verified']=inventory(b)==before
            except Exception as rollback:
                result['rollback_error']=repr(rollback)
        write('apply-failure.json',result)
        raise

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--apply':apply()
    else:capture(sys.argv[1] if len(sys.argv)>1 else 'before')
