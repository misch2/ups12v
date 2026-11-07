"""Approved silk-only change through native live KiCad IPC. Never writes CAD offline."""
from pathlib import Path
import sys,json,copy
sys.dont_write_bytecode=True
E=Path(__file__).resolve().parent
if '--apply' in sys.argv:
 raise RuntimeError('Disabled: native child removal/readback and rollback did not verify. Reconcile editor state and implement a supported native workflow before further mutation.')
sys.path.insert(0,str(E.parent/'ups_v4/.konnect/native-ipc'))
from kipy import KiCad
from kipy.board_types import BoardSegment,BoardLayer
from kipy.geometry import Vector2
from kipy.proto.common.commands.editor_commands_pb2 import CreateItems,CreateItemsResponse,UpdateItems,UpdateItemsResponse
from kipy.util import pack_any
from kipy.board_types import unwrap
from google.protobuf.json_format import MessageToDict
k=KiCad(socket_path='ipc://C:/Users/Michal/AppData/Local/Temp/kicad/api.sock',client_name='Approved connector silk-only correction')
b=k.get_board();assert b.name=='ups12v_v4.kicad_pcb' and Path(b.document.project.path).resolve()==(E.parent/'ups_v4').resolve()
fps={f.reference_field.text.value:f for f in b.get_footprints()}
entry=json.loads((E/'c9-apply-recovered-ipc.json').read_text())
assert entry['hashes']==json.loads((E/'c9-apply-entry-ipc.json').read_text())['hashes'],'Recovered saved checkpoint differs'
def normalize_fields(p):
 p=copy.deepcopy(p)
 for field in ['referenceField','valueField','datasheetField','descriptionField']:
  p.get(field,{}).get('text',{}).pop('id',None)
 p['definition']['items']=sorted(p['definition']['items'],key=lambda v:json.dumps(v,sort_keys=True))
 return p
assert {f.id.value:normalize_fields(MessageToDict(f.proto)) for f in fps.values()}=={i:normalize_fields(p) for i,p in entry['footprints'].items()},'Board changed since entry beyond native undo-generated field IDs'
targets={'J1':'8183c390-abf8-42e7-a92b-913bb21ffc84','J2':'a712d60f-4836-4ebe-8833-3e8485043999','J3':'59138b52-821f-4950-8797-8cd80bb31ada','J8':'4c872a8e-1765-433a-bbab-1069741676b7'}
j7ids=['0c5ab6dd-1105-456a-b88b-a0808a684ee9','a095fbc3-b1b2-45b2-9221-05200e5c9559'];front='a62337fc-494b-4888-af36-6aa3fd392d33'
old={};plans=[]
for ref,ident in targets.items():
 f=fps[ref];g=next(s for s in f.definition.shapes if s.id.value==ident)
 assert g.layer==BoardLayer.BL_F_SilkS
 x0=min(g.top_left.x,g.bottom_right.x)/1e6;x1=max(g.top_left.x,g.bottom_right.x)/1e6
 yrear=max(g.top_left.y,g.bottom_right.y)/1e6
 old[ident]=MessageToDict(g.proto)
 plans.append((ref,g,[[[x0,30.35],[x0,yrear]],[[x0,yrear],[x1,yrear]],[[x1,yrear],[x1,30.35]]]))
for ident in j7ids+[front]:
 g=next(s for s in fps['J7'].definition.shapes if s.id.value==ident);assert g.layer==BoardLayer.BL_F_SilkS;old[ident]=MessageToDict(g.proto)
def enc(items):return {i.id.value:MessageToDict(i.proto) for i in items}
protected={name:enc(getattr(b,'get_'+name)()) for name in ['pads','tracks','vias','zones','shapes','text']}
def without_selected(f):
 p=normalize_fields(MessageToDict(f.proto))
 p['definition']['items']=[i for i in p['definition']['items'] if i.get('id',{}).get('value') not in set(old)|set(created)]
 return p
created=[];updated=[];removed=list(targets.values())+[front]
if '--apply' not in sys.argv:
 print(json.dumps(dict(mode='read-only plan',rectangle_count=len(plans),j7_trim_count=2,j7_front_remove=True)));sys.exit(0)
commit=b.begin_commit();pushed=False
try:
 for ref,g,lines in plans:
  b.remove_items(g)
  new=[]
  for a,e in lines:
   s=BoardSegment();s.layer=BoardLayer.BL_F_SilkS;s.attributes=copy.deepcopy(g.attributes)
   s.start=Vector2.from_xy_mm(*a);s.end=Vector2.from_xy_mm(*e);new.append(s)
  cmd=CreateItems();cmd.header.document.CopyFrom(b.document);cmd.header.container.CopyFrom(fps[ref].id);cmd.container.CopyFrom(fps[ref].id)
  cmd.items.extend(pack_any(s.proto) for s in new)
  result=k._client.send(cmd,CreateItemsResponse)
  objs=[unwrap(r.item) for r in result.created_items];assert len(objs)==3
  created.extend(s.id.value for s in objs)
  assert all(s.proto.parent.value==fps[ref].id.value for s in objs),'New silk not parented to footprint'
 for ident in j7ids:
  g=next(s for s in fps['J7'].definition.shapes if s.id.value==ident)
  g.end=Vector2.from_xy_mm(125.65,g.end.y/1e6)
  cmd=UpdateItems();cmd.header.document.CopyFrom(b.document);cmd.header.container.CopyFrom(fps['J7'].id);cmd.items.append(pack_any(g.proto))
  response=k._client.send(cmd,UpdateItemsResponse)
  res=b._to_concrete_items([unwrap(s.item) for s in response.updated_items])
  (E/'c9-apply-silk-update-diagnostic.json').write_text(json.dumps(dict(request=MessageToDict(g.proto),returned=[MessageToDict(s.proto) for s in res]),indent=2)+'\n')
  assert len(res)==1 and res[0].end.x==125650000 and res[0].start==g.start and res[0].end.y==g.end.y and res[0].layer==g.layer and res[0].attributes.proto==g.attributes.proto
  updated.append(ident)
 b.remove_items(next(s for s in fps['J7'].definition.shapes if s.id.value==front))
 after={f.reference_field.text.value:f for f in b.get_footprints()}
 shapes={s.id.value:s for f in after.values() for s in f.definition.shapes}
 assert all(i not in shapes for i in removed)
 assert set(created).issubset(shapes)
 assert all(shapes[i].end.x==125650000 for i in j7ids),'Trim failed readback'
 assert all(without_selected(after[r])==without_selected(fps[r]) for r in fps),'Unrelated footprint data changed'
 assert all(protected[n]==enc(getattr(b,'get_'+n)()) for n in protected),'Unrelated board geometry changed'
 b.push_commit(commit,'Approved connector silk edge cleanup only');pushed=True
 b.save()
 result=dict(applied=True,source='Native live KiCad IPC, saved through editor',removed=removed,created=created,updated=updated,protected_geometry_unchanged=True)
 (E/'c9-apply-silk-operation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result))
except Exception as error:
 record=dict(error=repr(error),pushed=pushed)
 if not pushed:
  try:b.drop_commit(commit);record['rollback']='native cancellation completed'
  except Exception as cancellation:record['rollback_error']=repr(cancellation)
 (E/'c9-apply-silk-failure.json').write_text(json.dumps(record,indent=2)+'\n')
 raise
