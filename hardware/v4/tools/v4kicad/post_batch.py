"""Read-only production checks and exported native preservation; no CAD mutations."""
from pathlib import Path
from collections import Counter
import argparse
import re
import copy
import shutil
from .safety import read_json,write_json,verify_hashes,require,run_monitored
from .checks import parse_check
from .geometry import preservation


def verify_u3_full(entry_native,after_native,root,candidate,baseline_erc,plan):
    """Full bounded live/native preservation and actual-plane proof after U3 install."""
    from .ipc_install import SECTIONS,comparable
    from .ipc_u3 import check_candidate,POSITIONS
    from .safety import digest
    check_candidate(plan,candidate)
    a=read_json(entry_native/'native-audit.json');b=read_json(after_native/'native-audit.json')
    c=read_json(candidate/'native-audit.json')
    require(b==c,'Native artwork/zone audit differs from accepted U3 candidate; STOP')
    require(a['zones']==b['zones'] and a['drawings']==b['drawings'],'Zone/RF/board artwork changed; STOP')
    require(all(v==b['footprint_graphics'][k] for k,v in a['footprint_graphics'].items() if k not in POSITIONS),
            'Unrelated footprint artwork changed; STOP')
    layout=read_json(after_native/'layout.json');expected=read_json(candidate/'layout-final.json')
    require(layout['plane_samples']==expected['plane_samples'],'Native PGND fill grid differs; STOP')
    probes=lambda rows:sorted((p['net'],tuple(p['position']),p['center'],tuple(p['ring'])) for p in rows)
    require(probes(layout['via_plane_samples'])==probes(expected['via_plane_samples']),
            'Via/PGND plane probes differ; STOP')
    old=read_json(root/'live-before.json');final=read_json(root/'live-final.json')
    prepared=read_json(root/'live-placement-expected.json')
    for section in SECTIONS:
        if section=='zones':
            stripped=lambda rows:{u:{k:v for k,v in item.items() if k!='filledPolygons'} for u,item in rows.items()}
            require(stripped(old[section])==stripped(final[section]),'Live zone definitions changed; STOP')
        elif section in ['footprints','pads']:
            require(comparable(final[section])==comparable(prepared[section]),f'Live {section} differs; STOP')
        else:
            require(all(final[section][u]==v for u,v in old[section].items()),f'Original live {section} changed; STOP')
    warnings=lambda q:Counter((v['type'],v['description']) for s in q['sheets'] for v in s['violations'] if v['severity']=='warning')
    require(warnings(read_json(root/'production-erc.json'))==warnings(read_json(baseline_erc)),
            'Production ERC warnings changed; STOP')
    actual=read_json(root/'remaining-by-net.json');planned=read_json(candidate.parent/'phase4-8-u3-proposal-remaining-by-net.json')
    require({k:len(v) for k,v in actual.items()}=={k:len(v) for k,v in planned.items()},
            'Remaining net counts differ from accepted U3 candidate; STOP')
    manifest=read_json(root/'installed-manifest.json')
    source=Path(read_json(after_native/'context.json')['source'])
    verify_hashes(source.parent,manifest['hashes'])
    accepted=copy.deepcopy(final);accepted.update(manifest)
    write_json(root/'accepted-installed-baseline.json',accepted)
    shutil.copy2(plan,after_native/'plan.json')
    result=dict(full_live_retained_geometry_matches_expected=True,
        native_all_footprints_pads_and_artwork_match_accepted_candidate=True,zone_definitions_RF_rules_and_board_artwork_preserved=True,
        actual_native_PGND_fill_grid_equals_accepted=True,via_plane_probes_equal_accepted=True,production_ERC_warning_multiset_unchanged=True,
        production_DRC_verification=read_json(root/'native-preservation.json'),remaining_net_counts_equal_accepted=True,
        production_hashes=manifest['hashes'],plan_sha256=digest(plan))
    write_json(root/'full-preservation.json',result)
    return result


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


def verify_exported(before,after,plan,root,baseline_drc,u3_candidate=None):
    a,b,p=read_json(before),read_json(after),read_json(plan)
    if u3_candidate:
        from .ipc_u3 import check_candidate
        from .geometry import verify_placement_geometry
        check_candidate(plan,u3_candidate)
        candidate=read_json(Path(u3_candidate)/'final-snapshot.json')
        require(b['footprints']==candidate['footprints'] and b['pads']==candidate['pads'],
                'Production footprint/pad geometry differs from accepted native U3 candidate; STOP')
        placed=dict(a,footprints=candidate['footprints'],pads=candidate['pads'])
        verify_placement_geometry(a,placed,p['placements'])
        a=placed
    else:
        require(not p.get('placements'),'Explicit approved U3 candidate required for placement verification; STOP')
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
                  exact_approved_u3_placements=bool(u3_candidate),
                  ground_fill_contours={z['net']:{l:len(polys) for l,polys in z['layers'].items()} for z in b['zones'].values()})
    write_json(root/'native-preservation.json',result)
    return result


def verify_add_only_full(entry_native, after_native, root, baseline_erc, baseline_drc, plan):
    """Exact live non-fill preservation plus independent saved native evidence."""
    from .ipc_install import SECTIONS, comparable
    result = verify_exported(entry_native/'snapshot.json', after_native/'snapshot.json',
                             plan, root, baseline_drc)
    old, final = read_json(root/'live-before.json'), read_json(root/'live-final.json')
    for section in SECTIONS:
        for uid, value in old[section].items():
            require(uid in final[section], 'Original live item missing; STOP')
            after = final[section][uid]
            if section == 'zones':
                value = {k:v for k,v in value.items() if k != 'filledPolygons'}
                after = {k:v for k,v in after.items() if k != 'filledPolygons'}
            require(comparable(value) == comparable(after), f'Original live {section} changed; STOP')
        if section not in ['tracks','vias']:
            require(set(old[section]) == set(final[section]), 'Unexpected live item added; STOP')
    warnings = lambda q: Counter((v['type'],v['description']) for s in q['sheets']
        for v in s['violations'] if v['severity']=='warning')
    require(warnings(read_json(root/'production-erc.json')) == warnings(read_json(baseline_erc)),
            'Production ERC warnings changed; STOP')
    manifest = read_json(root/'installed-manifest.json')
    source = Path(read_json(after_native/'context.json')['source'])
    verify_hashes(source.parent, manifest['hashes'])
    accepted = copy.deepcopy(final); accepted.update(manifest)
    write_json(root/'accepted-installed-baseline.json', accepted)
    result.update(full_live_artwork_models_fields_and_zone_definitions_preserved=True,
                  ERC_warning_multiset_unchanged=True, production_hashes=manifest['hashes'])
    write_json(root/'full-preservation.json', result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
    c=sub.add_parser('check');c.add_argument('--board',type=Path,required=True);c.add_argument('--manifest',type=Path,required=True)
    c.add_argument('--root',type=Path,required=True);c.add_argument('--cli',required=True)
    v=sub.add_parser('verify');v.add_argument('--before',required=True);v.add_argument('--after',required=True)
    v.add_argument('--plan',required=True);v.add_argument('--root',type=Path,required=True);v.add_argument('--baseline-drc',required=True)
    v.add_argument('--u3-candidate',type=Path)
    f=sub.add_parser('full-u3',help='Read-only full U3 live/native/plane preservation proof')
    for name in ['entry-native','after-native','root','candidate','baseline-erc','plan']:
        f.add_argument('--'+name,type=Path,required=True)
    f=sub.add_parser('full-add',help='Read-only full addition-only batch preservation')
    for name in ['entry-native','after-native','root','baseline-erc','baseline-drc','plan']:
        f.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.action=='check':print(check_production(a.board,a.manifest,a.root,a.cli))
    elif a.action=='full-add':
        result=verify_add_only_full(a.entry_native,a.after_native,a.root,a.baseline_erc,a.baseline_drc,a.plan)
        print(dict(full_preservation=True,counts=result['counts'],production_hashes=result['production_hashes']))
    elif a.action=='full-u3':
        result=verify_u3_full(a.entry_native,a.after_native,a.root,a.candidate,a.baseline_erc,a.plan)
        print(dict(full_preservation=True,production_hashes=result['production_hashes']))
    else:print(verify_exported(a.before,a.after,a.plan,a.root,a.baseline_drc,a.u3_candidate))
