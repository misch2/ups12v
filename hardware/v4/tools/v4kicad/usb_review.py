"""Read-only USB route measurements from a native toolkit snapshot."""
from heapq import heappop, heappush
import math
from .track_geometry import track_length,track_points


LAYERS = ('F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu')
USB_NETS = ('USB_DP', 'USB_DN', '/USB_MCU_DP', '/USB_MCU_DN')


def _point(point):
    return tuple(round(float(value) * 1_000_000) for value in point)


def _distance(a, b):
    return math.hypot((a[0] - b[0]) / 1_000_000,
                      (a[1] - b[1]) / 1_000_000)


def _node(layer, point):
    p = _point(point)
    return (layer, p[0], p[1])


def _segment_distance(a, b, c, d):
    # Reuse the common tested segment geometry; inputs are native nanometres.
    # A product-of-orientations <=0 test alone falsely intersects disjoint
    # collinear segments and can invent negative copper clearances.
    from .plan_validation import intersects, segment_distance
    if intersects(a,b,c,d):
        return 0.0
    return min(segment_distance(a,c,d), segment_distance(b,c,d),
               segment_distance(c,a,b), segment_distance(d,a,b)) / 1_000_000


def _add_edge(graph, a, b, weight, metadata):
    graph.setdefault(a, []).append((b, weight, metadata))
    graph.setdefault(b, []).append((a, weight, metadata))


def _graph(snapshot, net):
    graph = {}
    tracks = {}
    for uid, track in snapshot['tracks'].items():
        if track['net'] != net:
            continue
        a = _node(track['layer'], track['start'])
        b = _node(track['layer'], track['end'])
        length = track_length(track)
        metadata = dict(kind='track', uuid=uid, layer=track['layer'], width=track['width'],
                        length=length, start=track['start'], end=track['end'])
        _add_edge(graph, a, b, length, metadata)
        tracks[uid] = metadata
    for uid, via in snapshot['vias'].items():
        if via['net'] != net:
            continue
        nodes = [_node(layer, via['position']) for layer in LAYERS]
        metadata = dict(kind='via', uuid=uid, position=via['position'], drill=via['drill'],
                        copper_widths=via['copper_widths'])
        for a, b in zip(nodes, nodes[1:]):
            _add_edge(graph, a, b, 0.0, metadata)
    return graph, tracks


def _pad_nodes(snapshot, ref, pin, net):
    nodes = []
    for pad in snapshot['pads'].values():
        if pad['ref'] != ref or str(pad['pin']) != str(pin) or pad['net'] != net:
            continue
        for layer in pad['polygons']:
            nodes.append(_node(layer, pad['position']))
        if any(float(v) > 0 for v in pad['drill_size']):
            pad_nodes = [_node(layer, pad['position']) for layer in pad['polygons']]
            for a, b in zip(pad_nodes, pad_nodes[1:]):
                # The returned list is consumed by _connect_pad_layers.
                nodes.append((a, b))
    return nodes


def _connect_pad_layers(graph, snapshot, net):
    for pad in snapshot['pads'].values():
        if pad['net'] != net or not any(float(v) > 0 for v in pad['drill_size']):
            continue
        nodes = [_node(layer, pad['position']) for layer in pad['polygons']]
        for a, b in zip(nodes, nodes[1:]):
            _add_edge(graph, a, b, 0.0, dict(kind='pad', ref=pad['ref'], pin=pad['pin']))


def _shortest(graph, starts, targets):
    starts = [node for node in starts if node in graph]
    targets = set(node for node in targets if node in graph)
    if not starts or not targets:
        return dict(connected=False, length_mm=None, tracks=[], vias=[], layers=[])
    distances = {}
    previous = {}
    queue = []
    for node in starts:
        distances[node] = 0.0
        heappush(queue, (0.0, node))
    end = None
    while queue:
        distance, node = heappop(queue)
        if distance != distances.get(node):
            continue
        if node in targets:
            end = node
            break
        for other, weight, metadata in graph[node]:
            candidate = distance + weight
            if candidate < distances.get(other, float('inf')):
                distances[other] = candidate
                previous[other] = (node, metadata)
                heappush(queue, (candidate, other))
    if end is None:
        return dict(connected=False, length_mm=None, tracks=[], vias=[], layers=[])
    edges = []
    node = end
    while node not in starts:
        prior, metadata = previous[node]
        edges.append(metadata)
        node = prior
    edges.reverse()
    tracks = [e['uuid'] for e in edges if e['kind'] == 'track']
    vias = sorted(set(e['uuid'] for e in edges if e['kind'] == 'via'))
    layers = [e['layer'] for e in edges if e['kind'] == 'track']
    return dict(connected=True, length_mm=distances[end], tracks=tracks, vias=vias,
                layers=layers)


def geometric_path(snapshot, net, start, end, heights):
    """Three-dimensional nominal path with endpoints fixed on F.Cu.

    PTHs must not start for free on either face: that would hide an asymmetric
    connector crossover. Via/PTH transfers use saved copper-center heights.
    """
    graph,_=_graph(snapshot,net)
    _connect_pad_layers(graph,snapshot,net)
    for node,edges in graph.items():
        graph[node]=[(other,abs(heights[node[0]]-heights[other[0]])
                      if metadata['kind'] in ['via','pad'] else weight,metadata)
                     for other,weight,metadata in edges]
    def endpoint(refpin):
        ref,pin=refpin.split('.',1)
        return [_node('F.Cu',pad['position']) for pad in snapshot['pads'].values()
                if pad['ref']==ref and str(pad['pin'])==pin and pad['net']==net]
    return _shortest(graph,endpoint(start),endpoint(end))


def analyze_3d(snapshot, heights):
    planar=analyze(snapshot)
    paths={name:dict(net=row['net'],start=row['start'],end=row['end'],
                    **geometric_path(snapshot,row['net'],row['start'],row['end'],heights))
           for name,row in planar['paths'].items()}
    totals={}
    for contact in ['A','B']:
        sides={}
        for polarity,resistor in [('DP','R48'),('DN','R49')]:
            pads={str(p['pin']):p for p in snapshot['pads'].values() if p['ref']==resistor}
            separation=math.dist(pads['1']['position'],pads['2']['position'])
            sides[polarity]=dict(trace_and_barrel_mm=paths[f'USB_{polarity}_{contact}_to_{resistor}']['length_mm']+
                                paths[f'MCU_{polarity}_{resistor}_to_U1']['length_mm'],
                                resistor_pad_center_separation_mm=separation)
            sides[polarity]['including_resistor_pad_center_span_mm']=sides[polarity]['trace_and_barrel_mm']+separation
        totals[contact]=dict(paths=sides,DP_minus_DN_mm=sides['DP']['including_resistor_pad_center_span_mm']-
                             sides['DN']['including_resistor_pad_center_span_mm'])
    return dict(endpoint_reference='F.Cu pad centers for connector and MCU; nominal barrel geometry',
                copper_center_heights_mm=heights,paths=paths,totals=totals,
                interpretation='Geometric estimates, not electrical flight time. Includes nominal layer transfers; resistor span is a pad-center proxy, and connector mating/contact geometry is excluded.')


def _pair_spacing(snapshot, positive_net='USB_DP', negative_net='USB_DN', layer=None):
    positive = [dict(track, uuid=uid) for uid, track in snapshot['tracks'].items()
                if track['net'] == positive_net and (layer is None or track['layer']==layer)]
    negative = [dict(track, uuid=uid) for uid, track in snapshot['tracks'].items()
                if track['net'] == negative_net and (layer is None or track['layer']==layer)]
    candidates = []
    for a in positive:
        for b in negative:
            if a['layer'] != b['layer']:
                continue
            pa=list(map(_point,track_points(a)));pb=list(map(_point,track_points(b)))
            center=min(_segment_distance(p,q,u,v) for p,q in zip(pa,pa[1:]) for u,v in zip(pb,pb[1:]))
            error=.0001*sum(t.get('geometry')=='arc' for t in [a,b])+.000002
            candidates.append(dict(layer=a['layer'], positive_uuid=a['uuid'],
                                   negative_uuid=b['uuid'], center_distance_mm=center,
                                   edge_clearance_mm=center - (a['width'] + b['width']) / 2,
                                   approximation_error_bound_mm=error))
    return min(candidates, key=lambda item: item['edge_clearance_mm']) if candidates else None


def analyze(snapshot):
    """Measure USB partitions, paths, widths, spacings and route transitions."""
    pads = {}
    for pad in snapshot['pads'].values():
        pads.setdefault((pad['ref'], str(pad['pin']), pad['net']), []).append(pad)
    pairs = {
        'USB_DP_A_to_R48': ('USB_DP', ('J7', 'A6'), ('R48', '2')),
        'USB_DP_B_to_R48': ('USB_DP', ('J7', 'B6'), ('R48', '2')),
        'USB_DN_A_to_R49': ('USB_DN', ('J7', 'A7'), ('R49', '2')),
        'USB_DN_B_to_R49': ('USB_DN', ('J7', 'B7'), ('R49', '2')),
        'MCU_DP_R48_to_U1': ('/USB_MCU_DP', ('R48', '1'), ('U1', '27')),
        'MCU_DN_R49_to_U1': ('/USB_MCU_DN', ('R49', '1'), ('U1', '26')),
    }
    paths = {}
    net_summary = {}
    for net in USB_NETS:
        graph, tracks = _graph(snapshot, net)
        _connect_pad_layers(graph, snapshot, net)
        lengths = [value['length'] for value in tracks.values()]
        layers = [value['layer'] for value in tracks.values()]
        branch_nodes = sum(len(edges) > 2 for edges in graph.values())
        net_summary[net] = dict(track_count=len(tracks), track_length_mm=sum(lengths),
                                width_mm=sorted(set(value['width'] for value in tracks.values())),
                                layer_counts={layer: layers.count(layer) for layer in LAYERS if layer in layers},
                                branch_node_count=branch_nodes)
        for name, (expected_net, start, end) in pairs.items():
            if expected_net != net:
                continue
            starts = [_node(layer, pad['position']) for pad in pads.get((start[0], start[1], net), [])
                      for layer in pad['polygons']]
            targets = [_node(layer, pad['position']) for pad in pads.get((end[0], end[1], net), [])
                       for layer in pad['polygons']]
            paths[name] = dict(net=net, start=f'{start[0]}.{start[1]}', end=f'{end[0]}.{end[1]}',
                               **_shortest(graph, starts, targets))
    result = dict(schema_version=1, nets=net_summary, paths=paths,
                  duplicate_contact_path_skew_mm=dict(
                      A=paths.get('USB_DP_A_to_R48', {}).get('length_mm', 0) -
                        paths.get('USB_DN_A_to_R49', {}).get('length_mm', 0),
                      B=paths.get('USB_DP_B_to_R48', {}).get('length_mm', 0) -
                        paths.get('USB_DN_B_to_R49', {}).get('length_mm', 0)),
                  mcu_path_skew_mm=paths.get('MCU_DP_R48_to_U1', {}).get('length_mm', 0) -
                    paths.get('MCU_DN_R49_to_U1', {}).get('length_mm', 0),
                  connector_pair_minimum=_pair_spacing(snapshot),
                  note='Lengths are trace centerline sums; resistor package traversal and vertical via barrel length are excluded.')
    return result
