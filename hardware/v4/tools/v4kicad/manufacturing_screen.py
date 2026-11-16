"""Bounded read-only manufacturing screens of accepted JSON exports.

No native imports, CAD parsing, process launch or import-time I/O. Mask opening
geometry is reused from native copper polygons only when zero margin and no
overrides/custom mask artwork have been established. This is not Gerber CAM.
"""
import argparse
from collections import Counter
from itertools import combinations

from .plan_validation import inside, inventory, nearby, separation, shape
from .safety import digest, read_json, require, write_json


def mask_assumptions(manifest, metadata):
    setup = {r[0]: r[1:] for r in metadata['setup_metadata']}
    require(setup['pad_to_mask_clearance'] == ['0'], 'Nonzero mask margin requires native mask polygons')
    require(setup['tenting'] == [['front', 'yes'], ['back', 'yes']], 'Unknown via tenting')
    for p in manifest['pads'].values():
        require(not any('mask' in k.lower() for k in p['padStack']), 'Pad mask override not supported')
    for f in manifest['footprints'].values():
        require(not any('mask' in k.lower() for k in f['overrides']), 'Footprint mask override not supported')
        for item in f['definition']['items']:
            require(item.get('layer') not in {'BL_F_Mask', 'BL_B_Mask'}, 'Custom mask artwork requires native mask polygons')
    for item in list(manifest['shapes'].values()) + list(manifest['texts'].values()):
        require(item.get('layer') not in {'BL_F_Mask', 'BL_B_Mask'}, 'Board mask artwork requires native mask polygons')
    return dict(global_mask_margin_mm=0, via_tenting_front_back=True,
                pad_and_footprint_mask_overrides=False, custom_mask_artwork=False,
                mask_geometry_basis='Accepted native pad copper polygons, 1:1 zero expansion; 100nm outside bound')


def via_pad_rows(snapshot, manifest, threshold=.35):
    openings = []
    for uid, p in snapshot['pads'].items():
        native = manifest['pads'][uid]
        for side, mask in [('F.Cu', 'BL_F_Mask'), ('B.Cu', 'BL_B_Mask')]:
            if mask not in native['padStack']['layers']:
                continue
            for poly in p['polygons'].get(side, []):
                openings.append((p, shape(uid, p['net'], side, poly, polygon=True, kind='opening')))
    rows = []
    for uid, v in snapshot['vias'].items():
        for p, opening in openings:
            side = opening['layer']
            center = v['position']
            annulus = shape(uid, v['net'], side, [center, center], v['copper_widths'][side]/2)
            if not nearby(annulus, opening, threshold):
                continue
            copper_gap = separation(annulus, opening)
            bore = shape(uid, v['net'], side, [center, center], v['drill']/2)
            bore_gap = separation(bore, opening)
            if copper_gap > threshold + 1e-6:
                continue
            rows.append(dict(via_uuid=uid, via_net=v['net'], via_position_mm=center,
                             via_bore_mm=v['drill'], via_copper_mm=v['copper_widths'][side],
                             ref=p['ref'], pin=p['pin'], pad_uuid=opening['id'], pad_net=p['net'], side=side,
                             annulus_edge_to_opening_mm=copper_gap, bore_edge_to_opening_mm=bore_gap,
                             via_center_in_opening=inside(center, opening['points']),
                             bore_intersects_opening=bore_gap <= 1e-6,
                             same_net=v['net'] == p['net']))
    return rows


def trace_screen(context):
    s = context['snapshot']
    copper, _ = inventory(s, context)
    net_tie_artwork = {g['uuid']: g['ref'] for g in context.get('copper_graphics', [])
                       if g.get('ref') in {'NT1', 'NT2', 'NT4'}}
    require(all(g['uuid'] in net_tie_artwork for g in context.get('copper_graphics', [])),
            'Unknown copper artwork needs explicit ownership review')
    # Accepted net-tie bridge artwork intentionally joins its named pad nets.
    # It is not an arbitrary foreign net called @fixed-artwork.
    copper = [c for c in copper if c['id'] not in net_tie_artwork]
    closest = None
    below = []
    # Only pairs involving a routed trace/arc: pad-pad vendor screen and full
    # plane/native connectivity are already accepted Phase4.21 evidence.
    for layer in ('F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu'):
        items = [c for c in copper if c['layer'] == layer]
        for a, b in combinations(items, 2):
            if a['kind'] != 'track' and b['kind'] != 'track':
                continue
            if a['net'] == b['net'] or not nearby(a, b, .101):
                continue
            gap = separation(a, b)
            row = dict(a=a['id'], b=b['id'], net_a=a['net'], net_b=b['net'], layer=layer, gap_mm=gap)
            if closest is None or gap < closest['gap_mm']:
                closest = row
            if gap < .1 - .000002:
                below.append(row)
    return dict(min_track_width_mm=min(t['width'] for t in s['tracks'].values()),
                width_counts_mm=dict(Counter(t['width'] for t in s['tracks'].values())),
                routed_objects=len(s['tracks']), tracks_below_010=[t['uuid'] for t in s['tracks'].values() if t['width'] < .1],
                trace_to_other_fixed_copper_below_010=below, closest_within_0101mm=closest,
                accepted_net_tie_artwork_separately_adjudicated=net_tie_artwork,
                scope='Actual accepted traces/arcs versus tracks/vias/pad copper; native arc polygons, no chord substitution. '
                      'Plane fills and pad-pad/via-via checks reuse accepted native DRC/vendor screens. 2nm numerical comparison allowance, '
                      'not a physical clearance waiver; native pad polygons are bounded outside by100nm.')


def main():
    parser = argparse.ArgumentParser()
    for arg in ('context', 'manifest', 'metadata', 'board', 'output'):
        parser.add_argument('--' + arg, required=True)
    args = parser.parse_args()
    c, m, metadata = map(read_json, (args.context, args.manifest, args.metadata))
    before = digest(args.board)
    require(before == c['board_sha256'] == m['hashes']['ups12v_v4.kicad_pcb'], 'Accepted source hash mismatch')
    from pathlib import Path
    require(not Path(args.output).exists(), 'Fresh output required')
    assumptions = mask_assumptions(m, metadata)
    rows = via_pad_rows(c['snapshot'], m)
    unique = lambda items: len({r['via_uuid'] for r in items})
    summary = dict(total_vias=len(c['snapshot']['vias']), via_pad_side_pairs_within035=len(rows),
                   unique_vias_within035=unique(rows),
                   unique_vias_center_in_opening=unique([r for r in rows if r['via_center_in_opening']]),
                   unique_vias_bore_intersects_opening=unique([r for r in rows if r['bore_intersects_opening']]),
                   affected_refs=dict(Counter(r['ref'] for r in rows)))
    result = dict(source_pcb_sha256=before, mask_assumptions=assumptions,
                  via_summary=summary, via_pad_pairs=rows, actual_trace_screen=trace_screen(c),
                  limits=['No Gerbers, CAM, actual coating or manufactured via guarantee.',
                          '0.35mm screen uses via annulus edge; bore edge separately reported because vendor wording needs confirmation.',
                          'Negative separation denotes overlap, not penetration depth.',
                          'Ink plugging cannot be assumed for via-in-pad/open/near-opening cases. No order/process change made.'])
    require(digest(args.board) == before, 'Source changed')
    write_json(args.output, result)
    print({k: v for k, v in summary.items() if k != 'affected_refs'})
    print({k: result['actual_trace_screen'][k] for k in ('min_track_width_mm', 'routed_objects', 'tracks_below_010')})
    print('Trace gaps below0.100mm:', len(result['actual_trace_screen']['trace_to_other_fixed_copper_below_010']))


if __name__ == '__main__':
    main()
