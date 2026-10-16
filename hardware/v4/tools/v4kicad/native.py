"""Isolated worker implementation; no native imports or work at module import."""
from pathlib import Path
import math
from .geometry import snapshot, preservation, inventory_row, layout_snapshot, verify_placement_geometry, native_audit, routed_diagnostics
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


def verify_added(before, after, expected, diagnostics_path=None):
    added = {uid: item for section in ['tracks', 'vias']
             for uid, item in after[section].items() if uid not in before[section]}
    if added != expected and diagnostics_path is not None:
        # Keep exact observations before failing. Never substitute/rewrite geometry.
        write_json(diagnostics_path, dict(expected=expected, actual=added,
            missing=sorted(set(expected)-set(added)), extra=sorted(set(added)-set(expected)),
            changed=sorted(u for u in set(expected)&set(added) if expected[u]!=added[u])))
    require(added == expected, 'Added native copper differs from the declared plan; STOP')


def worker(action, root):
    root = Path(root).resolve(strict=True)
    context = verify_context(root)
    path = Path(context['board'])
    api, board = api_load(path)
    before = snapshot(board, api)
    if action == 'audit':
        require(not (root/'native-audit.json').exists(),'Audit artifact already exists; STOP')
        write_json(root/'native-audit.json',native_audit(board,api))
        verify_context(root)
        print('Read-only native zone/artwork audit complete; no save')
        return
    if action == 'probe':
        types = {'polygon': api.SHAPE_POLY_SET, 'board': type(board),
                 'footprint': api.FOOTPRINT, 'zone': api.ZONE}
        names = {'polygon': ['HoleCount', 'CHole', 'Contains', 'Area'],
                 'board': ['GetBoardPolygonOutlines', 'GetDesignSettings'],
                 'footprint': ['GetCourtyard', 'BuildCourtyardCaches', 'SetPosition', 'SetOrientationDegrees'],
                 'zone': ['GetFilledPolysList', 'HitTestFilledArea', 'GetMinThickness', 'GetLocalClearance',
                          'Outline','GetDoNotAllowTracks','GetDoNotAllowVias','GetDoNotAllowPads',
                          'GetDoNotAllowCopperPour','GetDoNotAllowFootprints','GetAssignedPriority',
                          'GetThermalReliefGap','GetThermalReliefSpokeWidth','GetPadConnection']}
        write_json(root / 'api-probe.json', {k: {n: getattr(t, n).__doc__ if hasattr(t,n) else None
                                                for n in names[k]} for k,t in types.items()})
        write_json(root / 'snapshot.json', before)
        verify_context(root)
        print('Read-only native API probe complete; no save')
        return
    if action == 'snapshot':
        require(digest(path) == context['source_hashes'][path.name], 'Smoke copy differs from accepted source; STOP')
        write_json(root / 'snapshot.json', before)
        review=read_json(root/'review-request.json') if (root/'review-request.json').exists() else {}
        if review.get('route_diagnostics'):
            write_json(root/'routed-diagnostics.json',routed_diagnostics(board,api))
        bounds = review.get('review_bounds')
        write_json(root / 'layout.json', layout_snapshot(board, api,bounds))
        verify_context(root)
        print('Read-only native snapshot complete; no save')
        return
    request = read_json(root / 'request.json')
    change = ((request['track_uuid'], request['from_layer'], request['to_layer'])
              if request['track_uuid'] is not None else None)
    if action == 'apply':
        require(digest(path) == context['source_hashes'][path.name], 'Initial scratch hash differs; STOP')
        if change:
            require(change[0] in before['tracks'], 'Requested UUID is not an ordinary track; STOP')
            require(before['tracks'][change[0]]['layer'] == change[1], 'Source layer mismatch; STOP')
            target_layer = board.GetLayerID(change[2])
            require(target_layer in [api.F_Cu, api.In1_Cu, api.In2_Cu, api.B_Cu], 'Invalid destination copper layer; STOP')
            target = next(t for t in board.GetTracks() if t.m_Uuid.AsString() == change[0])
            target.SetLayer(target_layer)
        plan = read_json(root / 'plan.json')
        placements = plan.get('placements', {})
        if placements:
            require(request.get('allow_u3_placement') and change is None,
                    'Scratch placement not explicitly enabled or original copper change requested; STOP')
            require(set(placements) == {'L2','C37','C33','C45'}, 'Unapproved placement references; STOP')
            require(all(n in {'SYS','MAIN_3V3','PGND','/SW_NORMAL','/BST_NORMAL','/MAIN_FB','/NORMAL_EN','/NORMAL_SS'}
                        for rows in [plan['tracks'],plan['vias']] for n,*_ in rows), 'Non-U3 routing in placement plan; STOP')
            write_json(root / 'original.json', before)
            for fp in board.GetFootprints():
                if fp.GetReference() in placements:
                    x,y,angle = placements[fp.GetReference()]
                    fp.SetOrientationDegrees(angle)
                    fp.SetPosition(vec(api,[x,y]))
            placed = snapshot(board,api)
            write_json(root / 'placement-preservation.json', verify_placement_geometry(before,placed,placements))
            before = placed
            write_json(root / 'layout-placed.json', layout_snapshot(board,api))
        expected = apply_routes(board, api, plan)
        write_json(root / 'expected-added.json', expected)
        created = snapshot(board, api)
        write_json(root / 'created-snapshot.json', created)
        preservation(before, created, change)
        verify_added(before, created, expected, root / 'created-mismatch.json')
        # Recheck hashes and lock just before the only native write.
        verify_context(root)
        require(api.SaveBoard(str(path), board), 'Native scratch SaveBoard failed; STOP')
        api, reloaded = api_load(path)
        after = snapshot(reloaded, api)
        write_json(root / 'reloaded-snapshot.json', after)
        result = preservation(before, after, change)
        verify_added(before, after, expected, root / 'reloaded-mismatch.json')
        write_json(root / 'before.json', before)
        write_json(root / 'placed-snapshot.json', before)
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
        bounds = read_json(root / 'plan.json').get('review_bounds')
        write_json(root / 'layout-final.json', layout_snapshot(board,api,bounds))
        write_json(root / 'preservation.json', result)
    else:
        raise ValueError(action)
    verify_context(root)
    print(f'Native {action} complete; saved production hashes unchanged')
