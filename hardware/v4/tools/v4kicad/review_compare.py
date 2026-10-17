"""Read-only comparisons of owner-review exports and uncovered CAD properties.

Native exports are primary. Serialization is inspected only for properties
absent from those exports; this module never writes a CAD file or imports KiCad.
"""
from collections import Counter, defaultdict
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

from .safety import require, read_json, write_json, digest


def tree(path):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',
                        Path(path).read_text(encoding='utf-8'))
    stack, root = [], None
    for token in tokens:
        if token == '(':
            node = []
            if stack:
                stack[-1].append(node)
            stack.append(node)
        elif token == ')':
            require(bool(stack), 'Malformed read-only CAD inspection input')
            root = stack.pop()
        else:
            require(bool(stack), 'Unexpected CAD token outside root')
            stack[-1].append(token)
    require(not stack and root, 'Incomplete read-only CAD inspection input')
    return root


def stackup_centers(path):
    """Nominal saved copper-center heights, not a fab/impedance qualification."""
    root=tree(path)
    setup=next(n for n in root[1:] if isinstance(n,list) and n[0]=='setup')
    stackup=next(n for n in setup[1:] if isinstance(n,list) and n[0]=='stackup')
    active=False
    z=0.0
    centers={}
    rows=[]
    for layer in stackup[1:]:
        if not isinstance(layer,list) or layer[0]!='layer':
            continue
        name=layer[1].strip('"')
        if name=='F.Cu':
            active=True
        if not active:
            continue
        thickness=next((float(n[1]) for n in layer[2:] if n[0]=='thickness'),0.0)
        rows.append(dict(name=name,thickness_mm=thickness))
        if name.endswith('.Cu'):
            centers[name]=z+thickness/2
        z+=thickness
        if name=='B.Cu':
            break
    require(set(centers)=={'F.Cu','In1.Cu','In2.Cu','B.Cu'},'Incomplete four-layer nominal stackup')
    return dict(copper_center_z_mm=centers, copper_and_dielectric_thickness_mm=z, layers=rows,
                interpretation='Saved nominal stackup only; plating, assembly pin geometry and propagation are not measured.')


def child_identity(node):
    # Field UUIDs can be refreshed by an editor/library update without changing
    # the field. Its semantic name is the stable comparison identity.
    if node[0] == 'property' and len(node) > 1:
        return node[1]
    for child in node[1:]:
        if isinstance(child, list) and child and child[0] == 'uuid':
            return child[1]
    if node[0] in ['property', 'pad', 'pin', 'net', 'symbol', 'layer']:
        if len(node) > 1 and isinstance(node[1], str):
            return node[1]
    return None


def flattened(node, path=(), omit_fills=False):
    """Canonical sibling order, retaining indexed geometry and every leaf."""
    result = {path + ('@',): [x for x in node[1:] if not isinstance(x, list)]}
    counts = defaultdict(int)
    for child in node[1:]:
        if not isinstance(child, list) or not child:
            continue
        if omit_fills and child[0] == 'filled_polygon':
            continue
        identity = child_identity(child)
        key = (child[0], identity)
        index = counts[key]
        counts[key] += 1
        segment = f'{child[0]}:{identity if identity is not None else ""}:{index}'
        result.update(flattened(child, path + (segment,), omit_fills))
    return result


def property_delta(before, after, omit_fills=False):
    a, b = flattened(tree(before), omit_fills=omit_fills), flattened(tree(after), omit_fills=omit_fills)
    rows = [dict(path=list(k), before=a.get(k), after=b.get(k),
                 before_present=k in a, after_present=k in b)
            for k in sorted(a.keys() | b.keys()) if a.get(k) != b.get(k)
            or (k in a) != (k in b)]
    return dict(changed_leaf_count=len(rows),
                top_level_counts=dict(Counter(r['path'][0].split(':')[0] for r in rows)),
                changes=rows)


def netlist(path):
    root = ET.parse(path).getroot()
    components = {}
    for component in root.findall('./components/comp'):
        # XML element child order is export order, not an electrical property.
        def canonical(element):
            return [element.tag, sorted(element.attrib.items()),
                    (element.text or '').strip(),
                    sorted([canonical(c) for c in element], key=repr)]
        components[component.attrib['ref']] = canonical(component)
    nets = {}
    for net in root.findall('./nets/net'):
        nodes = sorted((n.attrib['ref'], n.attrib['pin']) for n in net.findall('node'))
        nets[net.attrib['name']] = nodes
    return dict(components=components, nets=nets)


def electrical_delta(before, after):
    a, b = netlist(before), netlist(after)
    names = a['components'].keys() | b['components'].keys()
    changed = {ref: dict(before=a['components'].get(ref), after=b['components'].get(ref))
               for ref in sorted(names) if a['components'].get(ref) != b['components'].get(ref)}
    reverse_a = {tuple(nodes): name for name, nodes in a['nets'].items()}
    reverse_b = {tuple(nodes): name for name, nodes in b['nets'].items()}
    renamed = [dict(before=reverse_a[p], after=reverse_b[p], pins=list(p))
               for p in reverse_a.keys() & reverse_b.keys() if reverse_a[p] != reverse_b[p]]
    return dict(component_count_before=len(a['components']), component_count_after=len(b['components']),
                changed_components=changed, net_count_before=len(a['nets']), net_count_after=len(b['nets']),
                partitions_equal=set(reverse_a) == set(reverse_b), renamed_nets=renamed,
                deleted_partitions=[dict(name=reverse_a[p], pins=list(p)) for p in reverse_a.keys()-reverse_b.keys()],
                added_partitions=[dict(name=reverse_b[p], pins=list(p)) for p in reverse_b.keys()-reverse_a.keys()])


def warning_rows(report, kind):
    rows = report['violations'] if kind == 'drc' else [v for s in report['sheets'] for v in s['violations']]
    # Retain item UUIDs and coordinates, ignoring export timestamps/paths only.
    return Counter(json.dumps(v, sort_keys=True) for v in rows if v['severity'] == 'warning')


def warning_identity_rows(report, kind):
    rows = report['violations'] if kind == 'drc' else [v for s in report['sheets'] for v in s['violations']]
    return Counter((v['type'],v['description'],tuple(sorted(i['uuid'] for i in v.get('items',[]))))
                   for v in rows if v['severity']=='warning')


def open_pairs(report):
    result = {}
    for item in report['unconnected_items']:
        ids = tuple(sorted(i['uuid'] for i in item['items']))
        result[ids] = item
    return result


def checks_delta(before, after):
    result = {}
    for kind in ['drc', 'erc']:
        a, b = read_json(Path(before)/(kind+'.json')), read_json(Path(after)/(kind+'.json'))
        wa, wb = warning_rows(a, kind), warning_rows(b, kind)
        result[kind] = dict(warnings_equal=wa == wb,
                           warning_identity_multiset_equal=warning_identity_rows(a,kind)==warning_identity_rows(b,kind),
                           removed_warnings=[json.loads(x) for x in (wa-wb).elements()],
                           added_warnings=[json.loads(x) for x in (wb-wa).elements()])
        if kind == 'drc':
            pa, pb = open_pairs(a), open_pairs(b)
            result[kind].update(before_open_count=len(pa), after_open_count=len(pb),
                closed_pairs=[pa[k] for k in pa.keys()-pb.keys()],
                added_pairs=[pb[k] for k in pb.keys()-pa.keys()],
                ignored_checks_equal=a['ignored_checks']==b['ignored_checks'])
    return result


def connectivity_delta(before, after):
    a, b = before['pad_partitions'], after['pad_partitions']
    assigned = {pad: i for i, group in enumerate(b) for pad in group}
    old_pads = {pad for group in a for pad in group}
    require(old_pads == set(assigned), 'Native review pad coverage differs')
    split = [group for group in a if len({assigned[p] for p in group}) > 1]
    return dict(before_pad_islands=len(a), after_pad_islands=len(b),
                before_pad_count=sum(map(len,a)), after_pad_count=sum(map(len,b)),
                split_old_islands=split, all_previous_pad_connections_preserved=not split)


def merge_counts(before, after, snapshot):
    old = {p:i for i,g in enumerate(before['pad_partitions']) for p in g}
    result = Counter()
    for group in after['pad_partitions']:
        count = len({old[p] for p in group})-1
        if count:
            nets = {snapshot['pads'][p]['net'] for p in group}
            require(len(nets)==1, 'Native connectivity merged different net assignments')
            result[next(iter(nets))] += count
    return dict(result)


def run(before, after, output):
    before, after, output = Path(before), Path(after), Path(output)
    require(not output.exists(), 'Review comparison output must be fresh')
    output.mkdir(parents=True)
    for extension, name in [('.kicad_pcb','board-properties'),('.kicad_sch','schematic-properties')]:
        write_json(output/(name+'.json'), property_delta(before/('ups12v_v4'+extension),
            after/('ups12v_v4'+extension), omit_fills=extension=='.kicad_pcb'))
    write_json(output/'electrical-topology.json', electrical_delta(before/'netlist.xml', after/'netlist.xml'))
    write_json(output/'checks-delta.json', checks_delta(before, after))
    write_json(output/'pad-connectivity.json', connectivity_delta(
        read_json(before/'native-review-inspection.json'),read_json(after/'native-review-inspection.json')))
    write_json(output/'identity.json', dict(before=str(before.resolve()), after=str(after.resolve()),
        project_equal=digest(before/'ups12v_v4.kicad_pro')==digest(after/'ups12v_v4.kicad_pro'),
        rules_equal=digest(before/'ups12v_v4.kicad_dru')==digest(after/'ups12v_v4.kicad_dru')))
    return output
