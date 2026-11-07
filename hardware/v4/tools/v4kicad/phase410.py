"""Phase 4.10 exported-evidence planning; no native APIs or work on import."""
import argparse
import copy
import math
from pathlib import Path
from .safety import read_json, write_json, require, ToolError
from .f0_plan import poly, append, incremental_tracks, reservations
from .route_plan import plan_routes
from .plan_validation import check_plan, review_regions, clean_microlegs


def refine(plan, context):
    """Absorb source-grid offsets inside pads, not into tiny oblique legs."""
    p=copy.deepcopy(plan)
    moves={('BATTERY','F.Cu',74.9,64.3875):(74.9,64.4),
        ('PMID','F.Cu',37.,71.7375):(37.,71.75),
        ('PMID','F.Cu',38.8,83.5375):(38.8,83.55),
        ('USB_CC1','F.Cu',113.49,75.5):(113.5,75.5),
        ('USB_CC1','In2.Cu',113.65,78.55):(113.65,78.535),
        ('USB_CC2','F.Cu',116.49,74.):(116.5,74.),
        ('USB_CC2','In2.Cu',119.8,78.65):(119.8,78.665)}
    for t in p['tracks']:
        for start in [3,5]:
            key=tuple(t[:2]+t[start:start+2])
            if key in moves:t[start:start+2]=moves[key]
    # Merge exactly collinear consecutive additions only. Original copper is
    # never enumerated as removable or modified.
    changed=True
    while changed:
        changed=False
        for i,a in enumerate(p['tracks']):
            for j,b in enumerate(p['tracks']):
                if i==j or a[:3]!=b[:3] or a[5:7]!=b[3:5]:continue
                u=[a[5]-a[3],a[6]-a[4]];v=[b[5]-b[3],b[6]-b[4]]
                if abs(u[0]*v[1]-u[1]*v[0])>1e-9 or sum(x*y for x,y in zip(u,v))<=0:continue
                node=a[5:7]
                if any(q[0]==a[0] and q[1:3]==node for q in p['vias']):continue
                p['tracks']=[r for k,r in enumerate(p['tracks']) if k not in [i,j]]+[a[:5]+b[5:7]]
                changed=True;break
            if changed:break
    require(check_plan(context['snapshot'],p,context)['valid'],'Refined additions conflict')
    p['review_regions']=review_regions(p)
    return p


def build(context):
    require(context['board_sha256']=='a3ba56068026a6942c4ca22d7e0eee8f5f2320afc4defefabbbcee3861b29a78',
        'Historical Phase4.10 planner requires its exact accepted entry baseline; never replay on the installed board')
    g = copy.deepcopy(context['snapshot'])
    reservations(g, context)
    p = dict(failure=None, tracks=[], vias=[], metrics=[], blocked=[])
    # Three parallel local connections per optional bulk pad. These are not
    # decorative stitches: each closes an isolated pad to the existing plane.
    pads = {(v['ref'],v['pin']):v for v in g['pads'].values()}
    for ref, vx in [('C20',45.2),('C22',43),('C24',35.6),('C25',37.4)]:
        pad = pads[(ref,'2')]
        require(pad['net']=='PGND','Bulk return net changed')
        x,y = pad['position']
        q = dict(failure=None, tracks=[], vias=[], metrics=[])
        for dy in [-.7,0,.7]:
            poly(q,'PGND','F.Cu',.8,[[x,y+dy],[vx,y+dy]])
            q['vias'].append(['PGND',vx,y+dy,.6,.3])
        candidate = dict(failure=None,tracks=p['tracks']+q['tracks'],vias=p['vias']+q['vias'])
        r = check_plan(context['snapshot'],candidate,context)
        if r['valid']:
            append(g,p,q)
            p['metrics'].append(dict(ref=ref,purpose='isolated bulk PGND pad',parallel_vias=3))
        else:p['blocked'].append(dict(ref=ref,reason='Joint return validator',findings=r))
    for ref in ['R13','R14']:
        x,y=pads[(ref,'2')]['position']
        require(pads[(ref,'2')]['net']=='PGND','CC return net changed')
        q=dict(failure=None,tracks=[['PGND','F.Cu',.3,x,y,x+.65,y]],
               vias=[['PGND',x+.65,y,.5,.3]],metrics=[])
        r=check_plan(context['snapshot'],dict(failure=None,tracks=p['tracks']+q['tracks'],vias=p['vias']+q['vias']),context)
        if r['valid']:append(g,p,q)
        else:p['blocked'].append(dict(ref=ref,reason='CC ground return blocked',findings=r))
    # Optional bulk detour stays outside C12's short existing bypass loop.
    bulk=dict(failure=None,tracks=[],vias=[],metrics=[])
    poly(bulk,'PMID','F.Cu',1.2,[[47,49.4],[49.175,51.575]])
    poly(bulk,'PMID','F.Cu',1.0,[[49.175,51.575],[49.175,55.725],
        [49.925,56.475],[51.2,56.475]])
    r=check_plan(context['snapshot'],dict(failure=None,tracks=p['tracks']+bulk['tracks'],vias=p['vias']),context)
    if r['valid']:append(g,p,bulk)
    else:p['blocked'].append(dict(net='PMID',endpoints=['C12','1','C20','1'],reason='Wide front detour blocked',findings=r))
    # Meters/testpoints and BATP sensing draw negligible branch current. They
    # neither replace nor narrow the retained power-current routes.
    tasks = [
        ('VIN1','TP15','1','@vin','1',.3,[32,42,43,60],'F.Cu','F.Cu',('F.Cu','In2.Cu')),
        ('BATTERY','TP16','1','@bat','1',.3,[73,39,82,48],'F.Cu','In2.Cu',('F.Cu','In2.Cu')),
        ('BATTERY','R4','2','@sense','1',.25,[72,62,78,70],'F.Cu','In2.Cu',('F.Cu','In2.Cu')),
        ('PMID','C20','1','C22','1',1.2,[38,47,50,56],'F.Cu','F.Cu',('F.Cu','In2.Cu')),
        ('PMID','C22','1','C24','1',1.2,[33,52,46,74],'F.Cu','F.Cu',('F.Cu','In2.Cu')),
        ('PMID','C24','1','C25','1',1.2,[33,69,44,85],'F.Cu','F.Cu',('F.Cu','In2.Cu')),
        ('USB_CC1','R13','1','J7','A5',.18,[111,73,120,85],'F.Cu','In2.Cu',('F.Cu','In2.Cu')),
        ('USB_CC2','R14','1','J7','B5',.18,[113,72,121,83],'F.Cu','In2.Cu',('F.Cu','In2.Cu')),
    ]
    for name, net, pos, layer in [('@vin','VIN1',[39.5375,49],'F.Cu'),
            ('@bat','BATTERY',[80,46],'In2.Cu'),('@sense','BATTERY',[74.9,67.45],'In2.Cu')]:
        g['pads'][name]=dict(ref=name,pin='1',net=net,position=pos,polygons={},drill_size=[0,0])
    for net, a, ap, b, bp, w, bounds, sl, tl, layers in tasks:
        print('Screening '+net+' '+a+' -> '+b,flush=True)
        try:
            q=incremental_tracks(g,plan_routes(g,[[net,a,ap,b,bp]],bounds,w,
                source_layer=sl,target_layer=tl,route_layers=layers))
            r=check_plan(context['snapshot'],dict(failure=None,
                tracks=p['tracks']+q['tracks'],vias=p['vias']+q['vias']),context)
            require(r['valid'],'Joint validator rejects route: '+str(r.get('violations',[])[:3]))
            # Bulk capacitor connections must remain wide and on F.Cu. A single
            # small through-via would transfer ripple to a weaker bottleneck.
            require(net!='PMID' or not q['vias'],'PMID transition needs an independently sized via bank')
            start = next(v['position'] for v in g['pads'].values() if v['ref']==a and v['pin']==ap)
            end = next(v['position'] for v in g['pads'].values() if v['ref']==b and v['pin']==bp)
            length=sum(math.dist(t[3:5],t[5:7]) for t in q['tracks'])
            require(length<=max(math.dist(start,end)*1.8,math.dist(start,end)+4),'Excessive detour')
            require(len(q['vias'])<=2,'More than two new transitions')
            append(g,p,q)
            p['metrics'].append(dict(net=net,endpoints=[a,ap,b,bp],length_mm=length))
        except ToolError as e:p['blocked'].append(dict(net=net,endpoints=[a,ap,b,bp],reason=str(e)))
    p,actions=clean_microlegs(p,context)
    p['microleg_cleanup']=actions
    p['review_regions']=review_regions(p)
    return refine(p,context)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--context',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    require(not args.output.exists(),'Fresh plan output required')
    p=build(read_json(args.context));write_json(args.output,p)
    print(dict(tracks=len(p['tracks']),vias=len(p['vias']),blocked=len(p['blocked'])))


if __name__=='__main__':main()
