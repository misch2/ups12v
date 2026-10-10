# Phase 4.1 — board initialization/import attempt (incomplete)

2026-10-10. Owner authorized board initialization and import verification only. No placement, routing, zones, fabrication or purchasing authorized or performed. Existing local project/PCB edits and earlier documentation preserved.

## Exact state

Konnect confirmed IPC available and the exact open PCB `C:/Users/Michal/Git/my/ups12v/hardware/v4/ups_v4/ups12v_v4.kicad_pcb` for project `ups12v_v4.kicad_pro` in the same directory. The board already existed at entry; it was reused. Live readback after the attempts: **2 copper layers, 0 footprints, 0 imported nets**. Four-layer initialization and import are NOT complete.

## Blockers and outcomes

1. Schematic-sync dry run returned `status=conflict`, one diagnostic `unsupported_library_footprint`: IC1 requires `Package_DFN_QFN:Texas_RQM0029A_VQFN-29_4x4mm_P0.4mm`, whose custom-shape pads cannot be placed by KiCad 10's typed placement path used by Konnect. This is a tooling limitation, not evidence that the approved TI footprint is invalid. The dry run planned/applied zero additions or updates; no import apply was attempted. No footprint substitution was made. Empty unassigned-footprint diagnostics do not prove all 152 references were validated because planning stopped at this conflict.
2. Live stackup readback was two-layer. Konnect reports the stackup IPC writer is not implemented and directs changes to KiCad Board Setup. The separate `add_layer(In1.Cu, power)` call returned `unsafe_file_fallback`, reason `kicad_lock_present`, explicitly stating no modification occurred. CAD mutations stopped. The lock is consistent with the deliberately open board; it was not deleted or bypassed. Do not close/restart/retry automatically to evade this guard.

Recovery requires supported KiCad Board Setup for four copper layers and an import method that preserves the exact approved custom pads (for example KiCad's native schematic update). Native GUI operations are not available through the current Konnect tools. After authoritative state is saved and the exact live board reconfirmed, repeat parity, pad readback and DRC. Do not replace IC1's qualified package geometry merely to satisfy the typed importer.

## Checks and render

- Fresh schematic ERC, KiCad 10.0.7: **0 errors / 4 unchanged isolated-label warnings**.
- Initial PCB DRC on the **saved file**, no save/refill: **1 error / 152 warnings**. Error: no Edge.Cuts outline, expected for the current blank board. Warnings: 152 missing-footprint schematic-parity findings, genuine evidence of import not completed. **0 unconnected items is not a pass**: no footprints/nets exist to route. Live geometry was not serialized by this DRC run.
- Critical imported pad maps for BQ25792/BQ25798, U1 ESP32-C3-MINI-1-N4X, F1, Q10, connectors and testpads are **not verifiable on this empty board**. Prior schematic/library evidence remains historical and does not establish PCB parity. No board pad mismatches can be assessed yet.
- Saved-file render exported to `phase4-1-empty-board.svg`; it represents the empty state, not an initialized design. No component placement was performed for presentation.
- Full tool responses: `phase4-1-tool-evidence.json`; DRC: `phase4-1-initial-drc.json`; ERC: `phase4-1-erc.json`.

## Retained strategy and gates

Four layers remain required, not configured. Future reference-plane intent: continuous PGND reference without a moat; do not force significant power-return current through NT1. GND/PGND copper assignment and NT1 net-tie treatment must preserve approved schematic domains and be checked before zones/routing; no copper continuity is claimed here. No zones were added.

One board must retain every F0/F5 footprint, with the existing 19 F5-only fitted parts DNP in F0. No component values, footprints, procurement fields or population definitions changed; BOM inventory therefore remains unchanged. C67/C68 assessment remains a recommendation, outside this import-only milestone.

VAC1 hot-plug transient concern remains an unresolved fabrication/power-up gate. BQ25792 2S default 2 A current risk remains unresolved. No hardware validation, firmware build, staging, commit or push performed. Stop here; milestone incomplete pending supported stackup/import operations.
