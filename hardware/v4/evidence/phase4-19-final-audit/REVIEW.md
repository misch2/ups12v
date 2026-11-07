# UPS V4 — Phase 4.19 final PCB engineering audit

2026-10-18. **Read-only audit complete; NOT READY for the planned JLCPCB
fabrication as currently documented. One demonstrated vendor-clearance mismatch
needs correction or explicit fabricator acceptance; the remaining release inputs
need owner decisions. No general electrical reroute is justified.**

## Quick start

1. Review DFM-01 below and the [native In2.Cu crop](../phase4-19-layer-review/J7-In2-crop.png).
2. Decide the actual stackup, Nano-Fit finished-hole tolerances and part/assembly
   qualifications. Keep the common PCB and approved2S1P/4S1P architecture.
3. If correction is authorized, limit Phase4.20 to the J7 CC2 clearance and any
   explicitly chosen markings/footprint actions. Do not replay legacy cleanup.
   Stop again after an isolated, verified candidate; fabrication is a separate gate.

## Prioritized decision table

| Class | Finding / consequence | Smallest reasonable disposition |
| --- | --- | --- |
| **MUST FIX BEFORE PCB FABRICATION** | **DFM-01:** J7 upper shell plated slot at(118.370,76.675), In2.Cu `USB_CC2` track atx119.800 has0.290mm physical hole-to-copper clearance versus JLCPCB's published0.300mm inner-layer PTH requirement. Accepted project0.250mm rule does not detect it. The present design cannot be represented as meeting this vendor limit. | Increase only this CC branch's clearance with margin, or obtain explicit fabricator acceptance of the exact geometry before fabrication. No waiver or change made. |
| **OWNER DECISION** | Actual four-layer stackup/copper/plating is not ordered/confirmed. Accepted loss/current calculations assume35um on all copper and25um via plating; standard JLC inner copper/plating differs. Nano-Fit drawing tolerances also exceed standard process precision. | Bind the fabricated construction and finished-hole/slot tolerances, or recalculate/obtain vendor-specific acceptance. Do not silently substitute standard construction or resize locators. |
| **OWNER DECISION** | Q1/Q2/Q10 central land differs from AOS recommendation; exact open MPNs, F5 sourcing, harnesses, PCB/assembly process and enclosure envelopes remain open. U8 is currently reported out of stock at LCSC. Optional C20/C22/C24/C25 must stay DNP. | Approve existing land/process for a controlled prototype or authorize bounded qualification/correction; resolve parts that could force a footprint change before board ordering. Stock delays with an unchanged footprint are assembly blockers, not copper defects. |
| **ACCEPTABLE FOR PROTOTYPE** | Accepted routing/connectivity, IC1/U3/U7 loop/PGND evidence, power-domain topology,19-item F5 projection,16 PCB/four ERC warnings and the2D mechanical placement remain consistent. No new physical collision, serious layout failure or need to reopen USB FS geometry was found. | Retain the accepted geometry and warning identities, within documented load/assembly/measurement limits. |
| **VERIFY ON HARDWARE** | VAC1 hot-plug; possible sustained2A BQ25792 reset default; exact pack/BMS/NTC; Ceff/stability; F5 thermal/dropout/5V2A envelope; USB-only service and back-power/leakage; connector heating, RF and real assembly fit. | Separately authorize controlled matching-hardware tests with source/load/cells/BOM/ambient/probes/raw logs recorded. No power-up or test was performed here. |
| **OPTIONAL/COSMETIC** | Dense/substandard-size legend, missing functional rail/F0-F5/BOOT-RESET markings; representation-only SYS merge. R35/C26 old routes are superseded by owner edits. | A small markings-only proposal can help manual assembly; use an annotated assembly map if accepted. Do not install obsolete routes or optimize accepted copper. |

## Authority, preservation and proportional coverage

Production PCB SHA256 is exactly
`4e13e4c11c486aa4fba7866817f5c37e715b248ab696cbd4a599970cf2a2ea84`.
The [Phase4.18 manifest](../phase4-18-production-adoption/accepted-installed-baseline.json)
and [native summary](../phase4-18-final-production-native/summary.json) bind
the unchanged schematic/project/rules. The accepted result is0opens,
0physical DRC,0parity,0ERC errors,154footprints,473pads,1170tracks/arcs and324vias.
The accepted production warnings are16/4, distinct from isolated-library20/11.

Reused: full native geometry/pad-island/fill/preservation proof; accepted charger
and normal-buck reviews; Phase4.17 F5 engineering calculations and PGND/FB checks;
the120-test accepted toolkit baseline. No whole-board identity/refill/route-search
or expensive native geometry analysis was repeated.

New: source hash binding, Konnect short/orphan/single-pin/rule reads; bounded
export-only DFM/courtyard/minimum-feature screens; exact current legacy-route
comparisons; unchanged-schematic XML population projection; warning disposition;
primary-source fab/part/sourcing checks; isolated native SVG mask/paste/silk/In2
illustrations. CLI runs used fresh baseline-bound scratch, existing monitored
worker and preservation guards; no editor opened, save/refill or IPC mutation.
No assertion, unstable IPC or safety recovery occurred.

The read-only export analyzer lives in `hardware/v4/tools/v4kicad/prefab_review.py`;
imports have no I/O/CAD/process side effects. Its four focused ring tests plus
the existing suite give **124 offline tests PASS**. No firmware build is required
for this audit. Generic aggregate/manufacturing wrappers were not rerun because
their whole-board DRC would duplicate the exact accepted evidence and would not
resolve the vendor-specific limits, tolerances, assembly or hardware questions.

## DFM-01 — demonstrated vendor-limit mismatch

- Footprint J7=`USB4085-GF-A`, origin(117.390,83.975),90degrees.
- Shell pad UUID`a795896d-5791-49b7-91ae-4207a4427483`, netPGND,
  center(118.370,76.675), plated oblong drill0.600x2.100mm rotated90degrees
  into the horizontal board axis. Its right physical drill edge isx119.420.
- Track UUID`1814d666-f764-4da0-839c-339e7a06c1ca`, netUSB_CC2,
  In2.Cu, width0.180mm, from(119.800,76.050)to(119.800,78.665).
  Its left copper edge isx119.710: **119.710−119.420=0.290mm**.
- Copper-to-copper is about0.140mm because the slot has a0.150mm annular
  ring. These dimensions pass the accepted0.100mm net clearance and0.250mm
  hole-clearance rules; zero DRC errors therefore remains true.
- JLCPCB currently publishes0.300mm for inner-layer PTH-hole-to-copper.
  The0.010mm shortfall is larger than the native polygon approximation bound;
  the hole/straight-track calculation itself is analytic.
- Consequence: documented process nonconformance/risk to drill registration and
  internal copper isolation; this is not a demonstrated existing short.
- Minimum correction scope: local CC2 offset/connecting legs with positive
  margin, preserving J7 lands and accepted USB data pair. A roughly0.02mm
  outward displacement of the straight leg would screen at0.310mm, but no
  candidate/adjacent-leg clearance has been engineered or authorized here.
  Alternatively seek explicit vendor acceptance; an owner assumption is not
  fabricator acceptance.

Evidence: [full screen](dfm-screen-complete.json), accepted native snapshot,
[actual-layer crop](../phase4-19-layer-review/J7-In2-crop.png), and
[JLCPCB rigid capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/),
Drilling/Traces, checked2026-10-18. This concerns CC2, not USB Full-Speed routing.

## Manufacturing feasibility and unconfirmed process inputs

Planned basis: routed four-layer FR4 prototype, manually assembled, likely
JLCPCB. No fab quote/engineering acceptance, process selection or CAM package
exists; alternative fabricators must be assessed on their own capabilities.

| Feature | Actual accepted CAD / process comparison |
| --- | --- |
| Width / spacing | Smallest track0.100mm; resolved class clearance0.100mm. Published multilayer1oz width/space0.09mm; pad-to-track0.10mm and distinct-net SMD pad spacing0.15mm are separately screened. No SMD gap below0.15mm found. A2oz choice changes requirements; do not assume compatibility. |
| Vias |239x0.50/0.30,25x0.60/0.30,9x0.70/0.30,39x0.70/0.40,10x0.80/0.40,2x1.00/0.50mm. Smallest annular ring0.100mm; through-vias only. These exceed published minimum via geometry. No microvia/filled/capped process inferred. |
| PTH | J7 contact drills0.40mm with0.70mm lands; shell0.60mm slots. PTH minimum ring0.150mm, exactly the published multilayer1oz absolute floor, below its recommendation. Other PTH lands are larger. Supported geometry, with no extra tolerance margin claimed. |
| NPTH | Four mounting holes3.20mm; each Nano-Fit has1.60mm round locator and1.60x1.75mm oval locator. No plating on locators/mounts. Widths exceed published NPTH/slot minima. Finished tolerances remain unresolved below. |
| Hole/copper spacing | Existing class/project hole clearance0.250mm; native physical DRC passes. Focused geometry finds only DFM-01 below the applicable published PTH-to-track screen; no PTH pair below0.45mm and no different-net PTH-to-In1-plane boundary below0.30mm. Via/NPTH manufacturing limits are below the accepted0.25mm hole floor. |
| Board edge | Closed rectangleX30–126,Y30–100. Minimum fixed copper/pad distance1.100mm; native PGND fill boundary is about1.0005mm from the outline. Project1.000mm copper-edge rule exceeds the published routed-edge requirement. No edge plating/castellation or exposed copper running to the edge is intended. |
| Mask | Zero global pad-mask expansion, front/back via tenting requested, no plugging/filling/capping. Native openings reviewed; pads are1:1 with no discovered per-pad mask override. JLC's current LDI process supports1:1. Use a confirmed mask color/process; do not treat requested tenting as guaranteed hermetic fill. |
| Paste/custom pads | Native F.Paste shows intended SMD and custom IC1 corner apertures. THT connectors and bare TP5–TP8/TP13–TP17 have no paste. Q1/Q2/Q10 and module soldering need a suitable reflow/hot-air process. This is not a validated stencil volume/reflow profile or solder-void result. |
| Legend |155visible text objects screened, all below at least one published standard legend size/stroke criterion (mostly0.8mm references; TX/RX/GND also small). Native silk contains overlaps and edge-clipped connector body artwork. No claim of factory-readable legend; no copper problem demonstrated. |
| Rules | `min_track_width=0` and silk-clearance/mask-copper settings0 are verification gaps, not measured zero-width copper. Actual minima and native images were screened here. A subsequently authorized fabrication-floor/rule adjustment must preserve real geometry and require its own validation; no rule was changed/waived. |

Vendor basis: [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/),
checked2026-10-18. Select actual copper, finished thickness, plating, finish,
mask, drill precision and routed outline before release. JLC currently lists
default inner0.5oz and average hole plating18um. That is different from the
accepted electrical calculation's35um/25um assumptions. It is not proof that
this board fails electrically; choose matching construction or recalculate.
No new USB impedance requirement is imposed by this audit.

### Nano-Fit tolerance decision

The owner-supplied SD-105313-100 RevJ1, sheet1, released2025-06-26,
was re-inspected using the retained
[drawing image](../nanofit-revj1-sheet1.png). It specifies:

- Contact PTH1.20±0.05mm, position calloutdiameter0.08 againstU/V.
- Round locator1.60+0.05/−0.00mm; oval1.60+0.05/−0.00 x1.75+0.10/−0.00mm.
- Recommended board thickness1.6–2.4mm.

The nominal RevJ1 CAD geometry matches. Standard JLC PTH +0.13/−0.08,
NPTH-slot±0.20 and hole-position±0.075mm do not guarantee those limits.
Nominal1.6mm board thickness with ordinary±10% also permits below1.6mm.
These are real specification gaps, not an observed manufactured collision.
Before fabrication, obtain a compatible process/tolerance commitment (including
the circular locators), or an explicit owner decision on a documented prototype
fit trial. Do not imply a fit trial validates the manufacturer's tolerances or
silently enlarge nominal holes. Contact-hole precision alone does not solve
the locator/position/thickness questions.

## Mechanical and assembly readiness

No enclosure model or final mating/strain-relief envelope was supplied. No
collision with a hypothetical enclosure is asserted. Native2D courtyards show
zero intersections; only NT1/NT2/NT4 intentionally lack purchased-body courtyards.

| Item | Actual geometry / remaining qualification |
| --- | --- |
| Outline / mounts |96x70mm. H1(35,47.5),H2(121,47.5),H3(35,95),H4(121,95),3.2mm NPTH. Existing screw-head courtyards clear. Actual screw/standoff diameter, under-board insulation and enclosure mounting tolerance remain unmeasured. The earlierY46 placement is historical. |
| Nano-Fit row | J1(43,40.38),J2(58,40.38),J3(73,40.38),J8(89,40.38),all90degrees, mating out toward−Y/top. Locators atY33.2, oval long axisX after rotation. Body-face-at-edge and latch overhang are intentional. Cable bend/latch-finger/strain-relief access must remain outside the row. |
| J4 / J6 | Side-entry JSTs at(122.5,40)/(104,38.5),180degrees, also outward−Y. Their native courtyards do not collide with Nano-Fit. Exact harness housings/contacts and vertical envelopes remain assembly decisions. |
| USB-C | J7 right-edge service position(117.39,83.975),90degrees; selected USB4085 plated-hole pattern accepted. No2D collision found; cable boot/plug/body and enclosure cutout are unmeasured. Inside-enclosure access remains allowed by requirements. |
| RF | U1(82,93.6),180degrees. All-layer antenna areaX75.4–88.6/Y99.2–104.6, no tracks/vias/pads/fill, plus custom exclusion for other footprints. Actual In1 fill/RF preservation is accepted. External metal/battery/harness/enclosure clearance and RF performance remain unverified; keep them away from the antenna. |
| Probe/service | TP5TX,TP6RX,TP7PGND atX32.5/Y82,84.54,87.08 preserve2.54mm pitch. Separate voltage probes and existing buttons accessible in2D; no UART power pin. TP17 is close to J4 reference artwork, affecting identification rather than electrical access. |
| Hand assembly | THT connectors are accessible from the reverse face and passives are conventional packages. IC1 QFN, U3/U5/U7 SOT583, AON exposed pads and U1 ground-pad grid require flux/hot-air/reflow and inspection; an iron-only assembly process is not qualified. Installed connector bodies/probes may obscure top pads: solder small SMD first, inspect, then connectors. No actual tool/body collision is demonstrated. |

The actual silk has reference IDs/pin1 markers but no comprehensive connector
rail/polarity map, F0/F5 population instruction or BOOT/RESET labels. Owner may
accept an explicit assembly/harness drawing for a controlled prototype or
authorize small markings; this is a meaningful assembly choice, not permission
to change connectors. Preserve the actual distinct sets: J1/J2 black/keyA,
J3/J8 natural/keyB, two/three positions respectively, with their matching
1053071202/1203 and1053072202/2203 housings. Do not erase that protection by
substituting key/color/circuit count; label the rails for assembly and service.

Current numbered pin map, checked in accepted native pad export (do not infer
mating-view left/right from the board's top view): J1=1PGND/2adapter-before-F1;
J2=1PGND/2NC/3SYS; J3=1PGND/2BATTERY; J8=1PGND/2NC/3F5_OUT.
No center crimp on J2/J8, no parallel-contact current assumption, no tin/gold
mixing. J4=1MAIN_3V3/2PGND/3SDA/4SCL/5CHG_REQ/6~INT;
J6=1GND/2TS (sense ground, not a new power PGND return).

## Electrical layout quality and retained qualifications

[Independent electrical/BOM review](INDEPENDENT_REVIEW.md) records the detailed
references and manufacturer revisions. Accepted charger geometry is in
[Phase4.5 routing review](../phase4-5-routing-review.md), followed by the accepted
BATTERY/PROG/control and owner-edit checkpoints; Phase4.18 proof binds the current
F0 geometry. Do not use a rejected historical scratch as current evidence.

IC1(60,66) switching paths, local VBUS/PMID bank, package escapes, BATTERY/SYS
distribution and PGND plane are retained.3mm inner distribution, widened outer
paths and deliberate parallel power vias address the approved current model.
The isolated plane is one connected PGND fill with RF exclusion; significant
power return is not assigned to NT1. There is no demonstrated new ground moat,
wrong-domain bridge or missing power connection. Package necks and the accepted
BATTERY loss of outer parallel spreading still require thermal validation.

For U3(49,79), reuse accepted3.703mm F.Cu SW/zero SW vias, local bootstrap,
input/output returns and597/597 FB-reference samples. For U7(102,59), reuse
2.780mm F.Cu SW/zero SW vias,1.552mm local bypass separation,
1.321/1.382mm² projected input/bootstrap loops and381/381 FB-reference samples.
These are layout/sample evidence, not extracted loop inductance or EMI tests.

The F5 SYS branch crosses BATTERY on B.Cu, not through it. U8 ANODE/EN=RAW,
Q10 source1–3=RAW/gate4/drain5–9=OUT, J8pin1PGND/pin2NC/pin3OUT. Reverse
blocking topology is correct; external energization/transient leakage is not
proven by netlists. NativeUSB/U4/U5 domains remain isolated from SYS/BAT/REGN/F5.

The existing F5 copper model gives SYS branch35.32/49.89mV at2A cold/hot
copper and output25.72/36.33mV, excluding contacts, plane spreading, U7 dropout
and U8/Q10 effects. The conditional4.78081V low-output screen is not a guarantee.
The earlier30mV allocation is not recast as a new mandatory product limit or
proof of failure. F5 remains the approved5V/2A prototype target within the total
source/battery budget; independent output maxima are not added together.

## Current deferred-cleanup disposition

[Exact UUID comparison](legacy-current-comparison.json) and
[current analytic metrics](legacy-current-metrics.json) supersede the old proposal:

| Historical candidate | Actual Phase4.18 result | Classification |
| --- | --- | --- |
| R35v2 bleeder | Six of seven old track preimages absent. Current owner path has0.400mm nearest different-net gap versus old proposed0.264178mm. Tiny same-net pad-internal overlaps remain but native connectivity is good. | **Superseded; unnecessary.** No historical replacement. |
| R12/C26v3 | Both old preimages absent. Current four0.8mm segments total6.644354mm; nearest C22.1/PMID gap0.601970mm versus old proposed0.259377mm. C26.1 remains behind2ohm R12, not VIN1. | **Superseded; unnecessary.** Preserve owner geometry and2ohm/2.2uF architecture. |
| SYS collinear | All three original1.2mm segments retained, X67.95–76.2 atY60.95. One replacement would have identical physical copper union. | **Optional/cosmetic only.** No current/thermal benefit. |
| Southeast SYS45degree | Rejected route's two old preimages absent. Historical scenario worsened resistance2.965%. | **Rejected; never recreate.** |

## BOM, population and sourcing

[population.json](population.json) binds the exported XML to the exact unchanged
schematic SHA256 and verifies all19F5-only references:
U7/U8/Q10/L3/R60–R63/C60–C69/J8. All present exactly once on the same PCB;
F0 omits all19, F5 fits them subject to qualification. TP17 is unfed inF0.
This is a documented/manual population projection, not a native separateF0
schematic/ERC. `PopulationGroup` and `47u DNP` values/BOM/variant instructions
are authoritative assembly instructions; native PCB DNP flags are not set for
these groups. A generic unfiltered BOM/export must not be used as an assembly list.

Exact F5 MPN/package identities agree with current BOM: TPS62933DRLR/SOT583,
LM74700QDBVRQ1/SOT23-6, AON7528/DFN3.3, XAL5050-682MEC;1210input capacitors
10uF50V,1206outputs22uF35V and0603support capacitors. R60/R61 need53k/10k
0.1% identities; R62/R63=100k/38.3k1%; exact order MPNs remain open.

Q1/Q2/Q10 have2.45x2.00mm central copper/paste versus AOS PO-00093H
recommended2.45x2.28mm land. Pitch/pin grouping is correct. The smaller land is
an explicit assembly/thermal acceptance question; neither manufacturer-exact
qualification nor a proven electrical failure is claimed. Native mask/paste
is now available in the layer-review evidence. Do not refresh/rescale it without
authorization. The [AOS drawing](https://www.aosmd.com/sites/default/files/res/packaging_information/DFN3.3x3.3_8L_EP1_S.pdf)
also identifies IR-reflow qualification; selected prototype assembly remains open.

Fitted high-voltage MLCC nominal ratings are consistent with recorded rail
envelopes (input/PMID50V, battery/SYS generally25V, C26=100V); this does not
prove biased capacitance, ripple, ageing or transient margin. Some normal/USB/MCU
capacitor exact MPN/voltage fields remain provisional/open: freeze them before
assembly, with a footprint review before fabrication if the selected part changes
package. For U3/U7, qualify effective input/output capacitance against the reused
TI recommendations at actual bias/temperature, not the nominal sum alone.

C20/C22 legacy20V POSCAP and C24/C25 legacy25V electrolytic candidates remain
unqualified **DNP in every present profile**, with native paste lands still on the
board. They must not be populated as available spares on the approved21V input
envelope;25V also misses the retained80% voltage-use target. Keeping DNP is a
valid prototype choice; fitting backup bulk requires an approved new selection.

[Dated sourcing check](SOURCING.md) records current preferred-supplier observations
without editing the BOM: U3/U7 and J7 have low-MOQ LCSC listings; U8's exact
LCSC SKU is out of stock; a preferred L3/Nano-Fit basket is not yet established.
No stock absence at all suppliers is inferred. Exact cells/BMS/NTC, crimp wire,
and some common power/logic parts remain procurement/qualification decisions.
No replacement or purchase is approved here.

## Power-up and matching-hardware validation boundary

Retain [the agreed safety architecture](../v4-safety-design-review-2026-10-11.md):
one PCB,2S1P/two18650 or4S1P/four18650; BQ25792/BQ25798 profiles;
nominal0.5A host charging and existing default-off CE. BQ25792 S792-2 can
restore sustained2A after POR/reset/watchdog while CE is already low. Qualify
each series cell, whole pack/BMS/wiring for that current with tolerance and
temperature. Firmware current and a generic BMS do not impose a0.5A ceiling.
No new limiter, supervisor, latch or watchdog is demanded.

Separate owner-authorized tests, not fabrication prerequisites requiring a
nonexistent board, must cover:

- Actual VAC1 hot-plug peaks/damping at the IC pin using approved adapter/cable
  stimuli;30V absolute maximum is not a desired test target. R12 pulse rating,
  C26 effective capacitance and Q1/Q2VDS/VGS also need matching evidence.
- Controlled charger POR/watchdog/REG_RST/CELL behavior, CE high/low/startup,
  NTC/BMS/pack disconnect and battery-backed SYS without MCU dependence.
  Start with protected fixtures/battery simulator before separately approved cells.
- U3/U7 ripple, load steps, Ceff/stability, startup and temperature; F5 low-SYS
  dropout and the full5V/2A budget with exact copper/contacts/ambient. No3A
  continuous claim follows from a TPS62933 part number.
- USB-only ROM/service operation with MAIN absent; U4LDO dissipation (existing
 0.3A provisional screen, not rating), U5priority/isolation, no USB backfeeding
  charger/SYS/BAT/F5, no off-domain MCU/I2C/GPIO/probe injection. Optional UART
  remains3.3V on a powered target, high-Z off, no VCC wire.
- U8/Q10forward drop, reverse current and transient disconnect with externally
  energized J8/SYS absent and source changes; connector/cable heating and pack
  current under the approved combined load; RF in actual enclosure/harness layout.

Record board revision/BOM/population, source/cable, exact cells/BMS, load,
ambient, probe bandwidth/grounding and raw logs. CAD/export calculations are
not physical measurements. No new failure thresholds or speculative redesign
is introduced; apply the approved requirements and component limits.

## Proposed bounded next phase — not executed

Phase4.20, only if owner authorizes: resolve DFM-01 vendor acceptance or make a
local CC2 candidate with margin. Retain exact accepted source binding, isolated
native worker, positive readback/preservation, then affected checks and one
ERC/DRC/parity/connectivity milestone. Preserve USB FS arcs/geometry, IC1/F0/F5
power loops, connectors, rules and population. Return candidate evidence before
production adoption. Add only an explicit owner-approved marking/footprint
whitelist; no legacy routing cleanup or broad component moves.

If the fabricator explicitly accepts DFM-01, no copper correction is inherently
required by this audit. Either path still needs stackup/tolerance and assembly/
procurement decisions before separate manufacturing-release authorization.

**STOP for owner decisions. Production CAD/rules/libraries/BOM/firmware remain
unchanged; no manufacturing package, order, power-up, commit or push occurred.**
