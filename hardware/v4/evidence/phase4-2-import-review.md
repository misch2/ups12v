# Phase 4.2 — native PCB import verification

2026-10-10. Owner performed native KiCad 10 F8 import and four-layer Board Setup. This checkpoint is read-only CAD verification: no save, import, library refresh, placement, routing, zones or rule changes by the agent. Existing local files preserved.

## Source binding and inventory

Konnect `open_project` confirmed `ipc_available=true`, `requested_open=true` and exact document `C:/Users/Michal/Git/my/ups12v/hardware/v4/ups_v4/ups12v_v4.kicad_pcb`, matching `ups12v_v4.kicad_pro` in the same directory. Inventory, all 152 per-reference pad queries and copper-layer readback came from live IPC. Physical stackup also reports four copper layers: F.Cu, In1.Cu, In2.Cu, B.Cu. Signal/power layer-type metadata is saved-file backed; a layer type is not proof of a ground plane.

Live board: **152 footprints, 102 nets, 461 physical pad entries**. Approved Phase 3.7 XML: **152 components, 102 nets, 439 exported pin entries**. Every exported pin is present and all duplicate physical pads carrying its number have the expected net. No missing/extra references, value/footprint identity differences, missing numbered pads, net mismatches or extra connected numbered pads found. Saved/live pad-number/net multisets agree for all references. Saved pad geometry matches all 37 current library definitions across 152 footprints after semantic normalization of layer order, pad order, numeric formatting and omitted zero pad angle.

The schematic SHA256 remains `16fbf0aa5000f4b312559aa22c4c59705b9ed9f2a34af95d4009dfc8d4ce4cb2`, binding the approved XML to the unchanged schematic. Full hashes and results are in `phase4-2-verification.json`; reproduction: `python hardware/v4/evidence/verify_phase4_2.py` (CAD read-only, writes evidence only).

## Critical mappings and geometry

- IC1: original `Package_DFN_QFN:Texas_RQM0029A_VQFN-29_4x4mm_P0.4mm`, 29 physical/unique numbered pads; **1,9,16,24 remain custom** in both live readback and saved board. Saved custom options/primitives match the current TI library exactly; no rectangular approximation. All pin/net assignments match the approved shared BQ25792/BQ25798 map. This verifies import preservation, not new manufacturer land qualification.
- U1 ESP32-C3-MINI-1-N4X: 61 physical pads/53 unique numbers; all pad geometry and nets preserved, including duplicated ground lands.
- F1: custom Littelfuse 451 footprint preserved; two pads at +/-2.4511 mm, 1.9558 x 3.1496 mm, matching the accepted local library.
- Q10 AON7528: nine numbered pads, source 1–3 to F5_RAW, gate 4 to F5_GATE, drain 5–9 to F5_5V_OUT. Geometry matches the existing library; inherited missing courtyard remains open. Q1/Q2 likewise match their library but lack courtyards.
- All connectors, U7/U8 and F5 passives have the approved references, footprint IDs, pads and nets. All **19 F5-only fitted references** from the accepted population CSV exist on this single board; F0 is still the DNP population, not another board.
- TP5/TP6/TP7 remain ESP_TX/ESP_RX/PGND. All nine Phase 3.7 copper-only testpads retain 1.5 mm footprints without paste. Removed TP9–TP12 are absent. Final UART pitch, board-edge access, orientation and probe segregation are placement tasks, not satisfied by native-import staging coordinates.

## Initial DRC and parity

KiCad DRC inspected the **saved board**, with `sync_live_board=false` and `refill_zones=false`; no editor save or refill performed. **0 schematic-parity findings**. The DRC counts 342 errors comprising:

| Findings | Count | Interpretation |
| --- | ---: | --- |
| Unconnected items | 337 | Expected for completely unrouted import; not import/pad-map errors. |
| Missing Edge.Cuts outline | 1 | Expected incomplete mechanical definition at this checkpoint; required before later design completion. |
| J7 internal hole clearance | 4 | Real footprint-versus-project constraint conflict, not explained by unrouted state. |

J7 ground pads A1/B12 and A12/B1 lie 0.1944 mm from its own locating NPTH holes against the current 0.2500 mm board constraint. Tool ownership resolves both items in each violation to **J7**; moving the footprint cannot fix this internal relationship. Preserve geometry and constraints for review; later resolve against the exact connector drawing and fabrication capability without silently weakening rules or distorting lands. No other design-rule findings or parity discrepancies were reported in this run; this is not fabrication approval.

Courtyard readback flags Q1/Q2/Q10 and C20/C22 as absent; NT1/NT2/NT4 also have no courtyard, to be assessed by their net-tie purpose rather than blindly adding one. These are existing library completeness issues and were not reported as DRC violations in the current run. Connector/harness/NTC physical choices remain provisional as already documented; matching an inherited footprint does not settle those choices.

## Limits and retained gates

Saved board has **0 tracks/arcs, 0 vias and 0 zones**. Continuous PGND reference without a moat and without significant return current through NT1 remains the approved future strategy, not implemented copper. NT1 remains pad1 GND/pad2 PGND in the import. No current-flow or thermal claim is made.

Konnect exposes live pad shape/size/layers/nets but not complete custom polygon primitives. Therefore primitive-level comparison uses read-only saved-board/current-library parsing as a last resort; it does not prove absence of arbitrary unsaved polygon edits. Live shape readback independently confirms the four custom pad identities. DRC likewise excludes unsaved geometry. No native GUI screenshot was taken; saved SVG is `phase4-2-imported-board.svg`.

No CAD/BOM changes: C67/C68 remain their approved imported 100 nF values; the separate recommendation is not implemented in this import-only task. Firmware/hardware tests, staging, commits and pushes not performed. Fresh schematic ERC was unnecessary because the schematic is unchanged; Phase 4.1 evidence remains 0 errors/4 unchanged warnings.

**Import/reference/pad-net verification passes; overall DRC is not clean.** Stop after this verification. VAC1 hot-plug fabrication/power-up gate and BQ25792 2S default 2 A current risk remain unresolved. Placement/routing and fabrication remain unauthorized.

Evidence: `phase4-2-live-readback.json`, `phase4-2-library-readback.json`, `phase4-2-check-sources.json`, `phase4-2-verification.json`, `phase4-2-drc.json`, `phase4-2-imported-board.svg`.
