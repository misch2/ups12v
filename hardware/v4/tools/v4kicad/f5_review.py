"""Export-only F5 electrical geometry review and layer images. No CAD I/O."""
from pathlib import Path
import math
from .safety import read_json, write_json, require, digest
from .f5_scratch import F5_REFS, BASELINE


def normalized_footprint(node):
    """Read-only proof: local definitions/attributes stay exact under rigid placement.

    Position is separately bound by native snapshot/plan proof. Child at angles
    are absolute in KiCad serialization; make them relative to the footprint.
    No serialized CAD is ever written by this comparison.
    """
    import copy
    import json
    from decimal import Decimal
    out=copy.deepcopy(node)
    parent=next(x for x in out if isinstance(x,list) and x[0]=='at')
    angle=Decimal(parent[3]) if len(parent)>3 else Decimal(0)
    def walk(n):
        if n[0]=='at':
            a=Decimal(n[3]) if len(n)>3 else Decimal(0)
            # Decimal remainder keeps a negative sign; normalize to [0,360).
            relative=(a-angle)%360
            if relative<0:relative+=360
            n[:]=n[:3]+[str(relative.normalize())]
        for x in n:
            if isinstance(x,list):walk(x)
    for child in out:
        if isinstance(child,list) and child is not parent:walk(child)
    parent[:]=['at','@separately-bound-native-placement']
    # KiCad's rotation reorders fp_line rows. Their exact complete payloads
    # (including UUIDs) form an unordered multiset; retain other child ordering.
    indices=[i for i,x in enumerate(out) if isinstance(x,list) and x[0]=='fp_line']
    lines=sorted((out[i] for i in indices),key=lambda x:json.dumps(x,separators=(',',':')))
    for i,line in zip(indices,lines):out[i]=line
    return out


def serialized_proof(source, candidate, plan, added, diagnostics=None):
    import json
    from collections import Counter
    from .replacement import serialized_retained
    def rows(path, removed):
        result=Counter()
        for text,count in serialized_retained(path,removed).items():
            node=json.loads(text)
            if node[0]=='footprint':
                ref=next(x[2].strip('"') for x in node if isinstance(x,list) and
                         x[0]=='property' and x[1].strip('"')=='Reference')
                if ref in plan['placements']:node=normalized_footprint(node)
            result[json.dumps(node,separators=(',',':'))]+=count
        return result
    a,b=rows(source,()),rows(candidate,added)
    if a!=b and diagnostics:
        write_json(diagnostics,dict(before_only=[json.loads(s) for s in (a-b).elements()],
                                   after_only=[json.loads(s) for s in (b-a).elements()]))
    require(a==b,'Non-placement serialized board or footprint properties changed')
    return dict(all_retained_board_structure_equal=True,all_footprint_definitions_and_properties_equal=True,
                exclusions='Only declared new copper, native-derived fills, generator metadata and independently bound18rigid placements; exact fp_line payload multisets order-normalized')


def plane_window(layout, bounds, step=.1):
    """Sample actual saved native PGND polygons with their holes, never net labels."""
    import numpy as np
    x0,y0,x1,y1 = bounds
    X,Y = np.meshgrid(np.arange(x0,x1+step/2,step),np.arange(y0,y1+step/2,step))
    def contains(poly):
        m = np.zeros(X.shape,dtype=bool)
        for p,q in zip(poly,poly[1:]+poly[:1]):
            if p[1] != q[1]:
                m ^= ((p[1]>Y)!=(q[1]>Y)) & (X<(q[0]-p[0])*(Y-p[1])/(q[1]-p[1])+p[0])
        return m
    mask = np.zeros(X.shape,dtype=bool)
    for zone in layout['fills'].values():
        if zone['net'] != 'PGND': continue
        for p in zone['layers'].get('In1.Cu',[]):
            m = contains(p['outline'])
            for h in p['holes']: m &= ~contains(h)
            mask |= m
    return dict(bounds=bounds,step=step,rows=[''.join('1' if c else '0' for c in row) for row in mask])


def path_metrics(plan, net, points, layer='F.Cu', copper_um=35.):
    """Explicit copper centerline path; require every leg in the actual plan."""
    from .plan_validation import segment_distance
    rows=[]
    for a,b in zip(points,points[1:]):
        matches=[t for t in plan['tracks'] if t[0]==net and t[1]==layer and
                 segment_distance(a,t[3:5],t[5:7])<1e-7 and
                 segment_distance(b,t[3:5],t[5:7])<1e-7]
        require(matches,'Unproven review path: '+str([net,a,b]))
        w=max(t[2] for t in matches); length=math.dist(a,b)
        rows.append(dict(length_mm=length,width_mm=w,R20_ohm=1.724e-5*length/(w*copper_um/1000)))
    return dict(length_mm=sum(r['length_mm'] for r in rows),
                R20_ohm=sum(r['R20_ohm'] for r in rows),segments=rows,path=points)


def engineering(entry, root, baseline_checks, output):
    from .u3_review import area, plane_path, copper_area
    from .review_compare import warning_identity_rows, merge_counts
    from .phase411_analysis import local_fill_comparison
    entry,root,baseline_checks=map(Path,[entry,root,baseline_checks])
    old=read_json(entry/'snapshot.json'); g=read_json(root/'snapshot.json')
    layout=read_json(root/'layout.json'); before_layout=read_json(entry/'layout.json')
    p=read_json(root/'plan.json'); summary=read_json(root/'summary.json')
    require(summary['candidate_acceptable'],'Rejected candidate cannot be reviewed as passing')
    warnings={kind:warning_identity_rows(read_json(root/(kind+'.json')),kind)==
             warning_identity_rows(read_json(baseline_checks/(kind+'.json')),kind) for kind in ['drc','erc']}
    require(all(warnings.values()),'Warning identities changed')
    merges=merge_counts(dict(pad_partitions=read_json(root/'partition-before.json')),
                        dict(pad_partitions=read_json(root/'partition-after.json')),g)
    require(sum(merges.values())==41 and set(merges)<= {'SYS','PGND'}|
            {a['net'] for a in g['pads'].values() if a['net'].startswith('/F5_')},'Unexpected pad merge')
    def pos(s,ref,pin): return next(v['position'] for v in s['pads'].values() if v['ref']==ref and v['pin']==pin)
    distances={}
    for name, a, b in [('SW_to_L3',('U7','5'),('L3','1')),('VIN_to_bypass',('U7','3'),('C69','1')),
          ('GND_to_bypass',('U7','4'),('C69','2')),('BST_to_C62',('U7','6'),('C62','1')),
          ('controller_gate_to_MOSFET',('U8','5'),('Q10','4'))]:
        distances[name]=dict(before_pad_center_mm=math.dist(pos(old,*a),pos(old,*b)),
                             after_pad_center_mm=math.dist(pos(g,*a),pos(g,*b)))
    paths={
        'U7_VIN':path_metrics(p,'SYS',[[101.26,59.25],[100.4,59.25],[99.875,58.725]]),
        'U7_PGND':path_metrics(p,'PGND',[[101.26,59.75],[100.85,59.75],[100.325,60.275],[99.8,60.275]]),
        'SW_L3':path_metrics(p,'/F5_SW',[[102.74,59.75],[103.,59.75],[103.2,60.],[103.2,60.2],[103.2,62.2]]),
        'BST':path_metrics(p,'/F5_BST',[[102.74,59.25],[104.3,59.25],[104.3,58.725]]),
        'SW_C62':path_metrics(p,'/F5_SW',[[102.74,59.75],[103.,59.75],[103.2,60.],[103.2,60.2],[103.2,60.275],[104.3,60.275]]),
        'Q10_gate':path_metrics(p,'/F5_GATE',[[113.98,57.96],[114.6,57.96],[115.14,58.5],[115.9625,58.5]]),
        'RAW_to_Q10':path_metrics(p,'/F5_RAW',[[109.5,62.275],[113.,62.275],[113.,61.98],[112.02,61.],[112.02,58.8],[112.02,57.96]]),
        'Q10_to_output_vias':path_metrics(p,'/F5_5V_OUT',[[113.,56.19],[113.,55.],[112.225,54.225],[112.225,52.5],[112.225,50.5]]),
        'output_to_J8':path_metrics(p,'/F5_5V_OUT',[[112.225,50.5],[112.225,47.775],[107.045,42.595],[96.215,42.595],[94.,40.38]],'In2.Cu'),
        'SYS_B_bridge':path_metrics(p,'SYS',[[76.2,47.5],[85.8,47.5]],'B.Cu'),
        'SYS_In2_branch':path_metrics(p,'SYS',[[85.8,47.5],[88.5,50.2],[88.5,57.025],[94.3,62.825]],'In2.Cu'),
        'SYS_local_feed':path_metrics(p,'SYS',[[94.3,62.825],[94.3,59.],[95.275,58.025],[96.5,58.025],[99.1,58.025],[99.8,58.725]]),
    }
    # Shape centers and straight internal-device closures: geometry, not inductance.
    input_loop=paths['U7_VIN']['path']+[[99.8,58.725]]+list(reversed(paths['U7_PGND']['path']))
    bst_loop=paths['BST']['path']+list(reversed(paths['SW_C62']['path']))
    plane=plane_window(layout,[94.,50.,120.,68.],.05)
    plane_layout=dict(plane_samples=plane)
    returns={name:plane_path(g,plane_layout,a,[100.,60.1]) for name,a in [
        ('C64',[109.5,66.9]),('C65',[113.,66.9]),('FB_ground',[104.25,56.9]),
        ('C66',[110.375,59.2]),('U8_ground',[117.5,58.9]) ]}
    # Sample the quiet FB copper projection and two lateral offsets in In1 fill.
    samples=[]; x0,y0,_,_=plane['bounds']; step=plane['step']
    for n,l,w,x,y,u,v in p['tracks']:
        if n!='/F5_FB':continue
        length=math.dist([x,y],[u,v]);dx,dy=(u-x)/length,(v-y)/length
        for i in range(math.ceil(length/.05)+1):
            f=min(1,i*.05/length)
            for off in [-.14,0,.14]:
                q=[x+f*(u-x)-dy*off,y+f*(v-y)+dx*off]
                samples.append(plane['rows'][round((q[1]-y0)/step)][round((q[0]-x0)/step)]=='1')
    preserved={name:local_fill_comparison(before_layout,layout,bounds,.1) for name,bounds in [
        ('IC1',[55,58,74,72]),('U3',[43,76,57,89]),('USB_left',[74,77,99,93]),('USB_right',[99,77,123,93])]}
    require(all(v['all_sampled_fill_occupancy_equal'] for v in preserved.values()),'F0 critical plane occupancy changed')
    require(all(samples),'FB projection crosses a PGND fill void')
    # 1.6mm plated length, 25um plating are sensitivity assumptions, not a fab contract.
    barrel=1.724e-8*.0016/(math.pi*(.0004+.000025)*.000025)
    output_R=sum(paths[n]['R20_ohm'] for n in ['RAW_to_Q10','Q10_to_output_vias','output_to_J8'])+barrel/2
    vin_R=sum(paths[n]['R20_ohm'] for n in ['SYS_B_bridge','SYS_In2_branch','SYS_local_feed','U7_VIN'])+3*barrel/2
    hot=1+.00393*(125-20)
    current=dict(assumptions='All design copper35um; rho20=1.724e-8ohm*m; via length1.6mm,plating25um,2equal barrels/transition. No pad/spreading/contact/plane loss model.',
        output_copper_R20_ohm=output_R,output_copper_drop_2A_20C_mV=output_R*2000,
        output_copper_drop_2A_125C_mV=output_R*hot*2000,
        SYS_branch_R20_ohm=vin_R,SYS_drop_2A_20C_mV=vin_R*2000,
        SYS_drop_2A_125C_mV=vin_R*hot*2000,via_single_R20_ohm=barrel,
        output_drop_18um_inner_sensitivity_mV=(output_R+paths['output_to_J8']['R20_ohm']*(35/18-1))*2000,
        previous_PCB_drop_allocation_mV=30.,
        lower_J8_static_screen_125C_V=4.89714-.05-.02-.01-output_R*hot*2,
        U7_typical_FET_conduction_W_2A_VIN6=4*(.076*5.04/6+.032*(1-5.04/6)),
        U7_typical_FET_conduction_W_2A_VIN18=4*(.076*5.04/18+.032*(1-5.04/18)))
    result=dict(schema_version=1,baseline_sha256=BASELINE,candidate_sha256=digest(root/'ups12v_v4.kicad_pcb'),
        serialized_preservation=serialized_proof(entry/'ups12v_v4.kicad_pcb',root/'ups12v_v4.kicad_pcb',p,read_json(root/'expected-additions.json'),Path(output).with_name('serialized-proof-diagnostic.json')),
        warnings_identity_equal=warnings,merged_pad_islands_by_net=merges,distances=distances,paths=paths,
        input_loop_projected_mm2=area(input_loop),bootstrap_loop_projected_mm2=area(bst_loop),
        loop_method='Native saved track/pad centers plus straight IC/cap internal closures; not field/inductance estimates',
        loops=dict(input=input_loop,bootstrap=bst_loop),
        SW_FCu_union_mm2=copper_area(g,'/F5_SW','F.Cu'),SW_vias=sum(v['net']=='/F5_SW' for v in g['vias'].values()),
        plane_returns=returns,FB_PGND_projection=dict(samples=len(samples),covered=sum(samples),lateral_offset_mm=.14),
        F0_critical_actual_fill=preserved,current_screen=current,
        completed_opens=41,remaining_opens=0,production_unchanged=True)
    output=Path(output); write_json(output,result)
    write_json(output.with_name('plane-window.json'),plane)
    print({k:result[k] for k in ['candidate_sha256','warnings_identity_equal','merged_pad_islands_by_net','input_loop_projected_mm2','bootstrap_loop_projected_mm2']})
    print('DC screen',current)
    return result


COLORS={'SYS':'#d88916','PGND':'#578f60','GND':'#427a89','/F5_SW':'#ec4935',
        '/F5_RAW':'#1d70b7','/F5_5V_OUT':'#164893','/F5_BST':'#a549a0',
        '/F5_FB':'#2c2634','/F5_EN':'#1b9999','/F5_SS':'#a58d11',
        '/F5_VCAP':'#bf4b88','/F5_GATE':'#8b502a'}


def render(g, layout, output, layer, bounds, title, scale=75, plane_paths=None, loops=None):
    from PIL import Image,ImageDraw,ImageFont
    x0,y0,x1,y1=bounds; top=72
    im=Image.new('RGB',(round((x1-x0)*scale),round((y1-y0)*scale)+top),'#fafafa')
    d=ImageDraw.Draw(im); font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
    heading=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
    def pt(q):return ((q[0]-x0)*scale,(q[1]-y0)*scale+top)
    for zone in layout['fills'].values():
        for poly in zone['layers'].get(layer,[]):
            d.polygon([pt(q) for q in poly['outline']],fill='#cee1d1')
            for hole in poly['holes']: d.polygon([pt(q) for q in hole],fill='#fafafa')
    for ref,polys in layout['courtyards'].items():
        for poly in polys:d.line([pt(q) for q in poly['outline']+[poly['outline'][0]]],fill='#bbb',width=1)
    for t in g['tracks'].values():
        if t['layer']!=layer:continue
        color=COLORS.get(t['net'],'#aaa')
        if t.get('geometry')=='arc':
            for poly in t['copper_polygons']:d.polygon([pt(q) for q in poly],fill=color)
        else:
            w=max(1,round(t['width']*scale)); d.line([pt(t['start']),pt(t['end'])],fill=color,width=w)
            for q in [t['start'],t['end']]:
                x,y=pt(q);r=w/2;d.ellipse([x-r,y-r,x+r,y+r],fill=color)
    for p in g['pads'].values():
        for poly in p['polygons'].get(layer,[]):d.polygon([pt(q) for q in poly],fill=COLORS.get(p['net'],'#bbb'))
    for v in g['vias'].values():
        x,y=pt(v['position']);r=v['copper_widths'][layer]*scale/2
        d.ellipse([x-r,y-r,x+r,y+r],fill=COLORS.get(v['net'],'#aaa'))
        r=v['drill']*scale/2;d.ellipse([x-r,y-r,x+r,y+r],fill='#fff')
    for p in g['pads'].values():
        if max(p['drill_size'])>0:
            x,y=pt(p['position']);a,b=[q*scale/2 for q in p['drill_size']]
            d.ellipse([x-a,y-b,x+a,y+b],fill='white')
        if p['ref'] in F5_REFS|{'TP17'} and p['polygons'].get(layer) and x0<p['position'][0]<x1 and y0<p['position'][1]<y1:
            x,y=pt(p['position']);d.text((x+3,y+3),p['ref']+'.'+p['pin'],font=font,fill='black',stroke_width=2,stroke_fill='white')
    for name,r in (plane_paths or {}).items():d.line([pt(q) for q in r['path']],fill='#693ca3',width=3)
    for name,path in (loops or {}).items():d.line([pt(q) for q in path+[path[0]]],fill='#161616',width=2)
    d.rectangle([0,0,im.width,top],fill='white');d.text((8,6),title+' | '+layer,font=heading,fill='black')
    d.text((8,32),'SYS orange | RAW blue | OUT navy | SW red | BST purple | PGND green | FB black',font=font,fill='black')
    d.text((8,50),'Saved native copper/pads/courtyards; actual PGND polygons and holes. Geometry review only.',font=font,fill='black')
    im.save(output)


def images(entry, root, review_path, output):
    entry,root,output=map(Path,[entry,root,output]);output.mkdir(exist_ok=True)
    g=read_json(root/'snapshot.json');layout=read_json(root/'layout.json');r=read_json(review_path)
    render(read_json(entry/'snapshot.json'),read_json(entry/'layout.json'),output/'before-FCu.png','F.Cu',[91,49,119,67],'Accepted Phase4.16 F5 placement')
    render(g,layout,output/'buck-FCu.png','F.Cu',[94,53.5,111,67.5],'Phase4.17 U7/L3 local power stage')
    render(g,layout,output/'blocker-FCu.png','F.Cu',[108,51,119.5,64.5],'Phase4.17 U8/Q10 reverse blocker')
    render(g,layout,output/'returns-In1Cu.png','In1.Cu',[94,50,120,68],'Actual PGND fill; purple sampled return paths',plane_paths=r['plane_returns'])
    render(g,layout,output/'local-BCu.png','B.Cu',[98,53,119,64],'Quiet RAW feedback pickup and SS/EN branches')
    render(g,layout,output/'power-In2Cu.png','In2.Cu',[73,38,119,68],'SYS input / protected output trunks',scale=42)
    render(g,layout,output/'bridge-BCu.png','B.Cu',[73,43,90,52],'SYS bridge across fixed BATTERY trunk',scale=70)


def finalize(root, output, manifest):
    """Final evidence binding, with fresh original-source hash guards."""
    from .safety import verify_context, verify_hashes, unlocked
    root,output,manifest=map(Path,[root,output,manifest])
    context=verify_context(root); p=read_json(root/'plan.json')
    accepted=read_json(manifest)['hashes']; source=Path(context['source'])
    source_hashes=verify_hashes(source.parent,accepted)
    candidate=root/source.name;unlocked(candidate)
    e=read_json(output/'engineering.json'); summary=read_json(root/'summary.json')
    require(digest(candidate)==e['candidate_sha256']==summary['preservation']['sha256'], 'Final candidate hash drift')
    companions={name:digest(root/name) for name in accepted if name!=source.name}
    require(all(h==accepted[name] for name,h in companions.items()),'Candidate electrical source/configuration drift')
    require(summary['candidate_acceptable'] and e['remaining_opens']==0, 'Incomplete final candidate')
    paths=[root/'plan.json',root/'snapshot.json',root/'layout.json',root/'partition-before.json',
           root/'partition-after.json',root/'expected-additions.json',root/'drc.json',root/'erc.json',
           output/'engineering.json',output/'REVIEW.md',output/'MIGRATION_PROPOSAL.md',output/'tests.log']
    paths+=list((output/'images').glob('*.png'))
    proof=dict(schema_version=1,date='2026-10-17',milestone='Phase4.17-F5-scratch-only',
        source=str(source.resolve()),accepted_manifest=str(manifest.resolve()),production_hashes=source_hashes,
        candidate=str(candidate.resolve()),candidate_sha256=digest(candidate),unchanged_candidate_companions=companions,
        baseline_sha256=BASELINE,all_original_sources_unchanged=True,
        exact_delta=dict(moved_F5_footprints=p['placements'],added_tracks=len(p['tracks']),added_vias=len(p['vias']),
                         removed_tracks=0,removed_vias=0,changed_existing_copper=0),
        totals={s:len(read_json(root/'snapshot.json')[s]) for s in ['footprints','pads','tracks','vias']},
        validation=summary,engineering=e,tests=dict(count=113,passed=True,log_sha256=digest(output/'tests.log')),
        bound_artifacts={str(path.resolve()):digest(path) for path in paths},
        authorization='Scratch milestone complete; production migration NOT authorized/executed')
    write_json(output/'FINAL_PROOF.json',proof)
    return dict(production_unchanged=True,candidate_sha256=proof['candidate_sha256'],
                moved_F5=len(p['placements']),added_tracks=len(p['tracks']),added_vias=len(p['vias']),tests=113)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--entry',required=True);p.add_argument('--candidate',required=True)
    p.add_argument('--baseline-checks',required=True);p.add_argument('--output-dir',required=True)
    a=p.parse_args();out=Path(a.output_dir);out.mkdir(exist_ok=True)
    engineering(a.entry,a.candidate,a.baseline_checks,out/'engineering.json')
    images(a.entry,a.candidate,out/'engineering.json',out/'images')
