# Phase4.7 charger sensing checkpoint — complete; STOP

2026-10-16. Owner accepted the saved/live 376-track/143-via checkpoint (PCB SHA256 `05fd52862efd2ee0da74f225192fd8e0ee27cfc94545d7d2543fbb8a1237c930`) and authorized only remaining TS/R7/J6/GND and REGN/R8 routing. No earlier routing was replayed.

## Entry authority and exact connectivity

Fresh isolated native snapshot: `../phase4-7-sense-entry-native/snapshot.json`. Exact-path Konnect confirmed IPC available, requested board open and one board. Full native IPC preflight matched the accepted baseline, normalizing only established runtime IDs/inactive circle-anchor metadata. Saved schematic/project hashes remained authoritative.

Current schematic export: `../phase4-7-sense-current.xml` (native kicadxml). Konnect's earlier `phase4-7-sense-current.net.xml` is actually its kicadsexpr format, despite extension; it was not parsed as XML or used as authoritative XML evidence. Current schematic connections:

- TS: IC1.16, R6.2, R7.2, J6.2.
- GND: R5.2, R7.1, NT1.1, J6.1.
- REGN: IC1.5, C3.1, NT2.2, R6.1, D3.2, R8.1.
- ILIM_HIZ: IC1.17, NT2.1. NT1.2 is PGND.

Every exported schematic pin/net mapping represented by a PCB pad matches the final native snapshot; independent production schematic parity is zero. No topology or component/BOM change.

## Completed small batches

| Batch | Installed geometry | Production validation |
|---|---|---|
| Local TS and R8 REGN | 3 TS tracks /2 through-vias;11 REGN F.Cu tracks. TS R6.2→R7.2 adds8.118864mm; REGN C3.1→R8.1 adds21.341845mm |390tracks/145vias;241unconnected/0physical errors/16warnings/0parity;ERC0errors/4warnings|
| J6 TS/GND |7 TS and8 GND F.Cu tracks,0vias. R7.2→J6.2 adds46.164664mm; existing R7.1 branch→J6.1 adds49.582558mm |405tracks/145vias;239unconnected/0physical errors/16warnings/0parity;ERC0errors/4warnings|

TS width0.15mm; REGN/GND0.20mm. Local TS through-vias Ø0.50/0.30mm at(71.3,70.05) and(77.85,71.5875), outside R7's solder pad. Their actual per-layer widths/drills were independently verified. A redundant12.5µm TS segment from the raster screen was removed before final scratch validation and production installation. Local B.Cu TS length6.728031mm; remaining local TS is F.Cu.

Plans: `../phase4-7-sense-batch1-final-plan.json`, `../phase4-7-sense-j6-final-plan.json`; cumulative exact additions: `cumulative-plan.json`. Each batch used a fresh scratch project with native save/reload/refill/DRC/parity/ERC, then fresh live preflight, one native undo transaction, returned geometry verification, push_commit, visible geometry verification, refill and save through the owning editor. Production was never overwritten by an external scratch save. Independent saved native snapshots and production checks completed before continuation.

Scratch warnings (20DRC/11ERC) include missing scratch-library context; they are not production warnings. Production remained16 identical library mismatch warnings and4 known ERC warnings, with unchanged ignored-rule list. Failed scratch direct/pair proposals contained actual pad/crossing collisions; these were investigated and avoided without editing existing copper or placement. They remain under `../phase4-7-sense-j6-scratch/` and `../phase4-7-sense-j6-paired-scratch/`.

## Quiet routing and reference limits

The remote TS/GND pair stays entirely on F.Cu, leaves the analog cluster to its east, runs together through an open corridor, skirts west of L3/U7 and approaches J6 from below. Most of the long corridor has0.5mm horizontal centreline offset (about0.35mm perpendicular on the diagonal); ground is a dedicated GND return to NT1, not a new direct PGND connection. The route avoids SW1/SW2/BTST1/BTST2 and does not follow switching traces. It also avoids L3's /F5_SW pad even though F5 routing remains deferred. The actual saved render was inspected: `../phase4-7-sense-j6-final-front.png`.

The existing In1 PGND zone remains one exported filled contour after refill. This export does not establish full hole topology or field-solver reference continuity. The companion GND reduces the remote loop area, but no noise-immunity measurement is claimed. Local TS crosses the dense analog/control corridor on B.Cu for6.728mm; B.Cu has less assured adjacent plane reference than F.Cu. Existing local IC1 TS escape and all charger switching/decoupling routes are preserved. Remote TS length and local bottom reference are prototype validation limits, not new acceptance thresholds or measured failures. Earlier electrical/BATTERY/PROG qualifications remain open.

## Final authority and preservation

Final **405tracks/145vias/154footprints/473pads**. `native-preservation.json` verifies all original native geometry and exact29tracks/2vias additions. `live-preservation.json` verifies every original IPC footprint/pad/track/via/shape/text and zone definition; only filled polygons changed. `accepted-to-final.diff` retains the bounded saved-CAD diff; removed content is recalculated fill vertices only. NT1/NT2 and every original power/charger route are preserved. No rule, netclass, placement, library or BOM edits.

Final production reports are `production-drc.json` / `production-erc.json`; actual remaining endpoints in `remaining-by-net.json`. TS/REGN/GND/ILIM_HIZ/CE_N/CE_BIAS each0; PGND86unchanged. Whole board still has239unconnected entries and is not released for fabrication.

Saved SHA256:

- PCB `8c2f16ff54b803f7c52b2b9084153f2f7c09f88403edd7643f6d7010f1cf5379`.
- Schematic `990d107296d149775884dc2d2512c2e6102b6191e4818e7fcf5bd9268d48c8f6` unchanged.
- Project `477e5c47219922b25619e9db0748961ed83af3958866842e0a34ad1d1641a21e` unchanged.

Future checkpoint baseline is `accepted-candidate-baseline.json` (final capture/hashes, pending owner review). The toolkit was reused without code edits.19regression tests passed outside the sandbox. Initial sandbox IPC GetVersion Permission denied stopped only its read-only worker; log established no CAD mutation, and explicit approval preceded the fresh host preflight. No real native assertion, automatic editor recovery or uncertain production write occurred.

**STOP at completed checkpoint for owner review.** D4 MAIN_3V3, Q5/host control, MCU/I2C/INT, U3/U7/F5 and unrelated routing remain deferred. No fabrication,purchasing,power-up,firmware,commit/push. Recommend a fresh session for the next separately authorized milestone.
