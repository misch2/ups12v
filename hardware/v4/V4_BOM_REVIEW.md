# V4 BOM review — power-stage and MCU-domain design inventory

Updated 2026-10-10. Preferred suppliers are TME.eu and LCSC.com under current
`AGENTS.md`; manual assembly and total small-order cost matter. This inventory
covers the power stage, Phase 3.1 MCU/native-USB checkpoint, and the current
Phase 3.2 MCU power-domain/isolation schematic checkpoint. The domain design
is still PROPOSED and is not a purchase, PCB or power-up approval.
One PCB is retained for S792-2/S792-4/S798-2/S798-4 and later F0/F5 overlays.
No schematic/BOM freeze, purchase, board order or power-up approval is implied.

`PROPOSED` is a design candidate with outstanding acceptance; `VERIFIED` requires
explicit identity/package/sourcing evidence with stated limits; `APPROVED`
requires owner approval; `REPLACE` flags an unsuitable fitted choice or a needed
metadata correction. Accepted pin maps alone do not mean hardware qualification.
Current populations therefore remain PROPOSED unless expressly stated otherwise.

## Current decisions and unresolved sourcing

| References / function | Exact identity and alternative | Sourcing and acceptance status |
| --- | --- | --- |
| IC1 charger, qty 1 | TI BQ25798RQMR; alternate BQ25792RQMR in S792 profiles. RQM VQFN-HR, official 29-logical-pin footprint with split corner lands. | BQ25798 catalog identity: [LCSC C2876593](https://www.lcsc.com/product-detail/C2876593.html), retrieved 2026-10-10, crawl four weeks old. Page displayed USD 2.9532 at 1+, MOQ/multiple 1 and positive stock; **current price/availability UNVERIFIED**. Exact TME link OPEN. Shared mapping in `V4_CHARGER_PACKAGE_MAP.md`; prototype qualification pending. BQ25792 custom-order limitation in procurement record; preserve required variant. |
| C12/C13/C15/C16/C18 input/PMID bulk ceramics, qty 5 | Murata GRM32ER71H106KA12L, 10 uF/50 V X7R 10%, 1210. Alternative TDK C3225X7R1H106M250AC is only a candidate, with looser 20% tolerance and unaccepted bias/package checks. | [TME GRM32ER71H106KA12L](https://www.tme.eu/en/details/grm32er71h106ka12l/mlcc-smd-capacitors/murata/), cached zero stock. [LCSC C77102](https://www.lcsc.com/product-detail/C77102.html) exact identity found; current price/MOQ/stock **UNVERIFIED**. Ceff/ripple/aging budget pending; do not silently substitute the TDK candidate. |
| C6/C7/C9 bypass, qty 3 | Murata GRM155R71H104KE14D, 100 nF/50 V X7R 10%, 0402. | Exact [TME code](https://www.tme.eu/en/details/grm155r71h104ke14d/mlcc-smd-capacitors/murata/) catalog identity accepted; current stock/price/MOQ UNVERIFIED. LCSC code OPEN. |
| C3 REGN, qty 1 | Murata GRM21BR71E475KA73L, 4.7 uF/25 V; 0805 assigned. | Updated source recorded in CAD; new manufacturer/physical-map acceptance and current procurement verification need explicit evidence. Preserve the 4.7 uF function; a voltage-metadata correction is not a measured Ceff result. |
| C4/C10/C11/C14/C17/C19/C21 BAT/SYS, qty 7 | Murata GRJ21BR61E106KE01K, 10 uF/25 V X5R 10%, 0805. | Exact MPN/manufacturer/dielectric fields corrected using manufacturer reference -02A (2024-12-10), reviewed 2026-10-10; see `V4_STAGE2_PARTS.md`. Historical TME Source/Bought preserved. Current price/MOQ/stock UNVERIFIED; Ceff over SYS/BAT envelope OPEN. Population remains PROPOSED. |
| C8 SDRV, qty 1 | Murata GCM1555C1H102JA16D, 1 nF/50 V C0G (NP0) 5%, 0402. | Fields reconciled using manufacturer reference -01A (2022-04-08), reviewed 2026-10-10; see `V4_STAGE2_PARTS.md`. Historical TME Source/Bought preserved; [LCSC C437434](https://www.lcsc.com/product-detail/C437434.html) discovered. Current price/MOQ/stock UNVERIFIED. Population remains PROPOSED. |
| C20/C22/C24/C25 optional PMID bulk | Legacy Panasonic 20TQC47MYF and EEEFK1E470P. | **REPLACE if fitting**: 20/25 V ratings unsuitable for 21 V plus retained derating target. Default DNP for initial VSYS prototype; forward Ceff/transient qualification still required. No PMID backup assembly approved. |
| D3/D4 CE diode OR, qty 2 | Nexperia BAS116H,115, SOD123F. | [TME BAS116H.115](https://www.tme.eu/en/details/bas116h.115/smd-universal-diodes/nexperia/bas116h-115/) identity/pin map in part acceptance; current stock/price/MOQ UNVERIFIED. |
| Q3 CE sink, qty 1 | Nexperia PMV16UN, SOT23. | Accepted G/S/D drawing and package mapping; exact reel suffix and preferred-supplier orderable identity OPEN. Do not substitute an electrical 2N7002 based on the drawing used. |
| Q1/Q2 input FET pair, qty 2 | AOS AON7528, DFN 3.3 x 3.3. | Retained recorded TME identity; 30 V VDS and 20 V VGS absolute limits are not transient/SOA qualification. Supported cable/source hot-plug and thermal evidence pending. |
| F1 adapter fuse, qty 1; PROPOSED | Littelfuse 0451005.MRL (5 A), 2410; 4 A alternative compared but not selected. `ups_v4:Littelfuse_451_2410`. | Manufacturer land comparison completed and footprint corrected through Konnect: pads 1.9558 x 3.1496 mm at +/-2.4511 mm. See [land review](evidence/phase2-6-fuse-land-review.md), manufacturer GD.12/01/25 p.4 and disposable verification limits. Existing TME 0451005.MRL / LCSC C48467 identities retained in procurement record; current price/MOQ/stock UNVERIFIED. Temperature, fault interruption, cable/BMS and hot-plug I2t coordination remain qualification gates. |
| R12/C26 VIN hot-plug shunt, qty 1 each in all four VSYS variants; PROPOSED | Vishay CRCW12062R00JNEAHP, 2 ohm 5%, 1206, `Resistor_SMD:R_1206_3216Metric`; KEMET C1210C225K1RACTU, 2.2 uF/100 V X7R 10%, 1210, `Capacitor_SMD:C_1210_3225Metric`. Murata GRM32ER72A225KA35L remains REPLACE/NRND, not fitted. | Implemented through Konnect. Electrical/package/pulse basis and dated sourcing in [phase 2.6 review](evidence/phase2-6-hotplug-envelope.md). LCSC C2168116 earlier live 2026-10-10: USD 0.2408, MOQ 1, stock 10. Same-date live DigiKey CZ: resistor 541-2.0UACT-ND, MOQ 1, 7.47 CZK ex VAT, stock 8219; capacitor 399-C1210C225K1RACTUCT-ND, MOQ 1, 23.27 CZK ex VAT, stock 387673. Shipping/total-order arithmetic and links in evidence; no order approved. Exact preferred-supplier resistor identity and current TME pricing remain OPEN (access denied). Generic land deviations recorded for PCB library freeze. Estimated Ceff is sensitivity evidence, not a guaranteed minimum; actual damping and pulse qualification remain open. |
| L1 energy storage, qty 1 | Eaton DR125-2R2-R, inherited 2.2 uH / 750 kHz selection. | Recorded [TME code](https://www.tme.eu/cz/details/dr125-2r2-r/tlumivky/eaton-electronics/). Manufacturer saturation/ripple/750 kHz loss and exact installed geometry remain qualification items. No current price/MOQ/stock claim. |
| R5 PROG, qty 1 | 27 kOhm for S792-4/S798-4; 8.2 kOhm for S792-2/S798-2, fixed by assembly. | Exact 1% MPNs OPEN. One physical resistor position; never populate both values or expose a cell-count jumper. |
| J1/J2/J3/J4/J6 connectors | Current footprints/headers are inherited; exact housings, keyed contacts, ratings and harness assemblies OPEN. | J6 historical thermistor URL describes the external NTC, not the connector. Specify separately before freeze. J4 is incompatible with V3 wiring; MAIN_3V3 is a normal-domain input, never USB 3V3. |
| Remaining resistors/LED/testpoints | Recorded CAD inventory below; exact orderable identities mostly OPEN. | Prefer common values/packages and existing valid sourcing. No stock, price or supplier code is invented. |

## Phase 3.2 MCU power domains and isolation checkpoint (2026-10-10)

The normal regulator U3 is the source of `MAIN_3V3`; the independent USB
regulator U4 produces `USB3V3`. TPS2116 U5 selects `MAIN_3V3` with normal
priority or `USB3V3` for USB-only recovery and produces `MCU3V3`. USB VBUS
has no schematic path to `SYS`, `BATTERY`, `REGN` or `MAIN_3V3`.
The charger gate includes R47, a 100 kOhm pulldown on the MCU request
transistor base, so reset/high-impedance firmware state defaults to disabled.
The exact regulator inductor and ceramic capacitor MPNs remain ordinary
prototype candidates; their effective capacitance, ripple current, thermal
loss and cable-drop margins require hardware qualification.

| References / function | Exact identity, package and quantity | Sourcing / acceptance status |
| --- | --- | --- |
| U3 normal 3V3 buck, qty 1 | Texas Instruments TPS62933DRLR, SOT-583-8; SYS input; R32 31.6 kOhm / R33 10 kOhm, both 0.1% / 10 ppm per degC, nominal 3.328 V. Owner-authorized full-budget correction; see Phase 3.6 review. | **PROPOSED**, retained. Approximately 1 A MCU demand; 3 A IC rating provides margin. Current/thermal and mux-drop validation remain OPEN. |
| U4 service USB LDO, qty 1, fitted all initial profiles | Diodes Incorporated AP7361C-33E-13, fixed 3.3 V, 1 A class, SOT-223; `Package_TO_SOT_SMD:SOT-223-3_TabPin2`. E pinout IN1/GND2/OUT3, ground tab=2; ER is incompatible. | **PROPOSED**. [LCSC C500795](https://www.lcsc.com/product-detail/C500795.html), cached observation 2026-10-10: USD 0.8178 at 1+, MOQ/multiple 1, 3,168 displayed; [TME exact MPN](https://www.tme.eu/cz/details/ap7361c-33e-13/stabilizatory-napeti-neregulovane-ldo/diodes-incorporated/), cached zero stock, CZK 9.45 ex VAT at 1+. Current stock/price unverified; shipping not quoted. [Manufacturer and service thermal/dropout rationale](evidence/phase3-4-usb-ldo-selection.md). No substitute selected; Wi-Fi off; 1 A continuous USB operation not claimed. |

| U5 normal-priority mux, qty 1; R23/R24 divider qty 1 each | Texas Instruments TPS2116DRL, SOT-583-8; MODE/VIN1=`MAIN_3V3`, VIN2=`USB3V3`, output=`MCU3V3`. R23=8.2 kOhm, R24=4.7 kOhm, 1%, 0402, MAIN-referenced PR1 divider. | **PROPOSED**, TI Rev. A Sections 5–8. Built-in priority comparator replaces U7 supervisor. Comparator tolerance/loading is recorded in current simplification evidence; source-transition MCU restarts are acceptable. Reverse blocking and safe partial-power operation still require prototype verification. No reset-free claim. |
| U6 I2C domain buffer, qty 1 | Texas Instruments TCA9517DGKR, original Rev.D, VSSOP-8; VCCA/A=`MAIN_3V3`, VCCB/B=`MCU3V3`; 4.7 kOhm pull-ups each side. | **PROPOSED**, TI original Rev.D Sections 3/5/7.5/9. Retain Q8/Q9 isolated EN so its internal MCU-side pull-up cannot bias MAIN. R07 leakage is a measurement target; unsafe back-power remains prohibited. |
| Q5/Q6/Q7 charger-domain drive, qty 3; R44/R46/R47/R50/R53 | BC857 PNP and two BC847 NPN, SOT-23; main-owned CE drive with simple firmware request. R44/R47/R50=100 kOhm; R46=4.7 kOhm; R53=10 kOhm; 0402. | **PROPOSED**, exact manufacturer/suffix/supplier OPEN. No latch or fresh-edge state. R50 derives Q6 bias directly from MAIN_3V3; transistor isolation retains default-off and USB/main separation. Final pin mapping and rationale are in current evidence. R11.2 remains service no-connect; external CHG_REQ cannot enable charge. |
| Q8/Q9 EN isolation, qty 2; R51/R52 pull-ups, qty 2 | Nexperia PMV16UN, SOT-23; Q8 gate=`MAIN_3V3`, Q8 drain=`NEN`, Q9 gate=`NEN`, Q9 drain=`TCA_EN`; both sources PGND. 100 kOhm MCU-owned pull-ups, 0402. | **PROPOSED**. Preserve EN partial-power isolation; gate leakage and transition timing require matching-hardware tests. No external MAIN supervisor retained. |
| L2 normal regulator inductor, qty 1 | Coilcraft XAL5030-472MEC 4.7 uH candidates; `Inductor_SMD:L_Coilcraft_XAL5030-XXX`. | **PROPOSED**. Retained footprint identity is exported; no new physical land-pattern or current/DCR/temperature qualification is claimed. Exact manufacturer rating reconciliation and supplier price/MOQ/stock remain OPEN before freeze. |
| Retained normal regulator/interface support | U3 retains its 2.2 uF + 100 nF input, 2 x 22 uF output, 100 nF 25 V bootstrap, 33 nF soft-start and feedback/EN parts; TCA9517 bypass retained. Per-reference quantities/footprints in fresh XML inventory below. | **PROPOSED**. Preserve package/voltage/Ceff/ripple and thermal checks; exact ordinary passive MPNs may finish at BOM freeze. |
| Removed simplification candidates — fitted qty 0 | U7/U8/U9/U10/U11/U12, Q10, D5, C41/C42/C49/C50/C51/C52, R54/R55/R56/R57. | **REPLACE / REMOVED**, owner-approved simplification 2026-10-10: MAIN/authorization/reset supervisors, latch/Schmitt/live-arm, TPS22975 and 470 uF hold-up circuitry. Retain historical supplier evidence only as history; do not populate these removed references. |
| R35 USB3V3 bleeder, qty 1 | 10 kOhm, 0402; exact manufacturer/MPN OPEN; fitted all initial profiles. | **PROPOSED**. Reuses the former USB FB lower resistor from USB3V3 to PGND. Approx. 0.33 mA load; provides finite leakage/discharge path. Dynamic unplug behavior remains a prototype check. |
| C35/C40 USB LDO output bypass, qty 1 each | C35 retained 22 uF candidate, 0805; C40 repurposed from 33 nF soft-start to 100 nF output bypass, 0402. Exact MPNs OPEN. | **PROPOSED**, all initial profiles, fitted. Effective C35 must meet the LDO's 2.2 uF output minimum; nominal capacitance is not Ceff evidence. |
| Removed USB-buck support — fitted qty 0 | L3, R34/R38/R39, C34/C38/C44/C46; U4 replaced, not an additional IC. | **REPLACE / REMOVED**, owner-selected service LDO follow-up. Historical supplier/part evidence is preserved in baseline copies; do not populate removed references. |



Cross-domain UART, strap, INT, I2C and USB D+/D- nets retain explicit labels
and pull-up domains. USB ESD remains rail-less on the D+/D- pair, and the
optional series-resistor footprints and BOOT/RESET straps remain available in
the Phase 3.1 schematic. MCU_CHG_ARM is now GPIO0/pad 12; GPIO7/pad 21 is
reserved as MCU_GPIO7 so ROM/JTAG defaults cannot authorize charging. No PCB
layout or footprint placement is authorized.

## Phase 3.1 MCU and native USB checkpoint (2026-10-10)

These entries are schematic candidates only. No purchase, PCB update or
hardware power-up approval is implied. `OPEN` identities remain unresolved
until exact manufacturer part, package/land pattern and preferred-supplier
evidence are recorded.

| References / function | Exact identity, package and quantity | Sourcing / acceptance status |
| --- | --- | --- |
| U1 ESP32-C3 module, qty 1 | Espressif `ESP32-C3-MINI-1-N4X` (current recommended variant); custom symbol uses Datasheet v2.2 Table 3-1 pin map. Project footprint `ups_v4:ESP32-C3-MINI-1-N4X`. | **PROPOSED / footprint corrected through Konnect**. The prior global footprint had 62 pads, duplicate numbers and unmodelled center pads. The project footprint now has 61 physical pads but 53 unique numbers: 48 edge lands, four corner lands, and nine 1.45 mm square central lands all numbered pad 49 at +/-1.975 mm centers, forming the 5.4 mm center array. See `evidence/references/esp32-c3-mini-1-v2.2.pdf` and `-land.png`; compare again before PCB placement. Preferred-supplier identity/price/stock OPEN. |
| J7 USB-C receptacle, qty 1 | `Connector:USB_C_Receptacle_USB2.0_16P`; footprint `Connector_USB:GCT_USB4105-xx-A_16P_TopMnt_Horizontal`; exact connector suffix/MPN OPEN. | **PROPOSED**. USB-C CC pulldowns, VBUS decoupling and shield/GND connections are drawn; exact manufacturer identity, ratings and supplier evidence OPEN. |
| U2 USB ESD, qty 1 | Texas Instruments `TPD2EUSB30ADRTRG4` (TPD2EUSB30A, provisional), 3-pin `Package_TO_SOT_SMD:Texas_DRT-3`; no VBUS clamp pin. | **PROPOSED** from TI SLVSAC2G Rev. G (June 2021), Section 5/Table 5-1: D+ pin 1, D- pin 2, GND pin 3. This rail-less candidate shunts the connector-side USB pair to PGND without injecting into floating USB VBUS; exact preferred-supplier evidence remains OPEN. |
| R48/R49 USB data series options, qty 2 | `0R` default populated links, with `22R` optional signal-integrity value; `Resistor_SMD:R_0402_1005Metric`, placed between the connector/ESD side and ESP32-C3 USB pins. | **PROPOSED / fit 0R by default** so native USB recovery remains connected; 22R qualification and exact MPN remain OPEN. |
| R13/R14 USB-C CC pulldowns, qty 2 | 5.1 kOhm 1%, `Resistor_SMD:R_0402_1005Metric`; exact MPN OPEN. | **PROPOSED**; verify USB-C sink configuration, rating and supplier identity before freeze. |
| C27 USB LDO input bypass, qty 1 | 4.7 uF 10 V candidate, `Capacitor_SMD:C_0805_2012Metric`; exact MPN OPEN. | **PROPOSED**; USB VBUS tolerance/inrush/ESD and source capability remain unqualified. |
| C28 USB LDO input HF bypass, qty 1 | 100 nF 10 V candidate, `Capacitor_SMD:C_0402_1005Metric`; exact MPN OPEN. | **PROPOSED**; exact MPN and supplier evidence OPEN. |
| R15/R16/R17/R18 strap/reset bias, qty 4 | 10 kOhm 1%, `Resistor_SMD:R_0402_1005Metric`; exact MPN OPEN. | **PROPOSED**; GPIO2/GPIO8/GPIO9/EN boot and reset behavior is schematic-only pending firmware/hardware qualification. |
| C29 EN reset RC, qty 1 | 1 uF provisional, `Capacitor_SMD:C_0402_1005Metric`; exact MPN OPEN. | **PROPOSED**; 1 uF follows the Espressif ESP32-C3 schematic checklist recommendation for EN timing. Exact MPN and reset timing/USB-only recovery behavior remain OPEN. |
| C30 MCU3V3 bulk bypass, qty 1 | 10 uF provisional, `Capacitor_SMD:C_0805_2012Metric`; exact MPN OPEN. | **PROPOSED**; local MCU3V3 bulk decoupling added for the deferred normal/USB power-domain design. Exact MPN, bias derating and source-domain qualification remain OPEN. |
| C31 MCU3V3 HF bypass, qty 1 | 100 nF provisional, `Capacitor_SMD:C_0402_1005Metric`; exact MPN OPEN. | **PROPOSED**; local high-frequency MCU3V3 bypass. Exact MPN and placement/return qualification remain OPEN. |
| SW1/SW2 manual recovery/reset, qty 2 | `Switch:SW_Push`; installed-library footprint `Button_Switch_SMD:SW_SPST_EVQP0`; exact MPN OPEN. | **PROPOSED**. The footprint library link now resolves in the installed KiCad library; exact switch identity, land pattern and supplier evidence remain OPEN. |

New significant alternatives require manufacturer and package checks before
selection. The Konnect local JLC component search was called on 2026-10-10 but
reported **database not found**; this is unavailable discovery, not zero parts
or zero stock. LCSC catalog identities above came from supplier web pages.
Do not use JLC assembly-library status as loose-component availability.

Price, MOQ and inventory observations are cached unless a live supplier check
is expressly recorded. Actual prototype total including shipping is OPEN; no
cost optimum or purchasing decision is claimed. Review every critical part and
any footprint-changing alternative before PCB ordering.

## Inventory maintenance

After any coherent component/value/footprint change, export fresh XML and run
`python hardware/v4/evidence/build_bom_review.py <fresh-export.xml>`.
This replaces only the inventory below, preserving these manual review decisions.
Then update relevant decisions above, DNP/variant quantities and procurement
evidence. Exported MPN fields marked OPEN must be resolved before freeze.

## Phase 3.6 schematic completion (2026-10-10)

Current service-pad authority: [Phase3.7 review](evidence/phase3-7-review.md), [population CSV](evidence/phase3-7-population.csv), fresh `phase3-7-final.net.xml` (152 components). Unchanged power calculations: [Phase3.6](evidence/phase3-6-review.md). All selected parts remain **PROPOSED**; supplier identity/observations do not imply owner approval or qualified hardware. The following table supersedes older missing-F5/UART and capacitor-selection statements. Exactly one PCB; F5 quantities are zero in F0. Prices are observed USD unit prices, excluding shipping/tax; no complete basket/shipping quote obtained.

| References / qty F5 (F0) | Manufacturer / exact MPN; package and KiCad footprint | Supplier evidence / alternatives / status |
| --- | --- | --- |
| U7 / 1 (0) | Texas Instruments TPS62933DRLR, SOT-583-8; `Package_TO_SOT_SMD:SOT-583-8` | [LCSC C3200405](https://www.lcsc.com/product-detail/C3200405.html), verified2026-10-10: stock32,215, MOQ/multiple1, USD0.6114 at1. TME exact item OPEN. No alternate approved; PROPOSED. |
| U8 / 1 (0) | Texas Instruments LM74700QDBVRQ1, DBV6; `Package_TO_SOT_SMD:SOT-23-6` | [LCSC C2941042](https://www.lcsc.com/product-detail/C2941042.html), verified2026-10-10: stock47, MOQ/multiple1, USD2.4712 at1. TME exact item OPEN. Do not substitute a different controller pinout; PROPOSED. |
| Q10 / 1 (0) | Alpha & Omega AON7528, DFN3.3x3.3; `easyeda2kicad:DFN-8_L3.3-W3.3-P0.65-BL-3` | [Recorded TME](https://www.tme.eu/cz/details/aon7528/tranzistory-s-kanalem-n-smd/alpha-omega-semiconductor/); current price/MOQ/stock unverified. LCSC exact code OPEN. Same candidate as Q1, pins1-3S/4G/5-9D confirmed. Footprint courtyard missing: resolve before layout freeze. No alternate approved; PROPOSED. |
| L3 / 1 (0) | Coilcraft XAL5050-682MEC, 6.8uH20%; `Inductor_SMD:L_Coilcraft_XAL5050-XXX` | Exact TME/LCSC listing not found. [DigiKey Marketplace candidate](https://www.digikey.com/en/products/detail/coilcraft/XAL5050-682MEC/21381690) retained because manufacturer reference inductor is electrically suitable; current stock/price/MOQ/shipping OPEN. Alternate common 6.8uH requires DCR, hot saturation, current and footprint review; none approved. PROPOSED. |
| R60,R61 / 1 each (0) | Manufacturer/MPN OPEN; 53k/10k, 0.1%,25ppm or better,0603; `Resistor_SMD:R_0603_1608Metric` | TME/LCSC exact sourcing OPEN, no invented order codes/stock. Alternative matching values/tolerance/TCR/package after verification. PROPOSED; resolve before freeze. |
| R62,R63 / 1 each (0) | Manufacturer/MPN OPEN;100k/38.3k1%,0603; `Resistor_SMD:R_0603_1608Metric` | TME/LCSC sourcing OPEN. Common 1%0603 alternatives with suitable voltage/TCR and EN-limit check; PROPOSED. |
| C60,C61 / 2 (0) | Murata GRM32ER71H106KA12L,10uF50VX7R10%,1210; `Capacitor_SMD:C_1210_3225Metric` | Same exact part as existing charger bulk; [LCSC C77102](https://www.lcsc.com/product-detail/C77102.html), existing TME record retained above. Current price/MOQ/stock unverified. TDK alternate above remains conditional, no silent substitution. PROPOSED. |
| C62,C66,C67,C68,C69 / 5 (0) | Murata GRM188R71H104KA93D,100nF50VX7R10%,0603; `Capacitor_SMD:C_0603_1608Metric` | [TME exact identity](https://www.tme.eu/gb/details/grm188r71h104ka93d/mlcc-smd-capacitors/murata/) checked2026-10-10; price/MOQ/stock unverified, LCSC code OPEN. Alternative same rating/dielectric/size after verification; PROPOSED. |
| C63 / 1 (0) | Murata GRM188R71H333KA61D,33nF50VX7R10%,0603; `Capacitor_SMD:C_0603_1608Metric` | [LCSC local catalog identity](https://item.szlcsc.com/87201.html) checked2026-10-10; global order code/current stock/price/MOQ and TME exact listing OPEN. Same-grade alternate conditional; PROPOSED. |
| C64,C65 / 2 (0) | TDK C3216X5R1V226M160AC,22uF35VX5R20%,1206; `Capacitor_SMD:C_1206_3216Metric` | [TME exact identity](https://www.tme.eu/gb/details/c3216x5r1v226mac/mlcc-smd-capacitors/tdk/c3216x5r1v226m160ac/), LCSC C69612 identity checked2026-10-10; price/MOQ/stock unverified. TI reference-design pair; manufacturer combined Ceff bound OPEN. No unverified lower-voltage substitute. PROPOSED. |
| J8 / 1 (0) | Phoenix Contact1757242, MSTBA2,5/2-G-5,08; `Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal` | Manufacturer drawing/rating checked2026-10-10; TME/LCSC exact procurement/price/MOQ/stock OPEN. Mating1757019 harness candidate, not PCB quantity and not approved. Compatible alternate must preserve keyed polarity/pitch/mechanics; PROPOSED. |
| R32,R33 / common 1 each | TE Connectivity RN73C1E31K6BTD / RN73C1E10KBTD candidates;31.6k/10k0.1%10ppm,0402; `Resistor_SMD:R_0402_1005Metric` | [TE10k identity](https://www.te.com/en/product-6-1879131-9.html) verified active2026-10-10;31.6k exact ordering identity needs final confirmation. TME/LCSC exact codes/current price/MOQ/stock OPEN for both. Alternative0.1%10ppm or better same values/package; PROPOSED. |
| C33,C45 / common 2 | TDK C3216X5R1V226M160AC,22uF35VX5R20%,1206; `Capacitor_SMD:C_1206_3216Metric` | Same sourcing as C64/C65. Explicit change from generic0805 to1206, value unchanged; Ceff/ripple still conditional. PROPOSED. |
| TP5-TP8,TP13-TP17 / 9 copper pads, zero fitted parts | Manufacturer/MPN not applicable; `TestPoint:TestPoint_Pad_D1.5mm` | F.Cu/F.Mask, no paste; no purchased parts. F0/F5 common copper; TP17 isolated inF0. Only TP5 ESP_TX(GPIO21),TP6 ESP_RX(GPIO20),TP7 GND form the optional2.54mm edge UART row, no fitted header. TP8 MCU3V3/TP13 MAIN_3V3 separate measurement only. TP9-TP12 removed, buttons retained; TP14 passive charger-domain CE_N bring-up probe separate fromUART. Mechanical keying/edge access during PCB layout; nativeUSB is primary service. PROPOSED. |

Preferred practical basket is LCSC for U7/U8 and appropriate common passives, TME for existing sourced parts/connector where available; L3 alternative supplier only if preferred-supplier search remains unsuccessful. Konnect LCSC/JLC catalog query returned database NOT_FOUND; web sources were used instead. Manual assembly, not assembly-library availability, governed selection. Record actual small-order shipping/MOQ economics before purchasing; no basket is approved yet.

Before freeze: resolve exact feedback/enable resistor orders, L3 availability or reviewed compatible alternative, J8 mating harness and existing J1/J2/J3/J4/J6/J7/NTC identities, input capacitor Ceff (C32/C43), C35 USB Ceff, exact BC847/BC857 suffixes, pack fuse/protection assembly and Q10 courtyard/land-pattern qualification. These ordinary sourcing items do not invalidate a provisional schematic review; footprint changes require Konnect updates and fresh checks. VAC1 fabrication/power-up block and BQ25792 2S default2A risk remain OPEN. See current handover for owner-review boundary.

<!-- EXPORTED CAD INVENTORY -->

Inventory source: `phase3-7-final.net.xml`.

Quantities below count schematic instances per PCB, not fitted quantities. Apply the explicit base-profile and F0/F5 population tables above; all F5-only references are DNP in F0.

### C1, C2, C23 — 47n 25V

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 3 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/gcm155r71e473ka55d/kondenzatory-mlcc-smd/murata/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `X7R`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C3 — 4.7u 25V

- Manufacturer / exact recorded MPN: Murata / `GRM21BR71E475KA73L`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: REGN ceramic.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/grm21br71e475ka73l/kondenzatory-mlcc-smd/murata/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `X7R`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C4, C10, C11, C14, C17, C19, C21 — 10u 25V

- Manufacturer / exact recorded MPN: Murata / `GRJ21BR61E106KE01K`.
- Quantity: 7 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/grj21br61e106ke01k/kondenzatory-mlcc-smd/murata/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `X5R; +/-10%; -55 to +85 degC`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C5 — 100n 25V

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/gcm155r71e104ke02d/kondenzatory-mlcc-smd/murata/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `X7R`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C6 — 100n 50V

- Manufacturer / exact recorded MPN: Murata / `GRM155R71H104KE14D`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: PMID ceramic.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/en/details/grm155r71h104ke14d/mlcc-smd-capacitors/murata/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `X7R`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C7 — 100n 50V

- Manufacturer / exact recorded MPN: Murata / `GRM155R71H104KE14D`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: VBUS ceramic.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/en/details/grm155r71h104ke14d/mlcc-smd-capacitors/murata/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `X7R`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C8 — 1nF, 50V

- Manufacturer / exact recorded MPN: Murata / `GCM1555C1H102JA16D`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/gcm1555c1h102ja16d/kondenzatory-mlcc-smd/murata/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `C0G (NP0); +/-5%; -55 to +125 degC`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C9 — 100n 50V

- Manufacturer / exact recorded MPN: Murata / `GRM155R71H104KE14D`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: VIN1 input ceramic.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/en/details/grm155r71h104ke14d/mlcc-smd-capacitors/murata/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `X7R`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C12, C15, C18 — 10u 50V

- Manufacturer / exact recorded MPN: Murata / `GRM32ER71H106KA12L`.
- Quantity: 3 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_1210_3225Metric`; package acceptance is separate from assignment.
- Function / population: PMID ceramic.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/en/details/grm32er71h106ka12l/mlcc-smd-capacitors/murata/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `X7R`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C13, C16 — 10u 50V

- Manufacturer / exact recorded MPN: Murata / `GRM32ER71H106KA12L`.
- Quantity: 2 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_1210_3225Metric`; package acceptance is separate from assignment.
- Function / population: VBUS ceramic.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/en/details/grm32er71h106ka12l/mlcc-smd-capacitors/murata/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `X7R`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C20, C22 — 47u DNP

- Manufacturer / exact recorded MPN: Panasonic / `20TQC47MYF`.
- Quantity: 2 footprints, **0 fitted (DNP)**.
- Package / footprint: `easyeda2kicad:CASE-D_7343`; package acceptance is separate from assignment.
- Function / population: PMID backup bulk DNP.
- DNP: 20V rating below 21V adapter envelope; do not fit.
- Recorded source: [existing Source](https://www.tme.eu/cz/en/details/20tqc47myf/smd-polymer-capacitors/panasonic/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: ` ` / `20V`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **REPLACE**; owner approval and hardware qualification are not implied.

### C24, C25 — 47u DNP

- Manufacturer / exact recorded MPN: Panasonic / `EEEFK1E470P`.
- Quantity: 2 footprints, **0 fitted (DNP)**.
- Package / footprint: `Capacitor_SMD:C_Elec_6.3x5.8`; package acceptance is separate from assignment.
- Function / population: PMID backup bulk DNP.
- DNP: Backup bulk deferred; 25V part not approved for 21V input; do not fit.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/eeefk1e470p/elektrolyticke-kondenzatory-smd/panasonic/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / ` low ESR; SMD; 47uF; 25VDC`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **REPLACE**; owner approval and hardware qualification are not implied.

### C26 — 2.2u 100V X7R

- Manufacturer / exact recorded MPN: KEMET / `C1210C225K1RACTU`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_1210_3225Metric`; package acceptance is separate from assignment.
- Function / population: VIN hot-plug damping; fitted all initial VSYS variants.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.lcsc.com/product-detail/C2168116.html).
- Recorded LCSC field: C2168116.
- Historical Bought / Parameters: `` / `1210 2.2uF 100V X7R 10%; Ceff sensitivity 1.226uF, not guaranteed Cmin; reflow assembly`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C27 — 4.7u 10V USB LDO IN

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: USB VBUS decoupling.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C28 — 100n 10V USB VBUS

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: USB VBUS decoupling.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C29 — 1u RESET RC (PROVISIONAL)

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: ESP32 EN reset RC.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C30 — 10u MCU3V3 BULK (PROVISIONAL)

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: ESP32 MCU3V3 bulk decoupling.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C31 — 100n MCU3V3 HF (PROVISIONAL)

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: ESP32 MCU3V3 HF decoupling.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C32 — 2.2u NORMAL IN

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 decoupling/passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Prototype value candidate; exact MPN/supplier and temperature/bias validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C33 — 22u/35V NORMAL OUT

- Manufacturer / exact recorded MPN: TDK / `C3216X5R1V226M160AC`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_1206_3216Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 decoupling/passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/gb/details/c3216x5r1v226mac/mlcc-smd-capacitors/tdk/c3216x5r1v226m160ac/).
- Recorded LCSC field: C69612.
- Historical Bought / Parameters: `` / `Normal-output tolerance budget: 2x22uF pair; 25uF Ceff design basis; X5R -55..85C; qualify ripple; no value/net change`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C35 — 22u USB OUT

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 decoupling/passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Prototype value candidate; exact MPN/supplier and temperature/bias validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C36 — 22u MCU3V3 BULK

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 decoupling/passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Prototype value candidate; exact MPN/supplier and temperature/bias validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C37 — 100n NORMAL BOOST

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C39 — 33n NORMAL SS

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C40 — 100n USB LDO OUT

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C43 — 100n NORMAL VIN

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C45 — 22u/35V NORMAL OUT

- Manufacturer / exact recorded MPN: TDK / `C3216X5R1V226M160AC`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_1206_3216Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/gb/details/c3216x5r1v226mac/mlcc-smd-capacitors/tdk/c3216x5r1v226m160ac/).
- Recorded LCSC field: C69612.
- Historical Bought / Parameters: `` / `Normal-output tolerance budget: 2x22uF pair; 25uF Ceff design basis; X5R -55..85C; qualify ripple; no value/net change`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C47 — 100n MCU TCA VCCB

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C48 — 100n MAIN TCA VCCA

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C60, C61 — 10u/50V

- Manufacturer / exact recorded MPN: Murata / `GRM32ER71H106KA12L`.
- Quantity: 2 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_1210_3225Metric`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: C77102.
- Historical Bought / Parameters: `` / `10uF/50V X7R 10%; 1210; Ceff must meet input budget at18V`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C62, C66, C67, C68, C69 — 100n/50V

- Manufacturer / exact recorded MPN: Murata / `GRM188R71H104KA93D`.
- Quantity: 5 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0603_1608Metric`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `100nF/50V X7R 10%; 0603`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C63 — 33n/50V

- Manufacturer / exact recorded MPN: Murata / `GRM188R71H333KA61D`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0603_1608Metric`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `33nF/50V X7R 10%; 0603`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C64, C65 — 22u/35V

- Manufacturer / exact recorded MPN: TDK / `C3216X5R1V226M160AC`.
- Quantity: 2 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_1206_3216Metric`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/gb/details/c3216x5r1v226mac/mlcc-smd-capacitors/tdk/c3216x5r1v226m160ac/).
- Recorded LCSC field: C69612.
- Historical Bought / Parameters: `` / `TI TPS62933 reference-design pair; 25uF effective at5V reference basis; X5R -55..85C`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### D1 — 12V

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Diode_SMD:D_SOD-123`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/en/details/bzt52c12-tp/smd-zener-diodes/micro-commercial-components/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `?? nemám je doma?` / `0.5W`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### D2 — LED

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `LED_SMD:LED_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/597-3605-607f/diody-led-smd-barevne/dialight/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### D3, D4 — BAS116H

- Manufacturer / exact recorded MPN: Nexperia / `BAS116H,115`.
- Quantity: 2 per assembled power stage; confirm variant below.
- Package / footprint: `Diode_SMD:D_SOD-123F`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/en/details/bas116h.115/smd-universal-diodes/nexperia/bas116h-115/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### F1 — 0451005.MRL 5A

- Manufacturer / exact recorded MPN: Littelfuse / `0451005.MRL`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `ups_v4:Littelfuse_451_2410`; package acceptance is separate from assignment.
- Function / population: All V4 profiles.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/en/details/0451005.mrl/smd-fuses-2410-ultra-fast/littelfuse/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `2410 SMD; 12.5 mOhm nominal cold; 5.566 A2s nominal melting integral; 25% continuous derating`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### H1, H2, H3, H4 — MountingHole

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 4 per assembled power stage; confirm variant below.
- Package / footprint: `MountingHole:MountingHole_3.2mm_M3`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `onboard` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### IC1 — BQ25798RQMR

- Manufacturer / exact recorded MPN: Texas Instruments / `BQ25798RQMR`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_DFN_QFN:Texas_RQM0029A_VQFN-29_4x4mm_P0.4mm`; package acceptance is separate from assignment.
- Function / population: S792/S798 x 2S/4S.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.ti.com/lit/ds/symlink/bq25798.pdf).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `bought @TI` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### J1 — ADAPTER 4.75-21V

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal`; package acceptance is separate from assignment.
- Function / population: All V4 profiles.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `at home` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### J2 — VSYS OUTPUT

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal`; package acceptance is separate from assignment.
- Function / population: All V4 profiles.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `at home` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### J3 — BATTERY 2S/4S

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal`; package acceptance is separate from assignment.
- Function / population: Qualified balanced protected pack.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `at home` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### J4 — MCU / BIAS INTERFACE

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Connector_JST:JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical`; package acceptance is separate from assignment.
- Function / population: Future MCU and normal 3V3 domain.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### J6 — NTC temp sensor

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/nrbe104f3380b1f/merici-termistory-ntc-tht/eaton-electronics/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `at home` / `socket/header only`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### J7 — USB-C PROGRAM / NATIVE USB

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`; package acceptance is separate from assignment.
- Function / population: USB programming/recovery.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Exact connector MPN/footprint pending verification.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### J8 — 5V / GND

- Manufacturer / exact recorded MPN: Phoenix Contact / `1757242`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `MSTBA 2,5/2-G-5,08;12A rated;1=5V2=PGND; mating1757019 candidate verify harness beforefreeze`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### L1 — 2.2uH

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Inductor_SMD:L_12x12mm_H6mm`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/dr125-2r2-r/tlumivky/eaton-electronics/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `>7.06A I_sat`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### L2 — 4.7uH XAL5030 NORMAL

- Manufacturer / exact recorded MPN: Coilcraft / `XAL5030-472MEC`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Inductor_SMD:L_Coilcraft_XAL5030-XXX`; package acceptance is separate from assignment.
- Function / population: Normal buck Coilcraft XAL5030 prototype candidate.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Coilcraft XAL50xx datasheet https://www.coilcraft.com/getmedia/49bc46c8-4b2c-45b9-9b6c-2eaa235ea698/xal50xx.pdf; verified 2026-10-10.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `4.7uH +/-20%; DCR max 40mOhm; Isat 4.3A at 20% drop; Irms 5.9A at 40C rise; 3A load + ~0.51A ripple peak estimate at 21V/500kHz; thermal/current qualification OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### L3 — 6.8uH

- Manufacturer / exact recorded MPN: Coilcraft / `XAL5050-682MEC`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Inductor_SMD:L_Coilcraft_XAL5050-XXX`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `6.8uH +/-20%; DCR max29.45mohm; Isat6A; Irms4.7A at20C rise`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### NT1, NT2 — ~

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 2 per assembled power stage; confirm variant below.
- Package / footprint: `NetTie:NetTie-2_SMD_Pad0.5mm`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `onboard` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### NT4 — ~

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `NetTie:NetTie-2_SMD_Pad0.5mm`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### Q1, Q2 — AON7528

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 2 per assembled power stage; confirm variant below.
- Package / footprint: `easyeda2kicad:DFN-8_L3.3-W3.3-P0.65-BL-3`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/aon7528/tranzistory-s-kanalem-n-smd/alpha-omega-semiconductor/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### Q3 — PMV16UN

- Manufacturer / exact recorded MPN: Nexperia / `PMV16UN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-23`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.nexperia.com/product/PMV16UN).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### Q4 — BC847 INT DOMAIN ISOLATOR

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-23`; package acceptance is separate from assignment.
- Function / population: Main-to-MCU INT one-way boundary.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Infineon BC847 series datasheet; exact orderable suffix OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `BC847 NPN; main ~INT pullup drives base; collector MCU_INT pullup; inverted firmware polarity; power-off injection requires hardware validation`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### Q5 — BC857 MAIN-GATED CHG SOURCE

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-23`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### Q6 — BC847 MAIN_VALID SINK

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-23`; package acceptance is separate from assignment.
- Function / population: MAIN_VALID gate in series with firmware authorization; external CHG_REQ path DNP.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### Q7 — BC847 MCU CHG ARM SINK

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-23`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### Q8 — PMV16UN MAIN_VALID

- Manufacturer / exact recorded MPN: Nexperia / `PMV16UN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-23`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://assets.nexperia.com/documents/data-sheet/PMV16UN.pdf; Sections 5-8).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `20V VDS; +/-8V VGS; MAIN_VALID gate; MCU3V3 pullup NEN; TCA_EN isolation; gate-charge and leakage qualification OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### Q9 — PMV16UN TCA_EN

- Manufacturer / exact recorded MPN: Nexperia / `PMV16UN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-23`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://assets.nexperia.com/documents/data-sheet/PMV16UN.pdf; Sections 5-8).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `20V VDS; +/-8V VGS; NEN gate; MCU3V3 pullup TCA_EN; gate-charge and leakage qualification OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### Q10 — AON7528

- Manufacturer / exact recorded MPN: Alpha & Omega Semiconductor / `AON7528`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `easyeda2kicad:DFN-8_L3.3-W3.3-P0.65-BL-3`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/aon7528/tranzistory-s-kanalem-n-smd/alpha-omega-semiconductor/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R1 — 270R

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: ` ` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R4 — 100R

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: ` ` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R5 — 27k 1%

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: ` ` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R6 — 5k6

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: ` ` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R7 — 33k

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: ` ` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R8 — 2k2

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: ` ` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R9 — 10k

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/en/details/rt0805brd0710k/smd-resistors/yageo/rt0805brd0710kl/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `doplnění zásob`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R10 — 10k

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R11 — 4k7 SERVICE CHG_REQ SENSE DNP

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Service-only CHG_REQ sense; DNP; does not enable charge.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `External CHG_REQ retained at J4 for service observation only; no charger drive`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R12 — 2R 5% pulse

- Manufacturer / exact recorded MPN: Vishay / `CRCW12062R00JNEAHP`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_1206_3216Metric`; package acceptance is separate from assignment.
- Function / population: VIN hot-plug damping; fitted all initial VSYS variants.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.digikey.cz/en/products/detail/vishay-dale/CRCW12062R00JNEAHP/2826105).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `1206 0.75W 5% +/-200ppm/K; preliminary pulse screen phase2-5; prototype validation required`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R13, R14 — 5k1 1%

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 2 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: USB-C CC pulldown.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R15 — 10k 1% BOOT

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: ESP32-C3 strap/reset bias.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R16 — 10k 1% EN

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: ESP32-C3 strap/reset bias.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R17 — 10k 1% GPIO2

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: ESP32-C3 strap/reset bias.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R18 — 10k 1% GPIO8

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: ESP32-C3 strap/reset bias.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R19 — 4k7 MCU I2C SCL PU

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 control/pull-up passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Prototype value candidate; exact MPN/supplier and temperature/bias validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R20 — 4k7 MCU I2C SDA PU

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 control/pull-up passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Prototype value candidate; exact MPN/supplier and temperature/bias validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R21 — 4k7 MAIN I2C SCL PU

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 control/pull-up passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Prototype value candidate; exact MPN/supplier and temperature/bias validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R22 — 4k7 MAIN I2C SDA PU

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 control/pull-up passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Prototype value candidate; exact MPN/supplier and temperature/bias validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R23 — 8k2 1% MAIN_VALID DIVIDER TOP

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 MAIN_VALID control/pull-up passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `8k2 1% MAIN-referenced TPS2116 PR1 divider top; priority threshold qualification OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R24 — 4k7 1% MAIN_VALID DIVIDER BOTTOM

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R25 — 100k MUX ST PU

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 control/pull-up passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Prototype value candidate; exact MPN/supplier and temperature/bias validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R28 — 10k MAIN INT PU

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 control/pull-up passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Prototype value candidate; exact MPN/supplier and temperature/bias validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R29 — 10k INT BASE

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 control/pull-up passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Prototype value candidate; exact MPN/supplier and temperature/bias validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R30 — 100k INT BASE PD

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 control/pull-up passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Prototype value candidate; exact MPN/supplier and temperature/bias validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R31 — 4k7 MCU INT PU

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 control/pull-up passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Prototype value candidate; exact MPN/supplier and temperature/bias validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R32 — 31k6 0.1% 10ppm NORMAL FB

- Manufacturer / exact recorded MPN: TE Connectivity / `RN73C1E31K6BTD`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `0.1% 10ppm/K 0402 candidate; procurement open; owner authorized31.6k;3.328V nominal`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R33 — 10k 0.1% NORMAL FB

- Manufacturer / exact recorded MPN: TE Connectivity / `RN73C1E10KBTD`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `10k 0.1% 10ppm/K maximum; procurement open; value and footprint retained`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R35 — 10k USB3V3 BLEED

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: USB service regulator support.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `10k USB3V3-to-PGND bleeder; approx 0.33mA at 3.3V; bounds unplug/backfeed output charge; prototype validation`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R36 — 100k NORMAL EN

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R37 — 38k3 NORMAL EN

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R44 — 100k CHG BASE PU

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R46 — 4k7 MCU CHG BASE

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R47 — 100k MCU CHG BASE PD

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R48 — 0R USB_DP SERIES (22R OPTION)

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: USB native data series; fit 0R default, 22R optional.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R49 — 0R USB_DN SERIES (22R OPTION)

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: USB native data series; fit 0R default, 22R optional.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R50 — 100k MAIN_VALID TO Q6 BASE

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: MAIN-domain isolation bias resistor.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `100k MAIN_3V3 to Q6 base; direct main-domain bias; exact loading qualification OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R51 — 100k NEN PU

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: TCA9517 EN isolation control.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `100k MCU3V3 pull-up for NEN; MOSFET gate leakage and EN timing qualification OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R52 — 100k TCA_EN PU

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: TCA9517 EN isolation control.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `100k MCU3V3 pull-up for TCA_EN; MOSFET gate leakage and EN timing qualification OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R53 — 10k Q5 BASE LIMIT

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Main-domain charger CE base limiter.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `10k Q5 base current limiter; forced-beta and CE sink current qualification OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R60 — 53k 0.1%

- Manufacturer / exact recorded MPN: OPEN / `OPEN: 53.0k 0.1% 25ppm/K`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0603_1608Metric`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R61 — 10k 0.1%

- Manufacturer / exact recorded MPN: OPEN / `OPEN: 10.0k 0.1% 25ppm/K`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0603_1608Metric`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R62 — 100k 1%

- Manufacturer / exact recorded MPN: OPEN / `OPEN: 100k 1% 100ppm/K`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0603_1608Metric`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### R63 — 38k3 1%

- Manufacturer / exact recorded MPN: OPEN / `OPEN: 38.3k 1% 100ppm/K`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0603_1608Metric`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### SW1 — BOOT / DOWNLOAD

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Button_Switch_SMD:SW_SPST_EVQP0`; package acceptance is separate from assignment.
- Function / population: Manual recovery control.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### SW2 — RESET

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Button_Switch_SMD:SW_SPST_EVQP0`; package acceptance is separate from assignment.
- Function / population: Manual recovery control.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### TP1 — GND

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TestPoint:TestPoint_Loop_D1.80mm_Drill1.0mm_Beaded`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `at home` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### TP3 — PGND

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TestPoint:TestPoint_Loop_D1.80mm_Drill1.0mm_Beaded`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `at home` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### TP4 — SYS

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TestPoint:TestPoint_Loop_D1.80mm_Drill1.0mm_Beaded`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `at home` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### TP5 — ESP_TX (GPIO21)

- Manufacturer / exact recorded MPN: PCB / `ETCHED_PAD_D1.5MM`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TestPoint:TestPoint_Pad_D1.5mm`; package acceptance is separate from assignment.
- Function / population: Common copper only; no fitted item.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Pogo fixture must be high-Z while MCU unpowered`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### TP6 — ESP_RX (GPIO20)

- Manufacturer / exact recorded MPN: PCB / `ETCHED_PAD_D1.5MM`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TestPoint:TestPoint_Pad_D1.5mm`; package acceptance is separate from assignment.
- Function / population: Common copper only; no fitted item.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Pogo fixture must be high-Z while MCU unpowered`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### TP7 — PGND

- Manufacturer / exact recorded MPN: PCB / `ETCHED_PAD_D1.5MM`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TestPoint:TestPoint_Pad_D1.5mm`; package acceptance is separate from assignment.
- Function / population: Common copper only; no fitted item.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Optional emergency UART GND; no fitted header`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### TP8 — MCU3V3

- Manufacturer / exact recorded MPN: PCB / `ETCHED_PAD_D1.5MM`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TestPoint:TestPoint_Pad_D1.5mm`; package acceptance is separate from assignment.
- Function / population: Common copper only; no fitted item.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Sense only; NOT power input`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### TP13 — MAIN_3V3

- Manufacturer / exact recorded MPN: PCB / `ETCHED_PAD_D1.5MM`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TestPoint:TestPoint_Pad_D1.5mm`; package acceptance is separate from assignment.
- Function / population: Common copper only; no fitted item.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Voltage measurement only; not UART group or external power input`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### TP14 — CE_N

- Manufacturer / exact recorded MPN: PCB / `ETCHED_PAD_D1.5MM`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TestPoint:TestPoint_Pad_D1.5mm`; package acceptance is separate from assignment.
- Function / population: Common copper only; no fitted item.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Passive CE_N bring-up measurement in charger domain only`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### TP15 — VIN1

- Manufacturer / exact recorded MPN: PCB / `ETCHED_PAD_D1.5MM`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TestPoint:TestPoint_Pad_D1.5mm`; package acceptance is separate from assignment.
- Function / population: Common copper only; no fitted item.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Pogo fixture must be high-Z while MCU unpowered`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### TP16 — BATTERY

- Manufacturer / exact recorded MPN: PCB / `ETCHED_PAD_D1.5MM`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TestPoint:TestPoint_Pad_D1.5mm`; package acceptance is separate from assignment.
- Function / population: Common copper only; no fitted item.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Pogo fixture must be high-Z while MCU unpowered`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### TP17 — F5_5V_OUT

- Manufacturer / exact recorded MPN: PCB / `ETCHED_PAD_D1.5MM`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `TestPoint:TestPoint_Pad_D1.5mm`; package acceptance is separate from assignment.
- Function / population: F5 copper only; unused F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `Pogo fixture must be high-Z while MCU unpowered`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### U1 — ESP32-C3-MINI-1-N4X

- Manufacturer / exact recorded MPN: Espressif / `ESP32-C3-MINI-1-N4X`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `ups_v4:ESP32-C3-MINI-1-N4X`; package acceptance is separate from assignment.
- Function / population: MCU / USB common.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `GPIO0/pad12 is MCU_CHG_ARM; GPIO7/pad21 is MCU_GPIO7; firmware leaves CHG_ARM input/low until charger configured; native USB/ROM recovery keeps charge gate off`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### U2 — TPD2EUSB30A (PROVISIONAL)

- Manufacturer / exact recorded MPN: Texas Instruments / `TPD2EUSB30ADRTRG4`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:Texas_DRT-3`; package acceptance is separate from assignment.
- Function / population: USB data-line ESD protection.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### U3 — TPS62933DRLR NORMAL 3V3

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-583-8`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### U4 — AP7361C-33E-13 USB 3V3 LDO

- Manufacturer / exact recorded MPN: Diodes Incorporated / `AP7361C-33E-13`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-223-3_TabPin2`; package acceptance is separate from assignment.
- Function / population: USB service regulator.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `1A fixed 3.3V LDO; VIN 2.2-6V; input >=1uF; output >=2.2uF; USB service-only; verify thermal/current on prototype`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### U5 — TPS2116DRL NORMAL PRIORITY

- Manufacturer / exact recorded MPN: Texas Instruments / `TPS2116DRLR`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-583-8`; package acceptance is separate from assignment.
- Function / population: Normal-priority MCU3V3 source mux.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.ti.com/lit/ds/symlink/tps2116.pdf; Rev.A May 2021; §§6.5,7.3.4,7.4,7.6.1).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `VIN1 MAIN_3V3 normal priority; VIN2 USB3V3 service; MODE=MAIN_3V3; PR1=8k2/4k7 MAIN_3V3 divider; 1.6-5.5V; 2.5A; switchover and leakage qualification OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### U6 — TCA9517DGKR REV.D

- Manufacturer / exact recorded MPN: Texas Instruments / `TCA9517DGKR`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_SO:VSSOP-8_3x3mm_P0.65mm`; package acceptance is separate from assignment.
- Function / population: MCU/main I2C domain buffer.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.ti.com/lit/gpn/tca9517; Rev.D; Sections 3,5,7.5,9).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `VCCA MAIN_3V3; VCCB MCU3V3; EN TCA_EN, MCU-powered isolated control; original Rev.D no VCCA<=VCCB restriction; 400kHz; A-side BQ low-level margin, B-side ESP VOL margin; R07 OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### U7 — TPS62933DRLR

- Manufacturer / exact recorded MPN: Texas Instruments / `TPS62933DRLR`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-583-8`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: C3200405.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### U8 — LM74700QDBVRQ1

- Manufacturer / exact recorded MPN: Texas Instruments / `LM74700QDBVRQ1`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-23-6`; package acceptance is separate from assignment.
- Function / population: F5 only; DNP in F0.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: C2941042.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

