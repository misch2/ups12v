# UPS V4 Phase 5.0 — sourcing proposal

2026-10-19. **65 PCBA purchasing lines;154 reference rows;28 separate harness,
assembly-material and battery-decision rows.** Counts verified: F0=115 fitted,
F5=134,19 F5-only,4 always-DNP and16 PCB-only features. The three real loop
testpoints count as fitted hardware. Accepted PCB/footprints and manufacturing
data are preserved. Owner confirms five bare boards and one0.10mm top stencil
already ordered; components are for manual assembly.

## Quick start

1. Review [open decisions](OPEN_DECISIONS.md) and [package/selection evidence](PACKAGE_AND_SELECTION_REVIEW.md).
2. Set assembly counts with `python -B hardware/v4/sourcing/build_purchasing_bom.py --n-f0 1 --n-f5 1`,
   then `python -B hardware/v4/sourcing/write_sourcing_reports.py`.
3. Review [master BOM](MASTER_PURCHASING_BOM.csv), [population](REFERENCE_POPULATION.csv),
   [supplier proposal](SUPPLIER_BASKETS.md) and [harness/assembly BOM](HARNESS_AND_ASSEMBLY_BOM.csv).
   Obtain missing exact quotes before considering an order.

## Quantity and price snapshot

Current **1F0+1F5 is provisional**, not an owner purchasing decision.
Fitted electronics quantity is `115*N_F0+134*N_F5`. For all five boards, with
`N_F0=5-N_F5`, this is `575+19*N_F5`:575,594,613,632,651,670 fitted pieces for
N_F5=0,1,2,3,4,5. Every purchasing row includes all six illustrations.

| Quantity / cost | Dated indicative result |
|---|---:|
| Known-price fitted electronics per F0, excludes unquoted parts | USD28.05 + unquoted lines |
| Known-price fitted electronics per F5, excludes unquoted parts | USD34.77 + unquoted lines |
| Provisional scenario PCBA purchase subtotal, spares/MOQ included | USD83.74 + 20 lines without usable extended quote |
| Separately priced harness connectors/contacts for scenario | USD9.17 + wire/tools/materials and other unquoted items |
| Complete electronics basket / delivered total | **Unknown; no defensible complete estimate yet** |

These are partial dated estimates, including explicitly cached page prices and
unconfirmed Coilcraft indicative prices. Historical stock is never called current;
cache age/date and availability are separate columns. Unavailable reference-only
prices are excluded. No FX rate, VAT, missing price, freight, handling or delivery
promise is invented. The supplier proposal records verified published Czech
shipping terms and the2026 LCSC EU import notice, with actual charges unresolved.

## Supplier split and critical outcome

Preferred split: **TME + LCSC**, with **DigiKey** exact mechanical/module/resistor
fallbacks and an exact **Coilcraft Europe** L2/L3 quote. The alternative is to
quote DigiKey+Coilcraft consolidation, or LCSC+DigiKey+Coilcraft when preferred
semiconductor/passive economics justify the extra shipment. Two-supplier complete
availability and minimum delivered cost are not established; Mouser/Farnell exact
fallbacks may add a shipment. No cart was made.

IC1 is verified **BQ25798RQMR**, not BQ25792. Retained exact N4X module, charger,
TPS62933 and GCT USB connector have useful sourced offers. Owner's EVQP0Q02Q,
DR125-2R2-R, TPD2EUSB30ADRTR and exact Nano-Fit choices govern older OPEN tables.
R60 now has a53.0k0.1%25ppm KOA cut-tape proposal; R61 a10k0.1%25ppm YAGEO
proposal. R62/R63 retain1%100ppm0603 requirements. No relaxed R32/R33 precision.

**Unresolved exact supply:** U8 at LCSC/DigiKey; TDK22uF35V C33/C45/C64/C65;
obsolete ordering code C70/C71; PMV16UN Q3/Q8/Q9. L2/L3 need exact manufacturer
stock/delivery quotes. TP1/TP3/TP4 lack verified exact hardware MPNs. Some ordinary
items have retained identity links but unverified price/MOQ/stock. C32/C35/C36
proposals remain conditional on retained effective-capacitance requirements.
Concrete capacitor alternatives are separate and **unapproved**, never silently
substituted into the master BOM. No accepted land deviation is reopened.

Owner decisions: final board split/spares and actual inventory; disposition of
unavailable retained parts versus reviewed alternatives; cable scope/lengths and
missing tools. Battery cells/BMS/NTC/profile are a separate, still unselected
decision. Routine missing quotes and manufacturer data are recorded as work,
not extra architecture approvals.

## Validation and STOP

Reference coverage/uniqueness, exact F0/F5 populations,19 F5-only references,
always-DNP/PCB-only exclusion, real testpoints, grouping totals, owner identities
and protected source hashes pass. [Machine-readable evidence](../evidence/phase5-0-sourcing/consistency.json).
196 protected CAD/library/manufacturing files unchanged.
No CAD mutation, new native KiCad run, manufacturing regeneration, firmware build,
purchase, cart, commit or push. ERC/DRC and firmware builds were not rerun for
documentation/CSV-only work; accepted release checks are reused.

**STOP for owner review of this procurement proposal. It is not approval to order.**
