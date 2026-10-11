# Phase 4.7 — 270° C23 test failed; original-position fallback blocked at PROG

2026-10-11. Owner authorized one additional C23 placement candidate: centre(63.0,67.6 mm),270°. If unsuccessful, abandon near-IC1 relocation, keep the original C23 placement, continue bounded local routing and stop if an actual obstruction requires changes outside the approved scope. **No production changes were applied. Accepted Batch 1 remains authoritative. Phase4.7 is incomplete.**

## Entry and final production preservation

Konnect confirmed exact production PCB/project open with IPC available. Fresh protobuf entry capture `c9-apply-phase4-7-c23-270-entry-ipc.json` exactly equals accepted `c9-apply-phase4-7-batch1-final-ipc.json`. All scratch work started from the latest saved **252tracks/138vias** board. Final live capture `c9-apply-phase4-7-c23-270-stop-ipc.json` again exactly equals accepted Batch1 for footprints,pads,tracks,vias,zones,shapes,text and saved PCB/schematic/project hashes. Counts remain154footprints/473pads/252tracks/138vias/2zones; C23 remains(71.5,66.3),90°. Existing power/switching copper, custom pads, vias, NT1/NT2, C9, PGND zone/fill, antenna keepout, placement, netclasses and net assignments are unchanged. [Final preservation summary](phase4-7-c23-270-final-preservation.json).

Native KiCad10.0.7 APIs loaded/saved/reloaded scratch boards only. Konnect/native CLI performed complete configured DRC with analysis-only refill; production was never refilled, saved, replaced or synchronized from scratch. Matching copies of the unchanged root schematic/project enabled actual scratch parity checking. Scratch library-context warnings are disclosed separately. No assertion, unexpected IPC failure or recovery occurred.

## Single 270° candidate

Native rotation readback is−90°, equivalent to270°. C23 electrical identities retained: BATP pad1 at(63.0,67.12), PGND pad2 at(63.0,68.08). Native custom-pad polygons were exported and used rather than pad bounding boxes.

Actual scratch routing included:

- IC1.18→C23.1→R4.1, F.Cu0.15 mm; the pin-to-cap path is approximately1.17 mm. No change to R4 or existing BATTERY copper.
- A distinct PGND0.50/0.30 mm through-via at C23.2(63.0,68.08), accounting for the existing In2 BATTERY trunk, NT2 and nearby vias.
- Actual ILIM_HIZ IC1.17→NT2.1 and TS IC1.16→R6.2 routes, with all preceding candidate copper retained.
- A diagnostic PROG escape from IC1.20 to an attempted0.50/0.30 mm via at(62.475,65.800). The bounded path search could not connect PROG to R5; this attempted via was added only to obtain concrete native rule findings, never as an accepted solution.

Complete native scratch DRC: **252unconnected/12other errors/21warnings/0parity findings**. All12 errors involve PROG; no copper error was reported against the candidate BATP/PGND/ILIM_HIZ/TS routes. PROG is therefore the failed complete-candidate gate, not a claim that the rotated capacitor itself shorts BATTERY. [Full 270° DRC](phase4-7-c23-270-drc.json), [diagnostic plan](phase4-7-c23-270-plan.json).

**The 270° candidate was not applied. Near-IC1 C23 relocation is abandoned for this milestone; no additional C23 position/orientation exploration was made or is proposed.**

## Original-position fallback routing

A fresh scratch board retained C23 at(71.5,66.3),90°, and every other production placement/copper item. A native DRC rejected an initial PGND via directly on C23.2 because it intersected the existing3 mm In2 BATTERY trunk. That rejected trial never entered production; no trunk was altered. The replacement scratch return uses a0.50/0.30 mm PGND via at **(71.5,65.525)**, reached by **0.305 mm** F.Cu copper.

The fallback subset physically routes BATP IC1.18→C23.1→R4.1, ILIM_HIZ IC1.17→NT2.1, TS IC1.16→R6.2 and C23 PGND. BATP uses approximately **14.166 mm total F.Cu route** (pin-to-cap plus cap-to-R4), with no BATP via and no existing switching copper modification. This is a short path found under the retained geometry, not a globally optimal-length or measured-noise claim.

Complete native DRC of this **partial fallback subset**: **252unconnected/0other errors/20library-context warnings/0parity findings**. Scratch only:24new tracks/1new via. [Partial clean subset DRC](phase4-7-original-partial-clean-drc.json), [matching plan](phase4-7-original-partial-clean-plan.json), [matching saved board](phase4-7-original-partial-clean.kicad_pcb). This is not a complete Phase4.7 solution and was not installed in production.

## Actual stopping obstacle — IC1.20 PROG escape

With original C23 placement restored, the bounded native-contour path search still could not connect IC1.20 to R5. It accounts for0.10 mm net clearance,0.25 mm copper-to-hole clearance,0.50/0.30 mm minimum through-vias and all existing copper layers when choosing via sites. Its connected F.Cu region has1121 grid nodes at0.025 mm spacing, **zero feasible via sites**, and zero reachable B.Cu nodes. [Search evidence](phase4-7-original-PROG-obstruction.json). Grid analysis is not exhaustive proof over every continuous routing strategy.

Native DRC of a concrete PROG escape attempt on the **original-position** fallback board confirms the physical conflicts, independently of C23 relocation:

| Conflict | Actual | Required |
|---|---:|---:|
| PROG via(62.475,65.8)→existing B.Cu SW2 track at X61.8 |0.0324 mm copper clearance|0.1000 mm|
| PROG via→BATTERY via(63.1,65.5)|0.0933 mm copper clearance|0.1000 mm|
| PROG via→IC1.21(~INT)|0.0579 mm copper clearance|0.1000 mm|
| PROG via→BTST2 via(62.5,66.4)|0.2005 mm copper-to-hole clearance|0.2500 mm|
| PROG via→existing B.Cu BTST2 trace|0.2007 mm copper-to-hole clearance|0.2500 mm|

The diagnostic original-position board reports **252unconnected/12other errors/21warnings/0parity findings**; every other error is PROG-related. [Full original-position obstruction DRC](phase4-7-original-prog-obstruction-drc.json), [matching diagnostic plan](phase4-7-original-prog-obstruction-plan.json), [matching board](phase4-7-original-trial.kicad_pcb).

**STOP at this obstruction before any production batch.** No compliant PROG escape has been established with the held power/switching copper and rules. Editing SW2/BATTERY/BTST2 copper or changing sizes/clearances to rescue the tested escape is outside scope; none was done. This is not a proof that every conceivable alternative is impossible, and no power-copper change is automatically recommended or authorized.

## Remaining state and validation limits

Production remains accepted Batch1: retained DRC257unconnected/0other errors/16existing warnings/0parity; retained ERC0errors/4existing warnings. No production batch was implemented, so no production refill/save/DRC/ERC was issued after the failed scratch tests. These retained results are not represented as new checks. Final live readback and saved hashes prove production preservation.

Remaining affected production records: REGN4,ILIM_HIZ1,TS3,BATP2,PROG1,CE_N3,CE_BIAS2,GND1(J6 deferred),/CHG_GATE1(Q5 deferred). R4 BATTERY sense feed/C23 PGND return remain open in production. ACDRV1/BTST1/BTST2/SDRV remain complete and preserved. No remaining independent REGN/CE batches were applied after encountering the PROG stop boundary. Previously deferred branches remain deferred. No fabrication,purchase,firmware,commit or push.
