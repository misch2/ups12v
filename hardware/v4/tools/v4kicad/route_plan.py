"""Bounded F/B scratch planning from exported toolkit geometry only; never loads CAD.

Accounts for all-layer copper at through-vias and the existing hole clearance.
Candidate feasibility must be established by native DRC, not this raster screen.
"""
import heapq
import math


def plan_routes(g, connections, bounds, width, step=.05, source_layer='F.Cu', target_layer='F.Cu',
                route_layers=('F.Cu','B.Cu')):
    import numpy as np
    from .safety import require
    x0,y0,x1,y1=bounds
    nx,ny=round((x1-x0)/step)+1,round((y1-y0)/step)+1
    tracks=list(g['tracks'].values());vias=list(g['vias'].values())
    all_pads=list(g['pads'].values())
    pads={(p['ref'],p['pin']):p for p in all_pads}
    output=dict(failure=None,tracks=[],vias=[],metrics=[])
    layers=list(route_layers);all_layers=['F.Cu','In1.Cu','In2.Cu','B.Cu']
    require(len(layers)==2 and len(set(layers))==2 and set(layers)<= {'F.Cu','In2.Cu','B.Cu'},
            'Choose two explicit routing layers; In1.Cu remains the PGND reference plane')
    require(source_layer in layers and target_layer in layers, 'Unsupported endpoint layer')

    def cells(a,b,r):
        ix=min(nx,max(0,math.floor((min(a[0],b[0])-r-x0)/step)));ex=max(0,min(nx,math.ceil((max(a[0],b[0])+r-x0)/step)+1))
        iy=min(ny,max(0,math.floor((min(a[1],b[1])-r-y0)/step)));ey=max(0,min(ny,math.ceil((max(a[1],b[1])+r-y0)/step)+1))
        X,Y=np.meshgrid(x0+np.arange(ix,ex)*step,y0+np.arange(iy,ey)*step)
        return ix,ex,iy,ey,X,Y

    def line(grid,a,b,r):
        ix,ex,iy,ey,X,Y=cells(a,b,r)
        dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
        t=np.clip(((X-a[0])*dx+(Y-a[1])*dy)/den,0,1) if den else 0
        grid[iy:ey,ix:ex] |= (X-a[0]-t*dx)**2+(Y-a[1]-t*dy)**2 <= r*r

    def polygon(grid,p,r):
        a=[min(v[i] for v in p) for i in [0,1]];b=[max(v[i] for v in p) for i in [0,1]]
        ix,ex,iy,ey,X,Y=cells(a,b,r);inside=np.zeros(X.shape,dtype=bool)
        for v,w in zip(p,p[1:]+p[:1]):
            if v[1]!=w[1]:inside ^= ((v[1]>Y)!=(w[1]>Y)) & (X<(w[0]-v[0])*(Y-v[1])/(w[1]-v[1])+v[0])
        grid[iy:ey,ix:ex] |= inside
        for v,w in zip(p,p[1:]+p[:1]):line(grid,v,w,r)

    def blocked(net,layer,margin,hole_margin):
        grid=np.zeros((ny,nx),dtype=bool)
        # Explicit planning-only corridors/keepouts, never instantiated as CAD.
        for region in g.get('routing_exclusions', []):
            if layer in region['layers']:
                polygon(grid, region['polygon'], margin)
        for t in tracks:
            if t['net']!=net and t['layer']==layer:line(grid,t['start'],t['end'],t['width']/2+margin)
        for p in all_pads:
            if p['net']!=net:
                for poly in p['polygons'].get(layer,[]):polygon(grid,poly,margin)
                if max(p['drill_size'])>0:line(grid,p['position'],p['position'],max(p['drill_size'])/2+hole_margin)
        if layer=='F.Cu':
            for ref in {p['ref'] for p in all_pads if p['ref'].startswith('NT')}:
                group=[p for p in all_pads if p['ref']==ref]
                if any(p['net']==net for p in group):continue
                points=[v for p in group for polys in p['polygons'].values() for poly in polys for v in poly]
                lo=[min(v[i] for v in points) for i in [0,1]];hi=[max(v[i] for v in points) for i in [0,1]]
                polygon(grid,[[lo[0],lo[1]],[hi[0],lo[1]],[hi[0],hi[1]],[lo[0],hi[1]]],margin)
        for v in vias:
            if v['net']!=net:line(grid,v['position'],v['position'],max(v['copper_widths'][layer]/2+margin,v['drill']/2+hole_margin))
        return grid

    for net,ref1,pin1,ref2,pin2 in connections:
        a,b=pads[(ref1,pin1)],pads[(ref2,pin2)]
        require(a['net']==net==b['net'],'Connection net mismatch; STOP')
        blocked_layers=[blocked(net,l,width/2+.11,width/2+.26) for l in layers]
        via_block=np.zeros((ny,nx),dtype=bool)
        for l in all_layers:via_block |= blocked(net,l,.25+.15,.15+.31)
        # A same-net drill is still a physical hole, not a legal new via site.
        for p in all_pads:
            if max(p['drill_size'])>0:
                line(via_block,p['position'],p['position'],max(p['drill_size'])/2+.15+.26)
        for v in vias:
            line(via_block,v['position'],v['position'],v['drill']/2+.15+.26)
        # Net-tie copper bridges are footprint graphics outside the pad snapshot.
        # Conservatively forbid holes near the entire pad group, preserving bridges.
        for ref in {p['ref'] for p in all_pads if p['ref'].startswith('NT')}:
            points=[v for p in all_pads if p['ref']==ref for polys in p['polygons'].values() for poly in polys for v in poly]
            lo=[min(v[i] for v in points) for i in [0,1]];hi=[max(v[i] for v in points) for i in [0,1]]
            polygon(via_block,[[lo[0],lo[1]],[hi[0],lo[1]],[hi[0],hi[1]],[lo[0],hi[1]]],.41)
        def gridpt(p):return (round((p[0]-x0)/step),round((p[1]-y0)/step))
        # Existing same-net through-vias/PTH pads are legal layer transitions,
        # not sites for another drilled hole. Reuse their exact native centres.
        existing_transitions={}
        for item in [v for v in vias if v['net']==net and all(v['copper_widths'].get(l,0)>0 for l in layers)]+[
            p for p in all_pads if p['net']==net and max(p['drill_size'])>0 and all(p['polygons'].get(l) for l in layers)]:
            ix,iy=gridpt(item['position'])
            if 0<=ix<nx and 0<=iy<ny:existing_transitions[(iy,ix)]=item['position']
        sx,sy=gridpt(a['position']);tx,ty=gridpt(b['position'])
        require(0<=sx<nx and 0<=tx<nx and 0<=sy<ny and 0<=ty<ny,'Endpoint outside bounded region')
        source=(layers.index(source_layer),sy,sx);target=(layers.index(target_layer),ty,tx)
        require(not blocked_layers[source[0]][sy,sx] and not blocked_layers[target[0]][ty,tx], 'Endpoint blocked in screen')
        heap=[(0.,0.,source)];distance={source:0.};parent={};found=False
        moves=[(dx,dy,math.hypot(dx,dy)*step) for dx in [-1,0,1] for dy in [-1,0,1] if dx or dy]
        while heap:
            _,cost,node=heapq.heappop(heap)
            if cost!=distance[node]:continue
            if node==target:found=True;break
            layer,y,x=node
            for dx,dy,dc in moves:
                xx,yy=x+dx,y+dy
                if not (0<=xx<nx and 0<=yy<ny) or blocked_layers[layer][yy,xx]:continue
                if dx and dy and (blocked_layers[layer][y,xx] or blocked_layers[layer][yy,x]):continue
                nxt=(layer,yy,xx);new=cost+dc
                if new<distance.get(nxt,float('inf')):
                    distance[nxt]=new;parent[nxt]=node
                    heapq.heappush(heap,(new+math.hypot(tx-xx,ty-yy)*step,new,nxt))
            if ((y,x) in existing_transitions or not via_block[y,x]) and not blocked_layers[1-layer][y,x]:
                nxt=(1-layer,y,x);new=cost+(.05 if (y,x) in existing_transitions else 5.)
                if new<distance.get(nxt,float('inf')):
                    distance[nxt]=new;parent[nxt]=node
                    heapq.heappush(heap,(new+math.hypot(tx-x,ty-y)*step,new,nxt))
        require(found,f'No route in bounded screen for {ref1}.{pin1} to {ref2}.{pin2}; STOP')
        path=[target]
        while path[-1]!=source:path.append(parent[path[-1]])
        path.reverse()
        # Remove grid staircases only where the complete chord remains screened.
        reduced=[];begin=0
        while begin<len(path):
            finish=begin
            while finish+1<len(path) and path[finish+1][0]==path[begin][0]:finish+=1
            run=path[begin:finish+1];i=0;reduced.append(run[0])
            while i<len(run)-1:
                j=len(run)-1
                chosen=None
                while j>i+1:
                    _,ay,ax=run[i];_,by,bx=run[j]
                    dx,dy=bx-ax,by-ay;d=min(abs(dx),abs(dy));sx=1 if dx>=0 else -1;sy=1 if dy>=0 else -1
                    corners=[(ax+sx*d,ay+sy*d),(bx-sx*d,by-sy*d)]
                    def clear_leg(a,b):
                        n=max(2,math.ceil(math.dist(a,b)*4));xx=np.linspace(a[0],b[0],n);yy=np.linspace(a[1],b[1],n)
                        return all(not blocked_layers[run[i][0]][ys,xs].any()
                            for xs in [np.floor(xx).astype(int),np.ceil(xx).astype(int)]
                            for ys in [np.floor(yy).astype(int),np.ceil(yy).astype(int)])
                    chosen=next((c for c in corners if clear_leg((ax,ay),c) and clear_leg(c,(bx,by))),None)
                    if chosen is not None:break
                    j-=1
                if chosen is not None:
                    middle=(run[i][0],chosen[1],chosen[0])
                    if middle!=reduced[-1] and middle!=run[j]:reduced.append(middle)
                reduced.append(run[j]);i=j
            begin=finish+1
        path=reduced
        def xy(node):return existing_transitions.get((node[1],node[2]),[round(x0+node[2]*step,6),round(y0+node[1]*step,6)])
        # Preserve direction changes, compress only exactly collinear grid legs.
        runs=[];start=path[0];previous=path[0];direction=None
        for node in path[1:]:
            if node[0]!=previous[0]:
                if start!=previous:runs.append((layers[previous[0]],xy(start),xy(previous)))
                p=xy(node)
                if (node[1],node[2]) not in existing_transitions:
                    output['vias'].append([net,*p,.5,.3]);vias.append(dict(net=net,position=p,drill=.3,copper_widths={l:.5 for l in all_layers}))
                start=node;direction=None
            else:
                newdir=(node[2]-previous[2],node[1]-previous[1])
                if direction is not None and newdir!=direction:
                    runs.append((layers[previous[0]],xy(start),xy(previous)));start=previous
                direction=newdir
            previous=node
        if start!=previous:runs.append((layers[previous[0]],xy(start),xy(previous)))
        # Absorb exact-pad/grid offsets into adjacent legs, avoiding duplicate
        # microscopic centre-correction tracks. Native preflight checks the result.
        if runs and runs[0][0]==source_layer:runs[0]=(runs[0][0],a['position'],runs[0][2])
        elif a['position']!=xy(source):runs.insert(0,(source_layer,a['position'],xy(source)))
        if runs and runs[-1][0]==target_layer:runs[-1]=(runs[-1][0],runs[-1][1],b['position'])
        elif b['position']!=xy(target):runs.append((target_layer,xy(target),b['position']))
        length=0.
        for layer,p,q in runs:
            if p==q:continue
            output['tracks'].append([net,layer,width,*p,*q]);tracks.append(dict(net=net,layer=layer,width=width,start=p,end=q));length+=math.dist(p,q)
        output['metrics'].append(dict(net=net,source=ref1+'.'+pin1,target=ref2+'.'+pin2,length_mm=length))
    return output


if __name__=='__main__':
    import argparse
    from .safety import read_json,write_json
    p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--connections',required=True)
    p.add_argument('--output',required=True);p.add_argument('--bounds',type=float,nargs=4,required=True)
    p.add_argument('--width',type=float,required=True)
    a=p.parse_args();result=plan_routes(read_json(a.snapshot),read_json(a.connections),a.bounds,a.width)
    write_json(a.output,result);print(dict(tracks=len(result['tracks']),vias=len(result['vias']),metrics=result['metrics']))
