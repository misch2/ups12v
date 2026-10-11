"""Read-only saved CAD preservation evidence; never writes CAD sources."""
from pathlib import Path
import json,re,sys,hashlib
P=Path(__file__).resolve().parent
B=P.parent/'ups_v4/ups12v_v4.kicad_pcb'
S=B.with_suffix('.kicad_sch')
def parse(text):
    stack=[]
    for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text):
        if t=='(':
            n=[]
            if stack: stack[-1].append(n)
            stack.append(n)
        elif t==')': root=stack.pop()
        else: stack[-1].append(t[1:-1] if t.startswith('"') else t)
    assert not stack
    return root
def many(n,k): return [x for x in n if isinstance(x,list) and x and x[0]==k]
def one(n,k): return next(iter(many(n,k)),None)
def ref(n): return next(x[2] for x in many(n,'property') if x[1]=='Reference')
def dump(name,obj): (P/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':
    mode=sys.argv[1]
    board=parse(B.read_text(encoding='utf-8')); sch=parse(S.read_text(encoding='utf-8'))
    if mode=='capture':
        dump('nanofit-cad-entry.json',{'board':board,'schematic':sch})
        print(json.dumps({'footprints':len(many(board,'footprint')),'tracks':len(many(board,'segment')),'vias':len(many(board,'via'))}))
    elif mode=='inspect':
        print(json.dumps({'wires_near_connectors':[w for w in many(sch,'wire') if any((35<float(p[1])<125 and 20<float(p[2])<35) or (400<float(p[1])<430 and 465<float(p[2])<485) for p in many(one(w,'pts'),'xy'))],'labels_near_J8':[l for l in many(sch,'label') if 400<float(one(l,'at')[1])<430 and 465<float(one(l,'at')[2])<485]},indent=2))
