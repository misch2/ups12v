"""Export-only local supply evidence; no CAD imports, writes or native processes."""
import argparse
import math
from collections import Counter
from pathlib import Path
from .geometry import preservation
from .safety import read_json, write_json, require
from .u3_review import plane_path


def review(evidence, output):
    e = Path(evidence)
    before = read_json(e/'phase4-8b-entry-native/snapshot.json')
    final = read_json(e/'phase4-8b-b3-native/snapshot.json')
    plans = [read_json(e/p) for p in ['phase4-8b-b1-plan.json',
              'phase4-8b-b2-plan-v3.json','phase4-8b-b3-plan.json']]
    result = dict(preservation=preservation(before, final), assumptions=dict(
        outer_copper_um=35, resistivity_ohm_m=1.724e-8, via_barrel_length_mm=1.6,
        via_plating_um=20, normal_output_screen_A=1, USB_service_screen_A=.3,
        hardware_measurements=False, manufacturing_stackup_confirmed=False))
    added = [t for u,t in final['tracks'].items() if u not in before['tracks']]
    require(Counter((t['net'],t['layer'],t['width'],*t['start'],*t['end']) for t in added) ==
            Counter(tuple(t) for p in plans for t in p['tracks']), 'Cumulative track mismatch')
    vias = [v for u,v in final['vias'].items() if u not in before['vias']]
    require(Counter((v['net'],*v['position'],v['copper_widths']['F.Cu'],v['drill']) for v in vias) ==
            Counter(tuple(v) for p in plans for v in p['vias']), 'Cumulative via mismatch')
    old = read_json(e/'phase4-8a-production-native/layout.json')
    new = read_json(e/'phase4-8b-final-u3-return/layout.json')
    require(old['plane_samples'] == new['plane_samples'], 'U3 reference fill changed')
    require(old['via_plane_samples'] == new['via_plane_samples'], 'U3 via reference changed')
    result['accepted_U3_native_PGND_samples_and_via_probes_exactly_preserved'] = True
    result['cumulative_exact_additions'] = dict(tracks=len(added),vias=len(vias))
    result['added_trace_inventory'] = [dict(net=n,layer=l,width_mm=w,
        length_mm=sum(math.dist(t['start'],t['end']) for t in added
                      if (t['net'],t['layer'],t['width'])==(n,l,w)))
        for n,l,w in sorted({(t['net'],t['layer'],t['width']) for t in added})]
    layout = read_json(e/'phase4-8b-b3-native/layout.json')
    usb_layout = read_json(e/'phase4-8b-b2-native/layout.json')
    samples = layout['via_plane_samples'] + usb_layout['via_plane_samples']
    result['new_PGND_plane_probes'] = []
    for v in vias:
        if v['net'] != 'PGND': continue
        hits = [p for p in samples if p['uuid']==v['uuid']]
        require(hits and all(p['center'] and all(p['ring']) for p in hits), 'PGND via lacks native filled-plane contact')
        result['new_PGND_plane_probes'].append(hits[0])
    result['sampled_return_paths'] = {}
    for name, lay, a, b in [
        ('C70_to_U5',layout,[63.05,85.85],[64.95,81]),
        ('C71_to_U5',layout,[69.55,82.75],[64.95,81]),
        ('C36_to_U5',layout,[67.8,78.5],[64.95,81]),
        ('R24_to_U5',layout,[61.81,81.4],[64.95,81]),
        ('C27_to_U4',usb_layout,[101.2,80.7],[105.55,83]),
        ('C35_to_U4',usb_layout,[107.8,88],[105.55,83]),
        ('C40_to_U4',usb_layout,[110.78,88.65],[105.55,83]),
        ('U4_tab_to_ground_lead',usb_layout,[111.2,82],[105.55,83]),
        ('USB_ground_to_U4',usb_layout,[117.69,78.025],[105.55,83]),
    ]:
        result['sampled_return_paths'][name] = plane_path(final,lay,a,b)
    result['declared_connections'] = [m for p in plans for m in p['metrics']]
    result['new_power_route_resistance_screens_mohm'] = {
        'SYS_feed_0p8mm': .01724*plans[0]['metrics'][0]['length_mm']/(.8*35)*1000,
        'MAIN_C45_to_U5_VIN1': .01724/35*(plans[0]['metrics'][1]['length_mm']/.6+
                                   plans[0]['metrics'][2]['length_mm']/.28)*1000,
        'USB_U4_to_U5_VIN2': .01724/35*(plans[1]['metrics'][6]['length_mm']/.8+
                                  plans[1]['metrics'][9]['length_mm']/.6+
                                  plans[2]['metrics'][0]['length_mm']/.28)*1000,
        'MCU_U5_VOUT7_to_C36': .01724/35*plans[2]['metrics'][2]['length_mm']/.28*1000,
        'single_0p3mm_via': .01724*.0016/(math.pi*.3*.02)*1000,
    }
    result['remaining_by_net'] = {n:len(v) for n,v in read_json(e/'phase4-8b-b3-ipc/remaining-by-net.json').items()}
    write_json(output,result)
    print(dict(cumulative=result['cumulative_exact_additions'],new_PGND_vias=len(result['new_PGND_plane_probes']),
               sampled_return_paths=len(result['sampled_return_paths']),U3_plane_preserved=True))


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();review(a.evidence,a.output)
