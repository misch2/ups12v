"""Read-only comparison of saved KiCad attributes and PCB pad nets; ignores geometry.
Usage: python hardware/v4/tools/compare_attributes.py before_project_dir after_project_dir --output report.json
Use exported netlists separately to verify schematic connectivity.
"""
import argparse
import json
from pathlib import Path
from read_annotations import read_tree, child

def snapshot(directory):
    directory=Path(directory)
    result={}
    for extension,kind in [('kicad_sch','symbol'),('kicad_pcb','footprint')]:
        path=next(directory.glob('*.'+extension))
        records={}
        for n in read_tree(path)[1:]:
            if not isinstance(n,list) or n[0]!=kind: continue
            props={p[1]:p[2] for p in n if isinstance(p,list) and p[0]=='property'}
            ref=props.get('Reference')
            if not ref: continue
            flags={key:child(n,key,[key,'absent'])[1:] for key in (['exclude_from_sim','in_bom','on_board','in_pos_files','dnp'] if kind=='symbol' else ['attr'])}
            record={'properties':props,'flags':flags}
            if kind=='symbol': record['library']=child(n,'lib_id')[1]
            else:
                record['library']=n[1]
                pads={}
                for pad in n:
                    if isinstance(pad,list) and pad[0]=='pad':
                        net=child(pad,'net',['net','0',''])
                        pads.setdefault(pad[1],set()).add(net[-1] if len(net)>2 else '')
                record['pad_nets']={k:sorted(v) for k,v in pads.items()}
            records[ref]=record
        result[extension]=records
    return result

def differences(a,b):
    result={'removed':sorted(a.keys()-b.keys()),'added':sorted(b.keys()-a.keys()),'changed':{}}
    for ref in sorted(a.keys() & b.keys()):
        changes={}
        for key in a[ref].keys() | b[ref].keys():
            x,y=a[ref].get(key),b[ref].get(key)
            if x==y:continue
            if isinstance(x,dict) and isinstance(y,dict):
                changes[key]={k:{'before':x.get(k),'after':y.get(k)} for k in sorted(x.keys() | y.keys()) if x.get(k)!=y.get(k)}
            else:changes[key]={'before':x,'after':y}
        if changes:result['changed'][ref]=changes
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('before');ap.add_argument('after');ap.add_argument('--output',required=True);args=ap.parse_args()
    a,b=snapshot(args.before),snapshot(args.after)
    report={k:differences(a[k],b[k]) for k in a}
    Path(args.output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:{'removed':v['removed'],'added':v['added'],'changed_count':len(v['changed'])} for k,v in report.items()}))
