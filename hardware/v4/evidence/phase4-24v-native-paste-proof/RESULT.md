# Phase4.24V — metadata-preserving native scratch proof PASS

2026-10-18. **Targeted pcbnew operations succeed without replacing footprints.**
Production and the rejected open Phase4.24U rehearsal were not modified.

| Identity | SHA256 |
|---|---|
| Production before AND after | `8c68d920e71cea6373f9ee1f767f661d228ebafd6e1a00fadc580e00bc460e87` |
| New V scratch, native saved/reloaded | `d0a8c95a1b8cfbeff1f4f7fa4a95abf297a86d9c95551ed5b7b3050f42b8ac2b` |
| Accepted T candidate | `d0a8c95a1b8cfbeff1f4f7fa4a95abf297a86d9c95551ed5b7b3050f42b8ac2b` |
| V independent inverse native save | `8c68d920e71cea6373f9ee1f767f661d228ebafd6e1a00fadc580e00bc460e87` |
| Owner ZIP, unchanged | `7dd71cf2854a50915d2d82f91e62bba5974efc659a69f52fda5b44882dc86d95` |

Candidate: [candidate-v3/ups12v_v4.kicad_pcb](candidate-v3/ups12v_v4.kicad_pcb).
It was created from a fresh production copy using native `PAD.SetLayerSet`,
`PCB_SHAPE.Clone`, supported casts, `SetParent`, `FOOTPRINT.Add`, and `SaveBoard`.
Only the four approved paste memberships were removed. The ten exact T graphics
were cloned with their original UUIDs and native Q2 polygon representation.
No whole-footprint IPC update, pattern recalculation, library refresh or CAD text
modification was used.

Independent native save/reload proves **473 pads, 324 vias, 154 footprints,
41 component PTH and12 NPTH**, all original copper/fills/connectivity/mask/silk/
outline/RF restrictions and footprint properties preserved. Full native bytes
equal T; reversing only the approved paste delta reproduces the original source.

| Explicit original symbol-unit metadata | Result after save/reload |
|---|---|
| Q1 unit A, pins4/6/7/8/9/5/1/2/3 | Exact original complete block preserved |
| Q2 unit A, pins4/6/7/8/9/5/1/2/3 | Exact original complete block preserved |
| Q10 | Original absence of units block preserved; none invented |
| U4 unit A, pins1/2/3 | Exact original complete block preserved |

Exact unit blocks and footprint UUIDs were compared for **all154 footprints**;
see [independent preservation proof](independent-readback-v3/verify-result.json).

Fresh actual GTP has **411 connected openings**, with **zero raw geometric XOR**
against T. Coverage remains Q1/Q2/Q10=61.1369%, U4=60.8148%; all401 unrelated
original pad contributions and F0/F5/DNP presence inherit the bound T CAM proof.
The actual GTP SHA is
`0266433a8bd6be743118c60f44295f88493c005f9b9ee12706f3656a5524505f`;
T GTP SHA is `bde8cbc17ee7e712a3d3eb56529752230332590bcd24ce0c4d62dc211bf9db49`.
Their only text differences are generation timestamps. See
[focused GTP comparison](independent-readback-v3/gtp-comparison.json).

Fresh DRC: **0 errors/0 opens/0 parity,18 exact accepted warnings** (original16
plus only the known Q2/Q10 paste/library mismatches). ERC: **0 errors,4 exact
accepted warning identities**. **195 regression tests PASS**. All55 bound source/
evidence inputs and9 project-local library files are unchanged. No native
assertion or IPC failure occurred. Earlier Python/SWIG adapter diagnostics remain
recorded in [validation notes](VALIDATION.md); they are not accepted candidates.

[Recommended production procedure](PRODUCTION_PROCEDURE.md) uses closed-editor
coordination and the same targeted native operations. **It was not executed.**
STOP for owner approval; no production adoption, Gerber ZIP re-export, upload,
order, purchase, commit or push. Stencil intent remains0.10mm/top/1:1 as per Paste
Layer, without automatic optimization.
