"""Read-only stencil audit of owner CAM, using accepted native JSON exports.

No native KiCad imports, CAD parsing, fabrication generation or input writes.
Third-party imports are deferred; --deps selects the already installed CAM runtime.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import warnings
import zipfile

from .gerber_review import EXPECTED_PCB, compose, difference, expected_geometry, read, sha, write

F5 = 'U7 U8 Q10 L3 R60 R61 R62 R63 C60 C61 C62 C63 C64 C65 C66 C67 C68 C69 J8'.split()
DNP = 'C20 C22 C24 C25'.split()
CRITICAL = 'IC1 U1 U2 U3 U4 U5 U6 U7 U8 Q1 Q2 Q10 L1 L2 L3 J7'.split()


def parts(g):
    if g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g]
    return [p for child in g.geoms for p in parts(child)]


def indicators(g, thickness=.1):
    """Actual area/perimeter AR; rectangle AR also given for comparison only."""
    coords = list(g.minimum_rotated_rectangle.exterior.coords)
    a, b = sorted(math.dist(coords[i], coords[i+1]) for i in range(2))
    return dict(width_mm=a, length_mm=b, area_mm2=g.area,
                perimeter_mm=g.length, area_ratio=g.area/(g.length*thickness),
                rectangular_area_ratio=a*b/(2*thickness*(a+b)),
                aspect_ratio=a/thickness, nominal_wet_paste_mm3=g.area*thickness,
                bounds_mm=g.bounds)


def associate(g, ref, pad_shapes, snapshot):
    """Ref attribute plus maximum geometric intersection, preserving physical UUID."""
    hits = sorted(((g.intersection(p).area, uid) for uid,p in pad_shapes.items()
                   if snapshot['pads'][uid]['ref']==ref and g.intersects(p)), reverse=True)
    if not hits or hits[0][0] < 1e-9:
        return None
    if len(hits)>1 and abs(hits[0][0]-hits[1][0])<1e-9:
        raise ValueError('Ambiguous physical pad assignment: '+ref)
    return hits[0][1]


def local_intersection(g, image):
    # Avoid repeating a full-board polygon overlay for every tiny terminal.
    from shapely import clip_by_rect
    a,b,c,d=g.bounds
    return g.intersection(clip_by_rect(image,a-.01,b-.01,c+.01,d+.01))


def closest_gap(index, shapes, bounds):
    a,b,c,d=bounds[index]
    def lower(j):
        e,f,g,h=bounds[j]
        return math.hypot(max(0,e-c,a-g),max(0,f-d,b-h))
    ordered=sorted((lower(j),j) for j in range(len(shapes)) if j!=index)
    best,nearest=math.inf,None
    for low,j in ordered:
        if low>best+1e-10:
            break
        distance=shapes[index].distance(shapes[j])
        if distance<best:
            best,nearest=distance,j
    return best,nearest


def audit(args):
    from gerbonara import GerberFile
    import gerbonara
    import shapely
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    out=Path(args.output)
    if out.exists():
        raise ValueError('A fresh output directory is required')
    out.mkdir(parents=True)
    prior=read(args.accepted_inputs)
    # Binding applies to archived accepted exports, not a potentially owner-saved PCB.
    for name in (args.context,args.layout,args.manifest):
        assert sha(name)==prior[name], 'Accepted export drift: '+name
    context,layout,manifest=read(args.context),read(args.layout),read(args.manifest)
    assert context['board_sha256']==manifest['hashes']['ups12v_v4.kicad_pcb']==EXPECTED_PCB
    snapshot=context['snapshot']
    protected=read(args.protection)['protected_before']
    paths=set(protected)|{args.zip,args.board,args.context,args.layout,args.manifest,
                         args.population,args.accepted_inputs,args.protection}
    # Include the loose owner manufacturing files and all ZIPs as they exist now.
    paths.update(str(p) for p in Path(args.zip).parent.rglob('*') if p.is_file())
    before={str(p):sha(p) for p in sorted(paths)}
    write(out/'inputs-before.json',before)
    parsed,images,member_rows,parser_warnings={},{},[],[]
    with zipfile.ZipFile(args.zip) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))
        for info in z.infolist():
            if info.is_dir():
                continue
            data=z.read(info)
            row=dict(member=info.filename,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
            ext=Path(info.filename).suffix.upper()
            if ext in ('.GTP','.GBP','.GTL','.GTS'):
                with warnings.catch_warnings(record=True) as captured:
                    warnings.simplefilter('always')
                    f=GerberFile.from_string(data.decode('utf-8-sig'))
                parser_warnings.extend(str(w.message) for w in captured)
                parsed[ext]=f
                images[ext]=compose(f)
                row.update(objects=len(f.objects),metadata=f.file_attrs)
            member_rows.append(row)
    assert all(k in parsed for k in ('.GTP','.GBP','.GTL','.GTS'))
    write(out/'zip-manifest.json',dict(zip_sha256=sha(args.zip),files=member_rows,
                                      parser_versions=dict(gerbonara=gerbonara.__version__,shapely=shapely.__version__),
                                      parser_warnings=parser_warnings))
    print('CAM parsed; comparing top copper/mask with accepted exports',flush=True)
    expected,_=expected_geometry(snapshot,context,layout,manifest)
    geometry={k:difference(expected[layer],images[k]) for k,layer in (('.GTL','F.Cu'),('.GTS','F.Mask'))}
    write(out/'accepted-top-geometry-comparison.json',geometry)
    pad_shapes={uid:unary_union([Polygon(poly) for poly in p['polygons'].get('F.Cu',[])])
                for uid,p in snapshot['pads'].items() if p['polygons'].get('F.Cu')
                and manifest['pads'][uid]['type']!='PT_NPTH'}
    apertures,shapes,unassigned=[],[],[]
    for index,obj in enumerate(parsed['.GTP'].objects):
        ref=obj.attrs.get('.C',('',))[0]
        g=compose(type('One',(),{'objects':[obj]})())
        for piece in parts(g):
            uid=associate(piece,ref,pad_shapes,snapshot)
            p=snapshot['pads'].get(uid,{})
            row=dict(index=len(apertures),gerber_object=index,ref=ref,pad=p.get('pin'),pad_uuid=uid,
                     gerber_type=type(obj).__name__,aperture_number=getattr(getattr(obj,'aperture',None),'original_number',None),
                     centroid_mm=[piece.centroid.x,piece.centroid.y],**indicators(piece))
            if uid:
                exposed=local_intersection(local_intersection(pad_shapes[uid],images['.GTL']),images['.GTS'])
                row.update(outside_intended_exposed_mm2=piece.difference(exposed.buffer(.00025)).area)
            else:
                unassigned.append(row['index'])
            apertures.append(row)
            shapes.append(piece)
    # Adjacent apertures: nearest separation, including same-number windowpanes.
    bounds=[g.bounds for g in shapes]
    print('Apertures assigned; calculating local exposure and nearest gaps',flush=True)
    for i,row in enumerate(apertures):
        gap,j=closest_gap(i,shapes,bounds)
        row.update(nearest_gap_mm=gap,nearest_aperture=j,
                   nearest_reference=apertures[j]['ref'],nearest_pad=apertures[j]['pad'])
    pad_rows=[]
    for uid,g in pad_shapes.items():
        p=snapshot['pads'][uid]
        local_copper=local_intersection(g,images['.GTL'])
        local_mask=local_intersection(g,images['.GTS'])
        exposed=local_intersection(local_copper,images['.GTS'])
        aps=[r for r in apertures if r['pad_uuid']==uid]
        paste=unary_union([shapes[r['index']] for r in aps])
        stack=manifest['pads'][uid]['padStack']
        pad_rows.append(dict(ref=p['ref'],pad=p['pin'],uuid=uid,position_mm=p['position'],
            native_type=manifest['pads'][uid]['type'],native_has_paste='BL_F_Paste' in stack['layers'],
            copper_land=indicators(g),exposed_area_mm2=exposed.area,
            mask_clipped_land_area_mm2=local_mask.area,
            actual_copper_missing_from_native_land_mm2=g.difference(local_copper.buffer(.00025)).area,
            aperture_count=len(aps),paste_area_mm2=paste.area,
            paste_to_exposed_ratio=paste.area/exposed.area if exposed.area else None,
            aperture_indices=[r['index'] for r in aps]))
    by_ref={}
    for ref in sorted({r['ref'] for r in apertures}|{p['ref'] for p in pad_rows}):
        aps=[r for r in apertures if r['ref']==ref]
        ps=[p for p in pad_rows if p['ref']==ref]
        by_ref[ref]=dict(aperture_count=len(aps),pad_numbers=sorted({r['pad'] for r in aps if r['pad'] is not None}),
                         physical_native_pads=len(ps),paste_area_mm2=sum(r['area_mm2'] for r in aps),
                         min_area_ratio=min((r['area_ratio'] for r in aps),default=None),
                         min_gap_mm=min((r['nearest_gap_mm'] for r in aps),default=None))
    with open(args.population,newline='',encoding='utf-8-sig') as f:
        population=list(csv.DictReader(f))
    masks=[]
    for ref in F5+DNP:
        aps=[r for r in apertures if r['ref']==ref]
        g=unary_union([shapes[r['index']] for r in aps])
        if aps:
            # Proposed cover is bounded 0.10 mm beyond aperture bounding box.
            rect=box(*g.bounds).buffer(.1,join_style=2)
            other=[(rect.distance(shape),a) for a,shape in zip(apertures,shapes) if a['ref']!=ref]
            gap,near=min(other,key=lambda x:x[0])
            bounds=rect.bounds
            overlaps=[dict(ref=a['ref'],pad=a['pad']) for a,shape in zip(apertures,shapes)
                      if a['ref']!=ref and rect.intersection(shape).area>1e-9]
        else:
            gap,near,bounds,overlaps=None,{},None,[]
        masks.append(dict(ref=ref,group='always-DNP' if ref in DNP else 'F5-only',
            F0='BLOCK' if aps else 'NO PASTE ALREADY',
            F5=('BLOCK' if ref in DNP else 'OPEN') if aps else 'NO PASTE ALREADY',
            pad_numbers=by_ref.get(ref,{}).get('pad_numbers',[]),aperture_count=len(aps),
            cover_bounds_mm=bounds,nearest_other_aperture_clearance_mm=gap,
            nearest_other_ref=near.get('ref'),cover_overlaps=overlaps))
    other_dnp=[dict(ref=r['reference'],state=r['state'],**by_ref.get(r['reference'],{}))
               for r in population if r['state']!='FITTED' and r['reference'] not in F5+DNP]
    missing=[p for p in pad_rows if p['native_has_paste'] and not p['aperture_count']]
    unexpected=[p for p in pad_rows if not p['native_has_paste'] and p['aperture_count']]
    connected=[]
    for g in parts(images['.GTP']):
        members=[r for r,shape in zip(apertures,shapes) if g.intersection(shape).area>1e-8]
        connected.append(dict(index=len(connected),references=sorted({r['ref'] for r in members}),
            pads=sorted({str(r['pad']) for r in members}),object_regions=[r['index'] for r in members],
            **indicators(g)))
    result=dict(accepted_pcb_sha256=EXPECTED_PCB,current_pcb_sha256=sha(args.board),
        exact_pcb_hash_matches=sha(args.board)==EXPECTED_PCB,zip_sha256=sha(args.zip),
        accepted_export_top_geometry_matches=all(v['pass_geometry'] for v in geometry.values()),
        top_objects=len(parsed['.GTP'].objects),top_object_regions=len(apertures),
        top_connected_apertures=len(connected),connected_aperture_records=connected,
        bottom_objects=len(parsed['.GBP'].objects),bottom_paste_area_mm2=images['.GBP'].area,
        unassigned_aperture_indices=unassigned,missing_expected_native_paste=missing,
        unexpected_paste_against_native_layers=unexpected,
        outside_exposed_apertures=[r['index'] for r in apertures if r.get('outside_intended_exposed_mm2',0)>1e-8],
        advisory_AR_below_066=[r['index'] for r in apertures if r['area_ratio']<.66],
        aperture_records=apertures,pad_records=pad_rows,reference_summary=by_ref,
        variant_mask_plan=masks,other_unfitted_population=other_dnp)
    write(out/'stencil-audit.json',result)
    def save_csv(name,rows):
        if rows:
            with (out/name).open('w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    save_csv('apertures.csv',apertures)
    save_csv('variant-mask-plan.csv',masks)
    proposal(out,result,shapes,apertures,pad_shapes,snapshot)
    render(out,images,shapes,apertures,pad_rows,pad_shapes)
    after={p:sha(p) for p in before}
    write(out/'preservation.json',dict(before=before,after=after,all_preserved=before==after))
    assert before==after,'Input preservation failure'
    print(json.dumps({k:result[k] for k in ('top_objects','top_connected_apertures','bottom_objects',
        'exact_pcb_hash_matches','accepted_export_top_geometry_matches','unassigned_aperture_indices',
        'outside_exposed_apertures','advisory_AR_below_066')}),flush=True)


def proposal(out,result,shapes,rows,pad_shapes,snapshot):
    """Exact mathematical proposal only: neither CAD nor manufacturing output."""
    from shapely.geometry import box
    from shapely.affinity import rotate,translate
    from shapely.ops import unary_union
    records=[]
    def rounded(w,h,x,y,angle):
        g=box(-w/2+.05,-h/2+.05,w/2-.05,h/2-.05).buffer(.05,quad_segs=128)
        return translate(rotate(g,angle,origin=(0,0)),xoff=x,yoff=y)
    for ref in ('Q1','Q2','Q10','U4'):
        ps=[p for p in result['pad_records'] if p['ref']==ref]
        p=(next(p for p in ps if p['pad']=='9') if ref!='U4' else
           max((p for p in ps if p['pad']=='2'),key=lambda p:p['exposed_area_mm2']))
        old=unary_union([shapes[i] for i in p['aperture_indices']])
        x,y=p['position_mm']
        if ref!='U4':
            drain=[q['position_mm'] for q in ps if q['pad'] in ('5','6','7','8')]
            vx,vy=sum(q[0] for q in drain)/4-x,sum(q[1] for q in drain)/4-y
            norm=math.hypot(vx,vy); vx,vy=vx/norm,vy/norm
            ux,uy=vy,-vx
            centers=[(x+sign*.625*ux-.1*vx,y+sign*.625*uy-.1*vy) for sign in (-1,1)]
            angle=math.degrees(math.atan2(uy,ux))
            specs=[(1.0,1.5,cx,cy,angle) for cx,cy in centers]
        else:
            # Accepted tab is globally X=2.0, Y=3.8 mm; exact current orientation.
            assert abs(old.bounds[2]-old.bounds[0]-2)<1e-6
            assert abs(old.bounds[3]-old.bounds[1]-3.8)<1e-6
            specs=[(.75,1.5,x+dx,y+dy,0) for dx in (-.5,.5) for dy in (-.9,.9)]
        proposed=[rounded(*s) for s in specs]
        g=unary_union(proposed)
        others=[shape for r,shape in zip(rows,shapes) if r['pad_uuid']!=p['uuid']]
        records.append(dict(ref=ref,pad=p['pad'],physical_pad_uuid=p['uuid'],
            old_object_region_indices=p['aperture_indices'],old_nominal_wet_paste_mm3=old.area*.1,
            new_nominal_wet_paste_mm3=g.area*.1,exposed_land_area_mm2=p['exposed_area_mm2'],
            new_paste_to_exposed_ratio=g.area/p['exposed_area_mm2'],
            new_windows=[dict(nominal_width_mm=w,nominal_height_mm=h,center_mm=[cx,cy],rotation_deg=ang,
                              corner_radius_mm=.05,**indicators(shape))
                         for (w,h,cx,cy,ang),shape in zip(specs,proposed)],
            min_other_paste_gap_mm=min(g.distance(q) for q in others),
            min_internal_web_mm=min(a.distance(b) for i,a in enumerate(proposed) for b in proposed[i+1:]),
            outside_old_paste_mm2=g.difference(old).area))
        assert g.difference(old).area<1e-8
        assert records[-1]['min_other_paste_gap_mm']>=.149999
    write(out/'scratch-only-correction-proposal.json',dict(status='PROPOSAL ONLY - NOT IMPLEMENTED',
        source_zip_sha256=result['zip_sha256'],current_board_sha256=result['current_pcb_sha256'],
        accepted_geometry_pcb_sha256=EXPECTED_PCB,changes=records,
        unchanged='All other paste including Q drain pins5-8, U1 all61 apertures, L1 pads1/2; all copper/mask/CAD/rules/BOM/drills/ZIP.'))


def render(out,images,shapes,rows,pads,pad_shapes):
    from PIL import Image,ImageDraw,ImageFont
    from shapely.geometry import box
    from shapely.ops import unary_union
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
    for ref in CRITICAL:
        group=[p for p in pads if p['ref']==ref]
        if not group:
            continue
        extent=unary_union([pad_shapes[p['uuid']] for p in group]).buffer(.8).bounds
        x0,y0,x1,y1=extent
        scale=min(1000/(x1-x0),900/(y1-y0))
        im=Image.new('RGB',(1040,round((y1-y0)*scale)+105),'#14212b')
        d=ImageDraw.Draw(im)
        def xy(p):return (20+(p[0]-x0)*scale,65+(p[1]-y0)*scale)
        def draw(g,fill=None,outline=None):
            for poly in parts(g.intersection(box(*extent))):
                pts=[xy(p) for p in poly.exterior.coords]
                if fill:d.polygon(pts,fill=fill)
                if outline:d.line(pts,fill=outline,width=2)
                for hole in poly.interiors:
                    if fill:d.polygon([xy(p) for p in hole.coords],fill='#14212b')
        draw(images['.GTL'],fill='#95703b')
        draw(images['.GTS'],outline='#00c5e0')
        draw(images['.GTP'],fill='#e6e5dd')
        for p in group:
            c=pad_shapes[p['uuid']].centroid
            x,y=xy((c.x,c.y))
            d.text((x,y),p['pad'],font=small,fill='#ff4545',anchor='mm')
        d.text((16,8),ref+' | top view: copper brown / mask cyan / paste white / pad red',font=font,fill='white')
        d.text((16,34),f'X {x0:.3f}..{x1:.3f} mm; Y {y0:.3f}..{y1:.3f} mm; Y increases downward',font=small,fill='white')
        d.text((16,im.height-27),'Filled/capped vias assumed planar; copper/mask/paste from actual ZIP, labels from accepted native export.',font=small,fill='white')
        im.save(out/('overlay-'+ref+'.png'))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('zip','board','context','layout','manifest','accepted-inputs','population','protection','output','deps'):
        p.add_argument('--'+name,required=True)
    args=p.parse_args()
    import sys
    sys.path.insert(0,str(Path(args.deps).resolve()))
    audit(args)


if __name__=='__main__':
    main()
