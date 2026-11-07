# Phase4.21 — exact accepted J7/USB_CC2 correction installed; PASS

2026-10-18. **Production adoption complete. STOP for owner review.**

## Quick start

Production [PCB](../../ups_v4/ups12v_v4.kicad_pcb) now contains precisely the
three accepted Phase4.20 CC2 track replacements. Use the
[new accepted manifest](accepted-installed-baseline.json) and
[final production proof](final-production-proof.json). All errors and opens are
zero; vendor J7 PTH clearance is0.350mm. Manufacturing preparation requires a
separate authorization. Do not replay this completed migration.

## Bound identities and exact delta

| File | SHA256 |
|---|---|
| Production PCB, new | `4eb7bd2c72fec3cf49d3746250864b5237e7919760ebdbc3647cbc0101fa8737` |
| Accepted production entry | `4e13e4c11c486aa4fba7866817f5c37e715b248ab696cbd4a599970cf2a2ea84` |
| Approved Phase4.20 candidate, unchanged | `4eb7bd2c72fec3cf49d3746250864b5237e7919760ebdbc3647cbc0101fa8737` |
| Schematic, unchanged | `281d5eccd48a9b07f3ab3b7b836c7ad395af59487c775ad20a4efb3828bdba68` |
| Project, unchanged | `477e5c47219922b25619e9db0748961ed83af3958866842e0a34ad1d1641a21e` |
| Rules, unchanged | `a7bfa1d3fe8b0ba2a9a034a982b866c439c939321d558af2460c7b95ac25ebb7` |

Production is byte-identical to the approved candidate **as the result of the
native owning-editor transaction/refill/save**. No candidate file was copied
over production. Fresh full saved/live identity preflights preceded both the
successful rehearsal and production mutation; each used exactly one commit.

| Removed source UUID | Installed approved UUID |
|---|---|
| `4d552340-51f3-4a54-8e44-32e11454ef13` | `6b749cde-148c-4782-a324-42b2486548e4` |
| `1814d666-f764-4da0-839c-339e7a06c1ca` | `4c8fa43c-a929-427d-a375-6b9d0366ee00` |
| `878d8bda-a418-454a-8362-c06c73dcd100` | `a01da3d3-795d-4da0-9171-01cdf01cb32a` |

All three remain USB_CC2/In2.Cu/width0.180mm. Fixed external endpoints are
(119.050,75.300) and(118.740,79.725); new corners are
**(119.860,76.110)/(119.860,78.605)**. Vertical legX119.860mm. No other track,
via, footprint, pad, rule, schematic or electrical connection was changed.
[Complete immutable UUID/preimage plan](../phase4-21-preparation/exact-migration-plan.json).
The focused Git diff is10inserted/10removed lines, with serializer ordering
accounting for the unchanged neighboring CC2 segment's textual relocation.

## Verification and preservation

| Context | Physical DRC errors | Opens | Parity errors | ERC errors | DRC/ERC warnings |
|---|---:|---:|---:|---:|---:|
| Successful owning-editor rehearsal, independent native review |0|0|0|0|20/11|
| Production, read-only native CLI |0|0|0|0|16/4|
| Final independent production-derived native review |0|0|0|0|20/11|

Rehearsal gate:
[candidate proof](../phase4-21-editor-rehearsal-v3/candidate-proof.json).
The production transaction required its exact plan, implementation hashes and
unchanged rehearsal sources. Production [preflight](ipc-preflight.json),
[prepared operations](prepared-transaction.json), [returned items](returned-items.json),
[post-commit readback](ipc-after.json), [live refill](live-refilled.json),
[editor save](ipc-saved.json) and [final live identity](final-live-readback.json)
are retained. Independent [native review](../phase4-21-final-production-native/summary.json)
proves saved geometry, native connectivity and refill preservation.

Preserved exactly: **473pads/116native pad islands/324vias/8native PCB arcs**,
1170tracks/arcs in total,154footprints, every retained object and its complete
non-fill saved properties, all original F0/F5 power/RF/USB geometry, all zone and
rule-area definitions. The actual PGND filled contour vertices and holes match
the approved candidate and original source; live fill equals independent native
saved/readback fill. This is physical copper preservation, not just zone outline
or filled-flag equality. No old pad connection split or new net merge exists.

The independent [vendor screen](vendor-screen.json) has **0PTH-track failures,
0PTH-plane failures,0hole-pair failures,0SMD-spacing failures and0courtyard
intersections**. J7 shell PTH-to-CC2 gap is **0.350000mm**; selected minimum
different-net copper/drill gaps remain0.161041/0.311041mm.
[Local analytic clearance](J7-clearance.json). Existing missing-courtyard
dispositions and warning identities remain unchanged, as do all six native
[ignored check identities](ignored-check-preservation.json). This is design
geometry evidence, not a manufactured tolerance or release qualification.

Final offline toolkit suite: **136tests PASS**, including exact UUID/geometry
negative controls, endpoint/PID/document binding, runtime-parent normalization
that still rejects real geometry changes, and cleanup refusal for production or
native assertion/IPC failure. [Log](../phase4-21-preparation/tests-complete-final.log).
Documentation/tooling changes require no firmware build; none was performed.

## Historical diagnostics and editor lifecycle

The first two read-only connection attempts used historical endpoints and were
refused before any CAD mutation. The owner explicitly authorized resuming and
closed all instances. Both stopped contexts remain preserved. A fresh complete
source saved/live preflight passed, then the first scratch commit was rejected
by an incorrectly nested comparison of only three runtime board-parent links.
Export-only diagnosis proved full meaningful equality; no native assertion,
IPC instability or genuine preservation failure occurred in that scratch.
[Diagnostic disposition](../phase4-21-editor-rehearsal-v2/validation-disposition.json).

The agent's hidden window caused an unnecessary request for owner cleanup.
The agent handled it: narrowly guarded live readback confirmed the exact known
scratch state, archived **only that diagnostic scratch** through its owning
editor, then normally closed its now-clean window. This exception cannot handle
production, genuine geometry mismatches, assertions or IPC stops, is not a
candidate gate, and never replays a transaction. The diagnostic context was
not reused. A completely fresh rehearsal-v3 then passed the corrected immutable
implementation before production. All subsequent endpoint selection used actual
OS pipe/PID/document evidence, rather than assumed addresses.

The final production editor was visible, saved, verified and normally closed.
All agent editors were cleaned up without force-kill or save/discard dialog
automation. [Final OS state](final-editor-state.json): **zero KiCad processes
and zero KiCad IPC pipes**.

## Phase boundary

Owner-fixed intended nominal PCB thickness is **1.6mm**. Production stackup,
copper weights, barrel-plating assumptions and fabrication parameters remain
**UNSELECTED**. No1.8/2.0mm proposal or stackup/rule/footprint/BOM/schematic
change was made. Existing Phase4.19 hardware/thermal/fit/sourcing qualifications
remain open. No USB/power optimization, legacy cleanup, Gerber/fabrication output,
release, component order, firmware change, hardware power-up, commit or push.

**STOP for owner review after verified production adoption.** Manufacturing
preparation requires separate authorization.
