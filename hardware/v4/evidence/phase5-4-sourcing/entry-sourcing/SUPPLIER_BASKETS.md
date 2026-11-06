# Phase5.3 — consolidated purchasing checklist; owner review STOP

2026-10-19. Quick start: OPEN_DECISIONS.md, PHASE5_3_COMPATIBILITY_REVIEW.md,
then the supplier groups below and PROPOSED_ORDERING_CHECKLIST.csv.
No cart, checkout, supplier message or order has been created.

## Assembly and purchasing quantities

| Basis | F0 per board | F5 per board | Five F5 boards |
|---|---:|---:|---:|
| Preserved authoritative CAD/manufacturing reference population |115|134|670|
| TP1/TP3/TP4 hardware omitted by explicit owner decision |−3|−3|−15|
| Actual physical component assembly target |112|131|655|

All154reference identities remain tracked. F5 has131physical parts +4always-DNP
capacitors +16pre-existing PCB-only features +3probe pads without hardware.
There are64physical purchasing groups plus2additional R5 stock rows =66lines.
The old67lines included one grouped TP hardware line, now removed. Original
manufacturing counts/files remain historical evidence; no regeneration occurred.
Spares and MOQ excess are purchased stock, not additional fitted positions.
Exactly5TI BQ25798RQMR; R5 exactly10each8.2k/13.7k/27k,30stock pieces for5positions.
TP hardware/wire/spares: zero. Existing owner loops may be used optionally later.

## Commercial scope

**Partial electronics USD244.1846**, excluding2unpriced lines (L3 and R32).
Separate harness USD16.7510; combined partial USD260.9356.
These are dated/cached page observations for proposed quantities; they are not
a complete delivered quote. VAT, freight, import/handling, FX and unselected
wire/tools/consumables remain outside the total. Unconfirmed L3USD15.10 has been
removed from the subtotal. R12's separate oldCZK quote is not added toUSD.
All66planning quantities now have recorded MOQ/multiple support; L3MOQ1 is a
supported order size, **not** an available allocation. R32MOQ1 is from an
AustraliaMouser page, **not** a Czech delivery commitment.

**Owner-accepted exact dated-price subset: 15lines, USD98.6589.**
This includes the newly approved AO3400A and prototype-approved C35/C36, as well
as prior approvals. It remains incomplete and conveys no authorization to buy.

## Complete proposed allocation

Rows retain exact MPN/SKU, original identity, spares and excess. A price does not
approve a proposed MPN. Refresh regional availability before any later purchase.
The C33bank line uses the now manufacturer-mapped TJ00E identity but still needs
owner prototype risk acceptance. C63Yageo is a new **proposal**, not an approval.

### Coilcraft Europe (direct quote): 1lines; partial USD0.0000

| Refs | MPN / SKU / source | Fit + spare + R5 stock | MOQ / multiple | Buy / excess | Unit USD | Ext USD | Status |
|---|---|---:|---:|---:|---:|---:|---|
| L3 | [XAL5050-682MEC](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal50xx/xal5050-682/); XAL5050-682MEC | 5 + 0 + 0 | 1/1 | 5/0 | quote | unpriced | RETAINED_PROVISIONAL; HOLD_SUPPLY_OR_QUOTE |

### DigiKey: 18lines; partial USD79.0800

| Refs | MPN / SKU / source | Fit + spare + R5 stock | MOQ / multiple | Buy / excess | Unit USD | Ext USD | Status |
|---|---|---:|---:|---:|---:|---:|---|
| C39 | [GRM155R71H333KE14D](https://www.digikey.com/en/products/detail/murata-electronics/GRM155R71H333KE14D/5403163); 490-11984-1-ND | 5 + 3 + 0 | 1/1 | 8/0 | 0.1 | 0.8 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C63 | [CC0603KRX7R9BB333](https://www.digikey.com/en/products/detail/yageo/CC0603KRX7R9BB333/2833735); 311-1429-1-ND | 5 + 3 + 0 | 1/1 | 8/0 | 0.12 | 0.96 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| D1 | [BZT52C12-TP](https://www.digikey.com/en/products/detail/mcc-micro-commercial-components/BZT52C12-TP/806054); SKU quote needed | 5 + 1 + 0 | 1/1 | 6/0 | 0.14 | 0.84 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| J1 | [1053131102](https://www.digikey.com/en/products/detail/molex/1053131102/7693174); WM16893-ND | 5 + 0 + 0 | 1/1 | 5/0 | 1.03 | 5.15 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| J2 | [1053131103](https://www.digikey.com/en/products/detail/molex/1053131103/7693175); WM16894-ND | 5 + 0 + 0 | 1/1 | 5/0 | 5.16 | 25.8 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| J3 | [1053132102](https://www.digikey.com/en/products/detail/molex/1053132102/7693181); WM16900-ND | 5 + 0 + 0 | 1/1 | 5/0 | 1.14 | 5.7 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| J8 | [1053132103](https://www.digikey.com/en/products/detail/molex/1053132103/7693182); WM16901-ND | 5 + 0 + 0 | 1/1 | 5/0 | 1.26 | 6.3 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| L1 | [DR125-2R2-R](https://www.digikey.com/en/products/detail/eaton-electronics-division/DR125-2R2-R/667148); 513-1662-1-ND | 5 + 0 + 0 | 1/1 | 5/0 | 0.83 | 4.15 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| R5 | [RC0805FR-0727KL](https://www.digikey.com/en/products/detail/yageo/RC0805FR-0727KL/730727); 311-27.0KCRCT-ND | 5 + 5 + 0 | 1/1 | 10/0 | 0.034 | 0.34 | SPEC_OWNER_APPROVED_MPN_PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R6 | [RC0805FR-075K6L](https://www.digikey.com/en/products/detail/yageo/RC0805FR-075K6L/728002); 311-5.60KCRCT-ND | 5 + 3 + 0 | 1/1 | 8/0 | 0.1 | 0.8 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R12 | [CRCW12062R00JNEAHP](https://www.digikey.com/en/products/detail/vishay-dale/CRCW12062R00JNEAHP/2228087); 541-2.0UACT-ND | 5 + 1 + 0 | 1/1 | 6/0 | 0.35 | 2.1 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R23 | [RC0402FR-078K2L](https://www.digikey.com/en/products/detail/yageo/RC0402FR-078K2L/726662); 311-8.20KLRCT-ND | 5 + 3 + 0 | 1/1 | 8/0 | 0.1 | 0.8 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R33 | [RN73C1E10KBTD](https://www.digikey.com/en/products/detail/te-connectivity-passive-product/RN73C1E10KBTD/5247931); A121671CT-ND | 5 + 3 + 0 | 1/1 | 8/0 | 0.68 | 5.44 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R60 | [RN73R1JTTD5302B25](https://www.digikey.com/en/products/detail/koa-speer-electronics-inc/RN73R1JTTD5302B25/10018802); 2019-RN73R1JTTD5302B25CT-ND | 5 + 3 + 0 | 1/1 | 8/0 | 0.1 | 0.8 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R63 | [RC0603FR-0738K3L](https://www.digikey.com/en/products/detail/yageo/RC0603FR-0738K3L/727191); 311-38.3KHRCT-ND | 5 + 3 + 0 | 1/1 | 8/0 | 0.1 | 0.8 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| U1 | [ESP32-C3-MINI-1-N4X](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-C3-MINI-1-N4X/27525554); 1965-ESP32-C3-MINI-1-N4XCT-ND | 5 + 0 + 0 | 1/1 | 5/0 | 3.26 | 16.3 | VERIFIED_RETAINED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R5 (alternative stock only) | [RC0805FR-078K2L](https://www.digikey.com/en/products/detail/yageo/RC0805FR-078K2L/731094); 311-8.20KCRCT-ND | 0 + 0 + 10 | 1/1 | 10/0 | 0.1 | 1.0 | SPEC_OWNER_APPROVED_MPN_PROPOSED; HOLD_EXACT_MPN_PROPOSAL_AND_QUOTE |
| R5 (alternative stock only) | [RC0805FR-0713K7L](https://www.digikey.com/en/products/detail/yageo/RC0805FR-0713K7L/727588); 311-13.7KCRCT-ND | 0 + 0 + 10 | 1/1 | 10/0 | 0.1 | 1.0 | SPEC_OWNER_APPROVED_MPN_PROPOSED; HOLD_EXACT_MPN_PROPOSAL_AND_QUOTE |

### LCSC: 43lines; partial USD158.1846

| Refs | MPN / SKU / source | Fit + spare + R5 stock | MOQ / multiple | Buy / excess | Unit USD | Ext USD | Status |
|---|---|---:|---:|---:|---:|---:|---|
| C1 C2 C23 | [GCM155R71E473KA55D](https://www.lcsc.com/product-detail/Multilayer-Ceramic-Capacitors-MLCC-SMD-SMT_Murata-Electronics_C126529.html); C126529 | 15 + 3 + 0 | 50/50 | 50/32 | 0.0103 | 0.515 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C3 C27 | [GRM21BR71E475KA73L](https://www.lcsc.com/product-detail/C162427.html); C162427 | 10 + 3 + 0 | 5/5 | 15/2 | 0.1365 | 2.0475 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C4 C10 C11 C14 C17 C19 C21 C30 | [GRJ21BR61E106KE01K](https://www.lcsc.com/product-detail/C5646740.html); C5646740 | 40 + 8 + 0 | 5/5 | 50/2 | 0.1077 | 5.385 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C5 C6 C7 C9 C28 C31 C37 C40 C43 C47 C48 | [GRM155R71H104KE14D](https://www.lcsc.com/product-detail/C77020.html); C77020 | 55 + 11 + 0 | 50/50 | 100/34 | 0.0106 | 1.06 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C8 | [GCM1555C1H102JA16D](https://www.lcsc.com/pl/product-detail/Multilayer-Ceramic-Capacitors-MLCC-SMD-SMT_Murata-Electronics-GCM1555C1H102JA16D_C437434.html); C437434 | 5 + 3 + 0 | 50/50 | 50/42 | 0.0133 | 0.665 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C12 C13 C15 C16 C18 C60 C61 | [GRM32ER71H106KA12L](https://www.lcsc.com/product-detail/C77102.html); C77102 | 35 + 1 + 0 | 5/5 | 40/4 | 0.3827 | 15.308 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C26 | [C1210C225K1RACTU](https://www.lcsc.com/product-detail/C2168116.html); C2168116 | 5 + 1 + 0 | 1/1 | 6/0 | 0.2408 | 1.4448 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C29 | [GRM155R61C105KA12D](https://www.lcsc.com/product-detail/C77006.html); C77006 | 5 + 3 + 0 | 50/50 | 50/42 | 0.0157 | 0.785 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C32 | [CC0805KKX7R9BB225](https://www.lcsc.com/product-detail/C125847.html); C125847 | 5 + 3 + 0 | 5/5 | 10/2 | 0.139 | 1.39 | PROPOSED_CONDITIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C33 C45 C64 C65 | [C3216X5R1V226MTJ00E](https://www.lcsc.com/product-detail/C342620.html); C342620 | 20 + 1 + 0 | 10/10 | 30/9 | 0.3642 | 10.926 | VERIFIED_IDENTITY_PROTOTYPE_REVIEW; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C35 C36 | [GRM21BR61E226ME44L](https://www.lcsc.com/product-detail/C86816.html); C86816 | 10 + 3 + 0 | 5/5 | 15/2 | 0.2263 | 3.3945 | OWNER_APPROVED_PROTOTYPE; OWNER_ACCEPTED_EXACT_QUOTED |
| C62 C66 C67 C68 C69 | [GRM188R71H104KA93D](https://www.lcsc.com/product-detail/C77055.html); C77055 | 25 + 5 + 0 | 50/50 | 50/20 | 0.0139 | 0.695 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C70 C71 | [C1608X7R1C105K080AC](https://www.lcsc.com/product-detail/C2167399.html); C2167399 | 10 + 3 + 0 | 10/10 | 20/7 | 0.0551 | 1.102 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| D3 D4 | [BAS116H,115](https://www.lcsc.com/de/product-detail/C74210.html); C74210 | 10 + 1 + 0 | 10/10 | 20/9 | 0.0669 | 1.338 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| F1 | [0451005.MRL](https://www.lcsc.com/product-detail/C48467.html); C48467 | 5 + 1 + 0 | 5/5 | 10/4 | 0.2483 | 2.483 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| IC1 | [BQ25798RQMR](https://www.lcsc.com/product-detail/C2876593.html); C2876593 | 5 + 0 + 0 | 1/1 | 5/0 | 2.8576 | 14.288 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| J4 | [S6B-XH-A(LF)(SN)](https://www.lcsc.com/product-detail/C157919.html); C157919 | 5 + 0 + 0 | 5/5 | 5/0 | 0.1427 | 0.7135 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| J6 | [S2B-XH-A-1(LF)(SN)](https://www.lcsc.com/product-detail/C163035.html); C163035 | 5 + 0 + 0 | 5/5 | 5/0 | 0.0995 | 0.4975 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| J7 | [USB4085-GF-A](https://www.lcsc.com/product-detail/C7095263.html); C7095263 | 5 + 0 + 0 | 1/1 | 5/0 | 1.4204 | 7.102 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| L2 | [XAL5030-472MEC](https://www.lcsc.com/product-detail/C7432409.html); C7432409 | 5 + 0 + 0 | 1/1 | 5/0 | 5.9335 | 29.6675 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| Q1 Q2 Q10 | [AON7528](https://www.lcsc.com/product-detail/C5297617.html); C5297617 | 15 + 1 + 0 | 1/1 | 16/0 | 0.7032 | 11.2512 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| Q3 Q8 Q9 | [AO3400A](https://www.lcsc.com/product-detail/C20917.html); C20917 | 15 + 1 + 0 | 5/5 | 20/4 | 0.098 | 1.96 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| Q4 Q6 Q7 | [BC847B,215](https://www.lcsc.com/product-detail/C57668.html); C57668 | 15 + 1 + 0 | 50/50 | 50/34 | 0.0087 | 0.435 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R1 | [RC0805FR-07270RL](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_yageo-rc0805fr-07270rl_C137558.html); C137558 | 5 + 3 + 0 | 100/100 | 100/92 | 0.0064 | 0.64 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R4 | [RC0805FR-07100RL](https://www.lcsc.com/product-detail/C105577.html); C105577 | 5 + 3 + 0 | 100/100 | 100/92 | 0.0044 | 0.44 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R7 | [RC0805FR-0733KL](https://www.lcsc.com/product-detail/C141696.html); C141696 | 5 + 3 + 0 | 100/100 | 100/92 | 0.0088 | 0.88 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R8 | [RC0805FR-072K2L](https://www.lcsc.com/product-detail/C114561.html); C114561 | 5 + 3 + 0 | 100/100 | 100/92 | 0.0069 | 0.69 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R9 R10 | [RT0805BRD0710KL](https://www.lcsc.com/product-detail/C110775.html); C110775 | 10 + 3 + 0 | 20/20 | 20/7 | 0.039 | 0.78 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R11 | [RC0805FR-074K7L](https://www.lcsc.com/product-detail/C60816.html); C60816 | 5 + 3 + 0 | 100/100 | 100/92 | 0.0073 | 0.73 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R13 R14 | [RC0402FR-075K1L](https://www.lcsc.com/product-detail/C105872.html); C105872 | 10 + 3 + 0 | 100/100 | 100/87 | 0.0025 | 0.25 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R15 R16 R17 R18 R28 R29 R35 R53 | [RC0402FR-0710KL](https://www.lcsc.com/product-detail/C60490.html); C60490 | 40 + 8 + 0 | 100/100 | 100/52 | 0.0024 | 0.24 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R19 R20 R21 R22 R24 R31 R46 | [RC0402FR-074K7L](https://www.lcsc.com/product-detail/C105871.html); C105871 | 35 + 7 + 0 | 100/100 | 100/58 | 0.0029 | 0.29 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R25 R30 R36 R44 R47 R50 R51 R52 | [RC0402FR-07100KL](https://www.lcsc.com/product-detail/C60491.html); C60491 | 40 + 8 + 0 | 100/100 | 100/52 | 0.0023 | 0.23 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R37 | [RC0402FR-0738K3L](https://www.lcsc.com/product-detail/C273719.html); C273719 | 5 + 3 + 0 | 100/100 | 100/92 | 0.0023 | 0.23 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R48 R49 | [RC0402JR-070RL](https://www.lcsc.com/product-detail/C60485.html); C60485 | 10 + 3 + 0 | 100/100 | 100/87 | 0.0024 | 0.24 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R61 | [RT0603BRD0710KL](https://www.lcsc.com/product-detail/C95204.html); C95204 | 5 + 3 + 0 | 20/20 | 20/12 | 0.0332 | 0.664 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R62 | [RC0603FR-07100KL](https://www.lcsc.com/product-detail/C14675.html); C14675 | 5 + 3 + 0 | 100/100 | 100/92 | 0.0027 | 0.27 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| U2 | [TPD2EUSB30ADRTR](https://www.lcsc.com/product-detail/C94934.html); C94934 | 5 + 1 + 0 | 1/1 | 6/0 | 0.5219 | 3.1314 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| U3 U7 | [TPS62933DRLR](https://www.lcsc.com/product-detail/C3200405.html); C3200405 | 10 + 1 + 0 | 1/1 | 11/0 | 0.3933 | 4.3263 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| U4 | [AP7361C-33E-13](https://www.lcsc.com/product-detail/C500795.html); C500795 | 5 + 1 + 0 | 1/1 | 6/0 | 0.9791 | 5.8746 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| U5 | [TPS2116DRLR](https://www.lcsc.com/product-detail/C3235557.html); C3235557 | 5 + 1 + 0 | 1/1 | 6/0 | 0.4022 | 2.4132 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| U6 | [TCA9517DGKR](https://www.lcsc.com/product-detail/C544515.html); C544515 | 5 + 1 + 0 | 1/1 | 6/0 | 0.8536 | 5.1216 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| U8 | [LM74700QDBVTQ1](https://www.lcsc.com/product-detail/C2653623.html); C2653623 | 5 + 1 + 0 | 1/1 | 6/0 | 2.715 | 16.29 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |

### Mouser: 1lines; partial USD0.0000

| Refs | MPN / SKU / source | Fit + spare + R5 stock | MOQ / multiple | Buy / excess | Unit USD | Ext USD | Status |
|---|---|---:|---:|---:|---:|---:|---|
| R32 | [RN73C1E31K6BTD](https://au.mouser.com/en/ProductDetail/TE-Connectivity-AMP/RN73C1E31K6BTD?qs=sGAEpiMZZMvdGkrng054t3JR9pTAeVpLheHvv27vnVmmmus07uyG1g%3D%3D); 279-RN73C1E31K6BTD | 5 + 3 + 0 | 1/1 | 8/0 | quote | unpriced | RETAINED_PROVISIONAL; HOLD_SUPPLY_OR_QUOTE |

### TME: 3lines; partial USD6.9200

| Refs | MPN / SKU / source | Fit + spare + R5 stock | MOQ / multiple | Buy / excess | Unit USD | Ext USD | Status |
|---|---|---:|---:|---:|---:|---:|---|
| D2 | [597-3605-607F](https://www.tme.eu/en/details/597-3605-607f/smd-colour-leds/dialight/); 597-3605-607F | 5 + 3 + 0 | 1/1 | 8/0 | 0.39 | 3.12 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| Q5 | [BC857B,215](https://www.tme.eu/en/details/bc857b.215/pnp-smd-transistors/nexperia/bc857b-215/); BC857B.215 | 5 + 1 + 0 | 1/1 | 6/0 | 0.12 | 0.72 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| SW1 SW2 | [EVQP0Q02Q](https://www.tme.eu/en/details/evqp0q02q/microswitches-tact/panasonic/); EVQP0Q02Q | 10 + 1 + 0 | 1/1 | 11/0 | 0.28 | 3.08 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |

## Practical consolidation before owner release

1. Use LCSC for the main electronics including exactD3/D4 and mappedTDKbank;
   L2fallback is5×C7432409. No need to substitute the low-leakage diodes.
2. Keep DigiKey cut tape for R5, exactL1, R12 and quoted precision/header lines.
   ProposedC63 also fits this shipment. Compare10-piece tiers for R6/R23/C63:
   their totalsUSD0.34/0.21/0.65 are lower than8-piece totalsUSD0.80/0.80/0.96.
   Current master conservatively retains8each; this optional3-line optimization
   savesUSD1.36 while adding6stock pieces, with655assembly components unchanged.
3. Retain the exactD2 TME last-stock offer,8pieces; refresh it before any purchase.
   If this is the onlyTME line left, compare its whole shipment cost with a reviewed
   same-footprint LED proposal; no replacement is needed while exact stock exists.
4. Request an exact5L3 plus optional5L2 CoilcraftEurope delivered quote. L2's
   direct price indication isUSD15.9675lower than itsLCSC line, before shipping.
   FarnellEU L3backorder is not timely confirmed supply. No unwanted full reels.
5. Quote R32Mouser8pieces with Czech delivery, and compare exactR32/R33 transfer
   to an existing shipment. Do not relax0402/0.1%/10ppm or add a parcel merely
   because a catalog source was found. Keep currencies separate until actualFX.

See PHASE5_3_COMMERCIAL_REVIEW.md for exact gaps and unsent requests; see
HARNESS_AND_ASSEMBLY_BOM.csv for separate materials. All other unapproved exact
identities can be reviewed together as the complete master list. **STOP before purchases.**
