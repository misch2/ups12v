"""Phase4.21 exact three-track owning-editor migration; import-safe.

The accepted scratch is evidence, never a replacement for production. Reuse the
guarded native transaction, fill comparison and isolated review infrastructure.
"""
from pathlib import Path
import argparse
import copy
import sys

from .safety import (require, read_json, write_json, digest, verify_hashes,
                     prepare_scratch, run_monitored, ToolError)
from .migration import delta, verify_refilled_capture
from .owner_migration import native_capture, build_transaction as build_copper

BASE = Path('hardware/v4')
PRODUCTION = BASE/'ups_v4/ups12v_v4.kicad_pcb'
MANIFEST = BASE/'evidence/phase4-18-production-adoption/accepted-installed-baseline.json'
GOAL = BASE/'evidence/phase4-20-j7-candidate'
ACCEPTED = '4e13e4c11c486aa4fba7866817f5c37e715b248ab696cbd4a599970cf2a2ea84'
APPROVED = '4eb7bd2c72fec3cf49d3746250864b5237e7919760ebdbc3647cbc0101fa8737'
OLD = ['4d552340-51f3-4a54-8e44-32e11454ef13', '1814d666-f764-4da0-839c-339e7a06c1ca',
       '878d8bda-a418-454a-8362-c06c73dcd100']
NEW = ['6b749cde-148c-4782-a324-42b2486548e4', '4c8fa43c-a929-427d-a375-6b9d0366ee00',
       'a01da3d3-795d-4da0-9171-01cdf01cb32a']
BEFORE = [[119.050,75.300], [119.800,76.050], [119.800,78.665], [118.740,79.725]]
AFTER = [[119.050,75.300], [119.860,76.110], [119.860,78.605], [118.740,79.725]]
COUNTS = dict(tracks=1170, vias=324, footprints=154, pads=473)


def implementations():
    names = ['j7_migration.py','owner_migration.py','migration.py','ipc_install.py',
             'safety.py','geometry.py','native.py','cli.py','checks.py','replacement.py',
             'j7_dfm_review.py','prefab_review.py','plan_validation.py','review_compare.py']
    return {str(Path(__file__).with_name(n).resolve()):digest(Path(__file__).with_name(n)) for n in names}


def reconcile(before, after):
    require(set(before)==set(after), 'Snapshot sections changed')
    ops = {s:delta(before[s],after[s]) for s in before}
    require({s:len(after[s]) for s in COUNTS}==COUNTS, 'Inventory count changed')
    for s,d in ops.items():
        if s!='tracks':
            require(not any(d.values()), 'Unauthorized object delta: '+s)
    d=ops['tracks']
    require(set(d['removed'])==set(OLD) and set(d['added'])==set(NEW) and not d['modified'],
            'Only the exact approved three-track replacement is authorized')
    for ids,points,key in [(OLD,BEFORE,'removed'),(NEW,AFTER,'added')]:
        for i,u in enumerate(ids):
            r=d[key][u]
            require(r['uuid']==u and r['net']=='USB_CC2' and r['layer']=='In2.Cu'
                    and r['width']==.180 and r['start']==points[i] and r['end']==points[i+1]
                    and r.get('kind')=='track', 'Approved track preimage/geometry differs: '+u)
    arcs=lambda g:{u:r for u,r in g['tracks'].items() if r.get('geometry')=='arc'}
    require(len(arcs(before))==8 and arcs(before)==arcs(after), 'Eight native arcs changed')
    return ops


def bindings(plan_path, installed=False):
    p=read_json(plan_path)
    require(p['hashes'][PRODUCTION.name]==ACCEPTED and p['candidate_sha256']==APPROVED,
            'Unapproved source identities')
    hashes=p['hashes'].copy()
    if installed:hashes.pop(PRODUCTION.name)
    verify_hashes(PRODUCTION.parent,hashes)
    require(digest(GOAL/PRODUCTION.name)==APPROVED, 'Approved candidate changed')
    for name,wanted in p['bound_artifacts'].items():require(digest(name)==wanted, 'Artifact drift: '+name)
    return p


def make_plan(entry, output):
    entry,output=Path(entry),Path(output)
    before=read_json(entry/'snapshot.json');goal=read_json(GOAL/'final-snapshot.json')
    require(before==read_json(GOAL/'before.json'), 'Fresh entry differs from approved source export')
    require(read_json(entry/'context.json')['source_hashes']==read_json(MANIFEST)['hashes'], 'Entry hash drift')
    ops=reconcile(before,goal)
    paths=[MANIFEST,entry/'snapshot.json',entry/'context.json',entry/'layout.json',entry/'routing-context.json',
           GOAL/'before.json',GOAL/'final-snapshot.json',GOAL/'layout-final.json',GOAL/'audit-before.json',
           GOAL/'pad-partition-before.json',GOAL/'plan.json',GOAL/'summary.json',
           BASE/'evidence/phase4-20-j7-review/geometry-screen.json']
    p=dict(phase='4.21',production_board=str(PRODUCTION.resolve()),candidate_sha256=APPROVED,
           entry=str(entry.resolve()),hashes=read_json(MANIFEST)['hashes'],operations=ops,
           bound_artifacts={str(x.resolve()):digest(x) for x in paths})
    require(not output.exists(), 'Fresh plan required')
    output.parent.mkdir(exist_ok=True);write_json(output,p);bindings(output)
    print('Exact approved UUID/preimage delta PASS:3removed/3added; all other objects equal')


def prepare(plan, output, proof=None, identity_only=False):
    plan,output=Path(plan),Path(output);p=bindings(plan)
    require(not (proof and identity_only), 'Identity preflight cannot install')
    if identity_only:
        require(not output.exists(), 'Fresh identity evidence required');output.mkdir()
        target=PRODUCTION.resolve()
    elif proof:
        q=read_json(proof)
        require(q['verdict']=='PASS_COMPLETE_CANDIDATE' and q['plan_hash']==digest(plan)
                and q['implementations']==implementations(), 'Identical completed rehearsal required')
        for name,wanted in q['candidate_sources'].items():require(digest(name)==wanted, 'Rehearsal drift')
        require(not output.exists(), 'Fresh production evidence directory required');output.mkdir()
        target=PRODUCTION.resolve()
    else:
        prepare_scratch(PRODUCTION,MANIFEST,output);target=output.resolve()/PRODUCTION.name
    c=dict(phase='4.21',production=bool(proof),identity_only=identity_only,target=str(target),plan=str(plan.resolve()),
           plan_hash=digest(plan),implementations=implementations())
    if proof:c.update(proof=str(Path(proof).resolve()),proof_hash=digest(proof))
    write_json(output/'j7-migration-context.json',c)
    print('Prepared '+('read-only production identity' if identity_only else 'production' if proof else 'isolated owning-editor rehearsal'))


def check_context(root, installed=False):
    root=Path(root);require(not (root/'STOP.json').exists(), 'Migration stopped; no IPC/recovery')
    c=read_json(root/'j7-migration-context.json')
    require(c['implementations']==implementations() and digest(c['plan'])==c['plan_hash'], 'Implementation/plan drift')
    p=bindings(c['plan'],installed)
    if c['production']:
        require(digest(c['proof'])==c['proof_hash'], 'Rehearsal proof drift')
        q=read_json(c['proof'])
        require(q['verdict']=='PASS_COMPLETE_CANDIDATE' and q['plan_hash']==c['plan_hash']
                and q['implementations']==c['implementations'], 'Identical completed rehearsal required')
        for name,wanted in q['candidate_sources'].items():require(digest(name)==wanted, 'Rehearsal drift')
    return c,p


def build_transaction(board, before, p):
    cp=dict(operations={s:dict(create=p['operations'][s]['added'],
        remove_with_preimage=p['operations'][s]['removed'],update_with_preimage={}) for s in ['tracks','vias']})
    cp['operations']['footprints']=dict(translate_whole_instance_with_preimage={})
    updates,creates,removes,expected=build_copper(board,before,cp,{})
    require(not updates and {x.id.value for x in creates}==set(NEW)
            and {x.id.value for x in removes}==set(OLD), 'Exact3remove/3create transaction required')
    return creates,removes,expected


def capture_equal(expected, actual):
    """Use the established per-section normalization of runtime item parents.

    Calling native_capture on the entire capture adds a nesting level, retaining
    the board-parent link that CRUD returns only after items enter the board.
    Never normalize child geometry or omit payload fields to accommodate this.
    """
    return set(expected)==set(actual) and all(
        native_capture(expected[s])==native_capture(actual[s]) for s in expected)


def resolve_endpoint(observed, target, pid, requested):
    """Pure OS-evidence guard; refuse wrong/ambiguous endpoints before KiCad."""
    processes=observed['processes'];pipes=observed['pipes']
    require(len(processes)==1 and processes[0]['ProcessId']==pid
            and processes[0]['Name'].lower()=='pcbnew.exe', 'Ambiguous/unexpected owning process')
    norm=lambda s:str(s).replace('\\','/').casefold()
    require(('"'+norm(Path(target).resolve())+'"') in norm(processes[0]['CommandLine']),
            'Owning process document differs')
    require(len(pipes)==1 and isinstance(pipes[0],str) and pipes[0].endswith('api.sock'),
            'Missing/ambiguous observed KiCad named pipe; no IPC attempted')
    endpoint='ipc://'+pipes[0]
    require(requested=='auto' or norm(requested)==norm(endpoint),
            'Requested endpoint differs from current OS named pipe; no IPC attempted')
    return endpoint


def observed_endpoint(root, requested, action):
    """Inspect OS only, then bind connection to the launched PID and document."""
    import json
    import os
    import subprocess
    root=Path(root);c=read_json(root/'j7-migration-context.json')
    launch=read_json(root/'editor-launch.json')
    command=r"""$ErrorActionPreference='Stop'; [ordered]@{
processes=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(pcbnew|eeschema|kicad)\.exe$' } | Select-Object ProcessId,Name,CommandLine);
pipes=@(Get-ChildItem '\\.\pipe\' | Where-Object { $_.Name -match 'kicad' -and $_.Name -match 'api.sock$' } | Select-Object -ExpandProperty Name)
} | ConvertTo-Json -Depth 4 -Compress"""
    shell=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
    result=subprocess.run([str(shell),'-NoProfile','-Command',command],capture_output=True,text=True,timeout=30)
    require(result.returncode==0, 'OS endpoint discovery failed; no IPC attempted: '+result.stderr)
    observed=json.loads(result.stdout)
    output=root/('os-endpoint-'+action+'.json')
    require(not output.exists(), 'Fresh endpoint observation required')
    write_json(output,observed)
    endpoint=resolve_endpoint(observed,c['target'],launch['process_id'],requested)
    print('OS PID/document/endpoint bound: '+endpoint,flush=True)
    return endpoint


def worker(root, action, socket):
    from .ipc_install import capture
    root=Path(root);c,p=check_context(root,installed=action=='verify-saved');target=Path(c['target'])
    require((target==PRODUCTION.resolve())==(c['production'] or c['identity_only']), 'Wrong target scope')
    if c['identity_only']:require(action=='preflight', 'Identity context is read-only')
    elif not c['production']:require(target.parent==root.resolve(), 'Rehearsal must be isolated')
    for name,wanted in p['hashes'].items():
        if name!=target.name:require(digest(target.parent/name)==wanted, 'Companion drift')
    sys.path.insert(0,str(PRODUCTION.parent.resolve()/'.konnect/native-ipc'))
    from kipy import KiCad
    from kipy.proto.common.types.base_types_pb2 import DocumentType
    k=KiCad(socket_path=socket,client_name='UPS V4 Phase4.21 exact J7 adoption')
    require(k.get_version().major==10, 'KiCad10 required')
    require(len(k.get_open_documents(DocumentType.DOCTYPE_PCB))==1, 'Ambiguous editor documents')
    b=k.get_board()
    require(b.name==target.name and Path(b.document.project.path).resolve()==target.parent, 'Wrong owning document')
    before=capture(b)
    if action=='verify-saved':
        require(native_capture(before)==native_capture(read_json(root/'live-saved.json')), 'Saved/live drift')
        require(digest(target)==read_json(root/'ipc-saved.json')['board_sha256'], 'Saved PCB drift')
        write_json(root/'final-live-readback.json',dict(saved_live_exact=True,board_sha256=digest(target)))
        print('Final saved/live identity PASS');return
    require(digest(target)==ACCEPTED, 'Accepted source PCB changed')
    baseline=read_json(MANIFEST)
    for s in before:require(native_capture(before[s])==native_capture(baseline[s]), 'Uncertain unsaved/live changes: '+s)
    if action=='preflight':
        require(not (root/'ipc-preflight.json').exists(), 'Fresh preflight required')
        write_json(root/'ipc-before.json',before)
        write_json(root/'ipc-preflight.json',dict(saved_live_exact=True,version=str(k.get_version()),target=str(target)))
        print('Fresh exact saved/live entry PASS');return
    require(action=='apply' and (root/'ipc-preflight.json').exists() and not (root/'commit.json').exists(),
            'Fresh preflighted unattempted transaction required')
    require(native_capture(before)==native_capture(read_json(root/'ipc-before.json')), 'Entry drift since preflight')
    reconcile(read_json(Path(p['entry'])/'snapshot.json'),read_json(GOAL/'final-snapshot.json'))
    creates,removes,expected=build_transaction(b,before,p)
    write_json(root/'ipc-expected.json',expected)
    write_json(root/'prepared-transaction.json',dict(create=NEW,remove=OLD,update=[]))
    check_context(root)
    commit=b.begin_commit();write_json(root/'commit.json',dict(value=commit.id.value))
    b.remove_items(removes);actual=b.create_items(creates)
    from google.protobuf.json_format import MessageToDict
    returned={x.id.value:MessageToDict(x.proto) for x in actual}
    write_json(root/'returned-items.json',returned)
    require(native_capture(returned)==native_capture({x.id.value:MessageToDict(x.proto) for x in creates}),
            'Returned item UUID/payload mismatch')
    b.push_commit(commit,'Phase4.21 exact accepted J7 USB_CC2 DFM adoption')
    after=capture(b);write_json(root/'ipc-after.json',after)
    require(capture_equal(expected,after), 'Post-commit native preservation failure')
    b.refill_zones();filled=capture(b);write_json(root/'live-refilled.json',filled)
    verify_refilled_capture(after,filled,read_json(GOAL/'layout-final.json'))
    b.save();saved=capture(b)
    require(native_capture(saved)==native_capture(filled), 'Editor save changed native payload')
    write_json(root/'live-saved.json',saved)
    write_json(root/'ipc-saved.json',dict(board_sha256=digest(target),saved_through_editor=True))
    installed=copy.deepcopy(saved)
    installed['hashes']={name:digest(target.parent/name) for name in p['hashes']}
    write_json(root/'installed-manifest.json',installed);check_context(root,installed=True)
    print('Exact3track transaction/readback/refill/owning-editor save PASS')


def prove(review, transaction, output):
    from .replacement import serialized_retained
    from .j7_dfm_review import selected_screen, physical_fill_equal
    from .prefab_review import audit
    from .review_compare import warning_rows
    review,transaction,output=map(Path,[review,transaction,output]);c,p=check_context(transaction,installed=True)
    current=read_json(review/'snapshot.json');goal=read_json(GOAL/'final-snapshot.json')
    require(current==goal, 'Independent saved native geometry differs from approved candidate')
    reconcile(read_json(Path(p['entry'])/'snapshot.json'),current)
    inspection=read_json(review/'native-review-inspection.json')
    require(inspection['audit']==read_json(GOAL/'audit-before.json'), 'Artwork/zone/RF definition changed')
    groups=inspection['pad_partitions']
    require(groups==read_json(GOAL/'pad-partition-before.json') and len(groups)==116
            and len({u for g in groups for u in g})==473, '473pads/116islands differ')
    require(serialized_retained(Path(p['entry'])/PRODUCTION.name,OLD)==
            serialized_retained(review/PRODUCTION.name,NEW), 'Unapproved saved non-fill property change')
    layout=read_json(review/'post-refill-layout.json')
    require(physical_fill_equal(read_json(GOAL/'layout-final.json'),layout), 'Actual PGND polygons/holes changed')
    context=read_json(review/'routing-context.json')
    screen=selected_screen(context,set(NEW))
    require(abs(screen['shell_min_gap_mm']-.350)<1e-6, 'J7PTH clearance differs from0.350mm')
    vendor=audit(context,read_json(MANIFEST),layout);write_json(transaction/'vendor-screen.json',vendor)
    require(not vendor['pth_track_below_published_screen'] and not vendor['pth_plane_below_published_screen']
            and not vendor['hole_pair_below_published_screen'], 'Vendor screen violation')
    summary=read_json(review/'summary.json')
    require(summary['drc']['errors']==summary['drc']['unconnected']==summary['drc']['parity']==summary['erc']['errors']==0,
            'Independent ERC/DRC/parity/connectivity must be zero')
    for kind in ['drc','erc']:
        require(warning_rows(read_json(GOAL/(kind+'.json')),kind)==warning_rows(read_json(review/(kind+'.json')),kind),
                'Matched isolated warning identities changed: '+kind)
    production_checks=None
    if c['production']:
        production_checks=read_json(transaction/'production-checks.json')
        require(production_checks['drc']['errors']==production_checks['drc']['unconnected']==
                production_checks['drc']['parity']==production_checks['erc']['errors']==0, 'Production check errors')
        for kind in ['drc','erc']:
            require(warning_rows(read_json(transaction/('production-'+kind+'.json')),kind)==
                    warning_rows(read_json(BASE/'evidence/phase4-18-production-adoption'/('production-'+kind+'.json')),kind),
                    'Production warning identity changed: '+kind)
    require(read_json(transaction/'final-live-readback.json')['saved_live_exact'], 'Final live identity missing')
    installed=read_json(transaction/'installed-manifest.json');target=Path(c['target'])
    verify_hashes(target.parent,installed['hashes'])
    proof=dict(verdict='PASS_FINAL_PRODUCTION' if c['production'] else 'PASS_COMPLETE_CANDIDATE',
        plan_hash=c['plan_hash'],implementations=implementations(),
        candidate_sources={str((target.parent/n).resolve()):h for n,h in installed['hashes'].items()},
        board_sha256=digest(target),checks=summary,production_checks=production_checks,
        exact_approved_uuid_delta=True,counts=COUNTS,pad_islands=116,native_arcs=8,
        saved_live_exact=True,non_fill_properties_preserved=True,actual_PGND_fill_equal=True,
        F0_F5_and_all_other_copper_exact=True,J7_shell_PTH_gap_mm=screen['shell_min_gap_mm'],
        vendor_screen_violations=0,independent_review=str(review.resolve()))
    write_json(transaction/'J7-clearance.json',screen);write_json(output,proof)
    if c['production']:write_json(transaction/'accepted-installed-baseline.json',installed)
    print(proof['verdict']+':473pads/116islands/324vias/8arcs;0physical/0opens/0parity/ERC0;J7PTH0.350mm')


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('plan');q.add_argument('--entry',type=Path,required=True);q.add_argument('--output',type=Path,required=True)
    q=sub.add_parser('prepare')
    for n in ['plan','output']:q.add_argument('--'+n,type=Path,required=True)
    q.add_argument('--proof',type=Path)
    q.add_argument('--identity-only',action='store_true')
    q=sub.add_parser('prove')
    for n in ['review','transaction','output']:q.add_argument('--'+n,type=Path,required=True)
    q=sub.add_parser('observe-endpoint',help='OS-only diagnosis; never connects to KiCad')
    q.add_argument('--root',required=True,type=Path);q.add_argument('--socket',default='auto')
    for action in ['preflight','apply','verify-saved','_worker-preflight','_worker-apply','_worker-verify-saved']:
        q=sub.add_parser(action);q.add_argument('--root',required=True,type=Path);q.add_argument('--socket',required=True)
    a=p.parse_args()
    try:
        if a.action=='plan':make_plan(a.entry,a.output)
        elif a.action=='prepare':prepare(a.plan,a.output,a.proof,a.identity_only)
        elif a.action=='prove':prove(a.review,a.transaction,a.output)
        elif a.action=='observe-endpoint':observed_endpoint(a.root,a.socket,'diagnosis')
        elif a.action.startswith('_worker-'):worker(a.root,a.action[8:],a.socket)
        else:
            require(not (a.root/'STOP.json').exists(), 'Stopped migration; no retry')
            log=a.root/('ipc-'+a.action+'.log');require(not log.exists(), 'Already attempted; no retry')
            endpoint=observed_endpoint(a.root,a.socket,a.action)
            try:run_monitored([sys.executable,'-B','-m','v4kicad.j7_migration','_worker-'+a.action,
                               '--root',a.root,'--socket',endpoint],log)
            except (ToolError,OSError) as e:
                write_json(a.root/'STOP.json',dict(action=a.action,error=str(e)));raise
            print('Monitored '+a.action+' complete')
        return 0
    except (ToolError,OSError,ValueError,KeyError,TypeError) as e:
        print('STOP: '+str(e),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
