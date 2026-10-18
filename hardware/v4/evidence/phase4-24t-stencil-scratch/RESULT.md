# Phase 4.24T — verified four-land stencil scratch candidate

2026-10-18. **PASS — SCRATCH ONLY. STOP for owner acceptance.**

The owner's approved four physical F.Paste corrections are installed in a fresh native KiCad 10 scratch project and verified against the actual owner-exported GTP. Production, its intentional silkscreen addition, the Gerber-to-Order ZIP and all protected manufacturing inputs remain unchanged.

## Quick start

1. Inspect the actual before/after images: [Q1](cam-verification/before-after-Q1.png), [Q2](cam-verification/before-after-Q2.png), [Q10](cam-verification/before-after-Q10.png), [U4](cam-verification/before-after-U4.png).
2. The review candidate is [candidate-v3/ups12v_v4.kicad_pcb](candidate-v3/ups12v_v4.kicad_pcb), with its copied project/schematic/rules and exact project-local library copies in the same directory. Its scratch-only actual paste export is [ups12v_v4-F_Paste.gtp](candidate-v3/paste-export/ups12v_v4-F_Paste.gtp).
3. Review the result below and [machine-readable physical aperture delta](cam-verification/physical-aperture-delta.json). **Do not substitute this scratch project or GTP into production.** A separately authorized phase must install the exact board-level correction; the owner will then manually re-export through Gerber to Order.

The intended stencil remains **top only, 0.10 mm, 1:1 as per Paste Layer**. No JLCPCB automatic aperture optimization is approved. No order/upload/purchase/commit/push occurred.

## Bound identities

| Artifact | SHA256 |
|---|---|
| Current production/source, unchanged | `8c68d920e71cea6373f9ee1f767f661d228ebafd6e1a00fadc580e00bc460e87` |
| Approved Phase4.24S proposal JSON, unchanged | `80f7d7d6155978dd882fa48a9497d5a1dc62d255c828ee9fbcbeaed0282efea3` |
| Original owner ZIP, unchanged | `7dd71cf2854a50915d2d82f91e62bba5974efc659a69f52fda5b44882dc86d95` |
| **Verified scratch candidate PCB** | **`d0a8c95a1b8cfbeff1f4f7fa4a95abf297a86d9c95551ed5b7b3050f42b8ac2b`** |
| **Scratch-only actual F.Paste Gerber** | **`bde8cbc17ee7e712a3d3eb56529752230332590bcd24ce0c4d62dc211bf9db49`** |

Fresh current-source baseline and read-only isolated snapshot were established before mutation. The earlier Phase4.21 hash is not used as the scratch source. The current production includes the owner's F.SilkS text addition, whose exact full-board preservation is established below.

## Exact implementation and actual-CAM result

Native `pcbnew` KiCad **10.0.7** edited only the candidate. The four original electrical pads retain all copper, mask, numbering, nets, pad geometry and other properties; only their F.Paste layer membership was removed. **Ten filled footprint graphics on F.Paste** replace those four full pad contributions. They have zero outline stroke. No helper electrical pads, drills or nets were added. Original pad count remains **473**.

The supported native rectangular-shape API supplies the exact R0.05 corners. The full-precision reviewed centers and rotations were passed to native vector/angle APIs and quantized only by KiCad's integer-nanometre coordinate representation. Q2's tiny deviation from 180 degrees is deliberately retained; native saving represents those two rotated shapes as polygons, so a rectangle-only radius scalar is not an applicable readback check. The composed exported geometry, including its rounded contours, matches the reviewed mathematical windows within **0.000005 mm (5 nm)**. This is a numerical comparison tolerance, not a manufacturing tolerance or a process guarantee. [Native API documentation](https://docs.kicad.org/doxygen/pcb__shape_8cpp_source.html) and installed introspection evidence establish API availability; actual saved/exported results establish success.

| Physical land | Removed original full contribution | Actual replacement | Area / exposed land | Actual AR at0.10mm | Internal web | Gap to retained neighboring paste |
|---|---|---|---:|---:|---:|---:|
| Q1.9 UUID `e4ac9e85-c811-4bc1-8b0f-fb744a86e69b` | 2.45×2.00 mm | 2×1.00×1.50 mm, R0.05 | **61.1369%** | **3.0480** each | **0.250 mm** | **0.199999 mm** |
| Q2.9 UUID `33d30c90-2a72-4b46-9865-95576d68a151` | 2.45×2.00 mm | same, proper reviewed rotation | **61.1369%** | **3.0480** each | **0.250 mm** | **0.200000 mm** |
| Q10.9 UUID `2afd57c8-68fa-4e00-b83b-d4a8134c24e4` | 2.45×2.00 mm | same, proper reviewed rotation | **61.1369%** | **3.0480** each | **0.250 mm** | **0.200000 mm** |
| U4 large tab2 UUID `8de1b06f-f0ab-4d16-8a34-c3891d716649` | rounded2.00×3.80 mm | 4×0.75×1.50 mm, R0.05 | **60.8148%** | **2.5438** each | **0.250/0.300 mm** | **1.400000 mm** |

The 1 nm difference at Q1 follows its retained source geometry; it is not a design-rule waiver. The measured U4 coverage rounds to60.81%; the earlier proposal displayed60.82% after decimal rounding. Actual area agrees with that proposal at the stated numerical tolerance.

**The original large paste contributions are actually absent.** Composed GTP removes approximately1.664291/1.664292/1.664292mm² of formerly pasted land at Q1/Q2/Q10 respectively, and2.893981mm² at U4. The MOSFET number is smaller than the full-pad area reduction because the overlapping drain fingers5–8 deliberately retain all their original paste. This is verified from the original individual Gerber contributions, not inferred from appearance.

Every proposed window lies within its original solderable exposed land. The whole candidate paste equals the union of **401 retained original pad contributions plus10 approved windows**, with **zero changed area outside the four authorized original lands**. No global reduction, overlay-only workaround, missing paste or extra deposit is accepted. U4's separate small pin2 is untouched.

The physical opening count changes **393→411**, as expected: each formerly joined MOSFET drain aperture becomes four preserved fingers plus two separated windows (+5 each), and the U4 tab becomes four openings (+3). Paste union area changes **443.156684→435.269828mm²**. Minimum actual area ratio anywhere remains **0.778346** at IC1. All other critical package apertures, including IC1, U1 and L1/L2/L3, are unchanged.

## Preservation and native checks

- **Independent native save/readback PASS.** A second native process reloads the saved candidate, compares its entire original electrical/copper geometry snapshot and filled-layout snapshot, then reverses only the ten added paste graphics and four paste-membership edits **in memory**. Saving that reversed state through KiCad reproduces the native baseline PCB **byte-for-byte**. It also hashes to the original current production identity above. No serialized CAD text was edited or used to patch the design. [Proof](candidate-v3/independent-readback-v2/result.json).
- Consequently original F.Cu/B.Cu/In1.Cu/In2.Cu, actual fills and holes, F.Mask/B.Mask, silkscreen including the owner addition, outline, nets, footprint placement/physical pads, drill geometry, rule settings and other board content are preserved. All **324 via UUIDs and their geometry** are unchanged. The accepted **41 component PTH and12 NPTH** hole classes/identities are unchanged; no component hole became a via or fill target. The full native byte comparison is stronger than a count-only check.
- **Read-only native DRC and schematic parity**, without refill/save: source **0 errors /0opens /0parity /16warnings**; candidate **0errors /0opens /0parity /18warnings**. Original16warning identities remain; added warnings are `lib_footprint_mismatch` for **Q2 and Q10** only, reflecting their intentional board-level paste changes relative to the untouched library. Q1/U4 already had corresponding library mismatch identities. Ignored checks are identical. There are no new physical/routing/clearance violations. [Exact warning delta](native-checks/warning-delta.json), [source report](native-checks/baseline-drc.json), [candidate report](native-checks/candidate-drc.json).
- Schematic/project/rules/library input files and BOM were not edited. Existing accepted ERC evidence is reused: this phase changes no circuit/pin map, and fresh DRC parity is zero. No routing or electrical audit was replayed, and no hardware/firmware testing was implied.
- **All182 offline toolkit tests PASS** (21.956s), including the existing safety/toolkit suite and the new physical-pad/authorization, native-layer-sequence and full-precision geometry tests. [Validation notes](VALIDATION.md).
- All **35 protected original inputs**, including26production CAD/library/BOM files, source ZIP, loose manufacturing files and accepted analysis evidence, remain byte-identical. [Final result manifest](final-result.json).

## Shared F0/F5 stencil handling

All19F5-only references retain their intended paste presence:18SMT references present, J8 absent as a through-hole connector. C20/C22/C24/C25 retain both apertures each and remain blocked for both variants. Other intentionally bare test/feature pads remain without paste. Q10's stencil pattern changes only as authorized.

The Phase4.24S [reference-level covering plan](../phase4-24s-stencil-audit/MASK_PLAN.md) remains geometrically applicable: new windows fit inside the same original covered lands, so its0.10mm outer margins and clearances to other references remain valid. Its old physical-aperture count refers to the original stencil. For this candidate **F0 blocks62physical apertures** (54on F5-only SMT parts plus8always-DNP); **F5 blocks8**. Candidate enabled physical openings: **F0=349**, **F5=403**. No DNP apertures were removed from CAD.

## Owner acceptance boundary

The **candidate-v3 PCB and its exact transaction/proposal** are the review result. No production installer was created or run. The production project and owner ZIP were not replaced. Subsequent installation must have separate owner authorization and preserve the exact verified paste geometry and all original board content; no library refresh or automatic JLC aperture transformation is authorized. The owner then manually generates the new Gerber-to-Order ZIP.

Physical print/reflow behavior, cap planarity and hardware joint quality remain outside this software verification. The previously selected0.10mm stencil and planar filled/capped-via assumption stand. **STOP after this verified scratch result.**
