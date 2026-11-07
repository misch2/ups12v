"""Focused saved-owner review from native exports only; no native/CAD writes."""
from pathlib import Path
from collections import Counter
import math
import json
from .safety import read_json,write_json,verify_review_context,digest
from .track_geometry import track_length
from .usb_review import analyze,analyze_3d,geometric_path,_pair_spacing
from .review_compare import checks_delta,connectivity_delta
from .legacy_review import reference_samples
from .phase411_analysis import local_fill_comparison
from .plan_validation import check_plan
from .usb_improvement_plan import planning_context,render,materialize


def run(previous,current):
    previous,current=Path(previous),Path(current)
    binding=verify_review_context(current,allow_target_change=True)
    old,g=[read_json(p/'snapshot.json') for p in [previous,current]]
    inspections=[read_json(p/'native-review-inspection.json') for p in [previous,current]]
    layouts=[read_json(p/'post-refill-layout.json') for p in [previous,current]]
    context=read_json(current/'routing-context.json')
    changed={}
    for section in ['tracks','vias','pads','footprints']:
        a,b=old[section],g[section]
        changed[section]=dict(added={u:b[u] for u in b.keys()-a.keys()},
                              removed={u:a[u] for u in a.keys()-b.keys()},
                              modified={u:dict(before=a[u],after=b[u]) for u in a.keys()&b.keys() if a[u]!=b[u]})
    pad_delta=connectivity_delta(*inspections)
    pad_delta['split_refs']=[[(g['pads'][u]['ref'],g['pads'][u]['pin'],g['pads'][u]['net']) for u in group]
                             for group in pad_delta['split_old_islands']]
    d=checks_delta(previous,current)
    h=read_json('hardware/v4/evidence/phase4-11-source-confirmed/nominal-stackup.json')['copper_center_z_mm']
    usb=analyze(g)
    esd={pin:geometric_path(g,net,'J7.'+pin,'U2.'+target,h) for pin,net,target in
         [('A6','USB_DP','1'),('A7','USB_DN','2'),('B6','USB_DP','1'),('B7','USB_DN','2')]}
    via_returns=[]
    for v in g['vias'].values():
        if v['net'] not in {'/USB_MCU_DP','/USB_MCU_DN'}:continue
        nearest=min((w for w in g['vias'].values() if w['net']=='PGND'),key=lambda w:math.dist(v['position'],w['position']))
        via_returns.append(dict(signal=v,nearest_PGND=nearest,center_distance_mm=math.dist(v['position'],nearest['position'])))
    lengths={n:{layer:sum(track_length(t) for t in g['tracks'].values() if t['net']==n and t['layer']==layer)
                for layer in ['F.Cu','B.Cu']} for n in ['/USB_MCU_DP','/USB_MCU_DN']}
    fill={}
    for n in lengths:
        tracks=[t for t in g['tracks'].values() if t['net']==n and t['layer']=='F.Cu']
        fill[n]=reference_samples(g,tracks,layouts[1],context)
        fill[n]['arc_max_chord_deviation_mm']=.0001
    grids={}
    for f in g['footprints'].values():
        if f['ref'] in ['IC1','L1','U3']:
            x,y=f['position'];grids[f['ref']]=local_fill_comparison(*layouts,[x-6,y-6,x+6,y+6])
    audit_equal={key:inspections[0]['audit'][key]==inspections[1]['audit'][key] for key in ['zones','drawings']}
    changed_graphics=[ref for ref in inspections[0]['audit']['footprint_graphics']
                      if inspections[0]['audit']['footprint_graphics'][ref]!=inspections[1]['audit']['footprint_graphics'][ref]]
    def graphic_semantics(inspection,ref):
        return sorted(json.dumps({k:v for k,v in row.items() if k!='uuid'},sort_keys=True)
                      for row in inspection['audit']['footprint_graphics'][ref].values())
    semantic_graphics_changes=[ref for ref in changed_graphics
                              if graphic_semantics(inspections[0],ref)!=graphic_semantics(inspections[1],ref)]
    widths={n:sorted({t['width'] for t in g['tracks'].values() if t['net']==n}) for n in usb['nets']}
    repaired=read_json(current/'minimal-repair-proposal.json')
    base=dict(g,tracks={u:t for u,t in g['tracks'].items() if u not in repaired['removed_track']})
    hypothetical=materialize(base,repaired['plan'],prefix='repair')
    optional=dict(failure=None,tracks=[],vias=[['PGND',113.984,81.4,.6,.3]])
    optional_check=check_plan(g,optional,planning_context(context))
    result=dict(verdict='NEEDS_FIX',source_hashes=binding['source_hashes'],
        previous_source_hashes=read_json(previous/'context.json')['source_hashes'],native_summary=read_json(current/'summary.json'),
        object_delta=changed,pad_delta=pad_delta,checks_delta=d,USB=usb,ESD=esd,
        nominal_3d=analyze_3d(g,h),nominal_heights=h,
        stackup_basis='Prior accepted nominal stackup assumption for barrel model; current thicknesses were not independently re-exported here. No impedance claim.',
        layer_lengths=lengths,via_returns=via_returns,In1_F_projection=fill,
        fill_refill_equal=read_json(current/'layout.json')['fills']==layouts[1]['fills'],
        local_protected_fill_grids=grids,audit_equal=audit_equal,changed_footprint_graphics=changed_graphics,
        semantic_footprint_graphics_changes=semantic_graphics_changes,
        widths=widths,source_schematic_project_rules_equal={ext:binding['source_hashes']['ups12v_v4'+ext]==
          read_json(previous/'context.json')['source_hashes']['ups12v_v4'+ext] for ext in ['.kicad_sch','.kicad_pro','.kicad_dru']},
        optional_U2_ground_via=dict(plan=optional,result=optional_check,applied=False),
        preservation=dict(original_sources_unchanged=True,accepted_manifest_sha256=digest(binding['reference_manifest'])),
        limitations='Native checks apply to isolated refill copy. Manual repair and optional via are export-only geometry screens, not applied CAD or native validated fixes. No impedance/ESD/EMI/hardware qualification.')
    write_json(current/'focused-review.json',result)
    for name,snapshot,title in [('missing-vias-B.png',g,'CURRENT: two missing non-USB vias; new USB D- occupies their clearance'),
                                 ('proposed-minimal-repair-B.png',hypothetical,'OWNER REPAIR PROPOSAL ONLY: short D- detour + restore original vias')]:
        render(current/name,[82,88.4,89.2,91.4],layer='B.Cu',snapshot=snapshot,layout_override=layouts[1],title=title,
               annotations=[('BOOT via (84.540,89.500)',[84.54,89.5],[82.2,88.5]),
                            ('EN via (86.740,89.500)',[86.74,89.5],[86,88.5]),
                            ('D- detour y90.200 after approval',[85,90.2],[83.1,91.1])],scale=145,
               notes=['Restore 0.50/0.30 mm through-vias on their ORIGINAL nets; do not simply place them on current D-.',
                      'Copper/drill preflight passes only with the shown local detour. Native DRC required after owner edits.'])
    verify_review_context(current,allow_target_change=True)
    return result


def confirm_repair(accepted,previous,current):
    """Confirm a subsequent owner correction without replaying a repair plan."""
    from .review_compare import merge_counts
    from .safety import require
    accepted,previous,current=map(Path,[accepted,previous,current])
    binding=verify_review_context(current,allow_target_change=True)
    a,p,g=[read_json(d/'snapshot.json') for d in [accepted,previous,current]]
    ai,pi,gi=[read_json(d/'native-review-inspection.json') for d in [accepted,previous,current]]
    summary=read_json(current/'summary.json')
    original_connectivity=connectivity_delta(ai,gi)
    correction_connectivity=connectivity_delta(pi,gi)
    merges=merge_counts(pi,gi,g)
    delta={}
    for section in ['tracks','vias','pads','footprints']:
        before,after=p[section],g[section]
        delta[section]=dict(added={u:after[u] for u in after.keys()-before.keys()},
            removed={u:before[u] for u in before.keys()-after.keys()},
            modified={u:dict(before=before[u],after=after[u]) for u in before.keys()&after.keys()
                      if before[u]!=after[u]})
    assigned={u:i for i,group in enumerate(gi['pad_partitions']) for u in group}
    def pad_island(refpin):
        ref,pin=refpin.split('.',1)
        islands={assigned[u] for u,v in g['pads'].items() if v['ref']==ref and str(v['pin'])==pin}
        require(len(islands)==1,'Pad missing or duplicate pad numbers split: '+refpin)
        return next(iter(islands))
    pairs=[('J7.A6','J7.B6'),('J7.A6','U2.1'),('U2.1','R48.2'),
           ('J7.A7','J7.B7'),('J7.A7','U2.2'),('U2.2','R49.2'),
           ('R48.1','U1.27'),('R49.1','U1.26'),('U2.3','U4.2')]
    closures=[dict(pads=[x,y],native_connected=pad_island(x)==pad_island(y)) for x,y in pairs]
    vbus=['J7.A4','J7.A9','J7.B4','J7.B9','U4.1','C28.1','C27.1']
    c=read_json(current/'routing-context.json')
    layouts=[read_json(d/'post-refill-layout.json') for d in [previous,current]]
    grids={}
    for f in g['footprints'].values():
        if f['ref'] in ['IC1','L1','U3']:
            x,y=f['position'];grids[f['ref']]=local_fill_comparison(*layouts,[x-6,y-6,x+6,y+6])
    projection={n:reference_samples(g,[t for t in g['tracks'].values()
                 if t['net']==n and t['layer']=='F.Cu'],layouts[1],c)
                for n in ['/USB_MCU_DP','/USB_MCU_DN']}
    lengths={n:{layer:sum(track_length(t) for t in g['tracks'].values()
                         if t['net']==n and t['layer']==layer) for layer in ['F.Cu','B.Cu']}
             for n in projection}
    warnings=checks_delta(accepted,current)
    other_tracks_equal=all(u in g['tracks'] and g['tracks'][u]==t for u,t in p['tracks'].items()
                          if t['net'] not in {'/USB_MCU_DP','/USB_MCU_DN'})
    unchanged_files={ext:binding['source_hashes']['ups12v_v4'+ext]==
                     read_json(accepted/'context.json')['source_hashes']['ups12v_v4'+ext]
                     for ext in ['.kicad_sch','.kicad_pro','.kicad_dru']}
    vbus_connected=len({pad_island(x) for x in vbus})==1
    returns=[]
    for via in g['vias'].values():
        if via['net'] not in {'/USB_MCU_DP','/USB_MCU_DN'}:continue
        nearest=min((v for v in g['vias'].values() if v['net']=='PGND'),
                    key=lambda v:math.dist(v['position'],via['position']))
        returns.append(dict(signal=via,nearest_PGND=nearest,
                            center_distance_mm=math.dist(via['position'],nearest['position'])))
    required=(summary['drc']['errors']==summary['drc']['parity']==summary['erc']['errors']==0
              and original_connectivity['all_previous_pad_connections_preserved']
              and correction_connectivity['all_previous_pad_connections_preserved']
              and all(r['native_connected'] for r in closures)
              and merges=={'MCU_EN':1,'MCU_BOOT_STRAP2':1}
              and vbus_connected and all(unchanged_files.values()) and other_tracks_equal
              and all(p[s]==g[s] for s in ['pads','footprints']) and pi['audit']==gi['audit']
              and warnings['drc']['warning_identity_multiset_equal']
              and warnings['erc']['warning_identity_multiset_equal'])
    report=dict(verdict='PASS_CORRECTION_USB_LAYOUT_REMAINS_CONDITIONAL' if required else 'NEEDS_FIX',
        native_summary=summary,source_hashes=binding['source_hashes'],
        native_connectivity_vs_accepted=original_connectivity,native_connectivity_vs_previous=correction_connectivity,
        newly_restored_native_connections=merges,USB_ESD_nine_closures=closures,
        VBUS_native_all_connected=vbus_connected,
        correction_delta=delta,USB=analyze(g),layer_lengths=lengths,In1_F_projection=projection,
        pair_spacing={name+':'+layer:_pair_spacing(g,*nets,layer)
                      for name,nets in [('connector',('USB_DP','USB_DN')),
                                        ('MCU',('/USB_MCU_DP','/USB_MCU_DN'))]
                      for layer in ['F.Cu','B.Cu']},
        USB_signal_via_returns=returns,
        local_protected_fill_grids=grids,checks_vs_accepted=warnings,
        unchanged_source_schematic_project_rules=unchanged_files,
        all_other_tracks_vs_previous_equal=other_tracks_equal,
        non_routed_geometry_vs_previous_equal={s:p[s]==g[s] for s in ['pads','footprints']},
        native_audit_vs_previous_equal=pi['audit']==gi['audit'],
        source_fill_equals_fresh_refill=read_json(current/'layout.json')['fills']==layouts[1]['fills'],
        original_sources_unchanged=True,accepted_manifest_sha256=digest(binding['reference_manifest']),
        limits='Independent structural correction pass only; existing MCU return/reference and U2-ground compromises remain. Not impedance, ESD, hardware qualification, fabrication release or migration approval.')
    write_json(current/'correction-confirmation.json',report)
    verify_review_context(current,allow_target_change=True)
    return report
