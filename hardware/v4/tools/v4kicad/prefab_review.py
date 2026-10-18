"""Read-only DFM screening of already accepted native/IPC JSON exports.

No KiCad import, launch, save, CAD parsing or geometry regeneration. Uses the
existing polygon/capsule helpers; findings are screens, not fabrication approval.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import argparse
import json
import math

from .plan_validation import inventory, nearby, separation, shape
from .safety import read_json, write_json, digest, require


def nm(pair):
    return [int(pair.get(k, 0))/1e6 for k in ('xNm', 'yNm')]


def ring(pad):
    """Concentric regular padstack only; custom/offset geometry is unevaluated."""
    ps=pad['padStack']; hole=nm(ps['drill'].get('diameter', {}))
    result=[]
    for layer in ps['copperLayers']:
        if layer['shape'] not in {'PSS_CIRCLE','PSS_OVAL','PSS_RECTANGLE','PSS_ROUNDRECT'} or any(nm(layer.get('offset',{}))):
            return None
        size=nm(layer['size'])
        result.append(min((size[i]-hole[i])/2 for i in (0,1)))
    return min(result) if result else None


def audit(context, manifest, layout):
    s=context['snapshot']; copper,holes=inventory(s,context)
    types={u:p['type'] for u,p in manifest['pads'].items()}
    pads=s['pads']
    def label(uid):
        p=pads.get(uid)
        return dict(uuid=uid,ref=p['ref'],pin=p['pin'],position=p['position'],net=p['net']) if p else dict(uuid=uid,net=s['vias'].get(uid,{}).get('net'))
    pairs=[]
    for a,b in combinations(holes,2):
        if not nearby(a,b,.45):continue
        d=separation(a,b)
        limit=.45 if types.get(a['id'])=='PT_PTH' and types.get(b['id'])=='PT_PTH' else .2
        if d<limit-1e-6:pairs.append(dict(a=label(a['id']),b=label(b['id']),gap_mm=d,screen_mm=limit))
    # Focus on PTH-to-track, the published threshold exceeds accepted project .25.
    pth=[]
    for h in holes:
        if types.get(h['id'])!='PT_PTH':continue
        for c in copper:
            if c['kind']!='track' or c['net']==h['net'] or not nearby(h,c,.3):continue
            limit=.3 if c['layer'] in {'In1.Cu','In2.Cu'} else .28
            d=separation(h,c)
            if d<limit-1e-6:pth.append(dict(hole=label(h['id']),track=c['id'],net=c['net'],layer=c['layer'],gap_mm=d,screen_mm=limit))
    rings=[]
    for u,p in manifest['pads'].items():
        if p['type']=='PT_PTH':rings.append(dict(**label(u),ring_mm=ring(p)))
    # Distinct-net SMD spacing; outside native polygons have <=100nm error.
    smd=[c for c in copper if c['kind']=='pad' and c['layer']=='F.Cu' and types.get(c['id'])=='PT_SMD']
    smd_gaps=[]
    for a,b in combinations(smd,2):
        if a['net']==b['net'] or a['id']==b['id'] or not nearby(a,b,.15):continue
        d=separation(a,b)
        if d<.15-1e-5:smd_gaps.append(dict(a=label(a['id']),b=label(b['id']),gap_mm=d))
    courtyard=[]
    courtyards=layout['courtyards']
    for (ra,pa),(rb,pb) in combinations(courtyards.items(),2):
        for x in pa:
            for y in pb:
                a=shape(ra,'','',x['outline'],polygon=True); b=shape(rb,'','',y['outline'],polygon=True)
                if nearby(a,b,0) and separation(a,b)<=0: courtyard.append([ra,rb])
    # Plane antipads matter independently of trace clearances. Test physical
    # hole capsules against all actual fill boundary segments, including holes.
    fill_gaps=[]
    for zid,z in layout['fills'].items():
        for layer,polys in z['layers'].items():
            edges=[]
            for poly in polys:
                for loop in [poly['outline'],*poly.get('holes',[])]:
                    edges.extend(shape(zid,z['net'],layer,[a,b]) for a,b in zip(loop,loop[1:]+loop[:1]))
            for h in holes:
                if types.get(h['id'])!='PT_PTH' or h['net']==z['net']:continue
                gaps=[separation(h,e) for e in edges if nearby(h,e,.3)]
                if gaps and min(gaps)<.3-1e-6:fill_gaps.append(dict(hole=label(h['id']),zone=zid,layer=layer,net=z['net'],gap_mm=min(gaps),screen_mm=.3))
    texts=[]
    def text(obj,owner):
        if obj.get('layer') not in {'BL_F_SilkS','BL_B_SilkS'}:return
        t=obj['text']; attrs=t['attributes']
        if not attrs.get('visible',False):return
        size=nm(attrs.get('size',{})); width=int(attrs.get('strokeWidth',{}).get('valueNm',0))/1e6
        texts.append(dict(owner=owner,text=t['text'],position=nm(t['position']),size_mm=size,stroke_mm=width,below_standard_legend=size[1]<1 or width<.15))
    for obj in manifest['texts'].values():text(obj,'board')
    for u,f in manifest['footprints'].items():
        ref=s['footprints'][u]['ref']
        for field in ['referenceField','valueField','datasheetField','descriptionField']:
            if f.get(field,{}).get('visible',False):text(f[field]['text'],ref)
        for obj in f['definition']['items']:
            if obj.get('@type','').endswith('BoardText'):text(obj,ref)
            elif obj.get('@type','').endswith('Field') and obj.get('visible',False):text(obj['text'],ref)
    # Edge screen for existing copper, including real arc polygons; fills separately.
    outline=context['board_outline'][0]['outline']; bounds=[min(p[i] for p in outline) for i in (0,1)]+[max(p[i] for p in outline) for i in (0,1)]
    edge=[]
    for c in copper:
        b=c['bounds']; d=min(b[0]-bounds[0],b[1]-bounds[1],bounds[2]-b[2],bounds[3]-b[3])
        edge.append((d,c['id'],c['kind'],c['layer']))
    via=Counter((v['drill'],min(v['copper_widths'].values())) for v in s['vias'].values())
    return dict(source_pcb_sha256=context['board_sha256'],counts={k:len(v) for k,v in s.items()},
        min_track_mm=min(t['width'] for t in s['tracks'].values()),track_widths=sorted(Counter(t['width'] for t in s['tracks'].values()).items()),
        via_sizes=[dict(drill_mm=k[0],diameter_mm=k[1],count=v,ring_mm=(k[1]-k[0])/2) for k,v in sorted(via.items())],
        hole_pair_below_published_screen=pairs,pth_track_below_published_screen=pth,pth_plane_below_published_screen=fill_gaps,pth_rings=rings,smd_pad_spacing_below_015=smd_gaps,
        outline_bounds_mm=bounds,minimum_existing_copper_to_rectangular_edge=sorted(edge)[:10],
        missing_courtyard=sorted(f['ref'] for f in s['footprints'].values() if not courtyards.get(f['ref'])),courtyard_intersections=courtyard,
        legend_text=texts,limits=['No generated manufacturing files or CAM preview.', 'No native CAD operation; accepted exported geometry reused.',
        'Courtyards are 2D; no mating/enclosure/height or tool access model.', 'Solder-mask/paste inheritance and text outlines need separate evidence.',
        'Published vendor screens do not establish vendor acceptance; same-net copper not treated as an unintended clearance fault.'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--context',required=True);p.add_argument('--manifest',required=True);p.add_argument('--layout',required=True);p.add_argument('--board',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();c=read_json(a.context);m=read_json(a.manifest)
    require(digest(a.board)==c['board_sha256'],'Accepted export/source hash mismatch')
    require(not Path(a.output).exists(),'Fresh output required')
    before=digest(a.board);result=audit(c,m,read_json(a.layout));require(digest(a.board)==before,'Source changed during analysis')
    write_json(a.output,result)
    print(json.dumps({k:len(result[k]) for k in ['hole_pair_below_published_screen','pth_track_below_published_screen','pth_plane_below_published_screen','smd_pad_spacing_below_015','courtyard_intersections','missing_courtyard']}))


if __name__=='__main__':main()
