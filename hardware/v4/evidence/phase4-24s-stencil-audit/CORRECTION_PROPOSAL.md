# Minimal scratch-only proposal — not implemented

2026-10-18. **B — LOCAL PASTE CHANGE RECOMMENDED. Owner review STOP.**

Only four physical lands would change: **Q1.9, Q2.9, Q10.9, and U4's large tab numbered 2**. U4's small lead numbered 2 stays unchanged. No U1, L1, fine-pitch or DNP aperture removal is proposed. All copper, mask, vias, accepted package deviations, circuitry, BOM and fabrication settings stay unchanged.

The exact geometric proposal is [scratch-only-correction-proposal.json](final-v2/scratch-only-correction-proposal.json), bound to the supplied ZIP and current/accepted PCB hashes. It is neither a KiCad file nor a replacement paste Gerber. Its geometrical checks confirm every proposed window remains inside its present aperture and clear of all retained paste.

## Q1, Q2, Q10 — pad 9 only

Current pad 9: **2.45×2.00 mm rectangle**, 4.900 mm² exposed/pasted, nominal wet volume 0.490 mm³ at 0.10 mm. The adjacent drain fingers 5–8 overlap it by approximately 0.15 mm and form one physical drain aperture with it. Their original paste is retained.

Propose **two 1.00×1.50 mm rounded windows, R0.05**, replacing only pad 9's paste contribution. Let `v` point from the pad 9 center toward the mean position of pins 5–8, and `u=(v_y,-v_x)`. Window centers are `pad9 ± 0.625u − 0.100v`; width is along `u`, length along `v`. This definition handles the oppositely oriented parts and preserves the accepted physical coordinate basis.

| Ref | Pad 9 center X/Y (mm) | Proposed two window centers X/Y (mm, display rounded to 6 decimals) |
|---|---|---|
| Q1 | 43.900000 / 69.710000 | 43.275000 / 69.610000; 44.525000 / 69.610000 |
| Q2 | 44.300000 / 64.690000 | 44.925000 / 64.790000; 43.675000 / 64.790000 |
| Q10 | 113.000000 / 56.190000 | 113.625000 / 56.290000; 112.375000 / 56.290000 |

The JSON retains the complete derived coordinates/rotations. Q2 has a negligible sub-micrometre row-axis deviation in the accepted numerical export; the displayed table does not override the formula/JSON. Native implementation must preserve intended nominal package axes and compare actual resulting geometry, not copy rounded display values blindly.

New pad 9 paste area **2.995708 mm² = 61.1369%** of its unchanged exposed land. Nominal wet volume **0.299571 mm³**, reduced by approximately 38.86%. Actual AR per window **3.048**, minimum internal web **0.250 mm**, minimum clearance to retained drain-finger paste **approximately 0.200 mm** (worst stored calculation 0.199999 mm from 1 nm source quantization). This is a genuine two-window pattern after union with all retained pad contributions, not just overlapping new shapes laid on top of the old aperture.

Rationale: reduce the large contiguous central deposit and introduce a vent/separation channel while retaining full lead deposits. This addresses solder pooling, possible lift and voiding; it does not assert a measured failure or a manufacturer-required percentage. The accepted smaller copper land is not enlarged.

## U4 — large tab pad 2 only

Select physical pad UUID **`8de1b06f-f0ab-4d16-8a34-c3891d716649`**, center **(112.150000, 83.000000) mm**. Current aperture is a rounded **2.00×3.80 mm** envelope, actual area **7.385397 mm²**; wet volume **0.738540 mm³**. The separate small pin 2 at (105.850000, 83.000000) is excluded from this proposal.

Propose **four 0.75×1.50 mm rounded windows, R0.05**, aligned to global X/Y, centers:

- (111.650000, 82.100000) mm
- (111.650000, 83.900000) mm
- (112.650000, 82.100000) mm
- (112.650000, 83.900000) mm

New total paste area **4.491416 mm² = 60.815%** of the rounded exposed tab; nominal wet volume **0.449142 mm³**. Actual AR per window **2.544**. Internal webs **0.250 mm X / 0.300 mm Y**; minimum gap to any other retained aperture **1.400 mm**. All four windows fit inside the existing rounded land.

Rationale: subdivide the broad power tab and provide vent paths, consistent with JLCPCB's published power-tab stencil guidance. Small leads 1/2/3 are unchanged. The numerical coverage is an engineering starting point for first-article assembly, not an exact-component manufacturer qualification.

## Boundary of a later authorized implementation

A future task would first establish fresh production identity and use the repository's guarded isolated native KiCad 10 workflow. Derive a fresh scratch from the actual production board; alter only these four physical pads' paste contributions using supported APIs, never serialized text edits. Confirm original full apertures are genuinely removed, drain fingers remain separate, new windows have the stated area/containment/webs, and all other pasted regions are unchanged. Reuse the accepted copper/mask evidence and perform affected native checks, parity/preservation and focused diffs required by AGENTS.md. Only after owner review may a new paste export/order proceed.

This phase performed none of those CAD or export operations. Stencil tape for F0/F5 is a separate shared-stencil process choice; it does not remove DNP apertures from the authoritative board.
