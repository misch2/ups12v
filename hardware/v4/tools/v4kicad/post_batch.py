"""Read-only production checks and exported native preservation; no CAD mutations."""
from pathlib import Path
from collections import Counter
import argparse
import re
from .safety import read_json,write_json,verify_hashes,require,run_monitored
from .checks import parse_check
from .geometry import preservation


def check_production(board,manifest,root,cli):
    hashes=read_json(manifest)['hashes'];verify_hashes(board.parent,hashes)
    result={}
    for kind in ['drc','erc']:
        report=root/('production-'+kind+'.json')
        require(not report.exists(),'Check already exists; STOP')
        if kind=='drc':
            command=[cli,'pcb','drc','--format','json','--all-track-errors','--schematic-parity','--output',report,board]
        else:
            command=[cli,'sch','erc','--format','json','--output',report,board.with_suffix('.kicad_sch')]
        run_monitored(command,root/('production-'+kind+'.log'));verify_hashes(board.parent,hashes)
        result[kind]=parse_check(read_json(report),kind)
        write_json(root/('production-'+kind+'-summary.json'),result[kind])
        require(result[kind]['errors']==0 and result[kind].get('parity',0)==0,'Unexpected production check failure; STOP')
    write_json(root/'production-checks.json',result)
    return result


def verify_exported(before,after,plan,root,baseline_drc):
    a,b,p=read_json(before),read_json(after),read_json(plan)
    result=preservation(a,b)
    added_tracks=[t for u,t in b['tracks'].items() if u not in a['tracks']]
    added_vias=[v for u,v in b['vias'].items() if u not in a['vias']]
    require(Counter((t['net'],t['layer'],t['width'],*t['start'],*t['end']) for t in added_tracks)==
            Counter(tuple(t) for t in p['tracks']),'Added track geometry differs from plan; STOP')
    require(all(len(v['copper_widths'])==4 and len(set(v['copper_widths'].values()))==1 for v in added_vias),
            'Unexpected per-layer via widths; STOP')
    require(Counter((v['net'],*v['position'],next(iter(v['copper_widths'].values())),v['drill']) for v in added_vias)==
            Counter(tuple(v) for v in p['vias']),'Added via geometry differs from plan; STOP')
    d=read_json(root/'production-drc.json');old=read_json(baseline_drc)
    warnings=lambda q:Counter((v.get('type',v.get('rule')),v['description']) for v in q['violations'] if v['severity']=='warning')
    require(warnings(d)==warnings(old),'Unexpected warning changes; STOP')
    require(d['ignored_checks']==old['ignored_checks'],'Ignored checks changed; STOP')
    remaining={}
    for v in d['unconnected_items']:
        descriptions=[i['description'] for i in v['items']]
        nets=set(n for text in descriptions for n in re.findall(r'\[([^\]]+)\]',text))
        for n in nets:remaining.setdefault(n,[]).append(descriptions)
    write_json(root/'remaining-by-net.json',remaining)
    result.update(exact_added_plan=True,warnings_unchanged=True,counts={k:len(b[k]) for k in b},
                  ground_fill_contours={z['net']:{l:len(polys) for l,polys in z['layers'].items()} for z in b['zones'].values()})
    write_json(root/'native-preservation.json',result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
    c=sub.add_parser('check');c.add_argument('--board',type=Path,required=True);c.add_argument('--manifest',type=Path,required=True)
    c.add_argument('--root',type=Path,required=True);c.add_argument('--cli',required=True)
    v=sub.add_parser('verify');v.add_argument('--before',required=True);v.add_argument('--after',required=True)
    v.add_argument('--plan',required=True);v.add_argument('--root',type=Path,required=True);v.add_argument('--baseline-drc',required=True)
    a=p.parse_args()
    if a.action=='check':print(check_production(a.board,a.manifest,a.root,a.cli))
    else:print(verify_exported(a.before,a.after,a.plan,a.root,a.baseline_drc))
