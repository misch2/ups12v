"""Export KiCad's native graphical polygons for silkscreen visual inspection."""
from pathlib import Path
import sys,json
import pcbnew as p
E=Path(__file__).resolve().parent
tag=sys.argv[1] if len(sys.argv)>1 else 'before'
b=p.LoadBoard(str(E/('before.kicad_pcb' if tag=='planned' else tag+'.kicad_pcb')))
if tag=='planned':
    plan=json.loads((E/'plan.json').read_text())['layout']
    for f in b.GetFootprints():
        if f.GetReference() in plan:
            c=plan[f.GetReference()];t=f.Reference()
            t.SetTextAngle(p.EDA_ANGLE(c['angle'],p.DEGREES_T))
            t.SetPosition(p.VECTOR2I(*[round(x*1e6) for x in c['pos']]))
shapes=[]
def emit(g,kind,ref=''):
    q=p.SHAPE_POLY_SET()
    if isinstance(g,p.PCB_TEXT):g.TransformTextToPolySet(q,0,10000,p.ERROR_INSIDE)
    elif isinstance(g,p.PAD):g.TransformShapeToPolygon(q,p.F_Cu,0,10000,p.ERROR_INSIDE)
    else:g.TransformShapeToPolygon(q,g.GetLayer(),0,10000,p.ERROR_INSIDE)
    polys=[]
    for i in range(q.OutlineCount()):
        c=q.COutline(i)
        points=lambda c:[[p.ToMM(c.CPoint(j).x),p.ToMM(c.CPoint(j).y)] for j in range(c.PointCount())]
        polys.append(dict(outline=points(c),holes=[points(q.CHole(i,j)) for j in range(q.HoleCount(i))]))
    shapes.append(dict(kind=kind,ref=ref,polys=polys))
for f in b.GetFootprints():
    for pad in f.Pads():emit(pad,'pad',f.GetReference())
    for g in f.GraphicalItems():
        if isinstance(g,p.PCB_SHAPE) and g.GetLayer() in [p.F_Fab,p.F_SilkS]:
            emit(g,'fab' if g.GetLayer()==p.F_Fab else 'silk',f.GetReference())
    if f.Reference().IsVisible() and f.Reference().GetLayer()==p.F_SilkS:emit(f.Reference(),'reference',f.GetReference())
for g in b.GetDrawings():
    if g.GetLayer()==p.F_SilkS:emit(g,'silk')
(E/(tag+'-visual.json')).write_text(json.dumps(shapes,separators=(',',':'))+'\n')
print(json.dumps(dict(tag=tag,native_shapes=len(shapes))))
