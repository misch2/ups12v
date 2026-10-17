"""Phase4.12 export-only hand-routing sketches and geometric screening.

No native imports, CAD writes, route search or A*. All proposed polylines are
explicit owner-editing sketches. Geometric checks are not post-edit native DRC.
"""
import copy
import math
from pathlib import Path
from .safety import read_json,write_json,require
from .plan_validation import check_plan,inventory,shape,separation,inside,nearby
from .usb_review import analyze


ROOT=Path('hardware/v4/evidence/phase4-11-owner-confirmed-native')


def load():
    return read_json(ROOT/'snapshot.json'),read_json(ROOT/'routing-context.json'),read_json(ROOT/'layout.json')


def transform(point,old,new,angle):
    r=math.radians(angle-old['angle']);c,s=math.cos(r),math.sin(r)
    u,v=point[0]-old['position'][0],point[1]-old['position'][1]
    return [round(new[0]+c*u+s*v,6),round(new[1]-s*u+c*v,6)]


def moved_U2(g,layout,center,angle=90):
    result=copy.deepcopy(g)
    old=next(f for f in g['footprints'].values() if f['ref']=='U2')
    for pad in result['pads'].values():
        if pad['ref']!='U2':continue
        pad['position']=transform(pad['position'],old,center,angle)
        pad['polygons']={l:[[transform(p,old,center,angle) for p in poly] for poly in polys]
                         for l,polys in pad['polygons'].items()}
    court=[[transform(p,old,center,angle) for p in poly['outline']] for poly in layout['courtyards']['U2']]
    return result,court


def add_poly(rows,net,width,points,layer='F.Cu'):
    for a,b in zip(points,points[1:]):
        if a!=b:rows.append([net,layer,width,*a,*b])


def planning_context(context):
    c=copy.deepcopy(context)
    # USB planning reservations belong to the USB task; RF/F5/CAD rules remain.
    c['reservations']=[r for r in c['reservations'] if not r['name'].startswith('USB ')]
    return c


def courtyard_gaps(court,layout):
    result=[]
    for ref,polys in layout['courtyards'].items():
        if ref=='U2' or not polys:continue
        gap=min(separation(shape('U2','','F.Cu',a,polygon=True),
                           shape(ref,'','F.Cu',b['outline'],polygon=True)) for a in court for b in polys)
        result.append(dict(ref=ref,gap_mm=gap))
    return sorted(result,key=lambda x:x['gap_mm'])


def pad_screen(g,context,ref):
    copper,holes=inventory(g,context)
    pads=[v for v in copper if v.get('ref')==ref]
    # Native inventory identifies pads by UUID, not ref on every schema.
    ids={u for u,p in g['pads'].items() if p['ref']==ref}
    pads=[v for v in copper if v['id'] in ids]
    violations=[];best=None
    for a in pads:
        for b in copper:
            if b['id'] in ids or b['net']==a['net'] or b['layer']!=a['layer']:continue
            if not nearby(a,b,2):continue
            gap=separation(a,b)
            if best is None or gap<best['gap_mm']:
                best=dict(gap_mm=gap,pad_uuid=a['id'],other_uuid=b['id'],other_net=b['net'])
            if gap<context['profile']['copper_clearance']-1e-6:
                violations.append(dict(kind='pad_copper',gap_mm=gap,against=b['id'],net=b['net']))
        for h in holes:
            if not nearby(a,h,context['profile']['hole_clearance']):continue
            gap=separation(a,h)
            if gap<context['profile']['hole_clearance']-1e-6:
                violations.append(dict(kind='pad_drill',gap_mm=gap,against=h['id']))
    return dict(minimum=best,violations=violations)


def u2_candidate(center,ground=None):
    g,context,layout=load()
    paths=analyze(g)['paths']
    retained,court=moved_U2(g,layout,center)
    removed=[]
    for key in ['USB_DP_A_to_R48','USB_DN_A_to_R49']:
        removed.extend(paths[key]['tracks'][:4])
    for uid in removed:del retained['tracks'][uid]
    pads={p['pin']:p for p in retained['pads'].values() if p['ref']=='U2'}
    rows=[];incoming={};outgoing={}
    for net,pin,jpin,end in [('USB_DP','1','A6',[116.84,85.464239]),
                             ('USB_DN','2','A7',[116.44002,85.629917])]:
        start=next(p['position'] for p in g['pads'].values() if p['ref']=='J7' and p['pin']==jpin)
        target=pads[pin]['position'];dy=target[1]-start[1]
        require(dy>=0,'This explicit sketch assumes U2 data pads south of corresponding J7 contacts')
        points=[start,[round(target[0]+dy,6),start[1]],target]
        incoming[net]=points
        add_poly(rows,net,.2,points)
        if pin=='1':
            q=[target,[target[0],83.0],[end[0],round(83.0+end[0]-target[0],6)],end]
        else:
            x=round(target[0]-.4,6)
            q=[target,[x,round(target[1]+.4,6)],[x,83.165686],
               [end[0],round(83.165686+end[0]-x,6)],end]
        outgoing[net]=q
        add_poly(rows,net,.2,q)
    ground=ground or [round(center[0]-1.016,6),center[1]]
    add_poly(rows,'PGND',.5,[pads['3']['position'],ground])
    plan=dict(mode='export-only-owner-sketch',failure=None,tracks=rows,vias=[['PGND',*ground,.6,.3]])
    c=planning_context(context)
    check=check_plan(retained,plan,c)
    padcheck=pad_screen(retained,c,'U2')
    courts=courtyard_gaps(court,layout)
    length=lambda pts:sum(math.dist(a,b) for a,b in zip(pts,pts[1:]))
    return dict(center=center,rotation=90,ground_via=ground,ground_pad_to_via_mm=math.dist(pads['3']['position'],ground),
                incoming=incoming,outgoing=outgoing,incoming_lengths_mm={n:length(q) for n,q in incoming.items()},
                removed_track_uuids=removed,retained_source_objects=True,proposed_plan=plan,
                joint_check=check,pad_check=padcheck,nearest_courtyards=courts[:4],
                courtyard_outline=court,pad_positions={p:q['position'] for p,q in pads.items()},
                valid=check['valid'] and not padcheck['violations'] and courts[0]['gap_mm']>=0)


def mcu_candidate(kind):
    g,c,l=load();base=copy.deepcopy(g);nets={'/USB_MCU_DP','/USB_MCU_DN'}
    removed_vias=[u for u,v in base['vias'].items() if v['net'] in nets]
    for u in removed_vias:del base['vias'][u]
    removed_tracks=[u for u,t in base['tracks'].items() if t['net'] in nets and t['layer']=='B.Cu']
    for u in removed_tracks:del base['tracks'][u]
    rows=[];vias=[];paths={}
    if kind=='direct-front':
        paths={'/USB_MCU_DP':[[77.724,91.4],[78.524,90.6],[91.656,90.6],[92.456,91.4]],
               '/USB_MCU_DN':[[77.724,90.2],[92.456,90.2]]}
        for n,p in paths.items():add_poly(rows,n,.2,p)
    elif kind=='short-bridge':
        sections=[('/USB_MCU_DP','F.Cu',[[77.724,91.4],[78.524,90.6],[84.92,90.6],[84.92,91.42],[85.3,91.8]]),
                  ('/USB_MCU_DN','F.Cu',[[77.724,90.2],[83.6,90.2],[83.8,90.0]]),
                  ('/USB_MCU_DP','B.Cu',[[85.3,91.8],[85.7,91.4],[90.6,91.4],[91.0,91.8]]),
                  ('/USB_MCU_DN','B.Cu',[[83.8,90.0],[84.8,91.0],[90.6,91.0],[91.0,90.6]]),
                  ('/USB_MCU_DP','F.Cu',[[91,91.8],[91.4,91.4],[92.456,91.4]]),
                  ('/USB_MCU_DN','F.Cu',[[91,90.6],[91.4,90.2],[92.456,90.2]])]
        for n,layer,p in sections:
            add_poly(rows,n,.2,p,layer);paths[n+':'+layer+':'+str(len(paths))]=p
        vias=[['/USB_MCU_DP',85.3,91.8,.6,.3],['/USB_MCU_DN',83.8,90.0,.6,.3],
              ['/USB_MCU_DP',91,91.8,.6,.3],['/USB_MCU_DN',91,90.6,.6,.3]]
    else:raise ValueError(kind)
    plan=dict(mode='export-only-owner-sketch',failure=None,tracks=rows,vias=vias)
    check=check_plan(base,plan,planning_context(c))
    return dict(kind=kind,valid=check['valid'],joint_check=check,proposed_plan=plan,
                paths=paths,removed_track_uuids=removed_tracks,removed_via_uuids=removed_vias)


def b_return_candidate(locations=None):
    g,c,l=load();base=copy.deepcopy(g)
    resized=[]
    for uid,v in base['vias'].items():
        if v['net'] not in {'/USB_MCU_DP','/USB_MCU_DN'}:continue
        resized.append(uid);v['drill']=.3;v['copper_widths']={layer:.6 for layer in v['copper_widths']}
    locations=locations or [[77.724,89.4],[77.724,92.2],[92.456,89.4],[92.456,92.2]]
    vias=[['PGND',*q,.6,.3] for q in locations]
    plan=dict(mode='export-only-owner-sketch',failure=None,tracks=[],vias=vias)
    check=check_plan(base,plan,planning_context(c))
    return dict(valid=check['valid'],joint_check=check,resized_signal_via_uuids=resized,proposed_plan=plan,
                note='Current fills remain the actual baseline. Smaller signal antipads and final return continuity need native refill/DRC after owner edits; no adjacent continuous In2 ground is created.')


def vbus_candidate():
    g,c,l=load();base=copy.deepcopy(g)
    removed=['39538545-32d8-47ee-a046-9dc6968c3827','71a59df5-5100-46e4-86cb-c026d529adfd',
             'd6cf62d7-25da-4f4e-ad79-c4ed034f2ce6','a337c176-ea75-471f-a3af-00d1b665f425',
             '295e14df-333f-4a1f-a8d8-67ec04f6f208']
    for u in removed:del base['tracks'][u]
    del base['vias']['a3b8a2f5-dcb0-48c8-be4b-75eb3930c432']
    main=[[117.39,78.875],[113.594,78.875],[106.032,78.875],[106.032,80.518]]
    branch=[[113.594,77.978],[113.594,78.875]]
    rows=[];add_poly(rows,'USB_VBUS',.6,main);add_poly(rows,'USB_VBUS',.3,branch)
    plan=dict(mode='export-only-owner-sketch',failure=None,tracks=rows,vias=[])
    check=check_plan(base,plan,planning_context(c))
    return dict(valid=check['valid'],joint_check=check,proposed_plan=plan,main=main,branch=branch,
                removed_track_uuids=removed,removed_via_uuid='a3b8a2f5-dcb0-48c8-be4b-75eb3930c432')


def materialize(g,plan,prefix='planning'):
    """Materialize an exported-geometry sketch only; never create/save CAD."""
    result=copy.deepcopy(g)
    for i,(n,layer,w,x,y,xx,yy) in enumerate(plan['tracks']):
        uid=prefix+'-track-'+str(i)
        require(uid not in result['tracks'],'Export planning ID collision')
        result['tracks'][uid]=dict(uuid=uid,net=n,kind='track',layer=layer,width=w,start=[x,y],end=[xx,yy])
    for i,(n,x,y,d,h) in enumerate(plan['vias']):
        uid=prefix+'-via-'+str(i)
        require(uid not in result['vias'],'Export planning ID collision')
        result['vias'][uid]=dict(uuid=uid,net=n,kind='via',position=[x,y],drill=h,
            copper_widths={layer:d for layer in ['F.Cu','In1.Cu','In2.Cu','B.Cu']})
    return result


def candidate_base(g,candidate):
    result=copy.deepcopy(g)
    for uid in candidate.get('removed_track_uuids',[]):del result['tracks'][uid]
    for uid in candidate.get('removed_via_uuids',[]):del result['vias'][uid]
    if candidate.get('removed_via_uuid'):del result['vias'][candidate['removed_via_uuid']]
    return result


def combined_proposal():
    """Jointly screen the three explicit sketches, including their return vias."""
    g,c,l=load()
    u=u2_candidate([115.0,81.4],[113.984,81.4])
    m=mcu_candidate('short-bridge');v=vbus_candidate()
    base,court=moved_U2(g,l,u['center'])
    for candidate in [u,m,v]:base=candidate_base(base,candidate)
    plan=dict(mode='export-only-owner-sketch',failure=None,tracks=[],vias=[])
    for candidate in [u,m,v]:
        for key in ['tracks','vias']:plan[key].extend(candidate['proposed_plan'][key])
    returns=[[85.3,92.6],[83.0,91.2],[91.0,92.6],[91.0,89.8]]
    plan['vias'].extend([['PGND',*q,.6,.3] for q in returns])
    check=check_plan(base,plan,planning_context(c))
    proposed=materialize(base,plan)
    return dict(valid=check['valid'],joint_check=check,proposed_plan=plan,
                u2=u,mcu=m,vbus=v,return_vias=returns,
                removed_track_uuids=u['removed_track_uuids']+m['removed_track_uuids']+v['removed_track_uuids'],
                removed_via_uuids=m['removed_via_uuids']+[v['removed_via_uuid']]),proposed


def summarize_proposal(output):
    from .usb_review import analyze_3d,_pair_spacing
    from .legacy_review import reference_samples
    g,c,l=load();proposal,after=combined_proposal()
    heights=read_json('hardware/v4/evidence/phase4-11-source-confirmed/nominal-stackup.json')['copper_center_z_mm']
    def summary(snapshot):
        a=analyze(snapshot)
        layers={}
        for n in ['/USB_MCU_DP','/USB_MCU_DN']:
            layers[n]={layer:sum(math.dist(t['start'],t['end']) for t in snapshot['tracks'].values()
                                if t['net']==n and t['layer']==layer) for layer in ['F.Cu','B.Cu']}
        spacing={n+':'+layer:_pair_spacing(snapshot,*nets,layer) for n,nets in
                 [('connector',('USB_DP','USB_DN')),('MCU',('/USB_MCU_DP','/USB_MCU_DN'))]
                 for layer in ['F.Cu','B.Cu']}
        return dict(planar=a,nominal_3d=analyze_3d(snapshot,heights),mcu_layer_lengths=layers,spacing=spacing)
    source=summary(g);proposed=summary(after)
    ftracks=[t for t in after['tracks'].values() if t['net'] in {'/USB_MCU_DP','/USB_MCU_DN'} and t['layer']=='F.Cu']
    reference=reference_samples(after,ftracks,l,c)
    fills=[p for z in l['fills'].values() if z['net']=='PGND' for p in z['layers'].get('In1.Cu',[])]
    positions=proposal['return_vias']+[proposal['u2']['ground_via']]
    ground=[dict(position=q,inside_current_In1_fill=any(inside(q,p['outline']) and not any(inside(q,h) for h in p['holes']) for p in fills)) for q in positions]
    result=dict(proposal=proposal,before=source,after=proposed,
                F_reference_projection=reference,ground_vias_current_fill=ground,
                limits='Export-only exact polylines; current native In1 fill projection includes old antipads. New signal via antipads and removed old holes require native refill after owner edits. Not native DRC or verified impedance.')
    write_json(output,result)
    return result,after


def gap_candidate():
    """Open the two existing straight necks without adding length tuning."""
    proposal,g=combined_proposal();_,c,_=load()
    # Existing R48/49 MCU fanout; retain the left endpoint positions.
    removed=['58cf192a-1ccf-47cd-b902-073704137a9f','618e899a-7d0d-4e11-b0c3-3bc503691cf2',
             'fdebadb4-ca5d-4ddf-8d5c-1b8f9ebd2b66','6ea5618e-1938-45b4-bdc3-863ded8a815e',
             '89490f32-ced8-4c24-9b02-40a8ecb551d3','e491a0a8-3cbc-4eb5-99b2-a33fd86154fe']
    removed+=['a9efacfa-34ee-47a6-8528-89b82472dd97','b4e123b2-4284-48ff-809e-490640f16771',
              '7592406e-5976-4bc7-8771-af73aedbcf83','85aba0f0-bc35-4736-82c9-9eaac62b0167',
              'b1b5e2dc-2679-4ec2-8085-cedabdd379b8']
    for uid in removed:del g['tracks'][uid]
    paths=[('/USB_MCU_DP',[[92.456,91.4],[92.874,90.982],[95.032,90.982],[95.49,91.44]]),
           ('/USB_MCU_DN',[[92.456,90.2],[92.838,90.582],[95.092,90.582],[95.49,90.184]]),
           ('USB_DN',[[96.990001,90],[97.410001,90.42],[110.405645,90.42],[111.06898,91.083335]])]
    rows=[]
    for n,p in paths:add_poly(rows,n,.2,p)
    plan=dict(mode='export-only-owner-sketch',failure=None,tracks=rows,vias=[])
    check=check_plan(g,plan,planning_context(c))
    return dict(valid=check['valid'],joint_check=check,proposed_plan=plan,paths=paths,removed_track_uuids=removed)


def focused_evidence(directory):
    import hashlib
    from .legacy_review import reference_samples
    g,c,l=load();proposal,after=combined_proposal();gap=gap_candidate()
    details={'removals':{}}
    for name,candidate in [('U2',proposal['u2']),('MCU',proposal['mcu']),('VBUS',proposal['vbus']),('gap',gap)]:
        vias=candidate.get('removed_via_uuids',[])+([candidate['removed_via_uuid']] if candidate.get('removed_via_uuid') else [])
        details['removals'][name]=dict(tracks={u:g['tracks'][u] for u in candidate.get('removed_track_uuids',[])},
                                       vias={u:g['vias'][u] for u in vias})
    temp=materialize({'tracks':{},'vias':{}},proposal['u2']['proposed_plan'])
    details['U2_current_fill_projection']=reference_samples(after,[t for t in temp['tracks'].values()
                        if t['net'] in {'USB_DP','USB_DN'}],l,c)
    authority=read_json('hardware/v4/evidence/phase4-11-source-confirmed/source-authority.json')
    binding=read_json(ROOT/'context.json');manifest=Path(binding['reference_manifest'])
    accepted=read_json(manifest)
    details['preservation']={}
    for name,base,hashes in [('owner',Path(authority['source']),authority['hashes']),
                             ('production',Path(binding['reference_board']).parent,accepted['hashes'])]:
        details['preservation'][name]={}
        for filename,expected in hashes.items():
            actual=hashlib.sha256((base/filename).read_bytes()).hexdigest()
            require(actual==expected,'Source authority changed: '+str(base/filename))
            details['preservation'][name][filename]=dict(sha256=actual,unchanged=True)
    details['preservation']['manifest_sha256']=hashlib.sha256(manifest.read_bytes()).hexdigest()
    details['native_operations_in_phase412']=False
    details['tests']='81 offline toolkit regressions passed; no hardware, native post-edit DRC/ERC or field solution'
    write_json(Path(directory)/'focused-evidence.json',details)
    return details


def fallback_with_gap():
    """Joint alternative: retain B routing, with U2/VBUS/gap improvements."""
    g,c,l=load();u=u2_candidate([115,81.4],[113.984,81.4]);v=vbus_candidate();gap=gap_candidate()
    base,court=moved_U2(g,l,u['center'])
    for via in base['vias'].values():
        if via['net'] in {'/USB_MCU_DP','/USB_MCU_DN'}:
            via['drill']=.3;via['copper_widths']={layer:.6 for layer in via['copper_widths']}
    plan=dict(mode='export-only-owner-sketch',failure=None,tracks=[],vias=[])
    for candidate in [u,v,gap]:
        base=candidate_base(base,candidate)
        for key in ['tracks','vias']:plan[key].extend(candidate['proposed_plan'][key])
    plan['vias'].extend([['PGND',*q,.6,.3] for q in [[77.724,92.2],[92.456,89.4],[92.456,92.2]]])
    check=check_plan(base,plan,planning_context(c))
    return dict(valid=check['valid'],joint_check=check,proposed_plan=plan,
                MCU_signal_vias='Resize existing four signal vias in place to0.60/0.30mm; preserve all current B tracks',
                note='U2 primary + VBUS + local gap + retained B with three ground stitches; native post-edit refill still required.')


def ground_options(g,context,target):
    """Bounded placement checks, not a trace router or a search over USB paths."""
    valid=[];rejected=0
    for dx in [-1.2,-.8,0,.8,1.2]:
        for dy in [-1.2,-.8,0,.8,1.2]:
            if dx==dy==0:continue
            q=[round(target[0]+dx,6),round(target[1]+dy,6)]
            hole=shape('proposal','PGND','*',[q,q],.15)
            # Avoid inventing via-in-SMD-pad assembly requirements.
            overlap=False
            for p in g['pads'].values():
                if max(p['drill_size'])>0:continue
                for poly in p['polygons'].get('F.Cu',[]):
                    obstacle=shape(p['uuid'],p['net'],'F.Cu',poly,polygon=True)
                    if nearby(hole,obstacle,0) and separation(hole,obstacle)<0:overlap=True
            if overlap:rejected+=1;continue
            plan=dict(failure=None,tracks=[],vias=[['PGND',*q,.6,.3]])
            check=check_plan(g,plan,planning_context(context))
            if check['valid']:valid.append(dict(position=q,distance_mm=math.dist(q,target)))
            else:rejected+=1
    return dict(target=target,valid=sorted(valid,key=lambda r:(r['distance_mm'],r['position'])),
                rejected=rejected,sample_offsets_mm=[-1.2,-.8,0,.8,1.2],
                note='Bounded geometric placement candidates only; not an exhaustive feasibility proof or native refill validation.')


def return_options(kind):
    g,c,l=load()
    if kind=='short-bridge':
        candidate=mcu_candidate(kind);g=materialize(candidate_base(g,candidate),candidate['proposed_plan'])
    elif kind=='preserve-B':
        for v in g['vias'].values():
            if v['net'] in {'/USB_MCU_DP','/USB_MCU_DN'}:
                v['drill']=.3;v['copper_widths']={layer:.6 for layer in v['copper_widths']}
    else:raise ValueError(kind)
    result=[]
    for v in g['vias'].values():
        if v['net'] not in {'/USB_MCU_DP','/USB_MCU_DN'}:continue
        result.append(dict(net=v['net'],signal_position=v['position'],
                           **ground_options(g,c,v['position'])))
    return result


def render(output,bounds,layer='F.Cu',candidate=None,title='',notes=(),paths=None,
           snapshot=None,annotations=(),show_In1=False,scale=100):
    """Exact exported geometry with labelled hypothetical placement/path overlay."""
    from PIL import Image,ImageDraw,ImageFont
    g,c,l=load();g=snapshot or g;x0,y0,x1,y1=bounds;margin=65;top=85
    image=Image.new('RGB',(round((x1-x0)*scale)+2*margin,round((y1-y0)*scale)+top+75+22*len(notes)),'white')
    d=ImageDraw.Draw(image);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
    def pt(q):return margin+(q[0]-x0)*scale,top+(q[1]-y0)*scale
    colors={'PGND':'#97bd9b','USB_DP':'#cc3b31','USB_DN':'#255fd2',
            '/USB_MCU_DP':'#cc3b31','/USB_MCU_DN':'#255fd2','USB_VBUS':'#d49716','USB3V3':'#8c51a8','MCU3V3':'#744d2e'}
    def within(q):return x0<=q[0]<=x1 and y0<=q[1]<=y1
    if show_In1:
        for z in l['fills'].values():
            if z['net']!='PGND':continue
            for poly in z['layers'].get('In1.Cu',[]):
                d.polygon([pt(p) for p in poly['outline']],fill='#e1efe4')
                for hole in poly['holes']:d.polygon([pt(p) for p in hole],fill='white')
    for x in range(math.ceil(x0),math.floor(x1)+1):
        d.line([pt([x,y0]),pt([x,y1])],fill='#eeeeee');d.text((pt([x,y0])[0]-12,top-22),str(x),fill='black',font=font)
    for y in range(math.ceil(y0),math.floor(y1)+1):
        d.line([pt([x0,y]),pt([x1,y])],fill='#eeeeee');d.text((15,pt([x0,y])[1]-7),str(y),fill='black',font=font)
    for ref,polys in l['courtyards'].items():
        for poly in polys:
            if any(within(p) for p in poly['outline']):d.line([pt(v) for v in poly['outline']+[poly['outline'][0]]],fill='#b8b8b8',width=1)
    for t in g['tracks'].values():
        if t['layer']!=layer:continue
        d.line([pt(t['start']),pt(t['end'])],fill=colors.get(t['net'],'#b4b4b4'),width=max(1,round(t['width']*scale)))
    for pad in g['pads'].values():
        for poly in pad['polygons'].get(layer,[]):d.polygon([pt(p) for p in poly],fill=colors.get(pad['net'],'#c9c9c9'))
        useful=pad['ref'] in {'U2','R48','R49','C28'} or (pad['ref']=='U1' and pad['pin'] in {'26','27'}) or (pad['ref']=='J7' and pad['pin'] in {'A6','A7','B6','B7','A9'})
        if useful and within(pad['position']) and pad['polygons'].get(layer):
            x,y=pt(pad['position']);d.text((x+4,y+4),pad['ref']+'.'+pad['pin'],fill='black',font=font)
    for v in g['vias'].values():
        if not within(v['position']):continue
        x,y=pt(v['position']);r=v['copper_widths'][layer]*scale/2
        d.ellipse([x-r,y-r,x+r,y+r],fill=colors.get(v['net'],'#a0a0a0'))
        r=v['drill']*scale/2;d.ellipse([x-r,y-r,x+r,y+r],fill='white')
    if candidate:
        for poly in candidate['courtyard_outline']:d.line([pt(p) for p in poly+[poly[0]]],fill='#009268',width=3)
        for net,points in candidate['incoming'].items():d.line([pt(p) for p in points],fill=colors[net],width=4)
        for net,points in candidate['outgoing'].items():d.line([pt(p) for p in points],fill=colors[net],width=4)
        for pin,q in candidate['pad_positions'].items():
            x,y=pt(q);d.rectangle([x-8,y-8,x+8,y+8],outline='#004c38',width=2);d.text((x+8,y-20),'NEW U2.'+pin,fill='#00684a',font=font)
        x,y=pt(candidate['ground_via']);d.ellipse([x-30,y-30,x+30,y+30],outline='#00865a',width=3)
        d.line([pt(candidate['pad_positions']['3']),pt(candidate['ground_via'])],fill='#00865a',width=5)
    for color,points,label in paths or []:
        d.line([pt(p) for p in points],fill=color,width=4)
        x,y=pt(points[len(points)//2]);d.text((x+4,y-20),label,fill=color,font=font)
    for text,target,at in annotations:
        xy=pt(at);end=pt(target)
        d.line([xy,end],fill='#202020',width=2)
        box=d.textbbox(xy,text,font=font);d.rectangle([box[0]-3,box[1]-3,box[2]+3,box[3]+3],fill='white',outline='#202020')
        d.text(xy,text,fill='black',font=font)
    bottom=top+round((y1-y0)*scale)+12
    d.rectangle([0,bottom-10,image.width,image.height],fill='white')
    d.rectangle([0,0,image.width,top-25],fill='white')
    d.text((margin,8),title+' | '+layer,font=font,fill='black')
    d.text((margin,30),'mm; RED D+ / BLUE D- / GOLD USB_VBUS / GREY other copper; thin outlines courtyards',font=font,fill='black')
    for i,note in enumerate(notes):d.text((margin,bottom+i*22),note,font=font,fill='black')
    d.text((margin,image.height-30),'EXPORT GEOMETRY / OWNER PLAN ONLY; source CAD unchanged; native post-edit checks still required.',font=font,fill='#00684a')
    image.save(output)


def illustrations(directory):
    directory=Path(directory);g,c,l=load();proposal,after=combined_proposal()
    u=proposal['u2'];alt=u2_candidate([114.7,82.5],[113.684,82.5])
    render(directory/'01-U2-before.png',[108.5,77.2,119.4,93.2],title='CURRENT: J7 -> U2 unprotected conductor 15.028 / 15.248 mm',
           annotations=[('U2 current 110.744,91.440 / 90 deg',[110.744,91.44],[108.8,92.5]),
                        ('A6 D+ / A7 D- contacts',[117.39,81.425],[112,79.5]),
                        ('Retain lower owner USB route',[108.5,90.52],[108.8,88.7])],scale=75)
    render(directory/'02-U2-primary.png',[112.5,77.2,119.4,86.4],snapshot=after,title='PRIORITY 1: U2 115.000,81.400 / 90 deg; A paths 2.100 / 2.162 mm',
           candidate=u,
           annotations=[('NEW U2 / 90 deg',[115,81.4],[113,79.7]),
                        ('PGND 113.984,81.400 / 0.6-0.3',[113.984,81.4],[112.65,84.7]),
                        ('Original DP / DN anchors retained',[116.84,85.464239],[114,86])],
           notes=['U4 courtyard left, J7 courtyard right; nearest U2 courtyard gap 0.640 mm.',
                  'Old U2 at (110.744,91.440) leaves the through-route intact; ground stub may remain.'])
    render(directory/'03-U2-alternative.png',[112.5,77.2,119.4,86.4],candidate=alt,title='ALTERNATIVE: U2 114.700,82.500 / 90 deg; A paths 2.855 / 2.917 mm',
           notes=['Overlay on current copper. Ground via (113.684,82.500), same 0.591 mm return.',
                  'U4 courtyard gap 0.610 mm; J7 gap 0.940 mm. Use instead of primary, never together.'])
    render(directory/'04-MCU-before-B.png',[75.5,88.5,96.2,93.5],layer='B.Cu',title='CURRENT MCU: 15.063 mm B.Cu on each net; no adjacent continuous In2 PGND',scale=75,
           annotations=[('Old 1.0/0.5 signal vias',[77.724,91.4],[76,92.8]),
                        ('In2 contains power/signals; In1 is farther away',[85,91.0],[82,88.7])])
    render(directory/'05-MCU-proposed-F.png',[75.5,88.5,96.2,93.5],snapshot=after,title='OPTIONAL MCU: F.Cu majority; fixed power routes preserved; 0.20 mm tracks',scale=85,
           annotations=[('Staggered signal vias 83.8,90.0 / 85.3,91.8',[83.8,90],[79,88.6]),
                        ('Fixed BOOT_STRAP2 diagonal blocks F',[86,90.96],[84.8,88.6]),
                        ('Fixed MCU3V3 / C30 fence',[90.06,91],[89.4,88.9]),
                        ('PGND stitches: see coordinate table',[85.3,92.6],[79,93.1]),
                        ('Right signals 91,90.6 / 91,91.8',[91,91.8],[90,93.1])],
           notes=['D+ F/B = 15.817 / 6.031 mm; D- F/B = 13.236 / 7.780 mm; planar skew +0.833 mm.',
                  'Four signal + four PGND vias 0.60/0.30 mm. No impedance claim.'])
    render(directory/'06-MCU-proposed-B.png',[82.5,89.3,92,93.1],layer='B.Cu',snapshot=after,title='Remaining B bridge: D+ 6.031 / D- 7.780 mm; 0.20 mm straight gap',
           notes=['Bridge remains a reference compromise. PGND stitches connect to In1; In2 is unchanged.'])
    render(directory/'07-MCU-current-In1-projection.png',[75.5,88.5,96.2,93.5],snapshot=after,show_In1=True,scale=85,
           title='PROPOSED F TRACKS over CURRENT ACTUAL In1 PGND fill (green)',
           notes=['Current old-via antipads shown, not a prediction of the post-edit fill.',
                  '1432 / 1842 center+edge samples covered; missing near old/new transitions. Refill must verify continuity.'])
    render(directory/'08-VBUS-proposal.png',[105.2,77.1,119.2,83.4],snapshot=after,title='PRIORITY 2: USB_VBUS 0.60 mm all-F feed; remove series via',scale=85,
           annotations=[('Remove old via 109.220,80.518',[109.22,80.518],[106.4,82.2]),
                        ('Retain input tail -> U4.1',[106.032,80.518],[105.5,78.4]),
                        ('C28 branch 0.30 mm / 0.897 mm',[113.594,78.4],[110.9,77.2]),
                        ('J7 A9 feed; B power ring retained',[117.39,78.875],[115,82.4])],
           notes=['Same 0.60 mm feed width; no barrel bottleneck; current rating still needs hardware validation.',
                  'C28 stays at its owner position; no change to USB3V3, U4 or connector duplicate power contacts.'])
    gap=gap_candidate();opened=materialize(candidate_base(after,gap),gap['proposed_plan'],prefix='gap')
    render(directory/'09-gap-before.png',[92.2,89.6,98.4,91.9],title='CURRENT R48/R49 fanouts: two 0.10 mm straight gaps',
           annotations=[('MCU side: y90.932 / 90.632',[94,90.782],[92.3,89.65]),
                        ('Connector side: y90.82 / 90.52',[98,90.67],[95.2,91.6])],scale=160)
    render(directory/'10-gap-proposal.png',[92.2,89.6,98.4,91.9],snapshot=opened,title='OPTIONAL local gap opening; width 0.20 / main straight gap 0.20 mm',
           annotations=[('MCU side: y90.982 / 90.582',[94,90.782],[92.3,89.65]),
                        ('Connector D- straight y90.420',[98,90.42],[95.2,91.6])],scale=160,
           notes=['MCU straight gap 0.20 mm; connector long straight 0.20 mm.',
                  'Geometric minimum approximately 0.20 mm on both data partitions. No serpentine; no rule change.'])
