"""Archive/close an agent scratch after the proven parent-link false positive.

Not assertion/IPC recovery and never a candidate gate. No discard dialog or
production write. Save only after live equality with the already captured exact
scratch transaction, then the normal clean-window lifecycle helper may close it.
"""
from pathlib import Path
import argparse
import sys
from .safety import require,read_json,write_json,digest,verify_hashes,run_monitored,ToolError


def evidence(root):
    from .j7_migration import capture_equal,PRODUCTION,MANIFEST,ACCEPTED,reconcile,GOAL
    root=Path(root).resolve();c=read_json(root/'j7-migration-context.json')
    target=Path(c['target']).resolve();d=read_json(root/'validation-disposition.json')
    require(target.parent==root and target!=PRODUCTION.resolve() and not c['production']
            and not c['identity_only'], 'Cleanup only owns an isolated agent scratch')
    require(read_json(root/'STOP.json')['error'].startswith('Native worker failed (exit 2)'),
            'No cleanup of native assertion/IPC failure')
    require('STOP: Post-commit native preservation failure' in (root/'ipc-apply.log').read_text()
            and d['classification']=='FALSE_POSITIVE_RUNTIME_PARENT_LINKS_ONLY'
            and d['no_native_assertion_or_IPC_failure'], 'Only proven metadata false positive may be archived')
    require(not (root/'ipc-saved.json').exists() and not (root/'live-refilled.json').exists(),
            'Unexpected scratch execution state')
    require(capture_equal(read_json(root/'ipc-expected.json'),read_json(root/'ipc-after.json')),
            'Actual transaction has non-metadata mismatch')
    reconcile(read_json(GOAL/'before.json'),read_json(GOAL/'final-snapshot.json'))
    verify_hashes(PRODUCTION.parent,read_json(MANIFEST)['hashes'])
    return target


def saved_cleanup(root):
    root=Path(root);target=evidence(root);p=read_json(root/'cleanup-saved.json')
    require(p['saved_live_expected_equal'] and p['not_a_candidate_gate'] and
            p['cleanup_implementation']==digest(__file__), 'Cleanup proof incomplete')
    verify_hashes(target.parent,p['hashes'])
    return p


def worker(root,socket):
    from .j7_migration import capture_equal,PRODUCTION,MANIFEST
    from .ipc_install import capture
    root=Path(root);target=evidence(root)
    require(not (root/'cleanup-saved.json').exists(), 'Cleanup already archived')
    sys.path.insert(0,str(PRODUCTION.parent.resolve()/'.konnect/native-ipc'))
    from kipy import KiCad
    from kipy.proto.common.types.base_types_pb2 import DocumentType
    k=KiCad(socket_path=socket,client_name='UPS V4 archive own verified diagnostic scratch')
    require(k.get_version().major==10 and len(k.get_open_documents(DocumentType.DOCTYPE_PCB))==1,
            'Ambiguous scratch editor')
    b=k.get_board()
    require(b.name==target.name and Path(b.document.project.path).resolve()==target.parent, 'Wrong scratch editor')
    actual=capture(b)
    require(capture_equal(read_json(root/'ipc-after.json'),actual), 'User/live scratch drift; no save/close')
    b.save();saved=capture(b)
    require(capture_equal(actual,saved), 'Scratch save changed native payload')
    hashes={n:digest(target.parent/n) for n in read_json(MANIFEST)['hashes']}
    write_json(root/'cleanup-saved.json',dict(saved_live_expected_equal=True,not_a_candidate_gate=True,
        cleanup_implementation=digest(__file__),hashes=hashes))
    evidence(root)
    print('Agent diagnostic scratch archived through owning editor; normal clean close allowed')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--worker',action='store_true');p.add_argument('--socket',default='auto');a=p.parse_args()
    try:
        if a.worker:worker(a.root,a.socket)
        else:
            from .j7_migration import observed_endpoint
            evidence(a.root);log=a.root/'cleanup.log';require(not log.exists(),'Cleanup cannot be repeated')
            socket=observed_endpoint(a.root,a.socket,'cleanup')
            run_monitored([sys.executable,'-B','-m','v4kicad.scratch_cleanup','--worker',
                           '--root',a.root,'--socket',socket],log)
            print('Monitored scratch archival complete')
        return 0
    except (ToolError,OSError,ValueError,KeyError,TypeError) as e:
        print('STOP: '+str(e),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
