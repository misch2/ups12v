"""Export-only local CC2/vendor-clearance evidence; no native CAD or import I/O."""
from collections import Counter
from pathlib import Path
import argparse
import copy
import math

from .safety import digest, read_json, require, write_json
from .plan_validation import inventory, nearby, separation, shape, LAYERS
from .prefab_review import audit
from .review_compare import warning_rows

SHELL = 'a795896d-5791-49b7-91ae-4207a4427483'


def selected_screen(context, ids, shell=SHELL):
    """Analytic capsules/native outside polygons; every drill spans all layers."""
    copper, holes = inventory(context['snapshot'], context)
    selected = [c for c in copper if c['id'] in ids]
    require(len(selected) == len(ids) and selected, 'Selected straight copper missing')
    hole = next(h for h in holes if h['id'] == shell)
    rows = []
    for c in selected:
        other = [o for o in copper if o['layer'] == c['layer'] and o['net'] != c['net']]
        # Include all physical drills, irrespective of copper layer/net.
        nearest = lambda objects: min((dict(uuid=o['id'], net=o['net'], kind=o['kind'],
                                            gap_mm=separation(c, o)) for o in objects),
                                     key=lambda r:r['gap_mm'])
        rows.append(dict(uuid=c['id'], shell_gap_mm=separation(c, hole),
                         different_net_copper=nearest(other), physical_drill=nearest(holes),
                         different_net_drill=nearest([h for h in holes if h['net']!=c['net']])))
    local = shape('window', '', '*', [[114,73],[125,73],[125,90],[114,90]], polygon=True)
    return dict(selected=rows, shell_min_gap_mm=min(r['shell_gap_mm'] for r in rows),
                local_copper_by_layer={l:dict(Counter(c['kind'] for c in copper
                    if c['layer']==l and nearby(c, local, 0))) for l in LAYERS},
                local_physical_drills=sum(nearby(h, local, 0) for h in holes))


def physical_fill_equal(before, after):
    # Compare actual native copper contours and every hole, not just zone outlines.
    return before['fills'] == after['fills']


def illustration(before, after, output):
    """Exact exported In2 geometry rendered with Pillow; no existing image edits."""
    from PIL import Image, ImageDraw, ImageFont
    scale=145; bounds=(116.8,74.8,120.45,80.05)
    panel_w=610; top=90
    image=Image.new('RGB',(1220,980),'white'); d=ImageDraw.Draw(image)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24)
    def text(x,y,s,f=font,fill='#202020'):d.text((x,y),s,font=f,fill=fill)
    for i,(c,label,gap,color) in enumerate([(before,'BEFORE: accepted production',.290,'#be3c30'),
                                            (after,'AFTER: scratch candidate',.350,'#087f5b')]):
        ox=20+i*panel_w
        def xy(p):return (round(ox+(p[0]-bounds[0])*scale),round(top+(p[1]-bounds[1])*scale))
        def line(points,width,color):
            pts=[xy(p) for p in points]; w=max(1,round(width*scale))
            d.line(pts,fill=color,width=w)
            for x,y in pts:d.ellipse((x-w/2,y-w/2,x+w/2,y+w/2),fill=color)
        copper,holes=inventory(c['snapshot'],c)
        window=shape('window','','',[[bounds[0],bounds[1]],[bounds[2],bounds[1]],
                                     [bounds[2],bounds[3]],[bounds[0],bounds[3]]],polygon=True)
        # A separate clipped scene keeps off-window tracks out of labels/panels.
        scene=Image.new('RGB',image.size,'white'); d=ImageDraw.Draw(scene)
        for item in copper:
            if item['layer']!='In2.Cu' or not nearby(item,window,0):continue
            col=color if item['net']=='USB_CC2' else '#bcc6ce'
            if item['polygon']:d.polygon([xy(p) for p in item['points']],fill=col)
            else:line(item['points'],2*item['radius'],col)
        for h in holes:
            if nearby(h,window,0):line(h['points'],2*h['radius'],'#ffffff')
        image.paste(scene.crop((ox,top,ox+round((bounds[2]-bounds[0])*scale),
                                top+round((bounds[3]-bounds[1])*scale))),(ox,top))
        d=ImageDraw.Draw(image)
        text(ox,12,label,title)
        text(ox,45,'In2.Cu + physical drills; dimensions in mm',small)
        # Physical slot edge and track edge, at the slot's centre height.
        a=xy([119.420,76.675]); b=xy([119.420+gap,76.675])
        d.line([a,b],fill='#151515',width=2)
        for x,y in [a,b]:d.line([(x,y-10),(x,y+10)],fill='#151515',width=2)
        text(ox+255,xy([0,76.675])[1]-48,f'{gap:.3f} drill-to-Cu',small)
        text(ox+30,xy([0,77.1])[1],'J7 upper shell slot',small)
        text(ox+30,xy([0,77.3])[1],'right drill edge X119.420',small)
        text(ox+30,xy([0,78.2])[1],'USB_CC2 width 0.180',small)
        text(ox+30,xy([0,78.4])[1],f'vertical X{119.8 if i==0 else 119.86:.3f}',small)
        text(ox,880,'Fixed endpoints (119.050,75.300) / (118.740,79.725)',small)
    text(20,915,'Grey: other In2 copper; white: drilled holes. Native polygon evidence, not Gerber/CAM.',small)
    text(20,944,'Only three CC2 tracks replaced. Actual In1 PGND fill, including all holes, is unchanged.',small)
    image.save(output)


def main():
    p=argparse.ArgumentParser()
    for k in ['context','candidate','manifest','plan','output-dir']:
        p.add_argument('--'+k,required=True,type=Path)
    a=p.parse_args(); c=read_json(a.context); root=a.candidate; out=a.output_dir
    require(not (out/'geometry-screen.json').exists(),'Fresh review outputs required')
    binding=read_json(root/'context.json'); plan=read_json(a.plan)
    require(digest(binding['source'])==c['board_sha256']==plan['baseline_sha256'],'Source drift')
    before=read_json(root/'before.json'); after=read_json(root/'final-snapshot.json')
    require(before==c['snapshot'],'Independent source export mismatch')
    require(read_json(root/'plan.json')==plan,'Candidate plan mismatch')
    final=copy.deepcopy(c); final['snapshot']=after; final['board_sha256']=digest(binding['board'])
    ids=set(after['tracks'])-set(before['tracks'])
    b=selected_screen(c,set(plan['remove_tracks'])); f=selected_screen(final,ids)
    lb=read_json(root/'layout-before.json'); lf=read_json(root/'layout-final.json')
    require(physical_fill_equal(lb,lf),'Physical filled copper changed; STOP')
    require(lb['plane_samples']==lf['plane_samples'] and lb['via_plane_samples']==lf['via_plane_samples'],
            'Local plane/return samples changed; STOP')
    # Repeat the vendor-specific board screen from independent native exports.
    m=read_json(a.manifest)
    for name,ctx,layout in [('before',c,lb),('after',final,lf)]:
        report=audit(ctx,m,layout); write_json(out/f'vendor-{name}.json',report)
    vendor=read_json(out/'vendor-after.json')
    require(not vendor['pth_track_below_published_screen'] and not vendor['pth_plane_below_published_screen'],
            'Remaining vendor PTH clearance failure; STOP')
    require(f['shell_min_gap_mm']>=.350-1e-6,'Target margin missed; STOP')
    require(all(r['different_net_copper']['gap_mm']>=.1-1e-6 and
                r['different_net_drill']['gap_mm']>=c['profile']['hole_clearance']-1e-6 for r in f['selected']),
            'Local physical clearance failed; STOP')
    warnings={}
    for kind in ['drc','erc']:
        accepted=read_json(Path('hardware/v4/evidence/phase4-18-final-production-native')/(kind+'.json'))
        current=read_json(root/(kind+'.json'))
        warnings[kind]=warning_rows(accepted,kind)==warning_rows(current,kind)
        require(warnings[kind],f'Changed isolated {kind} warning identities; STOP')
    length=lambda rows:sum(math.dist(t['start'],t['end']) for t in rows)
    result=dict(source_sha256=c['board_sha256'],candidate_sha256=final['board_sha256'],
                before=b,after=f,actual_fill_polygons_and_holes_equal=True,
                plane_and_via_samples_equal=True,matched_isolated_warning_identities_equal=warnings,
                removed=plan['remove_tracks'],added={u:after['tracks'][u] for u in sorted(ids)},
                length_delta_mm=length(after['tracks'][u] for u in ids)-length(plan['remove_tracks'].values()),
                layer_fill_counts={layer:sum(len(z['layers'].get(layer,[])) for z in lf['fills'].values())
                                   for layer in LAYERS},
                basis='KiCad10 native saved/reloaded exports; analytic drilled capsules and outside copper polygons <=100nm; no CAM or manufactured measurements')
    write_json(out/'geometry-screen.json',result)
    illustration(c,final,out/'J7-before-after.png')
    write_json(out/'review-input-hashes.json',{str(x):digest(x) for x in
        [a.context,a.manifest,a.plan,root/'final-snapshot.json',root/'layout-final.json',Path(__file__)]})
    print(f"CC2 shell clearance {b['shell_min_gap_mm']:.3f} -> {f['shell_min_gap_mm']:.3f}mm; fills/warnings preserved")


if __name__=='__main__':main()
