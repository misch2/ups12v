"""Explicit offline scratch CLI. No filesystem or native work on import."""
from pathlib import Path
import argparse
import json
import shutil
import sys
from .checks import run_check
from .safety import ToolError, prepare_scratch, read_json, require, run_monitored, verify_context, write_json


def native(root, python, action):
    entry = Path(__file__).resolve().parents[1] / 'kicad_v4.py'
    run_monitored([python, '-B', entry, '_worker', '--scratch-dir', root, '--action', action],
                  Path(root) / (action + '.log'))


def parser():
    result = argparse.ArgumentParser(description='V4 offline native KiCad 10 scratch tooling')
    sub = result.add_subparsers(dest='command', required=True)
    for name in ['snapshot', 'validate']:
        p = sub.add_parser(name)
        p.add_argument('--board', required=True, type=Path)
        p.add_argument('--baseline-manifest', required=True, type=Path,
                       help='JSON with hashes keyed by source filenames (SHA256)')
        p.add_argument('--output-dir', required=True, type=Path, help='Fresh, nonexistent scratch directory')
        p.add_argument('--native-python', required=True, type=Path)
        if name == 'validate':
            p.add_argument('--plan', required=True, type=Path)
            p.add_argument('--track-uuid')
            p.add_argument('--from-layer')
            p.add_argument('--to-layer')
            p.add_argument('--add-only', action='store_true')
            p.add_argument('--kicad-cli', required=True, type=Path)
            p.add_argument('--erc', action='store_true', help='Also run native ERC on the copied schematic')
    p = sub.add_parser('check', help='Run a check on an existing toolkit-created scratch project only')
    p.add_argument('--scratch-dir', required=True, type=Path)
    p.add_argument('--kind', required=True, choices=['drc', 'erc'])
    p.add_argument('--kicad-cli', required=True, type=Path)
    p = sub.add_parser('_worker', help=argparse.SUPPRESS)
    p.add_argument('--scratch-dir', required=True, type=Path)
    p.add_argument('--action', choices=['snapshot', 'apply', 'verify'], required=True)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == '_worker':
            from .native import worker
            worker(args.action, args.scratch_dir)
            return 0
        if args.command == 'check':
            print(json.dumps(run_check(args.scratch_dir, args.kicad_cli, args.kind)))
            return 0
        require(args.native_python.is_file(), f'Native Python executable missing: {args.native_python}; STOP')
        if args.command == 'validate':
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
        root = prepare_scratch(args.board, args.baseline_manifest, args.output_dir)
        if args.command == 'snapshot':
            native(root, args.native_python, 'snapshot')
            verify_context(root)
            print(json.dumps(dict(snapshot=str(root / 'snapshot.json'), production_unchanged=True)))
            return 0
        shutil.copy2(args.plan, root / 'plan.json')
        write_json(root / 'request.json', dict(track_uuid=args.track_uuid,
                                              from_layer=args.from_layer, to_layer=args.to_layer))
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
