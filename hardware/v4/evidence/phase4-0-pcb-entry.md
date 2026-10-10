# Phase 4.0 — PCB entry checkpoint

2026-10-10. Owner approved Phase 3.7 and requested continuation from the current instructions and handover. This records schematic acceptance and preparation for PCB integration; it does not grant fabrication, purchase or power-up approval.

## Verified entry state

- Branch: `codex/v4-phase2-power-stage`; HEAD `ca7ec20` (`phase 3.7`). Working tree clean at entry.
- Saved schematic SHA256 matches the accepted Phase 3.7 evidence: `16fbf0aa5000f4b312559aa22c4c59705b9ed9f2a34af95d4009dfc8d4ce4cb2`.
- Only CAD directory: `hardware/v4/ups_v4/`. Existing project and schematic are present; no matching PCB file exists.
- Existing ERC/XML results remain historical Phase 3.7 evidence; no fresh ERC, DRC, parity or hardware measurement is claimed in this documentation-only checkpoint.
- Konnect tools are callable, but `open_project` for the exact V4 project reports `ipc_available=false`, `ipc_failure.kind=not_configured`, no open boards and no confirmed requested board. See `phase4-0-ipc-probe.json`. This supersedes earlier responsive-IPC observations for this session. The response does not independently prove that no KiCad process exists.

## Next bounded CAD checkpoint

1. Establish KiCad 10 IPC connectivity and create/open `hardware/v4/ups_v4/ups12v_v4.kicad_pcb` using supported CAD operations. Do not use `create_project` over the existing project, and do not hand-create serialized board content. Before any live mutation, obtain exact full board-path confirmation from Konnect.
2. Dry-run schematic-to-board synchronization. Inspect missing/unassigned footprints and pad-map conflicts before applying its exact plan revision. Preserve all assembly variants on one physical PCB, including the 19 F5-only fitted parts.
3. Save and verify imported reference/pad/net parity against the accepted schematic, including F01 and the three-pad UART group. Run fresh ERC and initial DRC; distinguish expected unrouted/incomplete-board findings from unexpected library or connectivity defects. Store full reports under `evidence/`.
4. Stop for review of board initialization and footprint exceptions before a substantially different placement/routing milestone. Do not invent outline dimensions, mounting locations or a fab stackup. Four layers are the approved starting direction; physical geometry and fabrication parameters remain open.

Placement must retain M3/standoff function, all-layer antenna clearance, service-accessible USB, TP5/TP6/TP7 in that top-side order at 2.54 mm pitch, orientation marking, separate voltage/power probes and TP17 near J8. Existing harness/connector/NTC identities and Q10 courtyard need resolution before footprint freeze. Update `V4_BOM_REVIEW.md` whenever a component/value/footprint changes; no such change occurred here.

## Current stop and retained risks

PCB mutation is unavailable until the IPC endpoint is configured and the exact V4 board is addressable. Configure KiCad's API and the corresponding IPC Socket in Konnect settings, then reconnect the client as required by the server diagnostic. Recover/save any existing editor work before changing connection state.

VAC1 hot-plug remains a fabrication/power-up block. BQ25792 2S default 2 A charging risk remains open. Phase 3.7 approval does not resolve either risk or establish electrical/thermal qualification. No CAD, firmware, staging, commit, push, purchase or hardware activity occurred in this checkpoint.
