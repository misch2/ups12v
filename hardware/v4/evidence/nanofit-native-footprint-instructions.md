# Nano-Fit — native KiCad 10 footprint correction

2026-10-11. The four selected Molex parts and harness pin assignments remain **APPROVED**. This is a library-only owner GUI task. Do not change the production board/schematic yet, replace connector families, route, fabricate, purchase, commit or push.

**Verification limit: do not execute the locator edits until sheet 1's actual Rev J1 figure is visible.** Manufacturer PDF text confirms the round/slot dimensions below, but the tools did not deliver a usable current-page image. Therefore the round-versus-slot assignment to the two ends and the slot's long-axis orientation are NOT independently verified. The old local Rev F image is not authority for these details. No guessed endpoint/axis is supplied here. If the current drawing cannot be viewed, provide the Rev J1 PDF or a legible crop of its recommended PCB figure before editing holes.

Authoritative source: [Molex SD-105313-100, Rev J1, released 2025-06-26](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/105/105313/1053131102_sd.pdf), sheet 1 recommended PCB **connector-side view**, sheet 2 keys, sheet 3 selected part dimensions. Current PDF text was rechecked 2026-10-11; direct downloads failed and browser/PDF screenshot tools supplied no usable image. No local current PDF is claimed.

## 1. Make project-local copies using the GUI

Open the V4 project `C:/Users/Michal/Git/my/ups12v/hardware/v4/ups_v4/ups12v_v4.kicad_pro`. Launch **Footprint Editor**. In **Preferences → Manage Footprint Libraries → Project Specific Libraries**, confirm nickname `ups_v4` points to `${KIPRJMOD}/ups_v4.pretty`.

Open each stock `Connector_Molex` footprint and use **File → Save As…** into that existing project library, with these new names:

| Installed source | Project-local copy | Selected use |
|---|---|---|
| `Molex_Nano-Fit_105313-xx02_1x02_P2.50mm_Horizontal` | `ups_v4:Molex_Nano-Fit_105313-xx02_1x02_P2.50mm_Horizontal_RevJ1` | J1 1053131102, black/key A; J3 1053132102, natural/key B |
| `Molex_Nano-Fit_105313-xx03_1x03_P2.50mm_Horizontal` | `ups_v4:Molex_Nano-Fit_105313-xx03_1x03_P2.50mm_Horizontal_RevJ1` | J2 1053131103, black/key A; J8 1053132103, natural/key B |

Save to `C:/Users/Michal/Git/my/ups12v/hardware/v4/ups_v4/ups_v4.pretty/`. Do not overwrite installed global footprints or the existing external-library alias. Do not use a text editor on library/project/CAD files. Preserve the footprint origin, body/courtyard, graphics, models, attributes and electrical pads. Add a description note citing SD-105313-100 Rev J1 and the actual locator tolerances after visual confirmation.

## 2. Establish the drawing-to-footprint transform

Use millimetres and the unrotated **front/component-side** library view. Existing pad 1 is the origin. Electrical pins run along local +Y; the body/locators lie toward local +X. The drawing is a connector-side PCB view, not the harness mating view. Align its CKT 1 and numbered row with library pad 1 before reading hole assignment. Do not mirror the pattern or renumber contacts.

Confirmed installed coordinates, which are the two locator centres to review against the current figure:

| Footprint | Electrical pad centres (mm) | Locator centres (mm) |
|---|---|---|
| 2-position | 1=(0,0), 2=(0,2.50) | (7.18,0), (7.18,2.50) |
| 3-position | 1=(0,0), 2=(0,2.50), 3=(0,5.00) | (7.18,0), (7.18,5.00) |

The present two Ø1.70 mm NPTHs are obsolete relative to the current callouts. In the actual Rev J1 figure, identify the round locator end, slotted locator end and long-axis direction. Record which local coordinate receives each. **Do not assume the slot is at the last-circuit end or parallel to the pin row.** If the figure contradicts these centre coordinates, stop and report the discrepancy instead of compensating by moving electrical pads.

## 3. Edit only the two mechanical holes in Pad Properties

[KiCad 10 Pad Properties documentation](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#editing-pad-properties) distinguishes non-plated mechanical pads from electrical plated pads and exposes circular/oval hole settings.

Hover each unnumbered locator and press **E**. On **General**, retain/set **Pad type: NPTH, Mechanical**, blank pad number, no electrical net, no paste aperture. These are insulating locating features, not plated shell/retention contacts. Do not edit similarly located numbered electrical pads.

| Feature identified in current figure | Native hole setting | Nominal finished dimensions | Manufacturer tolerance |
|---|---|---|---|
| Round locator | Hole shape **Circular** | Ø1.60 mm | +0.05 / −0.00 mm |
| Slotted locator | Hole shape **Oval/Oblong** | width 1.60 mm × overall length 1.75 mm | width +0.05 / −0.00 mm; length +0.10 / −0.00 mm |

For the slot, set **hole size**, not only pad shape. At pad angle 0°, if the verified long axis is local X, enter hole X=1.75/Y=1.60; if it is local Y, enter X=1.60/Y=1.75. Keep the slot centred at its verified locator coordinate with no offset. Set the NPTH pad outline to the same oval dimensions and no copper annulus; preserve the stock mechanical layer/mask conventions. A circular hole with an oval drawing/pad is not a slot. Do not use Ø1.75 mm, overlapping round holes, or hand-drawn approximate geometry. The oval dimensions are overall extents, not centre travel (the straight centre travel is only 0.15 mm).

Reopen both pad dialogs after saving to confirm actual hole shapes, dimensions, centres and angle persisted. No production board net assignments are changed by editing a library copy.

## 4. Preserve and check every electrical pad

Read back independently against [captured installed geometry](nanofit-manual-correction-baseline.json): each electrical pad remains **plated through-hole**, Ø1.20 mm circular drill; copper size **2.20 × 1.70 mm**, pad angle 0°. Pad 1 stays round-rectangle with existing rounding ratio 0.147059; pads 2/3 stay oval. Keep all copper/mask layers, numbering and positions unchanged. Manufacturer electrical-hole tolerance is ±0.05 mm; nominal remains 1.20 mm. Preserve 2.50 mm pitch. A blank mechanical pad must never acquire pad number 1/2/3.

Review both count variants separately. Sheet 2 identifies black/key A and natural/key B; sheet 3 gives a common PCB pattern for each selected circuit count, so two local footprints serve all four approved MPNs. Do not alter locator geometry to encode key/color. Preserve mating-body/courtyard dimensions for the relevant count. Retain the existing 3D model reference; a generic model does not independently prove key/color.

Run the Footprint Editor's footprint checker (Inspect/checker command in the installed UI) on both saved copies. Save them, leave the V4 PCB open and report completion plus the visually confirmed round/slot coordinates and slot axis. **Stop here: do not assign/reimport these footprints into production yet.**

## 5. PCB manufacturer capability — supported process, tolerance unresolved

[JLCPCB rigid-PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/), checked 2026-10-11, list non-plated slots made by CNC, minimum slot width 1.0 mm and standard non-plated slot tolerance ±0.20 mm. A 1.60 mm wide slot is above the published minimum, so non-plated slotted holes are supported in principle. The extremely short 1.75 mm overall slot and Molex's unilateral tolerances are **not thereby guaranteed**. Standard ±0.20 mm is looser than the required width 1.60–1.65 / length 1.75–1.85 mm. Hole position tolerance is also published separately. Before fabrication, confirm the exact geometry and finished tolerances with the manufacturer, including locator round-hole tolerance; no supplier contact, acceptance or production approval is claimed. Do not enlarge the holes to compensate without manufacturer/owner review.

Represent the slot as native NPTH oblong drill geometry. At a later authorized fabrication check, inspect the NPTH drill/route interpretation and manufacturer preview, ensuring the slot was not circularized or lost. No drill/Gerber output is requested or generated at this checkpoint.

## Agent continuation after GUI completion

Reconfirm exact live PCB path; read both corrected local library footprints, including drill X/Y, shape/angle and blank mechanical numbers. If Konnect cannot expose these faithfully, use read-only saved-library inspection for the oval drill clause; do not author or rewrite CAD text. Compare numbered pad geometry and the owner's current-drawing orientation evidence. Then continue the **already approved** bounded J1/J2/J3/J8 replacement without reopening family selection.

Approved final connections: J1 1=PGND/2=adapter positive; J3 1=PGND/2=BATTERY; J2 1=PGND/2=NC/3=SYS; J8 1=PGND/2=NC/3=F5_5V_OUT. J2/J8 remapping is a separate approved production operation, not part of this mechanical library correction. J8 remains F0 DNP; J4/J6 unchanged. Preserve existing switching-loop routing and unrelated zones, keepouts, outline and components. If Konnect replacement rejects oval NPTH drills, stop and use a bounded native replacement handoff rather than discarding slots. Finish with fresh ERC/DRC, parity, pad/net readback, focused diff and handover. General routing remains unauthorized. VAC1 hot-plug and BQ25792 2S current gates remain OPEN.
