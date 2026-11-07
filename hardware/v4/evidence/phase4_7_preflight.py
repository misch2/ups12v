"""Read-only KiCad 10 saved/native IPC geometry evidence. Never saves CAD."""
from pathlib import Path
import sys,json,hashlib,xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
import pcbnew
E=Path(__file__).resolve().parent
B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
paths=[B,B.with_suffix('.kicad_sch'),B.with_suffix('.kicad_pro')]
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
snapshot=json.loads((E/'c9-apply-phase4-7-ipc.json').read_text())
assert snapshot['board']==B.name and Path(snapshot['project']).resolve()==B.parent.resolve()
assert snapshot['hashes']==hashes
b=pcbnew.LoadBoard(str(B))
def xy(v):return [round(pcbnew.ToMM(v.x),6),round(pcbnew.ToMM(v.y),6)]
fps=[]
for f in b.GetFootprints():
 pads=[]
 for p in f.Pads():
  box=p.GetBoundingBox()
  pads.append(dict(pin=p.GetNumber(),net=p.GetNetname(),xy=xy(p.GetPosition()),uuid=p.m_Uuid.AsString(),size=xy(p.GetSize()),bbox=[xy(box.GetOrigin()),xy(box.GetEnd())],shape=str(p.GetShape())))
 courts=[]
 for s in f.GraphicalItems():
  if s.GetLayer()==pcbnew.F_CrtYd:
   courts.append(dict(shape=str(s.GetShape()),start=xy(s.GetStart()),end=xy(s.GetEnd())))
 fps.append(dict(ref=f.GetReference(),value=f.GetValue(),xy=xy(f.GetPosition()),angle=f.GetOrientationDegrees(),uuid=f.m_Uuid.AsString(),pads=pads,courtyard=courts))
tracks=[];vias=[]
for t in b.GetTracks():
 row=dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname())
 if isinstance(t,pcbnew.PCB_VIA):row.update(width=pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu)),xy=xy(t.GetPosition()),drill=pcbnew.ToMM(t.GetDrillValue()));vias.append(row)
 else:row.update(width=pcbnew.ToMM(t.GetWidth()),start=xy(t.GetStart()),end=xy(t.GetEnd()),layer=b.GetLayerName(t.GetLayer()));tracks.append(row)
lp=snapshot['pads'];lt=snapshot['tracks'];lv=snapshot['vias']
def pxy(v):return [int(v.get(a+'Nm',0))/1e6 for a in ['x','y']]
assert set(lp)=={p['uuid'] for f in fps for p in f['pads']}
assert all(p['xy']==pxy(lp[p['uuid']]['position']) and p['net']==lp[p['uuid']].get('net',{}).get('name','') for f in fps for p in f['pads'])
assert set(lt)=={t['uuid'] for t in tracks} and set(lv)=={v['uuid'] for v in vias}
assert all(t['start']==pxy(lt[t['uuid']]['start']) and t['end']==pxy(lt[t['uuid']]['end']) and t['net']==lt[t['uuid']]['net']['name'] and abs(t['width']-int(lt[t['uuid']]['width']['valueNm'])/1e6)<1e-7 for t in tracks)
assert all(v['xy']==pxy(lv[v['uuid']]['position']) and v['net']==lv[v['uuid']]['net']['name'] for v in vias)
baseline=json.loads((E/'c9-apply-approved-final-ipc.json').read_text())
assert all(snapshot[n]==baseline[n] for n in ['footprints','pads','tracks','vias','zones','shapes','texts']), 'Live geometry differs from authoritative checkpoint'
assert all(hashes[p.name]==hashlib.sha256(p.read_bytes()).hexdigest() for p in paths)
out=dict(kicad=pcbnew.GetBuildVersion(),hashes=hashes,baseline_exact_live_match=True,saved_live_pad_track_via_match=True,footprints=fps,tracks=tracks,vias=vias)
(E/'phase4-7-geometry.json').write_text(json.dumps(out,indent=2)+'\n')
nets={'REGN','TS','BATP','PROG','CE_N','ILIM_HIZ','SDRV','ACDRV1','BTST1','BTST2','~INT','STAT'}
for n in sorted(nets):
 print(n,[(f['ref'],p['pin'],p['xy']) for f in fps for p in f['pads'] if p['net']==n], 'tracks',sum(t['net']==n for t in tracks),'vias',sum(v['net']==n for v in vias))
print('VERSION',out['kicad'],'BASELINE EXACT MATCH',True)
