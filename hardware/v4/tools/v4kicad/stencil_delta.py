"""Independent actual-CAM proof of the four-land native scratch correction."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from .gerber_review import compose,difference,read,sha,write
from .safety import require
from .stencil_review import indicators,parts
from .stencil_scratch import SOURCE_SHA,PROPOSAL_SHA,validate_proposal

GEOMETRY_TOL_MM=.000005  # 5 nm numerical comparison, not a fabrication tolerance.


def window_polygon(w):
    from shapely.geometry import box
    from shapely.affinity import rotate,translate
    a,b,r=w['nominal_width_mm'],w['nominal_height_mm'],w['corner_radius_mm']
    g=box(-a/2+r,-b/2+r,a/2-r,b/2-r).buffer(r,quad_segs=512)
    return translate(rotate(g,w['rotation_deg'],origin=(0,0)),
                     xoff=w['center_mm'][0],yoff=w['center_mm'][1])


def compare(args):
    from gerbonara import GerberFile
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    out=Path(args.output)
    require(not out.exists(),'Fresh CAM verification directory required');out.mkdir(parents=True)
    require(sha(args.proposal)==PROPOSAL_SHA,'Reviewed proposal drift')
    proposal=read(args.proposal);changes=validate_proposal(proposal)
    require(sha(args.zip)==proposal['source_zip_sha256'],'Owner ZIP drift')
    audit=read(args.audit)
    require(audit['zip_sha256']==sha(args.zip),'Prior aperture map does not bind actual ZIP')
    inputs={str(p):sha(p) for p in (args.proposal,args.zip,args.audit,args.candidate_gtp,args.native_before)}
    write(out/'inputs-before.json',inputs)
    with zipfile.ZipFile(args.zip) as z:
        old_files={ext:GerberFile.from_string(z.read(next(n for n in z.namelist() if n.endswith(ext))).decode('utf-8-sig'))
                   for ext in ('.GTP','.GTL','.GTS')}
    old_file=old_files['.GTP'];new_file=GerberFile.open(args.candidate_gtp)
    old_shapes=[compose(type('Single',(),{'objects':[o]})()) for o in old_file.objects]
    old_image=compose(old_file);actual=compose(new_file)
    removed={i for r in changes for i in r['old_object_region_indices']}
    require(len(removed)==4,'Exactly four original full-paste objects must be replaced')
    for r in changes:
        for i in r['old_object_region_indices']:
            row=audit['aperture_records'][i]
            require(row['pad_uuid']==r['physical_pad_uuid'] and row['gerber_object']==i,
                    'Original physical pad/object attribution mismatch')
    retained=unary_union([g for i,g in enumerate(old_shapes) if i not in removed])
    windows={r['ref']:[window_polygon(w) for w in r['new_windows']] for r in changes}
    expected=unary_union([retained]+[g for group in windows.values() for g in group])
    whole=difference(expected,actual,GEOMETRY_TOL_MM)
    write(out/'whole-paste-comparison.json',whole)
    require(whole['pass_geometry'],'Actual scratch GTP differs from exact reviewed four-land plan')
    allowed=unary_union([old_shapes[i] for i in removed])
    outside_delta=old_image.symmetric_difference(actual).difference(allowed.buffer(GEOMETRY_TOL_MM))
    require(outside_delta.area<1e-8,'Paste changed outside four authorized physical lands')
    retained_checks=[]
    buffered=actual.buffer(GEOMETRY_TOL_MM)
    for i,g in enumerate(old_shapes):
        if i not in removed:
            missing=g.difference(buffered).area
            require(missing<1e-8,'A retained original pad paste contribution changed')
            retained_checks.append(dict(original_object=i,ref=audit['aperture_records'][i]['ref'],
                                       pad=audit['aperture_records'][i]['pad'],missing_mm2=missing))
    actual_parts=parts(actual)
    details=[]
    for r in changes:
        expected_windows=windows[r['ref']]
        measured=[]
        measured_shapes=[]
        for w,g in zip(r['new_windows'],expected_windows):
            pieces=parts(actual.intersection(g.buffer(.025)))
            require(len(pieces)==1,'Window is missing, joined or unexpectedly fragmented')
            a=pieces[0];measured_shapes.append(a)
            d=difference(g,a,GEOMETRY_TOL_MM)
            require(d['pass_geometry'],'Measured window differs from full-precision proposal')
            measured.append(dict(proposed=w,actual=indicators(a),comparison=d))
        own=unary_union(measured_shapes)
        other=[g for g in actual_parts if not own.buffer(GEOMETRY_TOL_MM).covers(g)]
        original=unary_union([old_shapes[i] for i in r['old_object_region_indices']])
        require(own.difference(original.buffer(GEOMETRY_TOL_MM)).area<1e-8,'Window outside original aperture')
        internal=min(a.distance(b) for i,a in enumerate(measured_shapes) for b in measured_shapes[i+1:])
        external=min(own.distance(g) for g in other)
        require(internal>=.24999 and external>=.19999,'Insufficient actual web/neighbor gap')
        details.append(dict(ref=r['ref'],pad=r['pad'],physical_pad_uuid=r['physical_pad_uuid'],
            original_object_regions=r['old_object_region_indices'],actual_window_count=len(measured_shapes),
            original_paste_area_mm2=original.area,new_paste_area_mm2=own.area,
            paste_to_exposed_ratio=own.area/r['exposed_land_area_mm2'],
            min_internal_web_mm=internal,min_retained_neighbor_gap_mm=external,
            old_paste_actually_removed_mm2=original.difference(actual).area,
            actual_window_records=measured))
        require(details[-1]['old_paste_actually_removed_mm2']>1,'Original full paste was not removed')
    # Reference-level DNP presence is independent of the intentionally changed Q10 shape.
    variant=[]
    for row in audit['variant_mask_plan']:
        shapes=[old_shapes[a['gerber_object']] for a in audit['aperture_records'] if a['ref']==row['ref']]
        old=unary_union(shapes)
        changed=row['ref']=='Q10'
        missing=old.difference(buffered).area if not changed else None
        if not changed:require(missing<1e-8,'Variant/DNP aperture presence changed')
        variant.append(dict(ref=row['ref'],original_regions=row['aperture_count'],
            present_before=bool(shapes),present_after=actual.intersects(old) if shapes else False,
            unchanged=not changed,approved_Q10_shape_change=changed,missing_retained_mm2=missing))
    result=dict(status='PASS - SCRATCH ONLY',source_board_sha256=SOURCE_SHA,
        candidate_gtp_sha256=sha(args.candidate_gtp),proposal_sha256=PROPOSAL_SHA,
        tolerance_mm=GEOMETRY_TOL_MM,whole_paste=whole,
        before_physical_apertures=len(parts(old_image)),after_physical_apertures=len(actual_parts),
        original_objects=len(old_file.objects),new_objects=len(new_file.objects),
        exactly_four_original_full_objects_replaced=True,unchanged_original_pad_contributions=len(retained_checks),
        outside_authorized_land_delta_mm2=outside_delta.area,
        original_paste_union_area_mm2=old_image.area,new_paste_union_area_mm2=actual.area,
        min_after_area_ratio=min(indicators(g)['area_ratio'] for g in actual_parts),
        physical_land_delta=details,variant_presence=variant)
    write(out/'physical-aperture-delta.json',result)
    write(out/'retained-contributions.json',retained_checks)
    before=read(args.native_before)
    copper,mask=compose(old_files['.GTL']),compose(old_files['.GTS'])
    render(out,changes,before,old_image,actual,copper,mask)
    after={p:sha(p) for p in inputs}
    require(after==inputs,'CAM analysis modified an input')
    write(out/'preservation.json',dict(before=inputs,after=after,all_preserved=True))
    print(json.dumps({k:result[k] for k in ('status','before_physical_apertures','after_physical_apertures',
        'unchanged_original_pad_contributions','outside_authorized_land_delta_mm2','min_after_area_ratio')}))


def render(out,changes,before,old,new,copper,mask):
    from PIL import Image,ImageDraw,ImageFont
    from shapely.geometry import Polygon,box
    from shapely.ops import unary_union
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    for r in changes:
        ps=[p for p in before['pads'].values() if p['ref']==r['ref']]
        land=unary_union([Polygon(poly) for p in ps for poly in p['polygons'].get('F.Cu',[])])
        x0,y0,x1,y1=land.buffer(.5).bounds
        scale=min(760/(x1-x0),900/(y1-y0));height=round((y1-y0)*scale)+100
        image=Image.new('RGB',(1620,height),'#17222c');draw=ImageDraw.Draw(image)
        for side,(paste,title,color) in enumerate(((old,'BEFORE / owner GTP','#f0e7d3'),(new,'AFTER / native scratch GTP','#6edda5'))):
            ox=20+side*810
            def xy(p):return (ox+(p[0]-x0)*scale,65+(p[1]-y0)*scale)
            def paint(g,color,outline=False):
                for poly in parts(g.intersection(box(x0,y0,x1,y1))):
                    points=[xy(p) for p in poly.exterior.coords]
                    if outline:draw.line(points,fill=color,width=2)
                    else:draw.polygon(points,fill=color)
                    for ring in poly.interiors:
                        if not outline:draw.polygon([xy(p) for p in ring.coords],fill='#17222c')
            paint(copper,'#8f6b37');paint(mask,'#00bdd7',True);paint(paste,color)
            draw.text((ox,10),r['ref']+' '+title,font=font,fill='white')
            draw.text((ox,36),'Copper brown / mask cyan / actual paste filled',font=small,fill='white')
            for p in ps:
                draw.text(xy(p['position']),p['pin'],font=small,fill='#ff4141',anchor='mm')
        draw.text((20,height-27),'Same top-view scale. The four approved physical lands only; all retained neighboring paste is shown.',font=small,fill='white')
        image.save(out/('before-after-'+r['ref']+'.png'))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('zip','proposal','audit','candidate-gtp','native-before','output','deps'):
        p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args()
    import sys
    sys.path.insert(0,str(a.deps.resolve()))
    compare(a)


if __name__=='__main__':main()
