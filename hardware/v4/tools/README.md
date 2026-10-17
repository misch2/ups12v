# V4 guarded KiCad 10 toolkit

Read `AGENTS.md` and [V4_HANDOVER.md](../V4_HANDOVER.md) first. Current Phase4.9
checkpoint: **STOP for owner review**. These examples do not authorize another
batch. Never replay an installed/failed plan or hand-edit serialized CAD.

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

## Validation and limits

53 offline tests PASS (2026-10-17): three immutable scratch5 collision negatives,
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
