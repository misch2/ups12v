# Phase 5.0 supplier baskets — proposal only

2026-10-19. Scenario **1×F0 + 1×F5**, provisional, not the final assembly
quantity. Five bare PCBs and one0.10mm top stencil are already ordered according
to the owner. No component cart, RFQ transmission, order or import upload was made.

## Use and price limits

The64 named manufacturer identities plus one unresolved loop-testpoint group make
**65 PCBA purchasing lines**. Every line is allocated below, including unquoted
and blocked parts. Quantities in the table are fitted + suggested spare = desired;
the last numeric quantity is the separately MOQ-rounded proposed order. An em dash
means unverified terms, not zero pieces or zero cost. Sources are exact pages or
retained identity links. Source-cache age and all quote limitations remain in the
master CSV/evidence. Search snippets were used for identity discovery, not current
stock. A page observation is not a reservation or guaranteed delivery.

Known/indicative electronics purchase subtotal is **USD83.74**;
**20 lines lack a usable extended quote**. This subtotal includes spares,
MOQ excess and cached manufacturer indicative prices; unavailable reference-only
quotes are excluded. It is not a complete basket or a current delivered-price
estimate. The CSV's per-F0/F5 costs allocate known unit prices to fitted parts;
they exclude spares and MOQ excess. Unknown currency conversion is not invented.

## Strategy A — preferred TME + LCSC, exact secondary sources where needed

Use LCSC for verified exact semiconductor/MLCC/YAGEO groups. Hundred-piece resistor
MOQs cost cents per line; keep excess separate from intentional spares. Keep TME
for exact parts unavailable at LCSC and its existing mechanical/passive sources
when a refreshed small-order quote is economical. A cached TME stock count is
expressly not confirmed-current inventory. Use one DigiKey standard shipment for
the Nano-Fit headers/housings, N4X module and exact R60 where preferred supply is
unproven/unavailable. Obtain an exact combined Coilcraft Europe L2/L3 quote.

This strategy can involve **four suppliers** (TME, LCSC, DigiKey, Coilcraft), plus
Mouser/Farnell only if an unresolved exact part requires it. It is a supplier
preference strategy, not proof of the lowest delivered cost. Do not split more
shipments merely to save a few cents on resistors. Never replace an exact part
automatically to fill a supplier basket.

## Strategy B — reduce paid shipments

Quote **DigiKey + Coilcraft Europe** for all exact PCBA/harness identities, using
cut tape/bulk rather than Digi-Reel/full reel. This is a concrete consolidation
request keyed by the master MPNs and quantities, not a verified complete two-cart
offer: R32 cut-tape supply, old MLCC order codes and U8 still prevent a ready order.
If all exact parts cannot be supplied there, practical fallback is **LCSC +
DigiKey + Coilcraft**, transferring the small TME allocation only after exact
SKU/stock verification. A necessary Mouser exact R32/R33 purchase would add a
shipment and must be compared with that saving. No secondary-supplier charge is
assumed waived.

Compare the incremental delivered DigiKey price for transferred lines against the
entire extra TME/LCSC shipping, tax/import/handling bill. No complete delivered
quote exists, so no numeric saving or global optimum is claimed. Never add
unneeded components solely to reach free shipping; compare useful inventory only.

## Shipping, VAT, handling and delivery to Czech Republic

- [DigiKey Czech terms](https://www.digikey.cz/en/help-support/delivery-information/delivery-time-and-cost),
  retrieved2026-10-19: standard orders typically48h transit; CZK delivery free
  from1800CZK, otherwise600CZK; EUR threshold75EUR, otherwise25EUR. This is transit,
  not a backorder promise. UPS prepaid is described DDP; FedEx/DHL CPT may collect
  duty/customs/VAT on delivery. Marketplace ships separately, may charge extra,
  and does not count toward standard free-shipping thresholds. Use cut tape,
  not the optional USD7 Digi-Reel service. Actual Czech checkout/VAT remains open.
- [TME Czech delivery terms](https://www.tme.eu/cz/how-to-buy/7328/zpusoby-a-ceny-dopravy/),
  retrieved2026-10-19: carrier/weight/payment-dependent. Express≤10kg is listed
 390CZK net/471.90CZK gross; cash on delivery adds35CZK net/42.35CZK gross.
  These are examples from the official tariff, not the selected cheapest route.
  Small ground freight and actual product net/gross VAT must be quoted together.
  International USD pages sometimes display identical net/gross; do not interpret
  that as Czech VAT exemption. No Czech product checkout was performed.
- [LCSC shipping](https://www.lcsc.com/help-center/shipping-delivering/shipping-methods):
  actual freight, delivery time, handling/fuel surcharge, import/VAT and courier
  clearance costs are **unquoted**. The previously submitted JLCPCB shipment is
  separate. No combined shipping or obsolete coupon is assumed.
  [LCSC's2026 EU import notice](https://www.lcsc.com/pl/help-center/notice/eu-low-value-import-regulations-2026)
  describes a3EUR charge per main category for applicable≤150EUR B2C imports,
  separately from VAT. Have the supplier/courier determine actual categories and
  collection route; do not multiply3EUR by BOM line count or assume zero charges.
- [Coilcraft Europe](https://www.coilcraft.com/de-de/contact/saleslocations/europe-and-africa/)
  states no minimum order. Exact L2/L3 stock, fulfillment of retained MEC codes,
  Czech freight, UK import handling/VAT and delivery estimate remain unquoted.
  The old DigiKey L3 Marketplace listing is **no longer available**; its old
  price/stock is not used as a current fallback. Farnell and Mouser exact listings
  are leads, not secured supplies. Confirm any region restriction before payment.
- Tools, paste/cleaner and wire may be better bought locally with an existing
  shipment. Liquid/paste shipping/storage conditions and expiry need an exact
  quote. No ownership of these items has been assumed.

## Allocation and extended costs

### LCSC — 36 lines; priced subtotal USD49.79

| Group / references | Exact MPN / source SKU | Fitted + spare = desired | MOQ-rounded order | USD extended | Status |
|---|---|---:|---:|---:|---|
| P001 C1 C2 C23 | [GCM155R71E473KA55D](https://www.lcsc.com/product-detail/Multilayer-Ceramic-Capacitors-MLCC-SMD-SMT_Murata-Electronics_C126529.html); C126529 | 6 + 3 = 9 | — | — | UNVERIFIED; PROPOSED |
| P002 C3 C27 | [GRM21BR71E475KA73L](https://www.lcsc.com/product-detail/C162427.html); C162427 | 4 + 3 = 7 | 10 | 1.3650 | PAGE_IN_STOCK; PROPOSED |
| P003 C4 C10 C11 C14 C17 C19 C21 C30 | [GRJ21BR61E106KE01K](https://www.lcsc.com/product-detail/C5646740.html); C5646740 | 16 + 4 = 20 | 20 | 2.6160 | PAGE_IN_STOCK; PROPOSED |
| P004 C5 C6 C7 C9 C28 C31 C37 C40 C43 C47 C48 | [GRM155R71H104KE14D](https://www.lcsc.com/product-detail/C77020.html); C77020 | 22 + 5 = 27 | 50 | 0.5300 | PAGE_IN_STOCK; PROPOSED |
| P005 C8 | [GCM1555C1H102JA16D](https://www.lcsc.com/product-detail/C437434.html); C437434 | 2 + 3 = 5 | — | — | PAGE_IN_STOCK; RETAINED_PROVISIONAL |
| P006 C12 C13 C15 C16 C18 C60 C61 | [GRM32ER71H106KA12L](https://www.lcsc.com/product-detail/C77102.html); C77102 | 12 + 1 = 13 | 15 | 5.7405 | PAGE_IN_STOCK; RETAINED_PROVISIONAL |
| P007 C26 | [C1210C225K1RACTU](https://www.lcsc.com/product-detail/C2168116.html); C2168116 | 2 + 1 = 3 | 3 | 0.7224 | PAGE_IN_STOCK; RETAINED_PROVISIONAL |
| P008 C29 | [GRM155R61C105KA12D](https://www.lcsc.com/product-detail/C77006.html); C77006 | 2 + 3 = 5 | 50 | 0.7850 | PAGE_IN_STOCK; PROPOSED |
| P009 C32 | [CC0805KKX7R9BB225](https://www.lcsc.com/product-detail/C125847.html); C125847 | 2 + 3 = 5 | 5 | 0.6370 | PAGE_IN_STOCK; PROPOSED_CONDITIONAL |
| P011 C35 C36 | [GRM21BR61E226ME44L](https://www.lcsc.com/product-detail/C86816.html); C86816 | 4 + 3 = 7 | 10 | 2.2630 | PAGE_IN_STOCK; PROPOSED_CONDITIONAL |
| P013 C62 C66 C67 C68 C69 | [GRM188R71H104KA93D](https://www.lcsc.com/product-detail/C77055.html); C77055 | 5 + 3 = 8 | 50 | 0.6950 | PAGE_IN_STOCK; RETAINED_PROVISIONAL |
| P019 F1 | [0451005.MRL](https://www.lcsc.com/product-detail/C48467.html); C48467 | 2 + 1 = 3 | 5 | 1.2415 | PAGE_IN_STOCK; RETAINED_PROVISIONAL |
| P020 IC1 | [BQ25798RQMR](https://www.lcsc.com/product-detail/C2876593.html); C2876593 | 2 + 1 = 3 | 3 | 8.5728 | PAGE_IN_STOCK; VERIFIED_RETAINED |
| P024 J4 | [S6B-XH-A(LF)(SN)](https://www.lcsc.com/product-detail/C157919.html); C157919 | 2 + 0 = 2 | 5 | 0.7135 | PAGE_IN_STOCK; OWNER_APPROVED |
| P025 J6 | [S2B-XH-A-1(LF)(SN)](https://www.lcsc.com/product-detail/C163035.html); C163035 | 2 + 0 = 2 | 5 | 0.4975 | PAGE_IN_STOCK; OWNER_APPROVED |
| P026 J7 | [USB4085-GF-A](https://www.lcsc.com/product-detail/C7095263.html); C7095263 | 2 + 0 = 2 | 2 | 2.8408 | PAGE_IN_STOCK; OWNER_APPROVED |
| P031 Q1 Q2 Q10 | [AON7528](https://www.lcsc.com/product-detail/C5297617.html); C5297617 | 5 + 1 = 6 | 6 | 5.1456 | PAGE_IN_STOCK; RETAINED_PROVISIONAL |
| P033 Q4 Q6 Q7 | [BC847B,215](https://www.lcsc.com/product-detail/C57668.html); C57668 | 6 + 1 = 7 | 50 | 0.4350 | PAGE_IN_STOCK; PROPOSED |
| P035 R1 | [RC0805FR-07270RL](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_yageo-rc0805fr-07270rl_C137558.html); C137558 | 2 + 3 = 5 | — | — | UNVERIFIED; PROPOSED |
| P036 R4 | [RC0805FR-07100RL](https://www.lcsc.com/product-detail/C105577.html); C105577 | 2 + 3 = 5 | 100 | 0.4400 | PAGE_IN_STOCK; PROPOSED |
| P039 R7 | [RC0805FR-0733KL](https://www.lcsc.com/product-detail/C141696.html); C141696 | 2 + 3 = 5 | 100 | 0.8800 | PAGE_IN_STOCK; PROPOSED |
| P040 R8 | [RC0805FR-072K2L](https://www.lcsc.com/product-detail/C114561.html); C114561 | 2 + 3 = 5 | 100 | 0.6900 | PAGE_IN_STOCK; PROPOSED |
| P042 R11 | [RC0805FR-074K7L](https://www.lcsc.com/product-detail/C60816.html); C60816 | 2 + 3 = 5 | 100 | 0.7300 | PAGE_IN_STOCK; PROPOSED |
| P044 R13 R14 | [RC0402FR-075K1L](https://www.lcsc.com/product-detail/C105872.html); C105872 | 4 + 3 = 7 | 100 | 0.2500 | PAGE_IN_STOCK; PROPOSED |
| P045 R15 R16 R17 R18 R28 R29 R35 R53 | [RC0402FR-0710KL](https://www.lcsc.com/product-detail/C60490.html); C60490 | 16 + 4 = 20 | 100 | 0.2400 | PAGE_IN_STOCK; PROPOSED |
| P046 R19 R20 R21 R22 R24 R31 R46 | [RC0402FR-074K7L](https://www.lcsc.com/product-detail/C105871.html); C105871 | 14 + 3 = 17 | 100 | 0.2900 | PAGE_IN_STOCK; PROPOSED |
| P048 R25 R30 R36 R44 R47 R50 R51 R52 | [RC0402FR-07100KL](https://www.lcsc.com/product-detail/C60491.html); C60491 | 16 + 4 = 20 | 100 | 0.2300 | PAGE_IN_STOCK; PROPOSED |
| P051 R37 | [RC0402FR-0738K3L](https://www.lcsc.com/product-detail/C273719.html); C273719 | 2 + 3 = 5 | 100 | 0.2300 | PAGE_IN_STOCK; PROPOSED |
| P052 R48 R49 | [RC0402JR-070RL](https://www.lcsc.com/product-detail/C60485.html); C60485 | 4 + 3 = 7 | 100 | 0.2400 | PAGE_IN_STOCK; PROPOSED |
| P054 R61 | [RT0603BRD0710KL](https://www.lcsc.com/product-detail/C95204.html); C95204 | 1 + 3 = 4 | 20 | 0.6640 | PAGE_IN_STOCK; PROPOSED |
| P055 R62 | [RC0603FR-07100KL](https://www.lcsc.com/product-detail/C14675.html); C14675 | 1 + 3 = 4 | 100 | 0.2700 | PAGE_IN_STOCK; PROPOSED |
| P060 U2 | [TPD2EUSB30ADRTR](https://www.lcsc.com/product-detail/C94934.html); C94934 | 2 + 1 = 3 | 3 | 1.5657 | PAGE_IN_STOCK; OWNER_APPROVED |
| P061 U3 U7 | [TPS62933DRLR](https://www.lcsc.com/product-detail/C3200405.html); C3200405 | 3 + 1 = 4 | 4 | 2.0536 | PAGE_IN_STOCK; RETAINED_PROVISIONAL |
| P062 U4 | [AP7361C-33E-13](https://www.lcsc.com/product-detail/C500795.html); C500795 | 2 + 1 = 3 | 3 | 2.4534 | PAGE_IN_STOCK; RETAINED_PROVISIONAL |
| P063 U5 | [TPS2116DRLR](https://www.lcsc.com/product-detail/C3235557.html); C3235557 | 2 + 1 = 3 | 3 | 1.2066 | PAGE_IN_STOCK; RETAINED_PROVISIONAL |
| P064 U6 | [TCA9517DGKR](https://www.lcsc.com/product-detail/C544515.html); C544515 | 2 + 1 = 3 | 3 | 2.5608 | PAGE_IN_STOCK; RETAINED_PROVISIONAL |

### TME — 11 lines; priced subtotal USD2.21

| Group / references | Exact MPN / source SKU | Fitted + spare = desired | MOQ-rounded order | USD extended | Status |
|---|---|---:|---:|---:|---|
| P010 C33 C45 C64 C65 | [C3216X5R1V226M160AC](https://www.tme.eu/en/details/c3216x5r1v226mac/mlcc-smd-capacitors/tdk/c3216x5r1v226m160ac/); C3216X5R1V226MAC | 6 + 1 = 7 | 7 | — | OUT_OF_STOCK; RETAINED_PROVISIONAL |
| P014 C63 | [GRM188R71H333KA61D](https://www.tme.com/us/en-us/details/grm188r71h333ka61d/mlcc-smd-capacitors/murata/); GRM188R71H333KA61D | 1 + 3 = 4 | — | — | UNVERIFIED; RETAINED_PROVISIONAL |
| P016 D1 | [BZT52C12-TP](https://www.tme.eu/cz/en/details/bzt52c12-tp/smd-zener-diodes/micro-commercial-components/); SKU unverified | 2 + 1 = 3 | — | — | UNVERIFIED; PROPOSED |
| P017 D2 | [597-3605-607F](https://www.tme.eu/cz/details/597-3605-607f/diody-led-smd-barevne/dialight/); SKU unverified | 2 + 3 = 5 | — | — | UNVERIFIED; PROPOSED |
| P018 D3 D4 | [BAS116H,115](https://www.tme.eu/en/details/bas116h.115/smd-universal-diodes/nexperia/bas116h-115/); BAS116H.115 | 4 + 1 = 5 | — | — | UNVERIFIED; RETAINED_PROVISIONAL |
| P028 L1 | [DR125-2R2-R](https://www.tme.eu/cz/details/dr125-2r2-r/tlumivky/eaton-electronics/); DR125-2R2-R | 2 + 0 = 2 | — | — | UNVERIFIED; OWNER_APPROVED |
| P034 Q5 | [BC857B,215](https://www.tme.eu/en/details/bc857b.215/pnp-smd-transistors/nexperia/bc857b-215/); BC857B.215 | 2 + 1 = 3 | 3 | 0.3600 | PAGE_IN_STOCK; PROPOSED |
| P038 R6 | [RC0805FR-075K6L](https://www.tme.eu/en/details/rc0805fr-075k6/0805-smd-resistors/yageo/rc0805fr-075k6l/); RC0805FR-075K6 | 2 + 3 = 5 | — | — | UNVERIFIED; PROPOSED |
| P041 R9 R10 | [RT0805BRD0710KL](https://www.tme.eu/cz/en/details/rt0805brd0710k/smd-resistors/yageo/rt0805brd0710kl/); SKU unverified | 4 + 3 = 7 | — | — | UNVERIFIED; PROPOSED |
| P047 R23 | [RC0402FR-078K2L](https://www.tme.eu/en/details/rc0402fr-078k2l/smd-resistors/yageo/); RC0402FR-078K2L | 2 + 3 = 5 | 5 | 0.2000 | PAGE_IN_STOCK; PROPOSED |
| P057 SW1 SW2 | [EVQP0Q02Q](https://www.tme.eu/en/details/evqp0q02q/microswitches-tact/panasonic/); EVQP0Q02Q | 4 + 1 = 5 | 5 | 1.6500 | PAGE_IN_STOCK; OWNER_APPROVED |

### DigiKey — 12 lines; priced subtotal USD23.24

| Group / references | Exact MPN / source SKU | Fitted + spare = desired | MOQ-rounded order | USD extended | Status |
|---|---|---:|---:|---:|---|
| P012 C39 | [GRM155R71H333KE14D](https://www.digikey.com/en/products/detail/murata-electronics/GRM155R71H333KE14D/5403163); SKU unverified | 2 + 3 = 5 | — | — | UNVERIFIED; PROPOSED |
| P021 J1 | [1053131102](https://www.digikey.com/en/products/detail/molex/1053131102/7693174); WM16893-ND | 2 + 0 = 2 | 2 | 2.0600 | PAGE_IN_STOCK; OWNER_APPROVED |
| P022 J2 | [1053131103](https://www.digikey.com/en/products/detail/molex/1053131103/7693175); WM16894-ND | 2 + 0 = 2 | 2 | 10.3200 | PAGE_IN_STOCK; OWNER_APPROVED |
| P023 J3 | [1053132102](https://www.digikey.com/en/products/detail/molex/1053132102/7693181); WM16900-ND | 2 + 0 = 2 | 2 | 2.2800 | PAGE_IN_STOCK; OWNER_APPROVED |
| P027 J8 | [1053132103](https://www.digikey.com/en/products/detail/molex/1053132103/7693182); WM16901-ND | 1 + 0 = 1 | 1 | 1.2600 | PAGE_IN_STOCK; OWNER_APPROVED |
| P037 R5 | [RC0805FR-0727KL](https://www.digikey.in/en/products/detail/yageo/RC0805FR-0727KL/730727); SKU unverified | 2 + 3 = 5 | — | — | UNVERIFIED; PROPOSED |
| P043 R12 | [CRCW12062R00JNEAHP](https://www.digikey.com/en/products/detail/vishay-dale/CRCW12062R00JNEAHP/2826105); SKU unverified | 2 + 1 = 3 | 3 | — | PAGE_IN_STOCK; RETAINED_PROVISIONAL |
| P049 R32 | [RN73C1E31K6BTD](https://www.digikey.com.br/pt/products/detail/te-connectivity-passive-product/RN73C1E31K6BTD/6558319); SKU unverified | 2 + 3 = 5 | — | — | UNVERIFIED; RETAINED_PROVISIONAL |
| P050 R33 | [RN73C1E10KBTD](https://www.digikey.com/en/products/detail/te-connectivity-passive-product/RN73C1E10KBTD/5247931); SKU unverified | 2 + 3 = 5 | — | — | UNVERIFIED; RETAINED_PROVISIONAL |
| P053 R60 | [RN73R1JTTD5302B25](https://www.digikey.com/en/products/detail/koa-speer-electronics-inc/RN73R1JTTD5302B25/10018802); 2019-RN73R1JTTD5302B25CT-ND | 1 + 3 = 4 | 4 | 0.4000 | PAGE_IN_STOCK; PROPOSED |
| P056 R63 | [RC0603FR-0738K3L](https://www.digikey.com/en/products/detail/yageo/RC0603FR-0738K3L/727191); 311-38.3KHRCT-ND | 1 + 3 = 4 | 4 | 0.4000 | PAGE_IN_STOCK; PROPOSED |
| P059 U1 | [ESP32-C3-MINI-1-N4X](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-C3-MINI-1-N4X/27525554); 1965-ESP32-C3-MINI-1-N4XCT-ND | 2 + 0 = 2 | 2 | 6.5200 | PAGE_IN_STOCK; VERIFIED_RETAINED |

### Coilcraft direct — 2 lines; priced subtotal USD8.50

| Group / references | Exact MPN / source SKU | Fitted + spare = desired | MOQ-rounded order | USD extended | Status |
|---|---|---:|---:|---:|---|
| P029 L2 | [XAL5030-472MEC](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal50xx/xal5030-472/); XAL5030-472MEC | 2 + 0 = 2 | 2 | 5.4800 | QUOTE_REQUIRED; RETAINED_PROVISIONAL |
| P030 L3 | [XAL5050-682MEC](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal50xx/xal5050-682/); XAL5050-682MEC | 1 + 0 = 1 | 1 | 3.0200 | QUOTE_REQUIRED; RETAINED_PROVISIONAL |

### Unresolved / backorder — 4 lines; priced subtotal USD0.00

| Group / references | Exact MPN / source SKU | Fitted + spare = desired | MOQ-rounded order | USD extended | Status |
|---|---|---:|---:|---:|---|
| P015 C70 C71 | [GRM188R71C105KA12D](https://www.lcsc.com/product-detail/C97890.html); C97890 | 4 + 3 = 7 | 20 | — | NOT_AVAILABLE; VERIFIED_RETAINED |
| P032 Q3 Q8 Q9 | [PMV16UN,215](https://www.digikey.com/en/products/detail/nxp-usa-inc/PMV16UN-215/2704843); UNVERIFIED | 6 + 1 = 7 | — | — | SOURCE_UNRESOLVED; PROPOSED |
| P058 TP1 TP3 TP4 | OPEN_LOOP_1.8MM; SKU unverified | 6 + 1 = 7 | — | — | UNVERIFIED; OPEN |
| P065 U8 | [LM74700QDBVRQ1](https://www.lcsc.com/product-detail/C2941042.html); C2941042 | 1 + 1 = 2 | 2 | — | OUT_OF_STOCK; RETAINED_PROVISIONAL |

## Harness and conditional alternatives

HARNESS_AND_ASSEMBLY_BOM.csv is separate; its priced connector/contact subtotal
is not hidden inside PCBA cost. LCSC1053071202 MOQ5,1053002100 MOQ10 and JST mates/
contacts MOQ20/50/100 are explicit; DigiKey1053071203/2202/2203 can share the header
shipment. Two power contacts per harness;3-position centres remain empty.

If the two capacitor alternatives in UNAPPROVED_ALTERNATIVES.csv are eventually
accepted, their illustrative1+1 purchases would be10×USD0.3642 +10×USD0.0551 =
**USD4.193**, excluding tax/freight. They replace original lines, never add
duplicate capacitors. They currently have automatic purchase quantity0 and are
excluded from every accepted-identity subtotal. Neither option resolves U8,
PMV16UN, testpoint identity or the remaining quote gaps.

Current supplier-import column schemas were not verified; no supplier-import
CSV or cart-creation claim is made. The master CSV is the complete quote/request
worksheet; unapproved/conditional/open rows are not instructions to place an order.
