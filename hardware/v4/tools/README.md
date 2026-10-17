# V4 guarded KiCad 10 toolkit

Read `AGENTS.md` and [V4_HANDOVER.md](../V4_HANDOVER.md) first.

**Current Phase4.16 production adoption PASS; STOP before F5.** Use the
[current accepted manifest](../evidence/phase4-16-production-adoption/accepted-installed-baseline.json)
and [adoption report](../evidence/phase4-16-production-adoption/ADOPTION.md).
Exact owner routing is installed:1053tracks/arcs,294vias,473pads/157islands,
41F5opens/0F0/0physical/0parity/ERC0. All8native arcs and accepted power/PGND,
USB and F5 geometry were verified. Production warnings16/4 remain unchanged;
matched isolated warnings20/11 also unchanged.107offline tests PASS.

`v4kicad.owner_migration` binds the complete Phase4.15 whitelist and exact native
transaction, which passed a fresh isolated owning-editor rehearsal before the
production transaction. `v4kicad.owner_migration_proof` is the final export-only
proof command: it separately binds intentional owner/production project hashes
and compares their resolved electrical rules exactly. Native net comparisons
exclude numeric net-code cache only for exact named nets; net names, code-only
identities and geometry remain checked. `editor_lifecycle` supports normal close
of an agent-launched clean, saved, hash-bound editor; it refuses stopped targets,
dirty windows and modal ambiguity and never force-kills or handles dialogs.

The first stopped rehearsal and its implementation remain historical evidence;
the owner discarded its editor without saving. Do not reuse it or replay the
installed migration: production no longer matches its required entry hash.

Historical Phase4.13 production adoption **PASS**. The owner accepts
the current USB prototype geometry. Read the [adoption report](../evidence/phase4-13-production-adoption/ADOPTION.md).
Its [historical accepted manifest](../evidence/phase4-13-production-adoption/accepted-installed-baseline.json)
is superseded by Phase4.16 above.
`v4kicad.migration` holds exact UUID/preimage reconciliation, whole-footprint net
updates, native ArcTrack CRUD and an independently proven candidate gate before
production transactions. It rejects stopped/used rehearsals and changed inputs.
Do not replay this installed migration: its original-source guards deliberately
no longer match the new production checkpoint. Never trust returned individual
pad-net updates alone; the first failed rehearsal remains historical evidence.
Owner native F8 repair, fresh full rehearsal and final production verification
resolved that STOP. Current production has1027tracks/arcs,287vias,473pads,
44opens/0physical/0parity/ERC0. Production warnings16/4 remain unchanged;
matched isolated warnings20/11 equal owner. Offline95tests PASS.

Only the unordered footprint definition.items list is order-normalized, proven
by exact payload multisets and a negative test. Refill is not ignored: all
non-fill native payloads remain exact and each live copper polygon vertex/hole
must match independently saved/reloaded native target fill. Empty RF rule-area
containers must contain no copper. Exact pad-island sets and per-net open groups
take precedence over a DRC ratsnest's interchangeable pad/track representative.

Historical Phase4.12 owner
corrections now independently **PASS**: both MCU_EN/BOOT vias restored,44opens/
0physical/0parity,ERC0errors; existing USB reference qualifications remain.
See the [confirmation](../evidence/phase4-12-owner-correction-confirmation-2026-10-17/CONFIRMATION.md).
No agent CAD repairs or production migration occurred in Phase4.12. The
[previous review](../evidence/phase4-12-owner-post-edit-review-arc-aware-2026-10-17/REVIEW.md)
records the now-corrected missing vias and their geometric dependency.
Shared native snapshots now retain arc start/mid/end, true native length and
outside copper polygons; `track_geometry` supports bounded export-only arc
measurements, and legacy straight-only/raster paths refuse arcs. Native review
did not change original sources;85 offline tests pass. The earlier read-only
USB plan remains available:
The [owner guide](../evidence/phase4-12-usb-improvement-plan/OWNER_USB_PLAN.md)
uses explicit polylines screened by `v4kicad.usb_improvement_plan`, without
native CAD I/O or USB route search. Historical Phase4.11 conditional USB review
was superseded by owner acceptance and Phase4.13 adoption. New IC1 work and F5
need separately authorized scope. Legacy cleanup replacements remain deferred.
These examples do not authorize
another batch. Use the current Phase4.13 manifest/context from handover; the
historical Phase4.9 paths below illustrate the command shape only. Never replay
an installed/failed plan or hand-edit serialized CAD.

## Quick start (PowerShell, repository root)

Run offline tests:

```powershell
python -B -m unittest discover -s hardware/v4/tools/tests -q
```

Use the current accepted manifest from the handover. Export a read-only native
context to a fresh directory before a new authorized mutation workflow:

```powershell
python -B hardware/v4/tools/kicad_v4.py snapshot --board hardware/v4/ups_v4/ups12v_v4.kicad_pcb --baseline-manifest hardware/v4/evidence/phase4-9-completion-ipc/accepted-installed-baseline.json --output-dir hardware/v4/evidence/my-new-context --native-python 'C:/Program Files/KiCad/10.0/bin/python.exe' --routing-context
```

After authorization, validate an **uninstalled** addition-only plan. The plan
path below is a placeholder; source, context and manifest must match:

```powershell
python -B hardware/v4/tools/kicad_v4.py validate --board hardware/v4/ups_v4/ups12v_v4.kicad_pcb --baseline-manifest hardware/v4/evidence/phase4-9-completion-ipc/accepted-installed-baseline.json --output-dir hardware/v4/evidence/my-new-candidate --native-python 'C:/Program Files/KiCad/10.0/bin/python.exe' --kicad-cli 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe' --plan hardware/v4/evidence/my-approved-add-only-plan.json --validation-context hardware/v4/evidence/my-new-context/routing-context.json --add-only --erc
```

Output directories must be new and scratch boards unlocked. Native API loads/
saves only the isolated byte-copy. Never reuse an open scratch. Native success
still requires routing-quality and electrical review before installation.

## Read-only review of an owner-edited project

First establish source authority: reconcile with the owning editors, or obtain
the owner's confirmation that editors are closed and saved files are current.
An empty sandbox process query does not establish this. Owner edits may differ
from production; retain the accepted production manifest unchanged.

`kicad_v4.py review` takes explicit `--board` (owner source),
`--reference-board` (accepted production), `--baseline-manifest`, a fresh
`--output-dir`, `--native-python` and `--kicad-cli`. Optional
`--routing-context --route-diagnostics` retain the complete native inventories.
It copies sources, checks both identities, snapshots before checks, refills/saves
only the isolated copy during DRC, independently verifies all tracks/vias/pads/
placements after refill, runs ERC/parity, then exports native pair recognition,
netclass names, pad connectivity islands and actual fill polygons with holes.
Original owner/project/rule files and accepted production remain hash-guarded.
No production migration is implemented by this command.

`review_compare` compares exported XML topology/component properties, native
pad-island preservation and exact warnings. Its supplemental read-only structural
inspection records properties absent from native snapshots, including tuning
groups and metadata; it never edits serialization. Ratsnest representative
endpoints can change without losing connectivity: compare native pad islands,
not only UUID pairs. Compare scratch warnings to an exact accepted-production
copy in the same library context, not an earlier uninstalled routing candidate.

KiCad10 may return an opaque SWIG pointer from `NETINFO_ITEM.GetNetClass()`;
use the supported direct `GetNetClassName()` for the native name. Source gates
and normal Python binding errors are distinct from native assertions/IPC safety
stops; preserve all diagnostics and follow the repository's recovery rules.

## Joint pre-application check

`plan_validation` uses only the standard library. Parent `validate` checks
**before scratch creation/native invocation**; the worker verifies the bound
context again before loading CAD. `ipc_install` requires the context and checks
before connecting to the editor. PCB/project/rules hashes, native geometry,
pad overrides, artwork, restrictions and reservations are bound together.

All proposed tracks/vias are checked jointly regardless of generation order:
manual trunks, A*, fanouts, endpoint legs and stitching. Analytic checks include
actual widths, per-layer via copper, outside-approximated native pad polygons,
fixed copper artwork, physical drills including rotated oval holes, board edges,
native zone restrictions and RF/F5/USB reservations. Copper and drill clearance
are separate. Legal same-net junctions pass; same-net hole spacing still applies.

The current V4 profile resolves project netclass clearance0.10mm, board
hole/edge/via constraints and pad overrides. Unknown custom rules or differing
netclass clearances fail closed; extend resolved per-net rules before using such
a project. This is a focused V4 checker, not a universal KiCad rule interpreter.
Refillable PGND copper is not a fixed obstacle: native refill generates antipads,
then DRC/plane review checks the actual fill. Native rule areas remain hard.

Duplicate same-net paths (also reversed/different-width paths) are flagged
against both existing and proposed tracks, and rejected before application.
Sub-0.2mm legs are flagged. `clean_microlegs` removes only uninstalled redundant
pad-internal legs or merges a corner after another full joint check. A necessary
short escape needs recorded evidence: the retained0.141mm BOOT chamfer avoids NC
pads. Partial/near-parallel overlaps and branch topology still need explicit
quality inspection; the exact-duplicate guard does not find every such case.

`review_bounds` is a local domain, at most30mm per axis. Use
`review_regions(plan)` to tile larger geometry. Each tile retains the same native
guard; oversized local requests fail offline before mutation. `layout-final`
contains `plane_tiles` with actual native0.1mm In1 fill and via-center/four-ring
samples. Tiling corrects the domain assumption without bypassing the guard.

## Planning and exact native equality

`f0_plan`, `route_plan`, `review` and `u3_review` read exported evidence only.
Custom bounded A* screens feasibility; it is not KiCad's interactive router.
Smoothing uses H/V/45 legs with exact endpoint offsets absorbed into adjacent
legs. Existing same-net vias/PTH pads are reusable transitions, never additional
drill sites. Default search layers are F/B; explicit `route_layers` may select
F/In2 for ordinary signals. In1 remains PGND. Through-via clearance always checks
all layers. USB plan generation is explicitly refused.

Plan schema (mm): `failure:null`,
`tracks:[[net,layer,width,x1,y1,x2,y2],...]`,
`vias:[[net,x,y,diameter,drill],...]`. New objects are straight tracks and circular
through-vias. Existing inventories retain actual layer-specific via widths.
Dispatch PCB_VIA before PCB_TRACK: vias require explicit `GetWidth(layer)`;
parameterless `GetWidth()` remains valid for tracks.

Scratch construction uses native `pcbnew.PCB_TRACK/PCB_VIA`; live installation
uses SDK `kipy.board_types.Track/Via`. No graphic substitutes, serialized patches
or offline replacement of an open board. Expected/actual inventories are retained
before comparisons after creation, save and reload. Equality uses exact integer
nanometres with the same conversion as native constructors; **no tolerance**.
One-nanometre or net changes fail. `snapshot --route-diagnostics` and
`scratch_diagnostic` preserve/compare raw geometry and padstacks from captured
evidence without mutating the diagnostic source.

## Production lifecycle

From this directory, run `python -B -m v4kicad.ipc_install preflight|apply` with
explicit board, accepted manifest, uninstalled plan, `--validation-context`,
fresh output root, socket, `--add-only` and narrow `--allowed-nets` whitelist.
Read-only preflight compares saved/live entry. Apply stages one bounded commit,
checks returned objects, pushes, reads visible objects, refills and saves through
the owning editor. It never substitutes a scratch file for the open board.

Then export independent native `snapshot --routing-context` against
`installed-manifest.json`; run `post_batch check` for production ERC/DRC/parity
and `post_batch full-add` against prior native and production evidence.
These check original geometry, full live artwork/models/fields/pads/placements/
zone definitions, exact additions, warning multisets and hashes. They write the
next `accepted-installed-baseline.json` and `remaining-by-net.json`.
Compare actual native fills with accepted scratch and review reference/contact.
Final read-only IPC preflight reconciles saved/live state. Scratch library-context
warnings must not be reported as production warnings.

`safety.run_monitored` captures logs, detects assertions/IPC failure even without
newline and stops only its child. **No retry, suppression, editor recovery,
restart/close or uncertain save.** Follow owner approval rules. Sandbox denial
before connection requires log inspection and the normal command approval
mechanism; it does not justify editor recovery.

Current mutation preflight deliberately accepts only fixed-placement add-only
plans. Historical Phase4.7 layer-change/Phase4.8 U3 placement flags and evidence
are not working examples for the current validator or authorization to replay
those changes. Legacy scripts under evidence are historical; reuse this package.

## Scratch-only legacy copper replacement

`replace` is deliberately separate from the add-only production installer. It
accepts a fresh scratch directory, exact accepted source/hash manifest, native
read-only context and an explicit `scratch-track-replacement` plan. The plan
enumerates 1..20 removed ordinary track UUIDs with their complete original
geometry, and <=30 replacement tracks on that same net/layer. Vias, placement,
rules and other CAD changes are refused. Each representative starts again from
the exact production baseline; candidates are never built upon failed scratches.

Use `kicad_v4.py replace` with the same explicit board/manifest/context/output/
native-python/kicad-cli/plan arguments as `validate`, omitting `--add-only` and
`--erc` (ERC is mandatory here). Run only within an owner-authorized scratch task.

Joint preflight removes only the enumerated originals from the obstacle export.
The monitored native worker independently matches originals, removes native
objects with `BOARD.Remove`, creates ordinary native tracks, checks exact nets/
integer geometry and every other original track/via/pad/footprint, saves and
reloads scratch, refills with native DRC, runs ERC/parity and verifies again.
Native pad-island traversal must match the baseline. Full native artwork/zone
audits and a separate **read-only** comparison of native-authored serialization
cover models, fields, locks, pad settings and board setup absent from snapshots.
Only enumerated route objects, top-level ordering, generator identity and
derived zone `filled_polygon` blocks are excluded from that comparison; zone
definitions and all unrelated contents remain checked. No serialization is edited.

`legacy_review` audits exported objects and records original/proposed UUIDs,
analytic copper-edge gaps (outside pad polygons, <=100nm approximation), width/
drill cross-sections, resistive scenarios, local sampled copper unions, actual
native fill equality and drill-aware reference probes. Width subtracts same-net
drills too. Reference stations deduplicate collinear segmentation and retain
native antipad holes. Areas/width scans and resistance scenarios do not establish
ampacity, electromagnetic response or thermal qualification. No new copper shape
is accepted just for looking regular. The existing production installer still
refuses original-copper replacements; there is no production `replace` action.

See [completed review and exact evidence](../evidence/legacy-routing-geometry-review-2026-10-17.md).

## Validation history

78 offline tests PASS (2026-10-17), including owner-review source guards, full
exported electrical-partition comparison and negative resistor-bypass/island-
split controls, disjoint collinear geometry, native-plane holes and connector
PTH barrel contributions. Fresh owner/control native review passed on isolated
KiCad10.0.7 copies; see the Phase4.11 completed review. No production migration
was performed. `phase411_analysis` and `usb_review` consume native exports only.

61 offline tests PASS (2026-10-17), including an exact new-via exclusion and
retained-via negative test for the read-only serialized comparator. Read-only
`audit` also exports native pad partitions. `probe` records actual USB pair
recognition when `BOARD.DpCoupledNet` is available. `phase410` and `handoff_review`
consume exports only for the bounded Phase4.10 plan and handoff diagnostics.

The prior60 include seven scratch-replacement/measurement
tests with negative original/net/layer/placement/via/field preservation cases,
edge-clearance, same-net drill width and segmentation-independent plane probes.
The previous53 include three immutable scratch5 collision negatives,
no-native rejection, legal stitching/junctions/layer crossings, holes, pad overrides,
reservations, duplicates, exact-nanometre/net equality, domain tiling, transition
reuse and explicit In2 routing. Offline tests do not establish native execution.
Separately, positive integration and all installed batches passed actual
KiCad10.0.7 creation/save/reload/refill, ERC/DRC/parity and preservation; see the
Phase4.9 report linked from the handover.

Standard Python suffices for guards/checks; route screening uses NumPy, rendering
Pillow. Native workers require matching installed KiCad Python/CLI. Imports must
not load CAD, launch processes or write files. These tools do not establish
signal integrity, thermal/RF performance or hardware qualification.
