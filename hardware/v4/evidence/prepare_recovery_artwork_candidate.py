"""Native artwork-only candidate on an offline backup. NEVER writes live CAD."""
from pathlib import Path
import sys, json, hashlib, shutil
sys.dont_write_bytecode=True
import pcbnew
from verify_nanofit import parse, many, one, ref
E=Path(__file__).resolve().parent
combined='--include-approved-c9' in sys.argv
BASE=E/('revised-c9-candidate.kicad_pcb' if combined else 'c9-apply-entry.kicad_pcb')
OUT=E/('recovery-approved-combined-candidate.kicad_pcb' if combined else 'recovery-artwork-candidate.kicad_pcb')
LIVE=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
before=hashlib.sha256(LIVE.read_bytes()).hexdigest()
assert before==hashlib.sha256((E/'c9-apply-entry.kicad_pcb').read_bytes()).hexdigest()
b=pcbnew.LoadBoard(str(BASE))
fps={f.GetReference():f for f in b.GetFootprints()}
targets={'J1':'8183c390-abf8-42e7-a92b-913bb21ffc84','J2':'a712d60f-4836-4ebe-8833-3e8485043999',
         'J3':'59138b52-821f-4950-8797-8cd80bb31ada','J8':'4c872a8e-1765-433a-bbab-1069741676b7'}
changes=[]
def point(x,y):return pcbnew.VECTOR2I(round(x*1e6),round(y*1e6))
for name,uid in targets.items():
    f=fps[name];g=next(g for g in f.GraphicalItems() if g.m_Uuid.AsString()==uid)
    assert g.GetLayer()==pcbnew.F_SilkS and g.GetShape()==pcbnew.SHAPE_T_RECT
    x0,x1=sorted([pcbnew.ToMM(g.GetStart().x),pcbnew.ToMM(g.GetEnd().x)])
    rear=max(pcbnew.ToMM(g.GetStart().y),pcbnew.ToMM(g.GetEnd().y))
    width=g.GetWidth();f.Remove(g)
    lines=[((x0,30.35),(x0,rear)),((x0,rear),(x1,rear)),((x1,rear),(x1,30.35))]
    for a,z in lines:
        s=pcbnew.PCB_SHAPE(f);s.SetShape(pcbnew.SHAPE_T_SEGMENT);s.SetLayer(pcbnew.F_SilkS)
        s.SetWidth(width);s.SetStart(point(*a));s.SetEnd(point(*z));f.Add(s)
    changes.append({'ref':name,'replace_rectangle':uid,'global_segments_mm':lines})
j7=fps['J7']
for uid in ['0c5ab6dd-1105-456a-b88b-a0808a684ee9','a095fbc3-b1b2-45b2-9221-05200e5c9559']:
    g=next(g for g in j7.GraphicalItems() if g.m_Uuid.AsString()==uid)
    assert g.GetLayer()==pcbnew.F_SilkS and abs(pcbnew.ToMM(g.GetEnd().x)-126.12)<1e-6
    g.SetEnd(point(125.65,pcbnew.ToMM(g.GetEnd().y)))
    changes.append({'ref':'J7','trim_segment':uid,'end_x_mm':125.65})
g=next(g for g in j7.GraphicalItems() if g.m_Uuid.AsString()=='a62337fc-494b-4888-af36-6aa3fd392d33')
j7.Remove(g);changes.append({'ref':'J7','remove_offboard_front':g.m_Uuid.AsString()})
assert OUT.resolve()!=LIVE.resolve()
assert pcbnew.SaveBoard(str(OUT),b)
for suffix in ['.kicad_pro','.kicad_dru']:
    shutil.copy2(LIVE.with_suffix(suffix),OUT.with_suffix(suffix))
pcbnew.LoadBoard(str(OUT)) # independent native reload

# Read-only serialized comparison covers all attributes that a narrower native
# projection could miss. Only target footprint F.SilkS graphic objects excluded.
def normalized(v):
    if not isinstance(v,list):return v
    return sorted([normalized(x) for x in v],key=lambda x:json.dumps(x,sort_keys=True))
def without_target_silk(tree):
    for f in many(tree,'footprint'):
        if ref(f) not in set(targets)|{'J7'}:continue
        f[:]=[x for x in f if not (isinstance(x,list) and x and x[0] in
             ['fp_line','fp_rect','fp_arc','fp_circle','fp_poly','fp_curve'] and one(x,'layer')==['layer','F.SilkS'])]
    return tree
a=parse(BASE.read_text(encoding='utf8'));c=parse(OUT.read_text(encoding='utf8'))
same=normalized(without_target_silk(a))==normalized(without_target_silk(c))
assert same,'Unexpected non-artwork candidate change; do not apply'
assert hashlib.sha256(LIVE.read_bytes()).hexdigest()==before
out={'candidate':OUT.name,'native_version':pcbnew.GetBuildVersion(),'changes':changes,
     'all_non_target_silk_source_objects_equal':same,'native_save_reload':True,
     'production_PCB_unchanged':True,'production_hash':before,
     'candidate_hash':hashlib.sha256(OUT.read_bytes()).hexdigest(),
     'status':'Prepared candidate only; live/saved production PCB NOT modified'}
out['base_candidate']=BASE.name
OUT.with_name(OUT.stem+'-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['changes','production_hash','candidate_hash']}))
