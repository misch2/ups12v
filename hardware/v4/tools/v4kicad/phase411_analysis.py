"""Bounded read-only Phase 4.11 analysis of already-exported native snapshots.

This module never opens KiCad or parses serialized CAD.  It consumes the
toolkit's snapshot/layout JSON and emits measurements with their limits
explicitly preserved for the engineering review.
"""
from collections import defaultdict
import math

from .usb_review import _connect_pad_layers, _graph, _node, _shortest, LAYERS
from .track_geometry import track_length,require_straight


USB_NETS = ("USB_DP", "USB_DN", "/USB_MCU_DP", "/USB_MCU_DN")


def _point(p):
    return (float(p[0]), float(p[1]))


def _distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _segment_distance(a, b, c, d):
    from .usb_review import _segment_distance as native_distance, _point as native_point
    return native_distance(*(native_point(p) for p in [a,b,c,d]))


def _track_length(track):
    return track_length(track)


def net_metrics(snapshot, nets):
    """Return routed width/layer/via cross-sections for selected nets."""
    result = {}
    for net in nets:
        tracks = [t for t in snapshot['tracks'].values() if t['net'] == net]
        vias = [v for v in snapshot['vias'].values() if v['net'] == net]
        result[net] = dict(
            track_count=len(tracks),
            track_length_mm=sum(_track_length(t) for t in tracks),
            widths_mm=sorted({t['width'] for t in tracks}),
            layers={layer: sum(t['layer'] == layer for t in tracks) for layer in LAYERS
                    if any(t['layer'] == layer for t in tracks)},
            layer_lengths_mm={layer: sum(_track_length(t) for t in tracks if t['layer'] == layer)
                              for layer in LAYERS if any(t['layer'] == layer for t in tracks)},
            bounds=([
                min([p for t in tracks for p in (t['start'][0], t['end'][0])]),
                min([p for t in tracks for p in (t['start'][1], t['end'][1])]),
                max([p for t in tracks for p in (t['start'][0], t['end'][0])]),
                max([p for t in tracks for p in (t['start'][1], t['end'][1])])
            ] if tracks else None),
            via_count=len(vias),
            via_drills_mm=sorted({v['drill'] for v in vias}),
            via_copper_widths_mm=sorted({tuple(v['copper_widths'][layer] for layer in LAYERS)
                                         for v in vias}),
        )
    return result


def _changed_nets(reference, owner):
    return set(routed_delta(reference, owner))


def routed_delta(reference, owner):
    """Group exact native snapshot object deltas by reference/owner net."""
    result = {}
    for section in ('tracks', 'vias'):
        before, after = reference[section], owner[section]
        added = {uid: item for uid, item in after.items() if uid not in before}
        deleted = {uid: item for uid, item in before.items() if uid not in after}
        modified = {uid: (before[uid], after[uid]) for uid in set(before) & set(after)
                    if before[uid] != after[uid]}
        for uid, item in added.items():
            key = item['net']
            result.setdefault(key, {}).setdefault(section, dict(added=0, deleted=0, modified=0,
                                                                added_length_mm=0.0,
                                                                deleted_length_mm=0.0))
            result[key][section]['added'] += 1
            if section == 'tracks':
                result[key][section]['added_length_mm'] += _track_length(item)
        for uid, item in deleted.items():
            key = item['net']
            result.setdefault(key, {}).setdefault(section, dict(added=0, deleted=0, modified=0,
                                                                added_length_mm=0.0,
                                                                deleted_length_mm=0.0))
            result[key][section]['deleted'] += 1
            if section == 'tracks':
                result[key][section]['deleted_length_mm'] += _track_length(item)
        for uid, (before_item, after_item) in modified.items():
            key = f"{before_item['net']} -> {after_item['net']}" if before_item['net'] != after_item['net'] else after_item['net']
            result.setdefault(key, {}).setdefault(section, dict(added=0, deleted=0, modified=0,
                                                                added_length_mm=0.0,
                                                                deleted_length_mm=0.0))
            result[key][section]['modified'] += 1
    return result


def _pad_edges(pad, layer):
    for polygon in pad.get('polygons', {}).get(layer, []):
        points = [_point(p) for p in polygon]
        for a, b in zip(points, points[1:] + points[:1]):
            yield a, b


def minimum_same_layer_clearance(snapshot, target_nets):
    """Find minimum track-track and track-pad copper gap around target nets.

    This is a focused geometric screen. It excludes zones, 3-D stackup
    effects, solder mask, and copper not represented in the snapshot; native
    DRC remains authoritative for those checks.
    """
    require_straight(snapshot['tracks'].values(),'Legacy Phase4.11 clearance')
    tracks = list(snapshot['tracks'].items())
    pads = list(snapshot['pads'].values())
    pad_edges = defaultdict(list)
    for pad in pads:
        for layer in pad.get('polygons', {}):
            for c, d in _pad_edges(pad, layer):
                pad_edges[layer].append((pad, c, d,
                    min(c[0], d[0]), max(c[0], d[0]),
                    min(c[1], d[1]), max(c[1], d[1])))
    best = {net: {'track_track': None, 'track_pad': None} for net in target_nets}
    for uid, track in tracks:
        if track['net'] not in target_nets:
            continue
        a, b = _point(track['start']), _point(track['end'])
        for other_uid, other in tracks:
            if other['net'] == track['net'] or other['layer'] != track['layer']:
                continue
            c, d = _point(other['start']), _point(other['end'])
            # Bounding-box rejection preserves speed on the full board.
            margin = 1.0 + (track['width'] + other['width']) / 2
            if (max(a[0], b[0]) + margin < min(c[0], d[0]) or
                    max(c[0], d[0]) + margin < min(a[0], b[0]) or
                    max(a[1], b[1]) + margin < min(c[1], d[1]) or
                    max(c[1], d[1]) + margin < min(a[1], b[1])):
                continue
            gap = _segment_distance(a, b, c, d) - (track['width'] + other['width']) / 2
            current = best[track['net']]['track_track']
            candidate = dict(gap_mm=gap, layer=track['layer'], track_uuid=uid,
                             other_uuid=other_uid, other_net=other['net'])
            if current is None or gap < current['gap_mm']:
                best[track['net']]['track_track'] = candidate
        margin = 1.0 + track['width'] / 2
        for pad, c, d, cx0, cx1, cy0, cy1 in pad_edges.get(track['layer'], []):
            if pad['net'] == track['net']:
                continue
            if (max(a[0], b[0]) + margin < cx0 or cx1 + margin < min(a[0], b[0]) or
                    max(a[1], b[1]) + margin < cy0 or cy1 + margin < min(a[1], b[1])):
                continue
            gap = _segment_distance(a, b, c, d) - track['width'] / 2
            current = best[track['net']]['track_pad']
            candidate = dict(gap_mm=gap, layer=track['layer'], track_uuid=uid,
                             pad_ref=pad['ref'], pad_pin=pad['pin'], pad_net=pad['net'])
            if current is None or gap < current['gap_mm']:
                best[track['net']]['track_pad'] = candidate
    return best


def _pad_position(snapshot, ref, pin, net):
    for pad in snapshot['pads'].values():
        if pad['ref'] == ref and str(pad['pin']) == str(pin) and pad['net'] == net:
            return pad
    return None


def esd_paths(snapshot):
    """Measure connector-to-ESD pad routes and nearby PGND-via distances."""
    paths = {}
    for net, connector_pin in (('USB_DP', 'A6'), ('USB_DN', 'A7')):
        graph, _ = _graph(snapshot, net)
        _connect_pad_layers(graph, snapshot, net)
        start = _pad_position(snapshot, 'J7', connector_pin, net)
        target = _pad_position(snapshot, 'U2', '1' if net == 'USB_DP' else '2', net)
        starts = [_node(layer, start['position']) for layer in start['polygons']]
        targets = [_node(layer, target['position']) for layer in target['polygons']]
        paths[f'J7_{connector_pin}_to_U2'] = _shortest(graph, starts, targets)
    return paths


def nearby_pgnd(snapshot):
    """Report nearest PGND via to USB connector/ESD pads and route segments."""
    require_straight(snapshot['tracks'].values(),'Legacy Phase4.11 PGND proximity')
    pgnd = [v for v in snapshot['vias'].values() if v['net'] == 'PGND']
    pads = []
    for pad in snapshot['pads'].values():
        if ((pad['ref'] == 'J7' and str(pad['pin']) in {'A6', 'B6', 'A7', 'B7'}) or
                (pad['ref'] == 'U2' and str(pad['pin']) in {'1', '2', '3'})):
            pads.append(dict(ref=pad['ref'], pin=pad['pin'], net=pad['net'], position=pad['position']))
    result = {'pad_nearest': [], 'route_nearest': {}}
    for pad in pads:
        if not pgnd:
            continue
        via = min(pgnd, key=lambda v: _distance(_point(pad['position']), _point(v['position'])))
        result['pad_nearest'].append(dict(ref=pad['ref'], pin=pad['pin'], net=pad['net'],
                                          via_uuid=via['uuid'], via_position=via['position'],
                                          via_drill_mm=via['drill'],
                                          distance_mm=_distance(_point(pad['position']), _point(via['position']))))
    for net in USB_NETS:
        segments = [t for t in snapshot['tracks'].values() if t['net'] == net]
        candidates = []
        for track in segments:
            a, b = _point(track['start']), _point(track['end'])
            for via in pgnd:
                c = _point(via['position'])
                candidates.append((_segment_distance(a, b, c, c), track, via))
        if candidates:
            distance, track, via = min(candidates, key=lambda value: value[0])
            result['route_nearest'][net] = dict(distance_mm=distance, track_uuid=track['uuid'],
                                                layer=track['layer'], via_uuid=via['uuid'],
                                                via_position=via['position'])
    return result


def plane_layer_summary(snapshot, layout):
    """Summarize reference planes and whether bounded occupancy was exported."""
    zones = []
    for zone in snapshot.get('zones', {}).values():
        zones.append(dict(uuid=zone['uuid'], net=zone['net'], layers=sorted(zone['layers'])))
    return dict(zones=zones, plane_samples_available='plane_samples' in layout,
                plane_sample_bounds=layout.get('plane_samples', {}).get('bounds'),
                via_plane_samples=layout.get('via_plane_samples', []),
                interpretation='Only PGND In1.Cu is a filled zone in the exported snapshot; B.Cu USB segments are adjacent to In2.Cu, for which no filled zone is present.')


def protected_loop_summary(snapshot, references=('IC1', 'L1', 'U3')):
    """Summarize pads and routed nets attached to protected power references."""
    result = {}
    for ref in references:
        pads = [p for p in snapshot['pads'].values() if p['ref'] == ref]
        nets = sorted({p['net'] for p in pads if p['net']})
        result[ref] = dict(pads=[dict(pin=p['pin'], net=p['net'], position=p['position']) for p in pads],
                           nets={net: net_metrics(snapshot, [net])[net] for net in nets})
    return result


def analyze(reference, owner, owner_layout=None):
    changed_nets = sorted(_changed_nets(reference, owner))
    selected = sorted(set(changed_nets) | set(USB_NETS))
    return dict(schema_version=1,
                usb=net_metrics(owner, USB_NETS),
                owner_changed_net_metrics=net_metrics(owner, selected),
                reference_changed_net_metrics=net_metrics(reference, selected),
                routed_delta=routed_delta(reference, owner),
                usb_esd_paths=esd_paths(owner),
                nearby_pgnd=nearby_pgnd(owner),
                owner_plane=plane_layer_summary(owner, owner_layout or {}),
                owner_protected_loops=protected_loop_summary(owner),
                reference_protected_loops=protected_loop_summary(reference),
                owner_clearance_screen=minimum_same_layer_clearance(owner, selected),
                limitations=['Snapshot-only; no native API or live editor used here.',
                             'Track/pad clearance screen excludes filled zones, mask, 3-D stackup, and unexported copper.',
                             'No impedance, EMC, ESD waveform, current-density, thermal, or hardware measurement is inferred.'])


def engineering_detail(reference, owner, before_layout, owner_layout, before_context, owner_context):
    """Focused coherent delta review, reusing proven copper/drill/fill helpers."""
    require_straight(owner['tracks'].values(),'Legacy Phase4.11 engineering detail')
    from .legacy_review import metrics_tracks, clearance, conducting_width, reference_samples
    from .plan_validation import inventory, shape, separation
    changed = sorted(_changed_nets(reference,owner))
    details = {}
    for net in changed:
        if net in USB_NETS:
            continue
        result = {}
        for label,g,other,context,layout in [
            ('before',reference,owner,before_context,before_layout),
            ('after',owner,reference,owner_context,owner_layout)]:
            tracks = [t for u,t in g['tracks'].items()
                      if t['net']==net and other['tracks'].get(u)!=t]
            if not tracks:
                continue
            _,holes=inventory(g,context)
            result[label]=dict(metrics=metrics_tracks(tracks),
                minimum_copper_edge_clearance=clearance(g,tracks,context),
                residual_track_strip=conducting_width(tracks,holes),
                reference=reference_samples(g,tracks,layout,context),
                blocked_IC1_proximity=clearance(g,tracks,context,{'I2C_SCL','~INT','STAT'}),
                F5_proximity=clearance(g,tracks,context,{p['net'] for p in g['pads'].values() if p['net'].startswith('/F5_')}))
        details[net]=result
        print('Exported copper/drill/reference delta reviewed: '+net,flush=True)
    usb={}
    for net in USB_NETS:
        tracks=[t for t in owner['tracks'].values() if t['net']==net]
        usb[net]=dict(reference=reference_samples(owner,tracks,owner_layout,owner_context),
                      switching_clearance=clearance(owner,tracks,owner_context,
                        {'SW1','SW2','/SW_NORMAL','BTST1','BTST2','/BST_NORMAL','PMID','BATTERY','SYS'}))
        print('Exported USB reference reviewed: '+net,flush=True)
    protected={'SW1','SW2','BTST1','BTST2','REGN','BATP','/SW_NORMAL','/BST_NORMAL','/MAIN_FB','/NORMAL_SS'}
    loop_preserved={net:all({u:v for u,v in reference[k].items() if v['net']==net}==
                           {u:v for u,v in owner[k].items() if v['net']==net}
                           for k in ['tracks','vias']) for net in sorted(protected)}
    rf=owner_context['zones']['8afa84f7-5aa0-4bf5-8fa4-7f6e45b1987b']
    polygon=rf['outline'][0]['outline']
    obstacle=shape('RF','@RF','*',polygon,polygon=True)
    rf_gap=min([dict(gap_mm=separation(shape(t['uuid'],t['net'],t['layer'],[t['start'],t['end']],t['width']/2),obstacle),
                    track_uuid=t['uuid'],net=t['net'])
               for t in owner['tracks'].values() if t['net'] in USB_NETS],
               key=lambda row:row['gap_mm'])
    transitions=[]
    grounds=[v for v in owner['vias'].values() if v['net']=='PGND']
    for v in owner['vias'].values():
        if v['net'] not in USB_NETS:
            continue
        ground=min(grounds,key=lambda q:math.dist(q['position'],v['position']))
        transitions.append(dict(signal=v,nearest_ground=ground,
                                center_distance_mm=math.dist(ground['position'],v['position'])))
    return dict(non_USB_changed_tracks=details,USB_reference=usb,
                protected_net_geometry_equal=loop_preserved,USB_RF_keepout_minimum=rf_gap,
                USB_transition_nearest_ground_vias=transitions,
                interpretation='In1 projection samples preserve polygon holes and physical drills. B.Cu has no adjacent continuous In2 ground plane; projected In1 coverage is not proof of a controlled return or impedance. Residual strip widths omit helpful via/pad copper and are not ampacity ratings.')


def local_fill_comparison(before_layout, after_layout, bounds, step=.1):
    """Vectorized bounded actual-polygon occupancy comparison, including holes."""
    import numpy as np
    x0,y0,x1,y1=bounds
    X,Y=np.meshgrid(np.arange(x0,x1+step/2,step),np.arange(y0,y1+step/2,step))
    def contains(points):
        mask=np.zeros(X.shape,dtype=bool)
        for p,q in zip(points,points[1:]+points[:1]):
            if p[1]!=q[1]:
                mask^=((p[1]>Y)!=(q[1]>Y)) & (X<(q[0]-p[0])*(Y-p[1])/(q[1]-p[1])+p[0])
        return mask
    def filled(layout):
        mask=np.zeros(X.shape,dtype=bool)
        for zone in layout['fills'].values():
            if zone['net']!='PGND':
                continue
            for polygon in zone['layers'].get('In1.Cu',[]):
                m=contains(polygon['outline'])
                for hole in polygon['holes']:
                    m &= ~contains(hole)
                mask |= m
        return mask
    a,b=filled(before_layout),filled(after_layout)
    return dict(bounds=bounds,step_mm=step,samples=int(a.size),
                changed_samples=int(np.count_nonzero(a!=b)),
                all_sampled_fill_occupancy_equal=bool(np.array_equal(a,b)),
                interpretation='Finite actual native-polygon sampling, not proof between stations or a current-density solution.')
