# Phase4.16 — rehearsal STOP; production unchanged

2026-10-17. The owner accepted the final repaired Phase4.15 prototype review
and authorized its exact production migration. That authorization remains the
task scope; this checkpoint does not revoke it or authorize transaction recovery.

## Verified entry

Host CIM inspection established no running pcbnew/kicad/eeschema processes;
neither owner nor production project had a lock. All four production and owner
source hashes, accepted manifest and bound Phase4.15 proof artifacts matched.
Fresh monitored isolated native snapshot:
`../phase4-16-entry-native/`. Complete whitelist/preimage/UUID reconciliation
passed, including all eight actual PCB arcs, moved vias, removed/replaced tracks,
R8 translation and its two implicit pad translations.

The new import-safe `v4kicad.owner_migration` prepares native objects and uses
the owning KiCad editor API; it does not replay the historical Phase4.13 worker.
Nine new offline tests plus the previous 95 passed (104 total). Pure SDK object
construction verified complete R8 translation and retained arc payloads.

One production-derived rehearsal editor was launched: **PID103884**, target
`hardware/v4/evidence/phase4-16-editor-rehearsal/ups12v_v4.kicad_pcb`.
Its passively discovered named pipe was `.tmp\kicad\api.sock`.
The monitored exact saved/live preflight passed: 1027 tracks/arcs, 287 vias,
154 footprints, 473 pads; complete accepted native payloads matched.

## STOP and captured diagnosis

The worker began one native commit, and removal, update and creation calls
returned. Updated/created UUID sets matched the prepared transaction. Its next
guard rejected the returned native payload, **before `push_commit`**. The worker
exited and a persistent STOP marker prevents another invocation on this target.
No push, refill, save, rollback, retry, recovery or further KiCad call followed.

Offline comparison of the already captured payloads found exactly **260 leaf
differences on 260 routed objects**: `GetNets` supplies numeric `net.code` cache
fields, while the CRUD responses omit those fields. Net names and every other
returned payload field match exactly. This is a checker incompatibility, **not
evidence of a copper, pad geometry or electrical net-name defect**. No native
assertion or IPC timeout/transport failure was observed.

The staged editor transaction has not been reconciled/pushed after worker exit.
Its persistence/commit ownership must not be assumed. The process and evidence
are left untouched for owner disposition; the stopped rehearsal is not reusable.
Its saved PCB still equals the original production entry hash.

Evidence: [diagnosis](STOP-DIAGNOSIS.json), [returned payload delta](returned-payload-delta.json),
[worker log](ipc-apply.log), [commit identity](commit.json),
[prepared transaction](prepared-transaction.json), [full expected payload](ipc-expected.json),
[full returned payload](returned-items.json), [entry preflight](ipc-preflight.json).
The migration context records the exact plan and implementation hashes.

## Production and phase boundary

**No production migration occurred; the production editor was never opened.**
All four source hashes remain accepted Phase4.13, including PCB
`75060f4b3d0f57e65f2c6e4736f3dc32d42e62e359541671b1ffce63eceb7014`.
Owner PCB remains
`2ef3030c033f254742736c8da3d74468db133a13905eb55df3716a26335676e5`.
The accepted production manifest is unchanged. No final production ERC/DRC,
connectivity or acceptance claim is made; rehearsal never passed its gate.
The accepted owner target's 41 F5 opens/zero F0 have not been installed.

**Smallest owner action:** discard/close only the isolated rehearsal editor
without saving and confirm the disposition before any fresh KiCad rehearsal.
Do not save/promote this scratch, overwrite production or reuse this transaction.
Before a fresh rehearsal, fix and regress the request's numeric net-cache handling
(use exact net names as the existing native item APIs do), preserving all geometry,
padstack, full-footprint, UUID, net-name and input-hash guards. The stopped
implementation and its bound evidence are preserved for diagnosis.

F5 routing and its post-migration proposal remain pending the verified production
migration. No schematic/project/rule/BOM, firmware, fabrication, purchasing,
power-up, commit or push work occurred.
