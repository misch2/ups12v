# Phase 4.7 — focused PROG investigation; STOP for one-track proposal

2026-10-11. Owner accepted Batch 1 and prohibited further C23 exploration. **No production CAD changes.** C23 remains (71.5,66.3 mm)/90°. The conditional production-routing gate was not met.

## Combined routing result

Started from live/saved accepted Batch 1: 154 footprints,473 pads,252 tracks,138 vias,2 zones. Entry and final complete IPC captures equal `c9-apply-phase4-7-batch1-final-ipc.json` exactly; PCB/schematic/project SHA256 hashes also remain identical. KiCad10.0.7; Konnect reported `source:ipc`. Initial local-socket permission denial was sandbox access, resolved by the authorized outside-sandbox read-only snapshot; no IPC instability/native assertion observed.

Reused the native custom-pad polygons and **all original verified BATP/PGND/ILIM_HIZ/TS scratch geometry**, including the PGND via(71.5,65.525), unchanged. A0.10mm PROG trace search at0.025mm and then0.010mm grid spacing finds no F.Cu exit to R5.1 and no legal0.50/0.30mm through-via in the connected F.Cu region. Fine-grid region bounds(58.49,64.60)–(63.31,67.51)mm;22143 reachable F.Cu nodes,0 reachable B.Cu nodes,0 legal via sites. Copper clearance0.10mm and copper-to-hole clearance0.25mm remain unchanged. This is a bounded search, not exhaustive continuous-geometric impossibility proof.

Alternative route orders can connect PROG entirely on F.Cu but block BATP or ILIM_HIZ; farther BATP transitions also fail to produce the combined subset. They are failed candidates, never production geometry. No compliant combined candidate was established, so no other production routing batches followed.

## Smallest specific change found — PROPOSED only

**One existing BATTERY track changes copper layer; no position, width, length, endpoint, via, component, rule or PGND-plane change is proposed.**

| Object | Existing | Proposed |
|---|---|---|
| Track UUID `01ab1eb5-ab75-462d-9e54-2d6eab529481` | BATTERY,F.Cu,0.60mm wide,(63.1,65.5)→(63.8,66.9)mm;1.56525mm long | Same BATTERY net,geometry,width and endpoints; **In2.Cu** |
| Endpoint via `e012a565-4061-4615-bf98-9d4d2d4121a8` | BATTERY,(63.1,65.5),Ø0.70/0.40mm,through | Retain unchanged |
| Endpoint via `10f4a91e-df97-47f0-ba3d-640a866ac795` | BATTERY,(63.8,66.9),Ø0.70/0.40mm,through | Retain unchanged |

Both endpoints already have BATTERY through-vias, so the layer-change proposal does not require new holes. An obstacle-only numerical model retaining this segment on In2.Cu permits a **0.10mm entirely F.Cu PROG path,34 segments,28.65188mm,zero PROG vias**, together with the exact original scratch subset. This long path is a feasibility candidate, not optimized or hardware-qualified routing. The obstacle model changed no CAD object/file. It does not establish native DRC compliance of the proposed In2 segment or its electrical suitability.

Electrical consequences: BATTERY connectivity and conductor plan-view dimensions stay the same, but current redistribution and thermal conditions change. The outer-layer parallel path becomes an internal-layer path using the existing endpoint via barrels. Existing In2 BATTERY copper is retained:0.40mm feed(63.1,64.8)→(63.1,66.9),0.70mm link(63.1,66.9)→(63.8,66.9),and1.50mm continuation(63.8,66.9)→(64.5,67.6). Trace/via current sharing and inner-layer thermal suitability need explicit electrical review; no ampacity, temperature or noise performance is claimed. The proposed segment may overlap same-net copper; native clearance, refill and connectivity verification are still required. The long PROG path near power copper also merits review. No component/BOM/firmware changes.

## Independent native obstruction check

Saved a separate diagnostic scratch board from accepted production with **every original production object retained**, adding only the original successful subset and the modeled full-F.Cu PROG route. **The BATTERY layer change was NOT applied, even to this diagnostic board.**

Native KiCad CLI DRC with schematic parity: **251unconnected /1other error /20library-context warnings /0parity issues**. The sole other error is `tracks_crossing`: the exact BATTERY track above crosses the proposed PROG F.Cu segment(62.54,65.94)→(64.92,66.26)mm. No additional custom-pad, copper-clearance or copper-to-hole errors were reported. Diagnostic board310tracks/139vias includes all four previous routes. It is deliberately invalid and must not be transferred to production. CLI emitted sandbox registry-access messages but completed and wrote the report; library warnings remain context limitations.

This independently localizes one actual existing-copper obstruction. It **does not** convert the unapplied layer-change proposal into a DRC-clean solution. Separate owner approval is required before testing that existing-copper change in CAD, followed by native DRC, electrical review and the required production gate.

## Evidence and stop boundary

- Original combined-context search: `phase4-7-prog-focused-0.1-0.01-PROG-obstruction.json`; matching `...-plan.json` and `...-via-blockers.json`.
- Numerical one-track layer-change model/full-F.Cu plan: `phase4-7-prog-focused-0.1-0.01-omit-01ab1eb5-layer-model-front-only-plan.json`.
- Native diagnostic: `phase4-7-prog-focused-diagnostic.kicad_pcb` and `phase4-7-prog-focused-diagnostic-drc.json`.
- Preservation: `c9-apply-phase4-7-prog-focused-entry-ipc.json`, `c9-apply-phase4-7-prog-focused-stop-ipc.json`, `phase4-7-prog-focused-final-preservation.json`.

**STOP.** Production remains accepted Batch1, with retained production DRC257unconnected/0other errors/16warnings/0parity and ERC0errors/4warnings. These production checks were not rerun; no production mutation/refill/save required them. No schematic changes. No further C23 work, held-copper change, unrelated routing,fabrication,purchasing,firmware,commit or push.
