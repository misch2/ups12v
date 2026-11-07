"""Review-only epoxy/cap inventory of accepted exports, never CAD or CAM output.

No native imports, geometry regeneration, process launch or import-time I/O.
Reuses Phase4.22A mask-opening intersections and binds them to the same PCB.
"""
import argparse
from collections import Counter
import csv
from pathlib import Path

from .safety import digest, read_json, require, write_json


def classify(snapshot, manifest, exposed, limit_mm=.5):
    require(set(snapshot['vias']) == set(manifest['vias']), 'Via UUID inventories differ')
    require(set(snapshot['pads']) == set(manifest['pads']), 'Component pad inventories differ')
    require(not set(snapshot['vias']).intersection(snapshot['pads']), 'Via/component UUID collision')
    pairs = exposed['via_pad_pairs']
    require(all(p['via_uuid'] in snapshot['vias'] and p['pad_uuid'] in snapshot['pads'] for p in pairs),
            'Opening screen refers to unknown object')
    vias = []
    for uid, v in sorted(snapshot['vias'].items()):
        native = manifest['vias'][uid]
        drill = native['padStack']['drill']
        require(native['type'] == 'VT_THROUGH', 'Unexpected blind/buried via')
        require(drill['shape'] == 'DS_CIRCLE', 'Unexpected non-circular via hole')
        dims = [int(drill['diameter'][k])/1e6 for k in ('xNm', 'yNm')]
        require(dims == [v['drill'], v['drill']], 'Native/exported via drill mismatch')
        require([int(native['position'][k])/1e6 for k in ('xNm', 'yNm')] == v['position'],
                'Native/exported via position mismatch')
        own = [p for p in pairs if p['via_uuid'] == uid]
        opened = [p for p in own if p['bore_intersects_opening']]
        vias.append(dict(uuid=uid, net=v['net'], x_mm=v['position'][0], y_mm=v['position'][1],
                         drill_mm=v['drill'], copper_diameters_mm=v['copper_widths'],
                         exceeds_050=v['drill'] > limit_mm, at_050_limit=v['drill'] == limit_mm,
                         proposed_action='EPOXY_FILL_AND_COPPER_CAP',
                         bore_intersects_pad_opening=bool(opened),
                         open_pad_refs=';'.join(sorted({p['ref'] for p in opened})),
                         near_opening_refs=';'.join(sorted({p['ref'] for p in own}))))
    keep_open = []
    for uid, p in sorted(snapshot['pads'].items()):
        if manifest['pads'][uid]['type'] not in {'PT_PTH', 'PT_NPTH'}:
            continue
        native = manifest['pads'][uid]
        require([int(native['padStack']['drill']['diameter'][k])/1e6 for k in ('xNm', 'yNm')] == p['drill_size'],
                'Native/exported component hole mismatch')
        keep_open.append(dict(uuid=uid, reference=p['ref'], pin=p['pin'], net=p['net'],
                              pad_type=manifest['pads'][uid]['type'],
                              x_mm=p['position'][0], y_mm=p['position'][1],
                              drill_x_mm=p['drill_size'][0], drill_y_mm=p['drill_size'][1],
                              proposed_action='KEEP_OPEN_NO_FILL_NO_CAP'))
    refs = {}
    for ref in sorted({p['ref'] for p in pairs}):
        own = [p for p in pairs if p['ref'] == ref]
        opened = [p for p in own if p['bore_intersects_opening']]
        get = lambda selected: sorted({p['via_uuid'] for p in selected})
        ids = get(opened)
        refs[ref] = dict(near_vias=len(get(own)), center_inside_vias=len(get([p for p in own if p['via_center_in_opening']])),
                         bore_overlap_vias=len(ids), bore_overlap_uuid=ids,
                         bore_overlap_drills_mm=dict(Counter(str(snapshot['vias'][u]['drill']) for u in ids)),
                         oversize_exclusions=[u for u in ids if snapshot['vias'][u]['drill'] > limit_mm])
    return dict(via_count=len(vias), through_round_vias=True,
                via_drill_counts_mm=dict(sorted(Counter(str(v['drill_mm']) for v in vias).items())),
                holes_above_050=[v for v in vias if v['exceeds_050']],
                holes_at_050=[v for v in vias if v['at_050_limit']],
                keep_open_counts=dict(Counter(p['pad_type'] for p in keep_open)),
                all_exposed_pad_refs=refs, via_inventory=vias, component_holes_keep_open=keep_open,
                size_screen_pass=not any(v['exceeds_050'] for v in vias),
                limits=['Design drill diameters, not measured manufactured bores or tooling diameters.',
                        '0.5mm hole limit does not refer to outer copper annulus diameter.',
                        'No additional epoxy exclusion demonstrated by the reused opening screen; CAM acceptance remains pending.',
                        'Review inventories only; not fabrication files, drill files, a release or an instruction submitted to JLCPCB.'])


def csv_write(path, rows):
    require(bool(rows), 'Empty review inventory')
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        w = csv.DictWriter(handle, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    p = argparse.ArgumentParser()
    for key in ('board', 'snapshot', 'manifest', 'exposed', 'preservation', 'output'):
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    m, s, x = map(read_json, (a.manifest, a.snapshot, a.exposed))
    before = digest(a.board)
    require(before == m['hashes']['ups12v_v4.kicad_pcb'] == x['source_pcb_sha256'], 'Source hash mismatch')
    board = Path(a.board).resolve()
    root = board.parents[3]
    protected = read_json(a.preservation)
    for name, expected in protected.items():
        require(digest(root/name) == expected, 'Protected source mismatch: ' + name)
    source_guard = Path(a.exposed).parent/'analysis-source-manifest.json'
    require(source_guard.is_file(), 'Accepted Phase4.22A input hash manifest required')
    hashes = read_json(source_guard)
    for n in (a.snapshot, a.manifest, a.exposed):
        name = str(Path(n).resolve().relative_to(root))
        require(name in hashes and digest(n) == hashes[name], 'Accepted input export hash mismatch: ' + name)
    result = classify(s, m, x)
    require(result['via_count'] == 324, 'Expected accepted324vias')
    require(result['keep_open_counts'] == {'PT_PTH': 41, 'PT_NPTH': 12}, 'Component-hole inventory drift')
    result['source_pcb_sha256'] = before
    result['source_hashes'] = {str(Path(n).resolve().relative_to(root)): digest(n)
                               for n in (a.snapshot, a.manifest, a.exposed, a.preservation, source_guard, __file__)}
    out = Path(a.output)
    require(not out.exists(), 'Fresh output directory required')
    out.mkdir(parents=True)
    write_json(out/'via-fill-review.json', result)
    csv_write(out/'all-324-vias-review.csv', result['via_inventory'])
    csv_write(out/'component-holes-keep-open-review.csv', result['component_holes_keep_open'])
    for name, expected in protected.items():
        require(digest(root/name) == expected, 'Protected source changed: ' + name)
    write_json(out/'preservation.json', dict(protected_before=protected, protected_after=protected,
                                          unchanged=True, native_operations=0, fabrication_files_generated=0))
    print(dict(via_count=result['via_count'], via_drill_counts_mm=result['via_drill_counts_mm'],
               above050=len(result['holes_above_050']), at050=len(result['holes_at_050']),
               keep_open=result['keep_open_counts'], protected_unchanged=len(protected)))


if __name__ == '__main__':
    main()
