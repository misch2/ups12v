# UPS V4 — final purchase and assembly checklist

20 October 2026 · Phase 5.6 · five F5 boards · owner approvals FINAL.

Quick start:

1. Purchase the exact **71 LCSC + 7 TME rows** in [LCSC order](FINAL_LCSC_ORDER.csv)
   and [TME order](FINAL_TME_ORDER.csv). All 78 approved quantities are retained.
   Give priority to **J3 housing C17689101 ×5: exactly five in stock**.
2. Confirm stock and the final delivered amounts in your own supplier sessions,
   then submit/pay yourself. The remaining commercial checks are listed below.
3. Assemble using [FINAL_ASSEMBLY_BOM.csv](FINAL_ASSEMBLY_BOM.csv). It takes
   precedence over unchanged schematic purchasing metadata for this approved
   prototype batch. **R32/R33 and R60/R61 must each be fitted as complete pairs.**

No engineering sourcing decisions remain. No order, checkout, payment, supplier
message, commit or push was performed. The manufactured PCB and all CAD,
libraries, manufacturing outputs and firmware remain unchanged.

## Purchasing files and quantities

The CSVs are UTF-8 with BOM, comma-separated, with decimal points. Import SKU/MPN
columns as **text**. `supplier_sku` and `quantity` are the first two columns;
`unit` and `direct_product_url` follow. Use these as copy/paste purchasing lists;
if using a supplier's BOM importer, map just SKU and quantity and check its
preview. A site-specific unattended import schema has not been claimed/tested.
Each SKU appears once per supplier; no total or excluded row is mixed into an order.

For [TME Quick Buy](https://www.tme.eu/cz/Profile/QuickBuy/load.html), the exact
symbol/quantity pairs are below. **H09/H10 are metres; H11 is 10 m rolls.**
The selected TME country is Czech Republic, currency CZK, prices excluding VAT.

```text
C2012X7R1H225KAC	10
FLRY-B0.50-RD/1	5
FLRY-B0.50-BK/1	5
D-118-5	2
597-3605-607F	8
BC857B.215	6
EVQP0Q02Q	11
```

Keep the approved MOQ excess, including **100 each** R5 2S/3S/4S resistor,
C39 ×100, C63 ×100, C8 ×50, R32 ×20 and R33 ×10. Order **exactly five**
BQ25798RQMR. C32 Yageo ×10, the TDK output-bank parts ×30, and additional
TDK C32 comparison stock ×10 are all included. Comparison stock adds no fitted
position. The assembly CSV repeats a shared `ordered_group_quantity` on related
references for traceability: **sum purchase quantities only in the order CSVs**.

## Confirmed public prices versus estimates

All 78 product lines have **live public stock, price and purchase-multiple
observations on 20 October**. These are confirmed displayed prices at the listed
quantities, not binding quotations, reserved stock or paid invoice amounts.
No cached USD allowance is used for the seven final TME lines.

| Supplier / item | Amount | Status |
|---|---:|---|
| LCSC, 71 rows, goods | **USD 230.6740 net** | Live displayed USD unit prices × approved quantities |
| TME, 7 rows, goods | **CZK 532.1356 net** | Live Czech/CZK prices × approved quantities |
| TME goods with 21% VAT | approx. CZK 643.88 | Calculation; supplier invoice rounding may differ |
| TME standard Czech delivery ≤20 kg | CZK 140 net / **169.40 gross** | Published standard charge; actual basket/service to confirm |
| TME goods + standard delivery + 21% VAT | **approx. CZK 813.28** | Derived budget; final rounding/service/account price at order |
| LCSC freight, VAT, duty, clearance/handling and FX | **Unknown — checkout/import dependent** | Not included in the goods subtotal |
| Existing/local labels, heatshrink, ties and external-pack interface | Unknown incremental cost | Prior deferred owner materials; not priced as zero |
| Complete delivered total | **Not yet confirmed** | Do not treat the goods subtotal as landed cost |

LCSC J1 header C564339 is now USD 0.8477 each, down from 0.9325;
five cost USD 4.2385. The remaining LCSC unit prices match Phase 5.5.
The seven TME extensions are:

| SKU | Buy | CZK net/unit | CZK net line |
|---|---:|---:|---:|
| C2012X7R1H225KAC | 10 pcs | 6.547 | 65.470 |
| FLRY-B0.50-RD/1 | 5 m | 19.66 | 98.30 |
| FLRY-B0.50-BK/1 | 5 m | 19.66 | 98.30 |
| D-118-5 | 2 ×10 m rolls | 63.77 | 127.54 |
| 597-3605-607F | 8 pcs | 8.178 | 65.424 |
| BC857B.215 | 6 pcs | 2.3196 | 13.9176 |
| EVQP0Q02Q | 11 pcs | 5.744 | 63.184 |

Approved quantities stay fixed; no new price-break purchases are required.
TME delivery is normally 1–2 working days after dispatch; payment in advance
can defer dispatch until funds are booked. Cash on delivery adds CZK 42.35
gross and is not included above. Weight/dimensions and service can change freight.
[TME Czech delivery terms](https://www.tme.eu/cz/how-to-buy/7328/zpusoby-a-ceny-dopravy/).

LCSC's [customs terms](https://www.lcsc.com/help-center/shipping-delivering/customs-duties-taxes)
state FCA freight prepaid or EXW freight collect, with destination taxes,
duties and courier charges payable by the customer. **Do not assume checkout
collects Czech VAT, IOSS or duty, or that a prepaid-tax/DDP service is offered.**
If the selected service explicitly collects taxes/duties, keep its breakdown
and avoid paying/counting the same charge twice. Otherwise allow for import
VAT, applicable duty and the carrier's clearance/disbursement fee.

[Freight](https://www.lcsc.com/help-center/shipping-delivering/shipping-cost-calculation)
depends on weight, method and destination. Available methods and Czech transit
time must be checked for the actual parcel. No free JLCPCB consolidation is
assumed for the PCB order already placed. The
[USD 3 small-order fee](https://www.lcsc.com/help-center/ordering-quotation/handling-fee)
applies below USD 15 goods; this complete basket exceeds that threshold.
Paid reeling/optional packaging, payment conversion and carrier fees still
require the owner's final order preview.

The [2026 EU notice](https://www.lcsc.com/help-center/notice/eu-low-value-import-regulations-2026)
describes €3 per qualifying category for B2C consignments ≤€150, with VAT also
due. This is not €3 per part or necessarily per CSV row. This LCSC basket exceeds
€150 whenever USD 1 > EUR 0.6503; check the actual customs conversion. Above
€150, use applicable normal tariff treatment, not an assumed small-parcel flat
fee. Do not assume duty is zero or split the basket to manufacture a tax result.
For budgeting, import VAT normally includes goods, freight and applicable duty
([EU taxable-amount guidance](https://taxation-customs.ec.europa.eu/taxation/vat/vat-directive/taxable-amount_en)).
The applicable tax collection and carrier handling remain the owner's final
commercial checks, not another component review.

## Availability and smallest remedies

| Exact item | Approved buy | Live stock | Action if unavailable at purchase |
|---|---:|---:|---|
| J3 housing 1053072202 / [C17689101](https://www.lcsc.com/product-detail/C17689101.html) | 5 | **5** | Exact stock is essential; if fewer than five, order/wait for the exact MPN at LCSC or TME. Report lead time/shortfall; do not change key or add supplier. |
| C26 C1210C225K1RACTU / C2168116 | 6 | 10 | Same exact-MPN replenishment route if exhausted |
| J3 header 1053132102 / C17189968 | 5 | 20 | Preserve natural/key-B identity |
| J8 header 1053132103 / C17412426 | 5 | 20 | Preserve natural/key-B identity |
| J2 header 1053131103 / C561764 | 5 | 109 | Preserve black/key-A identity |
| J8 housing 1053072203 / C17399592 | 6 | 183 | Keep approved spare if available |
| SW1/SW2 EVQP0Q02Q at TME | 11 | 28 | Confirm all 11; page warns minimum can change after stock depletion |
| U6 TCA9517DGKR / C544515 | 6 | 264 | Keep original non-A version |
| IC1 BQ25798RQMR / C2876593 | 5 | 2,807 | Buy exact BQ25798, not another BQ2579x |
| U1 ESP32-C3-MINI-1-H4X / C41349510 | 5 | 1,187 | Keep H4X PCB-antenna identity |
| U3/U7 TPS62933DRLR / C3200405 | 11 | 17,616 | Exact DRL package |
| U4 AP7361C-33E-13 / C500795 | 6 | 2,895 | Exact E/SOT-223 variant |
| U5 TPS2116DRLR / C3235557 | 6 | 60,893 | Exact DRL package |
| U8 LM74700QDBVTQ1 / C2653623 | 6 | 1,097 | Approved T packaging suffix retained |

All other 78-row stock/MOQ details and direct URLs are in the order CSVs.
TME comparison capacitor stock is 22,076; red wire 1,513 m; black wire 1,962 m;
signal wire 29 rolls; D2 2,434; Q5 484,454. No actual shortage was found.
Nothing is reserved. Later depletion requires only an exact-item commercial
remedy; a substitute or third supplier requires a new explicit owner decision.

## Stable group identifiers

The original authoritative master is preserved in
`evidence/phase5-1-sourcing/entry-phase5-0-sourcing/MASTER_PURCHASING_BOM.csv`.
Removing the testpoint purchase shifted later IDs in the Phase 5.3–5.5 working
master/shopping list. **Final files restore the original IDs**, retaining
`phase5_5_group_id` as an explicit cross-reference. P001–P057 and all H/profile
IDs retain their meaning. There is no P058 purchase; it remains a no-hardware
record for TP1/TP3/TP4 in the assembly BOM.

| Refs | Phase 5.5 / working master ID | Original master / FINAL ID |
|---|---|---|
| TP1 TP3 TP4 | Purchase removed | P058, zero purchase/fit |
| U1 | P058 | P059 |
| U2 | P059 | P060 |
| U3 U7 | P060 | P061 |
| U4 | P061 | P062 |
| U5 | P062 | P063 |
| U6 | P063 | P064 |
| U8 | P064 | P065 |

Historical CSVs remain intact for audit. Do not regenerate/import those as the
final basket. All 78 purchase rows, their reference coverage and quantities
are preserved in the final files.

## Assembly checklist — repeat for boards 1–5

- [ ] Label each board F5 and record its serial, intended cell count and R5 profile.
  F5 describes the populated 5 V output converter; it does not select cell count.
  Default BOM R5 is 4S/27 kΩ; use the approved alternate for a 2S or 3S board.
- [ ] Fit the 131 actual PCB parts per board (655 across five). Populate all 19
  F5-only refs: C60–C69, J8, L3, Q10, R60–R63, U7 and U8.
- [ ] **R32 Viking ARG02BTC3162 + R33 RESI PTFR0402Q10K0N9 together.**
  R32 =31.6 kΩ/0.1%/25 ppm; R33 =10 kΩ/0.02%/10 ppm. Do not fit the
  rejected pair of two 0.1%/25 ppm resistors or mix with old purchasing stock.
- [ ] **R60 RT0603BRD0716KL =16 kΩ + R61 RT0603BRD073K01L =3.01 kΩ
  together.** Both 0.1%/25 ppm. The schematic still says 53 kΩ/10 kΩ;
  use the assembly BOM values and never replace only one member.
- [ ] Fit L2 Coilank AAPS0530M4R7F and L3 Bourns SRP5050FA-6R8M onto the
  existing ordered pads; preserve accepted orientation/placement. Both nonpolar.
- [ ] Fit U1 H4X, C39 Yageo CC0402KRX7R9BB333, R23 0402WGF8201TCE and
  R63 0603WAF3832T5E. Use the other already-approved ordinary passives in the CSV.
- [ ] Retain earlier approvals: Q3/Q8/Q9 AO3400A; C35/C36 GRM21BR61E226ME44L;
  C32 Yageo CC0805KKX7R9BB225; C33/C45/C64/C65 TDK C3216X5R1V226MTJ00E;
  C63 CC0603KRX7R9BB333; C70/C71 C1608X7R1C105K080AC; U2 TPD2EUSB30ADRTR;
  U8 LM74700QDBVTQ1. All reference-level differences are shown beside unchanged
  schematic metadata in the assembly CSV. R12 remains exact pulse-proof
  CRCW12062R00JNEAHP. Keep TCA9517 non-A and IC1 BQ25798RQMR.
- [ ] Keep the additional TDK C32 stock labelled **comparison only**. Default
  C32 assembly remains Yageo. If using the accepted comparison in a later
  documented prototype test, record the board/MPN; there is only one C32 site.
- [ ] Leave **C20/C22/C24/C25 DNP**. Fit **no testpoint loops, headers or pins**.
  TP1/TP3/TP4 and the copper probe pads remain usable board geometry only;
  mounting holes/net-ties also require no separate purchased hardware.
- [ ] Verify IC pin 1, diode/LED polarity and connector orientation before soldering.
  Mounting-hole hardware and enclosure materials are the existing owner scope.

| R5 profile | Approved MPN / LCSC SKU | Purchase | Fit per board |
|---|---|---:|---:|
| 2S | 0805W8F8201T5E / C17828, 8.2 kΩ | 100 | Exactly one, only on a 2S board |
| 3S | 0805W8F1372T5E / C17448, 13.7 kΩ | 100 | Exactly one, only on a 3S board |
| 4S default | 0805W8F2702T5E / C17593, 27 kΩ | 100 | Exactly one, only on a 4S board |

| Board | F5 / serial | Cell count / R5 | Both resistor pairs checked | DNP / connectors checked |
|---|---|---|---|---|
| 1 | ____ | ____ | [ ] | [ ] |
| 2 | ____ | ____ | [ ] | [ ] |
| 3 | ____ | ____ | [ ] | [ ] |
| 4 | ____ | ____ | [ ] | [ ] |
| 5 | ____ | ____ | [ ] | [ ] |

## Harness keying and pin checks

| PCB connector / exact header | Exact mating housing | Key / pins |
|---|---|---|
| J1 1053131102 | 1053071202 | Black key A, 2-way: 1 PGND, 2 adapter+ |
| J2 1053131103 | 1053071203 | Black key A, 3-way: 1 PGND, **2 empty**, 3 SYS |
| J3 1053132102 | 1053072202 | Natural key B, 2-way: 1 PGND, 2 BATTERY |
| J8 1053132103 | 1053072203 | Natural key B, 3-way: 1 PGND, **2 empty**, 3 F5 5V |
| J4 S6B-XH-A(LF)(SN) | XHP-6 | Current V4 service pinmap; incompatible with V3 |
| J6 S2B-XH-A-1(LF)(SN) | XHP-2 | 1 GND, 2 TS; passive sense, NTC remains owner-system item |

- [ ] Use 1053002100 tin contacts for Nano-Fit: eight per board, 40 fitted
  across five two-wire harness sets; 50 ordered includes 10 trial/rework spares.
  Do not fill centre cavities of J2/J8 and do not infer pins from wire-side views.
- [ ] Use exact **SXH-001T-P0.6**, not its N variant, for JST: up to eight per
  board / 40 total; 100 ordered includes approved spare/MOQ stock.
- [ ] Power wire is 0.5 mm² Cu stranded, 5 m red + 5 m black. Signal wire is
  0.14 mm² white, 2×10 m rolls; identify each conductor at both ends.
  Inspect crimps, retention, continuity, polarity and insulation before connection.
- [ ] Keep the existing external-pack/BMS/adapter/NTC/enclosure responsibility.
  XT30 gender/polarity was not selected: do not buy a guessed mate. Any needed
  exact mate/finishing consumables are owner materials; their unknown cost is
  outside the two component orders, not hidden as zero.

## Remaining owner actions

1. Load the two lists, confirm exact quantities allocate (especially all five J3
   housings), then select Czech delivery and review freight/tax/handling/FX.
2. Submit and pay the actual orders yourself; save supplier acknowledgements.
3. On receipt, check labels/quantities and record R5 choice per board. Follow
   the **existing documented prototype bring-up tests** on matching hardware;
   no additional engineering qualification or component sourcing phase is added.

No confirmed stock/identity blocker remains at this snapshot. Stop here for the
owner's purchase. Existing prototype limits remain recorded in the
[accepted Phase 5.5 review](PHASE5_5_SUBSTITUTION_REVIEW.md); no power-up occurred.
