# Phase4.15 — exact bounded production migration proposal

**PROPOSAL ONLY. No production application is authorized or performed.**
[Hash-bound input/object plan](production-migration-plan.json) binds source hashes,
the accepted manifest, final review proof and every changed UUID/preimage/postimage.

## Inputs and exact scope

- Accepted production PCB:
  `75060f4b3d0f57e65f2c6e4736f3dc32d42e62e359541671b1ffce63eceb7014`.
- Reviewed owner PCB:
  `2ef3030c033f254742736c8da3d74468db133a13905eb55df3716a26335676e5`.
-247new tracks and8new vias; remove221old tracks and1old via.
- Update2existing track endpoints and3existing via positions.
- Translate the complete R8 footprint from `(40,75.5)` to `(40,74.8792)`;
  preserve its fields, library link, padstack and nets. Its two pads move
  implicitly; no independent pad-net edits.
- Retain all other source objects, especially8arcs, SW1/SW2, USB, F5, zone/rule
  definitions and schematic. Keep production project/rules; do not import the
  owner's dropdown-only preset changes.
- Target inventory:1053tracks/arcs,294vias,154footprints,473pads/157islands.

## Execution after separate owner authorization

1. Bind the current source hashes and whitelist into the guarded native-editor
   migration tooling and run affected regressions. The historical hardcoded
   Phase4.13 installer rejects this baseline and **must not be replayed**.
2. Rehearse on a **fresh production-derived scratch project**, using KiCad10's
   native editor transaction. Match all preimages; create/remove/update only
   listed objects in one commit. Push, inspect native readback, refill and save
   through that scratch editor. Never overwrite an open PCB from another file.
3. Independently validate a fresh isolated copy of the rehearsal: native
   save/reload/refill, ERC/DRC/parity and actual physical copper/connectivity
   comparison against the reviewed owner target. Require473pads/157islands,
   exactly the3IC1 closures, no lost baseline pad connections,41F5opens,
   no new physical/parity/ERC errors or warning identities, and preserved
   SW1/SW2, PGND returns/isolation, net ties, RF/USB/F5 and8arcs. Compare real
   filled copper; harmless refill serialization/container order is irrelevant.
4. Only after rehearsal PASS, establish the exact saved/live production
   baseline in its owning editor. Apply the same bounded transaction, read
   back, refill and save through that editor. No schematic/project/rule edits.
5. Perform one final native saved/live reconciliation and independent isolated
   ERC/DRC/parity/connectivity/physical-preservation check. Only then write the
   new accepted-installed manifest and handover. **STOP before F5.**

Each native action uses monitored isolated workers and fresh evidence. First
assertion, uncertain IPC/transaction or unexplained electrical/geometry mismatch
requires immediate STOP; no retry, suppression or automatic editor recovery.
Production must still be at the bound hash; otherwise this plan is stale.
