"""Bounded track replacement on fresh isolated scratch boards only.

Deliberately separate from add-only production installation. No IPC entry point.
Importing this module does not load CAD, start processes, or write files.
"""
from pathlib import Path
from collections import Counter
import copy
import json
import re
import shutil

from .safety import require, read_json, write_json, digest, verify_context, prepare_scratch
from .plan_validation import check_plan, route_key


def remaining(context, plan):
    require(plan.get('mode') == 'scratch-track-replacement', 'Explicit scratch replacement mode required')
    require(not plan.get('placements') and not plan.get('vias'), 'Replacement cannot move parts or alter vias')
    old = context['snapshot']
    removed = plan.get('remove_tracks')
    require(isinstance(removed, dict) and 0 < len(removed) <= 20, 'Replacement requires 1..20 exact original tracks')
    require(0 < len(plan['tracks']) <= 30, 'Replacement additions must be bounded')
    require(all(old['tracks'].get(u) == t for u, t in removed.items()), 'Original replacement identity/geometry mismatch; STOP')
    require(len({(t['net'], t['layer']) for t in removed.values()}) == 1, 'One net/layer per candidate')
    net, layer = next(iter({(t['net'], t['layer']) for t in removed.values()}))
    require(all(t[:2] == [net, layer] for t in plan['tracks']), 'Replacement net/layer mismatch; STOP')
    require(plan.get('baseline_sha256') == context['board_sha256'], 'Replacement baseline mismatch')
    g = copy.deepcopy(old)
    for u in removed:
        del g['tracks'][u]
    return g


def preflight(plan_path, context_path, source, output):
    context, plan = read_json(context_path), read_json(plan_path)
    source = Path(source)
    require(context['board_sha256'] == digest(source), 'Replacement context/source drift')
    require(context['profile']['project_sha256'] == digest(source.with_suffix('.kicad_pro')) and
            context['profile']['rules_sha256'] == digest(source.with_suffix('.kicad_dru')), 'Replacement rules drift')
    result = check_plan(remaining(context, plan), plan, context)
    result.update(plan_sha256=digest(plan_path), context_sha256=digest(context_path),
                  explicitly_removed=sorted(plan['remove_tracks']))
    write_json(output, result)
    require(result['valid'], f"Replacement preflight rejected {len(result['errors'])} violations; no native mutation")
    require(not any(w['type'] == 'duplicate_track' for w in result['warnings']), 'Duplicate replacement rejected')
    return result


def preserved(before, after, plan, expected):
    """Independently enumerate removals, retain every other object, exact additions."""
    from .geometry import preservation
    from .native import verify_added
    retained = copy.deepcopy(before)
    for u, row in plan['remove_tracks'].items():
        require(before['tracks'].get(u) == row and u not in after['tracks'], 'Replacement removal mismatch; STOP')
        del retained['tracks'][u]
    result = preservation(retained, after)
    verify_added(before, after, expected)
    observed = [t for u, t in after['tracks'].items() if u not in before['tracks']]
    key = lambda t: route_key([t['net'], t['layer'], t['width'], *t['start'], *t['end']], 'track')
    require(Counter(map(key, observed)) == Counter(route_key(t, 'track') for t in plan['tracks']),
            'Independent replacement geometry differs from plan; STOP')
    result.update(removed_tracks=sorted(plan['remove_tracks']), added_uuids=sorted(expected),
                  retained_tracks=len(retained['tracks']), retained_vias=len(before['vias']))
    return result


def pad_partition(board):
    """Native connectivity traversal; compare pad islands independently of route UUIDs."""
    board.BuildConnectivity()
    cn = board.GetConnectivity()
    pads = {p.m_Uuid.AsString(): p for fp in board.GetFootprints() for p in fp.Pads()}
    seen, groups = set(), []
    for uid, p in sorted(pads.items()):
        if uid in seen:
            continue
        todo, visited = [p], set()
        while todo:
            item = todo.pop()
            u = item.m_Uuid.AsString()
            if u in visited:
                continue
            visited.add(u)
            todo.extend(x for x in cn.GetConnectedItems(item) if x.m_Uuid.AsString() not in visited)
        group = sorted(set(pads) & visited)
        seen.update(group)
        groups.append(group)
    return sorted(groups)


def serialized_retained(path, removed=()):
    """Read-only independent coverage of fields absent from geometry exports.

    Parse native-authored serialization for comparison only. Never write CAD.
    Keep nested order. Only top-level ordering, serializer identity, and native
    derived zone fills are excluded; zone definitions and all other fields remain.
    """
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', Path(path).read_text(encoding='utf-8'))
    stack, root = [], None
    for t in tokens:
        if t == '(':
            node = []
            if stack:
                stack[-1].append(node)
            stack.append(node)
        elif t == ')':
            root = stack.pop()
        else:
            stack[-1].append(t)
    require(not stack and root and root[0] == 'kicad_pcb', 'Invalid native board serialization')
    rows = []
    for node in root[1:]:
        if node[0] in ['generator', 'generator_version']:
            continue
        if node[0] == 'segment':
            uid = next(x[1].strip('"') for x in node[1:] if isinstance(x, list) and x[0] == 'uuid')
            if uid in removed:
                continue
        if node[0] == 'zone':
            node = [x for x in node if not (isinstance(x, list) and x[0] == 'filled_polygon')]
        rows.append(json.dumps(node, separators=(',', ':')))
    return Counter(rows)


def worker(action, root):
    from .native import api_load, apply_routes
    from .geometry import snapshot, native_audit, layout_snapshot
    root = Path(root)
    context = verify_context(root)
    bound = read_json(root/'replacement-binding.json')
    require(digest(bound['validation_context']) == bound['context_sha256'], 'Replacement context drift')
    preflight(root/'plan.json', bound['validation_context'], context['source'], root/(action+'-preflight.json'))
    plan = read_json(root/'plan.json')
    path = Path(context['board'])
    api, board = api_load(path)
    if action == 'replace-create':
        require(digest(path) == context['source_hashes'][path.name], 'Scratch is not the exact accepted baseline')
        before = snapshot(board, api)
        require(before == read_json(bound['validation_context'])['snapshot'], 'Read-only context/native geometry mismatch; STOP')
        audit = native_audit(board, api)
        partition = pad_partition(board)
        write_json(root/'before.json', before)
        write_json(root/'audit-before.json', audit)
        write_json(root/'pad-partition-before.json', partition)
        # <=30mm native plane windows; native exported fill and drill locations retained.
        write_json(root/'layout-before.json', layout_snapshot(board, api, plan['review_bounds']))
        objects = {t.m_Uuid.AsString(): t for t in board.GetTracks()}
        for u in plan['remove_tracks']:
            board.Remove(objects[u])
        expected = apply_routes(board, api, plan)
        write_json(root/'expected-added.json', expected)
        created = snapshot(board, api)
        write_json(root/'created-snapshot.json', created)
        preserved(before, created, plan, expected)
        require(native_audit(board, api) == audit, 'Non-route native fields changed; STOP')
        require(pad_partition(board) == partition, 'Native pad topology mismatch; STOP')
        verify_context(root)
        require(api.SaveBoard(str(path), board), 'Scratch replacement save failed; STOP')
        api, board = api_load(path)
        after = snapshot(board, api)
        write_json(root/'reloaded-snapshot.json', after)
    else:
        before = read_json(root/'before.json')
        expected = read_json(root/'expected-added.json')
        after = snapshot(board, api)
        write_json(root/'final-snapshot.json', after)
        write_json(root/'layout-final.json', layout_snapshot(board, api, plan['review_bounds']))
    result = preserved(before, after, plan, expected)
    require(native_audit(board, api) == read_json(root/'audit-before.json'), 'Non-route native preservation mismatch; STOP')
    require(pad_partition(board) == read_json(root/'pad-partition-before.json'), 'Native pad topology mismatch; STOP')
    # Independent source-vs-scratch serialized-object preservation, including models,
    # fields, locks, pad settings, zone definitions, board setup and unmodified routes.
    retained_source = serialized_retained(context['source'], plan['remove_tracks'])
    retained_after = serialized_retained(path, expected)
    if retained_source != retained_after:
        write_json(root/'serialization-mismatch.json', dict(
            missing=list((retained_source-retained_after).elements()),
            extra=list((retained_after-retained_source).elements())))
    require(retained_source == retained_after, 'Independent original-object preservation failed; STOP')
    result.update(full_serialized_retained_objects_equal=True, native_pad_partition_equal=True,
                  kicad=api.GetBuildVersion(), production_unchanged=True)
    write_json(root/(action+'-preservation.json'), result)
    verify_context(root)
    print(f'{action}: exact replacement/preservation/topology PASS; production unchanged')


def run(args):
    from .cli import native
    from .checks import run_check
    require(args.native_python.is_file() and args.kicad_cli.is_file(), 'KiCad executables missing')
    preflight(args.plan, args.validation_context, args.board,
              args.output_dir.parent/(args.output_dir.name+'-preapplication.json'))
    root = prepare_scratch(args.board, args.baseline_manifest, args.output_dir)
    shutil.copy2(args.plan, root/'plan.json')
    write_json(root/'replacement-binding.json', dict(validation_context=str(args.validation_context.resolve()),
                                                     context_sha256=digest(args.validation_context)))
    native(root, args.native_python, 'replace-create')
    drc = run_check(root, args.kicad_cli, 'drc')
    require(drc['errors'] == 0 and drc['parity'] == 0, 'Scratch replacement DRC/parity failed; inspect evidence')
    erc = run_check(root, args.kicad_cli, 'erc')
    require(erc['errors'] == 0, 'Scratch replacement ERC failed')
    native(root, args.native_python, 'replace-verify')
    summary = dict(drc=drc, erc=erc, preservation=read_json(root/'replace-verify-preservation.json'))
    write_json(root/'summary.json', summary)
    return summary
