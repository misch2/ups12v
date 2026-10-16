"""Bounded owner-approved IPC installation; import-safe, no external board overwrite.

Parent supervises one worker per action. preflight must precede apply in a fresh
evidence directory. Geometry verification remains in the shared native toolkit.
"""
from pathlib import Path
import argparse
import copy
import json
import sys
import uuid
from collections import Counter
from .safety import digest, read_json, require, run_monitored, verify_hashes, write_json

SECTIONS = ['footprints', 'pads', 'tracks', 'vias', 'zones', 'shapes', 'texts']
CHANGE = '01ab1eb5-ab75-462d-9e54-2d6eab529481'


def check_add_only(plan, allowed):
    require(plan.get('failure', 'missing') is None, 'Failed/missing plan status; STOP')
    require(bool(allowed), 'Explicit allowed nets required; STOP')
    require(all(row[0] in allowed for key in ['tracks', 'vias'] for row in plan[key]),
            'Plan contains a net outside approved batch; STOP')


def comparable(value, path=()):
    """Only runtime board-parent/custom-primitive IDs and inactive anchors differ on reload."""
    if isinstance(value, list):
        return [comparable(v, path + (str(i),)) for i, v in enumerate(value)]
    if isinstance(value, dict):
        return {k: comparable(v, path + (k,)) for k, v in value.items()
                if not (k == 'parent' and len(path) == 1)
                and not (k == 'id' and 'customShapes' in path)
                and not (k == 'customAnchorShape' and value.get('shape') == 'PSS_CIRCLE')}
    return value


def capture(board):
    from google.protobuf.json_format import MessageToDict
    getters = ['get_footprints', 'get_pads', 'get_tracks', 'get_vias', 'get_zones', 'get_shapes', 'get_text']
    return {section: {i.id.value: MessageToDict(i.proto) for i in getattr(board, getter)()}
            for section, getter in zip(SECTIONS, getters)}


def verify_created(items, plan, board):
    from kipy.board_types import Track, Via
    from kipy.proto.board.board_types_pb2 import ViaType
    tracks, vias = [], []
    for item in items:
        if isinstance(item, Via):
            require(item.type == ViaType.VT_THROUGH, 'Non-through created via; STOP')
            vias.append((item.net.name, item.position.x, item.position.y, item.diameter, item.drill_diameter))
        else:
            require(isinstance(item, Track), 'Unexpected created object type; STOP')
            tracks.append((item.net.name, item.layer, item.width, item.start.x, item.start.y, item.end.x, item.end.y))
    expected_tracks = [(n,board.get_layer_by_name(l),*[round(v*1e6) for v in values])
                       for n,l,*values in plan['tracks']]
    expected_vias = [(n,*[round(v*1e6) for v in values]) for n,*values in plan['vias']]
    require(Counter(tracks) == Counter(expected_tracks) and Counter(vias) == Counter(expected_vias),
            'Created geometry differs from exact plan; STOP')


def worker(action, root):
    context = read_json(root / 'install-context.json')
    source = Path(context['source'])
    sys.path.insert(0, str(source.parent / '.konnect/native-ipc'))
    from kipy import KiCad
    from kipy.board_types import Track, Via
    from kipy.geometry import Vector2
    k = KiCad(socket_path=context['socket'], client_name='Approved exact Phase4.7 production batch')
    require(k.get_version().major == 10, 'KiCad 10 required; STOP')
    b = k.get_board()
    require(b.name == source.name and Path(b.document.project.path).resolve() == source.parent,
            'Live document identity mismatch; STOP')
    baseline = read_json(context['baseline'])
    verify_hashes(source.parent, baseline['hashes'])
    before = capture(b)
    if action == 'preflight':
        for section in SECTIONS:
            require(comparable(before[section]) == comparable(baseline[section]),
                    f'Live baseline divergence in {section}; STOP')
        require(all(len(before[s]) == len(baseline[s]) for s in SECTIONS), 'Baseline counts differ; STOP')
        write_json(root / 'live-before.json', before)
        write_json(root / 'preflight.json', dict(identity=True, saved_hashes_match=True,
                   live_baseline_matches=True, owner_confirmed_saved=True))
        print('Read-only IPC preflight PASS')
        return
    require(action == 'apply', 'Unknown action')
    require(before == read_json(root / 'live-before.json'), 'Live state changed after preflight; STOP')
    plan = read_json(context['plan'])
    add_only = context.get('add_only', False)
    if add_only:
        check_add_only(plan, context['allowed_nets'])
        require(bool(plan['tracks']) or bool(plan['vias']), 'Empty install; STOP')
    else:
        require(plan['failure'] is None and len(plan['tracks']) == 47 and len(plan['vias']) == 3,
                'Unexpected approved plan; STOP')
    tracks = {t.id.value: t for t in b.get_tracks()}
    target = tracks[CHANGE] if not add_only else None
    if target:
        require(target.layer == b.get_layer_by_name('F.Cu') and target.net.name == 'BATTERY', 'Layer/net mismatch')
    nets = {n.name: n for n in b.get_nets()}
    template = next(v for v in b.get_vias() if v.diameter == 500000 and v.drill_diameter == 300000)
    adds = []
    for net, layer, width, x1, y1, x2, y2 in plan['tracks']:
        t = Track(); t.proto.id.value = str(uuid.uuid4()); t.locked = False
        t.net = nets[net]; t.layer = b.get_layer_by_name(layer); t.width = round(width * 1e6)
        t.start = Vector2.from_xy(round(x1*1e6), round(y1*1e6))
        t.end = Vector2.from_xy(round(x2*1e6), round(y2*1e6)); adds.append(t)
    for net, x, y, diameter, drill in plan['vias']:
        v = Via(template.proto); v.proto.id.value = str(uuid.uuid4()); v.proto.ClearField('parent')
        v.locked = False; v.net = nets[net]
        v.position = Vector2.from_xy(round(x*1e6), round(y*1e6))
        v.diameter = round(diameter*1e6); v.drill_diameter = round(drill*1e6); adds.append(v)
    expected = copy.deepcopy(before)
    if target:
        expected['tracks'][CHANGE]['layer'] = 'BL_In2_Cu'
    verify_hashes(source.parent, baseline['hashes'])
    commit = b.begin_commit()
    write_json(root / 'commit-id.json', dict(value=commit.id.value))
    # On any failure, leave diagnostics and editor untouched for owner recovery.
    if target:
        target.layer = b.get_layer_by_name('In2.Cu')
        updated = b.update_items([target]); require(len(updated) == 1, 'Partial original update; STOP')
    created = b.create_items(adds); require(len(created) == len(adds), 'Partial route creation; STOP')
    verify_created(created, plan, b)
    write_json(root / 'created-ids.json', [i.id.value for i in created])
    # KiCad stages new objects until EndCommit; getters cannot verify counts earlier.
    b.push_commit(commit, 'Approved Phase4.7 local add-only batch' if add_only else
                  'Approved Phase4.7 exact shorter PROG and associated local routes')
    write_json(root / 'commit-pushed.json', dict(pushed=True))
    after = capture(b)
    for section in SECTIONS:
        retained = {uid: item for uid, item in after[section].items() if uid in before[section]}
        require(retained == expected[section], f'Unexpected retained {section} change; STOP')
    require(len(after['tracks']) == len(before['tracks']) + len(plan['tracks']) and
            len(after['vias']) == len(before['vias']) + len(plan['vias']), 'Final counts mismatch; STOP')
    created_ids = {i.id.value for i in created}
    verify_created([i for i in [*b.get_tracks(), *b.get_vias()] if i.id.value in created_ids], plan, b)
    write_json(root / 'live-applied.json', after)
    b.refill_zones(block=True)
    filled = capture(b)
    require(all(filled[s] == after[s] for s in SECTIONS if s != 'zones'), 'Refill changed non-zone items; STOP')
    b.save()  # The owning editor saves its own live document; no external overwrite.
    require(all(digest(source.parent / n) == h for n,h in baseline['hashes'].items() if n != source.name),
            'Schematic/project drift during save; STOP')
    require(capture(b) == filled, 'Live state changed during save; STOP')
    write_json(root / 'live-final.json', filled)
    write_json(root / 'installed-manifest.json', dict(hashes={n:digest(source.parent/n) for n in baseline['hashes']}))
    print('IPC install/refill/editor-save complete; native readback and production checks still required')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['preflight', 'apply'])
    p.add_argument('--board', type=Path, required=True)
    p.add_argument('--baseline-manifest', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--socket', required=True)
    p.add_argument('--worker', action='store_true')
    p.add_argument('--add-only', action='store_true')
    p.add_argument('--allowed-nets', nargs='+', default=[])
    a = p.parse_args(); root = a.output_dir.resolve(); board = a.board.resolve(strict=True)
    if a.worker:
        worker(a.action, root); return
    if a.action == 'preflight':
        require(not root.exists(), 'Fresh evidence directory required; STOP')
        baseline = a.baseline_manifest.resolve(strict=True); plan = a.plan.resolve(strict=True)
        verify_hashes(board.parent, read_json(baseline)['hashes'])
        root.mkdir(parents=True)
        require(board.parent != root and board.parent not in root.parents, 'Evidence overlaps production; STOP')
        (root / 'accepted-before.kicad_pcb').write_bytes(board.read_bytes())
        write_json(root / 'install-context.json', dict(source=str(board), baseline=str(baseline),
                   plan=str(plan), plan_hash=digest(plan), socket=a.socket,
                   add_only=a.add_only, allowed_nets=a.allowed_nets))
    context = read_json(root / 'install-context.json')
    require(str(board) == context['source'] and str(a.plan.resolve()) == context['plan']
            and digest(a.plan) == context['plan_hash'] and a.socket == context['socket']
            and a.add_only == context.get('add_only', False)
            and a.allowed_nets == context.get('allowed_nets', []), 'Request drift; STOP')
    require(not (root / (a.action + '.log')).exists(), 'Action already attempted; STOP')
    result = run_monitored([sys.executable, '-B', '-m', 'v4kicad.ipc_install', *sys.argv[1:], '--worker'],
                           root / (a.action + '.log'))
    print(result['stdout'].strip())


if __name__ == '__main__':
    main()
