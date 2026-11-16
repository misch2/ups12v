"""Exact Phase4.24U paste adoption through one guarded owning KiCad editor."""
import argparse
import copy
import json
from pathlib import Path
import sys

from .safety import require,read_json,write_json,digest,run_monitored,ToolError
from .stencil_scratch import SOURCE_SHA,TARGETS

BASE=Path('hardware/v4')
PRODUCTION=BASE/'ups_v4/ups12v_v4.kicad_pcb'
GOAL=BASE/'evidence/phase4-24t-stencil-scratch/candidate-v3/ups12v_v4.kicad_pcb'
GOAL_SHA='d0a8c95a1b8cfbeff1f4f7fa4a95abf297a86d9c95551ed5b7b3050f42b8ac2b'
TROOT=BASE/'evidence/phase4-24t-stencil-scratch'


def normalized_capture(value):
    from .owner_migration import native_capture
    return {s:native_capture(rows) for s,rows in value.items()}


def reconcile(before,goal):
    """Exact physical UUID/property whitelist, including footprint child payloads."""
    from .migration import delta
    a,b=normalized_capture(before),normalized_capture(goal)
    require(set(a)==set(b),'Capture sections differ')
    d={s:delta(a[s],b[s]) for s in a}
    targets={uid for pin,uid in TARGETS.values()}
    require(set(d['pads']['modified'])==targets and not d['pads']['added'] and not d['pads']['removed'],
            'Exactly four existing physical pads required')
    fpids=set()
    transaction=read_json(TROOT/'candidate-v3/transaction.json')
    shape_ids=set(transaction['added_graphics'])
    require(len(shape_ids)==10,'Exact ten accepted graphic identities required')
    found=set()
    for uid,row in d['pads']['modified'].items():
        expected=copy.deepcopy(row['before'])
        layers=expected['padStack']['layers'];require(layers.count('BL_F_Paste')==1,'Pad paste preimage differs')
        layers.remove('BL_F_Paste')
        require(expected==row['after'],'Pad changed beyond F.Paste membership: '+uid)
    def child_key(row):
        uid=row.get('id',{}).get('value')
        return (row['@type'],uid or json.dumps(row,sort_keys=True))
    for fpuid,row in d['footprints']['modified'].items():
        expected=copy.deepcopy(row['before']);children=expected['definition']['items']
        ga={child_key(x):x for x in row['after']['definition']['items']}
        old={child_key(x):x for x in children}
        require(len(old)==len(children) and len(ga)==len(row['after']['definition']['items']),
                'Duplicate footprint child identity')
        require(not (old.keys()-ga.keys()),'Original footprint child removed')
        for child in children:
            uid=child.get('id',{}).get('value')
            if uid in targets:
                require(child['@type'].endswith('.Pad'),'Target is not a pad')
                child['padStack']['layers'].remove('BL_F_Paste')
        for key in ga.keys()-old.keys():
            child=ga[key];uid=child.get('id',{}).get('value')
            require(uid in shape_ids and uid not in found and child['@type'].endswith('.BoardGraphicShape')
                    and child['layer']=='BL_F_Paste','Unapproved added footprint child')
            children.append(copy.deepcopy(child));found.add(uid)
        def ordered(fp):
            fp=copy.deepcopy(fp);fp['definition']['items'].sort(key=lambda x:json.dumps(x,sort_keys=True));return fp
        require(ordered(expected)==ordered(row['after']),'Unapproved complete footprint property change')
        fpids.add(fpuid)
    require(len(fpids)==4 and found==shape_ids,'Four footprints / ten exact graphics required')
    for s,ops in d.items():
        if s not in ('pads','footprints'):require(not any(ops.values()),'Unapproved native section delta: '+s)
    require(not d['footprints']['added'] and not d['footprints']['removed'],'Footprint identity changed')
    return dict(footprint_ids=sorted(fpids),pad_ids=sorted(targets),graphic_ids=sorted(shape_ids),
                delta=d)


def implementations():
    names=['stencil_adoption.py','stencil_scratch.py','stencil_delta.py','ipc_install.py',
           'owner_migration.py','migration.py','j7_migration.py','safety.py','geometry.py','native.py','cli.py','checks.py']
    return {str(Path(__file__).with_name(n).resolve()):digest(Path(__file__).with_name(n)) for n in names}


def plan(entry,goal,output):
    entry,goal,output=Path(entry),Path(goal),Path(output)
    require(not output.exists(),'Fresh adoption plan required')
    for root,sha in ((entry,SOURCE_SHA),(goal,GOAL_SHA)):
        require(read_json(root/'snapshot-proof.json')['sha256']==sha,'Read-only identity proof mismatch')
    require(digest(PRODUCTION)==SOURCE_SHA and digest(GOAL)==GOAL_SHA,'Saved source/candidate drift')
    check=reconcile(read_json(entry/'capture.json'),read_json(goal/'capture.json'))
    bound=[entry/'capture.json',entry/'snapshot-proof.json',goal/'capture.json',goal/'snapshot-proof.json',
           TROOT/'final-result.json',TROOT/'candidate-v3/transaction.json',
           TROOT/'candidate-v3/paste-export/ups12v_v4-F_Paste.gtp',
           TROOT/'candidate-v3/before-native.json',TROOT/'candidate-v3/before-layout.json']
    write_json(output,dict(phase='4.24U',production=str(PRODUCTION.resolve()),goal=str(GOAL.resolve()),
        source_sha256=SOURCE_SHA,goal_sha256=GOAL_SHA,entry=str(entry.resolve()),
        goal_capture=str((goal/'capture.json').resolve()),whitelist=check,
        source_hashes=read_json(TROOT/'current-source-baseline.json')['hashes'],
        bindings={str(p.resolve()):digest(p) for p in bound},implementations=implementations()))
    print('Exact ten-graphic/four-pad production plan PASS')


def guard(root,installed=False):
    root=Path(root);require(not (root/'STOP.json').exists(),'Stopped context; no IPC/recovery')
    c=read_json(root/'editor-context.json');p=read_json(c['plan'])
    require(digest(c['plan'])==c['plan_sha256'] and implementations()==p['implementations'],
            'Rehearsed plan/implementation drift')
    require(digest(GOAL)==GOAL_SHA,'Accepted candidate drift')
    for path,h in p['bindings'].items():require(digest(path)==h,'Accepted evidence drift: '+path)
    for name,h in p['source_hashes'].items():
        if name!=PRODUCTION.name or not (installed and c['production']):
            require(digest(PRODUCTION.parent/name)==h,'Production source/companion drift')
    target=Path(c['target'])
    require((target.resolve()==PRODUCTION.resolve())==c['production'],'Wrong migration scope')
    if not installed:require(digest(target)==SOURCE_SHA,'Fresh source-derived target required')
    else:require(digest(target)==read_json(root/'ipc-saved.json')['sha256'],'Saved target drift')
    if c['production']:
        proof=read_json(c['rehearsal_proof'])
        require(digest(c['rehearsal_proof'])==c['rehearsal_sha256'] and proof['status']=='PASS_COMPLETE_REHEARSAL'
                and proof['plan_sha256']==c['plan_sha256'] and proof['implementations']==p['implementations'],
                'Identical completed owning-editor rehearsal required')
        for path,h in proof['bindings'].items():require(digest(path)==h,'Rehearsal proof input drift')
    return c,p


def prepare(plan_path,output,rehearsal=None):
    from .safety import prepare_scratch
    import shutil
    plan_path,output=Path(plan_path),Path(output);p=read_json(plan_path)
    require(digest(PRODUCTION)==SOURCE_SHA and digest(GOAL)==GOAL_SHA,'Source/goal drift')
    require(implementations()==p['implementations'],'Plan implementation drift')
    if rehearsal:
        require(not output.exists(),'Fresh production transaction output required');output.mkdir()
        target=PRODUCTION.resolve()
    else:
        output=prepare_scratch(PRODUCTION,TROOT/'current-source-baseline.json',output)
        target=output/PRODUCTION.name
        for name in ('fp-lib-table','sym-lib-table'):
            if (PRODUCTION.parent/name).exists():shutil.copy2(PRODUCTION.parent/name,output/name)
        for name in ('ups_v4.pretty','ups_v4_external.pretty'):
            shutil.copytree(PRODUCTION.parent/name,output/name)
    if not rehearsal:
        for path in PRODUCTION.parent.glob('*.kicad_sym'):shutil.copy2(path,output/path.name)
    manifest=output/'entry-manifest.json';write_json(manifest,dict(hashes=p['source_hashes']))
    c=dict(target=str(target.resolve()),sha256=SOURCE_SHA,manifest=str(manifest.resolve()),
        production=bool(rehearsal),plan=str(plan_path.resolve()),plan_sha256=digest(plan_path))
    if rehearsal:c.update(rehearsal_proof=str(Path(rehearsal).resolve()),rehearsal_sha256=digest(rehearsal))
    write_json(output/'editor-context.json',c);guard(output)
    print('Prepared guarded '+('production transaction' if rehearsal else 'owning-editor rehearsal'))


def transaction_worker(root,socket,action):
    from .ipc_install import capture
    from .j7_migration import capture_equal
    from .migration import verify_refilled_capture
    root=Path(root);c,p=guard(root,installed=action=='verify-live');target=Path(c['target'])
    sys.path.insert(0,str(PRODUCTION.parent.resolve()/'.konnect/native-ipc'))
    from kipy import KiCad
    from kipy.board_types import FootprintInstance
    from kipy.proto.board.board_types_pb2 import FootprintInstance as FootprintProto
    from kipy.proto.common.types.base_types_pb2 import DocumentType
    from google.protobuf.json_format import ParseDict,MessageToDict
    k=KiCad(socket_path=socket,client_name='UPS V4 Phase4.24U exact paste adoption')
    require(k.get_version().major==10 and len(k.get_open_documents(DocumentType.DOCTYPE_PCB))==1,'Ambiguous editor/version')
    b=k.get_board();require(b.name==target.name and Path(b.document.project.path).resolve()==target.parent.resolve(),'Wrong owning document')
    actual=capture(b)
    if action=='verify-live':
        require(capture_equal(read_json(root/'live-saved.json'),actual),'Saved/live drift')
        write_json(root/'final-live-proof.json',dict(saved_live_exact=True,sha256=digest(target)))
        print('Final live/saved exact readback PASS');return
    entry=read_json(Path(p['entry'])/'capture.json');goal=read_json(p['goal_capture'])
    require(capture_equal(entry,actual),'Unexpected/dirty live source; no transaction')
    reconcile(entry,goal)
    if action=='preflight':
        require(not (root/'ipc-preflight.json').exists(),'Fresh preflight required')
        write_json(root/'ipc-before.json',actual);write_json(root/'ipc-preflight.json',dict(saved_live_exact=True,target=str(target)))
        print('Exact source preflight PASS');return
    require(action=='apply' and (root/'ipc-preflight.json').exists() and not (root/'commit.json').exists(),
            'Fresh preflighted unattempted transaction required')
    require(capture_equal(read_json(root/'ipc-before.json'),actual),'Live source drift after preflight')
    updates=[]
    for uid in p['whitelist']['footprint_ids']:
        data=copy.deepcopy(goal['footprints'][uid])
        if 'parent' in actual['footprints'][uid]:data['parent']=actual['footprints'][uid]['parent']
        else:data.pop('parent',None)
        updates.append(FootprintInstance(ParseDict(data,FootprintProto())))
    write_json(root/'intended-footprints.json',{f.id.value:MessageToDict(f.proto) for f in updates})
    guard(root)
    commit=b.begin_commit();write_json(root/'commit.json',dict(id=commit.id.value))
    returned=b.update_items(updates)
    returned_map={f.id.value:MessageToDict(f.proto) for f in returned}
    write_json(root/'returned-footprints.json',returned_map)
    require(len(returned)==4 and {f.id.value for f in returned}==set(p['whitelist']['footprint_ids']),
            'Returned footprint identity/count differs; no automatic recovery')
    from .owner_migration import native_capture
    require(native_capture(returned_map)==native_capture({uid:goal['footprints'][uid] for uid in returned_map}),
            'Returned complete footprint child/property mismatch; STOP')
    b.push_commit(commit,'Phase4.24U exact accepted four-land F.Paste adoption')
    after=capture(b);write_json(root/'ipc-after.json',after)
    require(capture_equal(goal,after),'Exact child/pad/property post-commit mismatch; STOP')
    b.refill_zones();filled=capture(b);write_json(root/'live-refilled.json',filled)
    verify_refilled_capture(after,filled,read_json(TROOT/'candidate-v3/before-layout.json'))
    b.save();saved=capture(b);write_json(root/'live-saved.json',saved)
    require(capture_equal(filled,saved),'Owning save changed native payload')
    write_json(root/'ipc-saved.json',dict(sha256=digest(target),saved_through_owning_editor=True,
        exact_accepted_graphics_and_four_pad_changes=True))
    manifest=read_json(c['manifest']);manifest['hashes'][target.name]=digest(target)
    write_json(root/'installed-manifest.json',manifest)
    guard(root,installed=True)
    print('Exact footprint-child transaction/refill/owning-editor save PASS',flush=True)


def canonical_worker(root):
    """Read-only identity proof for KiCad IPC's differently formatted string export."""
    from .native import api_load
    from .safety import verify_context
    root=Path(root);c=verify_context(root);request=read_json(root/'normalization-request.json')
    require(digest(request['export'])==request['sha256'],'Native string export drift')
    require(not (root/'canonical-proof.json').exists(),'Fresh canonical proof required')
    api,source=api_load(c['board'])
    io=api.PCB_IO_KICAD_SEXPR()
    live=io.LoadBoard(str(Path(request['export']).resolve()),None)
    require(live is not None,'Native IPC export could not be read')
    require(api.SaveBoard(str(root/'source-canonical.kicad_pcb'),source),'Source canonical save failed')
    require(api.SaveBoard(str(root/'live-canonical.kicad_pcb'),live),'IPC export canonical save failed')
    result=dict(source_canonical_sha256=digest(root/'source-canonical.kicad_pcb'),
                live_canonical_sha256=digest(root/'live-canonical.kicad_pcb'),
                original_source_sha256=digest(c['source']),native_export_sha256=request['sha256'])
    result['complete_native_board_equal']=result['source_canonical_sha256']==result['live_canonical_sha256']
    write_json(root/'canonical-proof.json',result);verify_context(root)
    require(result['complete_native_board_equal'],'Genuine saved/live native source difference')
    print('Complete native canonical source/export identity PASS',flush=True)


def readback_worker(root):
    from .safety import verify_context
    from .native import api_load
    from .geometry import snapshot,layout_snapshot
    from .stencil_scratch import restore_paste,native_save
    root=Path(root);c=verify_context(root)
    require(not (root/'native-readback.json').exists(),'Fresh independent native readback required')
    api,b=api_load(c['board'])
    require(snapshot(b,api)==read_json(TROOT/'candidate-v3/before-native.json'),
            'Original native electrical/physical geometry changed')
    require(layout_snapshot(b,api)==read_json(TROOT/'candidate-v3/before-layout.json'),
            'Original actual fills/outline/courtyards changed')
    restore_paste(api,b,read_json(TROOT/'candidate-v3/transaction.json'))
    restored=root/'restored-source.kicad_pcb';native_save(api,b,restored)
    require(digest(restored)==SOURCE_SHA,'Full native board differs beyond the accepted paste delta')
    write_json(root/'native-readback.json',dict(status='PASS',saved_source_sha256=digest(c['source']),
        complete_restored_native_source_sha256=digest(restored),all_original_native_geometry_equal=True,
        all_original_layout_equal=True,pads=473,vias=324,PTH=41,NPTH=12))
    verify_context(root);print('Independent complete native preservation PASS',flush=True)


def observe(root,action):
    """Bind the sole native editor and socket from OS evidence, never guessing."""
    import os,subprocess
    from .j7_migration import resolve_endpoint
    root=Path(root);c=read_json(root/'editor-context.json');launch=read_json(root/'editor-launch.json')
    path=root/('os-'+action+'.json');require(not path.exists(),'Fresh OS observation required')
    command=r"""$ErrorActionPreference='Stop'; [ordered]@{
processes=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(pcbnew|eeschema|kicad)\.exe$' } | Select-Object ProcessId,Name,CommandLine);
pipes=@(Get-ChildItem '\\.\pipe\' | Where-Object { $_.Name -match 'kicad' -and $_.Name -match 'api.sock$' } | Select-Object -ExpandProperty Name)
} | ConvertTo-Json -Depth 4 -Compress"""
    shell=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
    r=subprocess.run([str(shell),'-NoProfile','-Command',command],capture_output=True,text=True,timeout=30)
    require(r.returncode==0,'OS discovery failed before IPC: '+r.stderr)
    observed=json.loads(r.stdout);write_json(path,observed)
    return resolve_endpoint(observed,c['target'],launch['process_id'],'auto')


def clean_window(root,action):
    import subprocess
    root=Path(root);c=read_json(root/'editor-context.json')
    output=root/('windows-'+action+'.json')
    manifest=root/'installed-manifest.json' if action=='verify-live' else Path(c['manifest'])
    command=[sys.executable,'-B','-m','v4kicad.editor_lifecycle','--launch',root/'editor-launch.json',
             '--board',c['target'],'--manifest',manifest,'--output',output]
    r=subprocess.run([str(x) for x in command],capture_output=True,text=True,timeout=30)
    require(r.returncode==0,'Editor window preflight failed: '+r.stderr)
    rows=read_json(output)['windows']
    frames=[r for r in rows if 'PCB Editor' in r['title'] and Path(c['target']).stem in r['title']]
    dialogs=[r for r in rows if r['window_class']=='#32770' or
             (r['window_class']=='wxWindowNR' and r not in frames and r['title']!='panel')]
    require(len(frames)==1 and not dialogs and '*' not in frames[0]['title'],
            'Dirty/ambiguous/modal editor; no IPC mutation allowed')


def snapshot_worker(root,socket):
    from .ipc_install import capture
    root=Path(root);c=read_json(root/'editor-context.json');target=Path(c['target'])
    require(digest(target)==c['sha256'],'Target saved identity differs')
    sys.path.insert(0,str(PRODUCTION.parent.resolve()/'.konnect/native-ipc'))
    from kipy import KiCad
    from kipy.proto.common.types.base_types_pb2 import DocumentType
    k=KiCad(socket_path=socket,client_name='UPS V4 Phase4.24U guarded paste identity')
    require(k.get_version().major==10,'KiCad10 owning editor required')
    require(len(k.get_open_documents(DocumentType.DOCTYPE_PCB))==1,'Ambiguous PCB documents')
    board=k.get_board()
    require(board.name==target.name and Path(board.document.project.path).resolve()==target.parent.resolve(),
            'Wrong owning document')
    serialized=board.get_as_string()
    (root/'live-serialized.txt').write_text(serialized,encoding='utf-8')
    current=capture(board);write_json(root/'capture.json',current)
    write_json(root/'capture-complete.json',dict(native_string_export_captured=True,
        target=str(target),sha256=digest(target),version=str(k.get_version()),
        counts={s:len(v) for s,v in current.items()}))
    require(digest(target)==c['sha256'],'Read-only source changed')
    print('Read-only editor capture complete; independent canonical identity still required',flush=True)


def postcheck(root,output):
    from .safety import prepare_scratch
    from .checks import parse_check
    from .gerber_review import compose,difference
    from .stencil_review import parts
    from collections import Counter
    import shutil
    root,output=Path(root),Path(output);c,p=guard(root,installed=True);target=Path(c['target'])
    output=prepare_scratch(target,root/'installed-manifest.json',output)
    for name in ('fp-lib-table','sym-lib-table'):
        if (target.parent/name).exists():shutil.copy2(target.parent/name,output/name)
    for name in ('ups_v4.pretty','ups_v4_external.pretty'):
        shutil.copytree(target.parent/name,output/name)
    for path in target.parent.glob('*.kicad_sym'):shutil.copy2(path,output/path.name)
    entry=Path(__file__).resolve().parents[1]/'kicad_v4.py'
    run_monitored(['C:/Program Files/KiCad/10.0/bin/python.exe','-B',entry,'_worker',
                   '--scratch-dir',output,'--action','stencil-adoption-readback'],output/'native-readback.log')
    cli='C:/Program Files/KiCad/10.0/bin/kicad-cli.exe';board=output/target.name
    checks={}
    for kind in ('drc','erc'):
        report=output/(kind+'.json')
        command=([cli,'pcb','drc','--format','json','--all-track-errors','--schematic-parity','--output',report,board]
                 if kind=='drc' else [cli,'sch','erc','--format','json','--output',report,board.with_suffix('.kicad_sch')])
        run_monitored(command,output/(kind+'.log'))
        checks[kind]=parse_check(read_json(report),kind);write_json(output/(kind+'-summary.json'),checks[kind])
        require(checks[kind]['errors']==0,'Native '+kind+' errors')
    require(checks['drc']['unconnected']==checks['drc']['parity']==0,'Native opens/parity errors')
    actual=read_json(output/'drc.json');accepted=read_json(TROOT/'native-checks/candidate-drc.json')
    key=lambda v:json.dumps(v,sort_keys=True)
    require(Counter(map(key,actual['violations']))==Counter(map(key,accepted['violations'])),
            'DRC warning identities/causes differ from accepted Phase4.24T')
    require(actual['ignored_checks']==accepted['ignored_checks'],'Ignored DRC checks changed')
    gerbers=output/'focused-paste-export';gerbers.mkdir()
    run_monitored([cli,'pcb','export','gerbers','--layers','F.Paste','--precision','6',
                   '--output',gerbers,board],gerbers/'export.log')
    files=list(gerbers.glob('*.gtp'));require(len(files)==1 and files[0].stat().st_size>0,'Missing/ambiguous fresh GTP')
    sys.path.insert(0,str((BASE/'evidence/phase4-24-owner-gerber-review/deps').resolve()))
    from gerbonara import GerberFile
    a=compose(GerberFile.open(TROOT/'candidate-v3/paste-export/ups12v_v4-F_Paste.gtp'))
    b=compose(GerberFile.open(files[0]));cam=difference(a,b,.000005)
    cam.update(physical_openings=len(parts(b)),accepted_gtp_sha256=digest(TROOT/'candidate-v3/paste-export/ups12v_v4-F_Paste.gtp'),
               actual_gtp_sha256=digest(files[0]),production_derived=c['production'])
    write_json(output/'accepted-gtp-comparison.json',cam)
    require(cam['pass_geometry'] and cam['physical_openings']==411,'Actual GTP differs from accepted 411-opening pattern')
    guard(root,installed=True)
    result=dict(status='PASS',production=c['production'],plan_sha256=c['plan_sha256'],
        target_sha256=digest(target),checks=checks,warning_identities_exactly_Phase424T=True,
        native_preservation=read_json(output/'native-readback.json'),GTP=cam,
        artifacts={str(x.resolve()):digest(x) for x in [board,output/'drc.json',output/'erc.json',
            output/'native-readback.json',output/'accepted-gtp-comparison.json',files[0]]})
    write_json(output/'postcheck.json',result)
    print(json.dumps(dict(status='PASS',physical_openings=411,DRC=checks['drc']['errors'],
                         opens=checks['drc']['unconnected'],parity=checks['drc']['parity'],ERC=checks['erc']['errors'],
                         warnings=checks['drc']['warnings'],source_preservation='complete native equality')))


def accept_rehearsal(root,checks,output):
    root,checks,output=Path(root),Path(checks),Path(output);c,p=guard(root,installed=True)
    require(not c['production'] and not output.exists(),'Fresh rehearsal-only proof required')
    check=read_json(checks/'postcheck.json')
    require(check['status']=='PASS' and not check['production'] and check['plan_sha256']==c['plan_sha256']
            and check['target_sha256']==digest(c['target']),'Rehearsal postcheck binding mismatch')
    require(read_json(root/'final-live-proof.json')['sha256']==digest(c['target']),'Final live/saved proof required')
    bindings={str(x.resolve()):digest(x) for x in [Path(c['target']),root/'ipc-before.json',root/'ipc-after.json',
        root/'ipc-saved.json',root/'live-saved.json',root/'final-live-proof.json',checks/'postcheck.json']}
    bindings.update(check['artifacts'])
    write_json(output,dict(status='PASS_COMPLETE_REHEARSAL',plan_sha256=c['plan_sha256'],
        implementations=p['implementations'],bindings=bindings,exact_ten_graphics=True,
        exact_four_original_pad_changes=True,saved_sha256=digest(c['target'])))
    print('Complete owning-editor rehearsal PASS; production gate established')


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('snapshot');q.add_argument('--root',type=Path,required=True)
    q=sub.add_parser('_snapshot');q.add_argument('--root',type=Path,required=True);q.add_argument('--socket',required=True)
    q=sub.add_parser('plan')
    for n in ('entry','goal','output'):q.add_argument('--'+n,type=Path,required=True)
    q=sub.add_parser('prepare')
    for n in ('plan','output'):q.add_argument('--'+n,type=Path,required=True)
    q.add_argument('--rehearsal',type=Path)
    q=sub.add_parser('postcheck')
    for n in ('root','output'):q.add_argument('--'+n,type=Path,required=True)
    q=sub.add_parser('accept-rehearsal')
    for n in ('root','checks','output'):q.add_argument('--'+n,type=Path,required=True)
    for action in ('preflight','apply','verify-live','_preflight','_apply','_verify-live'):
        q=sub.add_parser(action);q.add_argument('--root',type=Path,required=True)
        if action.startswith('_'):q.add_argument('--socket',required=True)
    a=p.parse_args()
    if a.action=='plan':plan(a.entry,a.goal,a.output);return
    if a.action=='prepare':prepare(a.plan,a.output,a.rehearsal);return
    if a.action=='postcheck':postcheck(a.root,a.output);return
    if a.action=='accept-rehearsal':accept_rehearsal(a.root,a.checks,a.output);return
    if a.action in ('_preflight','_apply','_verify-live'):
        transaction_worker(a.root,a.socket,a.action[1:]);return
    if a.action in ('preflight','apply','verify-live'):
        guard(a.root,installed=a.action=='verify-live')
        log=a.root/(a.action+'.log');require(not log.exists(),'Already attempted native action; no retry')
        endpoint=observe(a.root,a.action);clean_window(a.root,a.action)
        try:
            result=run_monitored([sys.executable,'-B','-m','v4kicad.stencil_adoption','_'+a.action,
                                  '--root',a.root,'--socket',endpoint],log)
        except (ToolError,OSError) as error:
            write_json(a.root/'STOP.json',dict(action=a.action,error=str(error)));raise
        print(result['stdout']);return
    if a.action=='_snapshot':snapshot_worker(a.root,a.socket);return
    require(not (a.root/'STOP.json').exists(),'Stopped editor context; no retry/recovery')
    log=a.root/'snapshot.log';require(not log.exists(),'Fresh snapshot context required')
    endpoint=observe(a.root,'snapshot');clean_window(a.root,'snapshot')
    try:
        r=run_monitored([sys.executable,'-B','-m','v4kicad.stencil_adoption','_snapshot',
                         '--root',a.root,'--socket',endpoint],log)
    except (ToolError,OSError) as error:
        write_json(a.root/'STOP.json',dict(action='snapshot',error=str(error)));raise
    print(r['stdout'])
    from .safety import prepare_scratch
    c=read_json(a.root/'editor-context.json')
    proof=prepare_scratch(c['target'],c['manifest'],a.root/'native-canonical-proof')
    export=(a.root/'live-serialized.txt').resolve()
    write_json(proof/'normalization-request.json',dict(export=str(export),sha256=digest(export)))
    entry=Path(__file__).resolve().parents[1]/'kicad_v4.py'
    try:
        r=run_monitored(['C:/Program Files/KiCad/10.0/bin/python.exe','-B',entry,'_worker',
                         '--scratch-dir',proof,'--action','stencil-serialization-proof'],proof/'worker.log')
    except (ToolError,OSError) as error:
        write_json(a.root/'STOP.json',dict(action='canonical-identity',error=str(error)));raise
    require(digest(c['target'])==c['sha256'],'Source drift during identity proof')
    write_json(a.root/'snapshot-proof.json',dict(saved_live_complete_native_board_equal=True,
        canonical_proof=str((proof/'canonical-proof.json').resolve()),sha256=c['sha256']))
    print(r['stdout'])


if __name__=='__main__':main()
