"""Read saved PCB using KiCad 10 APIs; write evidence only, never CAD."""
from pathlib import Path
import hashlib, json, sys
sys.dont_write_bytecode = True
import pcbnew
E = Path(__file__).resolve().parent
B = E.parent / 'ups_v4/ups12v_v4.kicad_pcb'
S = B.with_suffix('.kicad_sch')
N = E / 'nanofit-final.net.xml'
paths = [B, S, N]
hashes = {str(p.relative_to(E.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
b = pcbnew.LoadBoard(str(B))
def xy(v): return [round(pcbnew.ToMM(v.x), 6), round(pcbnew.ToMM(v.y), 6)]
refs = {'J1','F1','Q1','Q2','R12','C26','C9','IC1','NT1','NT4','C12','C13','C15','C16','C18'}
fps = []
for f in b.GetFootprints():
    if f.GetReference() not in refs: continue
    fps.append(dict(ref=f.GetReference(), xy_mm=xy(f.GetPosition()), pads=[
        dict(pin=p.GetNumber(), net=p.GetNetname(), xy_mm=xy(p.GetPosition())) for p in f.Pads()]))
nets = {'VIN1','VBUS','Net-(C26-Pad1)','Net-(J1-Pin_2)','Net-(NT4-Pad2)'}
tracks, vias = [], []
for t in b.GetTracks():
    if isinstance(t, pcbnew.PCB_VIA):
        if t.GetNetname() in nets or (t.GetNetname() == 'PGND' and pcbnew.ToMM(t.GetPosition().y) < 61):
            vias.append(dict(net=t.GetNetname(), xy_mm=xy(t.GetPosition()), drill_mm=pcbnew.ToMM(t.GetDrillValue())))
    elif t.GetNetname() in nets:
        tracks.append(dict(net=t.GetNetname(), start=xy(t.GetStart()), end=xy(t.GetEnd()),
                           layer=b.GetLayerName(t.GetLayer()), width_mm=pcbnew.ToMM(t.GetWidth()), length_mm=pcbnew.ToMM(t.GetLength())))
out=dict(kicad=pcbnew.GetBuildVersion(), source='native pcbnew saved-board read only; not live extraction',
         hashes=hashes, footprints=fps, tracks=tracks, vias=vias,
         counts=dict(footprints=len(list(b.GetFootprints())), tracks=sum(not isinstance(t,pcbnew.PCB_VIA) for t in b.GetTracks()),
                     vias=sum(isinstance(t,pcbnew.PCB_VIA) for t in b.GetTracks())))
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p.relative_to(E.parent))] for p in paths)
(E/'safety-review-native-read.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(counts=out['counts'], positions={f['ref']:f['xy_mm'] for f in fps},
                     track_lengths_mm={n:round(sum(t['length_mm'] for t in tracks if t['net']==n),2) for n in nets})))
