"""Read-only comparison of captured scratch additions; no CAD/native access."""
import argparse
import math
from collections import Counter
from .safety import read_json,write_json,require


def freeze(value):
    if isinstance(value,dict):return tuple(sorted((k,freeze(v)) for k,v in value.items()))
    if isinstance(value,list):return tuple(freeze(v) for v in value)
    return value


def fields(row):
    return (['kind','net','layer','width','start','end'] if row['kind']=='track' else
            ['kind','net','position','drill','copper_widths'])


def signature(row,ignore_net=False):
    return freeze({k:row[k] for k in fields(row) if not (ignore_net and k=='net')})


def compare(expected,actual):
    e,a=Counter(signature(r) for r in expected),Counter(signature(r) for r in actual)
    geometry_equal=Counter(signature(r,True) for r in expected)==Counter(signature(r,True) for r in actual)
    changes=[]
    for want in expected:
        if e[signature(want)]<=a[signature(want)]:continue
        matches=[r for r in actual if signature(r,True)==signature(want,True)]
        require(len(matches)==1,'Discrepant object lacks a unique exact-geometry match; report remains unresolved')
        got=matches[0]
        changes.append(dict(plan_kind=want['kind'],plan_ordinal_zero_based=want['ordinal'],
            actual_uuid=got['uuid'],expected={k:want[k] for k in fields(want)},
            actual={k:got[k] for k in fields(got)},
            field_differences={k:dict(expected=want[k],actual=got[k]) for k in fields(want) if want[k]!=got[k]},
            native_diagnostics=got['native_diagnostics']))
    duplicates=lambda rows:[dict(geometry=dict(key),count=count) for key,count in
        Counter(signature(r) for r in rows).items() if count>1]
    return dict(expected_counts=dict(Counter(r['kind'] for r in expected)),
        actual_counts=dict(Counter(r['kind'] for r in actual)),exact_equal=e==a,
        exact_geometry_equal_ignoring_net=geometry_equal,
        changed_objects=changes,first_discrepancy_in_plan_order=changes[0] if changes else None,
        missing_geometry_count=sum((Counter(signature(r,True) for r in expected)-
            Counter(signature(r,True) for r in actual)).values()),
        extra_geometry_count=sum((Counter(signature(r,True) for r in actual)-
            Counter(signature(r,True) for r in expected)).values()),
        expected_duplicates=duplicates(expected),actual_duplicates=duplicates(actual))


def point_segment(p,a,b):
    d=[b[i]-a[i] for i in [0,1]];den=sum(v*v for v in d)
    u=max(0,min(1,sum((p[i]-a[i])*d[i] for i in [0,1])/den)) if den else 0
    return math.dist(p,[a[i]+u*d[i] for i in [0,1]])


def overlaps(expected):
    tracks=[r for r in expected if r['kind']=='track']
    result=[]
    for via in (r for r in expected if r['kind']=='via'):
        for track in tracks:
            if via['net']==track['net']:continue
            distance=point_segment(via['position'],track['start'],track['end'])
            gap=distance-via['copper_widths'][track['layer']]/2-track['width']/2
            if gap<0:
                result.append(dict(via_ordinal_zero_based=via['ordinal'],via_net=via['net'],
                    via_position=via['position'],track_ordinal_zero_based=track['ordinal'],
                    track_net=track['net'],layer=track['layer'],track_start=track['start'],
                    track_end=track['end'],track_width_mm=track['width'],
                    centerline_distance_mm=distance,copper_edge_gap_mm=gap))
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True)
    a=p.parse_args();from pathlib import Path
    root=Path(a.root);e=read_json(root/'expected-inventory.json');actual=read_json(root/'actual-inventory.json')
    result=compare(e,actual);result['declared_different_net_via_track_overlaps']=overlaps(e)
    write_json(root/'object-level-diagnostics.json',result)
    print(dict(changed=len(result['changed_objects']),geometry_equal_ignoring_net=result['exact_geometry_equal_ignoring_net'],
        missing=result['missing_geometry_count'],extra=result['extra_geometry_count'],
        planned_overlaps=len(result['declared_different_net_via_track_overlaps'])))


if __name__=='__main__':main()
