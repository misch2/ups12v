# UPS V4 — Phase4.13 verified production adoption — PASS

2026-10-17. The approved owner design is now adopted into the original production
project through native KiCad10.0.7 editor transactions. **STOP for owner review.**
No subsequent IC1 or F5 routing is authorized by this checkpoint.

## Quick start

Production remains `hardware/v4/ups_v4/ups12v_v4.kicad_pro`. Its PCB editor was
left open on the successfully saved production board (agent-launched PID116104).
The original owner scratch remains unchanged and is no longer the production
baseline. Use [accepted-installed-baseline.json](accepted-installed-baseline.json)
for future guarded work; preserve the older manifests as historical evidence.

The bounded next proposal is [NEXT_IC1_F5.md](NEXT_IC1_F5.md). It is a proposal,
not an instruction to execute the next routing milestone.

## Exact accepted identities

| File | SHA256 |
|---|---|
| PCB | `75060f4b3d0f57e65f2c6e4736f3dc32d42e62e359541671b1ffce63eceb7014` |
| Schematic | `281d5eccd48a9b07f3ab3b7b836c7ad395af59487c775ad20a4efb3828bdba68` |
| Project, unchanged | `477e5c47219922b25619e9db0748961ed83af3958866842e0a34ad1d1641a21e` |
| Custom rules, unchanged | `a7bfa1d3fe8b0ba2a9a034a982b866c439c939321d558af2460c7b95ac25ebb7` |

The accepted manifest is generated from actual saved files and post-refill live
native objects, then accepted only after independent final validation. No
historical manifest or source hash was manually changed. Original owner PCB
remains `55fe96f32e8e440996924239dd1409f84cb0ffc27cb30c7ea48c7e6c02f610f5`;
all four original owner source files remain hash-identical. The accepted former
production is preserved by its original manifest and the initial immutable
[production copy](../phase4-13-production-preflight/context.json).

## Validation

| Check | Final production | Matched isolated control context |
|---|---:|---:|
| Physical DRC errors | **0** | **0** |
| Schematic/PCB parity | **0** | **0** |
| Remaining opens | **44** | **44** |
| DRC warnings | 16 | 20 |
| ERC errors | **0** | **0** |
| ERC warnings | 4 | 11 |

Production warning identities and ignored checks match the original accepted
production context. In the matched isolated context, warning identities match
the independently reviewed owner. Library-context differences are not design
regressions and no rule or exclusion was relaxed.

Final saved/native and live IPC identity both pass. Independently loaded,
saved/reloaded and refilled native output is exactly equal to the owner for:

- All **1027 track/arc objects, including eight true PCB_ARC objects**,287 vias,
  154 footprints and473 pads, with exact source UUID retention/mapping.
- Native copper widths on every via layer, drills, padstacks and routed geometry.
- All473 pad assignments and all160 native pad-island sets; no original
  accepted pad connection split. Original169 islands become160 by exactly the
  approved eight USB data closures and U2 PGND closure.
- All104 exported electrical partitions and154 component properties; both
  resistor-separated USB pairs, U1.27=D+ and U1.26=D−, all nine USB/ESD links,
  and all four J7 VBUS contacts plus U4/C28/C27 are retained. Neither R48 nor
  R49 is bypassed.
- Exact filled In1 PGND polygons, including holes, plus all zone definitions,
  board outline/drawings, RF keepout, F5 reservations and actual rule context.
  IC1/L1/U3 local fill grids and protected switching/bootstrap/feedback/bypass
  geometry match owner; all-pad partitions also retain NT1/NT2 electrical
  separation. These are CAD facts, not power-up or thermal measurements.
- All component values, footprint identities, population variants, project/rules
  and electrical architecture. No BOM component selection changed.

Exactly three F0 escapes remain: IC1.14 I2C_SCL, IC1.21 ~INT and IC1.1 STAT.
The other41 opens are the approved deferred F5 groups. See
[remaining-by-net.json](remaining-by-net.json).
One DRC ratsnest representative changes from an existing ~INT track to R28.2
on that same native island; exact island sets and per-net open counts prove
that no actual connection changed. This is not a new unrouted item.

## Complete production change inventory

Against the former accepted production:134 added/51 removed/3 modified native
track/arc objects;6 added/2 removed/1 modified vias; three footprint translations
C28/U2/R48 and ten affected native pad snapshots. The restored EN/BOOT vias use
owner UUIDs, with exact same physical geometry as the removed original UUIDs.
No duplicate replacement via was installed.

The schematic gains only two local labels, USB_MCU_DP at(436.88,134.62) and
USB_MCU_DN at(436.88,132.08); all pre-existing schematic objects remain. Exported
electrical topology exactly equals owner despite retained production wire
segmentation and independently generated label UUIDs.

The [full whitelist](../phase4-13-reconciliation/migration-whitelist.json) holds
all original/desired native objects and source-to-target UUIDs. The actual
[prepared transaction](prepared-transaction.json), [returned items](returned-items.json),
[post-commit readback](ipc-after.json), [post-refill live objects](live-saved.json)
and [final native proof](../phase4-13-final-production-native/final-production-proof.json)
record what was actually applied and independently observed.

Production retains its existing project/library metadata and schematic identity.
Owner-only tuning-generator records are omitted; their actual eight arcs and
all other finished copper are exactly retained. Field UUID/cache/unit/pin-type
presentation differences have independently equivalent artwork payloads,
component properties, electrical partitions, pad/drill geometry and filled
copper. No serialized CAD file was hand-edited and no scratch PCB replaced the
production file.

Safe intentional non-USB owner edits on SYS, VIN1, MAIN_3V3, MCU3V3, D1-A and
R12/C26 are retained exactly. Historical R35/C26/SYS cleanup proposals were not
replayed. No U2/USB optimization, new return via, pair tuning or rule change was
added. The owner's accepted prototype USB qualifications remain recorded; this
is not impedance, ESD, EMI, certification or hardware-function qualification.

## Repair, rehearsal and supported method

The owner confirmed completion of the requested native F8 repair. A new isolated
review proved it changed exactly the four intended pad net names, with no track,
via, footprint or pad geometry change; all473 pads/169 baseline islands retained.
DRC53opens/0physical/0parity, ERC0errors. The failed first rehearsal was neither
reused nor retried and its diagnostics remain intact.

A fresh production-derived editor rehearsal then used **whole-footprint native
updates** for pad-net assignments, retaining all footprint geometry, fields and
models. Individual pad-net updates are no longer used. It passed post-commit
readback, refill/editor save and full independent native validation before the
first production write. The identical mapped operations were then used on the
original live production PCB, after exact baseline preflight and supported
Konnect schematic-label additions.

A read-only final-check false failure was investigated before production: its
expected payload had the **old pre-refill copper**, and the RF rule area contains
empty per-layer fill containers. Captured diagnostics proved that only intended
derived fill changed. The corrected checker retains exact non-fill identity,
requires rule-area containers to remain empty and independently compares every
actual fill vertex/hole to native saved/reloaded output. Negative tests reject
wrong copper, pad nets and zone definitions. No CAD repair/retry was needed.

Full offline suite95tests PASS after the final checker change. Production
transactions and native inspections completed without unexpected assertion,
IPC transport failure, rollback or recovery. KiCad settings were not changed.
The temporary native editor used the discovered `ipc://.tmp/kicad/api.sock`.

## Phase boundary

No IC1 control escape or F5 routing, further USB redesign, historical cleanup,
BOM/architecture/stackup/rule change, firmware build/change, fabrication,
purchase, hardware power-up, commit or push occurred. STOP here for owner review.
Recommend a fresh session for the separately approved three-escape milestone.

Primary evidence: [accepted-checkpoint.json](accepted-checkpoint.json),
[production-checks.json](production-checks.json),
[final-live-readback.json](final-live-readback.json),
[complete candidate proof](../phase4-13-complete-candidate/complete-candidate-proof.json),
[independent final native proof](../phase4-13-final-production-native/final-production-proof.json).
