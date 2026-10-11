# Phase 4.7 — scratch BATTERY layer change and PROG comparison

2026-10-11. **Scratch-only validation complete; STOP for owner review. Production accepted Batch 1 is unchanged.** No production CAD mutations, fabrication, purchasing, firmware, commit or push. No further layout optimization was undertaken.

## Result and recommendation

The exact approved BATTERY layer change removes the original crossing error and passes complete native configured DRC after refill. Both the proposed 28.651880 mm F.Cu route and a shorter 14.198947 mm F.Cu/B.Cu comparison have **0 non-unconnected errors / 251 remaining unconnected items / 20 library warnings / 0 schematic-parity issues**. This is a locally clean routing candidate on an intentionally incomplete board, not a fully routed/release-clean PCB.

**Prefer the 14.198947 mm candidate for owner review.** It halves PROG length without moving R5, NT1, C23, any other footprint or any further original power copper. Its two through-vias avoid the large right-hand detour. The original F.Cu escape still has finite BTST2/SW2 exposure; the B.Cu section lacks an immediately adjacent ground plane. The BATTERY change removes useful separate outer-layer copper; it must not be described as an electrically neutral layer reassignment. These limitations are detailed below. No thermal or startup-noise qualification is claimed.

## Exact CAD scope and copper geometry

Native KiCad **10.0.7** loaded the accepted saved production board. Only original track **`01ab1eb5-ab75-462d-9e54-2d6eab529481`** changes: BATTERY, width **0.60 mm**, **(63.1,65.5) → (63.8,66.9) mm**, centreline **1.565248 mm**, **F.Cu → In2.Cu**. Net, UUID, width, endpoints and geometry are preserved. Endpoint through-vias `e012a565-4061-4615-bf98-9d4d2d4121a8` and `10f4a91e-df97-47f0-ba3d-640a866ac795` remain Ø0.70/0.40 mm and unchanged on all four copper layers. No other original track or via changed.

The exact original-position BATP/PGND/ILIM_HIZ/TS subset is reused in both candidates: C23 stays **(71.5,66.3)/90°**; BATP total **14.166 mm** and PGND **0.305 mm** to the existing proposed scratch via **(71.5,65.525), Ø0.50/0.30 mm**. This subset is still scratch-only.

| Property | Original proposal | Preferred comparison |
|---|---|---|
| Scratch board | `phase4-7-layer-validation.kicad_pcb` | `phase4-7-layer-validation-shorter.kicad_pcb` |
| PROG width / endpoints | 0.10 mm; IC1.20 (61.9,66.0) to R5.1 (63.5875,71.2) | Identical |
| PROG centreline length | 28.651880 mm | **14.198947 mm**, 50.44% shorter |
| PROG copper | 34 F.Cu segments | 23 segments; F.Cu **8.181075 mm**, B.Cu **6.017871 mm** |
| PROG vias | None | Ø0.50/0.30 mm through-vias at **(67.6,65.08)** and **(64.78,70.01)** |
| Board tracks / vias / footprints | 310 / 139 / 154 | 299 / 141 / 154 |
| Added tracks / vias over Batch 1 | 58 / 1 | 47 / 3 |

R5 stays **(64.5,71.2)/0°, 27k 1%**. All footprint positions, orientations, values, pad geometry and pad nets match the baseline. R5.2 and the accepted GND return through NT1 are unchanged; no R5 adjustment was needed for the comparison. Both plans retain every original power item apart from the single authorized layer change.

Exact native-readback geometry, including all added subset segments and vias with UUIDs, layers, widths and endpoints, is in **`phase4-7-layer-validation-exact-copper.csv`** and **`phase4-7-layer-validation-shorter-exact-copper.csv`**. These tables and the saved scratch boards are the authoritative detailed geometry. Native-save diffs are saved separately for both candidates. The review images are generated from native-exported tracks/polygons, not screenshots or manufacturing outputs.

## Native DRC, connectivity, refill and preservation

For each scratch board, native CLI ran **pcb drc --all-track-errors --schematic-parity --refill-zones --save-board --format json**. Refill and save finished before readback. The existing In1 PGND fill remains **one polygon**. No new copper-clearance, copper-to-hole, via, zone, thermal-starvation, track-crossing or parity finding was reported by the configured rules. Native reread confirms all original vias, footprint/pad geometry and original tracks except the named BATTERY layer are unchanged.

The 20 warnings are **6 lib_footprint_issues + 14 lib_footprint_mismatch**, exactly identical to the prior native diagnostic and to each other. They are not presented as a fully validated project-local library context. The 251 unconnected items are exactly the same count for both candidates and the previous diagnostic; no whole-board routing completion is claimed. The prior diagnostic had one additional crossing error, now absent.

Project settings and available `.kicad_dru` were copied unchanged from production. Six inherited ignored check categories remain unchanged: missing_courtyard, track_not_centered_on_via, tuning_profile_track_geometries, footprint_filters_mismatch, silk_overlap and silk_over_copper. **No design-rule value/severity or exclusion was relaxed.** “Complete DRC” means KiCad's complete configured ruleset, not overriding these existing project choices.

Production PCB/schematic/project SHA256 hashes equal the accepted Batch1 capture before and after validation. Konnect IPC remains unavailable; a fresh live-editor capture could not be obtained (connection refused even outside sandbox). Therefore preservation claims concern the saved production files; unsaved live-editor state was not independently verified. No production file was saved/refilled by this investigation.

## BATTERY current-path assessment

The segment bridges two existing through-vias. In2 already contains the BATTERY **0.40 mm** vertical feed **(63.1,64.8)→(63.1,66.9)**, **0.70 mm** horizontal link **(63.1,66.9)→(63.8,66.9)**, and **1.50 mm** diagonal continuation **(63.8,66.9)→(64.5,67.6)**. These and every other original power conductor remain unchanged. There is no BATTERY zone in this local comparison; the broad apparent copper comes from tracks and via annuli.

The diagonal **does not merely duplicate existing In2 copper**. A 0.0025 mm raster screen of native exported circular-ended track strokes, subtracting through-drill voids, finds approximately **80% overlap** with existing same-net In2 copper and **0.193 mm² of added distinct In2 copper**. The corresponding removal loses approximately **0.578 mm² of distinct F.Cu copper**. These are local geometric area estimates, not an ampacity model; the earlier 84% footprint estimate included drill voids and is superseded by the copper-only screen.

Originally, the F.Cu diagonal provided a separate conductive branch between the via nodes, in parallel with the existing inner-layer L-shaped path. It could share current and spread heat on the outer face. After the move, most of the diagonal merges into existing In2 copper: overlapping same-layer strokes do **not** double copper thickness. It widens/cuts across the inner path locally, but removes the independent outer branch. Current entering from IC1's F.Cu BAT pin escapes is redistributed through the retained BATTERY vias into In2, and may return through downstream vias into F.Cu. Barrel current allocation and heat spreading therefore change even though logical connectivity does not.

For scale only, using **35 µm copper, 20°C copper resistivity 1.724e-8 Ωm**, the isolated 1.565248×0.60 mm branch has about **1.285 mΩ** longitudinal resistance. The existing inner path between these two via centres has approximately **4.5 squares**, or **2.217 mΩ** at the same assumed thickness, before accounting for broad junctions, overlapping copper and vias. This shows why the outer branch can provide useful conductance; these are not a network solution, measured current shares, a guaranteed resistance increase or a thermal qualification. Actual stackup thickness, via plating, current distribution and operating temperature were not measured. No new ampacity acceptance limit is imposed.

## PROG electrical/noise assessment

Manufacturer basis: [TI BQ25798 SLUSDV2C, revised June 2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf), checked 2026-10-11, **§7.3.2–7.3.4, Table7-1, §8.4.1–8.4.2**. PROG selects default cell count/frequency at POR; 27 kΩ corresponds to 4S/750 kHz. The documented sequence reads it about 5 ms after supply validity, before normal converter startup. Thus normal steady switching cannot by itself be assumed to corrupt POR sampling. Transient immunity has not been measured, and DRC does not test the resistance measurement. TI explicitly separates BATP/TS from SW nodes; applying similar care to PROG is engineering judgment rather than a quoted PROG-specific distance rule.

Native exported pads/tracks/vias were screened at ≤0.01 mm arclength spacing, on all copper layers, plus visually inspected. Distances are approximate edge-to-edge plan-view distances; projections across layers are **not** electrical shorts. Comparison bins 0.5/1 mm and 15° parallelism are analytical summaries, not manufacturer acceptance limits.

- **Common F.Cu escape:** nearest SW1 copper is about **1.925 mm** away; nearest F.Cu SW2 copper about **0.365–0.366 mm**. About **1.12 mm** of route lies within 0.5 mm of roughly parallel F.Cu BTST2 copper, with approximately **0.160 mm** minimum edge gap. This exposure remains in both candidates; shortening the far detour does not cure it.
- **Opposite-layer exposure:** the F.Cu escape projects over parts of B.Cu SW2 and runs over/along the B.Cu BTST2 trace **(62.5,66.25)→(65.8,66.25)**. About **4.57 mm** is within the 0.5 mm projected BTST2 bin. In1 PGND lies between F.Cu and B.Cu and provides useful shielding where filled; nearby through-via clearances interrupt it locally. This is a remaining layout risk, not a demonstrated POR failure.
- **Short candidate B.Cu section:** same-layer SW2 gap is approximately **1.790 mm**, SW1 **5.270 mm**. Nearest BTST2 gap is about **0.354 mm**, with **0.810 mm** in the <0.5 mm bin and **no close parallel track exposure** under the defined 15° screen. It therefore does not trade length reduction for a long same-layer switch/bootstrap parallel run.
- **Other power copper:** the short B.Cu section passes under existing BATTERY distribution on In2 and near BATTERY through-vias (sampled same-layer gap approximately **0.109 mm**). BATTERY is a filtered power rail, not SW1/SW2 or the bootstrap switching node, but it can carry ripple and supply transients. In2 is not a continuous adjacent PGND reference for B.Cu. The route stays well away from PMID/SYS switching-loop copper; full per-net/layer results are saved in the electrical-geometry JSON.
- **Ground coverage:** native filled-plane Contains sampling at ≤0.02 mm finds missing In1 ground beneath about **0.675 mm** of the long F.Cu route, and **1.583 mm F.Cu + 1.703 mm B.Cu** for the short route, including via-clearance areas. Presence at centre and ±0.3 mm was also checked. The short route has poorer projected reference continuity despite shorter length; these samples are not field-solver shielding or return-impedance results.

The shorter route is a practical prototype candidate for owner review: substantially less copper length, unchanged resistor/ground return, no close B.Cu switch-node parallel run and no new configured physical DRC errors. It is **not** proven universally less coupled than the longer ground-referenced F.Cu path. Remaining uncertainty is common escape coupling, inner power/via current redistribution, local ground openings and actual startup/thermal behavior. No additional protective circuit, microvia, power reroute or component move was introduced.

## Evidence and stop boundary

- Native DRC: `phase4-7-layer-validation-drc.json`, `phase4-7-layer-validation-shorter-drc.json`.
- Exact copper: both `...-exact-copper.csv`; native `...-build.json`, `...-preservation.json`, `...-native-save.diff`.
- Electrical screen: `phase4-7-layer-validation-electrical-geometry.json`, `phase4-7-layer-validation-plane-screen.json`.
- Visual review: `phase4-7-layer-validation-prog-review.png`, `phase4-7-layer-validation-battery-review.png`.
- Overall check and hashes: `phase4-7-layer-validation-summary.json`.

The previous no-layer via-width assertion is resolved: owner instructed **Continue**, explicit-layer via reads succeeded, both native scratch saves/reloads and DRCs completed without further native assertions. The earlier process had exited with code1; it was not suppressed or automatically recovered.

**STOP. Preferred candidate is saved and reviewable; production implementation requires separate owner approval. No further CAD work is authorized by this result.**
