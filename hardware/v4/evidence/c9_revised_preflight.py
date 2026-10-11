"""Proposal only: native in-memory placement on checkpoint COPY; never SaveBoard."""
from pathlib import Path
import sys,json,math,hashlib
sys.dont_write_bytecode=True
import pcbnew
E=Path(__file__).resolve().parent
b=pcbnew.LoadBoard(str(E/'c9-apply-entry.kicad_pcb'))
c=next(f for f in b.GetFootprints() if f.GetReference()=='C9')
c.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(55.25),pcbnew.FromMM(70.35)))
c.SetOrientationDegrees(180)
def xy(p):return [pcbnew.ToMM(p.x),pcbnew.ToMM(p.y)]
for f in b.GetFootprints():f.BuildCourtyardCaches()
court=c.GetCourtyard(pcbnew.F_CrtYd)
collisions=[];nearest=[]
for f in b.GetFootprints():
 if f==c:continue
 p=f.GetCourtyard(pcbnew.F_CrtYd)
 if not p.OutlineCount():continue
 if court.Collide(p,0):collisions.append(f.GetReference())
 # Native polygon-to-polygon collision tests bracket separation to 1um.
 if court.Collide(p,pcbnew.FromMM(1)):
  lo,hi=0,1000000
  while hi-lo>1000:
   mid=(lo+hi)//2
   if court.Collide(p,mid):hi=mid
   else:lo=mid
  nearest.append([hi/1e6,f.GetReference()])
out={'position_mm':xy(c.GetPosition()),'rotation_degrees':c.GetOrientationDegrees(),'pads':[{'pin':p.GetNumber(),'net':p.GetNetname(),'xy':xy(p.GetPosition()),'bbox':[xy(p.GetBoundingBox().GetOrigin()),xy(p.GetBoundingBox().GetEnd())]} for p in c.Pads()],'courtyard_collisions':collisions,'nearest_native_courtyard_gaps_mm':sorted(nearest),'minimum_board_copper_clearance_mm':pcbnew.ToMM(b.GetDesignSettings().m_MinClearance),'native_version':pcbnew.GetBuildVersion(),'source':'Read-only baseline backup, candidate moved ONLY in memory; no PCB/library save'}
(E/'c9-revised-courtyard.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
