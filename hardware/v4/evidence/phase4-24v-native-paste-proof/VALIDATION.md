# Phase4.24V validation record

## Boundary and editor observation

AGENTS.md, active U handover, U RESULT/STOP/residual native diff and the T native
worker/transaction were read. `initial-editor-observation.json` records read-only
CIM/path/lock evidence for rejected U PID72064. No interaction with that editor
was issued. Production SHA8c68… and accepted T SHAd0a8… were checked before copying.

## Tested native method and attempts

`v4kicad.stencil_native_proof` is import-inert and scratch-only. It reuses the
toolkit's hash/context/lock guards, monitored native workers, concrete LSEQ/LSET,
native geometry/layout snapshots, native save, inverse paste operation and native
check parsing. It introduces no CAD text writer. The read-only metadata scanner
extracts complete native-authored unit blocks and reference/UUIDs; source text is
not modified or normalized. IPC cannot provide those omitted properties.

- `candidate/`: native read-only source snapshot passed. Apply failed on a Python
  binding TypeError because `Clone` returns EDA_ITEM and the shape cast requires
  BOARD_ITEM. Nothing was saved; copied PCB still equals8c68…; STOP retained.
- `candidate-v2/`: corrected supported two-stage cast succeeded; saved PCB equals
  T byte-for-byte. `independent-readback/` passed geometry/layout/unit equality
  and inverse full native SHA, but a later hole report traversed the consumed
  board after `Remove` and got a Python AttributeError on a SWIG proxy. STOP
  retained. The production and rejected U boards were not targets.
- `candidate-v3/`: fresh copy and fresh snapshot, then the same targeted operation;
  hole inventory now precedes the inverse proof. All checks completed. This is
  the **only final V candidate/proof context**. No stopped context was retried.

All final actions bind the same finalized implementation hashes. The duplicate
wx image-handler notices from two board loads and SWIG ownership exit notices
after removing proof graphics are retained in logs. **No native assertion or IPC
failure occurred**; no recovery or assertion suppression was used.

## Final checks

`offline-tests-v3.log`: **195 tests PASS**, including seven new negative/control
tests for exact unit preservation, absent blocks, reference identity, incomplete
coverage and rejection of production/U target paths. The full suite uses the
existing local CAM dependency directory; no dependency installation occurred.
It was rerun after each adapter correction before new native mutation.

`candidate-v3/snapshot-result.json`: KiCad10.0.7 source snapshot; source native save
equals original source bytes. `apply-result.json`: exact four pad memberships and
ten original accepted graphic UUIDs, native output equals accepted T SHA.

`independent-readback-v3/verify-result.json`: second-process native reload,
original geometry/layout equality, all154 complete unit block/UUID records equal,
473pads/324vias/41PTH/12NPTH, inverse native source exact SHA8c68….

`independent-readback-v3/checks-summary.json`: fresh native DRC0errors/0opens/
0parity,18 warnings; the complete violation records and ignored-check list equal
T. Original16 retained plus exactly Q2/Q10 intentional board/library paste
mismatches, no additional warning. Fresh ERC0errors/4warnings. Their complete
identities equal `phase4-21-production-adoption/production-erc.json`, as recorded
in `erc-production-baseline-comparison.json`.

An exploratory comparison against `phase4-21-final-production-native/erc.json`
instead found7 extra footprint-library-link warnings in that old isolated copy;
its4 isolated-pin-label warnings are the accepted ones. That exploratory mismatch
and diff are retained. It is superseded by the exact comparison to the actual
accepted **production** ERC report, not by filtering away a new warning.

`independent-readback-v3/gtp-comparison.json`: actual precision6 F.Paste export
composed using Gerbonara/Shapely,411 connected openings, **raw XOR=0mm²**, missing/
extra area=0. File hashes differ only because two generation timestamp lines
differ (`gtp-header-diff.txt`). Actual union area435.2698278212494mm². Exact T
full-native identity and exact GTP union bind the T physical four-land delta:
two windows eachQ1/Q2/Q10, fourU4,393→411openings,401 unrelated pad contributions
unchanged, accepted coverage/web/containment and F0/F5/DNP presence. T's full CAM
proof remains immutable rather than repeating unrelated audits or images.

`protected-inputs-after.json`: all55 bound production/accepted/U evidence inputs
unchanged. `local-library-preservation.json`: all9 copied project-local library/
table files match current production. Native checks did not change the V PCB hash.
No production modification, Gerber ZIP re-export, upload, order, purchase, commit
or push. `PRODUCTION_PROCEDURE.md` is a proposal, not an executed installation.
