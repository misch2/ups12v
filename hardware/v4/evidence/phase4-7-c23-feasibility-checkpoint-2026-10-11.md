# Phase 4.7 — conditional C23 routing test FAILED; production Batch 1 retained

2026-10-11. Owner accepted Batch 1 and conditionally authorized C23 (63.0,67.6 mm),90 degrees, only after a practical clearance-compliant scratch routing test. **No joint BATP/PGND solution was established. STOP; C23 relocation and further production routing were not applied.** This rejects the tested candidate, not a proof that every possible topology is impossible.

## Baseline and preservation

Exact production project confirmed open through Konnect IPC. Fresh assertion-safe protobuf capture `c9-apply-phase4-7-c23-feasibility-entry-ipc.json` exactly equals accepted `c9-apply-phase4-7-batch1-final-ipc.json`, including all objects and saved hashes: **154 footprints /473 pads /252 tracks /138 vias /2 zones**. Scratch native board loaded from this latest saved production board, not a pre-routing baseline. C23 alone moved in scratch to (63.0,67.6),90 degrees; save/reload verified. Production PCB/schematic/project SHA256 still equal the accepted checkpoint after the scratch test. No production mutation, save, refill, installation, identifier repair or copper deletion occurred. C23 remains (71.5,66.3),90 degrees. All production power/switching copper, custom pads, vias, NT1/NT2, C9 and PGND plane consequently remain unchanged.

## Practical candidate and obstacle

Native KiCad10.0.7 exported actual pad copper contours, including IC1 custom pads. Offline candidate search used these polygons and all current Batch 1 IPC tracks/vias, F.Cu/B.Cu paths,0.025 mm grid,0.15 mm tracks,0.50/0.30 mm through-vias,0.101 mm planning clearance. Existing netclass clearance remains0.10 mm; minimum via diameter/drill remains0.50/0.30 mm. No rule changes.

- BATP-first found IC1.18→C23.1→R4.1 F.Cu paths, but no PGND escape using the modeled existing geometry and minimum vias.
- PGND-first found C23.2→the existing PGND plane via at (61.9,69.1) on F.Cu, but then no BATP escape. Neither candidate required deleting existing copper.
- Both independently found corridors were physically added together to a **scratch-only diagnostic board**, deliberately exposing their incompatibility to KiCad's full DRC rather than calling either a completed solution. No new via was placed in this combined trial. Native save/reload completed; scratch analysis-only refill/DRC found **254 unconnected /13 other errors /20 warnings**. Concrete result: BATP/PGND tracks cross around **(62.575,67.500)**, with shorting and multiple violations below0.10 mm. Full report: `phase4-7-c23-feasibility-drc.json`. Scratch library-context warnings and unavailable schematic parity are disclosed; neither is used to excuse copper errors.

The C23 return and BATP escape compete for the west-side pocket between IC1 and C23. A PGND via directly on proposed C23.2 would overlap existing In2 BATTERY copper: the0.50 mm via's calculated copper overlap is approximately0.358 mm against the0.70 mm BATTERY segment from (63.1,66.9) to (63.8,66.9). This is an offline geometric check, not an actually placed/tested via. It explains why a visually convenient top-layer return site cannot simply be used. No alternate location was forced through existing copper.

## Clearance checks and limitations

Native polygon distance from C23 PGND pad2 to the actual0.70 mm BATTERY via at (63.8,66.9) is approximately **0.144981 mm**, versus0.10 mm required; native polygon approximation error at most0.0001 mm. The nearest preserved F.Cu BATTERY track is approximately0.159191 mm away. **IC1/C23 courtyard separation remains0.09 mm**, consistent with the accepted placement-only trial and absence of a courtyard-overlap finding. Placement clearance alone therefore does not resolve the routing conflict.

**ILIM_HIZ, TS and PROG simultaneous escape feasibility was not established**: the required BATP/PGND pair failed first. The candidate search is limited to two signal layers and through-vias and is not exhaustive. No claim that all possible placements or routing strategies fail is made. No narrower traces, altered clearance rules, component moves, existing copper changes or other scope expansion was attempted. No unexpected native assertion or IPC instability occurred; the first sandbox-only IPC permission denial was resolved by the approved read-only elevated snapshot.

## Remaining production routing and STOP

Production remains the accepted Batch 1 checkpoint: DRC257 unconnected/0 other errors/16 existing warnings/0 parity; ERC0 errors/4 existing warnings. These are **retained Batch 1 results**, not rerun after the scratch failure. No production implementation occurred, so no production refill/save or dependent checks were issued after the failed feasibility gate.

Affected remaining DRC records: REGN4,ILIM_HIZ1,TS3,BATP2,PROG1,CE_N3,CE_BIAS2,GND1(J6 deferred),/CHG_GATE1(Q5 deferred). R4 BATTERY sense feed/C23 PGND return still open; ACDRV1/BTST1/BTST2/SDRV remain complete. All previously deferred branches remain deferred.

Evidence: `phase4-7-c23-feasibility-summary.json`, `phase4-7-c23-feasibility-pad-polygons.json`, both routing-order plans, combined diagnostic plan, native scratch board, full DRC and the three reproducible helper scripts. No firmware, fabrication, purchase, commit or push. **Phase 4.7 remains incomplete. Owner review of this obstacle is the next boundary; no additional CAD action authorized by this failed trial is taken.**
