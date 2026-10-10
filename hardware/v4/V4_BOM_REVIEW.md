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
| U3/U4 normal and USB 3V3 bucks, qty 2 | Texas Instruments TPS62933DRLR, SOT-583-8; 3 A class. U3 input `SYS`, U4 input `USB_VBUS`; 31.6 kOhm/10 kOhm **0.1%** FB candidates target about 3.33 V. | **PROPOSED** from [TI TPS62933 datasheet Rev. D (Aug 2022)](https://www.ti.com/lit/ds/symlink/tps62933.pdf), Sections 5-8 and 10.2. The 3.8-30 V input and 3 A rating address the prior 0.5 A/USB headroom issue. Exact TME/LCSC identity, stock and price OPEN; 4.7 uH, 2.2 uF + 100 nF input and 2 x 22 uF output are candidates pending ripple/Ceff/thermal validation. Bootstrap parts are now 25 V candidates to satisfy the 16 V minimum guidance. |
| U5 normal-priority mux, qty 1 | Texas Instruments TPS2116DRL, SOT-583-8; `MODE=MAIN_3V3`, digital `PR1`/`MUX_PR1` MAIN_VALID node with R23 10 kOhm pull-up and U7 override, output `MCU3V3`. | **PROPOSED** from [TI TPS2116 datasheet Rev. A (May 2021)](https://www.ti.com/lit/ds/symlink/tps2116.pdf), Sections 5-8. VREF 0.92-1.08 V, reverse-current blocking and 2 us response are recorded in the phase evidence. U7 absolute MAIN threshold removes the former bare-divider tolerance gap; reset-free source insertion/removal remains an electrical qualification gate. |
| U6 I2C domain buffer, qty 1 | Texas Instruments TCA9517DGKR, original Rev.D, VSSOP-8; VCCA/A=`MAIN_3V3`, VCCB/B=`MCU3V3`; 4.7 kOhm pull-ups on both sides. Q8/Q9 PMV16UN plus R51/R52 isolate EN. | **PROPOSED** from [TI TCA9517 original data sheet](https://www.ti.com/lit/gpn/tca9517), Rev.D, Sections 3, 5, 7.5 and 9. The original revision has no later VCCA <= VCCB restriction; powered-off high-Z behavior is used for USB-only operation. EN is forced low when MAIN_VALID is absent, preventing MCU-side EN pull-up back-bias into MAIN. R07 aggregate partial-power leakage remains OPEN. |
| U7 normal-rail supervisor, qty 1 | Texas Instruments TPS389033DSET, WSON-6; fixed 3.17 V falling / 3.189 V rising threshold, open-drain RESET, 10 nF CT delay candidate. | **PROPOSED** from [TI TPS3890 data sheet Rev.A](https://www.ti.com/lit/ds/symlink/tps3890.pdf), Sections 5-8 and orderable table. `MAIN_3V3` powers VDD/MR and is also sensed; RESET releases the MUX_PR1 normal-valid node only after the normal domain is valid, avoiding normal-only startup deadlock. Exact preferred-supplier identity/stock and propagation/hold-up qualification OPEN. |
| Q5/Q6/Q7 charger-domain gate, qty 3 | BC857 PNP plus two BC847 NPNs, SOT-23; Q5 emitter is `MAIN_3V3`, Q6 is the `MUX_PR1`/MAIN_VALID sink and Q7 is firmware `MCU_CHG_ARM` sink in series through `CHG_AND`. | **PROPOSED** using existing Infineon/Nexperia candidate research; exact suffix and preferred-supplier orderability OPEN. R11.2 is DNP service sense, so external `CHG_REQ` cannot enable charge; normal validity and firmware authorization are both required. |
| R50 MAIN_VALID authorization, qty 1 | 100 kOhm candidate, `Resistor_SMD:R_0402_1005Metric`, from supervisor-released `MUX_PR1` to Q6 base. | **PROPOSED** ordinary passive; exact MPN/supplier and base-loading qualification OPEN. |
| Q8/Q9 EN isolation, qty 2 | Nexperia PMV16UN, SOT-23; Q8 gate=`MAIN_VALID`, Q8 drain=`NEN`, Q9 gate=`NEN`, Q9 drain=`TCA_EN`; sources PGND. | **PROPOSED**. Gate leakage, charge, EN timing and the powered-off aggregate R07 limit remain OPEN; the fail-low truth table is documented in the checkpoint evidence. |
| R51/R52 EN pull-ups, qty 2 | 100 kOhm, `Resistor_SMD:R_0402_1005Metric`; MCU3V3 pull-ups for `NEN` and `TCA_EN`. | **PROPOSED** ordinary passives; exact MPN/supplier and EN timing qualification OPEN. |
| R53 Q5 base-current limiter, qty 1 | 10 kOhm, `Resistor_SMD:R_0402_1005Metric`; between `CHG_BASE` and `Q5_BASE_LIMITED`. | **PROPOSED** ordinary passive; limits the main-domain Q5 base path, while forced-beta/CE sink qualification remains OPEN. |
| C49 MCU3V3 hold-up fit candidate, qty 1; default populated | 470 uF, 6.3 V polarized candidate, `Capacitor_SMD:C_Elec_8x10.2`, across `MCU3V3`/`PGND`; schematic DNP=`NO`. | **PROPOSED / FIT CANDIDATE** for source-removal testing. ESR, effective capacitance, inrush through both buck soft-starts and package/lifecycle suitability remain OPEN; no reset-free claim is made until measured. |
| L2/L3 and C32-C48 regulator/support passives | 4.7 uH inductors, 2.2 uF + 100 nF input, 2 x 22 uF output per buck, 100 nF 25 V bootstrap, 33 nF soft-start, 100 nF TCA9517 supply bypasses and 0402 divider resistors; exact MPNs intentionally OPEN. | **PROPOSED**. Inductor candidates use an Isat >=4.0 A and Irms >=3 A envelope; the two 22 uF output candidates target the TPS62933 40 uF typical 3.3 V recommendation before DC-bias derating. Keep package, voltage, Ceff, ripple-current, USB inrush and thermal checks in the prototype review; ordinary passive sourcing is intentionally not purchase-ready at this milestone. |

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
| C27 USB VBUS bulk, qty 1 | 10 uF 6.3 V candidate, `Capacitor_SMD:C_0805_2012Metric`; exact MPN OPEN. | **PROPOSED**; USB VBUS tolerance/inrush/ESD and source capability remain unqualified. |
| C28 USB VBUS bypass, qty 1 | 100 nF 10 V candidate, `Capacitor_SMD:C_0402_1005Metric`; exact MPN OPEN. | **PROPOSED**; exact MPN and supplier evidence OPEN. |
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

<!-- EXPORTED CAD INVENTORY -->

Inventory source: `phase3-2-mcu-power.net.xml`.

Quantities below count schematic instances per PCB. DNP groups have zero fitted quantity in initial VSYS assemblies.

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

### C27 — 10u 6.3V USB VBUS

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

### C33 — 22u NORMAL OUT

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

### C34 — 2.2u USB IN

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

### C38 — 100n USB BOOST

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

### C40 — 33n USB SS

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

### C41 — 100n MCU UV

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

### C42 — 10n SUP CT

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

### C44 — 100n USB VIN

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

### C45 — 22u NORMAL OUT 2

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### C46 — 22u USB OUT 2

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: OPEN.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / ``.
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

### C49 — 470u MCU HOLDUP

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_Elec_8x10.2`; package acceptance is separate from assignment.
- Function / population: Source-removal hold-up fit candidate; populate pending ESR/Ceff/USB inrush qualification.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary prototype capacitor; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `470u 6.3V candidate; effective capacitance, ESR, TPS62933 soft-start and USB inrush qualification OPEN; intended fit candidate`.
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

### L2 — 4.7uH NORMAL

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Inductor_SMD:L_1210_3225Metric`; package acceptance is separate from assignment.
- Function / population: Normal buck 4.7uH inductor; exact MPN OPEN.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: TI TPS62177 Rev.C §9.3.4 / Fig.61.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `4.7uH nominal; Isat >=4.0A candidate envelope from 3A load plus ~1.02A ripple at 12V/500kHz; Irms >=3A; DCR/ripple/thermal validation OPEN`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

### L3 — 4.7uH USB

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Inductor_SMD:L_1210_3225Metric`; package acceptance is separate from assignment.
- Function / population: USB buck 4.7uH inductor; exact MPN OPEN.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: TI TPS62177 Rev.C §9.3.4 / Fig.61.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `4.7uH nominal; Isat >=4.0A candidate envelope from 3A load plus ~1.02A ripple at 12V/500kHz; Irms >=3A; DCR/ripple/thermal validation OPEN`.
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

### R23 — 10k MAIN_VALID PULLUP

- Manufacturer / exact recorded MPN: OPEN / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Resistor_SMD:R_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Phase 3.2 MAIN_VALID control/pull-up passive.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `10k 1% MAIN_3V3 pull-up for TPS389033 RESET/MUX_PR1; digital MAIN_VALID release; exact loading qualification OPEN`.
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

### R32 — 31k6 0.1% NORMAL FB

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

### R33 — 10k 0.1% NORMAL FB

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

### R34 — 31k6 0.1% USB FB

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

### R35 — 10k 0.1% USB FB

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

### R38 — 100k USB EN

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

### R39 — 38k3 USB EN

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
- Function / population: MAIN_VALID to Q6 base authorization resistor.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: Ordinary passive; supplier verification deferred to BOM freeze.
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `100k candidate; supervisor-released MUX_PR1 drives Q6 base; exact loading qualification OPEN`.
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

### U4 — TPS62933DRLR USB 3V3

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

### U5 — TPS2116DRL NORMAL PRIORITY

- Manufacturer / exact recorded MPN: Texas Instruments / `TPS2116DRLR`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_TO_SOT_SMD:SOT-583-8`; package acceptance is separate from assignment.
- Function / population: Normal-priority MCU3V3 source mux.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.ti.com/lit/ds/symlink/tps2116.pdf; Rev.A May 2021; §§6.5,7.3.4,7.4,7.6.1).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `VIN1 normal priority; VIN2 USB; 1.6-5.5V; 2.5A; PR1=10k MAIN_VALID pull-up; U7 3.17V supervisor; switchover and leakage qualification OPEN`.
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

### U7 — TPS389033DSET MAIN UV

- Manufacturer / exact recorded MPN: Texas Instruments / `TPS389033DSET`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Package_SON:WSON-6_1.5x1.5mm_P0.5mm`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.ti.com/lit/ds/symlink/tps3890.pdf; Rev.A; Sections 5-8 and orderable table).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `` / `VDD/MR MAIN_3V3; SENSE MAIN_3V3; RESET MUX_PR1; fixed 3.17V falling / 3.189V rising; 10nF CT candidate`.
- Price / currency / MOQ / current availability: **UNVERIFIED**; do not interpret historical purchase fields as current stock.
- Verification: exported inventory 2026-10-10; manufacturer/package/procurement checks and alternatives are recorded above or remain OPEN.
- Approval status: **PROPOSED**; owner approval and hardware qualification are not implied.

