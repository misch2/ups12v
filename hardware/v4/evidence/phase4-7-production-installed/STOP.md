# Production installation stopped before commit confirmation/save

2026-10-11. Owner confirmed the board saved. Fresh production PCB/schematic/project hashes still matched accepted Batch1. Isolated native toolkit snapshot and direct live IPC preflight passed; 15 focused regression tests passed.

The bounded canonical IPC adapter called BeginCommit, changed the sole authorized BATTERY track to In2.Cu, and received 50 created-object replies whose geometry matched the accepted 47-track/3-via plan. It then checked board counts **before** EndCommit/push_commit. This was an adapter sequencing defect: the installed KiPy `Board.begin_commit` documentation explicitly says staged changes are not reflected in the editor until push_commit. Count check failed; worker stopped. No push_commit, refill or board save occurred. No native assertion or IPC failure occurred during this production attempt.

Read-only diagnostic capture `../c9-apply-phase4-7-install-stop-readback-ipc.json` confirms 252 tracks / 138 vias / 154 footprints, with exactly **one original track changed**: BATTERY UUID `01ab1eb5-ab75-462d-9e54-2d6eab529481`, now In2.Cu in live state. All other exported footprint/pad/track/via/zone/shape/text objects equal preflight. Added objects are not visible in the readback; their pending transaction status is uncertain. The initial adapter failed to persist the BeginCommit token, so no safe token-based completion/cancel is claimed.

Fresh saved PCB/schematic/project hashes all still equal Batch1. **DO NOT SAVE this partial live state as the approved installation.** No production DRC/ERC/parity or completed installation is claimed.

STOP for owner coordination. Safest bounded recovery is for the owner to close this PCB editor without saving the partial live changes and reopen the unchanged saved production board. Do not delete locks or recover/restart automatically. Confirm authoritative baseline after reopening before a fresh installation attempt; no duplicate application of the staged plan.

Adapter sequencing corrected on disk only: persist commit token immediately, verify returned created geometry, push the transaction before count/full-board readback, record push status, then verify exact added geometry again from visible objects. This correction has **not been executed on KiCad**. Before resumption, run focused tests/read-only preflight and use a fresh evidence directory. Canonical toolkit remains the implementation location; no ad-hoc native geometry helper added.

No automatic rollback, editor closure, save, recovery or retry. No remaining REGN/CE/control routing, fabrication, purchasing, power-up, firmware, commit or push.
