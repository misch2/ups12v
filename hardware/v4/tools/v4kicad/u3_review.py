"""Quantitative U3 review of exported geometry only; no native CAD access on import."""
import math
import heapq
from pathlib import Path
from .safety import read_json,write_json,require


def area(points):
    return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(points,points[1:]+points[:1])))/2


def route_path(plan,net,start,end):
    graph={}
    for n,layer,width,x,y,u,v in plan['tracks']:
        if n!=net:continue
        a,b=(x,y),(u,v);d=math.dist(a,b)
        graph.setdefault(a,[]).append((b,d));graph.setdefault(b,[]).append((a,d))
    start,end=tuple(start),tuple(end);heap=[(0,start)];dist={start:0};parent={}
    while heap:
        cost,node=heapq.heappop(heap)
        if cost!=dist[node]:continue
        if node==end:
            path=[node]
            while node!=start:node=parent[node];path.append(node)
            return dict(length_mm=cost,path=list(reversed(path)))
        for nxt,d in graph.get(node,[]):
            new=cost+d
            if new<dist.get(nxt,float('inf')):
                dist[nxt]=new;parent[nxt]=node;heapq.heappush(heap,(new,nxt))
    raise ValueError('Declared path not connected in route plan')


def plane_path(g,layout,start,end):
    """Find a sampled conductive path in actual native fill, subtracting real drills."""
    import numpy as np
    sample=layout['plane_samples'];x0,y0,x1,y1=sample['bounds'];s=sample['step']
    mask=np.array([[c=='1' for c in row] for row in sample['rows']],dtype=bool)
    yy,xx=np.indices(mask.shape);X=x0+xx*s;Y=y0+yy*s
    for via in g['vias'].values():
        x,y=via['position'];mask[(X-x)**2+(Y-y)**2<=(via['drill']/2+.015)**2]=False
    for pad in g['pads'].values():
        if max(pad['drill_size'])>0:
            x,y=pad['position'];mask[(X-x)**2+(Y-y)**2<=(max(pad['drill_size'])/2+.015)**2]=False
    def cell(p):return (round((p[1]-y0)/s),round((p[0]-x0)/s))
    a,b=cell(start),cell(end);require(mask[a] and mask[b],'Plane path endpoint outside copper')
    heap=[(0.,a)];dist={a:0.};parent={}
    while heap:
        cost,(y,x)=heapq.heappop(heap)
        if cost!=dist[y,x]:continue
        if (y,x)==b:
            path=[b];q=b
            while q!=a:q=parent[q];path.append(q)
            return dict(length_mm=cost,step_mm=s,path=[[round(x0+x*s,4),round(y0+y*s,4)] for y,x in reversed(path)],
                        native_fill_and_drills_checked=True)
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if not dx and not dy:continue
                u,v=y+dy,x+dx
                if not (0<=u<mask.shape[0] and 0<=v<mask.shape[1]) or not mask[u,v]:continue
                if dx and dy and (not mask[y,v] or not mask[u,x]):continue
                new=cost+math.hypot(dx,dy)*s
                if new<dist.get((u,v),float('inf')):
                    dist[u,v]=new;parent[u,v]=(y,x);heapq.heappush(heap,(new,(u,v)))
    raise ValueError('No connected plane return path')


def copper_area(g,net,layer,step=.01):
    import numpy as np
    pads=[p for p in g['pads'].values() if p['net']==net]
    tracks=[t for t in g['tracks'].values() if t['net']==net and t['layer']==layer]
    vias=[v for v in g['vias'].values() if v['net']==net]
    points=[v for p in pads for poly in p['polygons'].get(layer,[]) for v in poly]
    points += [v for t in tracks for v in [t['start'],t['end']]]+[v['position'] for v in vias]
    if not points:return 0.
    lo=[min(p[k] for p in points)-1 for k in [0,1]];hi=[max(p[k] for p in points)+1 for k in [0,1]]
    X,Y=np.meshgrid(np.arange(lo[0],hi[0],step),np.arange(lo[1],hi[1],step));mask=np.zeros(X.shape,dtype=bool)
    for p in pads:
        for poly in p['polygons'].get(layer,[]):
            inside=np.zeros(X.shape,dtype=bool)
            for a,b in zip(poly,poly[1:]+poly[:1]):
                if a[1]!=b[1]:inside ^= ((a[1]>Y)!=(b[1]>Y)) & (X<(b[0]-a[0])*(Y-a[1])/(b[1]-a[1])+a[0])
            mask|=inside
    for t in tracks:
        a,b=t['start'],t['end'];dx,dy=b[0]-a[0],b[1]-a[1]
        u=np.clip(((X-a[0])*dx+(Y-a[1])*dy)/(dx*dx+dy*dy),0,1)
        mask|=(X-a[0]-u*dx)**2+(Y-a[1]-u*dy)**2<=(t['width']/2)**2
    for v in vias:mask|=(X-v['position'][0])**2+(Y-v['position'][1])**2<=(v['copper_widths'][layer]/2)**2
    return float(mask.sum()*step*step)


def review(root,rejected,output):
    root=Path(root)
    g=read_json(root/('final-snapshot.json' if (root/'final-snapshot.json').exists() else 'snapshot.json'))
    layout=read_json(root/('layout-final.json' if (root/'layout-final.json').exists() else 'layout.json'))
    p=read_json(root/'plan.json')
    sw=route_path(p,'/SW_NORMAL',[49.74,79.75],[50,83.345])
    bst=route_path(p,'/BST_NORMAL',[49.74,79.25],[50.9,79.02])
    bsw=route_path(p,'/SW_NORMAL',[49.74,79.75],[50.9,79.98])
    vin=route_path(p,'SYS',[48.26,79.25],[47,81.48]);gnd=route_path(p,'PGND',[47,80.52],[48.26,79.75])
    input_loop=vin['path']+gnd['path']
    bootstrap_loop=bst['path']+list(reversed(bsw['path']))
    returns={}
    for name,a,b in [('C33',[53.3,82.4],[47.8,79.9]),('C45',[55.7,82.4],[47.8,79.9]),
                     ('FB_reference',[52.4,78.8],[47.8,79.9])]:returns[name]=plane_path(g,layout,a,b)
    output_loop=[[48.26,79.75],[49.74,79.75],*sw['path'][1:], [49.65,83.345],[49.65,86.655],[54,86.475],
                 [54,83.525],[53.5,83.025],[53.5,82.5],*returns['C33']['path'],[47.55,79.85],[47.85,79.75]]
    output_loop2=[[48.26,79.75],[49.74,79.75],*sw['path'][1:],[49.65,83.345],[49.65,86.655],
                  [54,86.475],[56.4,86.475],[56.4,83.525],[55.9,83.025],[55.9,82.5],
                  *returns['C45']['path'],[47.55,79.85],[47.85,79.75]]
    old=read_json(Path(rejected)/'final-snapshot.json')
    areas={layer:dict(candidate_mm2=copper_area(g,'/SW_NORMAL',layer),rejected_mm2=copper_area(old,'/SW_NORMAL',layer))
           for layer in ['F.Cu','B.Cu']}
    oldp=read_json(Path(rejected)/'plan.json')
    oldbst=route_path(oldp,'/BST_NORMAL',[49.74,79.25],[48.52,76])
    oldbsw=route_path(oldp,'/SW_NORMAL',[49.74,79.75],[49.48,76])
    oldloop=oldbst['path']+list(reversed(oldbsw['path']))
    sample=layout['plane_samples'];x0,y0,_,_=sample['bounds'];step=sample['step'];fb_samples=[]
    for net,layer,width,x,y,u,v in p['tracks']:
        if net!='/MAIN_FB':continue
        length=math.dist([x,y],[u,v]);dx,dy=(u-x)/length,(v-y)/length
        for i in range(math.ceil(length/.05)+1):
            f=min(1,i*.05/length)
            for offset in [-.15,0,.15]:
                q=[x+f*(u-x)-dy*offset,y+f*(v-y)+dx*offset]
                fb_samples.append(sample['rows'][round((q[1]-y0)/step)][round((q[0]-x0)/step)]=='1')
    rho=1.724e-8;t=.000035
    def resistance(net,points):
        return sum(rho*math.dist(a,b)*.001/(w*.001*t) for n,l,w,x,y,u,v in p['tracks'] if n==net
                   for a,b in [([x,y],[u,v])] if (tuple(a),tuple(b)) in set(zip(map(tuple,points),map(tuple,points[1:]))))
    thermal=[]
    for w in [.28,.5,.6,.8,1.2]:
        amil=(w/.0254)*(.035/.0254);dt=(1/(.048*amil**.725))**(1/.44)
        thermal.append(dict(width_mm=w,legacy_IPC2221_external_estimate_deltaC_at1A=dt))
    result=dict(placements=p['placements'],added_tracks=len(p['tracks']),added_vias=len(p['vias']),
        sw=sw,bst=bst,bootstrap_sw_return=bsw,input_vin=vin,input_pgnd=gnd,
        rejected_bootstrap_loop_projected_area_mm2=area(oldloop),
        feedback_native_plane_samples=dict(count=len(fb_samples),covered=sum(fb_samples),offset_mm=.15,step_mm=.05),
        input_loop_projected_area_mm2=area(input_loop),bootstrap_loop_projected_area_mm2=area(bootstrap_loop),
        output_C33_loop_projected_area_mm2=area(output_loop),output_C45_loop_projected_area_mm2=area(output_loop2),
        loops={'input':input_loop,'bootstrap':bootstrap_loop,'output_C33':output_loop,'output_C45':output_loop2},
        plane_return_paths=returns,sw_copper_raster_area=areas,sw_routed_vias=sum(v[0]=='/SW_NORMAL' for v in p['vias']),
        via_plane_samples=layout['via_plane_samples'],thermal_trace_screen=thermal,
        input_vin_path_35um_20C_ohms=resistance('SYS',vin['path']),sw_path_35um_20C_ohms=resistance('/SW_NORMAL',sw['path']),
        projected_loop_method='Trace/pad centers, straight internal IC/inductor/capacitor closure, sampled plane path; not field-solver or inductance',
        copper_area_method='0.01mm raster union of native copper pads, round-ended tracks and via lands; not solder-mask opening area',
        thermal_assumptions='35um outer copper,20C resistivity; legacy IPC2221 screening only; ambient40C illustrative,1A continuous prototype target; no manufacturing stackup or hardware thermal qualification')
    write_json(output,result)
    print({k:result[k] for k in ['added_tracks','added_vias','input_loop_projected_area_mm2','bootstrap_loop_projected_area_mm2','output_C33_loop_projected_area_mm2','output_C45_loop_projected_area_mm2','sw_copper_raster_area']})
    print('lengths',{k:round(result[k]['length_mm'],4) for k in ['sw','bst','bootstrap_sw_return','input_vin','input_pgnd']})


if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--scratch',required=True);a.add_argument('--rejected',required=True);a.add_argument('--output',required=True)
    v=a.parse_args();review(v.scratch,v.rejected,v.output)
