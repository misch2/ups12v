# Production IPC reconnect — read-only result

2026-10-11. Owner supplied `ipc://C:\Users\Michal\AppData\Local\Temp\kicad\api.sock` and requested another attempt. Konnect still reports no configured socket. Direct supported KiCad IPC through the existing read-only checkpoint exporter, supervised by the canonical toolkit monitor, succeeded outside the sandbox after explicit escalation approval. The sandbox attempt failed on socket Permission denied before document access; no native assertion occurred.

Exact live board `ups12v_v4.kicad_pcb`, project directory `C:/Users/Michal/Git/my/ups12v/hardware/v4/ups_v4`, confirmed by the exporter. Live counts: 154 footprints / 473 pads / 252 tracks / 138 vias / 2 zones. Fresh saved PCB/schematic/project hashes equal accepted Batch1.

Full live IPC capture: `../c9-apply-phase4-7-production-preflight-reconnect-host-ipc.json`. Difference evidence: `live-baseline-differences.json`, `live-baseline-field-differences.json`. Compared all exported footprints/pads/tracks/vias/zones/shapes/texts against accepted Batch1. 555 root parent references and eight references to four custom-pad primitive UUIDs differ. Beyond these identifiers, four circular vias report `customAnchorShape=PSS_RECTANGLE` rather than the baseline `PSS_CIRCLE`; their actual `shape=PSS_CIRCLE`, sizes, positions and nets are unchanged. No exported routing, placement, pad/drill-size, net, zone, outline or text difference was found beyond those fields. The inactive custom-anchor-field difference is not presented as a changed copper shape or electrical defect.

Unsaved/dirty editor status has not been established by this item capture. No save/revert/mutation was attempted to resolve that uncertainty. Owner's preflight requires STOP when live state cannot be reliably reconciled. Request owner to save the exact board normally without discarding edits, and confirm the saved state; then recheck hashes and review any changed baseline before production mutation. Installation approval remains valid; design approval is not being requested again.

No production installation, remaining control routing, fabrication, purchasing, power-up, firmware, commit or push.
