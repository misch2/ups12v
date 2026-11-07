"""Explicit offline scratch CLI. No filesystem or native work on import."""
from pathlib import Path
import argparse
import json
import shutil
import sys
from .checks import run_check
from .safety import (ToolError, prepare_scratch, prepare_review_scratch, read_json,
                     require, run_monitored, verify_context, write_json, digest)


def native(root, python, action):
    entry = Path(__file__).resolve().parents[1] / 'kicad_v4.py'
    run_monitored([python, '-B', entry, '_worker', '--scratch-dir', root, '--action', action],
                  Path(root) / (action + '.log'))


def parser():
    result = argparse.ArgumentParser(description='V4 offline native KiCad 10 scratch tooling')
    sub = result.add_subparsers(dest='command', required=True)
    for name in ['snapshot', 'probe', 'validate']:
        p = sub.add_parser(name)
        p.add_argument('--board', required=True, type=Path)
        p.add_argument('--baseline-manifest', required=True, type=Path,
                       help='JSON with hashes keyed by source filenames (SHA256)')
        p.add_argument('--output-dir', required=True, type=Path, help='Fresh, nonexistent scratch directory')
        p.add_argument('--native-python', required=True, type=Path)
        if name=='snapshot':
            p.add_argument('--review-bounds',type=float,nargs=4,help='Read-only native In1 fill sampling bounds')
            p.add_argument('--route-diagnostics',action='store_true',help='Read-only raw routed units and via padstacks')
            p.add_argument('--routing-context',action='store_true',help='Export exact offline copper-preflight context')
        if name == 'validate':
            p.add_argument('--plan', required=True, type=Path)
            p.add_argument('--validation-context',required=True,type=Path)
            p.add_argument('--track-uuid')
            p.add_argument('--from-layer')
            p.add_argument('--to-layer')
            p.add_argument('--add-only', action='store_true')
            p.add_argument('--allow-u3-placement', action='store_true',
                           help='Scratch-only L2/C37/C33/C45 rigid placement investigation')
            p.add_argument('--kicad-cli', required=True, type=Path)
            p.add_argument('--erc', action='store_true', help='Also run native ERC on the copied schematic')
    p = sub.add_parser('check', help='Run a check on an existing toolkit-created scratch project only')
    p.add_argument('--scratch-dir', required=True, type=Path)
    p.add_argument('--kind', required=True, choices=['drc', 'erc'])
    p.add_argument('--kicad-cli', required=True, type=Path)
    p = sub.add_parser('replace', help='Bounded scratch-only original track replacement; no production installer')
    for flag in ['board', 'baseline-manifest', 'output-dir', 'native-python', 'kicad-cli', 'plan', 'validation-context']:
        p.add_argument('--'+flag, required=True, type=Path)
    p = sub.add_parser('audit', help='Read-only zone/artwork audit of an unlocked toolkit scratch project')
    p.add_argument('--scratch-dir', required=True, type=Path)
    p.add_argument('--native-python', required=True, type=Path)
    p = sub.add_parser('review', help='Read-only owner-edited source review against an accepted baseline')
    for flag in ['board', 'baseline-manifest', 'output-dir', 'native-python', 'kicad-cli', 'reference-board']:
        p.add_argument('--'+flag, required=True, type=Path)
    p.add_argument('--route-diagnostics', action='store_true')
    p.add_argument('--routing-context', action='store_true')
    p = sub.add_parser('_worker', help=argparse.SUPPRESS)
    p.add_argument('--scratch-dir', required=True, type=Path)
    p.add_argument('--action', choices=['snapshot', 'probe', 'apply', 'verify', 'audit', 'polygon-audit', 'review-snapshot', 'review-post-check', 'review-inspect', 'replace-create', 'replace-verify', 'f5-build', 'f5-verify', 'stencil-build', 'stencil-verify', 'stencil-serialization-proof', 'stencil-adoption-readback', 'stencil-native-snapshot', 'stencil-native-apply', 'stencil-native-verify'], required=True)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == '_worker':
            from .native import worker
            worker(args.action, args.scratch_dir)
            return 0
        if args.command == 'replace':
            from .replacement import run
            summary = run(args)
            print(json.dumps(dict(scratch=str(args.output_dir), drc=summary['drc'], erc=summary['erc'],
                                  preservation=True, production_unchanged=True)))
            return 0
        if args.command == 'check':
            print(json.dumps(run_check(args.scratch_dir, args.kicad_cli, args.kind)))
            return 0
        if args.command == 'audit':
            require(not (args.scratch_dir/'audit.log').exists(), 'Audit already exists; STOP')
            require(args.native_python.is_file(), 'Native Python executable missing; STOP')
            native(args.scratch_dir,args.native_python,'audit')
            print('Read-only zone/artwork audit complete; no CAD save')
            return 0
        if args.command == 'review':
            require(args.native_python.is_file(), f'Native Python executable missing: {args.native_python}; STOP')
            require(args.kicad_cli.is_file(), f'KiCad CLI missing: {args.kicad_cli}; STOP')
            root = prepare_review_scratch(args.board, args.baseline_manifest, args.output_dir,
                                          args.reference_board)
            write_json(root / 'review-request.json', dict(review_bounds=None,
                       route_diagnostics=args.route_diagnostics,
                       routing_context=args.routing_context))
            native(root, args.native_python, 'review-snapshot')
            from .checks import run_review_check
            drc = run_review_check(root, args.kicad_cli, 'drc')
            native(root, args.native_python, 'review-post-check')
            erc = run_review_check(root, args.kicad_cli, 'erc', allow_target_change=True)
            require(drc['errors'] == 0 and drc['parity'] == 0,
                    f'Review DRC/parity failure: {drc["errors"]} errors, {drc["parity"]} parity; STOP')
            require(erc['errors'] == 0,
                    f'Review ERC failure: {erc["errors"]} errors; STOP')
            native(root, args.native_python, 'review-inspect')
            write_json(root / 'summary.json', dict(schema_version=1, mode='owner-edit-review',
                       drc=drc, erc=erc, source_hashes=read_json(root/'context.json')['source_hashes'],
                       accepted_hashes=read_json(root/'context.json')['accepted_hashes'],
                       original_sources_unchanged=True))
            print(json.dumps(dict(review=str(root), drc=drc, erc=erc,
                                  original_sources_unchanged=True)))
            return 0
        require(args.native_python.is_file(), f'Native Python executable missing: {args.native_python}; STOP')
        if args.command == 'validate':
            from .plan_validation import validate_bound
            require(args.kicad_cli.is_file(), f'KiCad CLI missing: {args.kicad_cli}; STOP')
            require(args.plan.is_file(), f'Plan missing: {args.plan}; STOP')
            require(args.board.with_suffix('.kicad_sch').is_file() and args.board.with_suffix('.kicad_pro').is_file(),
                    'Matching source schematic/project required for DRC parity and rules; STOP')
            if args.add_only:
                require(not any([args.track_uuid, args.from_layer, args.to_layer]),
                        'Add-only workflow cannot change original tracks; STOP')
            else:
                require(all([args.track_uuid, args.from_layer, args.to_layer]) and args.from_layer != args.to_layer,
                        'Explicit original track and different layers required; STOP')
            require(args.add_only and not args.allow_u3_placement,'New preflight currently supports add-only fixed-placement plans')
            result=validate_bound(args.plan,args.validation_context,args.board,
                args.output_dir.parent/(args.output_dir.name+'-preapplication.json'))
        root = prepare_scratch(args.board, args.baseline_manifest, args.output_dir)
        if args.command in ['snapshot', 'probe']:
            if args.command=='snapshot' and (args.review_bounds or args.route_diagnostics or args.routing_context):
                write_json(root/'review-request.json',dict(review_bounds=args.review_bounds,
                    route_diagnostics=args.route_diagnostics,routing_context=args.routing_context))
            native(root, args.native_python, args.command)
            verify_context(root)
            print(json.dumps(dict(snapshot=str(root / 'snapshot.json'), production_unchanged=True)))
            return 0
        shutil.copy2(args.plan, root / 'plan.json')
        write_json(root/'preflight-binding.json',dict(validation_context=str(args.validation_context.resolve()),
            context_sha256=digest(args.validation_context)))
        write_json(root / 'request.json', dict(track_uuid=args.track_uuid,
                                              from_layer=args.from_layer, to_layer=args.to_layer,
                                              allow_u3_placement=args.allow_u3_placement))
        native(root, args.native_python, 'apply')
        drc = run_check(root, args.kicad_cli, 'drc')
        # Do not continue into native APIs after a failed candidate check.
        require(drc['errors'] == 0 and drc['parity'] == 0,
                f'Candidate failed native DRC/parity: {drc["errors"]} errors, {drc["parity"]} parity; inspect {root / "drc.json"}; STOP')
        erc = run_check(root, args.kicad_cli, 'erc') if args.erc else None
        if erc:
            require(erc['errors'] == 0, f'ERC errors; inspect {root / "erc.json"}; STOP')
        native(root, args.native_python, 'verify')
        summary = dict(schema_version=1, drc=drc, erc=erc,
                       build=read_json(root / 'build-summary.json'),
                       preservation=read_json(root / 'preservation.json'),
                       production_hashes_unchanged=True)
        write_json(root / 'summary.json', summary)
        print(json.dumps(summary))
        return 0
    except (ToolError, OSError, ValueError, KeyError, TypeError) as error:
        print(f'STOP: {error}', file=sys.stderr)
        return 2
