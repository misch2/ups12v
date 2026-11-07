"""Export-only inductor sourcing overlay. No pcbnew/IPC imports or CAD writes.

Uses accepted native polygon exports and checks the four lands directly against
the immutable ordered Gerber ZIP. Manufacturer dimensions are explicit inputs.
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
import zipfile


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rect(x0, y0, x1, y1):
    from shapely.geometry import box
    return box(x0, y0, x1, y1)


def world(shape, position, angle):
    # KiCad positive angles are counterclockwise on the display (Y down).
    from shapely.affinity import rotate, translate
    return translate(rotate(shape, -angle, origin=(0, 0)), *position)


def terminals(gap, depth, width):
    return [rect(-gap/2-depth, -width/2, -gap/2, width/2),
            rect(gap/2, -width/2, gap/2+depth, width/2)]


def other_net_clearances(lands, swept_by_pin, copper_by_net, mask_union):
    """Check each terminal against every other net, including its paired pad."""
    from shapely.ops import unary_union
    areas, clearances = [], []
    for i, pad in enumerate(lands):
        foreign = unary_union([g for net, shapes in copper_by_net.items()
                               if net != pad['net'] for g in shapes]).intersection(mask_union)
        envelope = unary_union(swept_by_pin[i])
        areas.append(envelope.intersection(foreign).area)
        clearances.append(envelope.distance(foreign))
    return areas, clearances


def analyze(args):
    sys.path.insert(0, str(Path(args.deps).resolve()))
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    from gerbonara import GerberFile
    from .gerber_review import primitive_shape, difference, TOL
    accepted = json.loads(Path(args.accepted_baseline).read_text(encoding='utf-8-sig'))
    assert sha(args.source_board) == accepted['hashes']['ups12v_v4.kicad_pcb']
    proof = json.loads(Path(args.native_proof).read_text(encoding='utf-8-sig'))
    assert proof['all_original_native_bytes_preserved'] and proof['all154_units_exact']
    assert proof['target_sha256'] == sha(args.source_board)
    snapshot = json.loads(Path(args.snapshot).read_text(encoding='utf-8-sig'))
    snapshot_context = json.loads(Path(args.snapshot_context).read_text(encoding='utf-8-sig'))
    assert snapshot_context['source_hashes']['ups12v_v4.kicad_pcb'] == proof['inverse_sha256']
    layout = json.loads(Path(args.layout).read_text(encoding='utf-8-sig'))
    output = Path(args.output)
    output.mkdir(exist_ok=False)
    with zipfile.ZipFile(args.zip) as archive:
        gtl_name = next(n for n in archive.namelist() if n.endswith('.GTL'))
        mask_name = next(n for n in archive.namelist() if n.endswith('.GTS'))
        front = GerberFile.from_string(archive.read(gtl_name).decode())
        mask = GerberFile.from_string(archive.read(mask_name).decode())
    components = {v['ref']: v for v in snapshot['footprints'].values()}
    parts = {
        'L3': dict(mpn='SRP5050FA-6R8M', body_xy_max=[5.5, 5.7],
                   height_max=5.0, gap=[2.05, 2.3, 2.55],
                   depth=[.9, 1.1, 1.3], width=[4.0, 4.3, 4.6],
                   note='Bourns SRP5050FA REV.04/22 pp1-2; drawing rotated 90deg so terminals align with original pads'),
        'L2': dict(mpn='AAPS0530M4R7F', body_xy_max=[5.5, 5.7],
                   height_max=3.1, gap=[2.0, 2.3, 2.6],
                   depth=[.8, 1.1, 1.4], width=[4.3],
                   note='Coilank AAPS-F pp1,2,5; D=4.3mm is TYPICAL, no guaranteed minimum width supplied; not a guaranteed area bound'),
    }
    results = {}
    for ref, spec in parts.items():
        fp = components[ref]
        pos, angle = fp['position'], fp['angle']
        lands = sorted((p for p in snapshot['pads'].values() if p['ref'] == ref), key=lambda p:p['pin'])
        native = [unary_union([Polygon(poly) for poly in p['polygons']['F.Cu']]) for p in lands]
        flashes = [o for o in front.objects if type(o).__name__ == 'Flash' and o.attrs.get('.P', ('',))[0] == ref]
        assert len(flashes) == 2
        cam = {o.attrs['.P'][1]: unary_union([primitive_shape(p) for p in o.to_primitives()]) for o in flashes}
        # Reuse the toolkit's established 0.25um CAD/CAM tessellation tolerance.
        checks = [difference(n, cam[p['pin']], tolerance=TOL) for p,n in zip(lands,native)]
        assert all(c['pass_geometry'] for c in checks), (ref, checks)
        body = world(box(-spec['body_xy_max'][0]/2, -spec['body_xy_max'][1]/2,
                         spec['body_xy_max'][0]/2, spec['body_xy_max'][1]/2), pos, angle)
        court = unary_union([Polygon(p['outline'], p['holes']) for p in layout['courtyards'][ref]])
        neighbors = {r: unary_union([Polygon(p['outline'],p['holes']) for p in polys])
                     for r,polys in layout['courtyards'].items() if r != ref and polys}
        nearest = sorted((dict(ref=r, clearance_mm=body.distance(g)) for r,g in neighbors.items()), key=lambda r:r['clearance_mm'])[:5]
        nominal = [world(t,pos,angle) for t in terminals(2.3,1.1,4.3)]
        overlap = []
        swept = []
        swept_by_pin = [[], []]
        for gap, depth, width in itertools.product(spec['gap'],spec['depth'],spec['width']):
            pair = [world(t,pos,angle) for t in terminals(gap,depth,width)]
            for i,t in enumerate(pair):
                overlap.append(dict(pin=lands[i]['pin'],gap=gap,depth=depth,width=width,
                                    overlap_mm2=t.intersection(native[i]).area,
                                    terminal_fraction=t.intersection(native[i]).area/t.area))
                swept.append(t)
                swept_by_pin[i].append(t)
        terminal_envelope = unary_union(swept)
        # A +/-0.10 mm placement sensitivity is reported, not imposed as a new gate.
        from shapely.affinity import translate
        offset_results = []
        for dx,dy in itertools.product([-.1,0,.1],repeat=2):
            offset_results.extend(translate(t,dx,dy).intersection(native[i]).area for i,t in enumerate(nominal))
        nearby = box(pos[0]-4,pos[1]-4,pos[0]+4,pos[1]+4)
        copper_by_net = {}
        for obj in front.objects:
            attrs = getattr(obj, 'attrs', None)
            if not isinstance(attrs,dict):
                continue
            net = attrs.get('.N', ('',))[0]
            for primitive in obj.to_primitives():
                geom = primitive_shape(primitive)
                if geom.intersects(nearby):
                    copper_by_net.setdefault(net, []).append(geom.intersection(nearby))
        mask_shapes = []
        for obj in mask.objects:
            for primitive in obj.to_primitives():
                geom = primitive_shape(primitive)
                if geom.intersects(nearby):
                    mask_shapes.append(geom.intersection(nearby))
        mask_union = unary_union(mask_shapes)
        # Each terminal must also clear the OPPOSITE inductor net, not merely
        # unrelated component nets. Do not exclude both own nets together.
        pin_short_areas, pin_clearances = other_net_clearances(
            lands, swept_by_pin, copper_by_net, mask_union)
        short_area = sum(pin_short_areas)
        assert short_area < 1e-8
        assert body.difference(court).area < 1e-8
        assert not any(body.intersects(g) for g in neighbors.values())
        results[ref] = dict(**spec, position=pos, angle=angle, land_dimensions_mm=[1.18,4.7],
                            pad_centers_mm=[p['position'] for p in lands], pad_nets=[p['net'] for p in lands],
                            native_vs_ordered_CAM=checks, max_body_inside_original_courtyard=True,
                            minimum_courtyard_edge_reserve_mm=body.distance(court.boundary), nearest_courtyards=nearest,
                            nominal_overlap_mm2=[t.intersection(n).area for t,n in zip(nominal,native)],
                            tolerance_corner_minimum_overlap_mm2=min(o['overlap_mm2'] for o in overlap),
                            tolerance_corner_minimum_terminal_fraction=min(o['terminal_fraction'] for o in overlap),
                            overlap_is_guaranteed_bound=ref=='L3',
                            nominal_plusminus_0_1mm_placement_minimum_overlap_mm2=min(offset_results),
                            terminal_envelope_foreign_exposed_copper_overlap_mm2=short_area,
                            terminal_envelope_foreign_exposed_copper_clearance_mm=min(pin_clearances),
                            per_pin_other_net_clearance_mm=pin_clearances,
                            opposite_terminal_minimum_gap_mm=min(spec['gap']))
        # Dimensioned vector overlay; the native copper polygons are unmodified.
        view = [pos[0]-5,pos[1]-5,10,10]
        chunks = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view[0]} {view[1]} 10 10" width="900" height="900">',
                  f'<rect x="{view[0]}" y="{view[1]}" width="10" height="10" fill="white"/>']
        def draw(geom, color, fill='none', width=.025):
            for p in ([geom] if geom.geom_type=='Polygon' else getattr(geom,'geoms',[])):
                if p.geom_type=='Polygon':
                    points=' '.join(f'{x},{y}' for x,y in p.exterior.coords)
                    chunks.append(f'<polygon points="{points}" fill="{fill}" stroke="{color}" stroke-width="{width}"/>')
        for name,g in neighbors.items():
            if g.intersects(box(*[view[0],view[1],view[0]+10,view[1]+10])):
                draw(g,'#aaa','#f4f4f4',.02)
        draw(court,'#16843a')
        for n in native:draw(n,'#8d6900','#edce63')
        draw(body,'#185dd1',width=.045)
        for t in nominal:draw(t,'#d12727',width=.04)
        label=f'{ref} {spec["mpn"]}: gold=ordered copper, green=original courtyard, blue=max body, red=nominal terminals'
        chunks.append(f'<text x="{view[0]+.15}" y="{view[1]+.3}" font-size=".15">{label}</text></svg>')
        (output/(ref+'-overlay.svg')).write_text('\n'.join(chunks),encoding='utf-8')
    result = dict(status='PASS_BOUNDED_EXPORTED_FIT_SCREEN', native_CAD_operations=False,
                  qualification='PROTOTYPE_CANDIDATES_OWNER_APPROVAL_REQUIRED_NOT_HARDWARE_MEASUREMENTS',
                  input_hashes={str(p):sha(p) for p in [args.source_board,args.accepted_baseline,args.native_proof,args.snapshot,args.snapshot_context,args.layout,args.zip]},
                  parts=results)
    (output/'fit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({r:{k:v for k,v in d.items() if k in ['nominal_overlap_mm2','tolerance_corner_minimum_overlap_mm2','nearest_courtyards','terminal_envelope_foreign_exposed_copper_overlap_mm2']} for r,d in results.items()}))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['source-board','accepted-baseline','native-proof','snapshot','snapshot-context','layout','zip','deps','output']:
        parser.add_argument('--'+name,required=True)
    analyze(parser.parse_args())


if __name__ == '__main__':
    main()
