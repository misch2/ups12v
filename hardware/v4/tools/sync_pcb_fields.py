"""Copy selected schematic property values to a closed PCB using S-expression spans.
Dry run by default; --apply writes. Existing field geometry is preserved; new
fields are hidden on F.Fab. Does not change copper, native attributes or values.
"""
import argparse
import json
import os
from pathlib import Path
import re
import uuid

TOKEN=re.compile(r'\s+|[()]|"(?:\\.|[^"\\])*"|[^()\s]+')
def parse(text):
    stack=[];root=None
    for m in TOKEN.finditer(text):
        t=m.group()
        if t.isspace():continue
        if t=='(':
            n=[m.start(),None,[]]
            if stack:stack[-1][2].append(n)
            else:root=n
            stack.append(n)
        elif t==')':stack.pop()[1]=m.end()
        else:stack[-1][2].append((m.start(),m.end(),json.loads(t) if t.startswith('"') else t))
    if stack or root is None:raise ValueError('Unbalanced input')
    return root

def nodes(n,tag):return [x for x in n[2] if isinstance(x,list) and x[2][0][2]==tag]
def props(n):return {x[2][1][2]:x for x in nodes(n,'property')}
def records(root,tag):
    result={}
    for n in nodes(root,tag):
        p=props(n)
        if 'Reference' in p:
            ref=p['Reference'][2][2][2]
            if ref in result:raise ValueError('Duplicate reference '+ref)
            result[ref]=(n,p)
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('schematic',type=Path);ap.add_argument('pcb',type=Path)
    ap.add_argument('--fields',nargs='+',default=['PopulationGroup','Purpose','Description'])
    ap.add_argument('--apply',action='store_true');ap.add_argument('--report',type=Path,required=True)
    args=ap.parse_args()
    if args.apply and any(args.pcb.parent.glob('*.lck')):raise ValueError('Close KiCad before applying')
    raw=args.pcb.read_bytes();text=raw.decode('utf-8');nl='\r\n' if '\r\n' in text else '\n'
    sch=records(parse(args.schematic.read_text(encoding='utf-8')),'symbol')
    pcb=records(parse(text),'footprint');patches=[];changes=[]
    for ref,(foot,fields) in pcb.items():
        if ref not in sch:raise ValueError('No schematic symbol for '+ref)
        source=sch[ref][1];new=[]
        for name in args.fields:
            if name not in source:continue
            value=source[name][2][2][2];old=fields.get(name)
            if old and old[2][2][2]==value:continue
            changes.append({'reference':ref,'field':name,'before':old[2][2][2] if old else None,'after':value})
            if old:
                atom=old[2][2];patches.append((atom[0],atom[1],json.dumps(value,ensure_ascii=False)))
            else:
                new.append('\t\t(property '+json.dumps(name)+' '+json.dumps(value,ensure_ascii=False)+nl+'\t\t\t(at 0 0 0)'+nl+'\t\t\t(layer "F.Fab")'+nl+'\t\t\t(hide yes)'+nl+'\t\t\t(uuid "'+str(uuid.uuid4())+'")'+nl+'\t\t\t(effects (font (size 0.8 0.8) (thickness 0.15))))'+nl)
        if new:
            anchor=next(x for x in foot[2] if isinstance(x,list) and x[2][0][2]=='property')
            patches.append((anchor[0],anchor[0],''.join(new)+'\t\t'))
    out=text
    for a,b,s in sorted(patches,reverse=True):out=out[:a]+s+out[b:]
    result=records(parse(out),'footprint')
    for ref,(_,fields) in result.items():
        for name in args.fields:
            if name in sch[ref][1]:assert fields[name][2][2][2]==sch[ref][1][name][2][2][2]
    if args.apply and patches:
        if args.pcb.read_bytes()!=raw:raise ValueError('PCB changed during operation')
        tmp=args.pcb.with_suffix('.field-sync.tmp');tmp.write_bytes(out.encode('utf-8'));os.replace(tmp,args.pcb)
    args.report.write_text(json.dumps({'applied':args.apply,'changes':changes},indent=2)+'\n',encoding='utf-8')
    from collections import Counter
    print(json.dumps({'applied':args.apply,'changes':dict(Counter(x['field'] for x in changes))}))

if __name__=='__main__':main()
