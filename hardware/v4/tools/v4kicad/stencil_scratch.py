"""Four-land paste-only native scratch transaction; never a production installer."""
import argparse
from pathlib import Path
import shutil
import sys

from .safety import (digest, read_json, write_json, require, prepare_scratch,
                     verify_context, run_monitored)

SOURCE_SHA='8c68d920e71cea6373f9ee1f767f661d228ebafd6e1a00fadc580e00bc460e87'
PROPOSAL_SHA='80f7d7d6155978dd882fa48a9497d5a1dc62d255c828ee9fbcbeaed0282efea3'
TARGETS={'Q1':('9','e4ac9e85-c811-4bc1-8b0f-fb744a86e69b'),
         'Q2':('9','33d30c90-2a72-4b46-9865-95576d68a151'),
         'Q10':('9','2afd57c8-68fa-4e00-b83b-d4a8134c24e4'),
         'U4':('2','8de1b06f-f0ab-4d16-8a34-c3891d716649')}


def validate_proposal(data):
    require(data['current_board_sha256']==SOURCE_SHA,'Proposal source mismatch')
    changes=data['changes']
    require(len(changes)==4,'Exactly four physical lands required')
    require({r['ref']:(r['pad'],r['physical_pad_uuid']) for r in changes}==TARGETS,
            'Physical pad whitelist mismatch')
    for r in changes:
        windows=r['new_windows']
        require(len(windows)==(4 if r['ref']=='U4' else 2),'Wrong window count')
        for w in windows:
            dims=(w['nominal_width_mm'],w['nominal_height_mm'],w['corner_radius_mm'])
            require(dims==((.75,1.5,.05) if r['ref']=='U4' else (1.,1.5,.05)),
                    'Unapproved window dimensions')
    return changes


def guard(root):
    root=Path(root).resolve(strict=True)
    ctx=verify_context(root)
    request=read_json(root/'stencil-request.json')
    require(ctx['source_hashes'][Path(ctx['board']).name]==SOURCE_SHA,'Current-source drift')
    require(digest(request['proposal'])==PROPOSAL_SHA,'Reviewed proposal drift')
    validate_proposal(read_json(request['proposal']))
    for p,h in request['protected'].items():
        require(digest(p)==h,'Protected production/export input changed: '+p)
    return ctx,request


def native_save(api,board,path):
    original=board.GetFileName()
    require(api.SaveBoard(str(path),board),'Native scratch SaveBoard failed')
    board.SetFileName(original)


def layer_set(api,values):
    # KiCad10 SWIG accepts its concrete LSEQ, not a plain Python list.
    seq=api.LSEQ()
    for layer in values:seq.append(layer)
    return api.LSET(seq)


def restore_paste(api,board,transaction):
    by_uid={p.m_Uuid.AsString():p for fp in board.GetFootprints() for p in fp.Pads()}
    graphics={g.m_Uuid.AsString():(fp,g) for fp in board.GetFootprints() for g in fp.GraphicalItems()}
    for r in transaction['changed_pads']:
        pad=by_uid[r['uuid']]
        pad.SetLayerSet(layer_set(api,r['original_layer_ids']))
    for uid in transaction['added_graphics']:
        fp,g=graphics[uid]
        require(g.GetLayer()==api.F_Paste,'Non-paste graphic in transaction')
        fp.Remove(g)


def worker(action,root):
    from .native import api_load,vec
    from .geometry import snapshot,layout_snapshot
    root=Path(root).resolve(strict=True)
    ctx,request=guard(root)
    path=Path(ctx['board'])
    require(not (root/(action+'-done.json')).exists(),'Worker action already completed')
    api,board=api_load(path)
    require(api.GetBuildVersion()=='10.0.7','Review requires the verified installed KiCad10.0.7')
    changes=validate_proposal(read_json(request['proposal']))
    if action=='build':
        require(digest(path)==SOURCE_SHA,'Fresh production-derived candidate required')
        before=snapshot(board,api)
        require(before==read_json(request['reference_snapshot']),'Fresh read-only snapshot mismatch')
        write_json(root/'before-native.json',before)
        write_json(root/'before-layout.json',layout_snapshot(board,api))
        native_save(api,board,root/'reference-normalized.kicad_pcb')
        by_uid={p.m_Uuid.AsString():(fp,p) for fp in board.GetFootprints() for p in fp.Pads()}
        transaction=dict(changed_pads=[],added_graphics=[],windows=[])
        for r in changes:
            fp,pad=by_uid[r['physical_pad_uuid']]
            require(fp.GetReference()==r['ref'] and pad.GetNumber()==r['pad'],'Native pad identity mismatch')
            old_layers=list(pad.GetLayerSet().Seq())
            require(api.F_Paste in old_layers,'Original full paste contribution absent')
            transaction['changed_pads'].append(dict(ref=r['ref'],pad=r['pad'],uuid=r['physical_pad_uuid'],
                original_layer_ids=old_layers))
            # Existing electrical pad geometry, mask, nets and numbering untouched.
            pad.SetLayerSet(layer_set(api,[layer for layer in old_layers if layer!=api.F_Paste]))
            for index,w in enumerate(r['new_windows']):
                shape=api.PCB_SHAPE(fp)
                shape.SetShape(api.SHAPE_T_RECT)
                x,y=w['center_mm'];a=w['nominal_width_mm'];b=w['nominal_height_mm']
                shape.SetStart(vec(api,[x-a/2,y-b/2]))
                shape.SetEnd(vec(api,[x+a/2,y+b/2]))
                shape.SetCornerRadius(round(w['corner_radius_mm']*1e6))
                shape.SetWidth(0);shape.SetFilled(True);shape.SetLayer(api.F_Paste)
                shape.Rotate(vec(api,[x,y]),api.EDA_ANGLE(w['rotation_deg'],api.DEGREES_T))
                fp.Add(shape)
                uid=shape.m_Uuid.AsString()
                transaction['added_graphics'].append(uid)
                transaction['windows'].append(dict(ref=r['ref'],index=index,uuid=uid,
                    start_nm=[shape.GetStart().x,shape.GetStart().y],
                    end_nm=[shape.GetEnd().x,shape.GetEnd().y],radius_nm=shape.GetCornerRadius()))
        after=snapshot(board,api)
        require(after==before,'Unexpected native copper/pad/net/via/placement/fill geometry change')
        write_json(root/'transaction.json',transaction)
        native_save(api,board,path)
        write_json(root/'candidate-save.json',dict(sha256=digest(path),native_snapshot_unchanged=True))
    elif action=='verify':
        proof_name=request.get('verification_output','independent-readback')
        require(Path(proof_name).name==proof_name,'Unsafe verification output name')
        proof=root/proof_name
        require(not proof.exists(),'Fresh independent readback output required')
        proof.mkdir()
        transaction=read_json(root/'transaction.json')
        require(digest(path)==read_json(root/'candidate-save.json')['sha256'],'Saved candidate drift')
        after=snapshot(board,api)
        require(after==read_json(root/'before-native.json'),'Independent native readback geometry differs')
        require(layout_snapshot(board,api)==read_json(root/'before-layout.json'),'Actual fills/outline/courtyards changed')
        graphics={g.m_Uuid.AsString():g for fp in board.GetFootprints() for g in fp.GraphicalItems()}
        require(all(uid in graphics for uid in transaction['added_graphics']),'Missing saved paste graphics')
        for uid in transaction['added_graphics']:
            g=graphics[uid]
            require(g.GetLayer()==api.F_Paste and g.GetFillMode()==api.FILL_T_FILLED_SHAPE and g.GetWidth()==0,
                    'Paste graphic layer/fill/stroke readback mismatch')
            if g.GetShape()==api.SHAPE_T_RECT:
                require(g.GetCornerRadius()==50000,'Rounded rectangle radius mismatch')
            else:
                # KiCad's arbitrary-angle rectangle rotation uses an arc-bearing
                # polygon on save. Its radius scalar is inapplicable; final CAM
                # comparison must establish the actual curves at reviewed angle.
                record=next(r for r in transaction['windows'] if r['uuid']==uid)
                require(record['ref']=='Q2' and g.GetShape()==api.SHAPE_T_POLY,
                        'Unexpected saved paste representation')
        # Reversing only the exact whitelist IN MEMORY must reproduce the entire
        # canonical native source. No serialized CAD is parsed or edited.
        restore_paste(api,board,transaction)
        restored=proof/'restored-normalized.kicad_pcb'
        native_save(api,board,restored)
        require(digest(restored)==digest(root/'reference-normalized.kicad_pcb'),
                'Full canonical native board differs beyond the paste whitelist')
        write_json(proof/'result.json',dict(candidate_sha256=digest(path),
            all_original_native_snapshot_equal=True,all_original_layout_equal=True,
            full_native_canonical_board_equal_after_exact_paste_reversal=True,
            vias=len(after['vias']),pads=len(after['pads']),added_paste_only_graphics=len(transaction['added_graphics'])))
    else:
        raise ValueError(action)
    guard(root)
    write_json(root/(action+'-done.json'),dict(action=action,production_preserved=True))
    print(action+' complete: scratch only; production preserved',flush=True)


def prepare(args):
    require(digest(args.board)==SOURCE_SHA,'Production source no longer matches owner-reviewed current source')
    require(digest(args.proposal)==PROPOSAL_SHA,'Proposal drift')
    validate_proposal(read_json(args.proposal))
    root=prepare_scratch(args.board,args.baseline,args.output)
    # Preserve exact project-local links and library contents, not replacement libraries.
    source=Path(args.board).resolve().parent
    for name in ('fp-lib-table','sym-lib-table'):
        if (source/name).exists():shutil.copy2(source/name,root/name)
    for name in ('ups_v4.pretty','ups_v4_external.pretty'):
        if (source/name).exists():shutil.copytree(source/name,root/name)
    write_json(root/'stencil-request.json',dict(proposal=str(Path(args.proposal).resolve()),
        reference_snapshot=str(Path(args.reference_snapshot).resolve()),
        protected=read_json(args.protected),source_authority='Owner Phase4.24T scratch-only four F.Paste lands'))
    guard(root)
    return root


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('prepare')
    for name in ('board','baseline','proposal','reference-snapshot','protected','output'):
        p.add_argument('--'+name,required=True,type=Path)
    p=sub.add_parser('run')
    p.add_argument('--root',required=True,type=Path)
    p.add_argument('--native-python',required=True,type=Path)
    p.add_argument('--operation',required=True,choices=('build','verify'))
    p=sub.add_parser('_worker')
    p.add_argument('--root',required=True,type=Path)
    p.add_argument('--operation',required=True,choices=('build','verify'))
    args=parser.parse_args()
    if args.action=='prepare':
        print(prepare(args))
    elif args.action=='run':
        guard(args.root)
        require(not (args.root/(args.operation+'.log')).exists(),'Fresh worker invocation required')
        # KiCad's bundled Python may use an isolated ._pth environment. Use the
        # established toolkit entry point, which bootstraps its own package path.
        entry=Path(__file__).resolve().parents[1]/'kicad_v4.py'
        result=run_monitored([args.native_python,'-B',entry,'_worker',
                              '--scratch-dir',args.root,'--action','stencil-'+args.operation],
                             args.root/(args.operation+'.log'))
        print(result['stdout'])
    else:
        worker(args.operation,args.root)


if __name__=='__main__':
    main()
