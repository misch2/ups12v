# Phase 5.0 — exact parts and accepted package reconciliation

**Historical Phase5.0 baseline.** Current quantity and blocker dispositions are in
[Phase5.2 compatibility review](PHASE5_2_COMPATIBILITY_REVIEW.md) and
[summary](SOURCING_SUMMARY.md). New evidence there supersedes incomplete bias and
package-option sourcing statements below; approved engineering decisions remain.

2026-10-19. Procurement proposal only. No CAD, manufacturing export or hardware
operation. The accepted schematic SHA256 is
`281d5eccd48a9b07f3ab3b7b836c7ad395af59487c775ad20a4efb3828bdba68`;
production PCB is `d0a8c95a1b8cfbeff1f4f7fa4a95abf297a86d9c95551ed5b7b3050f42b8ac2b`.
The Phase4.22A reference CSVs bind the population; later accepted paste adoption
preserved component identities, connectivity and footprints. Actual footprint
names are transcribed per reference in REFERENCE_POPULATION.csv. No fresh native
KiCad operation was needed or performed.

## Critical identities

| References | Exact purchasing identity and package | Manufacturer / accepted evidence and disposition |
|---|---|---|
| IC1 | TI **BQ25798RQMR**, RQM0029A VQFN-HR4x4, 29 logical pins/33 split physical lands | [SLUSDV2C June2026 §5 and drawing4225253/A](https://www.ti.com/lit/ds/symlink/bq25798.pdf); reuse [project map](../V4_CHARGER_PACKAGE_MAP.md). Current exported Value, manufacturer part field and package agree. BQ25792 is an historical alternative, not the selected purchase. No charging architecture change. |
| U1 | Espressif ESP32-C3-MINI-1-N4X; PCB antenna,4MB,61 physical lands/53 unique numbers | [Manufacturer v2.2 §§10.1/11.1](https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf); accepted local footprint and nine central grounds retained. Exact N4X DigiKey cut tape verified; N4, H4X and antenna-connector variants are not substituted. |
| U3/U7 | TI TPS62933DRLR, DRL8 SOT-583 | [SLUSEA4D RevD, package4224486/G](https://www.ti.com/lit/ds/symlink/tps62933.pdf). Preserve base TPS62933; F/P/O suffixes change operation. Accepted eight-pad footprint; no invented exposed thermal pad. |
| U8 | TI LM74700QDBVRQ1, DBV6 SOT-23-6 | [SNOSD17G RevG, DBV0006A4214840/G](https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf). Exact6-pin part retained; DDF8 is incompatible. DBVTQ1 is an unapproved packaging option, not selected. LCSC/DigiKey exact supply currently unavailable. |
| L1 | Owner-approved Eaton DR125-2R2-R,2.2uH20%,12.5x12.5x6mm body | [Eaton Technical Data4315 Sept2017 p6/p9](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-dr-high-power-density-high-efficiency-shielded-drum-core-power-inductors-data-sheet.pdf). Reuse accepted Phase4.24S manufacturer/land review. Generic footprint name L_12x12mm_H6mm is retained; owner's accepted prototype land deviation is not reopened.10.9A Irms/15A Isat are reference conditions, not hot board ratings. |
| L2/L3 | Coilcraft XAL5030-472MEC4.7uH / XAL5050-682MEC6.8uH | [Document908 revised2026-02-26](https://www.coilcraft.com/getmedia/49bc46c8-4b2c-45b9-9b6c-2eaa235ea698/xal50xx.pdf), accepted native XAL5030/XAL5050 lands and Phase3.6 calculations. L2 DCR40mOhm max/Isat6.7A; L3 DCR29.45mOhm max/Isat6A at25C,30% inductance drop. Irms20C-rise4.3A/4.7A. Hot losses remain hardware qualification. Exact MEC manufacturer quotes proposed; no XGL or different packaging code selected. |
| Q1/Q2/Q10 | AOS AON7528 DFN3.3x3.3;1-3S,4G,5-9D | [AON7528 Rev1.0 Oct2023](https://www.aosmd.com/sites/default/files/res/datasheets/AON7528.pdf); [PO-00093H drawing](https://www.aosmd.com/sites/default/files/res/packaging_information/DFN3.3x3.3_8L_EP1_S.pdf). Reuse accepted prototype2.45x2.00mm drain land and accepted paste windows; no new waiver or footprint change. LCSC's generic3x3 label does not override the AOS drawing. |
| U2 | Owner-approved TI TPD2EUSB30ADRTR, DRT3 | [SLVSAC2G RevG June2021 §5/mechanical appendix](https://www.ti.com/lit/ds/symlink/tpd2eusb30a.pdf), accepted Texas_DRT-3 map1=D+,2=D-,3=GND. Purchasable TI C94934; reject TECH PUBLIC same-named clone. Old G4 ordering suffix is superseded for purchasing by owner's exact selection only; CAD untouched. |
| J7 | Owner-approved GCT USB4085-GF-A | GCT USB4085 RevB2023-02-28 sheets1-2, retained Phase4.4/4.21/4.24S review. Current LCSC C7095263 exact manufacturer identity. Shell slots and accepted installed footprint retained; no new USB review. |
| R32/R33 | Retained TE RN73C1E31K6BTD / RN73C1E10KBTD,0402,0.1%,10ppm/K | [TE RN73C1E10KBTD exact drawing/datasheet](https://www.te.com/en/product-6-1879131-9.html); retained RN73 family and31.6k candidate. Do not use25ppm parts here. Exact cut-tape sourcing for both remains a quote task; R32 Mouser279-RN73C1E31K6BTD candidate exists. |
| R60 | Proposed KOA RN73R1JTTD5302B25,0603,53.0k,0.1%,25ppm/K,0.1W75V | [KOA2026 catalog RN73R ordering/rating tables](https://www.koaspeer.com/pdfs/KOA_2026FullCatalog_Linked.pdf); exact DigiKey2019-RN73R1JTTD5302B25CT-ND. TME5000-piece MOQ is unsuitable.53.6k is not interchangeable. |
| R61 | Proposed YAGEO RT0603BRD0710KL,0603,10k,0.1%,25ppm/K,0.1W75V | [Manufacturer exact specsheet generated2025-10-20](https://www.yageogroup.com/component-documentation/download/specsheet/RT0603BRD0710KL). LCSC C95204 current MOQ20. Earlier KOA10k candidate was unavailable; no engineering-approved part was replaced because this reference had OPEN MPN. |
| R62/R63 | Proposed YAGEO RC0603FR-07100KL / RC0603FR-0738K3L,0603,1%,100ppm/K,0.1W75V | [R63 manufacturer exact specsheet](https://yageogroup.com/component-documentation/download/specsheet/RC0603FR-0738K3L); exact values and0603 footprints retained. Precision0.1% is required for R60/R61, not invented for R62/R63. |
| U4 | AP7361C-33E-13,SOT223,IN1/GND2/OUT3,tab2 | [DS37274 Rev5-2 Oct2020](https://www.diodes.com/assets/Datasheets/AP7361C.pdf), accepted package review. ER suffix has different pinout and is not selected. |
| U5/U6 | TPS2116DRLR SOT583 / original TCA9517DGKR DGK VSSOP8 | Reuse [SLVSFG1A](https://www.ti.com/lit/ds/symlink/tps2116.pdf) and [SCPS157D](https://www.ti.com/lit/ds/symlink/tca9517.pdf), accepted Phase4.24S package review. TCA9517A/SOIC variants are not substitutes. |

## MLCC and open ordinary selections

C32 proposal YAGEO CC0805KKX7R9BB225 is2.2uF±10%,50V X7R,0805.
[Exact manufacturer specification](https://www.yageogroup.com/download/specsheet/CC0805KKX7R9BB225)
gives2.0x1.25mm body and1.25mm nominal thickness. This matches the accepted0805
package class and exceeds the retained nominal voltage requirement. A DC-bias
curve at18V and a combined tolerance/temperature/aging bound were not obtained.
It is **conditional**, not proof of2.2uF effective at18V. No larger footprint is proposed.

C35/C36 proposal Murata GRM21BR61E226ME44L is22uF±20%,25V X5R,0805,
1.45mm maximum thickness. Manufacturer
[SimSurfing exact core](https://ds.murata.com/simsurfing/mlcc.html?oripartnumbers=%5B%22GRM21BR61E226ME44L%22%5D&partnumbers=%5B%22GRM21BR61E226ME44%22%5D&rgear=suaykx&rgearinfo=com&videoId=5970368750001)
lists it in production. The interactive bias graph was not exported; no numerical
Ceff claim is made. C35 must satisfy AP7361C's retained2.2uF effective minimum
at3.3V over the intended operating conditions. Nominal22uF and25V alone do not
establish that. C36 mux transient qualification is unchanged.

C33/C45/C64/C65 retain TDK C3216X5R1V226M160AC,22uF35V X5R20%,1206.
[TDK exact page](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3216X5R1V226M160AC)
reports **Production** and item-description family C3216X5R1V226MT****. Current
supplier exact stock is problematic. Farnell calls C3216X5R1V226MTJ00E "Also Known As";
that is a concrete supplier/manufacturer naming lead, not complete proof of
identical bias curves or packaging. It remains an explicitly unapproved option.

C70/C71 retain GRM188R71C105KA12D in the main BOM. DigiKey flags that ordering
code obsolete; LCSC C97890 is unavailable. J suffix is also marked obsolete by
DigiKey. Candidate TDK C1608X7R1C105K080AC is1uF16V X7R10%,0603; its supplier
package/ratings agree, but its exact primary manufacturer page could not be
retrieved successfully. It is an **unapproved same-footprint candidate**, not a
substitution already made.

Open100nF0402 positions propose the existing50V Murata GRM155R71H104KE14D;
open4.7uF0805 and10uF0805 positions reuse existing exact identities with matching
or higher voltage grade. C29 uses manufacturer-confirmed GRM155R61C105KA12D
1uF16V X5R0402. C39 uses GRM155R71H333KE14D33nF50V X7R0402. These are
procurement proposals against existing values/packages, not changes to source CAD.
Bulk charger MLCC bias/ripple evidence is reused, not promoted to measurement.

Ordinary resistors propose economical YAGEO RC/RT exact values and packages;
R9/R10 use the retained precision RT0805 candidate, R12 retains its high-pulse
Vishay HP identity (0.75W) and must not become a generic2ohm chip. Q4/Q6/Q7
propose Nexperia BC847B,215; Q5 BC857B,215,1=B2=E3=C. Manufacturer BC847x
ordering table lists groupB active; suffix resolution does not change the circuit.
Q3/Q8/Q9 retain core PMV16UN, with215 only a provisional procurement suffix;
legacy NXP stock/EOL and current Nexperia identity are not conflated. No verified
loose-component source was secured. TP1/TP3/TP4 retain real fitted loop hardware,
but exact MPN/lead/body compatibility remains open. No silent1.02mm minimum-hole
part is claimed to fit the accepted1.0mm drill.

D2's retained historical source candidate **Dialight597-3605-607F is blue465nm
with a Zener**, not green. [Dialight SMD selector guide2021 p11](https://www.dialight.com/wp-content/uploads/2021/07/DIA_Selector_Guide_SMD_042321.pdf)
identifies0805,2.0x1.25x0.8mm, pin1 cathode/pin2 anode and2mA optical test
conditions (Vf2.8V typical/3.05V maximum). The accepted schematic value is generic
LED; this exact sourcing proposal is not an approved color decision or CAD change.
MCC's manufacturer RoHS/package list confirms BZT52C12-TP as SOD-123 for D1.

Mechanical deviations already accepted for prototype use remain accepted. Hardware
assembly fit, bias, thermal and electrical qualification are distinct from this
desk sourcing review. No new electrical requirement or power-up approval follows.
