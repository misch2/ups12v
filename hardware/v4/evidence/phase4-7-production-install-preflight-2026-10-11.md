# Phase 4.7 production installation — preflight STOP

2026-10-11. Owner **APPROVED** production implementation of the exact validated 14.198946620 mm PROG candidate and associated BATTERY/BATP/PGND/ILIM_HIZ/TS geometry. No further design approval is pending. Installation has **not begun**.

Target project: `C:/Users/Michal/Git/my/ups12v/hardware/v4/ups_v4/ups12v_v4.kicad_pro`; board: same directory, `ups12v_v4.kicad_pcb`. Branch: `codex/v4-phase2-power-stage`.

Fresh SHA256 checks of production PCB, schematic and project all match `c9-apply-phase4-7-batch1-final-ipc.json`. The existing isolated accepted-baseline native snapshot records 252 tracks / 138 vias / 154 footprints; matching current board bytes bind the saved board to that geometry without a new native load. This verifies saved state only.

Konnect `open_project` returned `ipc_available=false`, `ipc_failure.kind=not_configured`, empty IPC address and `requested_open=null`. Its `kicad_ui_running=false` and zero open-board count do **not** establish that no editor is running when IPC is unconfigured. Both `~ups12v_v4.kicad_pcb.lck` and `~ups12v_v4.kicad_pro.lck` are present. Unsaved live state and document identity therefore cannot be reliably reconciled. Full response: `phase4-7-production-install-preflight-ipc.json`.

**STOP under owner preflight item 2.** No native CAD operation, production mutation, save/refill or lock deletion attempted. No production DRC/ERC/parity result is claimed. The scratch validation remains accepted evidence, not a substitute for fresh production checks.

Owner coordination needed: make the exact production board available through configured Konnect IPC, or explicitly reconcile any open/unsaved state and confirm a cleanly closed authoritative saved board before agreeing a supported closed-board procedure. Do not discard changes or remove locks automatically. If saving changes alters the accepted baseline, stop and review the divergence before installation.

After coordination, use the unchanged canonical toolkit for exported geometry/preservation/validation and a supported installation method that cannot overwrite an open board. Apply only the accepted plan and sole original BATTERY layer change. Preserve all approved placements, power/switching copper, netclasses, ground and RF keepout. Fresh production ERC/DRC/parity, persistence and baseline accounting remain required. REGN/CE/control routing stays outside scope. Existing BATTERY current-sharing/thermal and PROG coupling limits are documented in `phase4-7-preferred-final-checkpoint-2026-10-11.md`.

No fabrication, purchasing, power-up, firmware, commit or push.
