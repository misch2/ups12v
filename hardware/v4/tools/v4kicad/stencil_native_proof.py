"""Phase4.24V targeted pcbnew proof. Scratch-only; no production install action."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil

from .safety import (digest,read_json,write_json,require,prepare_scratch,
                     verify_context,run_monitored,unlocked,ToolError)
from .stencil_scratch import SOURCE_SHA,TARGETS,layer_set,native_save,restore_paste

BASE=Path('hardware/v4')
PRODUCTION=BASE/'ups_v4/ups12v_v4.kicad_pcb'
TROOT=BASE/'evidence/phase4-24t-stencil-scratch'
UROOT=BASE/'evidence/phase4-24u-production-paste-adoption'
GOAL=TROOT/'candidate-v3/ups12v_v4.kicad_pcb'
GOAL_SHA='d0a8c95a1b8cfbeff1f4f7fa4a95abf297a86d9c95551ed5b7b3050f42b8ac2b'
TOKEN=re.compile(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]')


def native_units(text):
    """Read-only exact native unit blocks; never rewrite or normalize CAD text.

    The installed IPC omits these properties. Read native-authored serialization
    solely for explicit metadata evidence, in addition to full native byte proofs.
    """
    stack=[];result={};fp=None
    for token in TOKEN.finditer(text):
        value=token.group()
        if value=='(':
            stack.append(dict(start=token.start(),atoms=[]));continue
        require(stack,'Unbalanced native serialization')
        if value!=')':
            stack[-1]['atoms'].append(value);continue
        node=stack.pop();atoms=node['atoms'];kind=atoms[0] if atoms else ''
        if len(stack)==1 and kind=='footprint':
            require(fp is not None and fp.get('ref'),'Footprint reference missing')
            require(fp['ref'] not in result,'Duplicate footprint reference')
            result[fp['ref']]={k:v for k,v in fp.items() if k!='ref'};fp=None
        elif len(stack)==2 and stack[-1]['atoms'][:1]==['footprint']:
            if fp is None:fp=dict(uuid=None,units=None)
            if kind=='property' and len(atoms)>2 and atoms[1]=='"Reference"':
                fp['ref']=json.loads(atoms[2])
            elif kind=='uuid':fp['uuid']=json.loads(atoms[1])
            elif kind=='units':
                require(fp['units'] is None,'Duplicate units property')
                fp['units']=text[node['start']:token.end()]
    require(not stack and result,'Incomplete native metadata coverage')
    return result


def require_units_equal(source,actual):
    require(source==actual,'Native symbol-unit/pin metadata or footprint identity changed')


def scratch_target(target):
    target=Path(target).resolve();production=PRODUCTION.resolve()
    require(target!=production and production.parent not in target.parents,
            'No production action exists in this scratch proof')
    require(UROOT.resolve() not in target.parents,'Rejected Phase4.24U context is immutable')
    unlocked(target)


def implementations():
    names=['stencil_native_proof.py','stencil_scratch.py','safety.py','native.py','cli.py','geometry.py','checks.py']
    return {str(Path(__file__).with_name(n).resolve()):digest(Path(__file__).with_name(n)) for n in names}


def guard(root):
    root=Path(root);require(not (root/'STOP.json').exists(),'Stopped proof context; no retry')
    c=verify_context(root);scratch_target(c['board']);p=read_json(root/'native-paste-request.json')
    require(digest(GOAL)==GOAL_SHA and digest(PRODUCTION)==SOURCE_SHA,'Accepted source/goal drift')
    require(implementations()==p['implementations'],'Proof implementation drift')
    for path,h in p['protected'].items():require(digest(path)==h,'Protected source/evidence drift: '+path)
    return c,p


def copy_libraries(source,output):
    for name in ('fp-lib-table','sym-lib-table'):
        if (source/name).exists():shutil.copy2(source/name,output/name)
    for name in ('ups_v4.pretty','ups_v4_external.pretty'):
        shutil.copytree(source/name,output/name)
    for path in source.glob('*.kicad_sym'):shutil.copy2(path,output/path.name)


def prepare(output):
    require(digest(PRODUCTION)==SOURCE_SHA and digest(GOAL)==GOAL_SHA,'Source/accepted candidate mismatch')
    prior=read_json(UROOT/'inputs-before.json')
    protected={**prior['protected'],**prior['accepted_artifacts']}
    for path,h in protected.items():require(digest(path)==h,'Protected input drift')
    for path in (GOAL,TROOT/'candidate-v3/transaction.json',TROOT/'native-checks/candidate-drc.json',
                 TROOT/'native-checks/baseline-drc.json',TROOT/'candidate-v3/paste-export/ups12v_v4-F_Paste.gtp',
                 TROOT/'cam-verification/physical-aperture-delta.json',UROOT/'STOP.json',
                 UROOT/'owning-editor-rehearsal/ups12v_v4.kicad_pcb',
                 UROOT/'owning-editor-rehearsal/STOP.json'):
        protected[str(path.resolve())]=digest(path)
    root=prepare_scratch(PRODUCTION,TROOT/'current-source-baseline.json',output)
    copy_libraries(PRODUCTION.parent,root)
    write_json(root/'native-paste-request.json',dict(scope='4.24V scratch only',protected=protected,
               implementations=implementations()))
    guard(root);print('Fresh production-derived native proof prepared')


def worker(action,root):
    from .native import api_load
    from .geometry import snapshot,layout_snapshot
    root=Path(root);c,p=guard(root);path=Path(c['board'])
    api,board=api_load(path)
    require(api.GetBuildVersion()=='10.0.7','Verified KiCad10.0.7 required')
    for name in ('Clone','SetParent'):
        require(hasattr(api.PCB_SHAPE,name),'Targeted native API missing: '+name)
    require(hasattr(api,'Cast_to_BOARD_ITEM') and hasattr(api,'Cast_to_PCB_SHAPE'),
            'Native EDA_ITEM/BOARD_ITEM/PCB_SHAPE cast API missing')
    if action=='snapshot':
        require(digest(path)==SOURCE_SHA,'Fresh source read-only snapshot required')
        write_json(root/'before-native.json',snapshot(board,api))
        write_json(root/'before-layout.json',layout_snapshot(board,api))
        units=native_units(path.read_text(encoding='utf-8'))
        write_json(root/'before-symbol-units.json',units)
        native_save(api,board,root/'source-native-save.kicad_pcb')
        require(digest(root/'source-native-save.kicad_pcb')==SOURCE_SHA,'Native source save not byte-identical')
        require_units_equal(units,native_units((root/'source-native-save.kicad_pcb').read_text(encoding='utf-8')))
        write_json(root/'snapshot-result.json',dict(source_sha256=SOURCE_SHA,complete_native_source_equal=True,
            footprints=len(units),native_api='pcbnew10.0.7 Clone/SetParent/FOOTPRINT.Add/PAD.SetLayerSet'))
    elif action=='apply':
        require((root/'snapshot-result.json').exists() and digest(path)==SOURCE_SHA,'Fresh preflighted copy required')
        require(snapshot(board,api)==read_json(root/'before-native.json'),'Fresh native source drift')
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
            # Clone returns EDA_ITEM. The installed SWIG shape cast requires
            # BOARD_ITEM, so use both supported casts in their declared order.
            shape=api.Cast_to_PCB_SHAPE(api.Cast_to_BOARD_ITEM(g.Clone()))
            require(shape is not None and shape.m_Uuid.AsString()==uid,'Native clone changed graphic identity')
            shape.SetParent(fp);fp.Add(shape);added.append(uid)
        require(snapshot(board,api)==read_json(root/'before-native.json'),'Native geometry/connectivity changed')
        require(layout_snapshot(board,api)==read_json(root/'before-layout.json'),'Native layout/fills changed')
        native_save(api,board,path)
        require_units_equal(read_json(root/'before-symbol-units.json'),native_units(path.read_text(encoding='utf-8')))
        require(digest(path)==GOAL_SHA,'Native result is not the exact accepted complete PCB')
        write_json(root/'apply-result.json',dict(status='PASS_SCRATCH_ONLY',sha256=digest(path),
            exact_accepted_complete_native_bytes=True,added_graphics=added,changed_pads=transaction['changed_pads']))
    elif action=='verify':
        require(digest(path)==GOAL_SHA,'Saved scratch is not exact accepted candidate')
        before=read_json(p['reference_root']+'/before-native.json')
        require(snapshot(board,api)==before,'Independent original native geometry/connectivity mismatch')
        require(layout_snapshot(board,api)==read_json(p['reference_root']+'/before-layout.json'),
                'Independent native layout/fill mismatch')
        units=native_units(path.read_text(encoding='utf-8'))
        require_units_equal(read_json(p['reference_root']+'/before-symbol-units.json'),units)
        write_json(root/'after-symbol-units.json',units)
        # Inventory before consuming the board for the inverse proof. Native
        # Remove() transfers SWIG ownership; do not traverse it after reversal.
        holes=Counter('NPTH' if pad.GetAttribute()==api.PAD_ATTRIB_NPTH else 'PTH'
                      for fp in board.GetFootprints() for pad in fp.Pads()
                      if max(pad.GetDrillSize().x,pad.GetDrillSize().y)>0)
        require(holes=={'PTH':41,'NPTH':12},'Component hole class mismatch')
        restore_paste(api,board,read_json(TROOT/'candidate-v3/transaction.json'))
        restored=root/'restored-original-native.kicad_pcb';native_save(api,board,restored)
        require(digest(restored)==SOURCE_SHA,'Complete native inverse is not the original production source')
        require_units_equal(units,native_units(restored.read_text(encoding='utf-8')))
        write_json(root/'verify-result.json',dict(status='PASS',candidate_sha256=GOAL_SHA,
            restored_original_sha256=digest(restored),all_original_native_bytes_preserved=True,
            all_symbol_unit_blocks_equal=True,target_symbol_units={ref:units[ref] for ref in TARGETS},
            pads=len(before['pads']),vias=len(before['vias']),footprints=len(before['footprints']),holes=dict(holes)))
    else:raise ToolError('Unknown native proof action')
    guard(root);print('Native '+action+' PASS; scratch only',flush=True)


def run(root,action):
    root=Path(root);guard(root);log=root/(action+'.log')
    require(not log.exists(),'Fresh monitored action required; no automatic retry')
    entry=Path(__file__).resolve().parents[1]/'kicad_v4.py'
    try:
        result=run_monitored(['C:/Program Files/KiCad/10.0/bin/python.exe','-B',entry,'_worker',
                              '--scratch-dir',root,'--action','stencil-native-'+action],log)
    except (ToolError,OSError) as error:
        write_json(root/'STOP.json',dict(action=action,error=str(error)));raise
    print(result['stdout'])


def independent(root,output):
    root=Path(root);c,p=guard(root)
    require(read_json(root/'apply-result.json')['sha256']==digest(c['board'])==GOAL_SHA,'Complete saved candidate required')
    manifest=root/'candidate-manifest.json';hashes=dict(c['source_hashes']);hashes[Path(c['board']).name]=GOAL_SHA
    write_json(manifest,dict(hashes=hashes))
    output=prepare_scratch(c['board'],manifest,output);copy_libraries(Path(c['board']).parent,output)
    request=dict(p,reference_root=str(root.resolve()))
    write_json(output/'native-paste-request.json',request)
    run(output,'verify')


def checks(root):
    from .checks import parse_check
    root=Path(root);c,p=guard(root);board=Path(c['board'])
    require((root/'verify-result.json').exists(),'Independent full native preservation required before checks')
    cli='C:/Program Files/KiCad/10.0/bin/kicad-cli.exe';summaries={}
    for kind in ('drc','erc'):
        report=root/(kind+'.json');require(not report.exists(),'Fresh native report required')
        command=([cli,'pcb','drc','--format','json','--all-track-errors','--schematic-parity','--output',report,board]
                 if kind=='drc' else [cli,'sch','erc','--format','json','--output',report,board.with_suffix('.kicad_sch')])
        run_monitored(command,root/(kind+'.log'))
        summaries[kind]=parse_check(read_json(report),kind)
        require(summaries[kind]['errors']==0,'Native '+kind+' errors')
    require(summaries['drc']['unconnected']==summaries['drc']['parity']==0,'Unconnected/parity errors')
    actual=read_json(root/'drc.json');gold=read_json(TROOT/'native-checks/candidate-drc.json')
    key=lambda v:json.dumps(v,sort_keys=True)
    require(Counter(map(key,actual['violations']))==Counter(map(key,gold['violations'])) and
            actual['ignored_checks']==gold['ignored_checks'],'Warning identity/cause or ignored-check drift')
    write_json(root/'checks-summary.json',dict(summaries,exact_accepted_DRC_warning_identities=True,
        added_warning_evidence=read_json(TROOT/'native-checks/warning-delta.json')))
    export=root/'paste-export';export.mkdir()
    run_monitored([cli,'pcb','export','gerbers','--layers','F.Paste','--precision','6','--output',export,board],export/'export.log')
    import sys
    sys.path.insert(0,str((BASE/'evidence/phase4-24-owner-gerber-review/deps').resolve()))
    from gerbonara import GerberFile
    from .gerber_review import compose,difference
    from .stencil_review import parts
    files=list(export.glob('*.gtp'));require(len(files)==1,'Fresh focused GTP missing/ambiguous')
    expected=TROOT/'candidate-v3/paste-export/ups12v_v4-F_Paste.gtp'
    a,b=compose(GerberFile.open(expected)),compose(GerberFile.open(files[0]))
    cam=difference(a,b,.000005)
    cam.update(physical_openings=len(parts(b)),expected_sha256=digest(expected),actual_sha256=digest(files[0]),
               byte_identical=digest(expected)==digest(files[0]))
    write_json(root/'gtp-comparison.json',cam)
    require(cam['pass_geometry'] and cam['physical_openings']==411,'Actual GTP not accepted 411-opening geometry')
    require(digest(board)==GOAL_SHA,'Read-only native checks changed candidate')
    guard(root);print(json.dumps(dict(status='PASS',checks=summaries,GTP_physical_openings=411,
                                      exact_native_candidate=True,production_unchanged=True)))


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('prepare');q.add_argument('--output',type=Path,required=True)
    q=sub.add_parser('run');q.add_argument('--root',type=Path,required=True);q.add_argument('--operation',choices=['snapshot','apply','verify'],required=True)
    q=sub.add_parser('independent');q.add_argument('--root',type=Path,required=True);q.add_argument('--output',type=Path,required=True)
    q=sub.add_parser('checks');q.add_argument('--root',type=Path,required=True)
    a=p.parse_args()
    if a.action=='prepare':prepare(a.output)
    elif a.action=='run':run(a.root,a.operation)
    elif a.action=='independent':independent(a.root,a.output)
    else:checks(a.root)


if __name__=='__main__':main()
