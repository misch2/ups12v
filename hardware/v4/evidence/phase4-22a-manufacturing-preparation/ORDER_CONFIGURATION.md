# JLCPCB order-configuration decision sheet — REVIEW ONLY

Checked 2026-10-18. Fixed: FR-4, four layers, nominal **1.6 mm**, 96 × 70 mm accepted outline, one physical board for F0/F5. **Owner checked the live configurator and APPROVES 1oz outer/1oz inner, bare PCB only, self-assembly of both variants.** Observed inner-copper surcharge **USD16.84** is owner-supplied evidence, not an agent quotation or total board price. **2oz is explicitly not selected.** No agent order cart, upload or vendor engineering acceptance was created.

| Field | A: 1 oz outer + 1 oz inner | B: 1 oz outer + 0.5 oz inner |
|---|---|---|
| Decision | **OWNER APPROVED 2026-10-18** | Comparison only; not selected |
| Nominal analysis | 35 µm F/B assumption; **30.5 µm processed inner** per owner's calculator observation; retain 35 µm only as old-model reference | 35 µm F/B; 17.5 µm ideal half-ounce, plus 15.2 µm published-stack example sensitivity |
| Offered construction at four layers / 1.6 mm | **Owner verified available**; exact laminate schedule/ID not supplied | Published default-weight comparison; exact cart not captured |
| Exact offered/selected stackup code | **PENDING** | **PENDING**; published `JLC04161H-7628` is only an example, not an order commitment |
| Price, quantity tiers, lead time, shipping/tax and total | **USD16.84 observed surcharge only**; full quote/tiers/total **PENDING** | **PENDING quotation** |
| Actual copper thickness tolerance / guaranteed minimum per layer | **PENDING vendor commitment** | **PENDING vendor commitment** |
| Minimum via-barrel copper | **PENDING vendor commitment** | **PENDING vendor commitment** |
| Electrical consequence | At30.5µm, inner trace R is **1.148×** old35µm model; see sensitivity report | Larger SYS/BATTERY/PGND and F5 inner-path resistance; see sensitivity report |

The [official copper guide](https://jlcpcb.com/help/article/jlcpcb-copper-weight), updated 2026-09-09 and retrieved 2026-10-18, lists inner 0.5/1/2 oz, with availability dependent on layers/thickness. It specifies **0.09 mm trace/space for ≥4-layer FR-4 with 0.5 or 1 oz**. The accepted 0.100 mm minimum therefore fits the published capability for both comparisons. **Confirm applicability to the exact quoted construction**, including any layer-dependent restrictions. This is capability screening, not CAM acceptance.

The [published stackup page](https://jlcpcb.com/impedance), retrieved 2026-10-18, has selectors for1.6mm and both inner weights. Its static example `JLC04161H-7628` lists outer0.035mm and inner0.0152mm; it is **not** the selected1oz-inner code. The owner's live-calculator observation supplies approximately **30.5µm processed1oz inner**, not a guaranteed minimum. That dynamic setting/code was not independently captured by the static page fetch; source attribution remains owner-reported. No exact1/1 stackup ID is asserted. The saved0.100/1.240/0.100mm dielectric model is not a manufacturing specification. **No controlled impedance or particular stackup is required without demonstrated need.**

The [rigid capabilities page](https://jlcpcb.com/capabilities/pcb-capabilities/), retrieved 2026-10-18, lists **average** hole plating 18 µm and trace-width tolerance ±20%; neither supplies minimum copper/barrel thickness. Its standard ≥1 mm board-thickness tolerance is ±10%: nominal 1.6 mm can finish at **1.44–1.76 mm**. All resistance/thermal assumptions must be tied to the eventual contract. Nominal thickness stays 1.6 mm regardless of tolerance disposition.

## Complete the actual order record next phase

| Setting / choice | Current decision state |
|---|---|
| Fabricator / layer order | JLCPCB fixed; F.Cu / In1.Cu PGND / In2.Cu / B.Cu; no rearrangement |
| Service tier and material/laminate/Tg | Exact offered FR-4 service/material **PENDING**, record shown option; do not infer impedance service from the stackup page |
| Finished thickness | Nominal **1.6 mm fixed**; owner accepts standard-process Nano-Fit prototype tolerance risk, including the previously documented thickness/locator/position gaps; no conformity claim |
| Copper / stackup / barrel | **A selected**; record offered schedule/identity if established and any actual tolerance/minimum evidence; unknown copper and barrel minima stay explicit |
| Surface finish / mask / legend | Exact finish and mask color **PENDING**; green mask / white legend is a practical proposal only. Preserve accepted openings and artwork; external assembly map addresses dense silk |
| Via process | Through vias; minimum existing drill0.30mm. Front/back tenting intended. Owner reports free **Plugged (ink)** available, not a confirmed selection or epoxy/copper cap. Actual via-in-pad/near-opening exclusions require [process disposition](VIA_PAD_ASSEMBLY.md) |
| Drills/slots | Separate PTH and NPTH, preserve plated J7 slots and Nano-Fit round/oval locators; obtain tolerance disposition, not nominal resizing |
| Outline/panelization | Accepted 96 × 70 mm routed rectangle, four 3.2 mm NPTH mounts. Single-board delivery proposed; no V-score, castellations or edge plating. Any panel/tooling addition needs separate scope approval |
| Impedance | No new controlled-impedance requirement. Do not permit vendor auto-adjustment of accepted widths/spacing; changes need separate authorization |
| Quantity / delivery / stencil | Owner quantity, delivery and optional stencil choice **PENDING**. **Bare PCB only approved; self-assembly both F0/F5**. Stencil/paste process needs QFN/AON/module/open-via review before assembly |
| Order-number marking / electrical test / CAM changes | Record offered marking location and test service; ensure no functional-pad/antenna conflict. No automatic geometry or footprint changes authorized |

Retained [Phase 4.19 DFM screen](../phase4-19-final-audit/REVIEW.md) and [Phase 4.21 vendor screen](../phase4-21-production-adoption/vendor-screen.json) cover minimum features, hole gaps, PTH rings, outline, mask/paste and unchanged warnings. J7 0.350 mm clearance is already resolved. Do not reopen routing or treat a generic wrapper as additional vendor acceptance.
