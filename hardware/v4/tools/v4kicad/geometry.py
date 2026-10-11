"""Native geometry extracted from the proven Phase 4.7 geometry helper.

The caller supplies pcbnew explicitly; this module is import-safe without KiCad.
Lengths/positions use mm. Stable UUIDs identify original objects.
"""
from .safety import ToolError


def xy(vector):
    return [vector.x / 1e6, vector.y / 1e6]


def copper_layers(api):
    return [api.F_Cu, api.In1_Cu, api.In2_Cu, api.B_Cu]


def inventory_row(item, board, api):
    common = dict(uuid=item.m_Uuid.AsString(), net=item.GetNetname())
    # PCB_VIA inherits PCB_TRACK: dispatch on via first, before geometry access.
    if isinstance(item, api.PCB_VIA):
        return dict(common, kind='via', position=xy(item.GetPosition()),
                    drill=item.GetDrillValue() / 1e6,
                    copper_widths={board.GetLayerName(layer): item.GetWidth(layer) / 1e6
                                   for layer in copper_layers(api)})
    if hasattr(api, 'PCB_ARC') and isinstance(item, api.PCB_ARC):
        raise ToolError('Arc track encountered: this V4 snapshot schema supports straight tracks only; STOP and extend the shared native geometry implementation before proceeding')
    if isinstance(item, api.PCB_TRACK):
        return dict(common, kind='track', layer=board.GetLayerName(item.GetLayer()),
                    width=item.GetWidth() / 1e6,
                    start=xy(item.GetStart()), end=xy(item.GetEnd()))
    raise ToolError(f'Unsupported routed object type: {type(item).__name__}; STOP')


def polygons(poly):
    return [[xy(poly.COutline(i).CPoint(j))
             for j in range(poly.COutline(i).PointCount())]
            for i in range(poly.OutlineCount())]


def pad_row(pad, footprint, board, api):
    shapes = {}
    for layer in copper_layers(api):
        if pad.IsOnLayer(layer):
            poly = api.SHAPE_POLY_SET()
            pad.TransformShapeToPolygon(poly, layer, 0, 100, api.ERROR_OUTSIDE)
            shapes[board.GetLayerName(layer)] = polygons(poly)
    return dict(uuid=pad.m_Uuid.AsString(), ref=footprint.GetReference(),
                pin=pad.GetNumber(), net=pad.GetNetname(),
                position=xy(pad.GetPosition()), polygons=shapes,
                drill_size=xy(pad.GetDrillSize()), drill_shape=int(pad.GetDrillShape()))


def identify(items):
    result = {}
    for item in items:
        uid = item['uuid']
        if uid in result:
            raise ToolError(f'Duplicate object UUID {uid}; STOP')
        result[uid] = item
    return result


def snapshot(board, api):
    routed = [inventory_row(item, board, api) for item in board.GetTracks()]
    footprints, pads, zones = [], [], []
    for footprint in board.GetFootprints():
        footprints.append(dict(uuid=footprint.m_Uuid.AsString(),
                               ref=footprint.GetReference(), value=footprint.GetValue(),
                               position=xy(footprint.GetPosition()),
                               angle=footprint.GetOrientationDegrees()))
        pads.extend(pad_row(pad, footprint, board, api) for pad in footprint.Pads())
    for zone in board.Zones():
        if not zone.GetIsRuleArea():
            zones.append(dict(uuid=zone.m_Uuid.AsString(), net=zone.GetNetname(),
                              layers={board.GetLayerName(layer): polygons(zone.GetFilledPolysList(layer))
                                      for layer in zone.GetLayerSet().Seq()}))
    return dict(tracks=identify(r for r in routed if r['kind'] == 'track'),
                vias=identify(r for r in routed if r['kind'] == 'via'),
                footprints=identify(footprints), pads=identify(pads), zones=identify(zones))


def preservation(before, after, track_change=None):
    """Allow one declared layer change and added routed objects, nothing else.

    Zone fill may change after refill; original zone identities/nets/layers remain.
    Explicitly compare added geometry to the supplied plan separately.
    """
    if track_change and track_change[0] not in before['tracks']:
        raise ToolError(f'Unknown original track UUID: {track_change[0]}; STOP')
    for section in ['footprints', 'pads']:
        if before[section] != after[section]:
            raise ToolError(f'Unexpected {section} change; STOP')
    for section in ['tracks', 'vias']:
        for uid, item in before[section].items():
            expected = dict(item)
            if section == 'tracks' and track_change and uid == track_change[0]:
                if expected['layer'] != track_change[1]:
                    raise ToolError(f'Track {uid} not on expected source layer; STOP')
                expected['layer'] = track_change[2]
            if after[section].get(uid) != expected:
                raise ToolError(f'Unexpected original {section} change: {uid}; STOP')
    if set(before['zones']) != set(after['zones']):
        raise ToolError('Zone identities changed; STOP')
    for uid, zone in before['zones'].items():
        new = after['zones'][uid]
        if zone['net'] != new['net'] or set(zone['layers']) != set(new['layers']):
            raise ToolError(f'Zone net/layers changed: {uid}; STOP')
    return dict(original_geometry_preserved=True,
                added_tracks=len(after['tracks']) - len(before['tracks']),
                added_vias=len(after['vias']) - len(before['vias']))
