# Phase4.24U validation record

## Successful preconditions

`production-identity-v2/snapshot-proof.json` and
`accepted-candidate-capture/snapshot-proof.json` bind the source and accepted
candidate to the owner-specified hashes. Their native canonical proof directories
compare full native read/save output from saved boards and IPC string exports.
The original `production-preflight/STOP.json` is retained: literal IPC string
serialization differed from saved text. Offline native canonical comparison
proved complete equality, so a fresh identity context was used. No source change,
assertion or unstable access occurred at that step.

`exact-adoption-plan-v2.json` binds the exact four original physical pads, ten
accepted graphic UUIDs/payloads, source/goal captures, accepted T evidence and
twelve implementation files. The earlier unsent `exact-adoption-plan.json` is
obsolete and was not used for the rehearsal.

## Regression checks

Six focused adoption tests pass. Full suite: **188 tests, OK**, using the existing
local CAM dependencies:

```powershell
python -B -c "import sys,unittest; sys.path.insert(0,'hardware/v4/evidence/phase4-24-owner-gerber-review/deps'); r=unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('hardware/v4/tools/tests')); sys.exit(not r.wasSuccessful())"
```

An initial full-suite invocation without that dependency path reported missing
gerbonara/shapely imports. No dependencies were installed or changed. Two initial
test-fixture lookups were corrected to identify Q1 by its physical pad UUID;
the final six focused tests and all188 tests passed before any mutation.

## Owning-editor rehearsal

`owning-editor-rehearsal/` was prepared from the production source and accepted
manifest, with local project/library companions copied to the isolated project.
It records clean PID/document/window/socket guards, `ipc-before.json`, intended
and returned full footprint payloads, commit token, post-commit capture, refilled
capture and saved capture. `ipc-saved.json` and `final-live-proof.json` record
successful editor save and saved/live readback. Production was never the target.

`rehearsal-independent-checks/` is a separate native readback copy. The monitored
worker passed original geometry and layout/fill comparisons, then failed the
complete native inverse test. `restored-source.kicad_pcb` is a diagnostic native
save only; it was never installed anywhere. `restored-source.diff` establishes
the exact Q1/Q2/U4 units metadata loss. These artifacts are retained, not repaired.

The worker exited with a normal ToolError after the failed hash check. No native
assertion or IPC failure was detected. DRC/ERC/export stages were not run, and
`accept-rehearsal` was never executed. No production context or transaction exists.

The later routine clean-close request was rejected by `editor_lifecycle` before
window operations: its generic STOP branch delegates to legacy J7 cleanup and
requires `j7-migration-context.json`. No bypass, forced close or retry followed.
The clean rehearsal editor remains open; this does not authorize further editing.

## Final preservation

`inputs-after.json` reproduces all35 protected and11 accepted-artifact hashes in
`inputs-before.json`. `final-result.json` and both STOP markers record rejection.
Production PCB before/after is identical at8c68d920…460e87; accepted candidate and
owner ZIP remain unchanged. No new release baseline is declared. No production
DRC/ERC/GTP success is inferred from the accepted T result or the partial rehearsal.
