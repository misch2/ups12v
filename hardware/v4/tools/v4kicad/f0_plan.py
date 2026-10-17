"""Phase4.9 export-only planning and review. Native access stays in guarded workers."""
import argparse
import copy
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from .safety import read_json, write_json, require, ToolError
from .route_plan import plan_routes

LAYERS = ['F.Cu','In1.Cu','In2.Cu','B.Cu']
CONTROL = ['I2C_SCL','I2C_SDA','~INT','/Q5_BASE_LIMITED','CHG_REQ','TCA_EN','NEN',
    '/CHG_GATE','MCU_CHG_BASE','CHG_AND','Net-(Q6-B)','/CHG_BASE','INT_BASE',
    'MCU_CHG_ARM','MCU_SDA','MCU_SCL','MCU_INT','MUX_ST']
LOCAL = ['MCU_EN','MCU_BOOT_STRAP2','MCU_BOOT_STRAP8','MCU_BOOT','UART_TX','UART_RX',
    'MCU_STATUS_LED','Net-(D2-A)','STAT']
POWER = ['MCU3V3','MAIN_3V3']
USB_P = 'Net-(U1-USB_D+_{slash}_GPIO19)'
USB_N = 'Net-(U1-USB_D-_{slash}_GPIO18)'
F5_REFS = {'U7','U8','Q10','L3','C60','C61','C62','C63','C64','C65','C66','C67',
    'C68','C69','R60','R61','R62','R63','R64','R65','R66','R67','R68','D6','NT2','TP17'}


def reservations(g,context=None):
    # RF exclusion copied from accepted native audit; F5 area is planning-only.
    g['routing_exclusions'] = [dict(layers=LAYERS, polygon=p) for p in [
        [[75.4,99.2],[88.6,99.2],[88.6,104.6],[75.4,104.6]],
        [[91,49],[119,49],[119,66.5],[100,66.5],[100,68],[91,68]]]]
    if context:g['routing_exclusions'].extend(context['reservations'])


def append(g, result, p):
    for n,l,w,x,y,xx,yy in p['tracks']:
        g['tracks']['planned-'+str(len(g['tracks']))] = dict(net=n,layer=l,width=w,start=[x,y],end=[xx,yy])
    for n,x,y,d,drill in p['vias']:
        g['vias']['planned-'+str(len(g['vias']))] = dict(net=n,position=[x,y],drill=drill,
            copper_widths={l:d for l in LAYERS})
    for k in ['tracks','vias','metrics']:
        result[k].extend(p.get(k,[]))


def poly(p, net, layer, width, points):
    p['tracks'].extend([[net,layer,*[round(v*1e6)/1e6 for v in [width,*a,*b]]]
        for a,b in zip(points,points[1:]) if a!=b])


def incremental_tracks(g,proposal):
    from .plan_validation import quantized_plan,route_key
    p=quantized_plan(proposal)
    seen={route_key([t['net'],t['layer'],t['width'],*a,*b],'track')
        for t in g['tracks'].values() for a,b in [(t['start'],t['end']),(t['end'],t['start'])]}
    retained=[]
    for t in p['tracks']:
        if route_key(t,'track') in seen:continue
        retained.append(t);seen.add(route_key(t,'track'))
        seen.add(route_key([*t[:3],*t[5:7],*t[3:5]],'track'))
    p['reused_track_objects']=len(p['tracks'])-len(retained);p['tracks']=retained
    return p


def mcu_local():
    p=dict(failure=None,tracks=[],vias=[],metrics=[],blocked=[])
    poly(p,'MCU3V3','F.Cu',.5,[[87.9,96],[89.52,96],[89.52,94.03],[90.05,93.5]])
    for a,b in [([90.48,96],[91.1,96]),([91.95,93.5],[92.6,93.5]),
        ([78.48,86],[78.48,86.5]),([76.05,88.65],[75.5,88.65]),
        ([87.95,88.65],[88.5,88.65]),([85.2,88.7],[85.2,89.1]),
        ([87.9,97.6],[88.5,97.6]),([32.5,87.08],[33.1,87.08])]:
        poly(p,'PGND','F.Cu',.3,[a,b]);p['vias'].append(['PGND',*b,.5,.3])
    poly(p,'PGND','F.Cu',.3,[[87.9,89.65],[88.5,89.65],[88.5,88.65]])
    poly(p,'PGND','F.Cu',.4,[[87.9,96.8],[87.9,98.5]])
    poly(p,'PGND','F.Cu',.4,[[76.05,98.5],[87.9,98.5]])
    p['vias'].extend([['PGND',x,98.5,.5,.3] for x in [77.2,82,86.8]])
    for y in [91.625,93.6,95.575]:poly(p,'PGND','F.Cu',.5,[[80.025,y],[83.975,y]])
    for x in [80.025,82,83.975]:
        poly(p,'PGND','F.Cu',.5,[[x,91.625],[x,96.4]])
        p['vias'].extend([['PGND',x,y,.5,.3] for y in [92.6,94.6,96.4]])
    for x in [42.12,52.12]:
        poly(p,'PGND','F.Cu',.4,[[x,96],[x+5.76,96]])
        p['vias'].extend([['PGND',x+.88,96,.5,.3],['PGND',x+4.88,96,.5,.3]])
    return p


def local_returns(plan,context,drc,refs):
    from .plan_validation import check_plan
    p=copy.deepcopy(plan)
    missing={i['uuid'] for v in drc['unconnected_items'] for i in v['items'] if '[PGND]' in i['description']}
    offsets=[(.65,0),(-.65,0),(0,.65),(0,-.65),(.6,.6),(-.6,.6),(.6,-.6),(-.6,-.6),(1,0),(-1,0),(0,1),(0,-1)]
    for pad in context['snapshot']['pads'].values():
        if pad['ref'] not in refs or pad['net']!='PGND' or pad['uuid'] not in missing:continue
        x,y=pad['position'];found=False
        for dx,dy in offsets:
            b=[round(x+dx,6),round(y+dy,6)]
            candidate=copy.deepcopy(p);poly(candidate,'PGND','F.Cu',.3,[[x,y],b])
            candidate['vias'].append(['PGND',*b,.5,.3])
            if check_plan(context['snapshot'],candidate,context)['valid']:
                p=candidate;found=True;break
        if not found:p['blocked'].append(dict(net='PGND',ref=pad['ref'],reason='No short local return passed joint all-layer copper/drill checks'))
    return p


def power_feeds(plan,context):
    from .plan_validation import check_plan
    p=copy.deepcopy(plan);g=copy.deepcopy(context['snapshot']);reservations(g,context)
    sink=dict(tracks=[],vias=[],metrics=[]);append(g,sink,p)
    groups=[(.5,[62,79,72,88],['MCU3V3','C36','1','R25','1']),
        (.6,[65,79,94,98],['MCU3V3','C36','1','C31','1']),
        (.5,[60,71,73,87],['MAIN_3V3','C70','1','R28','1']),
        (.5,[73,57,90,75],['MAIN_3V3','D4','2','Q5','2'])]
    for width,bounds,connection in groups:
        print('Planning power feed '+str(connection),flush=True)
        try:
            q=incremental_tracks(g,plan_routes(g,[connection],bounds,width))
            candidate=dict(failure=None,tracks=p['tracks']+q['tracks'],vias=p['vias']+q['vias'])
            require(check_plan(context['snapshot'],candidate,context)['valid'],'Joint copper check rejects feed')
            append(g,p,q)
        except ToolError as e:p['blocked'].append(dict(connection=connection,reason=str(e)))
    return p


def pairs(drc, nets):
    for v in drc['unconnected_items']:
        items=v['items']
        names=set(n for i in items for n in re.findall(r'\[([^\]]+)\]',i['description']))
        if len(names)!=1 or not (names & set(nets)): continue
        net=names.pop()
        if any(re.search(r' of ('+'|'.join(sorted(F5_REFS))+r') on ',i['description']) for i in items):continue
        yield net,items


def auto_pair(g,result,net,items,width=.18,context=None):
    connection=[net]
    layers=[]
    coords=[]
    for i,item in enumerate(items):
        ref='@'+item['uuid']
        pos=[item['pos']['x'],item['pos']['y']]
        g['pads'][ref]=dict(ref=ref,pin='1',net=net,position=pos,polygons={},drill_size=[0,0])
        connection.extend([ref,'1']);coords.append(pos)
        layers.append('B.Cu' if ' on B.Cu' in item['description'] else 'F.Cu')
    lo=[max(31,min(p[k] for p in coords)-4) for k in [0,1]]
    hi=[min([125,98.8][k],max(p[k] for p in coords)+4) for k in [0,1]]
    bounds=[*lo,*hi]
    p=incremental_tracks(g,plan_routes(g,[connection],bounds,width,step=.1 if math.dist(*coords)>25 else .05,
        source_layer=layers[0],target_layer=layers[1]))
    # A proposed geometry is not a successful route until the joint checker passes.
    if context:
        from .plan_validation import check_plan
        candidate=dict(failure=None,tracks=result['tracks']+p['tracks'],vias=result['vias']+p['vias'])
        review=check_plan(context['snapshot'],candidate,context)
        require(review['valid'],'Joint copper validator rejects proposed connection')
        require(not any(w['type']=='duplicate_track' for w in review['warnings']),'Duplicate track proposed')
    require(len(p['vias'])<=2,'Routing-quality screen: more than two transitions on one connection')
    for m in p['metrics']:
        m['endpoints']=[i['description'] for i in items]
        m['direct_mm']=math.dist(*coords)
        require(m['length_mm']<=max(1.6*m['direct_mm'],m['direct_mm']+4),
            'Routing-quality screen: severe unexplained detour')
    append(g,result,p)


def build(snapshot,drc,batch,context=None):
    require(batch!='usb','USB data routing deferred to owner-assisted KiCad; no new custom USB candidate')
    require(context is not None,'Bound native routing context required')
    g=copy.deepcopy(snapshot);reservations(g,context)
    p=dict(failure=None,tracks=[],vias=[],metrics=[],blocked=[],
        review_bounds=[96,73,123,98] if batch=='usb' else [70,70,99,99])
    if batch=='usb':
        # Paired back-layer trunks with short front-layer ordering fanouts.
        for net,points in [('USB_DP',[[114.225,78.85],[114.3,78.75]]),
                           ('USB_DN',[[114.225,78.15],[114.65,77.75],[115.3,77.75]])]:
            poly(p,net,'F.Cu',.18,points)
        poly(p,'USB_DP','B.Cu',.18,[[114.3,78.75],[111.8,81.25],[111.8,84.6],[107.7,88.7],[97.2,88.7]])
        poly(p,'USB_DN','B.Cu',.18,[[115.3,77.75],[115.3,78.65],[112.4,81.55],[112.4,85],[107.9,89.5],[98,89.5]])
        poly(p,'USB_DP','F.Cu',.18,[[97.2,88.7],[96.51,88]])
        poly(p,'USB_DN','F.Cu',.18,[[98,89.5],[97.49,90],[96.51,90]])
        for n,points in [(USB_P,[[95.49,88],[94.9,88.59],[94.9,91.2]]),
                         (USB_N,[[95.49,90],[95.6,90.6]])]:
            poly(p,n,'F.Cu',.18,points)
        for n,y,x in [(USB_P,91.2,94.9),(USB_N,90.4,95.6)]:
            poly(p,n,'B.Cu',.18,([[x,90.6],[95.4,y],[75.3,y]] if n==USB_N else [[x,y],[75.3,y]]))
            poly(p,n,'F.Cu',.18,[[75.3,y],[76.1,y]])
            p['vias'].extend([[n,x,90.6 if n==USB_N else y,.5,.3],[n,75.3,y,.5,.3]])
        p['vias'].extend([[n,x,y,.5,.3] for n,x,y in [
            ('USB_DP',114.3,78.75),('USB_DP',97.2,88.7),
            ('USB_DN',115.3,77.75),('USB_DN',98,89.5)]])
        for a,b in [([113.375,78.5],[112.7,78.5]),
                    ([114.51,75.5],[114.51,74.85]),([117.51,74],[118.15,74])]:
            poly(p,'PGND','F.Cu',.3,[a,b]);p['vias'].append(['PGND',*b,.5,.3])
        # Local return stitching at USB layer transitions, not airwire-count filler.
        p['vias'].extend([['PGND',x,y,.5,.3] for x,y in [
            (113.5,77.3),(115.8,77.15),(98.5,88.8),(97.1,90),
            (94.3,90.6),(95.7,91.5),(74.5,89.8),(74.5,91.8)]])
        initial=copy.deepcopy(p);p['tracks']=[];p['vias']=[];append(g,p,initial)
        # Connector duplicate contacts and ESD are deliberately short branches.
        padmap={(v['ref'],v['pin']):v for v in g['pads'].values()}
        routes=[['USB_DP','J7','A6','J7','B6'],['USB_DN','J7','A7','J7','B7'],
                ['USB_DP','J7','A6','U2','1'],['USB_DN','J7','A7','U2','2'],
                ['USB_CC1','J7','A5','R13','1'],['USB_CC2','J7','B5','R14','1']]
        for route in routes:
            try:
                q=plan_routes(g,[route],[111,72,122,84],.18,
                    source_layer='F.Cu' if route[0].startswith('USB_CC') else 'B.Cu',
                    target_layer='B.Cu' if route[3]=='J7' else 'F.Cu')
                append(g,p,q)
            except ToolError as e:p['blocked'].append(dict(connection=route,reason=str(e)))
    else:
        if batch=='mcu':append(g,p,mcu_local())
        nets={'local':LOCAL,'mcu':LOCAL,'control':CONTROL,'power':POWER}[batch]
        # Each pair is from fresh native DRC; do not replay obsolete airwires.
        for n,items in sorted(pairs(drc,nets),key=lambda pair:math.dist(
                [pair[1][0]['pos'][k] for k in ['x','y']],
                [pair[1][1]['pos'][k] for k in ['x','y']])):
            try:auto_pair(g,p,n,items,.5 if n in POWER else .18,context)
            except ToolError as e:p['blocked'].append(dict(net=n,endpoints=items,reason=str(e)))
    from .plan_validation import review_regions
    p.pop('review_bounds',None)
    if p['tracks'] or p['vias']:p['review_regions']=review_regions(p)
    return p


def whole_review(g,drc,output):
    grouped={}
    for label,nets in [('USB',['USB_DP','USB_DN',USB_P,USB_N,'USB_CC1','USB_CC2']),
                       ('MCU local',LOCAL),('Control',CONTROL),('Distribution',POWER)]:
        grouped[label]={n:dict(unconnected=sum(1 for _ in pairs(drc,[n])),
            pads=[{k:p[k] for k in ['ref','pin','position']} for p in g['pads'].values() if p['net']==n])
            for n in nets}
    result=dict(subsystems=grouped,remaining_other_nets=Counter(
        re.search(r'\[([^\]]+)\]',v['items'][0]['description']).group(1) for v in drc['unconnected_items']),
        sequence=['USB paired trunks/connector','Local MCU and reference ground','Control/isolation','Distribution and J4'],
        constraints=['Preserve all accepted copper/components/zone definitions',
            'Reserve F5 area (91..119,49..68); route J4 from outside it',
            'RF exclusion 75.4..88.6,99.2..104.6 all copper layers',
            'USB-C duplicated pin order and module/resistor opposite edges require layer fanouts',
            'No changes to power-domain net membership; no new domain crossings'],
        mechanisms=dict(planner='bounded raster A* and checked chord simplification; manual paired trunks',
            writer='canonical guarded kipy IPC Track/Via CreateItems; owning-editor refill/save',
            interactive_router_used=False,konnect_routing_tools_used=False,serialized_edits=False))
    write_json(output,result)
    return {k:sum(v['unconnected'] for v in rows.values()) for k,rows in grouped.items()}


def quality(before,after,output):
    tracks=[t for u,t in after['tracks'].items() if u not in before['tracks']]
    vias=[v for u,v in after['vias'].items() if u not in before['vias']]
    per=defaultdict(lambda:dict(segments=0,length_mm=0.,non_45_segments=0,short_segments=0,vias=0))
    vertices=defaultdict(list)
    for t in tracks:
        n=t['net'];r=per[n];r['segments']+=1;r['length_mm']+=math.dist(t['start'],t['end'])
        dx,dy=[abs(t['end'][i]-t['start'][i]) for i in [0,1]]
        r['non_45_segments']+=int(min(dx,dy)>1e-6 and abs(dx-dy)>1e-6)
        r['short_segments']+=int(math.hypot(dx,dy)<.2)
        for a,b in [(t['start'],t['end']),(t['end'],t['start'])]:
            vertices[(n,t['layer'],*a)].append([b[0]-a[0],b[1]-a[1]])
    acute=[]
    for key,vec in vertices.items():
        for i,a in enumerate(vec):
            for b in vec[i+1:]:
                angle=math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(a,b))/math.hypot(*a)/math.hypot(*b)))))
                if angle<89.9:acute.append(dict(net=key[0],layer=key[1],position=list(key[2:]),angle=angle))
    for v in vias:per[v['net']]['vias']+=1
    result=dict(standard_native_exported_tracks=len(tracks),standard_native_exported_vias=len(vias),
        per_net=dict(per),acute_centerline_junction_candidates=acute,
        caveats=['Angles at pad/via centers are candidates, not automatically copper defects',
            'Native DRC plus plane sampling and visual review are required',
            'Ratsnest/selection/highlight are not included in this native track inventory'])
    write_json(output,result)
    return dict(tracks=len(tracks),vias=len(vias),non_45=sum(v['non_45_segments'] for v in per.values()),acute_candidates=len(acute))


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['review','build','quality'])
    p.add_argument('--snapshot',required=True);p.add_argument('--drc');p.add_argument('--batch');p.add_argument('--before');p.add_argument('--context');p.add_argument('--output',required=True)
    a=p.parse_args();g=read_json(a.snapshot)
    if a.action=='review':print(whole_review(g,read_json(a.drc),a.output))
    elif a.action=='quality':print(quality(read_json(a.before),g,a.output))
    else:
        r=build(g,read_json(a.drc),a.batch,read_json(a.context));write_json(a.output,r)
        print(dict(tracks=len(r['tracks']),vias=len(r['vias']),blocked=len(r['blocked'])))


if __name__=='__main__':main()
