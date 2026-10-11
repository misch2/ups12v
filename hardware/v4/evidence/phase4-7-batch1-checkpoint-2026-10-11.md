# Phase 4.7 — verified first routing batch; C23 approval requested

2026-10-11. Owner approved bounded local auxiliary/control routing, with separate approval required before moving C23. **First independent batch is applied, refilled, saved and verified. BATP is not routed; C23 remains at its original position. STOP for owner review of the placement proposal before committing adjacent charger fanout.** Remaining approved local routing is explicitly incomplete.

## C23 placement assessment — proposal only

Recommend C23 centre **(63.0,67.6mm),90degrees**, retaining the original orientation, value **47nF/25V**, footprint and pad nets. Original centre(71.5,66.3),90degrees. Proposed BATP pad1(63,68.08) is **1.704mm** from IC1.18(61.875,66.8), versus9.625mm at present (~82% shorter). Proposed PGND pad2(63,67.12).

Only C23 was moved on a separate native KiCad10.0.7 scratch board, saved/reloaded through supported APIs; no via-width getter, library refresh, custom-pad replacement or production CAD overwrite. Full scratch DRC with analysis-only refill:262unconnected/0other errors/20warnings. Scratch warnings include unavailable project-local library context; parity is **unavailable** because the scratch board has no matching root schematic. No geometry violation was suppressed. Production schematic/project unchanged. [Scratch DRC](phase4-7-c23-placement-trial-drc.json), [trial script](phase4_7_c23_trial.py), [diagnostic detail](phase4-7-c23-proposal-detail.png).

The candidate fits between IC1, NT2 and existing BATTERY/bootstrap vias. IC1 courtyard endsX62.45; C23 courtyard beginsX62.54 (0.09mm positive separation). Its PGND pad bounding box endsX63.31, leaving approximately0.14mm to the BATTERY via copper at(63.8,66.9),diameter0.7mm; complete scratch DRC is the authoritative clearance check. Diagnostic image omits traces and uses bounding boxes, not custom-pad contours. Existing power copper, vias and unrelated placement were not moved for this trial. This validates placement against the current geometry; it does not validate a completed BATP/PROG/ILIM/TS routing solution in that pocket.

C23 movement and its BATP/PGND connections remain pending separate owner approval. No automatic identifier normalization or repair was performed. The remaining IC1 fanout is adjacent to this decision; a conservative offline corridor planner did not establish a route while reserving the entire proposed courtyard. This is a planner limitation, not proof that routing is impossible or authorization to change existing copper. Rather than commit interacting escapes prematurely, stop at the verified independent batch. No additional movement, copper deletion or netclass change is requested.

## Applied independent batch

Exactly **12 new tracks /4 new through-vias**, defined in `phase4-7-batch1-plan.json` and applied through Konnect, sequentially:

- R5.2→NT1.1 and R7.1→NT1.1 on GND. Short F.Cu land connections, two0.5/0.3mm signal vias and a0.2mm B.Cu branch south of the charger. NT1 remains the sole intended tie to PGND; J6 is untouched.
- Q3.1→R10.1 on `/CHG_GATE`,0.2mm F.Cu. Q5 collector/host circuitry untouched.
- Q3.2→PGND via at(77.8,62.3),0.7/0.3mm; R10.2→PGND via at(79.8,69.8),0.7/0.3mm. F.Cu returns0.3mm. R10 return is longer than a direct adjacent via because the large In2 BATTERY trunk precludes the initially considered local via sites. It runs around the outside of R11 and avoids the power trunk; no trunk change or replacement geometry.

Initial scratch routes were rejected for via diameter construction/clearance findings. The supported native SetWidth overload was inspected (layer argument precedes width in the two-argument setter), scratch via widths corrected on all four copper layers, and via sites changed to avoid the existing In2 power trunk. No KiCad assertion or unexpected IPC error occurred. Revised scratch batch passed with257unconnected/0other errors before production application. Scratch failures never entered the live board. [Final scratch report](phase4-7-batch1-trial-drc.json).

The production operation log is `phase4-7-batch1-konnect-log.json`. Independent kipy protobuf readback proved all pre-existing footprints/pads/tracks/vias/zones/shapes/texts identical before refill; new net/layer/width/endpoints/via dimensions match the plan. Two trace endpoints were quantized by1nm by the served API; recorded comparison tolerance1.1nm, maximum observed delta1nm. No existing identifier or geometry was normalized to make the check pass. [Pre-refill readback comparison](phase4-7-batch1-live-preservation.json).

## Saved verification and preservation

- Konnect synchronized DRC: **257unconnected /0other errors /16existing library-footprint warnings /0schematic parity findings**. `live_board_synced=true`, persisted IPC refill, save verification completed. [DRC](phase4-7-batch1-final-drc.json).
- ERC: **0errors /4unchanged isolated-label warnings**. [ERC](phase4-7-batch1-final-erc.json).
- Final saved/live capture:154footprints/473pads/**252tracks/138vias**/2zones. Final PCB/schematic/project hashes match the final capture; schematic/project hashes match entry. [Final live snapshot](c9-apply-phase4-7-batch1-final-ipc.json).
- All retained footprints/pads/copper/board shapes/text are byte-for-byte equal as captured protobuf objects. Zone definitions/settings unchanged; antenna zone and fill unchanged. Only PGND filled polygons changed during refill; PGND remains one filled polygon. No claim of extracted return impedance or measured noise is made. C9 remains(61.1,69.1),0degrees; C23 remains(71.5,66.3),90degrees. Nano-Fit geometry/artwork, power/switching routes, custom pads, NT1/NT2 and plane outline preserved. [Preservation and remaining-net counts](phase4-7-batch1-final-preservation.json).

## Remaining connections per affected net

Counts are KiCad DRC missing-connection records, not prescribed topology or an exact track count.

| Net | Remaining records | Status |
|---|---:|---|
| REGN |4| Local NT2/R6/D3 branches not yet applied; R8 remains deferred |
| ILIM_HIZ |1| IC1→NT2 not yet applied |
| TS |3| Local IC1/R6/R7 not yet applied; J6 deferred |
| BATP |2| Entire sense routing held for C23 decision |
| PROG |1| IC1→R5 not yet applied; R5 ground return complete |
| CE_N |3| Not yet applied |
| CE_BIAS |2| Not yet applied; D4 MAIN_3V3 supply remains deferred |
| GND |1| Local R5/R7→NT1 complete; only J6 deferred |
| /CHG_GATE |1| Q3→R10 complete; only Q5 deferred |
| ACDRV1/BTST1/BTST2/SDRV |0 each| Preserved, no changes |

R4.2 BATTERY sense feed and C23.2 PGND return also remain unconnected and held with BATP. Q3/R10 PGND returns are complete. General-board total fell262→257. No remote branch, U3/U7/F5 routing, firmware, fabrication, purchasing, commit or push was performed. The full approved Phase4.7 scope is **not complete**.

**Owner decision requested:** approve or reject C23(63.0,67.6),90degrees. This proposal does not ask to move any other component or alter existing power copper. Following that decision, resume the remaining approved local routing with the same small-batch verification and first-assertion stop rule.
