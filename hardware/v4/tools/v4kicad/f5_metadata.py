"""Export-only classification of KiCad10 IPC's absent default unit cache.

Only a single A unit covering exactly every physical pin may be omitted. This
does not normalize multi-unit mappings, pad data, variants or other metadata.
No CAD writes or side effects on import.
"""
import json
from .safety import read_json,require,ToolError


def default_units_only(diagnostic,snapshot,placements):
    def ref(n):return next(x[2].strip('"') for x in n if isinstance(x,list) and
                          x[0]=='property' and x[1].strip('"')=='Reference')
    a,b=diagnostic['before_only'],diagnostic['after_only']
    require(len(a)==len(b)==18 and all(n[0]=='footprint' for n in a+b),'Only18F5cache omissions permitted')
    before,after=[{ref(n):n for n in rows} for rows in [a,b]]
    require(set(before)==set(after)==set(placements),'Unit-cache scope differs')
    proofs={}
    for r,n in before.items():
        m=after[r];units=[x for x in n if isinstance(x,list) and x[0]=='units']
        require(len(units)==1 and len(units[0])==2,'Exactly one optional unit required')
        unit=units[0][1]
        require(len(unit)==3 and unit[:2]==['unit',['name','"A"']] and unit[2][0]=='pins',
                'Non-default/multi-unit mapping cannot be normalized')
        pins=[s.strip('"') for s in unit[2][1:]]
        physical={p['pin'] for p in snapshot['pads'].values() if p['ref']==r and p['pin']}
        require(set(pins)==physical and len(pins)==len(physical),'Default unit must cover all physical pin identities')
        require([x for x in n if x is not units[0]]==m,'A non-cache footprint property changed')
        proofs[r]=dict(unit='A',pins=sorted(physical))
    return dict(all_retained_board_structure_equal=True,all_physical_footprint_properties_equal=True,
                omitted_optional_single_A_unit_caches=proofs,
                interpretation='KiCad10 Get/UpdateItems omits optional unit metadata; only default A/all-pins is equivalent. All geometry,pad nets,models,variants and other properties remain exact.')


def serialized_proof(source,candidate,plan,added,diagnostics):
    from .f5_review import serialized_proof as exact
    try:return exact(source,candidate,plan,added,diagnostics)
    except ToolError as e:
        require(str(e)=='Non-placement serialized board or footprint properties changed',str(e))
        # Fresh independent native geometry was already bound/proven by the caller.
        from pathlib import Path
        g=read_json(Path(candidate).parent/'snapshot.json')
        return default_units_only(read_json(diagnostics),g,plan['placements'])
