"""Read-only snapshot comparison, normalize runtime board and field identities."""
import json
from pathlib import Path
E=Path(__file__).resolve().parent
a=json.loads((E/'c9-apply-entry-ipc.json').read_text());b=json.loads((E/'c9-apply-recovery-verified-ipc.json').read_text())
def norm(v,fpids,field=False):
 if isinstance(v,list):return sorted([norm(x,fpids,field) for x in v],key=lambda x:json.dumps(x,sort_keys=True))
 if not isinstance(v,dict):return v
 field=field or str(v.get('@type','')).endswith('.Field')
 out={}
 for k,x in v.items():
  if k=='parent' and x.get('value') not in fpids:out[k]='RUNTIME_BOARD';continue
  if k=='id' and field:out[k]='FIELD_RUNTIME_ID';continue
  out[k]=norm(x,fpids,field)
 return out
diff=[]
def walk(a,b,p):
 if type(a)!=type(b):diff.append([p,a,b]);return
 if isinstance(a,dict):
  for k in a.keys()|b.keys():walk(a.get(k),b.get(k),p+'/'+k)
 elif isinstance(a,list):
  if len(a)!=len(b):diff.append([p+'/length',len(a),len(b)])
  for i,(x,y) in enumerate(zip(a,b)):walk(x,y,p+'/'+str(i))
 elif a!=b:diff.append([p,a,b])
for k in ['footprints','pads','tracks','vias','zones','shapes','texts']:
 walk(norm(a[k],set(a['footprints'])),norm(b[k],set(b['footprints'])),k)
out={'hashes_match':a['hashes']==b['hashes'],'normalization':'List order, runtime board parent UUID and Field-generated IDs only; other geometry/attributes checked','differences':diff}
(E/'c9-recovery-comparison.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'hashes_match':out['hashes_match'],'differences':len(diff),'first':diff[:12]}))
