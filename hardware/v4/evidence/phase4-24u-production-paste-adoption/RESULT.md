# Phase4.24U — production adoption stopped before production

2026-10-18. **STOP: the owning-editor rehearsal failed complete native
preservation. Production was not modified.** The accepted Phase4.24T candidate
remains valid; the new IPC rehearsal is rejected.

| Object | Before SHA256 | After SHA256 |
|---|---|---|
| Production PCB | `8c68d920e71cea6373f9ee1f767f661d228ebafd6e1a00fadc580e00bc460e87` | identical |
| Accepted T candidate | `d0a8c95a1b8cfbeff1f4f7fa4a95abf297a86d9c95551ed5b7b3050f42b8ac2b` | identical |
| Owner manufacturing ZIP | `7dd71cf2854a50915d2d82f91e62bba5974efc659a69f52fda5b44882dc86d95` | identical |

The rejected rehearsal is `owning-editor-rehearsal/ups12v_v4.kicad_pcb`, SHA256
`96438b3c28a237997355c1849381fe2b910a29d57d3b8d61d11a8b45d869481b`.
It is a fresh production-derived project, not the accepted candidate copied over
production. No production transaction was begun and no completed rehearsal gate
was issued.

## Exact operation tested

The plan reconciled original physical pad UUIDs and complete footprint-child
payloads against the accepted candidate. It allowed only removal of F.Paste
membership on Q1.9, Q2.9, Q10.9 and U4 large tab2, and the ten exact accepted
F.Paste-only child graphics. Q2's accepted polygon payload was preserved. There
was no pattern regeneration, helper electrical pad, library refresh or CAD text
patch.

One guarded KiCad10.0.7 owning-editor commit updated the four complete footprint
instances. Returned payloads and complete IPC captures matched the accepted
candidate. Refill and save through that editor succeeded, and a subsequent
read-only IPC capture matched the saved capture.

## Why the rehearsal is rejected

An independent native process reloaded a separate copy of the saved rehearsal.
Original geometry/electrical and actual layout/fill inventories matched the
accepted baseline. The stronger check then reversed only the ten paste graphics
and four paste flags **in memory** and saved a separate proof file. Its complete
native bytes did not reproduce the original source.

The [full residual diff](rehearsal-independent-checks/restored-source.diff)
contains exactly three removed native symbol-unit blocks:

| Footprint | Removed metadata |
|---|---|
| Q1 | unit A, pins 4/6/7/8/9/5/1/2/3 |
| Q2 | unit A, pins 4/6/7/8/9/5/1/2/3 |
| U4 | unit A, pins 1/2/3 |

This is an actual property loss introduced by complete-footprint IPC update.
It is not the earlier IPC string-format difference. The installed
`kipy/proto/board/board_types_pb2.pyi` Footprint/FootprintInstance schema exposes
sheet/path/filter fields but no native symbol-unit/pin mapping. Thus matching
those IPC payloads cannot establish preservation of this omitted data. No safe
supported operation for preserving it was established; no workaround was used.

The failure was a deliberate preservation gate, not a KiCad assertion or IPC
connection failure. The native worker's SWIG pointer ownership exit notices are
also retained in [its log](rehearsal-independent-checks/native-readback.log).

## Verification and scope

- 188 complete offline regression tests passed, including six exact adoption
  delta rejection/acceptance tests.
- Source and accepted candidate each passed clean-editor identity, complete IPC
  capture and independent native canonical saved/live equality.
- Rehearsal IPC source preflight, exact intended/returned payload check,
  post-commit capture, refill and save checks passed.
- Independent original native geometry/layout comparisons passed; **complete
  native source preservation failed** as described above.
- DRC/ERC and focused GTP comparison were **not reached**. No production GTP,
  411-opening production confirmation or production warning disposition is
  claimed. The accepted T checks remain the previous evidence only.
- All35 protected source inputs and11 accepted artifacts match their entry
  hashes, including production, schematic, project/rules, libraries, BOM and ZIP.

The clean saved rehearsal editor remains open. The normal-close helper stopped
before sending a close because its STOP cleanup path expects legacy J7 context;
the editor was not forcibly closed, repaired or recovered. Root and rehearsal
STOP markers prohibit reuse of this mutation context.

See [validation details](VALIDATION.md), [machine status](final-result.json),
[protected hashes before](inputs-before.json) and [after](inputs-after.json).

**STOP before production adoption.** A future attempt must first establish and
fully rehearse a supported owning-editor operation preserving the missing
metadata. Do not copy the accepted PCB over production or refresh libraries.
No ZIP regeneration, manufacturing upload, order, purchase, commit or push.
Stencil intent remains0.10mm/top/1:1 as per Paste Layer; owner re-export is deferred.
