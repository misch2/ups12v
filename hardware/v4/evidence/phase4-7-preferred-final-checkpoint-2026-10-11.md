# Preferred PROG route — final bounded scratch checkpoint

2026-10-11. **Recommend the exact 14.198947 mm candidate for the next production routing batch, subject to owner approval. STOP; production installation is not authorized by this validation.**

## Scope and reproducibility

Used the canonical `hardware/v4/tools/` without modification or expansion. All 13 regression tests passed. The sandbox denied temporary-directory creation and production PCB reads; approved elevated reruns passed. Fresh isolated read-only snapshot: `phase4-7-preferred-final-smoke/`. No unexpected native assertion or IPC failure occurred.

The route plan `phase4-7-preferred-final-plan.json` is a direct transcription of **add** rows in the previously validated `phase4-7-layer-validation-shorter-exact-copper.csv`, not a new candidate or search. Independent comparison of final native readback against the historical shorter candidate confirms identical complete track/via geometry (ignoring newly generated added-object UUIDs).

Accepted baseline: `c9-apply-phase4-7-batch1-final-ipc.json`. Native KiCad **10.0.7** changed only original BATTERY track `01ab1eb5-ab75-462d-9e54-2d6eab529481`, F.Cu → In2.Cu; width 0.60 mm and endpoints (63.1,65.5) → (63.8,66.9) remain exact. Original endpoint vias remain unchanged. Original-position BATP/PGND/ILIM_HIZ/TS subset reused exactly; no C23, R5, NT1 or other component relocation.

PROG: 0.10 mm, **14.198946620 mm**, F.Cu **8.181075410 mm**, B.Cu **6.017871209 mm**. Two Ø0.50/0.30 mm through-vias at **(67.6,65.08)** and **(64.78,70.01)**. Total additions: 47 tracks / 3 vias, including the subset's PGND via. Final board: 299 tracks / 141 vias / 154 footprints / 473 pads.

## Checks and preservation

Fresh native scratch save/reload, full configured DRC with refill/save and schematic parity, and post-check reload all passed:

- DRC: **0 physical errors / 251 unconnected items / 20 warnings / 0 parity issues**. Board remains intentionally incompletely routed.
- All 20 DRC warnings have the same type/description multiset as the previously validated candidate: 6 library-footprint issues and 14 library-footprint mismatches. These are library-validation findings, not newly introduced copper violations; they remain unresolved and must not be treated as a production library pass.
- Scratch ERC only: **0 errors / 11 warnings**. Four known isolated-label warnings; six missing `ups_v4` footprint-library links and one missing `ups_v4_custom` symbol-library context. The seven context warnings result from the isolated project context. **This is not production ERC.**
- All original tracks except the one declared layer, all original vias with layer-specific widths/drills, footprint metadata and pad geometry/nets/drills preserved. Added geometry matches the declared plan after reload and refill. In1 PGND remains one filled contour.
- Rules/sidecars and six inherited ignored check categories remain unchanged. Native-save diff inspected: route additions, moved original track and native filled-polygon updates only; no footprint, outline or rule-area edit. A few remote fill contour vertices were re-tessellated by native refill; exact fill-byte identity is not claimed.
- Production PCB/schematic/project SHA256 hashes equal accepted Batch 1 before and after. No production save/refill occurred. No current unsaved live-editor reconciliation is claimed.

Full artifacts: `phase4-7-preferred-final-validation/summary.json`, `preservation.json`, `expected-added.json`, `before.json`, `final-snapshot.json`, `focused-review.json`, `drc.json`, `erc.json`, `native-save.diff` and monitored worker/check logs.

## Focused visual inspection

Inspected `phase4-7-preferred-final-validation/review-F_Cu.png`, `review-B_Cu.png`, `review-In2_Cu.png`. They show PROG, BATTERY, SW2, BTST2 and nearby ground pads/tracks/vias. Dashed magenta is the other-layer PROG projection, not same-layer copper. The only ground zone is on In1, not any of these three layers; its unchanged one-contour status is recorded separately. The renderer reads exported toolkit JSON only and contains no native API or CAD-file access. Filled-zone exports omit hole topology; the images are review illustrations, not manufacturing artwork or proof of ground continuity. Ground-reference assessment below reuses the prior native Contains screen.

## Electrical comparison and recommendation

Prior quantified electrical screen is reused because independent native readback proves identical track/via geometry. See `phase4-7-layer-validation-checkpoint-2026-10-11.md` and its electrical-geometry/plane-screen JSON for detailed assumptions and results; no new clearance threshold is imposed.

| Consideration | 28.651880 mm all-F.Cu | 14.198947 mm preferred F.Cu/B.Cu |
|---|---|---|
| Length / vias | Longer; no PROG vias | 50.44% shorter; two added through-vias |
| Common escape coupling | ~0.160 mm minimum BTST2 gap; ~1.12 mm close parallel exposure | Same exposure remains |
| Short-route bottom coupling | Not applicable | SW2 gap ~1.790 mm; BTST2 ~0.354 mm, without close parallelism in prior screen |
| Return reference | Better In1 projection continuity; ~0.675 mm missing ground in prior sample | B.Cu has In2 power copper adjacent, not continuous ground; ~1.583 mm F.Cu + 1.703 mm B.Cu lack projected In1 ground |
| BATTERY consequence | Same one-track layer move | Same one-track layer move; B.Cu PROG also crosses beneath BATTERY distribution |

The short route avoids the large detour while retaining resistor/ground-return geometry and avoiding a long same-layer switch/bootstrap parallel run. It is electrically reasonable for the approved prototype milestone, **not proven universally less noise-coupled**. Its two via clearances interrupt In1 locally, and B.Cu lacks an adjacent continuous ground reference. BATTERY ripple/transients remain a possible coupling mechanism. No startup-noise or thermal measurements exist for this change.

Manufacturer basis rechecked 2026-10-11: [TI BQ25798 SLUSDV2C, revised June 2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf), §7.3.3–7.3.4 and §8.4.1–8.4.2. PROG is read during POR, typically 5 ms after supply validity, before normal input-powered converter startup. This supports the bounded prototype recommendation; it does not establish immunity to supply transients. Applying sensitive-route separation to PROG is engineering judgment, not a datasheet-specific PROG clearance rule.

For **both** variants, moving BATTERY removes an independent F.Cu parallel branch and outer-face heat spreading. About 80% of relocated copper overlaps existing In2 in the prior copper-only raster screen (~0.193 mm² distinct In2 added vs ~0.578 mm² distinct F.Cu removed). Same-layer overlap does not double thickness. Current redistributes through retained vias/In2. Prior 35 µm/20°C estimates (~1.285 mΩ isolated outer branch; ~2.217 mΩ existing inner L-path before junction/via corrections) illustrate useful lost outer conductance, not solved current shares, guaranteed ampacity or measured temperature. Actual copper/plating, load and temperature must govern later hardware validation.

**Recommend this exact shorter candidate for separate owner approval of the next production batch.** Its benefit is reduced routing length with acceptable prototype tradeoffs, while acknowledging common escape noise exposure, reference discontinuities and the shared BATTERY current/thermal penalty.

## Mandatory next boundary

STOP. After explicit production approval, first coordinate a safe installation procedure: reconcile live versus saved state and ensure no external native overwrite of an open/locked board. Use live IPC or an explicitly coordinated closed-board workflow, with fresh production ERC/DRC/parity, routing/geometry readback and diff review. A saved scratch pass cannot substitute for those production checks.

No routing search, clearance relaxation, component relocation, toolkit expansion, production modification, fabrication, purchasing, firmware, commit or push.
