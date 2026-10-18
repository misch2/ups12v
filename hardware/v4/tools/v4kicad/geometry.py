"""Native geometry extracted from the proven Phase 4.7 geometry helper.

The caller supplies pcbnew explicitly; this module is import-safe without KiCad.
Lengths/positions use mm. Stable UUIDs identify original objects.
"""
from .safety import ToolError
import math


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
        needed=['GetMid','GetLength','TransformShapeToPolygon']
        if not all(hasattr(item,n) for n in needed):
            raise ToolError('Arc native APIs missing; no chord substitution')
        layer=item.GetLayer();poly=api.SHAPE_POLY_SET()
        item.TransformShapeToPolygon(poly,layer,0,100,api.ERROR_OUTSIDE)
        row=dict(common,kind='track',geometry='arc',layer=board.GetLayerName(layer),
                 width=item.GetWidth()/1e6,start=xy(item.GetStart()),mid=xy(item.GetMid()),
                 end=xy(item.GetEnd()),native_length_mm=item.GetLength()/1e6,
                 copper_polygons=polygons(poly),polygon_error_bound_mm=.0001)
        from .track_geometry import track_length
        track_length(row)
        if not row['copper_polygons']:raise ToolError('Native arc copper export is empty')
        return row
    if isinstance(item, api.PCB_TRACK):
        return dict(common, kind='track', layer=board.GetLayerName(item.GetLayer()),
                    width=item.GetWidth() / 1e6,
                    start=xy(item.GetStart()), end=xy(item.GetEnd()))
    raise ToolError(f'Unsupported routed object type: {type(item).__name__}; STOP')


def routed_diagnostics(board, api):
    """Read-only exact-unit/padstack evidence, separate from stable snapshots."""
    rows=[]
    for item in board.GetTracks():
        row=inventory_row(item,board,api)
        row['native_class']=type(item).__name__
        if isinstance(item,api.PCB_VIA):
            p=item.GetPosition();stack=item.Padstack()
            row.update(position_nm=[p.x,p.y],drill_nm=item.GetDrillValue(),
                via_type=int(item.GetViaType()),
                layer_pair=[board.GetLayerName(item.TopLayer()),board.GetLayerName(item.BottomLayer())],
                padstack_mode=int(stack.Mode()),drill_shape=int(stack.DrillShape()),
                remove_unconnected=item.GetRemoveUnconnected(),keep_start_end=item.GetKeepStartEnd(),
                padstack_layers={board.GetLayerName(l):dict(width_nm=item.GetWidth(l),
                    size_nm=[stack.Size(l).x,stack.Size(l).y],shape=int(stack.Shape(l)))
                    for l in copper_layers(api)})
        else:
            a,b=item.GetStart(),item.GetEnd()
            row.update(start_nm=[a.x,a.y],end_nm=[b.x,b.y],width_nm=item.GetWidth())
            if hasattr(api,'PCB_ARC') and isinstance(item,api.PCB_ARC):
                m=item.GetMid();row['mid_nm']=[m.x,m.y]
        rows.append(row)
    return dict(kicad=api.GetBuildVersion(),items=identify(rows),
        enums=dict(through_via=int(api.VIATYPE_THROUGH),circular_pad=int(api.PAD_SHAPE_CIRCLE)))


def routing_context(board,api,path,current):
    """Native read-only pad clearance/drill orientation and fixed-copper export."""
    from .plan_validation import profile,reserved_regions
    from .safety import digest
    pads={};graphics=[]
    for fp in board.GetFootprints():
        for p in fp.Pads():
            pads[p.m_Uuid.AsString()]=dict(orientation=p.GetOrientationDegrees(),
                clearances={board.GetLayerName(l):(p.GetOwnClearance(l) or 0)/1e6
                    for l in copper_layers(api) if p.IsOnLayer(l)})
        for item in fp.GraphicalItems():
            if item.GetLayer() not in copper_layers(api):continue
            poly=api.SHAPE_POLY_SET()
            item.TransformShapeToPolygon(poly,item.GetLayer(),0,100,api.ERROR_OUTSIDE)
            graphics.append(dict(uuid=item.m_Uuid.AsString(),ref=fp.GetReference(),
                layer=board.GetLayerName(item.GetLayer()),polygons=polygons(poly)))
    for item in board.GetDrawings():
        if item.GetLayer() not in copper_layers(api):continue
        poly=api.SHAPE_POLY_SET()
        item.TransformShapeToPolygon(poly,item.GetLayer(),0,100,api.ERROR_OUTSIDE)
        graphics.append(dict(uuid=item.m_Uuid.AsString(),ref='@board',
            layer=board.GetLayerName(item.GetLayer()),polygons=polygons(poly)))
    audit=native_audit(board,api)
    return dict(board_sha256=digest(path),snapshot=current,profile=profile(path),pads=pads,
        copper_graphics=graphics,zones=audit['zones'],board_outline=layout_snapshot(board,api)['board_outline'],
        reservations=reserved_regions(),pad_polygon_error_bound_nm=100,pad_polygon_error_side='outside')


def polygons(poly):
    return [[xy(poly.COutline(i).CPoint(j))
             for j in range(poly.COutline(i).PointCount())]
            for i in range(poly.OutlineCount())]


def polygons_with_holes(poly):
    """Export the actual native outline/hole topology, without flattening holes."""
    def chain(c):
        return [xy(c.CPoint(j)) for j in range(c.PointCount())]
    return [dict(outline=chain(poly.COutline(i)),
                 holes=[chain(poly.CHole(i, j)) for j in range(poly.HoleCount(i))])
            for i in range(poly.OutlineCount())]


def layout_snapshot(board, api, review_bounds=None):
    outline = api.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise ToolError('Native board outline unavailable; STOP')
    courtyards = {}
    for fp in board.GetFootprints():
        fp.BuildCourtyardCaches()
        courtyards[fp.GetReference()] = polygons_with_holes(fp.GetCourtyard(api.F_CrtYd))
    fills = {}
    for zone in board.Zones():
        if not zone.GetIsRuleArea():
            fills[zone.m_Uuid.AsString()] = dict(net=zone.GetNetname(), layers={
                board.GetLayerName(layer): polygons_with_holes(zone.GetFilledPolysList(layer))
                for layer in zone.GetLayerSet().Seq()})
    result = dict(board_outline=polygons_with_holes(outline), courtyards=courtyards, fills=fills)
    if review_bounds:
        x0,y0,x1,y1 = review_bounds
        if not (0 < x1-x0 <= 30 and 0 < y1-y0 <= 30):
            raise ToolError('Plane-sampling bounds must be positive and at most30mm per axis; STOP')
        step=.1; nx=round((x1-x0)/step)+1; ny=round((y1-y0)/step)+1
        plane = next((z for z in board.Zones() if not z.GetIsRuleArea()
                      and z.GetNetname()=='PGND' and z.IsOnLayer(api.In1_Cu)),None)
        if plane is None:raise ToolError('PGND In1 plane unavailable; STOP')
        result['plane_samples'] = dict(bounds=review_bounds,step=step,rows=[
            ''.join('1' if plane.HitTestFilledArea(api.In1_Cu,api.VECTOR2I(round((x0+x*step)*1e6),round((y0+y*step)*1e6)))
                    else '0' for x in range(nx)) for y in range(ny)])
        result['via_plane_samples'] = [dict(uuid=v.m_Uuid.AsString(),net=v.GetNetname(),position=xy(v.GetPosition()),
            center=plane.HitTestFilledArea(api.In1_Cu,v.GetPosition()),
            ring=[plane.HitTestFilledArea(api.In1_Cu,api.VECTOR2I(v.GetPosition().x+dx,v.GetPosition().y+dy))
                  for dx,dy in [(400000,0),(-400000,0),(0,400000),(0,-400000)]])
            for v in board.GetTracks() if isinstance(v,api.PCB_VIA)
            and x0<=v.GetPosition().x/1e6<=x1 and y0<=v.GetPosition().y/1e6<=y1]
    return result


def verify_placement_geometry(before, placed, placements):
    """Only the declared four footprint rigid transforms may alter exported geometry."""
    allowed = {'L2', 'C37', 'C33', 'C45'}
    if set(placements) != allowed:
        raise ToolError('Exactly L2/C37/C33/C45 placements required; STOP')
    if set(before['footprints']) != set(placed['footprints']) or set(before['pads']) != set(placed['pads']):
        raise ToolError('Placement changed object identities; STOP')
    originals = {f['ref']: f for f in before['footprints'].values()}
    def transform(point, ref):
        old = originals[ref]; x,y,angle = placements[ref]
        rad = math.radians(angle-old['angle']); c,s = math.cos(rad), math.sin(rad)
        u,v = point[0]-old['position'][0], point[1]-old['position'][1]
        return [x+c*u+s*v, y-s*u+c*v]
    def close(a,b): return math.dist(a,b) < .0003
    for uid, fp in before['footprints'].items():
        after = placed['footprints'][uid]; ref = fp['ref']
        expected = dict(fp)
        if ref in allowed:
            expected.update(position=placements[ref][:2], angle=placements[ref][2])
        if after != expected:
            raise ToolError(f'Unexpected footprint placement: {ref}; STOP')
    for uid, pad in before['pads'].items():
        after = placed['pads'][uid]; ref = pad['ref']
        if ref not in allowed:
            if after != pad: raise ToolError(f'Unapproved pad change: {ref}; STOP')
            continue
        for key in pad:
            if key not in ['position','polygons'] and pad[key] != after[key]:
                raise ToolError(f'Placement changed pad {ref} metadata: {key}; STOP')
        if not close(transform(pad['position'],ref),after['position']) or set(pad['polygons']) != set(after['polygons']):
            raise ToolError(f'Incorrect placed pad: {ref}; STOP')
        for layer, polys in pad['polygons'].items():
            expected_points = [transform(p,ref) for poly in polys for p in poly]
            actual = [p for poly in after['polygons'][layer] for p in poly]
            if len(expected_points) != len(actual) or any(not any(close(p,q) for q in actual) for p in expected_points):
                raise ToolError(f'Placement changed copper shape: {ref}; STOP')
    for section in ['tracks','vias','zones']:
        if before[section] != placed[section]:
            raise ToolError(f'Placement changed existing {section}; STOP')
    return dict(only_four_rigid_placements=True, references=sorted(allowed))


def native_polygon_artwork(board, api):
    """Exact polygon graphics, dispatched by concrete native shape before access."""
    result={}
    for fp in board.GetFootprints():
        for item in fp.GraphicalItems():
            if isinstance(item,api.PCB_SHAPE) and item.GetShape()==api.SHAPE_T_POLY:
                result.setdefault(fp.GetReference(),{})[item.m_Uuid.AsString()]=polygons_with_holes(item.GetPolyShape())
    return result


def native_audit(board, api):
    """Read-only preservation metadata for zones, RF keepouts and non-route artwork."""
    def item_row(item):
        row=dict(uuid=item.m_Uuid.AsString(),kind=item.GetClass(),layer=board.GetLayerName(item.GetLayer()))
        for name in ['GetPosition','GetStart','GetEnd','GetTextSize']:
            if hasattr(item,name):row[name]=xy(getattr(item,name)())
        for name in ['GetWidth','GetShape','GetText','GetTextThickness']:
            if hasattr(item,name):
                value=getattr(item,name)();row[name]=int(value) if name=='GetShape' else value
        if hasattr(item,'GetTextAngle'):row['text_angle']=item.GetTextAngle().AsDegrees()
        return row
    zone_rows=[]
    for z in board.Zones():
        row=dict(uuid=z.m_Uuid.AsString(),net=z.GetNetname(),rule_area=z.GetIsRuleArea(),
                 layers=[board.GetLayerName(l) for l in z.GetLayerSet().Seq()],outline=polygons_with_holes(z.Outline()))
        for name in ['GetDoNotAllowTracks','GetDoNotAllowVias','GetDoNotAllowPads','GetDoNotAllowZoneFills',
                     'GetDoNotAllowFootprints','GetAssignedPriority','GetThermalReliefGap',
                     'GetThermalReliefSpokeWidth','GetPadConnection','GetMinThickness']:
            if not hasattr(z,name):raise ToolError(f'Native zone audit API missing: {name}; STOP')
            value=getattr(z,name)();row[name]=int(value)
        zone_rows.append(row)
    fp_graphics={}
    for fp in board.GetFootprints():
        items=list(fp.GraphicalItems())+[fp.Reference(),fp.Value()]
        fp_graphics[fp.GetReference()]={i.m_Uuid.AsString():item_row(i) for i in items}
    return dict(zones=identify(zone_rows),drawings={i.m_Uuid.AsString():item_row(i) for i in board.GetDrawings()},
                footprint_graphics=fp_graphics)


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
