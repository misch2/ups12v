"""Native PCB field parity for only the four approved connectors."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
import pcbnew
from verify_nanofit import parse,many,ref
E=Path(__file__).resolve().parent
B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
S=B.with_suffix('.kicad_sch')
before=B.read_bytes()
b=pcbnew.LoadBoard(str(B))
symbols={ref(s):s for s in many(parse(S.read_text()),'symbol')}
changes=[]
allowed={}
for f in b.GetFootprints():
    r=f.GetReference()
    if r not in ('J1','J2','J3','J8'):continue
    allowed[r]=set()
    for p in many(symbols[r],'property'):
        key,value=p[1:3]
        if key in ('Reference','Footprint'):continue
        old=f.GetFieldText(key) if f.HasField(key) else None
        if old==value:continue
        allowed[r].add(key)
        existed=f.HasField(key)
        f.SetField(key,value)
        if not existed:
            f.GetField(key).SetVisible(False)
            f.GetField(key).SetPosition(f.GetPosition())
            f.GetField(key).SetTextThickness(150000)
        changes.append({'ref':r,'field':key,'before':old,'after':value})
C=E/'nanofit-native-fields-candidate.kicad_pcb'
assert pcbnew.SaveBoard(str(C),b)
def strip(v):
    if not isinstance(v,list):return v
    if v and v[0]=='footprint':
        r=ref(v)
        if r in allowed:return [strip(x) for x in v if not(isinstance(x,list) and x and x[0]=='property' and x[1] in allowed[r])]
    return [strip(x) for x in v]
assert strip(parse(before.decode()))==strip(parse(C.read_text())),'Unexpected non-field change'
reload=pcbnew.LoadBoard(str(C))
for f in reload.GetFootprints():
    if f.GetReference() not in allowed:continue
    sp={p[1]:p[2] for p in many(symbols[f.GetReference()],'property')}
    for key in allowed[f.GetReference()]:assert f.GetFieldText(key)==sp[key]
assert B.read_bytes()==before
assert pcbnew.SaveBoard(str(B),reload)
assert strip(parse(B.read_text()))==strip(parse(C.read_text()))
(E/'nanofit-native-fields.json').write_text(json.dumps({'changes':changes,'all_non_selected_field_attributes_preserved':True,'native_save_reload':True},indent=2)+'\n')
print('PASS: native connector field synchronization; all other attributes preserved; '+str(len(changes))+' field updates')
