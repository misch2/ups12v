# Single approved read-only verification — stopped on identity differences

2026-10-11. One owner-approved kipy IPC protobuf capture completed. No native pcbnew import, LoadBoard, geometry getter, save, refill, DRC, routing, revert, restart or close was performed. No assertion appeared in the command output; this is not independent observation of GUI dialogs. No IPC retry or recovery was attempted.

- Exact PCB filename and project directory matched `hardware/v4/ups_v4/ups12v_v4.kicad_pcb`.
- Counts:154 footprints/473 pads/240 tracks/134 vias/2 zones/4 board shapes/5 board texts. C9 remains(61.1,69.1),0degrees.
- PCB, schematic and project SHA256 hashes match the approved C9/artwork checkpoint and were unchanged across capture.
- Strict object comparison failed, so verification is **STOPPED, not PASS**.

Ordinary offline JSON comparison after the stop found no added or removed item IDs. Differences are limited to top-level objects' `/parent/value` and four IC1 custom-pad primitive `/id/value` fields (present both inside the footprint definition and the separately captured pads). No other field differences were found, including no geometry, connectivity, copper-fill or artwork differences. These identity changes are consistent with regenerated runtime identities, but this capture does not establish their cause. The strict failure is retained; no normalization has been used to silently convert it into a pass.

Evidence:

- `c9-apply-phase4-7-post-assertion-approved-ipc.json`: full capture.
- `phase4-7-post-assertion-verification.json`: exact identity, object comparison and before/after hashes.
- `phase4-7-post-assertion-differences.json`: complete changed field-path counts.
- `phase4_7_verify_ipc_once.py`: one-shot wrapper around existing kipy snapshot approach; refuses existing evidence to prevent accidental repeat.

The new general rule in AGENTS.md requires an immediate stop at the first unexpected native KiCad assertion, investigation, a safe workaround and owner approval before resuming operations.

STOP for owner review of the identity-only differences. No Phase4.7 routing preflight resumed and no production CAD changes authorized or applied. Any acceptance of these identity differences and authorization to resume the preflight must be explicit; no further live verification is performed automatically.
