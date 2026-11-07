# Phase4.24W — verified production adoption PASS

2026-10-18. **Production PCB is ready for owner's manual Gerber-to-Order re-export.**
The exact accepted native stencil correction is installed and independently
verified. Manufacturing ZIP regeneration was not performed.

| Identity | SHA256 |
|---|---|
| Production before; verified backup | `8c68d920e71cea6373f9ee1f767f661d228ebafd6e1a00fadc580e00bc460e87` |
| **Saved production after** | **`d0a8c95a1b8cfbeff1f4f7fa4a95abf297a86d9c95551ed5b7b3050f42b8ac2b`** |
| Accepted T/V target | `d0a8c95a1b8cfbeff1f4f7fa4a95abf297a86d9c95551ed5b7b3050f42b8ac2b` |
| Independent native inverse proof | `8c68d920e71cea6373f9ee1f767f661d228ebafd6e1a00fadc580e00bc460e87` |
| Owner ZIP, unchanged | `7dd71cf2854a50915d2d82f91e62bba5974efc659a69f52fda5b44882dc86d95` |

## Exact paste delta

Original copper pads remain unchanged. Only F.Paste membership was removed from
Q1.9/Q2.9/Q10.9 and U4 large tab2 UUID8de1b06f…6649. Ten exact accepted graphics
were cloned natively, retaining Q2's polygon representation and all graphic UUIDs.

| Physical land | Replacement windows | Coverage |
|---|---|---|
| Q1.9/Q2.9/Q10.9, each | 2 ×1.00×1.50mm, R0.05 | 61.1369% |
| U4 large tab2 | 4 ×0.75×1.50mm, R0.05 | 60.8148% |

Drain fingers5–8, U4 small2,401other original contributions and F0/F5/DNP presence
remain unchanged. [Exact native/physical delta](execution/exact-paste-delta.json).

## Acceptance evidence

- Fresh production-derived rehearsal of the W wrapper passed native inverse,
  metadata, DRC/ERC/parity and actual GTP before production was touched. Its
  targeted native operation is mechanically AST-identical to accepted V.
- Original production objects were mutated and saved directly through pcbnew10.0.7
  with all editors closed. No whole-footprint IPC, library refresh, serialized
  CAD edit or scratch-file replacement was used.
- Independent production reload equals complete T/V bytes; native inverse save
  equals complete original source. All154footprints,473pads,324vias,41PTH,12NPTH,
  original tracks/arcs/copper/fills/nets/mask/silk/RF/outline/properties preserved.
- All154complete unit blocks/UUIDs match: Q1/Q2 unitA and U4 unitA retained;
  Q10's original absence of units retained exactly.
- Actual production GTP: **411connected apertures, raw XOR=0mm² against T and V**.
- DRC **0errors/0opens/0parity**, exactly18accepted warnings: original16 plus only
  documented Q2/Q10 paste/library additions. Ignored checks unchanged.
  ERC **0errors/4exact accepted warning identities**.
- **198tests PASS before and after installation**. All110bound inputs checked;
  only authorized production PCB changed. Backup14artifacts and companions,
  libraries, BOM, firmware and accepted evidence preserved.

[Independent native proof](execution/production-readback/native-verification.json)
· [GTP comparison](execution/production-readback/gtp-comparison.json)
· [Full result](final-result.json)
· [Installed baseline](accepted-installed-baseline.json)
· [Validation/entry history](VALIDATION.md).

**STOP after successful production adoption.** Owner manually re-exports the
manufacturing package. Existing ZIP still describes previous paste geometry.
No ZIP generation/replacement, upload, order, purchase, commit or push. Intended
stencil0.10mm/top/1:1 as per Paste Layer; no automatic aperture optimization.
