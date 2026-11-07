# Phase 4.20 — fabrication decisions for the prototype

2026-10-18. **Read-only decision preparation; no selections applied and no
manufacturing release.** Retain the accepted Phase 4.19 electrical review and
its hardware qualifications. These choices do not reopen the architecture.

## Quick start

Recommended direction: 1oz copper on all four layers, retain nominal 1.6 mm
pending a finished-thickness/tolerance commitment, keep the existing AON lands
only with explicit prototype-process acceptance, use an external assembly map,
and assemble from an explicitly approved F0 or F5 population list. Exact
construction/tolerances and critical sourcing remain unresolved.

## 1. Copper, stackup and via barrels

Accepted model: 35 µm all layers, 1.6 mm via length, 25 µm barrels;
saved dielectrics 0.100/1.240/0.100 mm. JLC selectors offer 1/2oz outer and
0.5/1/2oz inner, subject to thickness. Displayed default `JLC04161H-7628`
has 35 µm outer, **15.2 µm inner**, 0.2104 mm prepregs and 1.065 mm core,
so it differs from the model. [Official stackups](https://jlcpcb.com/impedance),
[copper guide, updated 2026-09-09](https://jlcpcb.com/help/article/jlcpcb-copper-weight).

| Realistic choice | Recalculation/acceptance needed |
| --- | --- |
| **Recommended: 1oz outer + 1oz inner**, exact offered ID/minimum thickness confirmed | At actual 35 µm, retain trace resistance inputs; recalculate barrels unless 25 µm is confirmed. Review actual dielectric spacing/thermal spreading. Nominal 1oz is not a minimum-thickness guarantee. |
| Default 1oz outer + 0.5oz inner | Recalculate SYS/BATTERY In2, PGND In1 spreading, power transitions, F5 branch drops/low-output envelope and thermal/current estimates. Inner-layer resistance alone scales **2.30× at 15.2 µm**, **2× at 17.5 µm**. Outer contribution is retained if 35 µm confirmed. |
| Any 2oz option | Decline: existing 0.100 mm tracks/gaps conflict with the guide's 0.160 mm floor. Requires separate process acceptance/redesign, then affected-layer loss/thermal recalculation. |

Published average plating is **18 µm**, not a minimum. Versus 25 µm, via
resistance sensitivity is **1.39×** thin-wall, **1.42×** exact annulus at
0.3 mm finished bore. Hypothetical 1.8/2.0 mm adds length factors 1.125/1.25.
Update via-current/sharing, F5 branch drops and conditional 4.78081 V output
screen with actual minimum plating/thickness; these factors apply to barrels,
not the entire path or a guaranteed ampacity.
[JLCPCB plating specification](https://jlcpcb.com/capabilities/pcb-capabilities/).

**Owner decision:** authorize a specific offered 1oz/1oz stackup and either
obtain a quoted 25 µm minimum barrel construction or authorize recalculation
using a vendor-confirmed lower minimum. No guarantee is inferred from an average.

## 2. Nano-Fit Rev J1 finished holes and board thickness

Molex **SD-105313-100 Rev J1**, released 2025-06-26, sheet 1 requires contact
PTH **1.20 ±0.05 mm**, positional zone **Ø0.08** to U/V, round locator
**1.60 +0.05/−0.00 mm**, oval locator **1.60 +0.05/−0.00 ×
1.75 +0.10/−0.00 mm**, board **1.6–2.4 mm**.
[Manufacturer drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/105/105313/1053131102_sd.pdf).
Existing CAD matches these nominal features.

Standard JLCPCB PTH +0.13/−0.08, NPTH slots ±0.20, hole position ±0.075 mm
and board ±10% do **not guarantee** the drawing. Its ±0.05 circular ENIG
press-fit-hole option may address contact diameters by quotation; it does not
establish locator-slot limits, circular NPTH unilateral tolerances or the
Ø0.08 positional zone. Datum-based true position is not equivalent to ±XY.
[Published process limits](https://jlcpcb.com/capabilities/pcb-capabilities/).

**Recommended:** retain nominal 1.6 mm and quote the complete tolerance set.
Finished thickness must start at 1.60 mm for Molex compliance; standard stock
can be 1.44 mm. Order notes alone do not guarantee it. Fallback: explicit
prototype fit/yield-risk acceptance, incoming thickness and unpowered seating
checks; no forced locators or silent CAD resizing.

**1.8 mm ±10% =1.62–1.98 mm** fits Nano-Fit's range but is absent from the
displayed four-layer selector. J7 has 2.10 mm nominal shell stakes; thicker
boards reduce protrusion. J7/contact solderability, JST tails, mounts, seating
and access are unqualified at 1.8 mm. **Do not select 1.8 mm** until the offered
construction and complete assembly are compatible; likewise do not substitute
standard 2.0 mm solely for Nano-Fit.
[GCT connector data](https://gct.co/connector/usb4085).

**Owner decision:** seek a guaranteed complete tolerance quotation, or explicitly
accept standard-process prototype fit risk. Keep the present nominal stackup
until that decision; any thickness change needs separate assembly qualification.

## 3. Q1/Q2/Q10 exposed lands

Current **2.45 ×2.00 =4.900 mm²** versus AOS **2.45 ×2.28 =5.586 mm²**:
**12.3% less area**, 0.14 mm/end if centered. Mapping/pitch are correct.
Reduced wetting affects transfer, voiding and yield; whole-device thermal
resistance cannot be scaled directly by area. Equal-thickness full-aperture
paste volume is also 12.3% lower. AOS qualifies IR reflow; other processes need
its advice. [PO-00093 revision H, recommended
land and process note](https://www.aosmd.com/sites/default/files/res/packaging_information/DFN3.3x3.3_8L_EP1_S.pdf).

**Recommended:** retain under explicit prototype deviation; use controlled
reflow/hot-air, flux and assembler-defined paste, inspect hidden joints/voiding
as practical, then qualify temperature/drop before load claims. Edge solder
does not prove the hidden joint. Minimal alternatives: later stencil-process
study or separately authorized local land correction. Paste cannot add copper.

**Owner decision:** accept this land/process deviation for a controlled prototype,
or request bounded footprint/assembly qualification before fabrication.

## 4. Human-readable labels

**Recommended:** a separate top-view assembly/harness drawing with pin-1 marks,
explicit connector-side versus mating-face views, polarity and population
legend. Existing dense silk is not reliable enough to carry the instructions.
No copper/footprint move or undersized extra text is justified for this task.

| Item | Minimum drawing label / pin-number contract |
| --- | --- |
| J1 | ADAPTER IN: 1 PGND, 2 adapter input before F1 |
| J2 | SYS OUT: 1 PGND, 2 NC, 3 SYS; omit centre crimp |
| J3 | BATTERY: 1 PGND, 2 BATTERY; approved 2S1P or 4S1P pack profile |
| J8 | 5V OUT — F5 ONLY: 1 PGND, 2 NC, 3 F5_OUT; omit centre crimp |
| J4 | 1 MAIN_3V3, 2 PGND, 3 SDA, 4 SCL, 5 CHG_REQ, 6 ~INT |
| J6 | NTC: 1 GND, 2 TS; sense-ground return |
| J7 / switches / population | USB SERVICE; SW1 BOOT/DOWNLOAD; SW2 RESET; F0 omits F5 group, F5 fits it |

Use exact pin numbers from the accepted topology; do not infer harness left/right
by mirroring the PCB image. Print the selected cell/charger/population profile
on the assembly record. If PCB text is later desired, propose only safely fitting
rail/polarity/BOOT/RESET labels for separate approval and silk/mask checking.

**Owner decision:** approve the external drawing as the prototype labeling method,
or authorize a specific small PCB-text whitelist in a subsequent phase.

## 5. F0/F5 assembly readiness and critical sourcing

The common PCB is routed; an assembly-ready released BOM is **not available**.
Accepted [exact schematic population projection](../phase4-19-final-audit/population.json)
is a documented projection, not native DNP-filtered exports. Future assembly
lists must state exact PCB hash, 2S1P/4S1P and BQ25792/BQ25798 profile, F0/F5,
fitted quantities, exact MPN/package and a separate explicit DNP list.

**All 19 F5-only parts:** U7, U8, Q10, L3, R60, R61, R62, R63,
C60, C61, C62, C63, C64, C65, C66, C67, C68, C69, J8.
F0: omit all 19 and the J8 harness; TP17 is unfed. F5: fit all 19 with the
accepted identities and the keyed J8 harness; pin 2 stays NC. Existing TP17
is retained. Old removed-supervisor BOM text must not override this newer group.

**C20/C22/C24/C25 remain DNP in both F0 and F5**, excluded from fitted quantities
and paste/hand-assembly instructions. Recorded 20/25 V backup-bulk candidates
are not approved for the retained 21 V adapter envelope. Do not populate spare
capacitors in these positions; fitting bulk requires a new approved selection.

Critical unresolved items, reusing the accepted [2026-10-18 sourcing snapshot](../phase4-19-final-audit/SOURCING.md):

- **F5:** U8 LM74700QDBVRQ1 / [LCSC C2941042](https://www.lcsc.com/product-detail/C2941042.html)
  rechecked today: out of stock, MOQ/multiple 1; USD 2.4767 is reference only.
  L3 XAL5050-682MEC preferred-supplier basket remains unestablished. R60/R61
  53k/10k 0.1%, R62/R63 100k/38.3k 1% need exact order MPNs. No substitute chosen.
- **Both populations:** refresh exact IC1 profile availability; qualify L1/L2,
  provisional U2 protection and SW1/SW2 exact mechanical identity; finish open
  power/logic passive MPNs/ratings, particularly feedback and biased MLCCs.
  Resolve any package/footprint-sensitive uncertainty before PCB ordering.
- **Harness/pack:** complete exact Nano-Fit headers/housings and 1053002100 tin
  contacts, wire/crimp basket, J4/J6 mates, exact cell/BMS/NTC/pack qualifications.
  Historical `Bought` fields do not establish possession of the new Molex set.

**Recommended prototype choice:** prepare a reviewed F0 assembly list first if
U8 remains unavailable, while retaining the common F5-capable PCB; select F5
only with all 19 identities and the harness basket resolved. This does not delete
the approved F5 option or qualify the board for power-up. Prefer a practical
TME/LCSC basket; use an exact secondary-source part when needed with total
shipping/MOQ reviewed. No current stock claim beyond the cited checks.

**Owner decision:** choose the first assembly profile and authorize its exact
population/BOM freeze and sourcing resolution. A generic unfiltered BOM is
**not acceptable for assembly**. No BOM or procurement record was changed here.
