"""Independent read-only CAM review of an owner ZIP using accepted native exports.

No CAD imports, source parsing, native processes or fabrication generation.
Third party dependencies are injected by the command's --deps option only.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import warnings
import zipfile

LAYERS = {'GTL': 'F.Cu', 'GL2': 'In1.Cu', 'GL3': 'In2.Cu', 'GBL': 'B.Cu',
          'GTS': 'F.Mask', 'GBS': 'B.Mask', 'GTO': 'F.SilkS', 'GBO': 'B.SilkS',
          'GKO': 'Edge.Cuts', 'GTP': 'F.Paste', 'GBP': 'B.Paste'}
EXPECTED_PCB = '4eb7bd2c72fec3cf49d3746250864b5237e7919760ebdbc3647cbc0101fa8737'
TOL = .00025  # numerical comparison, not a manufacturing/design-rule waiver


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, data):
    Path(path).write_text(json.dumps(data, indent=2), encoding='utf-8')


def primitive_shape(p):
    from shapely.geometry import Point, LineString, Polygon
    from shapely import make_valid
    kind = type(p).__name__
    if kind == 'Circle':
        return Point(p.x, -p.y).buffer(p.r, quad_segs=512)
    if kind == 'Line':
        if p.x1 == p.x2 and p.y1 == p.y2:
            return Point(p.x1, -p.y1).buffer(p.width / 2, quad_segs=512)
        return LineString([(p.x1, -p.y1), (p.x2, -p.y2)]).buffer(p.width / 2, quad_segs=512)
    if kind == 'Rectangle':
        # Independently implement rotation rather than approximate a rotated rectangle.
        c, s = math.cos(p.rotation), math.sin(p.rotation)
        return Polygon([(p.x + c*x - s*y, -(p.y + s*x + c*y))
                        for x, y in [(-p.w/2, -p.h/2), (p.w/2, -p.h/2),
                                     (p.w/2, p.h/2), (-p.w/2, p.h/2)]])
    if kind == 'Arc':
        from gerbonara.utils import approximate_arc
        points = list(approximate_arc(p.cx,p.cy,p.x1,p.y1,p.x2,p.y2,p.clockwise,
                                     max_error=.000002))
        return LineString([(x,-y) for x,y in points]).buffer(p.width/2,quad_segs=512)
    if kind == 'ArcPoly':
        points = p.approximate_arcs(max_error=.000002).outline
        return make_valid(Polygon([(x, -y) for x, y in points]))
    raise ValueError('Unsupported CAM primitive: ' + kind)


def compose(file):
    """Apply ordered dark/clear exposure; batch consecutive equal polarities."""
    from shapely.geometry import GeometryCollection
    from shapely.ops import unary_union
    image, pending, polarity = GeometryCollection(), [], True
    for obj in file.objects:
        for p in obj.to_primitives():
            if p.polarity_dark != polarity and pending:
                group = unary_union(pending)
                image = image.union(group) if polarity else image.difference(group)
                pending = []
            polarity = p.polarity_dark
            pending.append(primitive_shape(p))
    if pending:
        group = unary_union(pending)
        image = image.union(group) if polarity else image.difference(group)
    return image


def difference(expected, actual, tolerance=TOL):
    missing = expected.difference(actual.buffer(tolerance))
    extra = actual.difference(expected.buffer(tolerance))
    return dict(expected_area_mm2=expected.area, exported_area_mm2=actual.area,
                raw_xor_mm2=expected.symmetric_difference(actual).area,
                missing_beyond_tolerance_mm2=missing.area, extra_beyond_tolerance_mm2=extra.area,
                pass_geometry=missing.area < 1e-8 and extra.area < 1e-8,
                missing_bounds=None if missing.is_empty else missing.bounds,
                extra_bounds=None if extra.is_empty else extra.bounds)


def drill_key(obj):
    width = obj.aperture.diameter
    if type(obj).__name__ == 'Flash':
        ends = [(obj.x, -obj.y)] * 2
    elif type(obj).__name__ == 'Line':
        ends = [(obj.x1, -obj.y1), (obj.x2, -obj.y2)]
    else:
        raise ValueError('Unsupported drill object ' + type(obj).__name__)
    return (round(width, 6), *sorted(tuple(round(v, 6) for v in p) for p in ends))


def native_hole_key(pad, orientation):
    from .plan_validation import drill
    d = drill('', '', pad['position'], pad['drill_size'], orientation)
    return (round(2*d['radius'], 6), *sorted(tuple(round(v, 6) for v in p) for p in d['points']))


def match_holes(holes, actual_keys, coordinate_tolerance=.000501):
    """Unique 1:1 match; metric decimal Excellon has 0.001mm coordinates here.

    Exact hole/tool diameters are required; only exported centre coordinates may
    differ by half of the declared output increment (plus 1nm input precision).
    """
    remaining = {k: list(v.elements()) for k,v in actual_keys.items()}
    for row in holes:
        kind = 'NPTH' if row['kind']=='PT_NPTH' else 'PTH'
        key = row['key']
        candidates = [(i,k) for i,k in enumerate(remaining[kind]) if k[0]==key[0]
            and max(abs(k[e][a]-key[e][a]) for e in (1,2) for a in (0,1)) <= coordinate_tolerance]
        if len(candidates)==1:
            i,k=candidates[0]
            row.update(match=True,exported_key=k,
                max_coordinate_delta_mm=max(abs(k[e][a]-key[e][a]) for e in (1,2) for a in (0,1)))
            remaining[kind].pop(i)
        else:
            row.update(match=False,candidate_count=len(candidates))
    return {k:dict(expected_count=sum((r['kind']=='PT_NPTH')==(k=='NPTH') for r in holes),
                   actual_count=sum(actual_keys[k].values()),
                   missing=[r['uuid'] for r in holes if (r['kind']=='PT_NPTH')==(k=='NPTH') and not r['match']],
                   extra=remaining[k],
                   pass_geometry=not remaining[k] and all(r['match'] for r in holes if (r['kind']=='PT_NPTH')==(k=='NPTH')))
            for k in actual_keys}


def expected_geometry(snapshot, context, layout, manifest):
    from shapely.geometry import Point, Polygon, LineString
    from shapely.ops import unary_union
    from shapely import make_valid
    from .plan_validation import inventory
    shapes, _ = inventory(snapshot, context)
    groups = defaultdict(list)
    by_net = defaultdict(list)
    for s in shapes:
        # Native geometry exposes NPTH placeholder pads on *.Cu. KiCad plots no
        # copper for these non-plated, hole-sized mechanical pads. Prove each is
        # wholly consumed by its own mechanical drill before excluding it.
        if s['kind']=='pad' and manifest['pads'][s['id']]['type']=='PT_NPTH':
            pad=snapshot['pads'][s['id']]
            key=native_hole_key(pad,context['pads'][s['id']]['orientation'])
            bore=(Point(key[1]).buffer(key[0]/2,quad_segs=512) if key[1]==key[2]
                  else LineString([key[1],key[2]]).buffer(key[0]/2,quad_segs=512))
            assert Polygon(s['points']).difference(bore.buffer(TOL)).area < 1e-8, 'NPTH has a real copper land'
            continue
        if s['polygon']:
            g = make_valid(Polygon(s['points']))
        elif s['points'][0] == s['points'][1]:
            g = Point(s['points'][0]).buffer(s['radius'], quad_segs=512)
        else:
            g = LineString(s['points']).buffer(s['radius'], quad_segs=512)
        groups[s['layer']].append(g)
        by_net[(s['layer'], s['net'])].append(g)
    for zone in layout['fills'].values():
        for layer, polys in zone['layers'].items():
            for p in polys:
                g = make_valid(Polygon(p['outline'], p['holes']))
                groups[layer].append(g)
                by_net[(layer, zone['net'])].append(g)
    for uid, pad in snapshot['pads'].items():
        stack = manifest['pads'][uid]['padStack']
        for side in ('F', 'B'):
            if 'BL_' + side + '_Mask' in stack['layers']:
                for p in pad['polygons'].get(side+'.Cu', []):
                    groups[side+'.Mask'].append(make_valid(Polygon(p)))
    return {k: unary_union(v) for k, v in groups.items()}, by_net


def review(args):
    import gerbonara
    import shapely
    from gerbonara import GerberFile, ExcellonFile
    from shapely.geometry import Point, Polygon, LineString, box
    from shapely.ops import unary_union, polygonize
    out = Path(args.output)
    # Never overwrite evidence from an earlier completed attempt.
    if (out/'cam-review.json').exists():
        raise ValueError('Fresh result destination required')
    out.mkdir(parents=True, exist_ok=True)
    board = Path(args.board)
    assert sha(board) == EXPECTED_PCB, 'Unaccepted production source'
    source = read(args.context)
    assert source['board_sha256'] == EXPECTED_PCB
    snapshot, layout, manifest = source['snapshot'], read(args.layout), read(args.manifest)
    assert manifest['hashes'][board.name] == EXPECTED_PCB
    protection = read(args.preservation)['protected_before']
    assert all(sha(p) == h for p, h in protection.items()), 'Protected input drift'
    inputs = {p: sha(p) for p in [args.zip, args.board, args.context, args.layout, args.manifest,
                                 args.preservation, args.exposed]}
    write(out/'inputs-before.json', inputs)
    files, parsed, images, drills, parser_warnings = [], {}, {}, {}, []
    with zipfile.ZipFile(args.zip) as z:
        assert z.testzip() is None, 'ZIP CRC failure'
        assert len(z.namelist()) == len(set(z.namelist())), 'Duplicate members'
        for i in z.infolist():
            content = z.read(i)
            ext = Path(i.filename).suffix[1:]
            row = dict(member=i.filename, bytes=len(content), crc32=f'{i.CRC:08x}',
                       sha256=hashlib.sha256(content).hexdigest(), directory=i.is_dir())
            if i.is_dir():
                files.append(row)
                continue
            text = content.decode('utf-8-sig')
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter('always')
                if ext in LAYERS:
                    layer = LAYERS[ext]
                    assert layer not in parsed, 'Duplicate manufacturing layer'
                    f = GerberFile.from_string(text, filename=i.filename)
                    parsed[layer] = f
                    images[layer] = compose(f)
                    row.update(layer=layer, file_attrs=f.file_attrs, objects=len(f.objects),
                               object_types=dict(Counter(type(o).__name__ for o in f.objects)),
                               area_mm2=images[layer].area,
                               bounds=None if images[layer].is_empty else images[layer].bounds)
                elif ext == 'TXT' and i.filename.endswith(('-PTH.TXT', '-NPTH.TXT')):
                    kind = 'NPTH' if i.filename.endswith('-NPTH.TXT') else 'PTH'
                    f = ExcellonFile.from_string(text, filename=i.filename, plated=kind == 'PTH')
                    drills[kind] = f
                    row.update(layer=kind, objects=len(f.objects),
                               object_types=dict(Counter(type(o).__name__ for o in f.objects)),
                               tools_mm=dict(Counter(str(o.aperture.diameter) for o in f.objects)))
                    # Retain independent X2 tool-function declarations as interpreted metadata.
                    row['tool_definitions'] = re.findall(r'T\d+C[0-9.]+', text)
                else:
                    raise ValueError('Unexplained member: ' + i.filename)
                parser_warnings.extend(str(w.message) for w in captured)
            files.append(row)
    assert set(parsed) == set(LAYERS.values()) and set(drills) == {'PTH', 'NPTH'}
    expected_functions = {'F.Cu': ('Copper','L1','Top'), 'In1.Cu': ('Copper','L2','Inr'),
                          'In2.Cu': ('Copper','L3','Inr'), 'B.Cu': ('Copper','L4','Bot'),
                          'F.Mask': ('Soldermask','Top'), 'B.Mask': ('Soldermask','Bot'),
                          'F.SilkS': ('Legend','Top'), 'B.SilkS': ('Legend','Bot'),
                          'Edge.Cuts': ('Profile','NP'), 'F.Paste': ('Paste','Top'),
                          'B.Paste': ('Paste','Bot')}
    assert all(tuple(parsed[l].file_attrs['.FileFunction']) == v for l,v in expected_functions.items())
    assert all(tuple(f.file_attrs['.SameCoordinates']) == ('Original',) for f in parsed.values())
    write(out/'zip-manifest.json', dict(zip_sha256=inputs[args.zip], files=files))
    print('Parsed 11 Gerbers and 2 Excellon files; comparing all native geometry.', flush=True)

    actual_keys = {k: Counter(drill_key(o) for o in f.objects) for k,f in drills.items()}
    expected_keys = {'PTH': Counter(), 'NPTH': Counter()}
    holes = []
    for uid, via in snapshot['vias'].items():
        key = (round(via['drill'],6), tuple(via['position']), tuple(via['position']))
        expected_keys['PTH'][key] += 1
        holes.append(dict(uuid=uid, kind='VIA', net=via['net'], key=key,
                          match=actual_keys['PTH'][key] == 1))
    for uid,p in snapshot['pads'].items():
        typ = manifest['pads'][uid]['type']
        if typ not in {'PT_PTH', 'PT_NPTH'}:
            continue
        kind = 'NPTH' if typ == 'PT_NPTH' else 'PTH'
        key = native_hole_key(p, source['pads'][uid]['orientation'])
        expected_keys[kind][key] += 1
        holes.append(dict(uuid=uid, kind=typ, reference=p['ref'], pin=p['pin'], key=key,
                          match=actual_keys[kind][key] == 1))
    drill_compare = match_holes(holes,actual_keys)
    write(out/'all-377-hole-comparison.json', dict(comparison=drill_compare, holes=holes))

    expected, by_net = expected_geometry(snapshot, source, layout, manifest)
    compare = {}
    for l in expected:
        print('Compare '+l,flush=True)
        compare[l] = difference(expected[l], images[l])
    # Preserve parsed/expected geometry for inspection without re-parsing/replotting.
    from shapely import to_wkb
    for l,g in images.items():
        (out/('parsed-'+l.replace('.','_')+'.wkb')).write_bytes(to_wkb(g))
    # Edge.Cuts centreline dimensions, not the width of its plotting stroke.
    outline_lines = [LineString([(o.x1,-o.y1),(o.x2,-o.y2)]) for o in parsed['Edge.Cuts'].objects]
    outlines = list(polygonize(unary_union(outline_lines)))
    assert len(outlines) == 1 and outlines[0].equals(box(30,30,126,100)), 'Outline differs'
    antenna = Polygon(next(z['outline'][0]['outline'] for z in source['zones'].values() if z['rule_area']))
    antenna_intersections = {l: images[l].intersection(antenna).area for l in ('F.Cu','In1.Cu','In2.Cu','B.Cu')}
    # Reuse proven pad-opening exposure membership, verify each selected actual exported area.
    exposed = read(args.exposed)
    priority = {'L1','Q1','Q2','U1','U4','U5','U8','C60','C64','C65','C67'}
    vip = []
    for p in exposed['via_pad_pairs']:
        if not p['bore_intersects_opening'] or p['ref'] not in priority:
            continue
        pad = snapshot['pads'][p['pad_uuid']]
        side = p['side']
        opening = unary_union([Polygon(poly) for poly in pad['polygons'][side]])
        bore = Point(p['via_position_mm']).buffer(p['via_bore_mm']/2, quad_segs=512)
        area = opening.intersection(bore)
        vip.append(dict(reference=p['ref'], pin=p['pin'], via_uuid=p['via_uuid'], side=side,
                        opening_overlap_mm2=area.area,
                        missing_mask_mm2=area.difference(images[side[0]+'.Mask'].buffer(TOL)).area,
                        missing_copper_mm2=area.difference(images[side].buffer(TOL)).area))
    # Holes are subtractive drill instructions, not copper/mask closures.
    # Verify connector pad rings separately from the exact drill count.
    component_pad_checks = []
    for uid,p in snapshot['pads'].items():
        if manifest['pads'][uid]['type'] != 'PT_PTH':
            continue
        checks = {l: unary_union([Polygon(v) for v in polys]).difference(images[l].buffer(TOL)).area
                  for l,polys in p['polygons'].items() if l in images}
        component_pad_checks.append(dict(uuid=uid,reference=p['ref'],pin=p['pin'],missing_copper_mm2=checks))
    # A net-agnostic physical-island spacing screen complements source DRC.
    # It includes same-net islands and therefore cannot diagnose net shorts.
    island_gaps = {}
    from shapely.strtree import STRtree
    for layer in ('F.Cu','In1.Cu','In2.Cu','B.Cu'):
        g=images[layer]
        polys=[v for v in (list(g.geoms) if hasattr(g,'geoms') else [g])
               if v.geom_type=='Polygon' and v.area>1e-8]
        tree=STRtree(polys)
        pairs=tree.query(polys,predicate='dwithin',distance=.2)
        values=[polys[i].distance(polys[j]) for i,j in zip(*pairs) if i<j]
        island_gaps[layer]=dict(islands=len(polys), minimum_distinct_island_gap_mm=min(values) if values else None,
                               scope='Net-agnostic copper-island distance; includes same-net islands, complements accepted native DRC.')
    result = dict(zip_sha256=inputs[args.zip], source_pcb_sha256=EXPECTED_PCB,
                  parser_versions=dict(gerbonara=gerbonara.__version__,shapely=shapely.__version__),
                  parser_warnings=parser_warnings, numerical_comparison_tolerance_mm=TOL,
                  npth_copper_placeholder_disposition='12 NPTH hole-sized native placeholders omitted from copper plot; each proven entirely consumed by its own NPTH drill. Mask openings retained and compared.',
                  outline=dict(bounds_mm=list(outlines[0].bounds),width_mm=96,height_mm=70,closed=True),
                  drill_comparison=drill_compare, via_count=len(snapshot['vias']),
                  via_drill_counts=dict(Counter(str(v['drill']) for v in snapshot['vias'].values())),
                  geometry_comparison=compare, antenna_keepout_copper_mm2=antenna_intersections,
                  copper_island_spacing=island_gaps,
                  priority_via_in_pad=vip, component_pad_checks=component_pad_checks,
                  scope_limits=['Gerbers do not prove physical epoxy filling, copper capping, plating or thermal performance.',
                                'No upload/order CAM preview or manufacturer process acceptance obtained.',
                                'Legend/paste are parsed/rendered; electrical copper/mask compared to accepted native polygons.'])
    result['pass_export_geometry'] = (all(v['pass_geometry'] for v in drill_compare.values())
        and all(v['pass_geometry'] for v in compare.values())
        and all(v < 1e-8 for v in antenna_intersections.values())
        and all(p['missing_mask_mm2'] < 1e-8 and p['missing_copper_mm2'] < 1e-8 for p in vip))
    write(out/'cam-review.json', result)
    render(images, drills, snapshot, out)
    after = {p: sha(p) for p in inputs}
    preserved = all(sha(p) == h for p,h in protection.items()) and after == inputs
    write(out/'preservation.json', dict(inputs_before=inputs, inputs_after=after,
        protected_files=protection, all_preserved=preserved))
    assert preserved, 'Read-only source preservation failure'
    print(json.dumps(dict(pass_export_geometry=result['pass_export_geometry'],drills=drill_compare,
                          layers=compare,antenna=antenna_intersections)), flush=True)


def render(images, drills, snapshot, out):
    """Render independent parsed geometry; no CAD viewer or image manipulation."""
    from PIL import Image, ImageDraw, ImageFont
    from shapely.geometry import box,Point,LineString
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
    def panel(bounds, width, layers, title):
        x0,y0,x1,y1=bounds
        scale=width/(x1-x0)
        im=Image.new('RGB',(width+40,round((y1-y0)*scale)+65),'#17222c')
        d=ImageDraw.Draw(im)
        def xy(p): return (20+(p[0]-x0)*scale,45+(p[1]-y0)*scale)
        def geom(g,color):
            if g.is_empty:return
            if g.geom_type=='Polygon':
                d.polygon([xy(p) for p in g.exterior.coords],fill=color)
                for hole in g.interiors:d.polygon([xy(p) for p in hole.coords],fill='#17222c')
            elif hasattr(g,'geoms'):
                for part in g.geoms:geom(part,color)
        for layer,color in layers:
            geom(images[layer].intersection(box(*bounds)),color)
        for kind,f in drills.items():
            for o in f.objects:
                k=drill_key(o)
                g=(Point(k[1]).buffer(k[0]/2,quad_segs=64) if k[1]==k[2]
                   else LineString([k[1],k[2]]).buffer(k[0]/2,quad_segs=64))
                if g.intersects(box(*bounds)):geom(g.intersection(box(*bounds)),'#090c10' if kind=='PTH' else '#d6e1ec')
        d.text((14,10),title,font=font,fill='white')
        return im
    for layer in ('F.Cu','In1.Cu','In2.Cu','B.Cu','F.Mask','B.Mask','F.SilkS','B.SilkS','F.Paste','B.Paste'):
        im=panel((29,29,127,101),1100,[(layer,'#d5ad51')],layer+' / parsed owner ZIP / top coordinate view')
        im.save(out/('CAM-'+layer.replace('.','_')+'.png'))
    refs=['L1','Q1','Q2','U1','U4','U5','U8','C60','C64','C65','C67','J7','J1']
    for ref in refs:
        pads=[p for p in snapshot['pads'].values() if p['ref']==ref]
        coords=[v for p in pads for poly in p['polygons'].get('F.Cu',[]) for v in poly]
        bounds=(min(p[0] for p in coords)-1,min(p[1] for p in coords)-1,
                max(p[0] for p in coords)+1,max(p[1] for p in coords)+1)
        panel(bounds,850,[('F.Cu','#866d32'),('F.Mask','#e0c98b')],
              ref+' / copper brown, mask openings pale, drill dark').save(out/('detail-'+ref+'.png'))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('zip','board','context','layout','manifest','preservation','exposed','output','deps'):
        p.add_argument('--'+name,required=True)
    a=p.parse_args()
    import sys
    sys.path.insert(0,str(Path(a.deps).resolve()))
    review(a)


if __name__=='__main__':
    main()
