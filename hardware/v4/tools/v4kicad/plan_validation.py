"""Order-independent, export-only copper/drill/region preflight. No native imports.

Capsules use analytic centreline distances; native pad/artwork polygons are
exported with ERROR_OUTSIDE (100 nm bound). Refillable zone contours are derived
geometry, not permanent obstacles; restrictions are hard obstacles. Native
refilled DRC and return/reference review remain mandatory.
"""
import argparse
import math
import re
from collections import Counter
from pathlib import Path
from .safety import require,read_json,write_json,digest

LAYERS=['F.Cu','In1.Cu','In2.Cu','B.Cu']


def route_key(row,kind):
    """Exact KiCad integer units, preserving net/layer identity; no tolerance."""
    split=2 if kind=='track' else 1
    return (*row[:split],*[round(v*1e6) for v in row[split:]])


def quantized_plan(plan):
    import copy
    result=copy.deepcopy(plan)
    for key,split in [('tracks',2),('vias',1)]:
        result[key]=[r[:split]+[round(v*1e6)/1e6 for v in r[split:]] for r in result[key]]
    return result


def profile(board):
    board=Path(board);pro=board.with_suffix('.kicad_pro');dru=board.with_suffix('.kicad_dru')
    q=read_json(pro);rules=q['board']['design_settings']['rules'];classes=q['net_settings']['classes']
    # This project's sole custom rule disallows other footprints in the RF area.
    # Unknown conditional copper rules cannot silently fall back to defaults.
    text=dru.read_text(encoding='utf-8').strip()
    expected="(version 1) (rule \"U1 antenna other components\" (condition \"A.Type == 'Footprint' && A.Reference != 'U1' && A.intersectsArea('U1_RF_ANTENNA')\") (constraint disallow footprint))"
    require(' '.join(text.split())==expected,'Unsupported custom rules; extend clearance export before routing')
    clearances={c['name']:c['clearance'] for c in classes}
    require(len(set(clearances.values()))==1,'Different class clearances require resolved per-net export')
    return dict(copper_clearance=max(rules['min_clearance'],*clearances.values()),
        hole_clearance=rules['min_hole_clearance'],hole_to_hole=rules['min_hole_to_hole'],
        edge_clearance=rules['min_copper_edge_clearance'],min_via_diameter=rules['min_via_diameter'],
        min_drill=rules['min_through_hole_diameter'],min_annular=rules['min_via_annular_width'],
        min_track_width=rules['min_track_width'],project_sha256=digest(pro),rules_sha256=digest(dru),
        class_clearances=clearances,custom_rules_supported=True)


def reserved_regions():
    # Planning reservations; never instantiated as CAD or design rules.
    return [dict(name='F5 future access',layers=LAYERS,polygon=
        [[91,49],[119,49],[119,66.5],[100,66.5],[100,68],[91,68]]),
        dict(name='USB under-module B corridor',layers=['B.Cu'],polygon=
        [[74.5,89.9],[96.4,89.9],[96.4,91.8],[74.5,91.8]]),
        dict(name='USB external B corridor',layers=['B.Cu'],polygon=
        [[96.4,77],[121,77],[121,91.8],[96.4,91.8]]),
        dict(name='USB connector F access',layers=['F.Cu'],polygon=
        [[112.5,77],[120.5,77],[120.5,83],[112.5,83]]),
        dict(name='USB resistor F access',layers=['F.Cu'],polygon=
        [[94,87],[99,87],[99,92],[94,92]])]


def segment_distance(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
    u=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
    return math.hypot(p[0]-a[0]-u*dx,p[1]-a[1]-u*dy)


def review_regions(plan):
    points=[p for _,_,_,x,y,xx,yy in plan['tracks'] for p in [[x,y],[xx,yy]]]+[v[1:3] for v in plan['vias']]
    require(points,'No review geometry')
    x0,y0=[min(p[i] for p in points)-1 for i in [0,1]]
    x1,y1=[max(p[i] for p in points)+1 for i in [0,1]]
    nx,ny=math.ceil((x1-x0)/29),math.ceil((y1-y0)/29)
    return [[x0+(x1-x0)*i/nx,y0+(y1-y0)*j/ny,x0+(x1-x0)*(i+1)/nx,y0+(y1-y0)*(j+1)/ny]
        for j in range(ny) for i in range(nx)]


def orientation(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def intersects(a,b,c,d):
    o=[orientation(a,b,c),orientation(a,b,d),orientation(c,d,a),orientation(c,d,b)]
    if o[0]*o[1]<0 and o[2]*o[3]<0:return True
    return any(v==0 and min(x[0],y[0])<=p[0]<=max(x[0],y[0]) and min(x[1],y[1])<=p[1]<=max(x[1],y[1])
               for v,x,y,p in [(o[0],a,b,c),(o[1],a,b,d),(o[2],c,d,a),(o[3],c,d,b)])


def inside(p,poly):
    result=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if segment_distance(p,a,b)==0:return True
        if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:result=not result
    return result


def shape(uid,net,layer,points,radius=0,polygon=False,**meta):
    require(len(points)>=2 and all(math.isfinite(v) for p in points for v in p),'Invalid geometry')
    bounds=[min(p[i] for p in points)-radius for i in [0,1]]+[max(p[i] for p in points)+radius for i in [0,1]]
    return dict(id=uid,net=net,layer=layer,points=points,radius=radius,polygon=polygon,bounds=bounds,**meta)


def separation(a,b):
    if a['polygon'] and any(inside(p,a['points']) for p in b['points']):return -a['radius']-b['radius']
    if b['polygon'] and any(inside(p,b['points']) for p in a['points']):return -a['radius']-b['radius']
    edges=lambda s:list(zip(s['points'],s['points'][1:]+(s['points'][:1] if s['polygon'] else [])))
    best=float('inf')
    for p,q in edges(a):
        for u,v in edges(b):
            if intersects(p,q,u,v):return -a['radius']-b['radius']
            best=min(best,segment_distance(p,u,v),segment_distance(q,u,v),segment_distance(u,p,q),segment_distance(v,p,q))
    return best-a['radius']-b['radius']


def nearby(a,b,gap):
    x,y=a['bounds'],b['bounds']
    return x[0]<=y[2]+gap and y[0]<=x[2]+gap and x[1]<=y[3]+gap and y[1]<=x[3]+gap


def drill(uid,net,pos,size,angle=0):
    w,h=size;require(w>0 and h>0,'Invalid drill dimensions')
    major=max(w,h);minor=min(w,h);r=math.radians(angle+(90 if h>w else 0));d=(major-minor)/2
    offset=[d*math.cos(r),d*math.sin(r)]
    return shape(uid,net,'*',[[pos[i]-offset[i] for i in [0,1]],[pos[i]+offset[i] for i in [0,1]]],minor/2,kind='hole')


def inventory(g,context):
    copper=[];holes=[]
    for u,t in g['tracks'].items():copper.append(shape(u,t['net'],t['layer'],[t['start'],t['end']],t['width']/2,kind='track'))
    for u,v in g['vias'].items():
        for l,w in v['copper_widths'].items():copper.append(shape(u,v['net'],l,[v['position']]*2,w/2,kind='via'))
        holes.append(drill(u,v['net'],v['position'],[v['drill']]*2))
    for u,p in g['pads'].items():
        own=context.get('pads',{}).get(u,{})
        for l,polys in p['polygons'].items():
            for poly in polys:copper.append(shape(u,p['net'],l,poly,polygon=True,kind='pad',
                clearance=own.get('clearances',{}).get(l,0)))
        if max(p['drill_size'])>0:
            require(u in context.get('pads',{}) or p['drill_size'][0]==p['drill_size'][1],
                'Oval hole orientation missing from native routing context')
            holes.append(drill(u,p['net'],p['position'],p['drill_size'],own.get('orientation',0)))
    for graphic in context.get('copper_graphics',[]):
        for poly in graphic['polygons']:copper.append(shape(graphic['uuid'],'@fixed-artwork',graphic['layer'],poly,polygon=True,kind='artwork'))
    return copper,holes


def check_plan(g,plan,context):
    require(plan.get('failure','missing') is None,'Failed/malformed plan')
    plan=quantized_plan(plan)
    require(not (plan.get('review_bounds') and plan.get('review_regions')),'Use local review bounds or explicit review tiles')
    for bounds in ([plan['review_bounds']] if plan.get('review_bounds') else plan.get('review_regions',[])):
        require(len(bounds)==4 and all(math.isfinite(v) for v in bounds) and
            0<bounds[2]-bounds[0]<=30 and 0<bounds[3]-bounds[1]<=30,
            'Plane review window must be positive and at most30mm per axis; tile larger domains before mutation')
    rules=context['profile'];existing,old_holes=inventory(g,context);added=[];holes=[];warnings=[];errors=[]
    for i,row in enumerate(plan['tracks']):
        n,l,w,x,y,xx,yy=row;require(l in LAYERS and w>0 and [x,y]!=[xx,yy],'Invalid track')
        require(w>=rules['min_track_width'],'Track below minimum width')
        added.append(shape('track:'+str(i),n,l,[[x,y],[xx,yy]],w/2,kind='track'))
        if math.dist([x,y],[xx,yy])<.2:warnings.append(dict(type='microleg',object='track:'+str(i),length_mm=math.dist([x,y],[xx,yy])))
    for i,row in enumerate(plan['vias']):
        n,x,y,d,h=row;u='via:'+str(i)
        require(d>=rules['min_via_diameter'] and h>=rules['min_drill'] and
            round(d*1e6)-round(h*1e6)>=2*round(rules['min_annular']*1e6),
            'Via below configured diameter/drill/annular minimum')
        for l in LAYERS:added.append(shape(u,n,l,[[x,y]]*2,d/2,kind='via'))
        holes.append(drill(u,n,[x,y],[h,h]))
    def finding(kind,a,b,gap,limit):
        errors.append(dict(type=kind,object=a['id'],against=b['id'],layer=a['layer'],
            net=a['net'],other_net=b['net'],actual_mm=gap,required_mm=limit))
    for i,a in enumerate(added):
        for b in [*existing,*added[:i]]:
            if a['layer']!=b['layer'] or (a['net'] and a['net']==b['net']):continue
            limit=max(rules['copper_clearance'],a.get('clearance',0),b.get('clearance',0))
            if nearby(a,b,limit):
                gap=separation(a,b)
                if gap<limit:finding('copper_clearance',a,b,gap,limit)
        for b in [*old_holes,*holes]:
            if a['id']==b['id'] or (a['net'] and a['net']==b['net']):continue
            if nearby(a,b,rules['hole_clearance']):
                gap=separation(a,b)
                if gap<rules['hole_clearance']:finding('copper_to_hole',a,b,gap,rules['hole_clearance'])
    # New holes against existing copper, as well as new copper against old holes.
    for i,a in enumerate(holes):
        for b in existing:
            if a['net'] and a['net']==b['net']:continue
            if nearby(a,b,rules['hole_clearance']):
                gap=separation(a,b)
                if gap<rules['hole_clearance']:finding('hole_to_existing_copper',a,b,gap,rules['hole_clearance'])
        for b in [*old_holes,*holes[:i]]:
            if nearby(a,b,rules['hole_to_hole']):
                gap=separation(a,b)
                if gap<rules['hole_to_hole']:finding('hole_to_hole',a,b,gap,rules['hole_to_hole'])
    regions=list(context.get('reservations',[]))
    for z in context.get('zones',{}).values():
        if not z['rule_area']:continue
        for poly in z['outline']:
            require(not poly['holes'],'Unsupported rule-area holes')
            regions.append(dict(name='zone:'+z['uuid'],layers=z['layers'],polygon=poly['outline'],
                tracks=z['GetDoNotAllowTracks'],vias=z['GetDoNotAllowVias']))
    for a in added:
        for r in regions:
            if a['layer'] not in r['layers'] or not r.get('tracks' if a['kind']=='track' else 'vias',True):continue
            b=shape(r['name'],'@reservation',a['layer'],r['polygon'],polygon=True)
            if nearby(a,b,0) and separation(a,b)<=0:finding('reserved_region',a,b,separation(a,b),0)
        for poly in context.get('board_outline',[]):
            require(not poly['holes'],'Unsupported board outline holes')
            require(len(context['board_outline'])==1,'Unsupported multi-outline board')
            points=poly['outline'];boundary=[shape('board-edge','',a['layer'],[p,q]) for p,q in zip(points,points[1:]+points[:1])]
            if not all(inside(p,points) for p in a['points']):finding('outside_board',a,boundary[0],-1,rules['edge_clearance'])
            for b in boundary:
                if nearby(a,b,rules['edge_clearance']):
                    gap=separation(a,b)
                    if gap<rules['edge_clearance']:finding('copper_to_edge',a,b,gap,rules['edge_clearance'])
    # Re-emitting a path at another width is still redundant copper, not a junction.
    duplicates=Counter((n,l,*sorted([(x,y),(xx,yy)])) for n,l,w,x,y,xx,yy in plan['tracks'])
    old_paths=Counter((t['net'],t['layer'],*sorted([tuple(t['start']),tuple(t['end'])]))
                      for t in g['tracks'].values())
    warnings.extend(dict(type='duplicate_track',geometry=list(k),count=v+old_paths[k],
                         proposed_count=v,existing_count=old_paths[k])
                    for k,v in duplicates.items() if v+old_paths[k]>1)
    return dict(valid=not errors,errors=errors,warnings=warnings,
        checked=dict(tracks=len(plan['tracks']),vias=len(plan['vias']),existing_copper_shapes=len(existing),existing_holes=len(old_holes)),
        zone_policy='Refillable copper is recomputed by native DRC; all rule-area restrictions are hard obstacles')


def validate_bound(plan_path,context_path,source,output=None):
    context=read_json(context_path);source=Path(source)
    require(context['board_sha256']==digest(source),'Routing context does not match saved board')
    require(context['profile']['project_sha256']==digest(source.with_suffix('.kicad_pro')) and
        context['profile']['rules_sha256']==digest(source.with_suffix('.kicad_dru')),'Routing rules/context drift')
    result=check_plan(context['snapshot'],read_json(plan_path),context)
    result.update(plan_sha256=digest(plan_path),context_sha256=digest(context_path),board_sha256=digest(source))
    if output:write_json(output,result)
    require(result['valid'],f"Offline copper preflight rejected {len(result['errors'])} violations; no native mutation")
    require(not any(w['type']=='duplicate_track' for w in result['warnings']),'Duplicate proposed tracks must be removed before application')
    return result


def clean_microlegs(plan,context):
    """Simplify an uninstalled plan only, with full joint revalidation each time."""
    import copy
    p=copy.deepcopy(plan);actions=[];g=context['snapshot']
    pads=[v for v in g['pads'].values()]
    # A tiny leg fully within one existing copper pad adds no connectivity.
    retained=[]
    for t in p['tracks']:
        n,l,w,x,y,xx,yy=t
        covered=math.dist([x,y],[xx,yy])<.2 and next((pad for pad in pads if pad['net']==n
            and any(all(inside(q,poly) for q in [[x,y],[xx,yy],[(x+xx)/2,(y+yy)/2]])
                for poly in pad['polygons'].get(l,[]))),None)
        if covered:actions.append(dict(action='remove_pad_internal_leg',track=t,pad=covered['uuid']))
        else:retained.append(t)
    p['tracks']=retained
    protected={(v[0],l,v[1],v[2]) for v in p['vias'] for l in LAYERS}
    protected.update((v['net'],l,*v['position']) for v in pads for l in v['polygons'])
    changed=True
    while changed:
        changed=False;nodes={}
        for i,(n,l,w,x,y,xx,yy) in enumerate(p['tracks']):
            for a,b in [((x,y),(xx,yy)),((xx,yy),(x,y))]:nodes.setdefault((n,l,*a),[]).append((i,w,b))
        for node,legs in nodes.items():
            if len(legs)!=2 or node in protected:continue
            (i,w,a),(j,ww,b)=legs
            if w!=ww or a==b or min(math.dist(a,node[2:]),math.dist(b,node[2:]))>=.2:continue
            t=[node[0],node[1],w,*a,*b]
            candidate=dict(p,tracks=[r for k,r in enumerate(p['tracks']) if k not in [i,j]]+[t])
            result=check_plan(g,candidate,context)
            if not result['valid'] or any(v['type']=='duplicate_track' for v in result['warnings']):continue
            actions.append(dict(action='merge_micro_corner',old=[p['tracks'][i],p['tracks'][j]],new=t))
            p=candidate;changed=True;break
    require(check_plan(g,p,context)['valid'],'Simplification introduced a copper conflict')
    return p,actions


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--context',required=True)
    p.add_argument('--board',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    r=validate_bound(a.plan,a.context,a.board,a.output)
    print(dict(valid=True,checked=r['checked'],warnings=len(r['warnings'])))
