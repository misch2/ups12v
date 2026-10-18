# Phase4.18 — accepted F5 installed into production; PASS

2026-10-18. Owner accepted Phase4.17 at prototype level and authorized its exact
bounded adoption. Production migration and final independent verification are
complete. **0opens/0physical DRC/0parity/0ERC errors. STOP for owner review.**

## Quick start

The current production project is [ups12v_v4.kicad_pro](../../ups_v4/ups12v_v4.kicad_pro).
Use the new [accepted manifest](accepted-installed-baseline.json) and
[final production proof](final-production-proof.json). The next milestone is
only a [cleanup/pre-fabrication review proposal](NEXT_REVIEW.md); no cleanup or
manufacturing output has been executed. Do not replay this installed migration.

## Installed identities

| Production file | SHA256 |
|---|---|
| PCB | `4e13e4c11c486aa4fba7866817f5c37e715b248ab696cbd4a599970cf2a2ea84` |
| Schematic, unchanged | `281d5eccd48a9b07f3ab3b7b836c7ad395af59487c775ad20a4efb3828bdba68` |
| Project, unchanged | `477e5c47219922b25619e9db0748961ed83af3958866842e0a34ad1d1641a21e` |
| Rules, unchanged | `a7bfa1d3fe8b0ba2a9a034a982b866c439c939321d558af2460c7b95ac25ebb7` |

Entry PCB was the exact accepted Phase4.16
`bce08349485b0f8d53060fcc9ef1a3911eaabf0408de16b288d0655e30754899`.
Accepted Phase4.17 scratch remains unchanged at
`8221929563ed10653f84933549a6fdf99d69071364c12e83860a22f55326b9e6`.
Installed production is byte-identical to the successfully saved owning-editor
rehearsal. Its physical geometry/connectivity/actual fill exactly matches the
accepted scratch; the optional single-unit metadata distinction is recorded below.

## Exact adopted delta

- 18complete F5 footprint translations/rotations: U7/U8/Q10/L3,R60–R63,C60–C69.
- 117new straight tracks and30new circular through-vias, retaining their reviewed UUIDs.
- Zero original track/via modifications or removals; all8native PCB arcs retained.
- All F0 placements/copper preserved. J8 and TP17 fixed; all473pad identities retained.
- Exactly41previous opens closed; no unfinished route or manual routing action remains.

Final inventory:154footprints,473pads,1170tracks/arcs,324vias;157→116pad islands.
Independent connectivity proves exactly the accepted merges: SYS5,PGND12,
RAW10,OUT4,BST1,EN2,GATE1,SW2,SS1,FB2,VCAP1. No previous pad island split.
Complete preimage/postimage reconciliation is in
[the bounded plan](../phase4-18-preparation/exact-migration-plan-v2.json).

Every source hash/artifact was checked before migration. Elevated host inspection
established no existing editors; scratch/production locks were checked. A fresh
production-derived rehearsal used one owning-editor transaction. Its complete
returned and visible payloads, refill and editor save passed before independent
native review and the candidate gate. The same immutable mutation implementation
then passed fresh production saved/live preflight and one production transaction.
No scratch file replaced production; no serialized CAD was hand-edited.

SDK preparation preserved whole footprint padstacks/nets/fields/artwork and local
3D models, using the previously proven exact integer quarter-turn handling.
Native polygon graphics were additionally exported/compared vertex-for-vertex;
circles, rectangles, line endpoints and all8PCB arcs retain their native geometry.
New0.80/0.40mm vias use a proven uniform circular NORMAL through-padstack with
only its explicitly reviewed copper diameter resized through the supported SDK;
the final native all-layer copper/drill/padstack inventories match the source.

## Verification

| Context | Unconnected | Physical errors | Parity errors | ERC errors | DRC/ERC warnings |
|---|---:|---:|---:|---:|---:|
| Actual production, read-only checks |0|0|0|0|16/4|
| Independent production-derived isolated review |0|0|0|0|20/11|

Production warning identity multisets match accepted Phase4.16 production.
Isolated warning identities match the accepted F5 scratch in the same library
context. Ignored checks are unchanged; no new waiver or rule relaxation exists.

The independent native copy verifies exact accepted target tracks/pads/vias,
complete pad islands, zone and RF rule-area definitions, actual filled polygons
including holes, board/footprint artwork and polygon graphics. Consequently U7
switching/bootstrap/FB geometry, U8/Q10polarity and forward/reverse topology,
SYS/OUTcurrent paths, PGND returns and prior F0 electrical geometry inherit the
accepted Phase4.17 review without a new layout experiment or duplicate electrical
analysis. Matching-hardware qualifications remain exactly those already accepted;
this milestone makes no new thermal, voltage,2A or reverse-transient measurement.

All120offline toolkit tests pass, including negative controls for original-copper
changes, arc flattening, fixed J8 movement, pad-net changes, via-stack differences,
unsafe polygon getters and missing/duplicate/non-default unit mappings.
[Final regression log](../phase4-18-preparation/tests-complete.log).
No firmware build was needed or performed.

## Bounded optional metadata distinction

The installed KiCad10.0.7IPC FootprintInstance/Definition messages do not expose
the serialized footprint `units` block. Updating18whole footprints therefore
omits their optional unit information. The first strict retained-serialization
check detected exactly these18omissions; the editor was left saved and unchanged
while the difference was investigated from captured evidence. No assertion,
unstable IPC, uncertain transaction, recovery or transaction retry occurred.

KiCad's [FOOTPRINT definition](https://raw.githubusercontent.com/KiCad/kicad-source-mirror/10.0/pcbnew/footprint.h)
describes unit information as optional mapping for multi-unit symbols. Its
[netlist updater](https://raw.githubusercontent.com/KiCad/kicad-source-mirror/10.0/pcbnew/netlist_reader/board_netlist_updater.cpp)
reconstructs that information from component units during schematic synchronization.
For this board, every omitted block is exactly one unit named A covering every
physical pin of that footprint, with no duplicate or missing pin. We classify
only this complete default form as derived metadata equivalent for this migration.
Multi-unit/non-A/subset mappings and every other property remain strict errors.

An export-only verifier now proves that narrow distinction with negative tests.
The native mutation implementation and both successful transactions stayed
unchanged. The independent verifier/helper are separately hash-bound through
the rehearsal proof and production gate. Full structural comparison finds no
other non-placement difference: values, footprint definitions, models, pads,
attributes/BOM/variant flags, local overrides and all unaffected objects remain
exact. No F8 synchronization or CAD patch was used to hide the distinction.

## Final evidence and boundary

- [Fresh native source preflight](../phase4-18-entry-native/context.json).
- [Successful rehearsal gate](../phase4-18-editor-rehearsal-v3/candidate-proof.json).
- [Production saved/live readback](final-live-readback.json).
- [Independent final native review](../phase4-18-final-production-native/summary.json).
- [Complete final proof](final-production-proof.json),
  [production checks](production-checks.json), [accepted native manifest](accepted-installed-baseline.json).
- [Final editor ownership](final-editor-ownership.json):0editors after normal,
  clean, hash-guarded closes of only the two agent-launched editors.

No F5 redesign, USB/IC1 optimization, F0 routing change, schematic/rules/BOM/
population change, deferred legacy cleanup, firmware, manufacture, purchasing,
power-up, Git commit or push. **STOP at this new production checkpoint.**
