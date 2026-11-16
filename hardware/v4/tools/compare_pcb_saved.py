"""Read-only native KiCad comparison of tracks/vias, placement and pad nets.

Usage: KiCad-python compare_pcb_saved.py BEFORE.kicad_pcb AFTER.kicad_pcb REPORT.json
Uses pcbnew.LoadBoard only; never saves or modifies a board.
"""
import json
import sys
from pathlib import Path
import pcbnew


def snapshot(path):
    b = pcbnew.LoadBoard(str(Path(path).resolve()))
    def xy(v): return [int(v.x), int(v.y)]
    tracks = {}
    for t in b.GetTracks():
        d = {'kind':type(t).__name__, 'start':xy(t.GetStart()),
             'end':xy(t.GetEnd()), 'width':int(t.GetWidth(pcbnew.F_Cu) if isinstance(t,pcbnew.PCB_VIA) else t.GetWidth()),
             'layer':int(t.GetLayer()), 'net':str(t.GetNetname())}
        if isinstance(t, pcbnew.PCB_VIA):
            d.update(drill=int(t.GetDrillValue()),top=int(t.TopLayer()),
                     bottom=int(t.BottomLayer()),via_type=int(t.GetViaType()))
        if isinstance(t, pcbnew.PCB_ARC):
            d['mid'] = xy(t.GetMid())
        tracks[str(t.m_Uuid.AsString())] = d
    footprints, pads = {}, {}
    for f in b.GetFootprints():
        ref = str(f.GetReference())
        footprints[ref] = {'position':xy(f.GetPosition()),
                           'angle':float(f.GetOrientationDegrees()),
                           'layer':int(f.GetLayer())}
        for pad in f.Pads():
            pads[str(pad.m_Uuid.AsString())] = {
                'ref':ref,'number':str(pad.GetNumber()),
                'position':xy(pad.GetPosition()),'size':xy(pad.GetSize()),
                'drill':xy(pad.GetDrillSize()),'shape':int(pad.GetShape()),
                'angle':float(pad.GetOrientationDegrees()),
                'layers':str(pad.GetLayerSet().FmtBin()),'net':str(pad.GetNetname())}
    return {'tracks':tracks,'footprints':footprints,'pads':pads}


def compare(a,b):
    result={}
    for kind in a:
        old,new=a[kind],b[kind]
        changed={k:{f:{'before':old[k].get(f),'after':new[k].get(f)}
                    for f in old[k].keys()|new[k].keys()
                    if old[k].get(f)!=new[k].get(f)}
                 for k in old.keys()&new.keys() if old[k]!=new[k]}
        result[kind]={'removed':sorted(old.keys()-new.keys()),
                      'added':sorted(new.keys()-old.keys()),'changed':changed}
    return result


if __name__=='__main__':
    a,b=snapshot(sys.argv[1]),snapshot(sys.argv[2])
    r={'native_version':pcbnew.Version(),'before':a,'after':b,'difference':compare(a,b)}
    Path(sys.argv[3]).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'native_version':r['native_version'],'counts_before':{k:len(v) for k,v in a.items()},
                      'counts_after':{k:len(v) for k,v in b.items()},
                      'differences':{k:{'removed':len(v['removed']),'added':len(v['added']),
                                        'changed':len(v['changed'])} for k,v in r['difference'].items()}}))
