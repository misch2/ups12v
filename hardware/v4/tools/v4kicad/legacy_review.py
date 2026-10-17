"""Export-only legacy routing audit, bounded proposals and comparison evidence."""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import math

from .safety import read_json, write_json, require
from .plan_validation import inventory, separation, nearby, shape, check_plan, inside
from .replacement import remaining


def conventional(t):
    dx,dy = [abs(round((t['end'][i]-t['start'][i])*1e6)) for i in [0,1]]
    return dx == 0 or dy == 0 or dx == dy


def risk(net):
    if net in {'SYS','VIN1','VBUS','PMID','BATTERY','BATP','SW1','SW2','BTST1','BTST2',
               'ACDRV1','SDRV','PGND','GND','Net-(C26-Pad1)','/SW_NORMAL','/BST_NORMAL','/MAIN_FB'}:
        return 'C'
    if net in {'CHG_REQ','CHG_AND','MCU_CHG_BASE','MCU_CHG_ARM','UART_RX','UART_TX',
               'MUX_ST','Net-(D1-A)','Net-(D1-K)','Net-(D2-A)'}:
        return 'A'
    return 'B'


def metrics_tracks(tracks):
    lengths=[math.dist(t['start'],t['end']) for t in tracks]
    # Thin uniform conductor model; explicit thickness scenario, not a board rating.
    squares=sum(l/t['width'] for t,l in zip(tracks,lengths))
    return dict(segments=len(tracks),length_mm=sum(lengths),
                width_profile=[dict(uuid=t['uuid'],width_mm=t['width'],length_mm=l) for t,l in zip(tracks,lengths)],
                min_track_width_mm=min(t['width'] for t in tracks),
                non_04590=sum(not conventional(t) for t in tracks),microlegs=sum(l<.2 for l in lengths),
                length_times_width_mm2=sum(l*t['width'] for l,t in zip(lengths,tracks)),
                series_squares=squares,resistance_35um_20C_ohm=.0004925714285714286*squares,
                resistance_model='rho=1.724e-8 ohm*m, t=35um,20C; excludes spreading, parallel copper and pads')


def audit(context):
    g=context['snapshot'];by_net=defaultdict(list)
    for t in g['tracks'].values():by_net[t['net']].append(t)
    rows=[]
    for n,ts in by_net.items():
        m=metrics_tracks(ts)
        rows.append(dict(net=n,risk=risk(n),**m,
                         via_count=sum(v['net']==n for v in g['vias'].values())))
    duplicates=defaultdict(list)
    for u,t in g['tracks'].items():
        duplicates[t['net'],t['layer'],*sorted([tuple(t['start']),tuple(t['end'])])].append(u)
    return dict(baseline_sha256=context['board_sha256'],counts={k:len(v) for k,v in g.items()},
                nets=sorted(rows,key=lambda r:(r['risk'],-r['non_04590'])),
                duplicate_centerlines=[dict(net=k[0],layer=k[1],endpoints=k[2:],uuids=v)
                                       for k,v in duplicates.items() if len(v)>1],
                nonconventional_tracks=[t for t in g['tracks'].values() if not conventional(t)],
                microlegs=[t for t in g['tracks'].values() if math.dist(t['start'],t['end'])<.2],
                caution='Angle, microleg, width changes and via counts are review flags, not electrical defects.')


def plans(context):
    g=context['snapshot']
    r35={u:t for u,t in g['tracks'].items() if t['net']=='USB3V3' and t['width']==.3 and
         min(t['start'][0],t['end'][0])>=109.49}
    c26={u:t for u,t in g['tracks'].items() if t['net']=='Net-(C26-Pad1)' and t['start']==[42.4625,50.5]}
    sys={u:t for u,t in g['tracks'].items() if t['net']=='SYS' and t['width']==1.2 and
         t['start'][1]==60.95 and t['end'][1]==60.95}
    winding={u:g['tracks'][u] for u in ['3b8f4637-0f0e-4d99-8c0c-51ea287f1c7d','1abd7e07-09a2-4e2d-8257-275248cba12e']}
    require(len(r35)==7 and len(c26)==1 and len(sys)==3, 'Representative original inventory differs; STOP')
    def plan(name,removed,rows,bounds):
        return dict(name=name,mode='scratch-track-replacement',failure=None,baseline_sha256=context['board_sha256'],
                    remove_tracks=removed,tracks=rows,vias=[],review_bounds=bounds)
    candidates={}
    # Sample a small, deterministic set of bleeder escapes; native copper does not move.
    for y in [88.1,88.2,88.3,88.4,88.5,88.6]:
        x=109.52+(89.5-y)
        rows=[['USB3V3','F.Cu',.3,109.52,88.,109.52,y],
              ['USB3V3','F.Cu',.3,109.52,y,x,89.5],['USB3V3','F.Cu',.3,x,89.5,111.99,89.5]]
        p=plan('R35 bleeder',r35,rows,[103,80,116,93])
        check=check_plan(remaining(context,p),p,context)
        candidates[str(y)]=dict(valid=check['valid'],errors=check['errors'])
        if check['valid']:
            r35_plan=p
            break
    require(any(v['valid'] for v in candidates.values()), 'No legal R35 proposal found')
    return dict(r35=r35_plan,
        c26=plan('R12-C26 snubber clearance',c26,
                 [['Net-(C26-Pad1)','F.Cu',.8,42.4625,50.5,39.975,50.5],
                  ['Net-(C26-Pad1)','F.Cu',.8,39.975,50.5,37.475,53]], [32,46,46,58]),
        sys=plan('SYS exact collinear merge',sys,[['SYS','F.Cu',1.2,67.95,60.95,76.2,60.95]],[60,55,80,67]),
        sys_oblique=plan('SYS oblique 45-degree study',winding,
                        [['SYS','F.Cu',.8,77.2,76.2,76.25,77.15],['SYS','F.Cu',.8,76.25,77.15,67.1,77.15]],
                        [64,73,80,80])),candidates


def project(p,a,b):
    d=[b[i]-a[i] for i in [0,1]];den=sum(x*x for x in d)
    t=max(0,min(1,sum((p[i]-a[i])*d[i] for i in [0,1])/den)) if den else 0
    return [a[i]+t*d[i] for i in [0,1]]


def closest_points(a,b):
    edges=lambda q:list(zip(q['points'],q['points'][1:]+(q['points'][:1] if q['polygon'] else [])))
    best=(float('inf'),None,None)
    for u,v in edges(a):
        for x,y in edges(b):
            for p,q in [(u,project(u,x,y)),(v,project(v,x,y)),(project(x,u,v),x),(project(y,u,v),y)]:
                d=math.dist(p,q)
                if d<best[0]:best=(d,p,q)
    d,p,q=best
    if d:
        direction=[(q[i]-p[i])/d for i in [0,1]]
        p=[p[i]+a['radius']*direction[i] for i in [0,1]]
        q=[q[i]-b['radius']*direction[i] for i in [0,1]]
    return dict(on_candidate=p,on_neighbour=q)


def clearance(g,tracks,context,target_net=None):
    copper,_=inventory(g,context);best=None
    for t in tracks:
        a=shape(t['uuid'],t['net'],t['layer'],[t['start'],t['end']],t['width']/2)
        for b in copper:
            if b['net']==a['net'] or b['layer']!=a['layer']:continue
            if target_net and b['net'] not in ({target_net} if isinstance(target_net,str) else target_net):continue
            if best and not nearby(a,b,best['gap_mm']):continue
            gap=separation(a,b)
            if best is None or gap<best['gap_mm']:
                best=dict(gap_mm=gap,object_uuid=t['uuid'],neighbour_uuid=b['id'],neighbour_net=b['net'],
                          neighbour_kind=b['kind'],layer=t['layer'],location=closest_points(a,b))
                if b['id'] in g['pads']:
                    p=g['pads'][b['id']];best['neighbour_ref_pin']=p['ref']+'.'+p['pin']
    if best:
        best['pad_polygon_bound_mm']=.0001 if best['neighbour_kind']=='pad' else 0
        best['method']='Exact capsule distance; native pad polygons ERROR_OUTSIDE <=100nm. Physical geometry, not rule clearance.'
    return best


def compare(context,plan,after,root=None):
    before=context['snapshot'];original=list(plan['remove_tracks'].values())
    new=[t for u,t in after['tracks'].items() if u not in before['tracks']]
    bounds=plan['review_bounds'];net=original[0]['net'];layer=original[0]['layer']
    result=dict(name=plan['name'],original_objects=original,proposed_objects=new,
        before=metrics_tracks(original),after=metrics_tracks(new),
        original_clearance=clearance(before,original,context),proposed_clearance=clearance(after,new,context),
        vias_changed=[],all_original_vias_identical=before['vias']==after['vias'],
        nearby_vias=[v for v in before['vias'].values() if bounds[0]<=v['position'][0]<=bounds[2] and bounds[1]<=v['position'][1]<=bounds[3]])
    if net=='Net-(C26-Pad1)':
        result['original_PMID_clearance']=clearance(before,original,context,'PMID')
        result['proposed_PMID_clearance']=clearance(after,new,context,'PMID')
    if root:
        a,b=read_json(root/'layout-before.json'),read_json(root/'layout-final.json')
        result['native_fill_polygons_exact_equal']=a['fills']==b['fills']
        result['native_0p1mm_plane_grid_exact_equal']=a['plane_samples']==b['plane_samples']
        result['native_via_plane_samples_exact_equal']=a['via_plane_samples']==b['via_plane_samples']
        result['reference_sampling_before']=reference_samples(before,original,a,context)
        result['reference_sampling_after']=reference_samples(after,new,b,context)
    for label,g,tracks in [('before',before,original),('after',after,new)]:
        _,holes=inventory(g,context)
        gaps=[separation(shape(t['uuid'],net,layer,[t['start'],t['end']],t['width']/2),h)
              for t in tracks for h in holes]
        result[label]['minimum_track_edge_to_physical_hole_mm']=min(gaps)
        result[label]['drill_reduces_selected_conductor_width']=min(gaps)<0
        result[label]['conducting_width']=conducting_width(tracks,holes)
        result[label]['sensitive_node_proximity']=clearance(g,tracks,context,
            {'SW1','SW2','/SW_NORMAL','/MAIN_FB','TS','PROG','ILIM_HIZ','BTST1','BTST2'})
        result[label]['remaining_USB_proximity']=clearance(g,tracks,context,
            {'USB_DP','USB_DN','USB_CC1','USB_CC2','Net-(U1-USB_D+_{slash}_GPIO19)','Net-(U1-USB_D-_{slash}_GPIO18)'})
        result[label]['blocked_IC1_net_proximity']=clearance(g,tracks,context,{'I2C_SCL','~INT','STAT'})
        result[label]['F5_node_proximity']=clearance(g,tracks,context,
            {p['net'] for p in g['pads'].values() if p['net'].startswith('/F5_')})
    # Raster union resolves corner overlap/parallel pads; this is sampled exported copper,
    # not an ampacity or inductance measurement. Same fixed local box for both cases.
    result['local_copper_union']=dict(bounds=bounds,step_mm=.02,
        before_mm2=local_area(before,net,layer,bounds,context),after_mm2=local_area(after,net,layer,bounds,context))
    return result


def conducting_width(tracks,holes):
    """Residual metal across the selected track strip, subtracting circular drills.

    This excludes helpful pad/parallel-branch copper outside that strip. It is a
    conservative geometric width, not a current rating or solved current density.
    """
    best=None
    for t in tracks:
        a,b=t['start'],t['end'];length=math.dist(a,b)
        ux,uy=(b[0]-a[0])/length,(b[1]-a[1])/length;nx,ny=-uy,ux;w=t['width']
        relevant=[]
        for h in holes:
            if not nearby(shape(t['uuid'],t['net'],t['layer'],[a,b],w/2),h,0):continue
            if h['points'][0]!=h['points'][1]:
                return dict(minimum_mm=None,reason='Oval drill intersects selected region; cross-section method needs extension')
            x,y=h['points'][0];s=(x-a[0])*ux+(y-a[1])*uy;o=(x-a[0])*nx+(y-a[1])*ny
            relevant.append((h,s,o))
        stations={0,length,*[max(0,min(length,s)) for _,s,_ in relevant]}
        # A dense scan plus exact drill-center stations. Report the resolution;
        # symmetric overlapping holes in this candidate reach their minimum there.
        stations.update(length*k/max(1,math.ceil(length/.01)) for k in range(math.ceil(length/.01)+1))
        for s in stations:
            intervals=[];ids=[]
            for h,hs,offset in relevant:
                delta=abs(s-hs);r=h['radius']
                if delta>=r:continue
                half=math.sqrt(r*r-delta*delta);lo=max(-w/2,offset-half);hi=min(w/2,offset+half)
                if hi>lo:intervals.append((lo,hi));ids.append(h['id'])
            end=-w/2;removed=0
            for lo,hi in sorted(intervals):
                removed+=max(0,hi-max(lo,end));end=max(end,hi)
            width=w-removed
            if best is None or width<best['minimum_mm']:
                best=dict(minimum_mm=width,track_uuid=t['uuid'],location=[a[0]+s*ux,a[1]+s*uy],drill_uuids=ids,
                          method='Selected strip minus exact circular drill chords; <=0.01mm longitudinal scan plus exact drill-center stations',
                          excludes='Pads/parallel branch copper outside strip, plated barrel conduction, current crowding and thermal rating')
    return best


def reference_samples(g,tracks,layout,context):
    """Probe center and both edges over actual In1 polygons, subtracting drills."""
    fills=[p for z in layout['fills'].values() if z['net']=='PGND' for p in z['layers'].get('In1.Cu',[])]
    _,holes=inventory(g,context)
    covered,total,missing=0,0,[]
    visited=set()
    for t in tracks:
        a,b=t['start'],t['end'];length=math.dist(a,b);nx,ny=-(b[1]-a[1])/length,(b[0]-a[0])/length
        steps=math.ceil(round(length*1e6)/50000)
        for k in range(steps+1):
            for offset in [-t['width']/2,0,t['width']/2]:
                p=[a[0]+(b[0]-a[0])*k/steps+nx*offset,a[1]+(b[1]-a[1])*k/steps+ny*offset]
                key=tuple(round(x*1e6) for x in p)
                if key in visited:continue
                visited.add(key)
                p=[v/1e6 for v in key]
                point=shape('sample','', 'In1.Cu',[p,p])
                on=any(inside(p,poly['outline']) and not any(inside(p,h) for h in poly['holes']) for poly in fills)
                if on:
                    on=not any(nearby(point,h,0) and separation(point,h)<=0 for h in holes)
                total+=1;covered+=bool(on)
                if not on:missing.append(p)
    return dict(max_along_step_mm=.05,lateral_offsets='center and +/- half track width',samples=total,
                PGND_copper_samples=covered,missing_samples=missing,
                interpretation='Geometric samples only, not an inductance or impedance field solution')


def local_area(g,net,layer,bounds,context,step=.02):
    import numpy as np
    from .plan_validation import inventory as inv
    x0,y0,x1,y1=bounds
    X,Y=np.meshgrid(np.arange(x0+step/2,x1,step),np.arange(y0+step/2,y1,step))
    mask=np.zeros(X.shape,dtype=bool)
    # This area mask covers tracks/pads/vias and subtracts all physical holes.
    c,h=inv(g,context)
    for a in c:
        if a['net']!=net or a['layer']!=layer:continue
        if a['polygon']:
            hit=np.zeros(X.shape,dtype=bool)
            for p,q in zip(a['points'],a['points'][1:]+a['points'][:1]):
                if p[1]!=q[1]:hit^=((p[1]>Y)!=(q[1]>Y)) & (X<(q[0]-p[0])*(Y-p[1])/(q[1]-p[1])+p[0])
        else:
            p,q=a['points'];dx,dy=q[0]-p[0],q[1]-p[1];den=dx*dx+dy*dy
            u=np.clip(((X-p[0])*dx+(Y-p[1])*dy)/den,0,1) if den else 0
            hit=(X-p[0]-u*dx)**2+(Y-p[1]-u*dy)**2<=a['radius']**2
        mask|=hit
    for a in h:
        p,q=a['points'];dx,dy=q[0]-p[0],q[1]-p[1];den=dx*dx+dy*dy
        u=np.clip(((X-p[0])*dx+(Y-p[1])*dy)/den,0,1) if den else 0
        mask&=((X-p[0]-u*dx)**2+(Y-p[1]-u*dy)**2>a['radius']**2)
    return float(mask.sum()*step*step)


def illustration(before,after,plan,path):
    """Focused native-export geometry comparison; plane evidence is separate."""
    from PIL import Image, ImageDraw, ImageFont
    bounds=plan['review_bounds'];x0,y0,x1,y1=bounds;scale=42
    w,h=round((x1-x0)*scale),round((y1-y0)*scale)
    im=Image.new('RGB',(w*2,h+70),'white')
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
    net=next(iter(plan['remove_tracks'].values()))['net']
    for j,(label,g) in enumerate([('ORIGINAL',before),('SCRATCH',after)]):
        panel=Image.new('RGB',(w,h+45),'white');d=ImageDraw.Draw(panel)
        pt=lambda p:((p[0]-x0)*scale,(p[1]-y0)*scale+45)
        for t in g['tracks'].values():
            if t['layer']!='F.Cu':continue
            col='#cd3030' if t['net']==net else '#c1c1c1'
            if t['net']=='PMID' and net!='PMID':col='#be83bc'
            d.line([pt(t['start']),pt(t['end'])],fill=col,width=max(1,round(t['width']*scale)))
            for p in [t['start'],t['end']]:
                x,y=pt(p);r=t['width']*scale/2;d.ellipse((x-r,y-r,x+r,y+r),fill=col)
        for p in g['pads'].values():
            for poly in p['polygons'].get('F.Cu',[]):d.polygon([pt(v) for v in poly],fill='#e77272' if p['net']==net else '#ddd0bd')
            if x0<p['position'][0]<x1 and y0<p['position'][1]<y1:
                x,y=pt(p['position']);d.text((x+3,y+3),p['ref']+'.'+p['pin'],font=font,fill='black')
        for v in g['vias'].values():
            x,y=pt(v['position']);r=v['copper_widths']['F.Cu']*scale/2
            d.ellipse((x-r,y-r,x+r,y+r),fill='#8e8e8e');r=v['drill']*scale/2
            d.ellipse((x-r,y-r,x+r,y+r),fill='white')
        selected=set(plan['remove_tracks']) if j==0 else set(after['tracks'])-set(before['tracks'])
        for uid in selected:
            for p in [g['tracks'][uid]['start'],g['tracks'][uid]['end']]:
                x,y=pt(p);d.ellipse((x-2,y-2,x+2,y+2),fill='#402080')
        d.rectangle((0,0,w,43),fill='white');d.text((8,7),label+' | '+plan['name'],font=font,fill='black')
        im.paste(panel,(j*w,0))
    d=ImageDraw.Draw(im)
    d.text((8,h+50),'F.Cu exported copper, mm; red = selected net. Ground fill assessed separately.',font=font,fill='black')
    im.save(path)


def finalize(context_path,proposal_root,control,output):
    """Full joint candidate check and independent check-result comparison."""
    import copy
    from .safety import digest
    context=read_json(context_path);g=copy.deepcopy(context['snapshot'])
    names=['r35-v2','c26-v3','sys']
    joint=dict(failure=None,tracks=[],vias=[],review_regions=[])
    changes={}
    for name in names:
        plan=read_json(proposal_root/(name+'-plan.json'))
        remaining(context,plan)  # independent exact original declaration guard
        for uid,row in plan['remove_tracks'].items():
            require(g['tracks'].pop(uid,None)==row,'Joint removal overlap/mismatch')
        joint['tracks'].extend(plan['tracks']);joint['review_regions'].append(plan['review_bounds'])
        changes[name]=dict(plan_sha256=digest(proposal_root/(name+'-plan.json')),
                           original_uuids=list(plan['remove_tracks']),added_tracks=plan['tracks'])
    check=check_plan(g,joint,context)
    require(check['valid'] and not any(w['type']=='duplicate_track' for w in check['warnings']),
            'Joint candidate preflight failed')
    write_json(proposal_root/'joint-preflight.json',check)
    old_d,old_e=read_json(control/'drc.json'),read_json(control/'erc.json')
    warnings=lambda q,kind:Counter((v['type'],v['description']) for v in
        (q['violations'] if kind=='drc' else [v for s in q['sheets'] for v in s['violations']]) if v['severity']=='warning')
    results={}
    for suffix in ['r35','c26','sys','r35-v2','c26-v3','sys-oblique']:
        root=proposal_root.parent/('legacy-geometry-'+suffix+'-scratch-2026-10-17')
        d,e=read_json(root/'drc.json'),read_json(root/'erc.json')
        require(warnings(d,'drc')==warnings(old_d,'drc') and warnings(e,'erc')==warnings(old_e,'erc'),
                'New DRC/ERC warning versus matching scratch control')
        require(d['ignored_checks']==old_d['ignored_checks'] and len(d['unconnected_items'])==len(old_d['unconnected_items']),
                'Ignored checks or unconnected count changed')
        results[suffix]=dict(warning_multisets_equal_control=True,ignored_checks_equal=True,
                            unconnected_equal=True,preservation=read_json(root/'replace-verify-preservation.json'))
    result=dict(baseline_sha256=context['board_sha256'],context_sha256=digest(context_path),
                joint_preflight=check,explicit_intended_changes=changes,
                independent_original_object_and_native_checks=results,
                hypothetical_joint_counts=dict(tracks=len(g['tracks'])+len(joint['tracks']),vias=len(g['vias'])),
                installation_authorized=False)
    write_json(output,result)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--context',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--compare-root',type=Path)
    a=p.parse_args();context=read_json(a.context)
    if a.compare_root:
        plan=read_json(a.compare_root/'plan.json');after=read_json(a.compare_root/'final-snapshot.json')
        result=compare(context,plan,after,a.compare_root)
        write_json(a.output,result)
        illustration(context['snapshot'],after,plan,a.output.with_suffix('.png'))
        print(dict(name=plan['name'],segments=[result[k]['segments'] for k in ['before','after']],
                   length_mm=[result[k]['length_mm'] for k in ['before','after']],
                   clearance_mm=[result[k]['gap_mm'] for k in ['original_clearance','proposed_clearance']],
                   plane_equal=result['native_fill_polygons_exact_equal']))
    else:
        require(not a.output.exists(),'Fresh proposal directory required')
        a.output.mkdir(parents=True)
        write_json(a.output/'audit.json',audit(context))
        proposals,search=plans(context)
        write_json(a.output/'r35-search.json',search)
        for name,plan in proposals.items():
            write_json(a.output/(name+'-plan.json'),plan)
            result=check_plan(remaining(context,plan),plan,context)
            write_json(a.output/(name+'-preflight.json'),result)
            print(dict(name=name,removed=len(plan['remove_tracks']),added=len(plan['tracks']),valid=result['valid'],violations=len(result['errors'])))


if __name__=='__main__':main()
