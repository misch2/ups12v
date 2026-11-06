# Phase 5.2 — component qualification and purchasing disposition

**Historical Phase5.2 evidence.** Active Phase5.3 owner decisions supersede
the FET/Murata/testpoint selection holds and counts below. TDK full-code
mapping is now closed; see [Phase5.3](PHASE5_3_COMPATIBILITY_REVIEW.md).

2026-10-19. Procurement documents only. No CAD, native KiCad, firmware, physical
assembly, power-up or order. This review extends Phase 5.1; it does not revoke
accepted architecture or create a new production revision.

Quick start: U8 and C70/C71 are now OWNER_APPROVED procurement identities.
Recommend AO3400A for Q3/Q8/Q9 and the wire-loop realization below, both pending
owner approval. C32 and both TDK output banks remain engineering holds. New TDK
manufacturer numerical data closes the missing typical-curve lookup, but does
not establish the required combined minimum or the TJ00E suffix equivalence.

Evidence is in [Phase 5.2](../evidence/phase5-2-sourcing/). Full raw page responses,
cache ages and failed lookups are retained. The accepted Phase 4.21 snapshot and
Phase 4.17 exported netlist are reused; later accepted changes were paste-only.
The unchanged 196-file manifest binds the current CAD/library/manufacturing set.
This is documentary analysis, not matching-hardware qualification.

## Approved identities and traceability

| Refs | Original procurement identity | Owner-approved procurement identity | Five-board request |
|---|---|---|---|
| U8 | TI LM74700QDBVRQ1 | TI **LM74700QDBVTQ1**, LCSC C2653623 | 5 fitted + 1 spare = 6 |
| C70/C71 | Murata GRM188R71C105KA12D | TDK **C1608X7R1C105K080AC**, LCSC C2167399 | 10 fitted + 3 spares + 7 MOQ excess = 20 |

Authority is the explicit Phase 5.2 owner instruction. Phase 5.1's DBV6/pinout and
0603 local-bypass compatibility evidence remains applicable. Source CAD retains
the original MPNs intentionally. Both old and new identities are recorded in the
reference/master CSVs; neither approved replacement remains in UNAPPROVED_ALTERNATIVES.

## Q3/Q8/Q9 — comparison completed to the limits of published specifications

Manufacturer basis: [PMV16UN Rev.1, 4 April 2011, §§2/5/7/9](https://assets.nexperia.com/documents/data-sheet/PMV16UN.pdf),
[PMV16XN, 11 November 2014, §§2/6/9/11](https://assets.nexperia.com/documents/data-sheet/PMV16XN.pdf),
[AO3400A Rev.3.1 July 2023, pp.1–3](https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf).
The AOS electrical table was visually checked in saved AO3400A-page2.png:
its hot-leakage condition is **55°C**, not 125°C. OCR's “mA” for IDSS is µA.

| Parameter | Retained PMV16UN | PMV16XN / exact order PMV16XNR | AO3400A |
|---|---:|---:|---:|
| Pinout, top view | G1/S2/D3 | G1/S2/D3 | G1/S2/D3 |
| VDS / absolute VGS | 20 V / ±8 V | 20 V / ±12 V | 30 V / ±12 V |
| Maximum RDS(on), 2.5 V gate, 25°C | 23 mΩ | 24 mΩ | 48 mΩ |
| Maximum RDS(on), 1.8 V gate, 25°C | 40 mΩ | 33 mΩ | not specified |
| Threshold range, 250 µA / 25°C | 0.4–1.0 V | 0.4–0.9 V | 0.65–1.45 V |
| IDSS maximum, full rated VDS, gate zero | 1 µA at25°C; 20 µA at150°C | 1 µA at25°C; no hot maximum tabulated | 1 µA at25°C; 5 µA at55°C; no85°C maximum tabulated |
| Gate leakage max at25°C / rated gate test | 100 nA at±8 V | 100 nA at±12 V | 100 nA at±12 V |
| Ciss / Coss / Crss, typical | 670/195/85 pF at10 V | 1240/145/125 pF at10 V | 630/75/50 pF at15 V |
| Total Qg typical / max, 4.5 V drive | 7.4/11 nC | 13.4/20.2 nC | 6/7 nC |
| td(on)/tr/td(off)/tf, typical ns | 12/40/170/85 | 9/24/31/36 | 3/2.5/25/4 |

Capacitance is nonlinear and these test voltages/drain currents differ. Switching
times use low-impedance laboratory gate drivers, including 10 V drive for AOS;
they are not delays guaranteed in the actual 3.3 V / 100 kΩ circuits. Full hot
RDS(on) at 2.5 V is also not guaranteed by these room-temperature rows.

**Actual circuit, correcting the simplified Phase 5.1 gate description:**
Q3 gate /CHG_GATE is driven from MAIN_3V3 through PNP Q5, with R10=10 kΩ to PGND;
the Q6/Q7 chain controls Q5. It is not a direct MCU-driven 1 kΩ/10 kΩ divider.
R11 has an intentionally unconnected second pin in the accepted export. Q3 drain
CE_N has R9=10 kΩ to CE_BIAS; its source is PGND. Nominal valid-main gate drive
is close to3.3 V minus Q5 saturation. The 2.5 V RDS point supports the static
proposal; it does not prove the gate voltage during every brownout.

At the existing 5.2 V bias screening ceiling, 9.9 kΩ gives at most0.526 mA.
AO3400A's 48 mΩ yields25 µV channel drop at25°C, negligible versus CE VIL0.4 V.
An illustrative 5 µA FET +1 µA CE leakage drops61 mV across10.1 kΩ. With the
previous illustrative 3.0−0.9=2.1 V bias, CE≈2.039 V exceeds VIH1.3 V. These
conditions combine different component test points, so are **not** a temperature
guarantee. PMV16UN's old20 µA/150°C calculation is not transferable to AOS.

Q8 gate=MAIN_3V3, drain=NEN; Q9 gate=NEN, drain=TCA_EN; sources=PGND.
R51/R52 are100 kΩ pull-ups to MCU3V3. The steady-state truth table is preserved:

| Power state | Q8 | NEN / Q9 | TCA_EN and consequence |
|---|---|---|---|
| Main valid and MCU powered | ON | LOW / OFF | HIGH; repeater enabled |
| USB-only MCU, main absent | OFF | HIGH / ON | LOW; charger-domain I2C isolated |
| Both supplies absent | no gate supply | no positive pull-up | no powered-high EN source |
| Charge request absent / Q5 off | Q3 gate discharged by R10 | Q3 OFF | CE pulled HIGH: charging disabled, SYS not switched off |

All three candidates' body diodes have anode at grounded source, cathode at drain;
they do not provide a positive supply path from drain to gate or MAIN. Gate
leakage, capacitively coupled pulses and rail ramps still need qualification.

For TCA9517 [Rev.D §§7.3/7.5](https://www.ti.com/lit/ds/symlink/tca9517.pdf),
EN requires0.7×VCCB high and0.3×VCCB low. At3.3 V/55°C, using AOS5 µA drain
leakage plus EN1 µA high-state leakage gives nominal TCA_EN≥2.7 V, versus2.31 V
VIH. EN sources up to30 µA at0.2 V, so Q9's low-state load includes this current
as well as the33 µA external pull-up. RDS margin is ample at a valid gate voltage.
EN's specified low-state current can also accelerate its rise; it is not a
constant1 µA input over the entire transition. No85°C bound is inferred.

First-order, typical RC comparisons only: Q3 gate discharge R10×Ciss is6.7 µs
(UN),12.4 µs (XN),6.3 µs (AOS). NEN rise R51×(Q9 Ciss+Q8 Coss) is86.5/138.5/70.5 µs.
These use capacitance at10/15 V rather than3.3 V and omit nonlinear Miller,
threshold spread, board capacitance and Q5/rail slew. They establish why XN's
larger charge is not a timing improvement; they are not accepted timing limits.
On main removal with USB present, Q8 releases NEN, then Q9 pulls EN low after
this analog transition. On main insertion the opposite sequence enables it.
Observe MAIN/NEN/TCA_EN/CE during later prototype ramps and removal; no added
supervisor, gate circuit or firmware work is proposed here.

**Preferred: AO3400A, LCSC C20917**, 20 pieces=15fit+1spare+4MOQ excess, USD1.96
cached page allowance. It has the smallest typical charge/capacitance of these
available options and sufficient static drive. It remains **unapproved** and is
not a proven full-temperature replacement. AOS hot-leakage data or prototype
characterization across the already intended operating range remains necessary.
This limitation is explicit, not a new ambient restriction or a waived OFF state.

PMV16XN is now genuinely sourced as **PMV16XNR, C110920**: page retrieved today,
cache today,65,625 displayed, MOQ/multiple5,20×USD0.1494=USD2.988. Nexperia's
[chemical/ordering record](https://www.nexperia.com/chemical-content/PMV16XN.html)
maps12NC934068844215 to PMV16XNR and type PMV16XN. The previous unsourced
“PMV16XN,215” proposal is corrected to this observed order identity. It is a
second choice, not a second purchase. PMV16UN remains EOL without trusted stock.

## C32 — input network, required capacitance and ripple

Actual accepted network: U3 SYS→3.3 V, L2=4.7 µH, RT floating (500 kHz nominal),
C32=2.2 µF/0805 and local C43=0.1 µF/0402. R06 specifies6–18 V and≥1 A normal
3V3 capability; the3 A IC rating is not a3 A board requirement. SYS is shared
with C21=10 µF/0805, charger banks and F5 input C60/C61=10 µF/50 V/1210 each.
Concurrent F5 load and charger switching also perturb this network.

Saved pad coordinates give straight-line VIN-to-SYS-pad distances: C43≈2.56 mm,
C32≈4.93 mm, C21≈30.61 mm (C21-to-C32≈35.45 mm). C60/C61 are around50 mm from
U3. These are exported physical distances, not routed loop inductance. The
previous progress estimate of roughly33 mm was approximate; use these computed
pad-to-pad distances. Remote banks cannot simply be summed as ideal local C.

[TPS62933 SLUSEA4D Rev.D §10.2.2.9](https://www.ti.com/lit/ds/symlink/tps62933.pdf)
requires input decoupling, voltage/ripple-current suitability and bias accounting;
10 µF is a typical recommendation, not a mandatory10 µF-effective minimum.
Its example's400 mV input ripple is not an approved UPS requirement.

For ideal CCM buck duty D≈3.3/VIN, the input-capacitor design relations are:

```
I_CIN,rms ≈ Iout*sqrt(D*(1-D))
ΔVcapacitive ≈ Iout*D*(1-D)/(fs*C_local_effective)
C_local_effective >= Iout*D*(1-D) / (fs*(allowed_ripple - ESR/ESL/source contributions))
```

At1 A, the rectangular-current RMS is0.497 A at6 V,0.387 A at18 V; its worst
over this range is0.5 A near6.6 V. Including ideal triangular inductor ripple
adds D*ΔIL²/12 under the RMS square root. With4.7 µH/500 kHz, estimates become
0.515 A at6 V and0.412 A at18 V. Losses, L tolerance, fs tolerance, PFM operation,
shared-source current and layout need further allowance; these are calculations,
not manufacturer-rated ripple capacity or measurements.

The saved Yageo9March2023 curve gives about0.5–0.6 µF typical at18 V. C32 alone
then gives about0.50–0.60 Vpp at1 A/18 V/500 kHz; TI's duty-independent0.25
envelope gives0.83–1.00 Vpp. If the local100 nF were ideal and fully effective,
the first figures become0.43–0.50 Vpp; its high-frequency impedance and ESL still
matter. The old illustrative0.38 µF tolerance/temp/aging screen is not a
guaranteed input-network minimum. At the IC's3 A rating these currents/ripples
scale by3, but that is a sensitivity case, not a newly imposed load requirement.

**Conclusion: no numerical Cmin can be established from the approved requirements
alone**, because neither allowable VIN ripple nor the source/route impedance and
combined capacitor current sharing is specified or measured. The calculation
does not prove the Yageo unacceptable; neither does nominal50 V prove it adequate.
Do not reduce an existing requirement or accept the part by borrowing ideal C21.
Preferred resolution is a manufacturer-supported same2.2 µF/0805 candidate plus
an input-impedance/ripple assessment against R06, followed by prototype waveforms.

TDK C2012X7R1H225K125AB is a same-nominal50 V/X7R/0805 catalog investigation
candidate, **not a qualified alternative**: thickness1.25 mm class would need
terminal/actual-land confirmation, bias and self-heating data. The attempted
official lookup/download was unavailable; no better Ceff is claimed. No change
to2.2 µF, footprint, copper or input architecture is selected. C32 stays HOLD.

## C33/C45 and C64/C65 — new numerical TDK evidence; suffix still open

The retained catalog part has published3.2±0.2×1.6±0.2×1.6±0.2 mm, X5R±15%,
22 µF±20%,35 V, DF≤10%, IR≥22 MΩ, −55..85°C. Existing1206 lands have2.95 mm
centres and1.15×1.8 mm copper envelopes. No body-height/termination/bias proof
for full TJ00E can be derived from a1206 label alone.

**New manufacturer export:** [TDK-C3216X5R1V226M160AC-dcbias.csv](../evidence/phase5-2-sourcing/TDK-C3216X5R1V226M160AC-dcbias.csv),
created19October2026 GMT by the official product page's DC Bias CSV control.
Downloaded through the browser after direct PDF requests returned403. The page
explicitly calls characteristic graphs reference data without a guarantee.

| Bias | One capacitor, typical | Pair, typical | Illustrative pair ×0.8 tolerance ×0.85 temperature |
|---|---:|---:|---:|
| 3.3 V | 16.671 µF (interpolation3.15–4 V) | 33.343 µF | 22.673 µF |
| 5.0 V | 12.8591 µF (exported point) | 25.7182 µF | 17.4884 µF |

Even before adding aging or small-AC uncertainty, this screening calculation is
below the **retained25 µF pair design basis**. It is not a guaranteed joint lower
bound or proof of actual failure. In particular,25.718 µF typical at5 V provides
little nominal margin and cannot establish25 µF over tolerance/temperature.

U3/U7 both have RT floating/500 kHz. TI Rev.D table10-2 gives minimum effective
COUT15 µF at3.3 V with4.7 µH and10 µF at5 V with6.8 µH (typical40/20 µF).
These minima do **not** supersede the project's25 µF basis; using a lower
effective value requires reviewed design evidence, not a purchasing substitution.
Output ripple, transient and loop requirements apply to both banks, including
the F5 pair before U8/Q10. No additional output capacitor is authorized.

TDK's [ordering FAQ](https://product.tdk.com/en/contact/faq/capacitors-0117.html)
and [part-number FAQ](https://product.tdk.com/en/contact/faq/capacitors-0116.html)
do not map the fullTJ00E code. The catalog gives only C3216X5R1V226MT****.
Farnell's alias and Arrow's dimensions corroborate plausibility but are not
manufacturer confirmation of controlled specification, dielectric stack or bias.
The exact manufacturer suffix query failed (502); **equivalence remains unproven**.
No contact or RFQ was sent. Preferred next step: obtain a TDK signed specification
or written mapping for both complete identities, including joint Ceff/aging/AC
conditions at3.3/5 V and the25 µF bank basis. Keep C342620 outside approved basket.

## C35/C36 — typical curve assessment complete; guarantees distinguished

Reuse the saved [Murata EC sheet](../evidence/phase5-1-sourcing/Murata-GRM21BR61E226ME44-EC.pdf)
(manufacturer-authored,12/2020, hosted by TI). It covers GRM21BR61E226ME44;
L is the proposed packing suffix.0805 body2.0±0.2×1.25±0.2×1.25±0.2 mm.
At120 Hz/0.5 Vrms the nominal tolerance range is17.6–26.4 µF. The DC curve at
that AC level reads roughly12–14 µF at3.3 V. These conditions differ from the
much smaller AC signal on a regulated output. The AC curve is typical too.

The previous4.7124 µF screen (22×0.50×0.80×0.85×0.90×0.70) is reproducible,
but its0.90 aging and0.70 small-AC factors are assumptions, not guaranteed Murata
limits. Bias/temp/AC/aging are not proven independent. The sheet explicitly says
typical specifications and requests approval specification before ordering.
Therefore it supports a prototype proposal with margin to the retained C35
2.2 µF effective LDO minimum, **not guaranteed combined qualification**.
C36 remains22 µF nominal MCU bulk; no new2.2 µF gate is assigned to it.

Preferred resolution: accept the exact Murata procurement proposal with this
documented qualification limit for prototype evaluation, or obtain its approval
specification if a guaranteed minimum is required. Neither acceptance nor hardware
validation occurs in Phase5.2. No larger capacitor/gating architecture proposed.

## TP1/TP3/TP4 — fabrication proposal cancelled by owner

Phase5.3 supersedes the former wire-loop proposal. No hardware purchase,
fabrication, spare or obligatory fitting is required. Existing PCB pads and
plated holes suffice for probing; optional loops are already owned. All geometry
is preserved. Historical pre-decision text is retained only in Phase5.3 entry evidence.

## L2/L3 — availability established for L2; L3 and delivered quote open

L2 **XAL5030-472MEC**, LCSC **C7432409**: retrieved19October, provider cache3days,
1,174 displayed, MOQ/multiple1,5×USD5.9335=USD29.6675. This is an actual
small-order supplier offer, not live reserved stock. No automatic spare.
Coilcraft's direct page showsUSD2.74 at1 (5=USD13.70) but its static rendering
contains both stock and unavailable-configuration text; actual UK stock unproved.

L3 **XAL5050-682MEC**,5 pieces: Coilcraft pageUSD3.02 at1 (5=USD15.10) is an
indicative allowance only; selected-configuration availability conflicts with
generic stock text. Coilcraft Europe says no minimum and general UK warehouse
stock, not this exact SKU. No actual5-piece stock/delivery quote established.

Farnell cut-tape2289069(L2)/2289071(L3) retain exact identities. Denmark's L2 page
has a last-month2,374 stock observation, not Czech stock confirmation. Swiss L3
page has a last-month26February2027 delivery estimate; no Czech fulfillment
commitment.5131620/5131621 full-reel400/250 offers are excluded. Neither stale
regional inventory nor the old unavailable DigiKey Marketplace line closes L3.

Request one combined5+5 exact-MEC Coilcraft Europe delivered quote, compared
with Farnell Czech cut tape. Freight, dispatch stock/date, lead time, incoterms,
VAT/import/handling remain unknown; no cheapest delivered claim is possible.
At the displayed prices L2's LCSC premium versus direct indication isUSD15.9675;
buying it with LCSC can save a separate shipment only if L3 is also consolidated.
No supplier message was transmitted.
