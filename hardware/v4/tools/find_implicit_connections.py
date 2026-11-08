"""Find label-connected physical islands from Konnect JSON and KiCad exports.

Usage: python -B hardware/v4/tools/find_implicit_connections.py EVIDENCE_DIR
Inputs: wires.json (coordinate arrays), pins.json, components.json, labels.json,
current.net and ups12v_v4.svg. Never reads or writes serialized CAD sources.
"""
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from verify_equivalence import snapshot


def run(folder):
    p = Path(folder)
    read = lambda name: json.loads((p / name).read_text(encoding='utf-8'))
    wires, pins, comps = read('wires.json'), read('pins.json'), read('components.json')
    labels = read('labels.json')['labels']
    parent = {}
    def point(x, y):
        k = (round(x, 4), round(y, 4))
        parent.setdefault(k, k)
        return k
    def root(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k
    def join(a, b):
        parent[root(a)] = root(b)
    def on(q, w):
        x, y = q; a, b, c, d = w
        return (min(a,c)-1e-4 <= x <= max(a,c)+1e-4 and
                min(b,d)-1e-4 <= y <= max(b,d)+1e-4 and
                abs((x-a)*(d-b)-(y-b)*(c-a)) < 1e-4)
    for a,b,c,d in wires:
        join(point(a,b), point(c,d))
    junctions = []
    def walk(node, inherited=''):
        style = inherited + ' ' + node.get('style','')
        if node.tag.endswith('circle') and node.get('r') == '0.4572' and 'fill:#009600' in style:
            junctions.append(point(float(node.get('cx')),float(node.get('cy'))))
        for child in node: walk(child,style)
    walk(ET.parse(p/'ups12v_v4.svg').getroot())
    for q in junctions:
        for w in wires:
            if on(q,w): join(q,point(w[0],w[1]))
    # Labels may attach inside a segment. They do not bridge wire crossings.
    for lab in labels:
        q = point(lab['x'],lab['y'])
        hits = [w for w in wires if on(q,w)]
        if hits:
            join(q,point(hits[0][0],hits[0][1]))
    for pin in pins: point(pin['x'],pin['y'])
    logical = snapshot(p/'current.net')['pin_nets']
    groups = defaultdict(lambda: defaultdict(list))
    for pin in pins:
        identity = pin['ref']+'.'+pin['pin']
        if identity in logical:
            groups[logical[identity]][root(point(pin['x'],pin['y']))].append(identity)
    # A physically continuous island cannot carry two native net names.
    physical_names = defaultdict(set)
    for net, islands in groups.items():
        for k in islands: physical_names[k].add(net)
    conflicts = {str(k):sorted(v) for k,v in physical_names.items() if len(v)>1}
    if conflicts: raise ValueError('Geometry/native-netlist conflict: '+str(conflicts))
    annotations = defaultdict(list)
    for lab in labels:
        annotations[root(point(lab['x'],lab['y']))].append(lab)
    for c in comps:
        if c['lib'].startswith('power:') and c['value'] != 'PWR_FLAG':
            for pin in pins:
                if pin['ref']==c['ref']:
                    annotations[root(point(pin['x'],pin['y']))].append(
                        {'net':c['value'],'type':'power_symbol','x':pin['x'],'y':pin['y']})
    result=[]
    for net,islands in sorted(groups.items()):
        if len(islands)<2 or net.startswith('unconnected-'): continue
        parts=[]
        for k,members in sorted(islands.items(),key=lambda kv:sorted(kv[1])):
            parts.append({'pins':sorted(members),'labels':annotations[k]})
        result.append({'net':net,'islands':parts,'minimum_wires_to_join_all':len(parts)-1})
    # Every disconnected group must have an explicit label or power name.
    unexplained=[(n['net'],i['pins']) for n in result for i in n['islands'] if not i['labels']]
    report={'junctions':len(junctions),'nets':len(groups),'implicit_nets':result,
            'unexplained_islands':unexplained,'physical_net_conflicts':conflicts}
    (p/'implicit-connections.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'junctions':len(junctions),'implicit_nets':len(result),
                      'unexplained':unexplained,'names':[n['net'] for n in result]}))
    return report


if __name__=='__main__': run(sys.argv[1])
