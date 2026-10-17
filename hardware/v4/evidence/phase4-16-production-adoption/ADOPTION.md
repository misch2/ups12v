# Phase4.16 — exact owner routing installed; PASS

2026-10-17. Owner accepted the repaired Phase4.15 prototype review and authorized
this bounded migration. **Production installation and final verification PASS.**
The source was the saved `phase4-14-owner-walkaround/ups12v_v4` project, PCB
SHA256 `2ef3030c033f254742736c8da3d74468db133a13905eb55df3716a26335676e5`.
The previous production PCB was
`75060f4b3d0f57e65f2c6e4736f3dc32d42e62e359541671b1ffce63eceb7014`.

## Accepted installed identities

| Production file | SHA256 |
|---|---|
| `ups12v_v4.kicad_pcb` | `bce08349485b0f8d53060fcc9ef1a3911eaabf0408de16b288d0655e30754899` |
| `ups12v_v4.kicad_sch` | `281d5eccd48a9b07f3ab3b7b836c7ad395af59487c775ad20a4efb3828bdba68` |
| `ups12v_v4.kicad_pro` | `477e5c47219922b25619e9db0748961ed83af3958866842e0a34ad1d1641a21e` |
| `ups12v_v4.kicad_dru` | `a7bfa1d3fe8b0ba2a9a034a982b866c439c939321d558af2460c7b95ac25ebb7` |

[Accepted complete native manifest](accepted-installed-baseline.json),
[final proof](final-production-proof.json), [compact checkpoint](checkpoint.json).
Schematic, production project and rules hashes are unchanged. Owner source files
remain unchanged. The installed PCB is byte-identical to the saved successful
production-derived editor rehearsal, including its retained production metadata.

## Exact bounded transfer

The complete native owner/production delta was reconciled against every UUID,
preimage and postimage in the unchanged Phase4.15 proposal:

- Create247 tracks and8 vias; remove221 tracks and1 via.
- Update2 existing track endpoints and3 existing via positions.
- Translate complete R8 `(40,75.5)` → `(40,74.8792)`, including both pads,
  artwork and fields, retaining padstacks, nets, library link and other properties.
- Retain all8 actual PCB arcs and all other production source objects/settings.

No serialized CAD was hand-edited or overwritten from a scratch file. The
historical Phase4.13 installer was not replayed. One new native transaction in
the rehearsal and one identical production transaction each passed returned-item
and complete visible-object readback, refill and owning-editor save.

The intentionally accepted BATTERY repair is present exactly:0.60mm In2 segment
between `(63.1,64.8)` and `(63.1,65.5)`, both original0.70/0.40mm vias retained;
the removed auxiliary branch was not recreated. Existing prototype path/current/
thermal qualifications from the [accepted review](../phase4-15-repaired-review.md)
remain applicable. This milestone introduces no new electrical qualification.

## Verification

Fresh independent native save/reload/refill, full ERC/DRC/parity, actual pad
polygons/drills, routed copper/padstack diagnostics, artwork, zone definitions,
fills including every polygon/hole, and all473 native pad islands match the
accepted owner target. Final inventory: **1053 tracks/arcs,294 vias,154 footprints,
473 pads,157 pad islands**. Exactly one island merge on each of I2C_SCL,~INT,STAT;
all160 baseline islands preserve their earlier pad connections. No net reassignment.

Production DRC: **41 unconnected,0 physical errors,0 parity,16 warnings**.
Production ERC: **0 errors,4 warnings**. Warning identity multisets and ignored
checks match accepted production. Matched isolated review:20DRC/11ERC warnings,
also identical to accepted isolated owner evidence; these are different library
contexts and must not be combined. Final saved/live reconciliation PASS.

All41 remaining unconnected entries are the accepted F5 remainder; **F0=0**:

| Net | Entries |
|---|---:|
| PGND |12|
| SYS |5|
| /F5_SW |2|
| /F5_RAW |10|
| /F5_FB |2|
| /F5_BST |1|
| /F5_EN |2|
| /F5_VCAP |1|
| /F5_SS |1|
| /F5_5V_OUT |4|
| /F5_GATE |1|

Critical power/PGND return connectivity and isolation, net ties, actual PGND
filled copper, SW1/SW2, USB routing/pair recognition, RF rules and existing F5
copper exactly match the accepted target. No repeated thermal/USB optimization
or signal-integrity analysis was needed because this geometry is identical.
Saved structural differences from the entry are confined to whitelisted routing
objects and R8; incidental fill serialization is excluded, actual copper is not.

Full offline toolkit suite: **107 tests PASS**. Added controls reproduce the
captured numeric net-cache omission, reject wrong net names/geometry and validate
separate production/owner project provenance while retaining exact resolved rules.

Evidence: [independent final native review](../phase4-16-final-production-native/summary.json),
[saved/live readback](final-live-readback.json), [production checks](production-checks.json),
[exact post-transaction preservation](ipc-preservation.json),
[complete delta reconciliation](complete-reconciliation.json),
[rehearsal proof](../phase4-16-editor-rehearsal-v2/complete-candidate-proof.json).

## Earlier interrupted rehearsal and editor lifecycle

The owner forcibly terminated the first hidden rehearsal PID103884 without saving.
Host process inspection confirmed exit and all original hashes unchanged. Its
stopped transaction was not reused. Old locks/evidence were preserved, including
the hash-bound stopped implementation. The fresh v2 native rehearsal used a new
production-derived directory and new editor PID131372.

The numeric GetNets cache is now excluded only when an exact nonempty net name
is available; code-only/unknown identities, names and physical geometry remain
checked. New objects are sent with names without numeric cache codes. The
export-only verifier separately binds the intentional owner/production project
hash difference caused by approved dropdown presets; resolved rules stay exact.
The native transaction implementation remained unchanged between successful
rehearsal and production. The separate verifier hash is recorded in both proofs.

KiCad exposes one shared endpoint in this environment. The saved rehearsal and
a clean production editor launched while that endpoint was occupied were closed
normally, before any production IPC. The exclusive owning production editor
PID88180 then passed preflight/application/final readback. It was closed normally
after the final PASS, with accepted saved hashes guarded before and after close.
No hidden editor was intentionally left running. No native assertion, IPC
transport instability, failed production transaction, rollback or recovery occurred
during the successful v2 rehearsal/production workflow.

## Phase boundary

**STOP for owner review before any F5 implementation.** Only the short
[F5 phase proposal](NEXT_F5.md) was prepared. No F5/USB optimization, deferred
legacy cleanup, BOM change, firmware, fabrication, purchase, hardware power-up,
Git commit or push was performed. Matching-hardware electrical/thermal validation
remains a separate existing qualification. Recommend a fresh session for F5.
