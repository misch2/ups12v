"""Phase4.18 exact, rehearsal-gated owning-editor adoption of accepted F5.

No serialized CAD writes or activity on import. Historical installers stay bound
to their original checkpoints; only reusable capture/object helpers are shared.
"""
from pathlib import Path
from collections import Counter
import argparse
import copy
import json
import sys

from .safety import (require, read_json, write_json, digest, verify_hashes,
                     prepare_scratch, run_monitored, ToolError)
from .migration import delta, verify_refilled_capture
from .owner_migration import native_capture, build_transaction as build_copper
from .f5_scratch import BASELINE, F5_REFS, NETS

GOAL = '8221929563ed10653f84933549a6fdf99d69071364c12e83860a22f55326b9e6'
COUNTS = dict(tracks=1170, vias=324, footprints=154, pads=473)


def implementations():
    names=['f5_migration.py','f5_migration_proof.py','owner_migration.py','migration.py',
           'ipc_install.py','ipc_u3.py','safety.py','f5_scratch.py','f5_review.py',
           'geometry.py','native.py','cli.py']
    return {str(Path(__file__).with_name(n).resolve()):digest(Path(__file__).with_name(n)) for n in names}


def reconcile(before, goal, p):
    ops={s:delta(before[s],goal[s]) for s in ['tracks','vias','footprints','pads']}
    require(ops==p['operations'],'Complete native UUID/preimage/postimage whitelist differs')
    require(not any(ops[s]['removed'] or ops[s]['modified'] for s in ['tracks','vias']),
            'Original F0 copper cannot change')
    require(len(ops['tracks']['added'])==117 and len(ops['vias']['added'])==30,'Wrong additions')
    require(not any(ops[s]['added'] or ops[s]['removed'] for s in ['footprints','pads']),
            'Footprint/pad identities changed')
    moved=ops['footprints']['modified']
    require(len(moved)==18 and {v['after']['ref'] for v in moved.values()}==F5_REFS-{'J8'},
            'Only eighteen exact F5 footprints may move')
    require({s:len(goal[s]) for s in COUNTS}==COUNTS,'Target counts differ')
    for row in moved.values():
        a,b=row['before'],row['after']; ref=a['ref']
        require([*b['position'],b['angle']]==p['accepted_routing_plan']['placements'][ref],
                'Placement differs from reviewed plan')
        require({k:v for k,v in a.items() if k not in ['position','angle']}==
                {k:v for k,v in b.items() if k not in ['position','angle']},'Footprint metadata differs')
    from .f5_scratch import retained
    expected={u:v for s in ['tracks','vias'] for u,v in ops[s]['added'].items()}
    retained(before,goal,p['accepted_routing_plan'],expected)
    arcs=lambda g:{u:v for u,v in g['tracks'].items() if v.get('geometry')=='arc'}
    require(len(arcs(before))==8 and arcs(before)==arcs(goal),'Native arcs changed')
    require(all(v['net'] in NETS for s in ['tracks','vias'] for v in ops[s]['added'].values()),
            'Unapproved power-domain connection')
    return dict(complete_delta_equal=True,eight_native_arcs_equal=True,
                counts={s:{k:len(v) for k,v in d.items()} for s,d in ops.items()})


def bindings(plan_path, installed=False):
    p=read_json(plan_path); production=Path(p['production_board']); source=Path(p['accepted_F5_board'])
    require(p['production_hashes'][production.name]==BASELINE and p['F5_hashes'][source.name]==GOAL,
            'Unapproved source identities')
    hashes=p['production_hashes'].copy()
    if installed:hashes.pop(production.name)
    verify_hashes(production.parent,hashes);verify_hashes(source.parent,p['F5_hashes'])
    for path,wanted in p['bound_artifacts'].items():require(digest(path)==wanted,'Bound artifact drift: '+path)
    return p


def make_plan(entry, goal, output):
    entry,goal,output=map(Path,[entry,goal,output])
    proof_path=Path('hardware/v4/evidence/phase4-17-review/FINAL_PROOF.json')
    proof=read_json(proof_path)
    before,target=[read_json(d/'snapshot.json') for d in [entry,goal]]
    routing=read_json(Path(proof['candidate']).parent/'plan.json')
    paths=[proof_path,Path(proof['accepted_manifest']),entry/'snapshot.json',entry/'context.json',
           entry/'routed-diagnostics.json',entry/'native-audit.json',entry/'pad-partition.json',
           goal/'snapshot.json',goal/'routed-diagnostics.json',goal/'native-audit.json',
           goal/'pad-partition.json',goal/'routing-context.json',goal/'layout.json',goal/'polygon-artwork.json']
    bound=proof['bound_artifacts']|{str(x.resolve()):digest(x) for x in paths}
    p=dict(schema_version=1,phase='4.18',authorization='Owner accepted Phase4.17 and authorized exact production migration',
        production_board=proof['source'],accepted_F5_board=proof['candidate'],
        accepted_production_manifest=proof['accepted_manifest'],production_hashes=proof['production_hashes'],
        F5_hashes=proof['production_hashes']|{'ups12v_v4.kicad_pcb':GOAL},
        entry=str(entry.resolve()),goal=str(goal.resolve()),accepted_routing_plan=routing,
        operations={s:delta(before[s],target[s]) for s in ['tracks','vias','footprints','pads']},
        bound_artifacts=bound)
    reconcile(before,target,p);write_json(output,p);bindings(output)
    print('Exact F5 plan:18whole footprints/117tracks/30vias; all original copper and8arcs retained')


def prepare(plan_path, output, candidate_proof=None):
    plan_path,output=map(Path,[plan_path,output]);p=bindings(plan_path)
    entry,goal=Path(p['entry']),Path(p['goal'])
    reconciliation=reconcile(read_json(entry/'snapshot.json'),read_json(goal/'snapshot.json'),p)
    if candidate_proof:
        q=read_json(candidate_proof)
        require(q['verdict']=='PASS_COMPLETE_CANDIDATE' and q['plan_hash']==digest(plan_path)
                and q['implementations']==implementations(),'Complete identical rehearsal required')
        for path,wanted in q['candidate_sources'].items():require(digest(path)==wanted,'Rehearsal source drift')
        require(not output.exists(),'Fresh production evidence directory required');output.mkdir(parents=True)
        target=Path(p['production_board'])
    else:
        prepare_scratch(p['production_board'],p['accepted_production_manifest'],output)
        target=output.resolve()/Path(p['production_board']).name
    raw=read_json(entry/'routed-diagnostics.json')['items'];target_raw=read_json(goal/'routed-diagnostics.json')['items']
    templates=via_templates(raw,target_raw,p['operations']['vias']['added'])
    c=dict(phase='4.18',production=bool(candidate_proof),target=str(target.resolve()),
           plan=str(plan_path.resolve()),plan_hash=digest(plan_path),implementations=implementations(),via_templates=templates)
    if candidate_proof:c.update(candidate_proof=str(Path(candidate_proof).resolve()),candidate_proof_hash=digest(candidate_proof))
    write_json(output/'f5-migration-context.json',c);write_json(output/'reconciliation.json',reconciliation)
    print('Prepared '+('production' if candidate_proof else 'isolated owning-editor rehearsal'))


def via_templates(raw,target_raw,added):
    """Match the full native NORMAL circular through-stack, resize only copper."""
    def signature(v):
        r={k:x for k,x in v.items() if k not in ['uuid','net','position','position_nm','copper_widths']}
        r['padstack_layers']={l:{k:x for k,x in a.items() if k not in ['width_nm','size_nm']}
                              for l,a in r['padstack_layers'].items()}
        return r
    result={}
    for uid in added:
        v=target_raw[uid]
        require(v['via_type']==4 and v['padstack_mode']==0 and v['drill_shape']==1
                and v['layer_pair']==['F.Cu','B.Cu'] and len(set(v['copper_widths'].values()))==1,
                'Only reviewed uniform circular through vias supported')
        matches=sorted(u for u,w in raw.items() if w['kind']=='via' and signature(w)==signature(v))
        require(matches,'Exact non-copper native via padstack missing: '+uid);result[uid]=matches[0]
    return result


def check_context(root, installed=False):
    root=Path(root);require(not (root/'STOP.json').exists(),'Migration stopped; no IPC or recovery')
    c=read_json(root/'f5-migration-context.json')
    require(digest(c['plan'])==c['plan_hash'] and implementations()==c['implementations'],'Implementation/plan drift')
    p=bindings(c['plan'],installed)
    if c['production']:
        require(digest(c['candidate_proof'])==c['candidate_proof_hash'],'Rehearsal proof drift')
        q=read_json(c['candidate_proof'])
        require(q['verdict']=='PASS_COMPLETE_CANDIDATE' and q['implementations']==c['implementations']
                and q['plan_hash']==c['plan_hash'],'Identical complete rehearsal required')
        for path,wanted in q['candidate_sources'].items():require(digest(path)==wanted,'Rehearsal source drift')
    return c,p


def prepare_footprints(originals,p):
    """Proven integer quarter-turn transform, preserving complete local models."""
    from kipy.board_types import FootprintInstance,Footprint3DModel,Field
    from kipy.geometry import Vector2,Angle
    goal=read_json(Path(p['goal'])/'snapshot.json'); placements=p['accepted_routing_plan']['placements']
    expected={f['ref']:f for f in goal['footprints'].values()};updates=[]
    def identity(item):
        if hasattr(item.proto,'id'):return item.proto.DESCRIPTOR.full_name,item.proto.id.SerializeToString()
        require(isinstance(item,Footprint3DModel),'Unsupported footprint child')
        return item.proto.DESCRIPTOR.full_name,item.proto.SerializeToString()
    def quarter(vector,angle,center):
        turns=round(angle.degrees/90)
        require(abs(angle.degrees-turns*90)<1e-10,'Only exact quarter turns authorized')
        dx,dy=vector.x-center.x,vector.y-center.y
        for _ in range(turns%4):dx,dy=dy,-dx
        vector.x,vector.y=center.x+dx,center.y+dy
        return vector
    for original in originals:
        ref=original.reference_field.text.value
        if ref not in placements:continue
        fp=FootprintInstance(original.proto);x,y,a=placements[ref]
        identities=Counter(map(identity,fp.definition.items))
        models=[(i,item) for i,item in enumerate(fp.definition.items) if isinstance(item,Footprint3DModel)]
        old_rotate=Vector2.rotate
        try:
            Vector2.rotate=quarter;fp.orientation=Angle.from_degrees(a)
        finally:Vector2.rotate=old_rotate
        items=list(fp.definition.items)
        for i,item in models:items.insert(i,item)
        fp.definition.items=items;fp.position=Vector2.from_xy(round(x*1e6),round(y*1e6))
        for pad in fp.definition.pads:pad.padstack.angle=Angle.from_degrees(pad.padstack.angle.degrees%360)
        for item in fp.texts_and_fields:
            text=item.text if isinstance(item,Field) else item;text.attributes.angle%=360
        require(identities==Counter(map(identity,fp.definition.items)),'Footprint child identities changed: '+ref)
        require([fp.position.x/1e6,fp.position.y/1e6]==expected[ref]['position']
                and fp.orientation.degrees==expected[ref]['angle'],'Footprint target differs: '+ref)
        for pad in fp.definition.pads:
            target=goal['pads'][pad.id.value]
            require([pad.position.x/1e6,pad.position.y/1e6]==target['position'] and pad.net.name==target['net'],
                    'Pad position/net target differs: '+ref+'.'+target['pin'])
        updates.append(fp)
    require(len(updates)==18,'Exactly18F5 footprint updates required')
    return updates


def build_transaction(board,before,p,templates):
    from google.protobuf.json_format import MessageToDict
    from kipy.board_types import Via,Net
    from kipy.geometry import Vector2
    cp=dict(operations={s:dict(create=p['operations'][s]['added'] if s=='tracks' else {},
                             remove_with_preimage={},update_with_preimage={}) for s in ['tracks','vias']})
    cp['operations']['footprints']=dict(translate_whole_instance_with_preimage={})
    updates,creates,removes,expected=build_copper(board,before,cp,templates)
    require(not updates and not removes and len(creates)==117,'Exact add-only track transaction required')
    originals={v.id.value:v for v in board.get_vias()}
    for uid,row in p['operations']['vias']['added'].items():
        item=Via(originals[templates[uid]].proto)
        item.id.value=uid;item.position=Vector2.from_xy(*(round(v*1e6) for v in row['position']))
        require(len(set(row['copper_widths'].values()))==1,'Uniform native padstack required')
        item.diameter=round(row['copper_widths']['F.Cu']*1e6)
        item.drill_diameter=round(row['drill']*1e6);item.net=Net(name=row['net'])
        creates.append(item);expected['vias'][uid]=MessageToDict(item.proto)
    updates=prepare_footprints(board.get_footprints(),p)
    for fp in updates:
        expected['footprints'][fp.id.value]=MessageToDict(fp.proto)
        for pad in fp.definition.pads:expected['pads'][pad.id.value]=MessageToDict(pad.proto)
    return updates,creates,expected


def worker(root,action,socket):
    from .ipc_install import capture
    root=Path(root);c,p=check_context(root,installed=action=='verify-saved');target=Path(c['target'])
    require((target==Path(p['production_board']))==c['production'],'Target scope mismatch')
    if not c['production']:require(target.parent==root.resolve(),'Rehearsal must be isolated')
    for name,wanted in p['production_hashes'].items():
        if name!=target.name:require(digest(target.parent/name)==wanted,'Target companion drift')
    sys.path.insert(0,str(Path(p['production_board']).parent/'.konnect/native-ipc'))
    from kipy import KiCad
    from kipy.proto.common.types.base_types_pb2 import DocumentType
    k=KiCad(socket_path=socket,client_name='UPS V4 Phase4.18 exact accepted F5 adoption')
    require(k.get_version().major==10,'KiCad10 required')
    require(len(k.get_open_documents(DocumentType.DOCTYPE_PCB))==1,'Ambiguous editor documents')
    b=k.get_board()
    require(b.name==target.name and Path(b.document.project.path).resolve()==target.parent,'Wrong owning editor')
    before=capture(b)
    if action=='verify-saved':
        require(native_capture(before)==native_capture(read_json(root/'live-saved.json')),'Saved/live drift')
        require(digest(target)==read_json(root/'ipc-saved.json')['board_sha256'],'Saved PCB drift')
        write_json(root/'final-live-readback.json',dict(saved_live_exact=True,board_sha256=digest(target)))
        print('Final owning-editor saved/live readback PASS');return
    require(digest(target)==BASELINE,'Exact accepted entry PCB required')
    baseline=read_json(p['accepted_production_manifest'])
    for s in before:require(native_capture(before[s])==native_capture(baseline[s]),'Unsaved/live entry differs: '+s)
    if action=='preflight':
        require(not (root/'ipc-preflight.json').exists(),'Fresh preflight required')
        write_json(root/'ipc-before.json',before)
        write_json(root/'ipc-preflight.json',dict(saved_live_exact=True,version=str(k.get_version()),target=str(target)))
        print('Exact saved/live entry PASS');return
    require(action=='apply' and (root/'ipc-preflight.json').exists() and not (root/'commit.json').exists(),
            'Fresh, preflighted, unattempted transaction required')
    require(native_capture(before)==native_capture(read_json(root/'ipc-before.json')),'Entry changed since preflight')
    updates,creates,expected=build_transaction(b,before,p,c['via_templates'])
    write_json(root/'ipc-expected.json',expected)
    write_json(root/'prepared-transaction.json',dict(update=[x.id.value for x in updates],create=[x.id.value for x in creates],remove=[]))
    check_context(root)
    commit=b.begin_commit();write_json(root/'commit.json',dict(value=commit.id.value))
    actual_updates=b.update_items(updates);actual_creates=b.create_items(creates)
    from google.protobuf.json_format import MessageToDict
    returned=[MessageToDict(x.proto) for x in actual_updates+actual_creates]
    write_json(root/'returned-items.json',returned)
    require({x.id.value for x in actual_updates}=={x.id.value for x in updates}
            and {x.id.value for x in actual_creates}=={x.id.value for x in creates},'Returned UUID mismatch')
    wanted={x.id.value:MessageToDict(x.proto) for x in updates+creates}
    require(native_capture({x['id']['value']:x for x in returned})==native_capture(wanted),'Returned payload mismatch')
    b.push_commit(commit,'Phase4.18 exact accepted F5 placement and routing adoption')
    after=capture(b);write_json(root/'ipc-after.json',after)
    different=[s for s in expected if native_capture(expected[s])!=native_capture(after[s])]
    write_json(root/'ipc-preservation.json',dict(exact_equal=not different,different_sections=different))
    require(not different,'Post-commit native payload mismatch')
    b.refill_zones();filled=capture(b);write_json(root/'live-refilled.json',filled)
    verify_refilled_capture(after,filled,read_json(Path(p['goal'])/'layout.json'))
    b.save();saved=capture(b);require(native_capture(saved)==native_capture(filled),'Save changed live payload')
    write_json(root/'live-saved.json',saved)
    write_json(root/'ipc-saved.json',dict(board_sha256=digest(target),saved_through_editor=True))
    installed=copy.deepcopy(saved)
    installed['hashes']={target.with_suffix(ext).name:digest(target.with_suffix(ext))
                         for ext in ['.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_dru']}
    write_json(root/'installed-manifest.json',installed);check_context(root,installed=True)
    print('Exact F5 transaction/readback/refill/owning-editor save PASS')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    q=sub.add_parser('plan')
    for name in ['entry','goal','output']:q.add_argument('--'+name,required=True,type=Path)
    q=sub.add_parser('prepare')
    for name in ['plan','output']:q.add_argument('--'+name,required=True,type=Path)
    q.add_argument('--candidate-proof',type=Path)
    for name in ['preflight','apply','verify-saved','_worker-preflight','_worker-apply','_worker-verify-saved']:
        q=sub.add_parser(name);q.add_argument('--root',required=True,type=Path);q.add_argument('--socket',required=True)
    a=parser.parse_args(argv)
    try:
        if a.action=='plan':make_plan(a.entry,a.goal,a.output)
        elif a.action=='prepare':prepare(a.plan,a.output,a.candidate_proof)
        elif a.action.startswith('_worker-'):worker(a.root,a.action[8:],a.socket)
        else:
            require(not (a.root/'STOP.json').exists(),'Migration stopped; no retry')
            log=a.root/('ipc-'+a.action+'.log');require(not log.exists(),'Action already attempted; no retry')
            try:run_monitored([sys.executable,'-B','-m','v4kicad.f5_migration','_worker-'+a.action,'--root',a.root,'--socket',a.socket],log)
            except (ToolError,OSError) as e:
                write_json(a.root/'STOP.json',dict(action=a.action,error=str(e)));raise
            print('Monitored '+a.action+' complete')
        return 0
    except (ToolError,OSError,ValueError,KeyError,TypeError) as e:
        print('STOP: '+str(e),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
