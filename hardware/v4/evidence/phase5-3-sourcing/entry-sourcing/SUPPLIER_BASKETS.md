# Phase5.2 — proposed supplier ordering checklist; owner review STOP

2026-10-19. Quick start: OPEN_DECISIONS.md → PHASE5_2_COMPATIBILITY_REVIEW.md →
this checklist and PROPOSED_ORDERING_CHECKLIST.csv. No cart, checkout, RFQ or order.

Purchase capacity **0F0+5F5**:670fitted components;65physical groups plus2extraR5
stock rows. Exactly5TI BQ25798RQMR/C2876593. R5:10each8.2k/13.7k/27k0805/1%,
30pieces;5mutually exclusive fitted positions counted once. Spares/MOQ excess
separate. C20/C22/C24/C25 and16PCB-only features buy zero. External cells/BMS,
external PD converter and firmware remain out of scope.

## Cost boundary

**Incomplete electronics allowance USD236.7896**, 10lines without a
usable USD extended total; 9lines lack confirmed MOQ-derived quantities.
Includes cached prices, proposed identities, unquoted Coilcraft L3USD15.10
indication, and D3/D4 price despite stock3versus11required. It is not an executable
complete basket. Separate priced harness portionUSD16.7510; combined partial
USD253.5406. Missing parts/materials, VAT, freight, import/handling and FX
remain additional unknowns. No complete delivered total or cheapest-route claim.
R12 historical10October2026quote7.47CZKnet/pc,6=44.82CZK, remains separate; no FX
conversion or double count. Current quote still needed.

## Explicitly accepted exact identities with dated price observations

**12-line subset, USD89.1544**. U8/C70/C71 are incorporated with
original MPN traceability. No other substitute was promoted. This subset is
incomplete and is not purchase authorization. Cached stock is not reserved;
confirm regional stock/terms before purchasing. Unapproved parts are excluded.

| Supplier / refs | Manufacturer MPN / SKU / direct URL | Fit+spare | Order | Unit USD | Extended USD |
|---|---|---:|---:|---:|---:|
| DigiKey / J1 | [Molex 1053131102](https://www.digikey.com/en/products/detail/molex/1053131102/7693174);WM16893-ND | 5+0 | 5 | 1.03 | 5.15 |
| DigiKey / J2 | [Molex 1053131103](https://www.digikey.com/en/products/detail/molex/1053131103/7693175);WM16894-ND | 5+0 | 5 | 5.16 | 25.8 |
| DigiKey / J3 | [Molex 1053132102](https://www.digikey.com/en/products/detail/molex/1053132102/7693181);WM16900-ND | 5+0 | 5 | 1.14 | 5.7 |
| DigiKey / J8 | [Molex 1053132103](https://www.digikey.com/en/products/detail/molex/1053132103/7693182);WM16901-ND | 5+0 | 5 | 1.26 | 6.3 |
| LCSC / C70 C71 | [TDK C1608X7R1C105K080AC](https://www.lcsc.com/product-detail/C2167399.html);C2167399 | 10+3 | 20 | 0.0551 | 1.102 |
| LCSC / IC1 | [Texas Instruments BQ25798RQMR](https://www.lcsc.com/product-detail/C2876593.html);C2876593 | 5+0 | 5 | 2.8576 | 14.288 |
| LCSC / J4 | [JST S6B-XH-A(LF)(SN)](https://www.lcsc.com/product-detail/C157919.html);C157919 | 5+0 | 5 | 0.1427 | 0.7135 |
| LCSC / J6 | [JST S2B-XH-A-1(LF)(SN)](https://www.lcsc.com/product-detail/C163035.html);C163035 | 5+0 | 5 | 0.0995 | 0.4975 |
| LCSC / J7 | [GCT USB4085-GF-A](https://www.lcsc.com/product-detail/C7095263.html);C7095263 | 5+0 | 5 | 1.4204 | 7.102 |
| LCSC / U2 | [Texas Instruments TPD2EUSB30ADRTR](https://www.lcsc.com/product-detail/C94934.html);C94934 | 5+1 | 6 | 0.5219 | 3.1314 |
| LCSC / U8 | [Texas Instruments LM74700QDBVTQ1](https://www.lcsc.com/product-detail/C2653623.html);C2653623 | 5+1 | 6 | 2.715 | 16.29 |
| TME / SW1 SW2 | [Panasonic EVQP0Q02Q](https://www.tme.eu/en/details/evqp0q02q/microswitches-tact/panasonic/);EVQP0Q02Q | 10+1 | 11 | 0.28 | 3.08 |

## Complete conditional planning allocation

**All rows below are conditional proposals**, including unapproved selections and engineering holds. A price does not approve an MPN. Blank means unknown, never zero. CSV includes packaging, cache age, evidence, original MPN and per-line readiness.

### Coilcraft Europe (direct quote): 1lines; partial USD15.1000

| Refs | Manufacturer MPN / SKU / URL | Fit+spare+R5 stock | MOQ/multiple | Order/excess | Unit USD | Ext USD | Selection / commercial gate |
|---|---|---:|---:|---:|---:|---:|---|
| L3 | [Coilcraft XAL5050-682MEC](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal50xx/xal5050-682/);XAL5050-682MEC | 5+0+0 | 1/1 | 5/0 | 3.02 | 15.1 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |

### DigiKey: 17lines; partial USD70.2700

| Refs | Manufacturer MPN / SKU / URL | Fit+spare+R5 stock | MOQ/multiple | Order/excess | Unit USD | Ext USD | Selection / commercial gate |
|---|---|---:|---:|---:|---:|---:|---|
| C39 | [Murata GRM155R71H333KE14D](https://www.digikey.com/en/products/detail/murata-electronics/GRM155R71H333KE14D/5403163);490-11984-1-ND | 5+3+0 | 1/1 | 8/0 | 0.1 | 0.8 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C63 | [Murata GRM188R71H333KA61D](https://www.digikey.com/en/products/detail/murata-electronics/GRM188R71H333KA61D/702550);SKU missing | 5+3+0 | ?/? | quote/? | unquoted | unpriced | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| D1 | [Micro Commercial Components BZT52C12-TP](https://www.digikey.com/en/products/detail/mcc-micro-commercial-components/BZT52C12-TP/806054);SKU missing | 5+1+0 | 1/1 | 6/0 | 0.14 | 0.84 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| J1 | [Molex 1053131102](https://www.digikey.com/en/products/detail/molex/1053131102/7693174);WM16893-ND | 5+0+0 | 1/1 | 5/0 | 1.03 | 5.15 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| J2 | [Molex 1053131103](https://www.digikey.com/en/products/detail/molex/1053131103/7693175);WM16894-ND | 5+0+0 | 1/1 | 5/0 | 5.16 | 25.8 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| J3 | [Molex 1053132102](https://www.digikey.com/en/products/detail/molex/1053132102/7693181);WM16900-ND | 5+0+0 | 1/1 | 5/0 | 1.14 | 5.7 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| J8 | [Molex 1053132103](https://www.digikey.com/en/products/detail/molex/1053132103/7693182);WM16901-ND | 5+0+0 | 1/1 | 5/0 | 1.26 | 6.3 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| Q3 Q8 Q9 | [Nexperia PMV16UN,215](https://www.digikey.com/en/products/detail/nxp-usa-inc/PMV16UN-215/2704843);SKU missing | 15+1+0 | ?/? | quote/? | unquoted | unpriced | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R5 | [YAGEO RC0805FR-0727KL](https://www.digikey.com/en/products/detail/yageo/RC0805FR-0727KL/730727);311-27.0KCRCT-ND | 5+5+0 | 1/1 | 10/0 | 0.034 | 0.34 | SPEC_OWNER_APPROVED_MPN_PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R12 | [Vishay CRCW12062R00JNEAHP](https://www.digikey.com/en/products/detail/vishay-dale/CRCW12062R00JNEAHP/2826105);541-2.0UACT-ND | 5+1+0 | ?/? | quote/? | unquoted | unpriced | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R32 | [TE Connectivity RN73C1E31K6BTD](https://www.digikey.com.br/pt/products/detail/te-connectivity-passive-product/RN73C1E31K6BTD/6558319);SKU missing | 5+3+0 | ?/? | quote/? | unquoted | unpriced | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R33 | [TE Connectivity RN73C1E10KBTD](https://www.digikey.com/en/products/detail/te-connectivity-passive-product/RN73C1E10KBTD/5247931);A121671CT-ND | 5+3+0 | 1/1 | 8/0 | 0.68 | 5.44 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R60 | [KOA Speer RN73R1JTTD5302B25](https://www.digikey.com/en/products/detail/koa-speer-electronics-inc/RN73R1JTTD5302B25/10018802);2019-RN73R1JTTD5302B25CT-ND | 5+3+0 | 1/1 | 8/0 | 0.1 | 0.8 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R63 | [YAGEO RC0603FR-0738K3L](https://www.digikey.com/en/products/detail/yageo/RC0603FR-0738K3L/727191);311-38.3KHRCT-ND | 5+3+0 | 1/1 | 8/0 | 0.1 | 0.8 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| U1 | [Espressif ESP32-C3-MINI-1-N4X](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-C3-MINI-1-N4X/27525554);1965-ESP32-C3-MINI-1-N4XCT-ND | 5+0+0 | 1/1 | 5/0 | 3.26 | 16.3 | VERIFIED_RETAINED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R5 (alternative stock only) | [YAGEO RC0805FR-078K2L](https://www.digikey.com/en/products/detail/yageo/RC0805FR-078K2L/731094);311-8.20KCRCT-ND | 0+0+10 | 1/1 | 10/0 | 0.1 | 1.0 | SPEC_OWNER_APPROVED_MPN_PROPOSED; HOLD_EXACT_MPN_PROPOSAL_AND_QUOTE |
| R5 (alternative stock only) | [YAGEO RC0805FR-0713K7L](https://www.digikey.com/en/products/detail/yageo/RC0805FR-0713K7L/727588);311-13.7KCRCT-ND | 0+0+10 | 1/1 | 10/0 | 0.1 | 1.0 | SPEC_OWNER_APPROVED_MPN_PROPOSED; HOLD_EXACT_MPN_PROPOSAL_AND_QUOTE |

### LCSC: 41lines; partial USD143.1796

| Refs | Manufacturer MPN / SKU / URL | Fit+spare+R5 stock | MOQ/multiple | Order/excess | Unit USD | Ext USD | Selection / commercial gate |
|---|---|---:|---:|---:|---:|---:|---|
| C1 C2 C23 | [Murata GCM155R71E473KA55D](https://www.lcsc.com/product-detail/Multilayer-Ceramic-Capacitors-MLCC-SMD-SMT_Murata-Electronics_C126529.html);C126529 | 15+3+0 | 50/50 | 50/32 | 0.0103 | 0.515 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C3 C27 | [Murata GRM21BR71E475KA73L](https://www.lcsc.com/product-detail/C162427.html);C162427 | 10+3+0 | 5/5 | 15/2 | 0.1365 | 2.0475 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C4 C10 C11 C14 C17 C19 C21 C30 | [Murata GRJ21BR61E106KE01K](https://www.lcsc.com/product-detail/C5646740.html);C5646740 | 40+8+0 | 5/5 | 50/2 | 0.1077 | 5.385 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C5 C6 C7 C9 C28 C31 C37 C40 C43 C47 C48 | [Murata GRM155R71H104KE14D](https://www.lcsc.com/product-detail/C77020.html);C77020 | 55+11+0 | 50/50 | 100/34 | 0.0106 | 1.06 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C8 | [Murata GCM1555C1H102JA16D](https://www.lcsc.com/product-detail/C437434.html);C437434 | 5+3+0 | ?/? | quote/? | 0.0094 | unpriced | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C12 C13 C15 C16 C18 C60 C61 | [Murata GRM32ER71H106KA12L](https://www.lcsc.com/product-detail/C77102.html);C77102 | 35+1+0 | 5/5 | 40/4 | 0.3827 | 15.308 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C26 | [KEMET C1210C225K1RACTU](https://www.lcsc.com/product-detail/C2168116.html);C2168116 | 5+1+0 | 1/1 | 6/0 | 0.2408 | 1.4448 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C29 | [Murata GRM155R61C105KA12D](https://www.lcsc.com/product-detail/C77006.html);C77006 | 5+3+0 | 50/50 | 50/42 | 0.0157 | 0.785 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C32 | [YAGEO CC0805KKX7R9BB225](https://www.lcsc.com/product-detail/C125847.html);C125847 | 5+3+0 | 5/5 | 10/2 | 0.1274 | 1.274 | PROPOSED_CONDITIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C35 C36 | [Murata GRM21BR61E226ME44L](https://www.lcsc.com/product-detail/C86816.html);C86816 | 10+3+0 | 5/5 | 15/2 | 0.2263 | 3.3945 | PROPOSED_CONDITIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C62 C66 C67 C68 C69 | [Murata GRM188R71H104KA93D](https://www.lcsc.com/product-detail/C77055.html);C77055 | 25+5+0 | 50/50 | 50/20 | 0.0139 | 0.695 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| C70 C71 | [TDK C1608X7R1C105K080AC](https://www.lcsc.com/product-detail/C2167399.html);C2167399 | 10+3+0 | 10/10 | 20/7 | 0.0551 | 1.102 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| F1 | [Littelfuse 0451005.MRL](https://www.lcsc.com/product-detail/C48467.html);C48467 | 5+1+0 | 5/5 | 10/4 | 0.2483 | 2.483 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| IC1 | [Texas Instruments BQ25798RQMR](https://www.lcsc.com/product-detail/C2876593.html);C2876593 | 5+0+0 | 1/1 | 5/0 | 2.8576 | 14.288 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| J4 | [JST S6B-XH-A(LF)(SN)](https://www.lcsc.com/product-detail/C157919.html);C157919 | 5+0+0 | 5/5 | 5/0 | 0.1427 | 0.7135 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| J6 | [JST S2B-XH-A-1(LF)(SN)](https://www.lcsc.com/product-detail/C163035.html);C163035 | 5+0+0 | 5/5 | 5/0 | 0.0995 | 0.4975 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| J7 | [GCT USB4085-GF-A](https://www.lcsc.com/product-detail/C7095263.html);C7095263 | 5+0+0 | 1/1 | 5/0 | 1.4204 | 7.102 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| L1 | [Eaton DR125-2R2-R](https://www.lcsc.com/product-detail/C5337632.html);C5337632 | 5+0+0 | ?/? | quote/? | unquoted | unpriced | OWNER_APPROVED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| L2 | [Coilcraft XAL5030-472MEC](https://www.lcsc.com/product-detail/C7432409.html);C7432409 | 5+0+0 | 1/1 | 5/0 | 5.9335 | 29.6675 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| Q1 Q2 Q10 | [Alpha & Omega Semiconductor AON7528](https://www.lcsc.com/product-detail/C5297617.html);C5297617 | 15+1+0 | 1/1 | 16/0 | 0.7032 | 11.2512 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| Q4 Q6 Q7 | [Nexperia BC847B,215](https://www.lcsc.com/product-detail/C57668.html);C57668 | 15+1+0 | 50/50 | 50/34 | 0.0087 | 0.435 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R1 | [YAGEO RC0805FR-07270RL](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_yageo-rc0805fr-07270rl_C137558.html);C137558 | 5+3+0 | 100/100 | 100/92 | 0.0064 | 0.64 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R4 | [YAGEO RC0805FR-07100RL](https://www.lcsc.com/product-detail/C105577.html);C105577 | 5+3+0 | 100/100 | 100/92 | 0.0044 | 0.44 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R7 | [YAGEO RC0805FR-0733KL](https://www.lcsc.com/product-detail/C141696.html);C141696 | 5+3+0 | 100/100 | 100/92 | 0.0088 | 0.88 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R8 | [YAGEO RC0805FR-072K2L](https://www.lcsc.com/product-detail/C114561.html);C114561 | 5+3+0 | 100/100 | 100/92 | 0.0069 | 0.69 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R9 R10 | [YAGEO RT0805BRD0710KL](https://www.lcsc.com/product-detail/C110775.html);C110775 | 10+3+0 | 20/20 | 20/7 | 0.039 | 0.78 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R11 | [YAGEO RC0805FR-074K7L](https://www.lcsc.com/product-detail/C60816.html);C60816 | 5+3+0 | 100/100 | 100/92 | 0.0073 | 0.73 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R13 R14 | [YAGEO RC0402FR-075K1L](https://www.lcsc.com/product-detail/C105872.html);C105872 | 10+3+0 | 100/100 | 100/87 | 0.0025 | 0.25 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R15 R16 R17 R18 R28 R29 R35 R53 | [YAGEO RC0402FR-0710KL](https://www.lcsc.com/product-detail/C60490.html);C60490 | 40+8+0 | 100/100 | 100/52 | 0.0024 | 0.24 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R19 R20 R21 R22 R24 R31 R46 | [YAGEO RC0402FR-074K7L](https://www.lcsc.com/product-detail/C105871.html);C105871 | 35+7+0 | 100/100 | 100/58 | 0.0029 | 0.29 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R25 R30 R36 R44 R47 R50 R51 R52 | [YAGEO RC0402FR-07100KL](https://www.lcsc.com/product-detail/C60491.html);C60491 | 40+8+0 | 100/100 | 100/52 | 0.0023 | 0.23 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R37 | [YAGEO RC0402FR-0738K3L](https://www.lcsc.com/product-detail/C273719.html);C273719 | 5+3+0 | 100/100 | 100/92 | 0.0023 | 0.23 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R48 R49 | [YAGEO RC0402JR-070RL](https://www.lcsc.com/product-detail/C60485.html);C60485 | 10+3+0 | 100/100 | 100/87 | 0.0024 | 0.24 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R61 | [YAGEO RT0603BRD0710KL](https://www.lcsc.com/product-detail/C95204.html);C95204 | 5+3+0 | 20/20 | 20/12 | 0.0332 | 0.664 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R62 | [YAGEO RC0603FR-07100KL](https://www.lcsc.com/product-detail/C14675.html);C14675 | 5+3+0 | 100/100 | 100/92 | 0.0027 | 0.27 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| U2 | [Texas Instruments TPD2EUSB30ADRTR](https://www.lcsc.com/product-detail/C94934.html);C94934 | 5+1+0 | 1/1 | 6/0 | 0.5219 | 3.1314 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |
| U3 U7 | [Texas Instruments TPS62933DRLR](https://www.lcsc.com/product-detail/C3200405.html);C3200405 | 10+1+0 | 1/1 | 11/0 | 0.3933 | 4.3263 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| U4 | [Diodes Incorporated AP7361C-33E-13](https://www.lcsc.com/product-detail/C500795.html);C500795 | 5+1+0 | 1/1 | 6/0 | 0.9791 | 5.8746 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| U5 | [Texas Instruments TPS2116DRLR](https://www.lcsc.com/product-detail/C3235557.html);C3235557 | 5+1+0 | 1/1 | 6/0 | 0.4022 | 2.4132 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| U6 | [Texas Instruments TCA9517DGKR](https://www.lcsc.com/product-detail/C544515.html);C544515 | 5+1+0 | 1/1 | 6/0 | 0.8536 | 5.1216 | RETAINED_PROVISIONAL; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| U8 | [Texas Instruments LM74700QDBVTQ1](https://www.lcsc.com/product-detail/C2653623.html);C2653623 | 5+1+0 | 1/1 | 6/0 | 2.715 | 16.29 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |

### TME: 7lines; partial USD8.2400

| Refs | Manufacturer MPN / SKU / URL | Fit+spare+R5 stock | MOQ/multiple | Order/excess | Unit USD | Ext USD | Selection / commercial gate |
|---|---|---:|---:|---:|---:|---:|---|
| C33 C45 C64 C65 | [TDK C3216X5R1V226M160AC](https://www.tme.eu/en/details/c3216x5r1v226mac/mlcc-smd-capacitors/tdk/c3216x5r1v226m160ac/);C3216X5R1V226MAC | 20+1+0 | 1/1 | 21/0 | 0.44 | unpriced | RETAINED_PROVISIONAL; HOLD_INSUFFICIENT_OBSERVED_STOCK |
| D2 | [Dialight 597-3605-607F](https://www.tme.eu/en/details/597-3605-607f/smd-colour-leds/dialight/);597-3605-607F | 5+3+0 | 1/1 | 8/0 | 0.39 | 3.12 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| D3 D4 | [Nexperia BAS116H,115](https://www.tme.eu/en/details/bas116h.115/smd-universal-diodes/nexperia/bas116h-115/);BAS116H.115 | 10+1+0 | 1/1 | 11/0 | 0.12 | 1.32 | RETAINED_PROVISIONAL; HOLD_INSUFFICIENT_OBSERVED_STOCK |
| Q5 | [Nexperia BC857B,215](https://www.tme.eu/en/details/bc857b.215/pnp-smd-transistors/nexperia/bc857b-215/);BC857B.215 | 5+1+0 | 1/1 | 6/0 | 0.12 | 0.72 | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R6 | [YAGEO RC0805FR-075K6L](https://www.tme.eu/en/details/rc0805fr-075k6/smd-resistors/yageo/rc0805fr-075k6l/);RC0805FR-075K6 | 5+3+0 | ?/? | quote/? | 0.06 | unpriced | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| R23 | [YAGEO RC0402FR-078K2L](https://www.tme.eu/en/details/rc0402fr-078k2l/smd-resistors/yageo/);RC0402FR-078K2L | 5+3+0 | ?/? | quote/? | 0.04 | unpriced | PROPOSED; HOLD_FOR_SELECTION_OR_PROCUREMENT |
| SW1 SW2 | [Panasonic EVQP0Q02Q](https://www.tme.eu/en/details/evqp0q02q/microswitches-tact/panasonic/);EVQP0Q02Q | 10+1+0 | 1/1 | 11/0 | 0.28 | 3.08 | OWNER_APPROVED; OWNER_ACCEPTED_EXACT_QUOTED |

### TME / LCSC exact-MPN quote needed: 1lines; partial USD0.0000

| Refs | Manufacturer MPN / SKU / URL | Fit+spare+R5 stock | MOQ/multiple | Order/excess | Unit USD | Ext USD | Selection / commercial gate |
|---|---|---:|---:|---:|---:|---:|---|
| TP1 TP3 TP4 | OPEN OPEN_LOOP_1.8MM;SKU missing | 15+1+0 | ?/? | quote/? | unquoted | unpriced | OPEN; HOLD_FOR_SELECTION_OR_PROCUREMENT |

## Missing usable USD totals

| Refs | Exact MPN | Desired request |
|---|---|---:|
| C8 | GCM1555C1H102JA16D | 8 |
| C33 C45 C64 C65 | C3216X5R1V226M160AC | 21 |
| C63 | GRM188R71H333KA61D | 8 |
| L1 | DR125-2R2-R | 5 |
| Q3 Q8 Q9 | PMV16UN,215 | 16 |
| R6 | RC0805FR-075K6L | 8 |
| R12 | CRCW12062R00JNEAHP | 6 |
| R23 | RC0402FR-078K2L | 8 |
| R32 | RN73C1E31K6BTD | 8 |
| TP1 TP3 TP4 | OPEN_LOOP_1.8MM | 16 |

[Commercial gaps and delivery comparison](PHASE5_2_COMMERCIAL_REVIEW.md) explains every missing quote, shortage, cached observation and shipment strategy. [Compatibility](PHASE5_2_COMPATIBILITY_REVIEW.md) controls engineering holds.

## Unapproved alternatives

| Refs | Candidate / SKU / URL | Conditional order | USD | Gate |
|---|---|---:|---:|---|
| C33 C45 C64 C65 | [C3216X5R1V226MTJ00E](https://www.lcsc.com/product-detail/C342620.html);C342620 | 30 | 10.926 | HOLD_EXACT_SUFFIX_AND_CEFF_CONFIRMATION |
| Q3 Q8 Q9 | [AO3400A](https://www.lcsc.com/product-detail/C20917.html);C20917 | 20 | 1.96 | PREFERRED_PROPOSAL_OWNER_APPROVAL_REQUIRED |
| Q3 Q8 Q9 | [PMV16XNR](https://www.lcsc.com/product-detail/C110920.html);C110920 | 20 | 2.988 | SOURCED_ALTERNATIVE_OWNER_APPROVAL_REQUIRED |

AO3400A and PMV16XNR are mutually exclusive; never add both costs/quantities. TDK candidate stays on engineering hold. Harness materials remain separate in HARNESS_AND_ASSEMBLY_BOM.csv. **STOP for owner review.**
