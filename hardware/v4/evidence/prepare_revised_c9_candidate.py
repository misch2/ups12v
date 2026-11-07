"""Build the C9 proposal on an offline checkpoint copy; never writes live CAD."""
from pathlib import Path
import hashlib,json,sys,subprocess,shutil
sys.dont_write_bytecode=True
import pcbnew
E=Path(__file__).resolve().parent
B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
before=hashlib.sha256(B.read_bytes()).hexdigest()
p=json.loads((E/'c9-revised-copper.json').read_text())
b=pcbnew.LoadBoard(str(E/'c9-apply-entry.kicad_pcb'))
c=next(f for f in b.GetFootprints() if f.GetReference()=='C9')
def xy(pt):return pcbnew.VECTOR2I(round(pt[0]*1e6),round(pt[1]*1e6))
c.SetPosition(xy([61.1,69.1]));c.SetOrientationDegrees(0)
removed=[]
for t in list(b.GetTracks()):
    uid=t.m_Uuid.AsString()
    if uid in p['remove_tracks'] or uid in p['remove_vias']:
        removed.append(uid);b.Remove(t)
assert set(removed)==set(p['remove_tracks'])|set(p['remove_vias'])
for net,a,z,w in p['segments']+[p['source_In2_segment']]:
    t=pcbnew.PCB_TRACK(b);t.SetStart(xy(a));t.SetEnd(xy(z));t.SetWidth(round(w*1e6))
    t.SetLayer(pcbnew.In2_Cu if [net,a,z,w]==p['source_In2_segment'] else pcbnew.F_Cu)
    t.SetNet(b.FindNet(net));b.Add(t)
net,pt,dia,drill=p['new_PGND_via']
v=pcbnew.PCB_VIA(b);v.SetPosition(xy(pt));v.SetWidth(round(dia*1e6));v.SetDrill(round(drill*1e6))
v.SetViaType(pcbnew.VIATYPE_THROUGH);v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu);v.SetNet(b.FindNet(net));b.Add(v)
# Standalone pcbnew ZONE_FILLER crashed on the scratch board in this install.
# Use CLI analysis-only refill for DRC instead; never invoke this in live IPC.
out=E/'revised-c9-candidate.kicad_pcb'
assert out.resolve()!=B.resolve()
assert pcbnew.SaveBoard(str(out),b)
# Native saving from a backup without its own project can write default scratch
# settings; restore an exact copy for representative scratch DRC afterwards.
for suffix in ['.kicad_pro','.kicad_dru']:
    shutil.copy2(B.with_suffix(suffix),out.with_suffix(suffix))
check=subprocess.run([sys.executable,'-c',
    "import pcbnew,json,sys; b=pcbnew.LoadBoard(sys.argv[1]); print(json.dumps({'footprints':len(list(b.GetFootprints())),'tracks':sum(not isinstance(t,pcbnew.PCB_VIA) for t in b.GetTracks()),'vias':sum(isinstance(t,pcbnew.PCB_VIA) for t in b.GetTracks())}))",str(out)],capture_output=True,text=True,check=True)
counts=json.loads(check.stdout)
assert counts==p['expected_counts']
assert hashlib.sha256(B.read_bytes()).hexdigest()==before
(E/'revised-c9-candidate-verification.json').write_text(json.dumps({'proposal_only':True,'production_unchanged':True,'production_hash':before,'candidate_hash':hashlib.sha256(out.read_bytes()).hexdigest(),'native_save_reload':True,'refill':'Use CLI analysis-only refill for DRC; standalone pcbnew filler crashed before save','counts':counts,'removed_item_ids':removed,'position_mm':[61.1,69.1],'rotation':0},indent=2)+'\n')
print(json.dumps({'proposal_only':True,'production_unchanged':True,'counts':counts}))
