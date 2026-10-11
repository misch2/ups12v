"""Isolated worker implementation; no native imports or work at module import."""
from pathlib import Path
import math
from .geometry import snapshot, preservation, inventory_row
from .safety import digest, read_json, require, verify_context, write_json


def api_load(board_path):
    import pcbnew as api
    require(api.GetBuildVersion().startswith('10.'), 'KiCad 10 native Python is required; STOP')
    board = api.LoadBoard(str(board_path))
    require(board is not None, f'Native LoadBoard failed: {board_path}; STOP')
    require(board.GetCopperLayerCount() == 4, 'This V4 toolkit requires the four-layer V4 stack; STOP')
    return api, board


def vec(api, point):
    return api.VECTOR2I(*(round(x * 1e6) for x in point))


def mm(value):
    return round(value * 1e6) / 1e6


def apply_routes(board, api, plan):
    require('failure' in plan and plan['failure'] is None, 'Route plan is failed or lacks status; STOP')
    require(isinstance(plan.get('tracks'), list) and isinstance(plan.get('vias'), list),
            'Plan requires explicit tracks/vias lists; STOP')
    expected = {}
    for net, layer, width, x1, y1, x2, y2 in plan['tracks']:
        require(width > 0 and [x1, y1] != [x2, y2], 'Invalid route track geometry; STOP')
        layer_id = board.GetLayerID(layer)
        require(layer_id in [api.F_Cu, api.In1_Cu, api.In2_Cu, api.B_Cu], 'Invalid copper layer; STOP')
        found = board.FindNet(net)
        require(found is not None and found.GetNetCode() > 0, f'Unknown route net {net}; STOP')
        track = api.PCB_TRACK(board)
        track.SetStart(vec(api, [x1, y1])); track.SetEnd(vec(api, [x2, y2]))
        track.SetWidth(round(width * 1e6)); track.SetLayer(layer_id)
        track.SetNetCode(found.GetNetCode()); board.Add(track)
        uid = track.m_Uuid.AsString()
        expected[uid] = dict(uuid=uid, net=net, kind='track', layer=layer,
                             width=mm(width), start=[mm(x1), mm(y1)], end=[mm(x2), mm(y2)])
    for net, x, y, diameter, drill in plan['vias']:
        require(0 < drill < diameter, 'Invalid through-via copper/drill size; STOP')
        found = board.FindNet(net)
        require(found is not None and found.GetNetCode() > 0, f'Unknown via net {net}; STOP')
        via = api.PCB_VIA(board); via.SetPosition(vec(api, [x, y]))
        via.SetViaType(api.VIATYPE_THROUGH); via.SetLayerPair(api.F_Cu, api.B_Cu)
        for layer in [api.F_Cu, api.In1_Cu, api.In2_Cu, api.B_Cu]:
            via.SetWidth(layer, round(diameter * 1e6))
        via.SetDrill(round(drill * 1e6)); via.SetNetCode(found.GetNetCode()); board.Add(via)
        uid = via.m_Uuid.AsString()
        expected[uid] = dict(uuid=uid, net=net, kind='via', position=[mm(x), mm(y)], drill=mm(drill),
                             copper_widths={board.GetLayerName(l): mm(diameter)
                                            for l in [api.F_Cu, api.In1_Cu, api.In2_Cu, api.B_Cu]})
    return expected


def verify_added(before, after, expected):
    added = {uid: item for section in ['tracks', 'vias']
             for uid, item in after[section].items() if uid not in before[section]}
    require(added == expected, 'Added native copper differs from the declared plan; STOP')


def worker(action, root):
    root = Path(root).resolve(strict=True)
    context = verify_context(root)
    path = Path(context['board'])
    api, board = api_load(path)
    before = snapshot(board, api)
    if action == 'snapshot':
        require(digest(path) == context['source_hashes'][path.name], 'Smoke copy differs from accepted source; STOP')
        write_json(root / 'snapshot.json', before)
        verify_context(root)
        print('Read-only native snapshot complete; no save')
        return
    request = read_json(root / 'request.json')
    change = (request['track_uuid'], request['from_layer'], request['to_layer'])
    if action == 'apply':
        require(digest(path) == context['source_hashes'][path.name], 'Initial scratch hash differs; STOP')
        require(change[0] in before['tracks'], 'Requested UUID is not an ordinary track; STOP')
        require(before['tracks'][change[0]]['layer'] == change[1], 'Source layer mismatch; STOP')
        target_layer = board.GetLayerID(change[2])
        require(target_layer in [api.F_Cu, api.In1_Cu, api.In2_Cu, api.B_Cu], 'Invalid destination copper layer; STOP')
        target = next(t for t in board.GetTracks() if t.m_Uuid.AsString() == change[0])
        target.SetLayer(target_layer)
        plan = read_json(root / 'plan.json')
        expected = apply_routes(board, api, plan)
        preservation(before, snapshot(board, api), change)
        # Recheck hashes and lock just before the only native write.
        verify_context(root)
        require(api.SaveBoard(str(path), board), 'Native scratch SaveBoard failed; STOP')
        api, reloaded = api_load(path)
        after = snapshot(reloaded, api)
        result = preservation(before, after, change)
        verify_added(before, after, expected)
        write_json(root / 'before.json', before)
        write_json(root / 'expected-added.json', expected)
        result.update(kicad=api.GetBuildVersion(), change=change,
                      prog_length_mm=sum(math.dist(t[3:5], t[5:7]) for t in plan['tracks'] if t[0] == 'PROG'))
        write_json(root / 'build-summary.json', result)
    elif action == 'verify':
        original = read_json(root / 'before.json')
        expected = read_json(root / 'expected-added.json')
        result = preservation(original, before, change)
        verify_added(original, before, expected)
        write_json(root / 'final-snapshot.json', before)
        write_json(root / 'preservation.json', result)
    else:
        raise ValueError(action)
    verify_context(root)
    print(f'Native {action} complete; saved production hashes unchanged')
