# Phase 4.24S — actual solder-paste stencil audit

2026-10-18. **B — LOCAL PASTE CHANGE RECOMMENDED**, limited to Q1/Q2/Q10 pad 9 and U4's large tab, pad 2. Prepare the bounded scratch candidate described below before ordering; then retain **1:1 as per Paste Layer**, top only, 0.10 mm steel. Do not delegate the final aperture geometry to automatic standard processing. This is an engineering assembly recommendation, not proof that the present stencil cannot print or reflow successfully.

No CAD, library, paste layer, Gerber, drill, ZIP, BOM or manufacturing setting was changed. No upload, purchase, commit or push. **STOP for owner review before any implementation or order.**

## Quick start for the owner

1. Review the four-pad proposal in [CORRECTION_PROPOSAL.md](CORRECTION_PROPOSAL.md). It is mathematical evidence only, not a new manufacturing file.
2. Retain the accepted IC1 pattern, U1's existing nine EPAD islands, L1/L2/L3 and all other paste. Neither a global reduction nor extra paste everywhere is justified.
3. Use [MASK_PLAN.md](MASK_PLAN.md) when printing F0/F5. Four always-DNP capacitors need blocking in both variants; F0 additionally blocks 18 F5 SMT references. J8 has no paste to block.
4. If a correction is authorized later, verify its isolated native scratch/export before approving 1:1 stencil production. The current ZIP remains the audited original.

## Identity and actual export

The supplied [owner ZIP](../../ups_v4/gerber_to_order/ups12v_v4_96.0x70.0mm_for_JLCPCB.zip) has SHA256 `7dd71cf2854a50915d2d82f91e62bba5974efc659a69f52fda5b44882dc86d95`. It is **not** the older ZIP hash `b07e1a3c…96e6c` in the preceding incomplete Phase 4.24 run. See [fresh member hashes/metadata](final-v2/zip-manifest.json).

Accepted geometry baseline: PCB SHA256 `4eb7bd2c72fec3cf49d3746250864b5237e7919760ebdbc3647cbc0101fa8737`. Current saved PCB: `8c68d920e71cea6373f9ee1f767f661d228ebafd6e1a00fadc580e00bc460e87`. Read-only Git provenance establishes that the accepted bytes equal `b8e18ba` with working-tree CRLF; current bytes equal HEAD with CRLF. Their entire diff is the 13-line F.SilkS text addition in `b6c7d51` ("add silkscreen text"). This resolves the hash discrepancy without pretending the files are byte-identical. [Recorded proof](identity-provenance.json).

The accepted native context, layout and manifest still match their previously recorded hashes. Fresh composition of actual GTL/GTS matches accepted F.Cu/F.Mask polygons: **zero missing or extra area beyond 0.00025 mm numerical tolerance**. Raw polygon differences are retained; the tolerance is not a fabrication allowance. No Gerber generation or repeated routing/electrical audit was needed. See [top-layer comparison](final-v2/accepted-top-geometry-comparison.json).

GTP contains **405 flash/object regions but 393 physical connected stencil openings**. The three MOSFET drain groups each join five flashed regions into one aperture. GBP has **0 objects / 0 mm²**. Every GTP region is assigned to an accepted physical pad UUID; none is missing against native F.Paste layer membership, none unexpected, and none extends beyond its intended exposed land at the stated numerical tolerance. All SMT paste/land area ratios are approximately **100%** here (small curve-tessellation differences only). Therefore 1:1 reproduces these particular unreduced lands; this conclusion comes from CAM geometry, not a generic assumption about KiCad settings.

Copper land areas and actual GTL∩GTS exposed areas are recorded per physical pad in [stencil-audit.json](final-v2/stencil-audit.json). Mask openings do not clip these paste lands. Filled/capped vias are counted as planar solderable copper, not subtracted as open bores.

## Critical-pad comparison

Dimensions in mm; areas in mm²; AR = actual opening area / (opening perimeter × 0.10). "100%" uses actual mask-exposed copper land, not package body area. Rounded rectangle dimensions describe the outside envelope; area uses its actual corners. C denotes process actions below, D denotes unverified process qualification, not a discovered geometry defect.

| Ref / pads | Actual copper/exposed land and GTP | Current openings / coverage | AR at 0.10 mm / separation | Disposition |
|---|---|---|---|---|
| IC1 BQ25798, 1–29 | 17 small 0.20×0.60; other straight leads 0.20×0.65/0.68/0.70/0.95/1.00; corner 1/9/16/24 L shapes, envelopes 0.70×0.90/0.95 | 29 separate, 100%; no central thermal rectangle to invent | min **0.778**; rectangle model 0.750 for 0.20×0.60; min web **0.200** | **A**, retain exact RQM pattern |
| U1, 1–48 | 0.40×0.80 | 48, 100% | 1.333; min module gap 0.350 | **A/C** |
| U1, 49 (nine physical lands) | 9×1.45×1.45; exposed total18.9225 | 9 windows, 100% of lands; **64.89% of5.4×5.4 envelope** | 3.625; neighboring central windows0.525 | **A/C/D**, retain segmentation; do not reduce again merely because each island is100% |
| U1, 50–53 | 0.70×0.70 | 4, 100% | 1.750 | **A/C** |
| U3/U7 TPS62933 and U5 TPS2116, 1–8 | 0.30×0.67 rounded; ~0.198854 exposed each | 8 per package, 100%; **no EPAD** | 1.072; rectangle1.036; web0.200 | **A**, matches DRL stencil envelope |
| Q1/Q2/Q10, 1–4 | 0.40×0.65 | 4 per part, 100% | 1.238; gaps between leads0.240/0.260 | **A**, preserve |
| Q1/Q2/Q10, 5–9 | pad9=2.45×2.00, exposed4.900; pads5–8=0.40×0.60 | **One joined, unwindowed drain opening per part**, area~5.620; 2.45×2.45 envelope;100% of exposed drain union | physical joined AR~4.496; zero gap inside same-net drain group is intentional, not a short | **B**, split pad9 paste; retain5–8 |
| L1, 1/2 | 2.90×5.40; exposed15.660 each | 2, 100%; no windows | 9.434; nominal wet paste1.566mm³ per terminal | **A/C/D**, capped24vias; retain large terminal deposits |
| L2/L3, 1/2 | 1.18×4.70 rounded; exposed~5.49235 each | 2 per part,100% | 4.847; wet paste0.549235mm³ per terminal | **A/C**, balanced accessible end joints |
| U4 AP7361C, large tab2 | 2.00×3.80 rounded; exposed7.385397 | 1 full tab,100% | 6.876; wet paste0.738540mm³ | **B**, four windows |
| U4, small1/2/3 | 1.50×2.00 rounded; exposed~2.879286 each | 3,100% | 4.530 | **A**, small pin2 is not the tab |
| U8 LM74700, 1–6 | 0.60×1.325 rounded; exposed~0.775686 each | 6,100% | 2.159; web0.350 | **A/C/D**, thinner than TI's0.125 example |
| U6 TCA9517, 1–8 | 0.50×1.625 rounded; exposed~0.799087 each | 8,100% | 1.980; **web0.150**, smallest between independent leads | **A/C**, inspect printing/bridges; no AR concern |
| U2 TPD2EUSB30ADRTR, 1–3 | 0.30×0.30 rounded; exposed~0.085171 each | 3,100% | 0.795; web0.400 | **A/C/D**, exact DRT, not DQA stencil diagram |
| 0402 R/C and USB series/support passives | R min width0.540; C min0.560; retained rounded geometry | all expected pads;100% | minAR1.550/1.559; min gap0.440/0.400 | **A/C**; no blanket reduction |

All remaining pasted passives/transistors/diodes/switches were included in the 405-region geometry screen. Larger passives have no aperture-release limitation. Their exact metric dimensions, nominal wet volumes and neighbors are in [apertures.csv](final-v2/apertures.csv). These are wet-paste volumes at perfect transfer, **not** final solder volume or measured transfer efficiency.

## Manufacturer comparison and interpretation

Sources were checked 2026-10-18; exact revisions, sections/drawings, links and saved references are in [SOURCES.md](SOURCES.md).

- **TI RQM0029A, drawing4225253/A11/2019**, BQ25798 RevC appendix p150: the actual IC1 pattern follows the0.10mm stencil example, including the L-shaped corner leads. A generic QFN central windowpane rule would be wrong for this package. Its narrow0.20mm apertures are the limiting release geometry but have positive calculated margin. Retain them.
- **TI DRL0008A, drawing4224486/G11/2024**, TPS62933 RevD p50 and TPS2116 RevA p24:8×0.30×0.67,R0.05,0.10mm steel. Actual U3/U5/U7 agrees in envelope; actual corner radius/area are measured rather than forced to match the drawing. No large hidden pad exists.
- **Espressif MINI-1 v2.2 §9, §10.1/§11.1** warns that excessive EPAD paste can lift the module. Actual U1 already has nine distinct central windows. At0.10mm its central nominal wet volume is1.89225mm³; edge/corner total1.732mm³. No exact manufacturer percentage was found that establishes a need to shrink these islands further. Retain the grid, do not add a hand-dispensed central mound, and inspect first-article seating.64.89% of a geometric envelope is **not** a claim of64.89% coverage of the actual nine metal lands.
- **AOS AON7528 Rev1.0 October2023 / PO-00093H** confirms the exact package and IR-reflow qualification, but does not prescribe the proposed stencil percentage. The accepted2.45×2.00mm land is retained. Splitting its large contiguous drain deposit is a calculated assembly recommendation to reduce pooling/lift and provide vent paths; the proposed61.14% land coverage is **not an AOS mandate or a guarantee of void fraction**. AOS DrMOS-specific paste guidance is not treated as exact AON7528 evidence.
- **U4:** Diodes AP7361C DS37274 Rev5-2 gives land geometry, not this window design. JLCPCB's stencil process standard §4 calls for bridges/subdivision on large power tabs. The proposed60.82% tab coverage leaves the three small-lead deposits unchanged. This is a bounded paste decision, not reopening the copper footprint.
- **L1 Eaton DR125 Technical Data 4315, September 2017 p6:** terminal/land drawing, no exact paste percentage. Accepted land deviation stands. Two equally thick 0.10 mm deposits on separate accessible terminals do not establish the same float mechanism as a central hidden EPAD; automatic thinning would risk starved high-current joints. Keep full lands with planar caps and controlled heating. **L2/L3 Coilcraft XAL50xx Document 908, revised 2026-02-26:** the current electrical sheet gives no stencil/land drawing; accepted native geometry remains the basis, with no newly verified exact-component paste percentage.
- **U6 DGK:** latest TI drawing 4214862/A, 04/2023 uses 0.45×1.40; actual 0.50×1.625 is broader with a 0.150 web. The current diagram does not establish stencil thickness. This is a bridging/first-print watch item, not an automatic rejection. **U8 DBV** TI 4214840/G, 08/2024 uses 0.60×1.10 at 0.125 mm; actual 0.60×1.325 at 0.10 mm has about **94.3%** of that nominal wet volume (actual rounded area versus TI's R0.05 example). No extra paste is prescribed. **U2** DRT-specific aperture recommendation was not established from the accessed datasheet; DQA pages apply to a different package.

## C — assembly-process actions only

Follow the exact [reference-level tape plan](MASK_PLAN.md). Use thin, removable tape on the **paste-application side**, kept within the listed cover rectangles; no board-side tape that lifts the stencil. Rectangles include0.10mm beyond each reference's outer paste bounds and have no overlap with any other aperture. The minimum remaining clearance is0.450mm (C63/C66). Geometric feasibility is established; tape tack, thickness, solvent compatibility and squeegee snagging remain process variables. Inspect after cleaning and after every variant change. Avoid thick stacks. Covering the whole component area, including the unused gap between its pads, is intentional.

Seat and support the bare board flat in the owner's existing fixture; do a first print and inspect under magnification **before** placing parts. Confirm complete IC1/U2 transfers, no smear at U6 and equal opposing inductor deposits. A paste supplier's process suitable for0.20mm openings is needed; powder, alloy, flux, squeegee pressure/speed, separation and coating performance are not known here. Clear a defective print and reprint; do not compensate globally with hand-added paste.

Use controlled preheat/reflow or controlled hot air consistent with the selected paste and each component's reflow limits. Large L1 terminals and the ground-rich U1/Q/U4 regions need actual heat reaching the joint, not just melting visible paste at an edge. Inspect seating, fillets and bridges. Hidden-joint voiding/wetting cannot be certified visually from the top; X-ray is useful when available, otherwise record this limit and observe the assembled prototype. No power-up was performed or authorized here.

The calculation assumes **all324vias properly epoxy-filled, copper-capped and planar/solderable**, subject to JLC CAM acceptance. If uncapped/open vias are supplied, solder can drain into barrels, particularly L1's24 and Q1/Q2's4each; hidden-joint starvation, voiding and opposite-side leakage become materially different problems. Ink plugging/tenting alone is not an equivalent solderable cap. Stop the affected assembly for process disposition; neither extra paste nor these window reductions are a demonstrated fix for a fabrication deviation.

Top-only, frameless120×120mm is geometrically compatible with the96×70mm board (nominal centered margins12/25mm). Stencil origin/placement in the120mm sheet must match the existing fixture. Electropolishing/nano-coating may help transfer; neither supplies missing process qualification.

## D — remaining unverified matters and release boundary

Exact paste material/metal loading/particle distribution, actual transfer, stencil cut tolerance/taper/coating, cap planarity, exact hot-air/reflow profile and first-article hidden-joint quality are unmeasured. Manufacturer-specific stencil percentages for AON7528, AP7361C, DR125, XAL parts and MINI-1 were not established; the four-pad proposal is explicitly engineering-derived. No new electrical/thermal performance claim or sourcing refresh is made.

JLCPCB publishes its standard processing rules, so the policy is not wholly undocumented; its exact transformation of this mixed board has not been reviewed. It would change more than the four proposed pads, potentially including the accepted fine-pitch patterns. Prefer explicit local paste geometry followed by **1:1**, retaining Confirm Production File=Yes and owner review. No automatic global CAM changes are approved.

Phase4.22A/B manufacturing and population evidence was reused. No separate Phase4.23 decision document was found; the owner's current task supplies the later accepted MPNs and filled/capped assumption and supersedes older pending wording.21focused export-only tests pass. Final preservation covers35input files including26protected production CAD/library/BOM files and the supplied ZIP/loose manufacturing files. No native KiCad/editor operations, ERC/DRC repeat, firmware build or hardware test; none is required for this non-CAD aperture analysis. [Full validation and run notes](VALIDATION.md).

## Close-ups and detailed evidence

Actual parsed GTP over actual GTL/GTS, top coordinate view: [IC1](final-v2/overlay-IC1.png), [Q1](final-v2/overlay-Q1.png), [Q2](final-v2/overlay-Q2.png), [Q10](final-v2/overlay-Q10.png), [L1](final-v2/overlay-L1.png), [U1](final-v2/overlay-U1.png), [U3](final-v2/overlay-U3.png), [U7](final-v2/overlay-U7.png), [U4](final-v2/overlay-U4.png). White paste, brown copper, cyan mask-opening contour, red native pad numbers. Where paste equals the full exposed land the copper/mask beneath it is intentionally obscured; numerical per-pad measurements remain authoritative. Open drill holes are not superimposed on surfaces assumed to be capped.

**Owner review STOP.** This report does not authorize stencil/CAD/export modification, manufacturing release/upload or an order.
