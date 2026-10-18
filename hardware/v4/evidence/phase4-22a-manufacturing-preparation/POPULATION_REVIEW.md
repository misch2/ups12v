# F0/F5 population and sourcing projections — REVIEW ONLY

2026-10-18. One accepted PCB; owner plans bare-board purchase and self-assembly of **both F0 and F5**. These lists do not change or freeze the authoritative BOM. Charger/cell profile selection remains separate: current exported IC1 is BQ25798RQMR; S792/S798 ×2S/4S options need their own exact assembly/firmware record. No profile is selected by choosing F0/F5.

| Projection | Fitted component instances | DNP references | PCB features, zero fitted quantity |
|---|---:|---:|---:|
| [F0 review CSV](F0-population-review.csv) | 115 | 23 | 16 |
| [F5 review CSV](F5-population-review.csv) | 134 | 4 | 16 |

Each CSV has **154 individual reference rows**, explicit state/quantity, value/function, known manufacturer/MPN, footprint, recorded ratings/limitations and sourcing status. This avoids ambiguous grouped quantities. [Detailed JSON](population-detail.json) preserves raw accepted fields; [summary JSON](population-summary.json) enumerates every fitted/DNP/feature reference. Sources: Phase4.21 accepted export, unchanged authoritative BOM, unchanged-schematic Phase4.19 population proof. Historical inventory fields are not current possession, procurement approval or live stock evidence.

**Exact F5-only group, 19 references:** U7, U8, Q10, L3, R60, R61, R62, R63, C60, C61, C62, C63, C64, C65, C66, C67, C68, C69, J8. F0 fits zero of these; F5 projects one of each. F0 omits J8 harness and leaves TP17 unfed. All other fitted references are common.

**Always DNP:** C20, C22, C24, C25. No paste/part fitting in either assembly. Historical 20/25 V backup-bulk candidates are not approved for the retained adapter envelope. Their copper/mask openings remain physically present; DNP does not seal a nearby via.

**PCB features:** H1–H4, NT1/NT2/NT4, TP5–TP8 and TP13–TP17 require no purchased PCB component. TP1/TP3/TP4 are the existing loop-testpoint population candidates and count as fitted parts; do not confuse them with the nine bare pads. Removed old supervisor references are not reintroduced.

## Unresolved choices that can affect footprints

| Item | Decision scope before bare-board freeze |
|---|---|
| SW1/SW2 | Exact switch MPN remains OPEN against `Button_Switch_SMD:SW_SPST_EVQP0`; establish actual compatible mechanical/land identity. A different switch can force a footprint change |
| L1 | Current 2.2 µH, `L_12x12mm_H6mm`, recorded >7.06 A Isat; historical Eaton DR125-2R2-R source link is a **candidate**, not a frozen selected MPN. Verify the exact saturation/DCR/thermal/land candidate or consciously retain the prototype footprint before ordering |
| U2 | TPD2EUSB30ADRTRG4 / Texas_DRT-3 is provisional; confirm that exact candidate/pin map or obtain owner review of any substitute. A sourcing delay for the same part is not a copper defect |
| Open biased MLCCs and power passives | In particular C32/C35 and charger/output support: establish voltage, effective capacitance, tolerance, power and package suitability. A same-footprint conforming identity is ordinary sourcing; needing a larger package is a footprint decision. No need to assume all open passives force redesign |
| Any proposed replacement for L2/L3/U1/IC1/U8 or connectors | Existing exact package is the projection basis. Sourcing alternatives are not interchangeable without verification. L2/L3 thermal qualification remains separate from supply availability |

Nano-Fit RevJ1 tolerance risk and Q1/Q2/Q10 2.45×2.00 mm exposed land versus AOS 2.45×2.28 mm are **OWNER ACCEPTED FOR PROTOTYPE USE, 2026-10-18**. These inherited deviations are not new defects and not claims of manufacturer conformity. The new [via/pad assembly screen](VIA_PAD_ASSEMBLY.md) is a separate process concern; smaller-land acceptance does not imply filled/capped vias.

## Ordinary sourcing / assembly gaps

- U8 LM74700QDBVRQ1: retained Phase4.19 2026-10-18 LCSC C2941042 observation is out of stock. This is an F5 assembly blocker at that supplier, not a bare-board defect. U3/U7 and J7 had in-stock observations in that same retained snapshot. No stock/price refresh was performed in this phase.
- L3 XAL5050-682MEC: preferred TME/LCSC basket unestablished; retained exact secondary-source candidate exists. No substitution or order made.
- R60/R61: exact 53 kΩ/10 kΩ, 0.1%, 25 ppm/K-class order MPNs OPEN; R62/R63: 100 kΩ/38.3 kΩ, 1%, exact MPNs OPEN. R32/R33 TE candidates retain their documented procurement limits. Ordinary same-package identities can be resolved without CAD changes.
- Common transistors/passives/loop testpoints and other `OPEN` rows need exact MPN/ratings and practical supplier quantities. TME/LCSC preferred; retain existing source identities, then compare actual combined small-order shipping/MOQ before purchase. Current prices/MOQs/stock are explicitly unverified unless a dated retained observation is named.
- Nano-Fit housings/1053002100 tin contacts, JST mates/contacts, wire/crimp tools, pack/BMS/NTC and assembly materials form a separate harness/assembly basket. No inferred purchases from `Bought` fields.

The CSV rating column carries recorded values, voltage/dielectric/tolerance/current/DCR where established; omitted ratings remain OPEN. IC capabilities are not board limits. Small targeted primary-source rating checks on 2026-10-18: [TI BQ25798](https://www.ti.com/product/BQ25798) 3.6–24 V input, 30 V absolute maximum, 1–4 cells/5 A charger; [TI TPS62933](https://www.ti.com/product/TPS62933) 3.8–30 V/3 A converter; [TI exact LM74700QDBVRQ1](https://www.ti.com/product/LM74700-Q1/part-details/LM74700QDBVRQ1) 3.2–65 V controller. These checks make no changes to the approved source/load/cell envelope.
