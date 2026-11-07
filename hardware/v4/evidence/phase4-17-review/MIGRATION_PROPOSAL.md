# Proposed Phase4.18 — exact F5 production migration

Proposal only,2026-10-17. **Not authorized or executed by Phase4.17.**

Review [Phase4.17 findings and electrical limitations](REVIEW.md) first. There are
no unfinished routes or required manual geometry edits. Owner acceptance of this
specific scratch candidate and separate authorization to migrate are the next
decisions; no new electrical architecture, component or design-rule decision is
needed to describe the bounded transaction.

## Exact immutable target

- Accepted production source PCB SHA256:
  `bce08349485b0f8d53060fcc9ef1a3911eaabf0408de16b288d0655e30754899`.
- Reviewed scratch PCB SHA256:
  `8221929563ed10653f84933549a6fdf99d69071364c12e83860a22f55326b9e6`.
- Geometry: candidate [plan.json](../phase4-17-final-candidate-v2/plan.json),
  [snapshot.json](../phase4-17-final-candidate-v2/snapshot.json),
  [native created identities](../phase4-17-final-candidate-v2/expected-additions.json)
  and [FINAL_PROOF.json](FINAL_PROOF.json). These hashes bind the proposal.
- Translate/rotate exactly18whole F5 footprints: U7/U8/Q10/L3,
  R60–R63 and C60–C69, to the exact positions/orientations in that plan.
  Preserve full footprint payloads/pad nets, reference/value fields and artwork.
  J8 and TP17 stay fixed, as do all F0 placements.
- Add exactly117straight tracks and30through-vias, with the exact named nets,
  layers, widths, positions, copper diameters and drills in the reviewed plan.
  The original1053tracks/arcs and294vias are untouched; no removal, replacement,
  rule-area, stackup, schematic, library/BOM/population or unrelated change.
- Result:154footprints,473pads,1170tracks/arcs,324vias;0unconnected,
  0physical/0parity errors,ERC0errors and no lost old pad islands.

The existing production add-only installer does not authorize footprint moves.
A focused, regressed owning-editor transaction must therefore be prepared for
these18whole-footprint rigid changes plus the exact additions. Phase4.17's
`f5_scratch` module deliberately has no production installer.

## Proposed execution after separate authorization

1. Guard all accepted source/project/rules/manifest and target evidence hashes;
   establish exact saved/live production authority without recovering an editor.
2. Implement/regress the exact full-footprint/native SDK payload transform and
   new-object whitelist. Perform one new isolated, production-derived owning-editor
   rehearsal; do not reuse any Phase4.17 scratch or historical rehearsal editor.
3. Prove returned payloads, pushed visible objects, native refill/save and an
   independent saved readback against this reviewed geometry. Require ERC/DRC,
   all473pads/old connections, original F0 copper/arcs and critical PGND regions,
   exact warning identities in their appropriate library contexts, and saved/live
   actual-filled-copper agreement. Benign cache IDs/serialization are not copper defects.
4. Only after that rehearsal passes, apply one identical bounded transaction in
   the owning production editor. Never replace production with a scratch file.
   Refill/save/read back and repeat the production adoption proof, then update
   the accepted manifest/handover and STOP for review.

Unexpected native assertions or uncertain IPC outcomes retain the immediate
STOP/owner-recovery rule. Normal validation failures are investigated within
the authorized scope without weakening preservation/electrical checks.

This proposed migration does not authorize fabrication, purchasing, hardware
power-up or physical qualification. The hot-copper voltage allocation and U7
thermal/dropout/Ceff/reverse-transient limits remain documented qualifications
for subsequent matching-hardware work, not evidence of completed measurements.
