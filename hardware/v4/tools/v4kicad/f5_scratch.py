"""Phase4.17 bounded F5 placement/routing on fresh baseline copies only.

No production installer or IPC operations. Importing performs no CAD/file I/O.
Geometry screening and native operations reuse the guarded toolkit.
"""
from pathlib import Path
import argparse
import copy
import math
import shutil

from .safety import (require, read_json, write_json, digest, prepare_scratch,
                     verify_context, run_monitored, ToolError)
from .plan_validation import check_plan, route_key

F5_REFS = frozenset(['U7', 'U8', 'Q10', 'L3', 'J8'] +
                    ['R'+str(i) for i in range(60, 64)] +
                    ['C'+str(i) for i in range(60, 70)])
BASELINE = 'bce08349485b0f8d53060fcc9ef1a3911eaabf0408de16b288d0655e30754899'
NETS = frozenset(['SYS', 'PGND'] + ['/F5_'+n for n in
                ['RAW', 'SW', 'BST', 'FB', 'SS', 'EN', 'GATE', 'VCAP', '5V_OUT']])


def transformed(g, placements):
    """Rigid-transform exported geometry; native save/readback remains authoritative."""
    require(set(placements) <= F5_REFS, 'Only nineteen F5 assembly references may move')
    out = copy.deepcopy(g)
    originals = {f['ref']: f for f in g['footprints'].values()}
    require(set(placements) <= set(originals), 'Unknown placement reference')
    def point(p, ref):
        old = originals[ref]; x, y, angle = placements[ref]
        require(all(math.isfinite(v) for v in [x, y, angle]), 'Nonfinite placement')
        require(angle % 90 == 0 and old['angle'] % 90 == 0, 'Only exact orthogonal placement')
        a = math.radians(angle-old['angle']); c, s = round(math.cos(a)), round(math.sin(a))
        u, v = p[0]-old['position'][0], p[1]-old['position'][1]
        return [round(x+c*u+s*v, 6), round(y-s*u+c*v, 6)]
    for fp in out['footprints'].values():
        if fp['ref'] in placements:
            p = placements[fp['ref']]; fp.update(position=p[:2], angle=p[2])
    for p in out['pads'].values():
        if p['ref'] not in placements:
            continue
        ref = p['ref']; p['position'] = point(p['position'], ref)
        p['polygons'] = {l: [[point(q, ref) for q in poly] for poly in polys]
                         for l, polys in p['polygons'].items()}
    return out


def scope(context, plan):
    require(context['board_sha256'] == BASELINE, 'F5 requires exact accepted Phase4.16 source')
    require(plan.get('baseline_sha256') == BASELINE and plan.get('mode') == 'F5-scratch-only',
            'Unbound or non-scratch F5 plan')
    require(not plan.get('remove_tracks') and not plan.get('remove_vias'),
            'This milestone preserves all accepted copper')
    require(plan.get('failure', 'missing') is None, 'Failed or malformed plan')
    require(len(plan['tracks']) <= 240 and len(plan['vias']) <= 70, 'F5 batch exceeds bound')
    require(all(t[0] in NETS for t in plan['tracks']+plan['vias']), 'Unapproved routing net')
    for t in plan['tracks']:
        require(t[1] != 'In1.Cu' or t[0] == 'PGND', 'In1 remains PGND reference')
    g = transformed(context['snapshot'], plan.get('placements', {}))
    c = copy.deepcopy(context)
    # Remove only the historical planning reservation for the now-authorized F5.
    # Native rule areas, all physical rules and USB reservations remain hard.
    c['reservations'] = [r for r in c['reservations'] if r['name'] != 'F5 future access']
    for uid, p in context['snapshot']['pads'].items():
        if p['ref'] in plan.get('placements', {}):
            old = next(f for f in context['snapshot']['footprints'].values() if f['ref'] == p['ref'])
            c['pads'][uid]['orientation'] += plan['placements'][p['ref']][2]-old['angle']
    return g, c


def preflight(context, plan):
    g, c = scope(context, plan)
    return check_plan(g, plan, c)


def compare_placed(before, after, placements):
    expected = transformed(before, placements)
    # Polygon cyclic ordering can differ after an exact native quarter turn.
    for uid, pad in expected['pads'].items():
        actual = after['pads'].get(uid)
        require(actual is not None, 'Placement lost a pad')
        for key in pad:
            if key == 'polygons':
                require(set(pad[key]) == set(actual[key]), 'Pad copper layers changed')
                for layer in pad[key]:
                    from collections import Counter
                    pts = lambda polys: Counter((round(x, 6), round(y, 6)) for poly in polys for x, y in poly)
                    require(pts(pad[key][layer]) == pts(actual[key][layer]), 'Pad shape changed: '+pad['ref'])
            else:
                require(pad[key] == actual[key], 'Pad metadata/position changed: '+pad['ref']+'/'+key)
    for s in ['footprints', 'tracks', 'vias', 'zones']:
        require(expected[s] == after[s], 'Unexpected placement change: '+s)
    return dict(F0_exact=True, all_original_copper_exact=True, rigid_F5_refs=sorted(placements))


def retained(before, after, plan, expected):
    from .geometry import preservation
    from .native import verify_added
    placed = transformed(before, plan.get('placements', {}))
    # Use actual native pad polygon ordering, after the explicit rigid check.
    stripped = copy.deepcopy(after)
    for section in ['tracks', 'vias']:
        stripped[section] = {u: v for u, v in after[section].items() if u in before[section]}
    stripped['zones'] = before['zones']
    compare_placed(before, stripped, plan.get('placements', {}))
    placed['pads'] = stripped['pads']
    result = preservation(placed, after)
    verify_added(before, after, expected)
    return result


def worker(action, root):
    from .native import api_load, vec, apply_routes
    from .geometry import snapshot, native_audit, layout_snapshot, routing_context
    from .replacement import pad_partition
    root = Path(root); ctx = verify_context(root)
    binding = read_json(root/'f5-binding.json')
    require(digest(binding['context']) == binding['context_sha256'], 'F5 context drift')
    require(digest(root/'plan.json') == binding['plan_sha256'], 'F5 plan drift')
    source_context = read_json(binding['context']); plan = read_json(root/'plan.json')
    require(digest(ctx['source']) == BASELINE, 'Production source drift')
    require(preflight(source_context, plan)['valid'], 'F5 preflight no longer valid')
    path = Path(ctx['board']); api, board = api_load(path)
    if action == 'build':
        require(digest(path) == BASELINE, 'Fresh untouched accepted scratch required')
        before = snapshot(board, api)
        require(before == source_context['snapshot'], 'Entry snapshot mismatch')
        write_json(root/'before.json', before)
        write_json(root/'audit-before.json', native_audit(board, api))
        write_json(root/'partition-before.json', pad_partition(board))
        for fp in board.GetFootprints():
            if fp.GetReference() in plan.get('placements', {}):
                x, y, angle = plan['placements'][fp.GetReference()]
                fp.SetOrientationDegrees(angle); fp.SetPosition(vec(api, [x, y]))
        placed = snapshot(board, api)
        write_json(root/'placement-preservation.json', compare_placed(before, placed, plan.get('placements', {})))
        expected = apply_routes(board, api, plan)
        write_json(root/'expected-additions.json', expected)
        write_json(root/'pre-save-preservation.json', retained(before, snapshot(board, api), plan, expected))
        require(api.SaveBoard(str(path), board), 'Native scratch save failed')
        write_json(root/'saved-hash.json', dict(sha256=digest(path)))
    else:
        before = read_json(root/'before.json'); after = snapshot(board, api)
        proof = retained(before, after, plan, read_json(root/'expected-additions.json'))
        old_partition = read_json(root/'partition-before.json'); new_partition = pad_partition(board)
        require(all(any(set(a) <= set(b) for b in new_partition) for a in old_partition),
                'A previously connected pad island was split')
        audit_before = read_json(root/'audit-before.json'); audit = native_audit(board, api)
        require(audit_before['zones'] == audit['zones'] and audit_before['drawings'] == audit['drawings'],
                'Zone definitions or board artwork changed')
        for ref, graphics in audit_before['footprint_graphics'].items():
            if ref not in plan.get('placements', {}):
                require(graphics == audit['footprint_graphics'][ref], 'F0 artwork changed: '+ref)
        write_json(root/'snapshot.json', after)
        write_json(root/'layout.json', layout_snapshot(board, api))
        write_json(root/'routing-context.json', routing_context(board, api, path, after))
        write_json(root/'partition-after.json', new_partition)
        proof.update(all_old_pad_islands_preserved=True, pad_count=len(after['pads']),
                     before_islands=len(old_partition), after_islands=len(new_partition),
                     source_hashes_unchanged=True, sha256=digest(path))
        write_json(root/'preservation.json', proof)
    verify_context(root)
    print('F5 scratch '+action+' complete')


def run(args):
    from .checks import run_check
    context = read_json(args.context); plan = read_json(args.plan)
    require(digest(args.board) == BASELINE, 'Accepted production hash mismatch')
    result = preflight(context, plan)
    # Offline rejection writes only diagnostics; no native worker is launched.
    write_json(args.output_dir.parent/(args.output_dir.name+'-preflight.json'), result)
    require(result['valid'], 'F5 preflight rejected '+str(len(result['errors']))+' geometric conflicts')
    require(not any(w['type'] == 'duplicate_track' for w in result['warnings']), 'Duplicate routes rejected')
    root = prepare_scratch(args.board, args.baseline_manifest, args.output_dir)
    shutil.copy2(args.plan, root/'plan.json')
    write_json(root/'f5-binding.json', dict(context=str(args.context.resolve()),
               context_sha256=digest(args.context), plan_sha256=digest(root/'plan.json')))
    entry = Path(__file__).resolve().parents[1]/'kicad_v4.py'
    for action in ['build', 'verify']:
        if action == 'verify':
            drc = run_check(root, args.kicad_cli, 'drc')
            # Normal DRC errors are evidence for an independent fresh candidate.
            # Always preserve geometry/islands even for a rejected candidate.
        run_monitored([args.native_python, '-B', entry, '_worker', '--action', 'f5-'+action,
                       '--scratch-dir', root], root/(action+'.log'))
    erc = run_check(root, args.kicad_cli, 'erc')
    summary = dict(drc=drc, erc=erc, preservation=read_json(root/'preservation.json'),
                   candidate_acceptable=(drc['errors'] == 0 and drc['parity'] == 0 and erc['errors'] == 0))
    write_json(root/'summary.json', summary)
    print(__import__('json').dumps(summary))


def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '_worker':
        worker(sys.argv[2], Path(sys.argv[3])); return
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['board', 'baseline-manifest', 'context', 'plan', 'output-dir', 'native-python', 'kicad-cli']:
        p.add_argument('--'+name, required=True, type=Path)
    try:
        run(p.parse_args())
    except (ToolError, OSError, ValueError, KeyError, TypeError) as e:
        print('STOP: '+str(e), file=sys.stderr); sys.exit(2)


if __name__ == '__main__':
    main()
