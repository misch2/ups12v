"""Phase4.13 exact reconciliation and candidate-gated native-editor adoption.

Import-safe. No serialized CAD writer. The identical mapped operations must pass
an isolated production-derived editor and independent native proof before adoption.
"""
from pathlib import Path
from collections import Counter
import argparse
import copy
import json
import sys

from .safety import (require, read_json, write_json, digest, verify_hashes,
                     prepare_scratch, run_monitored, ToolError)

BASE = Path('hardware/v4')
PRODUCTION = BASE/'ups_v4/ups12v_v4.kicad_pcb'
OWNER = BASE/'evidence/phase4-10-owner-editable-scratch/ups12v_v4.kicad_pcb'
MANIFEST = BASE/'evidence/phase4-10-independent-ipc/accepted-installed-baseline.json'
ACCEPTED = '6d692e893773a28c690c359ca7e7583b54a7b8effe03ffa9844131a36a6c0f80'
APPROVED = '55fe96f32e8e440996924239dd1409f84cb0ffc27cb30c7ea48c7e6c02f610f5'
OWNER_REVIEW = BASE/'evidence/phase4-12-owner-correction-confirmation-2026-10-17'
CONTROL = BASE/'evidence/phase4-11-accepted-control-native'
PREFLIGHT = BASE/'evidence/phase4-13-production-preflight'
RENAMES = {'Net-(U1-USB_D+_{slash}_GPIO19)': '/USB_MCU_DP',
           'Net-(U1-USB_D-_{slash}_GPIO18)': '/USB_MCU_DN'}
SECTIONS = ('tracks', 'vias', 'footprints', 'pads')


def semantic_capture(value):
    """Preserve every payload; footprint definition.items is an unordered set.

    C37/L2 editor reload changed only item order, independently demonstrated by
    exact full-payload multisets. Do not normalize polygons, models or UUIDs.
    """
    from .ipc_install import comparable
    result=comparable(value)
    if isinstance(result,dict):
        for item in result.values():
            if isinstance(item,dict) and isinstance(item.get('definition'),dict):
                definition=item['definition']
                if isinstance(definition.get('items'),list):
                    definition['items']=sorted(definition['items'],key=lambda x:json.dumps(x,sort_keys=True))
    return result


def delta(a, b):
    return dict(added={u:b[u] for u in sorted(b.keys()-a.keys())},
                removed={u:a[u] for u in sorted(a.keys()-b.keys())},
                modified={u:dict(before=a[u], after=b[u])
                          for u in sorted(a.keys()&b.keys()) if a[u]!=b[u]})


def bindings():
    require(digest(PRODUCTION)==ACCEPTED, 'Accepted production PCB differs; STOP')
    require(digest(OWNER)==APPROVED, 'Approved owner PCB differs; STOP')
    context=read_json(OWNER_REVIEW/'context.json')
    verify_hashes(OWNER.parent,context['source_hashes'])
    verify_hashes(PRODUCTION.parent,context['accepted_hashes'])
    require(digest(OWNER.with_suffix('.kicad_dru'))==digest(PRODUCTION.with_suffix('.kicad_dru')),
            'Owner/production rules differ; STOP')
    sources={str(p.resolve()):digest(p) for root in [PRODUCTION.parent, OWNER.parent]
             for p in root.glob('ups12v_v4.kicad_*')
             if p.suffix in ['.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_dru']}
    sources[str(MANIFEST.resolve())]=digest(MANIFEST)
    return sources


def verify_bindings(expected):
    for name, wanted in expected.items():
        require(digest(name)==wanted, 'Migration input drift: '+name+'; STOP')


def verify_inputs(context, plan, installed=False):
    """Guard all originals while allowing only recorded production changes."""
    production=context.get('mode')=='production-mapped-adoption'
    for name,wanted in context['bindings'].items():
        path=Path(name)
        if production and path==PRODUCTION.with_suffix('.kicad_sch').resolve():
            wanted=context.get('authorized_schema_hash',wanted)
        if production and installed and path==PRODUCTION.resolve():
            continue
        require(digest(path)==wanted,'Migration input drift: '+name+'; STOP')
    if production:
        require(digest(context['candidate_proof'])==context['candidate_proof_hash'],'Candidate proof drift')
        proof=read_json(context['candidate_proof'])
        require(proof['verdict']=='PASS_COMPLETE_CANDIDATE','Complete candidate proof required')
        require(digest(__file__)==context['implementation_hash'],'Production implementation drift')
        for path,wanted in proof['candidate_sources'].items():
            require(digest(path)==wanted,'Validated candidate source drift')


def open_net_counts(report, native):
    """Ratsnest representatives may be a track or a pad of the same island."""
    objects={u:item for s in ['pads','tracks','vias'] for u,item in native[s].items()}
    result=Counter()
    for row in report['unconnected_items']:
        require(all(x['uuid'] in objects for x in row['items']),'Unknown native open endpoint')
        nets={objects[x['uuid']]['net'] for x in row['items']}
        require(len(nets)==1,'Open endpoints have different native net identities')
        result[next(iter(nets))]+=1
    return dict(result)


def verify_refilled_capture(before, after, layout):
    """Allow only derived fill changes, and prove every native polygon/vertex."""
    require(set(before)==set(after),'IPC capture sections differ')
    for section in before:
        if section!='zones':
            require(semantic_capture(before[section])==semantic_capture(after[section]),
                    'Post-refill native identity differs: '+section)
    def definitions(rows):
        return {u:{k:v for k,v in row.items() if k!='filledPolygons'} for u,row in rows.items()}
    require(semantic_capture(definitions(before['zones']))==semantic_capture(definitions(after['zones'])),
            'Post-refill zone definition changed')
    layers={'BL_F_Cu':'F.Cu','BL_In1_Cu':'In1.Cu','BL_In2_Cu':'In2.Cu','BL_B_Cu':'B.Cu'}
    def chain(row):
        require(all(set(n)=={'point'} for n in row.get('nodes',[])),'Unsupported curved IPC fill chain')
        return [[int(n['point'].get('xNm',0))/1e6,int(n['point'].get('yNm',0))/1e6] for n in row['nodes']]
    observed={}
    for uid,zone in after['zones'].items():
        # KiCad serializes empty per-layer containers for an RF rule area;
        # those are not copper and must remain empty rather than disappear.
        polygons=[p for p in zone.get('filledPolygons',[]) if p.get('shapes',{}).get('polygons')]
        if not polygons:continue
        require(uid in layout['fills'],'Unexpected live filled zone')
        observed[uid]={}
        for row in polygons:
            require(row['layer'] in layers,'Unknown live fill layer')
            observed[uid][layers[row['layer']]]=[dict(outline=chain(p['outline']),
                holes=[chain(h) for h in p.get('holes',[])]) for p in row['shapes']['polygons']]
        require(observed[uid]==layout['fills'][uid]['layers'],'Live fill differs from independent native polygons')
    require(set(observed)==set(layout['fills']),'Missing native filled zone coverage')
    return dict(non_fill_native_identity_exact=True,live_fill_exact_independent_native=True)


def verify_candidate(root, output, final=False):
    """Independent native/export comparisons; no original CAD writes."""
    from .review_compare import (checks_delta,connectivity_delta,electrical_delta,
                                 property_delta,merge_counts)
    from .phase411_analysis import local_fill_comparison,protected_loop_summary
    from .usb_review import analyze
    owner=OWNER_REVIEW
    a,b=[read_json(p/'snapshot.json') for p in [owner,root]]
    ia,ib=[read_json(p/'native-review-inspection.json') for p in [owner,root]]
    summary=read_json(root/'summary.json')
    native_equal={s:a[s]==b[s] for s in a}
    require(all(native_equal.values()),'Candidate native geometry/pads/fill differ from approved owner')
    require(read_json(owner/'routed-diagnostics.json')==read_json(root/'routed-diagnostics.json'),
            'Native copper/drill/padstack diagnostics differ')
    require(ia['pad_partitions']==ib['pad_partitions'],'Exact 473-pad native islands differ')
    require(ia['usb_pairs']==ib['usb_pairs'],'Native resistor-separated pair/netclass recognition differs')
    require(ia['audit']['zones']==ib['audit']['zones'] and ia['audit']['drawings']==ib['audit']['drawings'],
            'Zone/RF definitions or board drawings differ')
    art=lambda rows:Counter(json.dumps({k:v for k,v in row.items() if k!='uuid'},sort_keys=True)
                            for row in rows.values())
    require(all(art(ia['audit']['footprint_graphics'][ref])==art(rows)
                for ref,rows in ib['audit']['footprint_graphics'].items()),'Footprint artwork semantics differ')
    ca,cb=[read_json(p/'routing-context.json') for p in [owner,root]]
    for section in ['profile','pads','copper_graphics','zones','board_outline','reservations']:
        require(ca[section]==cb[section],'Actual rule/geometry/reservation context differs: '+section)
    require(summary['drc']['errors']==summary['drc']['parity']==summary['erc']['errors']==0
            and summary['drc']['unconnected']==44,'Candidate ERC/DRC/parity failed')
    checks=checks_delta(owner,root)
    require(checks['drc']['warning_identity_multiset_equal'] and checks['drc']['ignored_checks_equal']
            and checks['erc']['warning_identity_multiset_equal'],'Candidate warning identities/rules differ')
    netlist=root/'netlist.xml'
    if not netlist.exists():
        run_monitored(['C:/Program Files/KiCad/10.0/bin/kicad-cli.exe','sch','export','netlist',
                       '--format','kicadxml','--output',netlist,root/'ups12v_v4.kicad_sch'],root/'netlist-export.log')
    topology=electrical_delta(BASE/'evidence/phase4-11-owner-confirmed-native/netlist.xml',netlist)
    require(topology['partitions_equal'] and not topology['renamed_nets'] and not topology['changed_components'],
            'All-component electrical partitions/properties differ')
    base_i=read_json(CONTROL/'native-review-inspection.json')
    connectivity=connectivity_delta(base_i,ib)
    require(connectivity['all_previous_pad_connections_preserved'],'Original accepted pad connections split')
    assigned={u:i for i,g in enumerate(ib['pad_partitions']) for u in g}
    def island(ref,pin):
        matches={assigned[u] for u,v in b['pads'].items() if v['ref']==ref and str(v['pin'])==pin}
        require(len(matches)==1,'Pad missing/split: '+ref+'.'+pin)
        return next(iter(matches))
    pairs=[('J7.A6','J7.B6'),('J7.A6','U2.1'),('U2.1','R48.2'),
           ('J7.A7','J7.B7'),('J7.A7','U2.2'),('U2.2','R49.2'),
           ('R48.1','U1.27'),('R49.1','U1.26'),('U2.3','U4.2')]
    closures={x+'-'+y:island(*x.split('.',1))==island(*y.split('.',1)) for x,y in pairs}
    require(all(closures.values()),'USB/ESD closure missing')
    vbus=['J7.A4','J7.A9','J7.B4','J7.B9','U4.1','C28.1','C27.1']
    require(len({island(*p.split('.',1)) for p in vbus})==1,'VBUS contacts split')
    for ref in ['R48','R49']:
        require(island(ref,'1')!=island(ref,'2'),'Series resistor bypass')
    layouts=[read_json(p/'post-refill-layout.json') for p in [owner,root]]
    require(layouts[0]['fills']==layouts[1]['fills'],'Actual In1 fill polygons differ')
    protected={f['ref']:local_fill_comparison(*layouts,[f['position'][0]-6,f['position'][1]-6,
               f['position'][0]+6,f['position'][1]+6]) for f in b['footprints'].values()
               if f['ref'] in ['IC1','L1','U3']}
    structural=property_delta(owner/'ups12v_v4.kicad_pcb',root/'ups12v_v4.kicad_pcb',True)
    require(set(structural['top_level_counts']) <= {'footprint','generated'},'Unexpected structural board delta')
    permitted={'pad/pintype/@','pad/pinfunction/@','property/@','units/@','units/unit/@',
               'units/unit/name/@','units/unit/pins/@','property/uuid/@'}
    require(all('/'.join(p.split(':')[0] for p in row['path'][1:]) in permitted
                for row in structural['changes'] if row['path'][0].startswith('footprint:')),
            'Unclassified footprint metadata difference')
    write_json(root/'owner-structural-delta.json',structural)
    context=read_json(root/'context.json')
    sources={str((Path(context['source']).parent/name).resolve()):value
             for name,value in context['source_hashes'].items()}
    report=dict(verdict='PASS_FINAL_PRODUCTION' if final else 'PASS_COMPLETE_CANDIDATE',
        candidate_sources=sources,original_owner_hash=APPROVED,native_equal=native_equal,
        exact_route_padstack_diagnostics=True,exact_473pad_islands=True,
        native_pairs=ib['usb_pairs'],electrical_topology=topology,connectivity_vs_original=connectivity,
        nine_USB_ESD_closures=closures,all_VBUS_contacts_connected=True,series_resistors_not_bypassed=True,
        original_to_final_merges=merge_counts(base_i,ib,b),checks=summary,warnings=checks,
        actual_fill_exact_owner=True,protected_local_fill_grids=protected,
        protected_loop_summary=protected_loop_summary(b),metadata_only_differences=structural['top_level_counts'],
        metadata_equivalence='Exact pad geometry/nets, 104 exported electrical partitions/154 component properties, '
          'all field/artwork payloads except UUID, exact routed diagnostics/fills; retained production cache/presentation '
          'and omitted owner tuning-generator records do not alter finished copper or circuit.',
        remaining='3 IC1 SCL/INT/STAT and 41 F5, exact original-owner DRC open identities',
        implementation_hash=digest(__file__))
    # Exact pad-island sets above prove the actual remaining connectivity.
    # DRC may choose R28.2 instead of a connected ~INT track as representative.
    original_opens=open_net_counts(read_json(owner/'drc.json'),a)
    actual_opens=open_net_counts(read_json(root/'drc.json'),b)
    require(original_opens==actual_opens,'Remaining unconnected net groups differ')
    report['remaining_by_net']=actual_opens
    report['ratsnest_representatives_may_differ']=True
    write_json(output,report)
    print(json.dumps(dict(verdict=report['verdict'],pads=473,opens=44,physical=0,parity=0,erc_errors=0)))


def production_prepare(plan_path, proof_path, output):
    p=read_json(plan_path);verify_bindings(p['bindings'])
    proof=read_json(proof_path)
    require(proof['verdict']=='PASS_COMPLETE_CANDIDATE','Complete candidate PASS required before production')
    require(proof['implementation_hash']==digest(__file__),'Candidate implementation differs')
    require(not output.exists(),'Production transaction output must be fresh')
    output.mkdir(parents=True)
    repair=BASE/'evidence/phase4-13-owner-F8-verified'
    context=dict(mode='production-mapped-adoption',method='full-footprint-net-update-v2',
        plan=str(plan_path.resolve()),plan_hash=digest(plan_path),target=str(PRODUCTION.resolve()),
        bindings=p['bindings'],repair_review=str(repair.resolve()),repair_snapshot_hash=digest(repair/'snapshot.json'),
        candidate_proof=str(proof_path.resolve()),candidate_proof_hash=digest(proof_path),
        implementation_hash=digest(__file__),expected_fill_hash=digest(OWNER_REVIEW/'post-refill-layout.json'))
    verify_inputs(context,p)
    write_json(output/'migration-context.json',context)
    print('Guarded production context prepared; no CAD writes')


def bind_production_schema(root):
    from .review_compare import property_delta,electrical_delta
    context=read_json(root/'migration-context.json');p=read_json(context['plan'])
    require(context.get('mode')=='production-mapped-adoption' and (root/'ipc-preflight.json').exists(),
            'Production read-only preflight required')
    change=property_delta(PREFLIGHT/'ups12v_v4.kicad_sch',PRODUCTION.with_suffix('.kicad_sch'))
    require(set(change['top_level_counts'])=={'label'},'Unapproved production schematic edit')
    # Exact semantic label inventory must equal the successfully validated candidate.
    from .review_compare import tree
    def label_set(path):
        return Counter(json.dumps([n[0],n[1],[c for c in n if isinstance(c,list) and c[0]=='at']],sort_keys=True)
                       for n in tree(path)[1:] if isinstance(n,list) and n[0]=='label')
    proof=read_json(context['candidate_proof'])
    candidate_sch=next(Path(n) for n in proof['candidate_sources'] if n.endswith('.kicad_sch'))
    require(label_set(PRODUCTION.with_suffix('.kicad_sch'))==label_set(candidate_sch),'Production label mapping differs')
    netlist=root/'production-before-PCB.net.xml'
    run_monitored(['C:/Program Files/KiCad/10.0/bin/kicad-cli.exe','sch','export','netlist',
                   '--format','kicadxml','--output',netlist,PRODUCTION.with_suffix('.kicad_sch')],root/'schema-export.log')
    topology=electrical_delta(BASE/'evidence/phase4-11-owner-confirmed-native/netlist.xml',netlist)
    require(topology['partitions_equal'] and not topology['renamed_nets'] and not topology['changed_components'],
            'Production schematic topology differs')
    context['authorized_schema_hash']=digest(PRODUCTION.with_suffix('.kicad_sch'))
    verify_inputs(context,p)
    write_json(root/'production-schematic-proof.json',dict(delta=change,topology=topology,
                                                         hash=context['authorized_schema_hash']))
    write_json(root/'migration-context.json',context)
    print('Production schematic: exactly the two proven labels, full topology PASS')


def validate_delta(d, before, owner):
    require(set(d)==set(SECTIONS), 'Incomplete migration object scope')
    require(not d['footprints']['added'] and not d['footprints']['removed'], 'Component set changed')
    require({v['after']['ref'] for v in d['footprints']['modified'].values()}=={'C28','U2','R48'},
            'Unexpected footprint moves')
    for row in d['footprints']['modified'].values():
        require({k:v for k,v in row['before'].items() if k!='position'}==
                {k:v for k,v in row['after'].items() if k!='position'}, 'Non-translation footprint edit')
    require(not d['pads']['added'] and not d['pads']['removed'], 'Physical pad identities changed')
    for row in d['pads']['modified'].values():
        a,b=row['before'],row['after']
        require(b['net']==RENAMES.get(a['net'],a['net']), 'Unapproved pad net change')
        require(a['ref'] in {'C28','U2','R48','R49','U1'}, 'Unapproved pad modification')
    require(len(owner['pads'])==473 and len(owner['footprints'])==154, 'Incomplete owner inventory')
    require(sum(v.get('geometry')=='arc' for v in owner['tracks'].values())==8,
            'Owner arc inventory differs')
    return True


def plan(output):
    from .review_compare import property_delta, electrical_delta, connectivity_delta, checks_delta
    from .phase411_analysis import routed_delta
    require(not output.exists(), 'Reconciliation output must be fresh')
    bound=bindings()
    before=read_json(PREFLIGHT/'snapshot.json'); owner=read_json(OWNER_REVIEW/'snapshot.json')
    require(before==read_json(CONTROL/'snapshot.json'), 'Fresh production inventory differs from control')
    d={s:delta(before[s],owner[s]) for s in SECTIONS}
    validate_delta(d,before,owner)
    output.mkdir(parents=True)
    for ext,name in [('.kicad_pcb','board'),('.kicad_sch','schematic')]:
        write_json(output/(name+'-structural-delta.json'),
                   property_delta(PRODUCTION.with_suffix(ext),OWNER.with_suffix(ext),ext=='.kicad_pcb'))
    topology=electrical_delta(CONTROL/'netlist.xml', BASE/'evidence/phase4-11-owner-confirmed-native/netlist.xml')
    write_json(output/'electrical-partitions.json',topology)
    write_json(output/'pad-connectivity.json',connectivity_delta(
        read_json(CONTROL/'native-review-inspection.json'),read_json(OWNER_REVIEW/'native-review-inspection.json')))
    write_json(output/'checks-delta.json',checks_delta(CONTROL,OWNER_REVIEW))
    replacements={}
    for old,v in d['vias']['removed'].items():
        physical=lambda item:{k:value for k,value in item.items() if k!='uuid'}
        matches=[u for u,w in d['vias']['added'].items() if physical(v)==physical(w)]
        require(len(matches)==1, 'Removed original via lacks exact replacement')
        replacements[old]=matches[0]
    mapping={s:{u:dict(target_uuid=u, operation=('create' if u in d[s]['added'] else
               'update' if u in d[s]['modified'] else 'retain')) for u in owner[s]}
             for s in SECTIONS}
    result=dict(schema_version=1, mode='scratch-rehearsal-only', bindings=bound,
        production=str(PRODUCTION.resolve()), owner=str(OWNER.resolve()),
        baseline=str(MANIFEST.resolve()), baseline_snapshot=str((PREFLIGHT/'snapshot.json').resolve()),
        owner_snapshot=str((OWNER_REVIEW/'snapshot.json').resolve()), delta=d,
        mapping=mapping, exact_via_replacements=replacements, net_renames=RENAMES,
        schematic_labels=[dict(net='USB_MCU_DP',x=436.88,y=134.62,rotation=0),
                          dict(net='USB_MCU_DN',x=436.88,y=132.08,rotation=0)],
        counts={s:{k:len(v) for k,v in d[s].items()} for s in SECTIONS},
        routed_by_net=routed_delta(before,owner),
        metadata_policy='Retain production metadata; omit owner editor tuning generators and refreshed field IDs. '
                        'Require exact native finished copper/pads/fills and exported electrical partitions.',
        exclusions=['historical cleanup proposals','IC1 escapes','F5 routing','rules','BOM','firmware'])
    write_json(output/'migration-whitelist.json',result)
    verify_bindings(bound)
    print(json.dumps(result['counts']))


def prepare(plan_path, output):
    p=read_json(plan_path);verify_bindings(p['bindings'])
    require(p['mode']=='scratch-rehearsal-only', 'No production apply supported')
    root=prepare_scratch(p['production'],p['baseline'],output)
    repair=BASE/'evidence/phase4-13-owner-F8-verified'
    require((repair/'summary.json').is_file(), 'Independent F8 repair review required')
    require(read_json(repair/'summary.json')['drc']['errors']==0, 'F8 repair has physical errors')
    write_json(root/'migration-context.json',dict(plan=str(plan_path.resolve()),plan_hash=digest(plan_path),
               target=str((root/PRODUCTION.name).resolve()), bindings=p['bindings'],
               method='full-footprint-net-update-v2',repair_review=str(repair.resolve()),
               repair_snapshot_hash=digest(repair/'snapshot.json'),
               expected_fill_hash=digest(OWNER_REVIEW/'post-refill-layout.json')))
    print(str(root))


def diagnose(root):
    """Analyze captured responses only after the scratch preservation STOP.

    Does not connect to KiCad, save CAD, refill, retry, or recover the editor.
    """
    from .review_compare import property_delta, tree
    p=read_json(read_json(root/'migration-context.json')['plan'])
    verify_bindings(p['bindings'])
    expected=read_json(root/'ipc-expected.json');actual=read_json(root/'ipc-after.json')
    def walk(a,b,path=()):
        if isinstance(a,dict) and isinstance(b,dict):
            return [r for k in sorted(a.keys()|b.keys()) for r in walk(a.get(k),b.get(k),path+(k,))]
        if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
            return [r for i,(u,v) in enumerate(zip(a,b)) for r in walk(u,v,path+(str(i),))]
        return [] if a==b else [dict(path=list(path),expected=a,actual=b)]
    differences={s:walk(semantic_capture(expected[s]),semantic_capture(actual[s])) for s in expected}
    write_json(root/'readback-delta.json',differences)
    native=read_json(p['owner_snapshot']);returned=read_json(root/'returned-items.json')
    bad_pads=[]
    for row in differences['pads']:
        uid=row['path'][0];pad=native['pads'][uid]
        bad_pads.append(dict(uuid=uid,ref=pad['ref'],pin=pad['pin'],
            requested_net=row['expected'],observed_net=row['actual'],
            response_nets=[x.get('net',{}).get('name') for x in returned if x.get('id',{}).get('value')==uid]))
    nonusb={}
    old=read_json(BASE/'evidence/phase4-11-owner-confirmed-native/snapshot.json')
    owner=read_json(p['owner_snapshot'])
    for net in ['SYS','VIN1','MAIN_3V3','MCU3V3','Net-(D1-A)','Net-(C26-Pad1)','USB3V3']:
        nonusb[net]=all({u:v for u,v in old[s].items() if v['net']==net}==
                       {u:v for u,v in owner[s].items() if v['net']==net} for s in ['tracks','vias'])
    schema_delta=property_delta(PRODUCTION.with_suffix('.kicad_sch'),root/PRODUCTION.with_suffix('.kicad_sch').name)
    write_json(root/'scratch-schematic-delta.json',schema_delta)
    def labels(path):
        rows=[]
        for item in tree(path)[1:]:
            if not isinstance(item,list) or item[0]!='label':continue
            at=next(x for x in item if isinstance(x,list) and x[0]=='at')
            uid=next(x for x in item if isinstance(x,list) and x[0]=='uuid')
            rows.append(dict(uuid=json.loads(uid[1]),net=json.loads(item[1]),at=at[1:]))
        return rows
    target_labels=labels(root/PRODUCTION.with_suffix('.kicad_sch').name)
    label_mapping=[]
    for source_label in labels(OWNER.with_suffix('.kicad_sch')):
        same=[v for v in target_labels if v['net']==source_label['net'] and v['at']==source_label['at']]
        require(len(same)==1,'Schematic label target mapping is ambiguous')
        label_mapping.append(dict(source=source_label,target=same[0]))
    write_json(root/'schematic-label-UUID-mapping.json',label_mapping)
    write_json(root/'source-copper-fill-delta.json',dict(
        zone_definitions_structurally_unchanged=True,
        production_native_fills=read_json(PREFLIGHT/'layout.json')['fills'],
        owner_native_fills=read_json(OWNER_REVIEW/'post-refill-layout.json')['fills'],
        source_fill_equals_fresh_refill=read_json(OWNER_REVIEW/'correction-confirmation.json')['source_fill_equals_fresh_refill'],
        limits='Native polygons with holes; no candidate fill was generated after the STOP.'))
    report=dict(verdict='STOP_REHEARSAL_NET_PRESERVATION_FAILURE_NO_PRODUCTION_WRITES',
        native_assertion=False,ipc_transport_failure=False,commit_pushed=True,
        refill_invoked=False,save_invoked=False,rollback_invoked=False,retry_invoked=False,
        saved_scratch_PCB_hash=digest(root/PRODUCTION.name),
        saved_scratch_is_original_production=digest(root/PRODUCTION.name)==ACCEPTED,
        original_bindings_unchanged=True,original_bindings=p['bindings'],
        wrong_pad_nets=bad_pads,
        wrong_routed_net_counts={s:dict(Counter(row['expected']+' -> '+row['actual']
            for row in differences[s] if row['path'][-2:]==['net','name'])) for s in ['tracks','vias']},
        exact_count_match={s:len(expected[s])==len(actual[s]) for s in expected},
        differences_by_section={s:len(v) for s,v in differences.items()},
        unchanged_sections=[s for s,v in differences.items() if not v],
        nonUSB_owner_routes_equal_reviewed_Phase411=nonusb,
        scratch_schematic_only_two_labels=(schema_delta['top_level_counts'].keys()=={'label'}),
        completed_candidate_validation=False,accepted_baseline_promoted=False,
        minimum_owner_action='Close the rehearsal PCB without saving; reopen this isolated project, '
          'use native F8 Update PCB from Schematic to establish USB_MCU_DP/DN net identities, '
          'save that isolated PCB and close editors. Report completion before a fresh guarded rehearsal. '
          'Do not apply the owner geometry or copy any scratch PCB over production.')
    write_json(root/'STOP-diagnosis.json',report)
    print(json.dumps(dict(verdict=report['verdict'],wrong_pads=bad_pads,
                         wrong_routed_net_counts=report['wrong_routed_net_counts'],
                         original_bindings_unchanged=True)))


def worker(root, action, socket):
    from .ipc_install import capture, comparable
    require(not (root/'ipc-preservation.json').exists() or
            read_json(root/'ipc-preservation.json').get('exact_equal') is True,
            'Rehearsal is STOPPED after preservation failure; no further IPC, save or recovery allowed')
    context=read_json(root/'migration-context.json');p=read_json(context['plan'])
    require(context.get('method')=='full-footprint-net-update-v2',
            'Historical individual-pad net method is disabled')
    require(digest(Path(context['repair_review'])/'snapshot.json')==context['repair_snapshot_hash'],
            'Independent F8 reference drift')
    require(digest(context['plan'])==context['plan_hash'], 'Migration plan changed')
    verify_inputs(context,p,installed=action=='verify-saved')
    target=Path(context['target'])
    production=context.get('mode')=='production-mapped-adoption'
    require((production and target.resolve()==PRODUCTION.resolve()) or
            (not production and target.parent==root.resolve() and target.resolve()!=Path(p['production']).resolve()),
            'Target is not the guarded project for this transaction')
    require(digest(target.with_suffix('.kicad_pro'))==digest(PRODUCTION.with_suffix('.kicad_pro')),
            'Scratch project/rules changed')
    sys.path.insert(0,str(PRODUCTION.parent/'.konnect/native-ipc'))
    from kipy import KiCad
    from kipy.board_types import Track, ArcTrack, Via, Net, FootprintInstance
    from kipy.geometry import Vector2
    from kipy.proto.board.board_types_pb2 import ViaType
    from google.protobuf.json_format import MessageToDict
    k=KiCad(socket_path=socket,client_name='V4 Phase4.13 isolated migration rehearsal')
    require(k.get_version().major==10, 'KiCad 10 editor required')
    b=k.get_board()
    require(b.name==target.name and Path(b.document.project.path).resolve()==target.parent.resolve(),
            'Requested scratch is not the live document')
    baseline=read_json(p['baseline']);before=capture(b)
    if action=='verify-saved':
        expected=read_json(root/('live-saved.json' if (root/'live-saved.json').exists() else 'ipc-after.json'))
        write_json(root/'final-live-observed.json',before)
        equivalence=verify_refilled_capture(expected,before,read_json(OWNER_REVIEW/'post-refill-layout.json'))
        require(digest(target)==read_json(root/'ipc-saved.json')['board_sha256'],'Saved PCB drift')
        write_json(root/'final-live-readback.json',dict(identity=True,saved_hash=digest(target),
            native_sections_equal=True,source=str(target),refill_equivalence=equivalence))
        print('Final saved/live identity PASS');return
    if action=='observe':
        require(not (root/'ipc-observation.json').exists(), 'Observation already exists')
        write_json(root/'ipc-observation.json',before)
        changes={}
        for section in before:
            a,c=comparable(baseline[section]),comparable(before[section])
            paths=[]
            def walk(x,y,path=()):
                if isinstance(x,dict) and isinstance(y,dict):
                    for key in sorted(x.keys()|y.keys()):walk(x.get(key),y.get(key),path+(key,))
                elif x!=y:paths.append(dict(path=list(path),before=x,after=y))
            walk(a,c);changes[section]=paths
        write_json(root/'ipc-observation-delta.json',changes)
        print(json.dumps({s:len(v) for s,v in changes.items()}));return
    if action=='preflight':
        require(digest(target)==ACCEPTED, 'Rehearsal must start from exact production PCB')
        for section in before:
            require(semantic_capture(before[section])==semantic_capture(baseline[section]),
                    'Live rehearsal baseline differs in '+section)
        write_json(root/'ipc-before.json',before)
        write_json(root/'ipc-preflight.json',dict(identity=True, live_saved_match=True,
                   target=str(target), version=str(k.get_version()), schematic_hash=digest(target.with_suffix('.kicad_sch'))))
        print('Scratch IPC preflight PASS');return
    require(action=='apply' and (root/'ipc-preflight.json').is_file(), 'Scratch preflight required')
    require(not (root/'commit.json').exists(), 'Rehearsal already attempted; never retry a transaction')
    require(before==read_json(root/'ipc-before.json'), 'Live scratch changed after preflight')
    require(digest(target.with_suffix('.kicad_sch'))==
            (context.get('authorized_schema_hash') if production else
             read_json(root/'ipc-preflight.json')['schematic_hash']),
            'Scratch schematic changed after preflight')
    goal=read_json(p['owner_snapshot']);d=p['delta'];updates=[];creates=[];removes=[]
    expected=copy.deepcopy(before)
    vec=lambda xy:Vector2.from_xy(*(round(v*1e6) for v in xy))
    footprints={x.id.value:x for x in b.get_footprints()}
    changed_pad_refs={v['after']['ref'] for v in d['pads']['modified'].values()}
    for uid,original in footprints.items():
        ref=original.reference_field.text.value
        if ref not in changed_pad_refs:continue
        fp=FootprintInstance(footprints[uid].proto)
        if uid in d['footprints']['modified']:
            fp.position=vec(d['footprints']['modified'][uid]['after']['position'])
        for pad in fp.definition.pads:
            pad.net=Net(name=goal['pads'][pad.id.value]['net'])
        updates.append(fp)
        expected['footprints'][uid]=MessageToDict(fp.proto)
        for pad in fp.definition.pads:expected['pads'][pad.id.value]=MessageToDict(pad.proto)
    routed={x.id.value:x for x in list(b.get_tracks())+list(b.get_vias())}
    via_template=next(iter(b.get_vias()))
    for section in ['tracks','vias']:
        for uid in d[section]['removed']:
            removes.append(routed[uid]);del expected[section][uid]
        for operation in ['modified','added']:
            for uid,row in d[section][operation].items():
                if operation=='modified':row=row['after']
                if section=='tracks':
                    cls=ArcTrack if row.get('geometry')=='arc' else Track
                    item=cls(routed[uid].proto) if operation=='modified' else cls()
                    item.locked=False
                    item.start=vec(row['start']);item.end=vec(row['end']);item.width=round(row['width']*1e6)
                    item.layer=b.get_layer_by_name(row['layer'])
                    if cls is ArcTrack:item.mid=vec(row['mid'])
                else:
                    template=next((old for old,new in p['exact_via_replacements'].items() if new==uid),None)
                    item=Via(routed[uid if operation=='modified' else template].proto) if operation=='modified' or template else Via(via_template.proto)
                    item.position=vec(row['position']);item.type=ViaType.VT_THROUGH
                    widths=set(row['copper_widths'].values())
                    require(len(widths)==1,'Nonuniform via padstack requires explicit layer mapping')
                    item.diameter=round(next(iter(widths))*1e6);item.drill_diameter=round(row['drill']*1e6)
                item.id.value=uid;item.net=Net(name=row['net'])
                (updates if operation=='modified' else creates).append(item)
                expected[section][uid]=MessageToDict(item.proto)
    write_json(root/'ipc-expected.json',expected)
    write_json(root/'prepared-transaction.json',dict(update=[x.id.value for x in updates],
        create=[x.id.value for x in creates],remove=[x.id.value for x in removes]))
    commit=b.begin_commit();write_json(root/'commit.json',dict(value=commit.id.value))
    b.remove_items(removes)
    actual_updates=b.update_items(updates);actual_creates=b.create_items(creates)
    write_json(root/'returned-items.json',[MessageToDict(x.proto) for x in actual_updates+actual_creates])
    require({x.id.value for x in actual_updates}=={x.id.value for x in updates},'Updated UUID set differs')
    require({x.id.value for x in actual_creates}=={x.id.value for x in creates},'Created UUID set differs')
    b.push_commit(commit,'Phase4.13 exact approved owner design rehearsal')
    after=capture(b);write_json(root/'ipc-after.json',after)
    differences=[s for s in expected if semantic_capture(expected[s])!=semantic_capture(after[s])]
    write_json(root/'ipc-preservation.json',dict(exact_equal=not differences,different_sections=differences))
    require(not differences,'Rehearsal native IPC readback differs; STOP')
    b.refill_zones();b.save()
    saved=capture(b)
    verify_refilled_capture(after,saved,read_json(OWNER_REVIEW/'post-refill-layout.json'))
    write_json(root/'live-saved.json',saved)
    write_json(root/'ipc-saved.json',dict(board_sha256=digest(target),saved_through_editor=True))
    if production:
        installed=copy.deepcopy(saved)
        installed['hashes']={target.with_suffix(ext).name:digest(target.with_suffix(ext))
                            for ext in ['.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_dru']}
        write_json(root/'installed-manifest.json',installed)
    verify_inputs(context,p,installed=production)
    print('Mapped native-editor transaction, readback, refill and save PASS')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('plan');p.add_argument('--output',required=True,type=Path)
    p=sub.add_parser('prepare');p.add_argument('--plan',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p=sub.add_parser('diagnose');p.add_argument('--scratch',required=True,type=Path)
    p=sub.add_parser('verify-candidate');p.add_argument('--root',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--final',action='store_true')
    p=sub.add_parser('production-prepare');p.add_argument('--plan',required=True,type=Path);p.add_argument('--proof',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p=sub.add_parser('bind-schema');p.add_argument('--root',required=True,type=Path)
    for name in ['observe','preflight','apply','verify-saved','_worker-observe','_worker-preflight','_worker-apply','_worker-verify-saved']:
        p=sub.add_parser(name);p.add_argument('--scratch',required=True,type=Path);p.add_argument('--socket',required=True)
    args=parser.parse_args(argv)
    try:
        if args.action=='plan':plan(args.output)
        elif args.action=='prepare':prepare(args.plan,args.output)
        elif args.action=='diagnose':diagnose(args.scratch)
        elif args.action=='verify-candidate':verify_candidate(args.root,args.output,args.final)
        elif args.action=='production-prepare':production_prepare(args.plan,args.proof,args.output)
        elif args.action=='bind-schema':bind_production_schema(args.root)
        elif args.action.startswith('_worker-'):worker(args.scratch,args.action[8:],args.socket)
        else:
            log=args.scratch/('ipc-'+args.action+'.log')
            if log.exists():
                log=args.scratch/('ipc-'+args.action+'-reconciled.log')
            require(not log.exists(),'Action log already exists; STOP')
            run_monitored([sys.executable,'-B','-m','v4kicad.migration','_worker-'+args.action,
                           '--scratch',args.scratch,'--socket',args.socket],log)
            print('Monitored scratch '+args.action+' completed')
        return 0
    except (ToolError, OSError) as error:
        print('STOP: '+str(error),file=sys.stderr);return 2


if __name__=='__main__':
    raise SystemExit(main())
