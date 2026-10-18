# Phase4.21 — stopped at first read-only IPC preflight

2026-10-18. **Production adoption INCOMPLETE. No CAD mutation attempted.**

The owner accepted the Phase4.20 candidate and authorized the exact three-track
production migration. That authorization remains bounded to the stated delta;
this checkpoint is an unexpected IPC safety STOP, not a new phase decision.

## Completed evidence

- Production SHA256 still
  `4e13e4c11c486aa4fba7866817f5c37e715b248ab696cbd4a599970cf2a2ea84`.
- Accepted candidate SHA256 still
  `4eb7bd2c72fec3cf49d3746250864b5237e7919760ebdbc3647cbc0101fa8737`.
- Fresh isolated native snapshot: [entry](../phase4-21-entry-native/context.json).
  Its complete geometry equals the candidate's accepted source export.
- [Exact plan](../phase4-21-preparation/exact-migration-plan.json) reconciles
  precisely the three approved removed UUIDs and three candidate added UUIDs,
  original/new endpoints, In2.Cu, USB_CC2 and 0.180mm width. All other snapshot
  objects, including all eight arcs, match. This is preparation, not installation.
- Existing 127 offline tests and four focused migration tests passed before the
  attempted connection. The migration implementation has not passed its native
  owning-editor rehearsal and must not be treated as production-verified.
  Final offline-only suite: **131 tests PASS**; [log](../phase4-21-preparation/tests-complete.log).
- Elevated host inspection found no existing KiCad editors before launch.
  Agent launched production PCB Editor PID95208 for read-only identity only.

## Trigger and retained state

The first worker's first `GetVersion` request attempted the historical endpoint
`ipc://.tmp/kicad/api.sock`. Connection was refused. The monitor stopped only
the worker and wrote [STOP.json](STOP.json); see [full log](ipc-preflight.log).
No document capture, transaction, item removal/creation, refill or save occurred.
No native assertion was observed. There was no retry, editor close, restart,
recovery, scratch overwrite or production file replacement.

Subsequent **OS-only** inspection identified exactly one KiCad process (PID95208,
exact production board command line) and an existing Windows named pipe:
`C:\Users\Michal\AppData\Local\Temp\kicad\api.sock`.
The actual host `TEMP`/`TMP` is `C:\Users\Michal\AppData\Local\Temp`;
`TMPDIR` is `.tmp`. The agent incorrectly reused a historical socket instead of
discovering this running editor's endpoint before connecting. No KiCad API was
called during this diagnosis. MainWindowTitle was empty, consistent with the
hidden launch; this provides no evidence of clean/saved live document state.
That identity remains unverified until a successful read-only IPC capture.

## Smallest safe continuation, requiring owner recovery approval

AGENTS.md requires owner approval before resuming KiCad operations after an
unexpected IPC failure. Preserve this stopped directory and diagnostics.
After approval, use a **fresh identity evidence directory** and the observed
endpoint `ipc://C:\Users\Michal\AppData\Local\Temp\kicad\api.sock` only after
OS-only re-identification of the exact process/pipe and unchanged file hashes.
Do not retry this stopped context. Perform read-only complete saved/live
comparison first; stop on document ambiguity or unsaved differences. Do not
restart, recover, close or save the editor as an IPC repair.

Only after that identity succeeds may the authorized isolated production-derived
owning-editor rehearsal begin. The same immutable implementation must pass full
native proof before its production transaction. Production adoption, refill,
independent readback, final ERC/DRC/parity/connectivity, PGND/F0/F5 preservation
and independent vendor screening are **not yet completed** in Phase4.21.
The Phase4.20 evidence remains accepted evidence, not proof of installation.

Nominal PCB thickness is owner-fixed **1.6mm**. Stackup, copper weights,
barrel-plating assumptions and fabrication parameters remain **UNSELECTED**.
No stackup/rule/footprint/BOM/schematic/firmware change, manufacturing output,
release, purchase, power-up, commit or push occurred.
