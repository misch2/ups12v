# V4 BOM review — power-stage design inventory

Updated 2026-10-10. Preferred suppliers are TME.eu and LCSC.com under current
`AGENTS.md`; manual assembly and total small-order cost matter. This inventory
covers the power stage currently drawn, not the deferred MCU/USB/regulator BOM.
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
| C4/C10/C11/C14/C17/C19/C21 BAT/SYS, qty 7 | Inherited source points to Murata GRJ21BR61E106KE01K, 10 uF/25 V. Exact MPN is absent from current fields. | Source name indicates a different dielectric family from inherited `Parameters=X7R`; verify manufacturer data before freeze and correct metadata deliberately. Ceff over SYS/BAT envelope is OPEN. |
| C8 SDRV, qty 1 | Inherited source points to Murata GCM1555C1H102JA16D, 1 nF/50 V. | Exact identity/dielectric field reconciliation OPEN; inherited X7R text must not override manufacturer identity. |
| C20/C22/C24/C25 optional PMID bulk | Legacy Panasonic 20TQC47MYF and EEEFK1E470P. | **REPLACE if fitting**: 20/25 V ratings unsuitable for 21 V plus retained derating target. Default DNP for initial VSYS prototype; forward Ceff/transient qualification still required. No PMID backup assembly approved. |
| D3/D4 CE diode OR, qty 2 | Nexperia BAS116H,115, SOD123F. | [TME BAS116H.115](https://www.tme.eu/en/details/bas116h.115/smd-universal-diodes/nexperia/bas116h-115/) identity/pin map in part acceptance; current stock/price/MOQ UNVERIFIED. |
| Q3 CE sink, qty 1 | Nexperia PMV16UN, SOT23. | Accepted G/S/D drawing and package mapping; exact reel suffix and preferred-supplier orderable identity OPEN. Do not substitute an electrical 2N7002 based on the drawing used. |
| Q1/Q2 input FET pair, qty 2 | AOS AON7528, DFN 3.3 x 3.3. | Retained recorded TME identity; 30 V VDS and 20 V VGS absolute limits are not transient/SOA qualification. Supported cable/source hot-plug and thermal evidence pending. |
| F1 adapter fuse, qty 1 | Littelfuse 0451005.MRL (5 A), 2410, saved prototype candidate; 0451004.MRL (4 A) compared but not selected. | Comparison in `V4_PROCUREMENT_RESUME.md`. [TME 0451005.MRL](https://www.tme.eu/en/details/0451005.mrl/smd-fuses-2410-ultra-fast/littelfuse/) and [LCSC C48467 catalog image/identity](https://www.lcsc.com/product-image/C48467.html) found. Current price/MOQ/stock UNVERIFIED. Konnect-created local footprint is PROPOSED: disposable readback/render exists, but manufacturer land-pattern confirmation and temperature/cable/fault coordination remain required. |
| VIN damping branch, not yet drawn | TI Figure 8-1: series 2 Ohm / shunt 2.2 uF for hot-plug above 15 V. Exact pulse-rated resistor and capacitor MPNs OPEN. | Schematic completion blocker for the supported 20 V adapter envelope. See calculations and source in `V4_PROCUREMENT_RESUME.md`. Do not treat a schematic text note as a populated protection provision. |
| L1 energy storage, qty 1 | Eaton DR125-2R2-R, inherited 2.2 uH / 750 kHz selection. | Recorded [TME code](https://www.tme.eu/cz/details/dr125-2r2-r/tlumivky/eaton-electronics/). Manufacturer saturation/ripple/750 kHz loss and exact installed geometry remain qualification items. No current price/MOQ/stock claim. |
| R5 PROG, qty 1 | 27 kOhm for S792-4/S798-4; 8.2 kOhm for S792-2/S798-2, fixed by assembly. | Exact 1% MPNs OPEN. One physical resistor position; never populate both values or expose a cell-count jumper. |
| J1/J2/J3/J4/J6 connectors | Current footprints/headers are inherited; exact housings, keyed contacts, ratings and harness assemblies OPEN. | J6 historical thermistor URL describes the external NTC, not the connector. Specify separately before freeze. J4 is incompatible with V3 wiring; MAIN_3V3 is a normal-domain input, never USB 3V3. |
| Remaining resistors/LED/testpoints | Recorded CAD inventory below; exact orderable identities mostly OPEN. | Prefer common values/packages and existing valid sourcing. No stock, price or supplier code is invented. |

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

Inventory source: `phase2-3-review.net.xml`.

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

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 7 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0805_2012Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/grj21br61e106ke01k/kondenzatory-mlcc-smd/murata/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `X7R`.
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

- Manufacturer / exact recorded MPN: UNVERIFIED / `OPEN`.
- Quantity: 1 per assembled power stage; confirm variant below.
- Package / footprint: `Capacitor_SMD:C_0402_1005Metric`; package acceptance is separate from assignment.
- Function / population: Inherited charger support; all SYS profiles unless variant review overrides.
- DNP: No DNP reason recorded; review initial assembly BOM.
- Recorded source: [existing Source](https://www.tme.eu/cz/details/gcm1555c1h102ja16d/kondenzatory-mlcc-smd/murata/).
- Recorded LCSC field: OPEN; see verified catalog identities above.
- Historical Bought / Parameters: `basket @TME` / `X7R`.
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

### R5 — 27k 1-2%

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

### R11 — 1k

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

