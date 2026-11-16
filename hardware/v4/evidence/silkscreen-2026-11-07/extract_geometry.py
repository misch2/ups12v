"""Read native IPC-exported snapshot; geometry experiments remain in memory only."""
from pathlib import Path
import json, sys
import pcbnew as p
E=Path(__file__).resolve().parent
tag=sys.argv[1] if len(sys.argv)>1 else 'before'
b=p.LoadBoard(str(E/(tag+'.kicad_pcb')))
def box(q):
    return [p.ToMM(v) for v in [q.GetX(),q.GetY(),q.GetRight(),q.GetBottom()]]
def union(boxes):
    return [min(q[0] for q in boxes),min(q[1] for q in boxes),max(q[2] for q in boxes),max(q[3] for q in boxes)]
def text_box(t):
    return box(t.GetEffectiveTextShape().BBox())
rows=[]
for f in b.GetFootprints():
    ref=f.Reference()
    physical=[box(pad.GetBoundingBox()) for pad in f.Pads()]
    physical += [box(g.GetBoundingBox()) for g in f.GraphicalItems()
                 if isinstance(g,p.PCB_SHAPE) and g.GetLayer() in [p.F_Fab,p.F_SilkS]]
    if not physical:
        physical=[box(f.GetBoundingBox(False,False))]
    orig=ref.GetTextAngle().AsDegrees()
    pos=[p.ToMM(v) for v in ref.GetPosition()]
    row=dict(ref=f.GetReference(),body=union(physical),footprint_bbox=box(f.GetBoundingBox(False,False)),
             pads=[box(pad.GetBoundingBox()) for pad in f.Pads()], pos=pos,
             angle=orig,visible=ref.IsVisible(),layer=ref.GetLayerName(),
             text_box=text_box(ref),sizes={},offsets={})
    for angle in [0,90]:
        ref.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T))
        q=text_box(ref)
        row['sizes'][angle]=[q[2]-q[0],q[3]-q[1]]
        row['offsets'][angle]=[(q[0]+q[2])/2-pos[0],(q[1]+q[3])/2-pos[1]]
    ref.SetTextAngle(p.EDA_ANGLE(orig,p.DEGREES_T))
    rows.append(row)
static=[]
for g in b.GetDrawings():
    if g.GetLayer()==p.F_SilkS:
        static.append(dict(type=g.GetClass(),text=g.GetShownText(False) if isinstance(g,p.PCB_TEXT) else '',box=text_box(g) if isinstance(g,p.PCB_TEXT) else box(g.GetBoundingBox())))
for f in b.GetFootprints():
    for t in [f.Value()]+[g for g in f.GraphicalItems() if isinstance(g,p.PCB_TEXT)]:
        if t.GetLayer()==p.F_SilkS and t.IsVisible():
            static.append(dict(type=t.GetClass(),text=t.GetShownText(False),box=text_box(t)))
result=dict(board=box(b.GetBoardEdgesBoundingBox()),labels=rows,static=static)
(E/(tag+'-geometry.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(labels=len(rows),visible=sum(r['visible'] for r in rows),angles={a:sum(r['angle']==a for r in rows) for a in sorted(set(r['angle'] for r in rows))},static=len(static))))
