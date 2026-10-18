"""Owner-authorized Phase4.24W wrapper for the exact accepted V native delta."""
import argparse
import ast
from collections import Counter
import json
import os
from pathlib import Path
import subprocess

from .safety import (require,read_json,write_json,digest,prepare_scratch,verify_context,
                     unlocked,run_monitored,ToolError)
from .stencil_native_proof import (PRODUCTION,GOAL,GOAL_SHA,TROOT,TARGETS,SOURCE_SHA,
    native_units,require_units_equal,copy_libraries)
from .stencil_scratch import layer_set,native_save,restore_paste
from .native import api_load
from .geometry import snapshot,layout_snapshot

VROOT=Path('hardware/v4/evidence/phase4-24v-native-paste-proof')
ENTRY=Path(__file__).resolve().parents[1]/'stencil_install.py'


def native_delta(api,board,root):
    _,accepted=api_load(GOAL)
    transaction=read_json(TROOT/'candidate-v3/transaction.json')
    original_fps={fp.m_Uuid.AsString():fp for fp in board.GetFootprints()}
    pads={pad.m_Uuid.AsString():(fp,pad) for fp in board.GetFootprints() for pad in fp.Pads()}
    all_ids={g.m_Uuid.AsString() for fp in board.GetFootprints() for g in fp.GraphicalItems()}
    graphics={g.m_Uuid.AsString():(fp,g) for fp in accepted.GetFootprints() for g in fp.GraphicalItems()}
    require(len(set(transaction['added_graphics']))==10,'Exactly ten accepted graphics required')
    require(not all_ids.intersection(transaction['added_graphics']),'Graphic UUID already exists')
    for ref,(number,uid) in TARGETS.items():
        fp,pad=pads[uid]
        require(fp.GetReference()==ref and pad.GetNumber()==number,'Physical target identity mismatch')
        old=list(pad.GetLayerSet().Seq())
        row=next(r for r in transaction['changed_pads'] if r['uuid']==uid)
        require(old==row['original_layer_ids'] and api.F_Paste in old,'Pad layer preimage mismatch')
    # Native object changes only. Do not replace or deserialize footprints.
    for ref,(number,uid) in TARGETS.items():
        fp,pad=pads[uid];old=list(pad.GetLayerSet().Seq())
        pad.SetLayerSet(layer_set(api,[l for l in old if l!=api.F_Paste]))
    added=[]
    for uid in transaction['added_graphics']:
        owner,g=graphics[uid];fp=original_fps[owner.m_Uuid.AsString()]
        require(fp.GetReference() in TARGETS and isinstance(g,api.PCB_SHAPE) and g.GetLayer()==api.F_Paste,
                'Unapproved accepted footprint graphic')
        shape=api.Cast_to_PCB_SHAPE(api.Cast_to_BOARD_ITEM(g.Clone()))
        require(shape is not None and shape.m_Uuid.AsString()==uid,'Native clone changed graphic identity')
        shape.SetParent(fp);fp.Add(shape);added.append(uid)
    require(snapshot(board,api)==read_json(root/'before-native.json'),'Native geometry/connectivity changed')
    require(layout_snapshot(board,api)==read_json(root/'before-layout.json'),'Native layout/fills changed')
    return added,transaction


def operation_proof(candidate=None):
    """Compare the executed native operation AST to immutable accepted V code."""
    source=Path(__file__).with_name('stencil_native_proof.py')
    tree=ast.parse(source.read_text(encoding='utf-8'))
    f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='worker')
    apply=next(x for x in ast.walk(f) if isinstance(x,ast.If) and
               ast.unparse(x.test)=="action == 'apply'")
    start=next(i for i,s in enumerate(apply.body) if isinstance(s,ast.Assign) and
               isinstance(s.value,ast.Call) and ast.unparse(s.value)=='api_load(GOAL)')
    end=next(i for i,s in enumerate(apply.body) if isinstance(s,ast.Expr) and
             isinstance(s.value,ast.Call) and ast.unparse(s.value.func)=='native_save')
    original=ast.Module(body=apply.body[start:end],type_ignores=[])
    candidate=Path(__file__).read_text(encoding='utf-8') if candidate is None else candidate
    current=next(x for x in ast.parse(candidate).body if isinstance(x,ast.FunctionDef) and x.name=='native_delta')
    actual=ast.Module(body=current.body[:-1],type_ignores=[])
    require(ast.dump(original,include_attributes=False)==ast.dump(actual,include_attributes=False),
            'Targeted native operation differs from accepted V implementation')
    return dict(exact_V_operation_AST=True,accepted_file_sha256=digest(source))


def os_guard(root,label):
    """Require closed editors and no production lock; never touch stale U locks."""
    root=Path(root);output=root/('os-'+label+'.json')
    require(not output.exists(),'Fresh process observation required')
    shell=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
    command=r"""$ErrorActionPreference='Stop'; @(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(pcbnew|eeschema|kicad)\.exe$' } | Select-Object ProcessId,Name,CommandLine) | ConvertTo-Json -Depth 4 -Compress"""
    r=subprocess.run([str(shell),'-NoProfile','-Command',command],capture_output=True,text=True,timeout=30)
    require(r.returncode==0,'Process identification unavailable; STOP')
    editors=json.loads(r.stdout) if r.stdout.strip() else []
    if isinstance(editors,dict):editors=[editors]
    locks=[p.name for p in PRODUCTION.parent.iterdir() if p.name.endswith('.lck')]
    write_json(output,dict(editors=editors,production_locks=locks,rejected_U_locks_untouched=True))
    require(not editors and not locks,'KiCad editor or production lock present; owner closure required')


def runtime_hashes():
    return {str(p.resolve()):digest(p) for p in (Path(__file__),ENTRY)}


def guard(root,installed=False):
    root=Path(root);require(not (root/'STOP.json').exists(),'Stopped W execution; no retry or recovery')
    plan=read_json(root/'plan.json');require(plan['runtime']==runtime_hashes(),'W wrapper drift')
    operation_proof()
    require(digest(PRODUCTION)==(GOAL_SHA if installed else SOURCE_SHA),'Production source/saved identity drift')
    for name,h in plan['protected'].items():
        if Path(name).resolve()!=PRODUCTION.resolve():require(digest(name)==h,'Protected input drift: '+name)
    for name,h in plan['backup_hashes'].items():require(digest(name)==h,'Pre-change backup drift')
    return plan


def prepare(root):
    from .stencil_native_proof import guard as v_guard
    root=Path(root);require(not root.exists(),'Fresh W execution directory required');root.mkdir()
    os_guard(root,'entry')
    _,accepted=v_guard(VROOT/'candidate-v3');protected=dict(accepted['protected'])
    protected.update(read_json(VROOT/'final-result.json')['implementations'])
    for path in (VROOT/'final-result.json',VROOT/'independent-readback-v3/verify-result.json',
                 VROOT/'independent-readback-v3/gtp-comparison.json',
                 VROOT/'independent-readback-v3/paste-export/ups12v_v4-F_Paste.gtp',
                 Path('hardware/v4/evidence/phase4-21-production-adoption/production-erc.json')):
        protected[str(path.resolve())]=digest(path)
    for directory in ('software','hardware/v4/ups_v4/ups_v4.pretty','hardware/v4/ups_v4/ups_v4_external.pretty'):
        for path in Path(directory).rglob('*'):
            if path.is_file() and not any(x in path.parts for x in ('.pio','.git','__pycache__')):
                protected[str(path.resolve())]=digest(path)
    backup=prepare_scratch(PRODUCTION,TROOT/'current-source-baseline.json',root/'backup')
    copy_libraries(PRODUCTION.parent,backup)
    backup_hashes={str(p.resolve()):digest(p) for p in backup.rglob('*') if p.is_file()}
    write_json(root/'plan.json',dict(phase='4.24W',source_sha256=SOURCE_SHA,target_sha256=GOAL_SHA,
        protected=protected,backup_hashes=backup_hashes,runtime=runtime_hashes(),operation=operation_proof()))
    guard(root);print('Closed-editor entry, accepted identities and hash-verified backup PASS')


def worker(root,kind):
    root=Path(root);plan=guard(root,installed=kind=='verify');os_guard(root,kind+'-worker-entry')
    reference=root/'rehearsal'
    if kind=='verify':
        target=root/'production-readback/ups12v_v4.kicad_pcb';verify_context(target.parent)
    else:
        target=PRODUCTION.resolve() if kind=='production' else reference/'ups12v_v4.kicad_pcb'
    unlocked(target)
    api,board=api_load(target);require(api.GetBuildVersion()=='10.0.7','Accepted KiCad10.0.7 required')
    require(snapshot(board,api)==read_json(reference/'before-native.json'),'Original geometry/connectivity mismatch')
    require(layout_snapshot(board,api)==read_json(reference/'before-layout.json'),'Original layout/fill mismatch')
    units=read_json(reference/'before-symbol-units.json')
    require_units_equal(units,native_units(target.read_text(encoding='utf-8')))
    if kind=='verify':
        require(digest(target)==GOAL_SHA,'Independent production copy not exact accepted target')
        holes=Counter('NPTH' if pad.GetAttribute()==api.PAD_ATTRIB_NPTH else 'PTH'
            for fp in board.GetFootprints() for pad in fp.Pads()
            if max(pad.GetDrillSize().x,pad.GetDrillSize().y)>0)
        require(holes=={'PTH':41,'NPTH':12},'Physical hole classes changed')
        restore_paste(api,board,read_json(TROOT/'candidate-v3/transaction.json'))
        restored=root/'production-readback/restored-original-native.kicad_pcb';native_save(api,board,restored)
        require(digest(restored)==SOURCE_SHA,'Complete independent native inverse differs from original source')
        require_units_equal(units,native_units(restored.read_text(encoding='utf-8')))
        write_json(root/'production-readback/native-verification.json',dict(status='PASS',pads=473,vias=324,
            footprints=154,PTH=41,NPTH=12,all_original_native_bytes_preserved=True,
            inverse_sha256=digest(restored),target_sha256=digest(target),
            target_units={ref:units[ref] for ref in TARGETS},all154_units_exact=True))
    else:
        require(digest(target)==SOURCE_SHA,'Exact original source required')
        if kind=='production':
            require(read_json(root/'rehearsal-complete.json')['status']=='PASS','Complete identical rehearsal required')
            for name,h in read_json(root/'rehearsal-complete.json')['bindings'].items():
                require(digest(name)==h,'Rehearsal result drift')
        added,transaction=native_delta(api,board,reference)
        guard(root);os_guard(root,kind+'-before-save');unlocked(target)
        require(digest(target)==SOURCE_SHA,'Source changed before native save')
        write_json(root/(kind+'-save-attempt.json'),dict(target=str(target.resolve()),source_sha256=digest(target)))
        native_save(api,board,target)
        require_units_equal(units,native_units(target.read_text(encoding='utf-8')))
        require(digest(target)==GOAL_SHA,'Native saved target not exact accepted PCB; STOP')
        result=dict(status='PASS',sha256=digest(target),native_direct_object_save=True,
                    added_graphics=added,changed_pads=transaction['changed_pads'])
        write_json(root/(kind+'-saved.json'),result)
        if kind=='rehearsal':write_json(reference/'apply-result.json',result)
    guard(root,installed=kind in ('production','verify'))
    print('Exact native '+kind+' PASS',flush=True)


def run(root,kind):
    root=Path(root);guard(root,installed=kind=='verify')
    log=root/(kind+'.log');require(not log.exists(),'Already attempted; no retry')
    os_guard(root,kind+'-parent-entry')
    try:
        result=run_monitored(['C:/Program Files/KiCad/10.0/bin/python.exe','-B',ENTRY,
                             '_worker','--root',root,'--kind',kind],log)
    except (ToolError,OSError) as error:
        write_json(root/'STOP.json',dict(kind=kind,error=str(error),production_sha256=digest(PRODUCTION)));raise
    print(result['stdout'])


def certify_rehearsal(root):
    root=Path(root);guard(root)
    checked=root/'rehearsal-readback'
    require(read_json(checked/'verify-result.json')['status']=='PASS','Native rehearsal proof missing')
    c=read_json(checked/'checks-summary.json')
    require(c['drc']['errors']==c['drc']['unconnected']==c['drc']['parity']==c['erc']['errors']==0,'Rehearsal checks failed')
    require(read_json(checked/'gtp-comparison.json')['raw_xor_mm2']==0,'Rehearsal GTP differs')
    files=[root/'rehearsal-saved.json',root/'rehearsal/ups12v_v4.kicad_pcb']
    files.extend(p for p in checked.rglob('*') if p.is_file())
    write_json(root/'rehearsal-complete.json',dict(status='PASS',operation=operation_proof(),
        runtime=runtime_hashes(),bindings={str(p.resolve()):digest(p) for p in files}))
    print('Complete W wrapper rehearsal certified')


def production_checks(root):
    from .checks import parse_check
    root=Path(root);guard(root,installed=True)
    require(read_json(root/'production-saved.json')['sha256']==GOAL_SHA,'Native production save not established')
    if not (root/'production-readback').exists():
        source=read_json(root/'backup/context.json')['source_hashes'];source[PRODUCTION.name]=GOAL_SHA
        manifest=root/'installed-manifest.json';write_json(manifest,dict(hashes=source))
        out=prepare_scratch(PRODUCTION,manifest,root/'production-readback');copy_libraries(PRODUCTION.parent,out)
    run(root,'verify')
    out=root/'production-readback';board=out/PRODUCTION.name
    cli='C:/Program Files/KiCad/10.0/bin/kicad-cli.exe';summaries={}
    for kind in ('drc','erc'):
        report=out/(kind+'.json');require(not report.exists(),'Fresh report required')
        command=([cli,'pcb','drc','--format','json','--all-track-errors','--schematic-parity','--output',report,board]
            if kind=='drc' else [cli,'sch','erc','--format','json','--output',report,board.with_suffix('.kicad_sch')])
        run_monitored(command,out/(kind+'.log'));summaries[kind]=parse_check(read_json(report),kind)
        require(summaries[kind]['errors']==0,'Production '+kind+' errors')
    require(summaries['drc']['unconnected']==summaries['drc']['parity']==0,'Production opens/parity findings')
    key=lambda x:json.dumps(x,sort_keys=True)
    actual=read_json(out/'drc.json');expected=read_json(TROOT/'native-checks/candidate-drc.json')
    require(Counter(map(key,actual['violations']))==Counter(map(key,expected['violations'])) and
            actual['ignored_checks']==expected['ignored_checks'],'Production warning identity or ignored-check mismatch')
    erows=lambda p:Counter(key(v) for s in p['sheets'] for v in s['violations'])
    require(erows(read_json(out/'erc.json'))==erows(read_json('hardware/v4/evidence/phase4-21-production-adoption/production-erc.json')),
            'Accepted ERC warning identity mismatch')
    export=out/'paste-export';export.mkdir()
    run_monitored([cli,'pcb','export','gerbers','--layers','F.Paste','--precision','6','--output',export,board],export/'export.log')
    import sys
    sys.path.insert(0,str(Path('hardware/v4/evidence/phase4-24-owner-gerber-review/deps').resolve()))
    from gerbonara import GerberFile
    from .gerber_review import compose,difference
    from .stencil_review import parts
    files=list(export.glob('*.gtp'));require(len(files)==1,'Fresh focused production GTP missing/ambiguous')
    actual=compose(GerberFile.open(files[0]));cam=[]
    for ref in (TROOT/'candidate-v3/paste-export/ups12v_v4-F_Paste.gtp',VROOT/'independent-readback-v3/paste-export/ups12v_v4-F_Paste.gtp'):
        record=difference(compose(GerberFile.open(ref)),actual,.000005)
        record.update(reference=str(ref),reference_sha256=digest(ref),actual_sha256=digest(files[0]),physical_openings=len(parts(actual)))
        require(record['raw_xor_mm2']==0 and record['physical_openings']==411,'Production physical GTP mismatch')
        cam.append(record)
    require(digest(board)==GOAL_SHA,'Checks changed saved production copy')
    guard(root,installed=True)
    result=dict(status='PASS_PRODUCTION_ADOPTED_OWNER_REEXPORT_STOP',source_sha256=SOURCE_SHA,
        production_sha256=digest(PRODUCTION),checks=summaries,all_warning_identities_exact=True,
        native=read_json(out/'native-verification.json'),GTP=cam,
        owner_zip_unchanged=True,reexport_ready=True)
    write_json(out/'gtp-comparison.json',cam);write_json(root/'final-result.json',result)
    print(json.dumps(dict(status=result['status'],production_sha256=digest(PRODUCTION),DRC=summaries['drc']['errors'],
        ERC=summaries['erc']['errors'],physical_openings=411)))


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    for name in ('prepare','rehearsal','production','certify-rehearsal','checks'):
        q=sub.add_parser(name);q.add_argument('--root',type=Path,required=True)
    q=sub.add_parser('_worker');q.add_argument('--root',type=Path,required=True);q.add_argument('--kind',choices=['rehearsal','production','verify'],required=True)
    a=p.parse_args()
    if a.action=='prepare':prepare(a.root)
    elif a.action=='_worker':worker(a.root,a.kind)
    elif a.action=='certify-rehearsal':certify_rehearsal(a.root)
    elif a.action=='checks':production_checks(a.root)
    else:run(a.root,a.action)


if __name__=='__main__':main()
