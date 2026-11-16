# Phase 4.19 independent electrical and BOM review

Date: 2026-10-18  
Scope: read-only review of the accepted Phase 4.18 production PCB.  
Reviewer boundary: electrical layout, population/BOM consistency, component
qualification and the previously deferred R35/R12-C26/SYS cleanup. Manufacturing,
mechanical, native-warning and full-board identity review remain with the parent
reviewer.

## Review basis and verdict

The review is bound to production PCB SHA256
`4e13e4c11c486aa4fba7866817f5c37e715b248ab696cbd4a599970cf2a2ea84`, unchanged
schematic/project/rules, and the accepted Phase 4.18 proof. Phase 4.18 added only
the already-reviewed F5 footprint transforms and F5 copper; the accepted proof
states that all F0 placements/copper and the prior power geometry were preserved.
I therefore reused the Phase 4.17 electrical review for the F5 geometry and the
Phase 4.8A/4.8B evidence for the normal TPS62933 path instead of repeating a
whole-board geometry audit.

**Electrical CAD verdict:** no demonstrated copper, topology or return-path
failure was found that justifies reopening the accepted routing. The board is
not a procurement or hardware-qualified release: the owner must still decide
the fabrication stackup and unresolved part/footprint qualifications, and the
assembled hardware must qualify Ceff, hot-plug, charging, thermal, reverse
blocking and source/load behavior.

## Decision table

| Class | Finding, evidence and consequence | Smallest action |
|---|---|---|
| **MUST FIX BEFORE PCB FABRICATION** | No electrical CAD defect demonstrated by the accepted evidence. Do not treat the calculated power margins as a fabrication waiver: the Phase 4.17 F5 calculation assumes 35 µm copper and 25 µm via plating, while the Phase 4.8B/normal-buck calculations also state that the manufacturing stackup is unconfirmed. A thinner inner copper construction changes SYS/F5 drop and thermal margin. | Bind the actual four-layer stackup/copper/plating to the board order, or recalculate the power allocation and obtain an owner decision. This is a release input, not a routing request. |
| **OWNER DECISION** | Q1, Q2 and Q10 use the same project-local `easyeda2kicad:DFN-8_L3.3-W3.3-P0.65-BL-3` land pattern. The isolated F.Mask/F.Paste render shows the paste layer with no per-pad or global paste override, but pad 9 is 2.45 × 2.00 mm versus AOS's 2.45 × 2.28 mm recommended land callout. This is a manufacturer-land deviation requiring owner/assembler and thermal-pad acceptance; it is not by itself a demonstrated CAD blocker. | Accept the smaller exposed land for the selected AON7528 and assembly/stencil process, or authorize a footprint review. Do not substitute a part silently. |
| **OWNER DECISION** | F5 critical sourcing is still provisional: U7 `TPS62933DRLR`, U8 `LM74700QDBVRQ1`, Q10 `AON7528`, L3 `XAL5050-682MEC`, C60/C61, C62/C63/C66–C69 and C64/C65 have exact recorded identities, but most current preferred-supplier stock/MOQ and all four F5 feedback resistor MPNs (R60–R63) are open. R60/R61 require 0.1%/25 ppm-class values; R62/R63 are 1% values. | Freeze exact orderable MPNs and supplier evidence before assembly. Preserve the selected values and footprints; replacements require owner approval and a fresh footprint/electrical review. |
| **OWNER DECISION** | J8 is the approved-for-CAD Molex Nano-Fit `105313-2103` RevJ1 project-local footprint at `(89.0,40.38)`, with F5 pin mapping PGND/NC/OUT (pins 1/2/3) as documented by the Phase 4.17 review. The mating housing `105307-2203`, terminals and harness/wire assembly are not procurement or current qualification approval. | Approve the exact keyed harness, wire/contact choice and pin order for the prototype. Do not use the older two-position or Phoenix mapping. |
| **OWNER DECISION** | Optional PMID bulk positions C20/C22/C24/C25 remain DNP. The recorded 20/25 V POSCAP candidates are unsuitable for the retained 21 V adapter envelope and have no approved backup assembly. Populating them would be a new electrical/procurement choice. | Keep them explicitly DNP for this prototype, or select and qualify a >=35 V alternative before population. No PCB change is needed for the DNP choice. |
| **ACCEPTABLE FOR PROTOTYPE** | U7 F5 local switching geometry is evidenced by U7 `(102.0,59.0)`, C69 `(99.8,59.5)`, L3 `(105.0,64.2)`, C60/C61 `(96.5,59.5)/(96.5,64.3)`, C64/C65 `(109.5,63.75)/(113.0,63.75)`, U8 `(117.1,58.5)` and Q10 `(113.0,56.5)`: 1.552 mm U7 VIN/GND-to-C69 separation, 2.780 mm F.Cu SW-to-L3 copper, zero SW vias, projected 1.321 mm² input and 1.382 mm² bootstrap loops, and native PGND return sampling all pass in the Phase 4.17 review. | Retain the accepted F5 routing. Measure it on the matching assembled board before claiming 5 V/2 A continuous operation. |
| **ACCEPTABLE FOR PROTOTYPE** | The accepted U3 normal TPS62933 geometry remains the Phase 4.8A installation: U3 `(49.0,79.0)`, L2 `(49.65,85.0)`, C37 `(50.9,79.5)`, C33 `(54.0,85.0)`, C45 `(56.4,85.0)`. SW is 3.703 mm on F.Cu with zero SW vias; bootstrap is 1.255 mm plus 1.894 mm return; 597/597 FB reference samples and the native PGND grid were preserved. Phase 4.8B preserves these returns while completing the normal distribution. | Retain the accepted normal-buck geometry. Do not infer 1 A thermal, stability or RF performance from CAD evidence. |
| **ACCEPTABLE FOR PROTOTYPE** | F5 copper screens at the accepted 35 µm assumption are 25.72 mV output branch drop at 2 A/20 °C and 36.33 mV at 125 °C; SYS-to-U7 input branch is 35.32/49.89 mV. The 18 µm inner-copper sensitivity raises the cold output estimate to 36.89 mV. These are bounded calculations, not a demonstrated failure or a guaranteed 5 V envelope. | Retain the board as a prototype candidate only under a recorded stackup and load limit; verify the full converter envelope on hardware. |
| **VERIFY ON HARDWARE** | C60/C61 are 10 µF/50 V X7R input capacitors and C64/C65 are 22 µF/35 V X5R output capacitors. The BOM and Phase 3.6/4.17 review explicitly leave DC-bias, temperature, aging, ripple-current and effective capacitance open. The nominal values cannot prove TPS62933 stability or load-step margin. | Measure or otherwise qualify effective capacitance and ripple/temperature using the exact assembled MPNs at the intended SYS/RAW bias before sustained load claims. |
| **VERIFY ON HARDWARE** | U8/Q10 reverse blocker topology and polarity are correct: U8 ANODE/EN senses RAW, Q10 source pins 1–3 are RAW, gate is pin 4, drain/exposed pad pins 5–9 are OUT, and J8 remains OUT/NC/PGND. External J8 energization, gate transients, leakage and power-off reverse current are not proven by DRC. | Test forward drop, reverse current, turn-off transient and externally energized J8 with SYS absent and with the exact F5 population. Keep the F5 output limited to the approved 5 V/2 A prototype budget. |
| **VERIFY ON HARDWARE** | Retain the agreed charger architecture: 2S1P or 4S1P only, default-off CE, and BQ25792's possible 2 A reset/watchdog default. The selected cells, complete pack, BMS, NTC and wiring are still open; firmware's nominal 0.5 A setting is not a hardware ceiling. | Qualify the exact pack/cell/BMS/wiring for the possible 2.0–2.16 A current condition and temperature range before charger power-up. Do not add a limiter, supervisor or watchdog without a new owner decision. |
| **VERIFY ON HARDWARE** | VAC1 retains owner-approved R12 `CRCW12062R00JNEAHP` 2 Ω and C26 `C1210C225K1RACTU` 2.2 µF/100 V. The retained input snubber is an accepted architecture choice, but Ceff/pulse behavior and adapter/cable ringing remain unmeasured. The Phase 2.6/2026-10-11 model reports sensitivity, not a measured peak or universal protection guarantee. | Use a controlled fixture and the actual adapter/cable to measure J1/VAC1/VBUS, FET stress and R12 pulse behavior before first unrestricted charger use. Do not replace the approved network from calculations alone. |
| **VERIFY ON HARDWARE** | The normal path, F5 path, PGND plane and power-domain isolation are CAD-qualified only. U3/U7 thermal rise, inductors, connector contacts, source/load transitions, USB-only service, leakage/back-power and F5 output ripple/dropout are not measured. | Record exact PCB/BOM/cells/source/cable/load/ambient and run the bounded bring-up plan before claiming operating ratings. |
| **OPTIONAL/COSMETIC** | Current-board comparison shows the historical R35-v2 preimage has six of seven original tracks absent, and the C26-v3 preimage has both original tracks absent; these are owner-superseded historical candidates, not current missing cleanup. The current R35 route is at `(109.5,88.926)→(110.074,89.5)` with its collinear tail. The current R12 pad is `(42.4625,49.0)` and the current C26 route is the four-segment 0.8 mm path through `(40.4085,51.054)`, `(39.624,51.054)`, `(37.678,53.0)`, `(37.475,53.0)`. SYS exact-collinear preimage objects are unchanged; the rejected SYS oblique preimage objects are absent. | Leave R35 and R12/C26 alone. Treat SYS merge as an optional representation-only cleanup if ever requested; do not recreate absent historical or rejected routes. Evidence: `phase4-19-final-audit/legacy-current-comparison.json`. |

## Population and identity check

The accepted Phase 4.18 PCB manifest was inspected by reference. The complete
F5 set is present exactly once on the common PCB. The PCB-only export does not
serialize the schematic `PopulationGroup` property; the F5-only/DNP projection
below is therefore bound to the current `V4_BOM_REVIEW.md` and
`V4_VARIANTS.md` records, with the Phase 4.18 proof binding the physical F5
references to this accepted PCB:

`U7, U8, Q10, L3, R60, R61, R62, R63, C60, C61, C62, C63, C64, C65, C66,
C67, C68, C69, J8` (19 references).

The manifest values and footprint families match `V4_BOM_REVIEW.md`:

- U7 `TPS62933DRLR` / `SOT-583-8`; U8 `LM74700QDBVRQ1` / `SOT-23-6`.
- Q10 `AON7528` / project-local DFN-8 3.3 × 3.3 mm custom footprint.
- L3 `XAL5050-682MEC` / project-local Coilcraft XAL5050 footprint.
- C60/C61 `GRM32ER71H106KA12L` 10 µF/50 V 1210; C62/C66–C69
  `GRM188R71H104KA93D` 100 nF/50 V 0603; C63
  `GRM188R71H333KA61D` 33 nF/50 V 0603; C64/C65
  `C3216X5R1V226M160AC` 22 µF/35 V 1206.
- R60/R61/R62/R63 retain the intended values 53 kΩ/10 kΩ/100 kΩ/38.3 kΩ,
  but exact orderable MPNs remain open.
- J8 `1053132103` uses the project-local RevJ1 three-position key-B Nano-Fit
  footprint; the center contact is NC. The accepted Phase 4.17 electrical map
  is pin 1 PGND, pin 2 NC, pin 3 OUT. The older two-position/Phoenix mapping
  must not be reused.

The 19-item projection is internally consistent. It is a population contract,
not an F0 ERC run or a proof that an F5 part can be procured or assembled.

## Bounded AON7528 land-pattern qualification

The accepted Phase 4.18 export was queried for Q1, Q2 and Q10 only; no source
CAD or native editor was opened. All three have the same nine-pad project-local
footprint and the same pad geometry. Q1 is at approximately `(43.9,69.4)`, Q2
at `(44.3,65.0)` and Q10 at `(113.0,56.5)`.

| Exported item | Q1/Q2/Q10 result | AOS primary drawing comparison |
| --- | --- | --- |
| Edge-pad pitch | 0.65 mm between four pads on each row | AOS package `e = 0.65 BSC`; matches |
| Edge-pad copper | 0.40 × 0.65 mm on pads 1–4; 0.40 × 0.60 mm on pads 5–8 | AOS recommended land pattern includes 0.40 and 0.65 mm callouts; no pitch or width mismatch was demonstrated |
| Exposed drain pad 9 | 2.45 × 2.00 mm F.Cu rectangle; isolated F.Mask/F.Paste SVG shows both layers and no per-pad/global paste override | AOS recommended land callout is 2.45 × 2.28 mm, so the exported land is 0.28 mm shorter in one dimension. The smaller land requires owner/assembler acceptance of stencil coverage, solder voiding and thermal spreading; exact manufacturer qualification cannot be claimed |
| Nets | Q1/Q2 pins 1–3 = D1-A, pin 4 = D1-K, pins 5–9 = VIN1 / NT4-Pad2; Q10 pins 1–3 = F5_RAW, pin 4 = F5_GATE, pins 5–9 = F5_5V_OUT | Pin grouping is consistent with the accepted reverse-blocker/input-FET use; no pad/net swap was found |

Primary sources checked 2026-10-18: [AOS AON7528 product page](https://www.aosmd.com/zh/products/mosfets/low-voltage-mosfets-12v-30v/aon7528), [AON7528 datasheet](https://www.aosmd.com/res/datasheets/AON7528.pdf), and [AOS package outline PO-00093](https://www.aosmd.com/sites/default/files/res/packaging_information/DFN3.3x3.3_8L_EP1_S.pdf). The product page identifies AON7528 as full production, 30 V, 20 V gate, DFN3.3x3.3-8L; the package drawing says the package was qualified with IR reflow and directs other solder processes to AOS. The isolated render proves the intended mask/paste layers are present, but not solder-joint quality, thermal-pad voiding, thermal spreading or production assembly yield. Exact AOS land-pattern qualification is unresolved because of the 2.45 × 2.00 mm versus 2.45 × 2.28 mm exposed-land deviation; no demonstrated routing or connectivity blocker was found.

## Capacitor population and voltage check

The accepted PCB export marks C20, C22, C24 and C25 as `47u DNP` in the
board values. `V4_BOM_REVIEW.md` records C20/C22 as Panasonic `20TQC47MYF`
(20 V POSCAP) and C24/C25 as Panasonic `EEEFK1E470P` (25 V SMD electrolytic),
with quantity zero fitted and DNP for the PMID backup bulk. `V4_VARIANTS.md`
projects all four as DNP by default for both 2S and 4S F0/F5 plans. The
20/25 V candidates must not be fitted into the retained 21 V adapter envelope;
they are a procurement/design decision, not a missing-PAD issue.

The fitted power-cap voltage identities visible in the accepted PCB and BOM
are bounded as follows:

- Charger input/PMID: C6/C7/C9 are 100 nF/50 V; C12/C13/C15/C16/C18 are
  10 uF/50 V.
- BATTERY/SYS and charger support: C1/C2/C4/C5/C8/C10/C11/C14/C17/C19/C21/C23
  are recorded 25 V parts, except C8 is 1 nF/50 V; C26 is 2.2 uF/100 V.
  The 25 V parts have nominal voltage headroom over the 18 V SYS/BAT range,
  but bias, transient and effective-capacitance qualification remains open.
- Normal regulator: C32/C43 are 2.2 uF and 100 nF input support with exact
  voltage/MPN still open; C33/C45 are 22 uF/35 V. C37/C39 are switching and
  soft-start support with exact MPN/voltage qualification open.
- USB/service and MCU domains: C27/C28 are recorded 10 V candidates on USB
  VBUS; C29/C30/C31, C35/C36/C40/C47/C48 have provisional/open exact
  voltage/MPN status in the BOM. C70/C71 are verified 1 uF/16 V X7R.
- F5: C60/C61 10 uF/50 V, C62/C63/C66–C69 100/33 nF/50 V, and C64/C65
  22 uF/35 V. Exact MPN identities are recorded, but DC-bias Ceff, ripple,
  temperature and ageing are not proven by nominal labels.

This inventory demonstrates no fitted capacitor below its recorded nominal
rail envelope, but it does not establish effective capacitance. Before a
fabrication or load claim, freeze the exact open MPNs/voltage ratings and
qualify Ceff at the actual DC bias, especially C12/C13/C15/C16/C18, C32/C35,
C60/C61 and C64/C65. No replacement is selected here.

## Electrical layout disposition

The accepted evidence supports the intended topology and return behavior:

- U7 uses SYS/PGND/F5_SW/F5_BST/F5_SS/F5_FB as intended. SW remains a short
  F.Cu path with no SW via; bootstrap and input loops are local. The feedback
  route is kept away from the SW/inductor region and has 381/381 sampled PGND
  reference points in the Phase 4.17 evidence.
- The F5 SYS branch uses the retained In2 trunk, a B.Cu bridge over the fixed
  BATTERY trunk, paired transitions and a 2 mm In2 OUT trunk to J8. This is
  connectivity/geometry evidence, not a current-density or contact rating.
- U3's accepted local SW/BST/input/output loops and Kelvin/PGND reference are
  preserved by later distribution work. U4 USB service and U5 mux isolation
  remain separate from SYS, BATTERY, REGN and F5 OUT; USB-only service is not a
  substitute for the main adapter.
- No accepted evidence supports a new IC1, F0 USB, feedback, PGND or reverse
  blocking reroute. The F5 adoption report explicitly states that no new
  thermal, voltage, 2 A or reverse-transient measurement was made.

The serious electrical risks are therefore qualification risks rather than
demonstrated CAD failures: effective capacitance/stability, hot input ringing,
pack current after charger reset, F5 thermal/dropout/ripple, reverse blocking,
connector/harness contacts and the actual fabrication stackup.

## Deferred cleanup result

The current-board metrics, rather than the historical scratch preimages, are
the release basis. Phase 4.18 preserved the accepted F0 copper, while the
legacy comparison shows which proposals were superseded by later owner edits:

- **R35 v2** is superseded and unnecessary: the current nearest physical gap
  is 0.400 mm, compared with 0.264178 mm in the historical v2 proposal. The
  current six-track branch is already the owner-edited state; do not recreate
  the historical v2 route.
- **R12-C26 v3** is superseded and unnecessary: the current C26 branch is a
  6.644354 mm, 0.8 mm-wide path with 0.601970 mm nearest clearance to C22.1.
  The v3 scratch comparison used 0.259377 mm and cannot be treated as the
  current-board condition. Leave the owner-edited route unchanged; this does
  not qualify VAC1 damping or Ceff.
- **SYS exact-collinear merge** remains a three-to-one representation change
  only; the current physical copper is unchanged and it adds no ampacity.
- **SYS southeast oblique route** remains rejected and its historical objects
  are absent from the current board. Do not recreate it.

Evidence: `phase4-19-final-audit/legacy-current-metrics.json` and
`phase4-19-final-audit/legacy-current-comparison.json`.

## Source evidence

- `hardware/v4/evidence/phase4-18-production-adoption/ADOPTION.md`
- `hardware/v4/evidence/phase4-18-production-adoption/accepted-installed-baseline.json`
- `hardware/v4/evidence/phase4-18-production-adoption/final-production-proof.json`
- `hardware/v4/evidence/phase4-17-review/REVIEW.md`
- `hardware/v4/evidence/phase4-17-review/engineering.json`
- `hardware/v4/evidence/phase4-8a-production-checkpoint-2026-10-16.md`
- `hardware/v4/evidence/phase4-8b-production-checkpoint-2026-10-16.md`
- `hardware/v4/evidence/phase4-8b-electrical-review.json`
- `hardware/v4/evidence/legacy-routing-geometry-review-2026-10-17.md`
- `hardware/v4/evidence/v4-safety-design-review-2026-10-11.md`
- `hardware/v4/evidence/phase4-19-layer-review/svg/ups12v_v4-F_Mask.svg`
- `hardware/v4/evidence/phase4-19-layer-review/svg/ups12v_v4-F_Paste.svg`
- `hardware/v4/evidence/phase4-19-layer-review/layers.log`
- `hardware/v4/V4_BOM_REVIEW.md`, `hardware/v4/V4_REQUIREMENTS.md`

Manufacturer basis is retained from the cited primary-source reviews: TI
TPS62933 SLUSEA4D Rev D, TI LM74700-Q1 SNOSD17G Rev G, AOS AON7528 Rev 1.0,
Coilcraft XAL50xx document 908-1, TI TPS2116 SLVSFG1A and TI BQ25798/BQ25792
input and charger guidance. No new part selection or manufacturer claim was
introduced in this read-only review.

**Readiness recommendation:** keep the accepted PCB unchanged. Before any
fabrication order, obtain the owner decisions on stackup and open footprint/
procurement qualifications. Treat VAC1, the BQ25792 2 A possibility, F5 5 V/2 A,
Ceff, thermal and reverse-current behavior as controlled hardware qualification
gates. If the owner wants CAD changes, the smallest bounded follow-up would be
an explicitly authorized footprint/stackup decision phase; no routing cleanup is
currently justified.
