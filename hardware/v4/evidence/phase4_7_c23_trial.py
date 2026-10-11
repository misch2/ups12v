"""Focused scratch-only native placement; never saves production CAD."""
from pathlib import Path
import hashlib,json,shutil,sys
sys.dont_write_bytecode=True
import pcbnew
E=Path(__file__).resolve().parent;B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
assert pcbnew.GetBuildVersion().startswith('10.0.')
h=hashlib.sha256(B.read_bytes()).hexdigest()
b=pcbnew.LoadBoard(str(B))
f=next(f for f in b.GetFootprints() if f.GetReference()=='C23')
f.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(63.0),pcbnew.FromMM(67.6)))
target=E/'phase4-7-c23-placement-trial.kicad_pcb'
pcbnew.SaveBoard(str(target),b)
shutil.copy2(B.with_suffix('.kicad_pro'),target.with_suffix('.kicad_pro'))
r=pcbnew.LoadBoard(str(target));c=next(f for f in r.GetFootprints() if f.GetReference()=='C23')
assert c.GetPosition()==f.GetPosition()
assert h==hashlib.sha256(B.read_bytes()).hexdigest()
print(json.dumps(dict(kicad=pcbnew.GetBuildVersion(),scratch=str(target),C23=[63.0,67.6],production_hash_unchanged=True)))
