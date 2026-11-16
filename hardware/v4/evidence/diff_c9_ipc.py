from pathlib import Path
import json,sys
E=Path(__file__).resolve().parent
a=json.loads((E/'c9-apply-entry-ipc.json').read_text());b=json.loads((E/f'c9-apply-{sys.argv[1]}-ipc.json').read_text())
diff=[]
def walk(a,b,p=''):
 if type(a)!=type(b):diff.append([p,a,b]);return
 if isinstance(a,dict):
  for k in a.keys()|b.keys():walk(a.get(k),b.get(k),p+'/'+k)
 elif isinstance(a,list):
  if len(a)!=len(b):diff.append([p+'/length',len(a),len(b)])
  for i,(x,y) in enumerate(zip(a,b)):walk(x,y,p+'/'+str(i))
 elif a!=b:diff.append([p,a,b])
walk(a['footprints'],b['footprints'])
(E/f'c9-apply-{sys.argv[1]}-diff.json').write_text(json.dumps(diff,indent=2)+'\n')
print(json.dumps(dict(differences=len(diff),paths=[r[0] for r in diff[:35]])))
