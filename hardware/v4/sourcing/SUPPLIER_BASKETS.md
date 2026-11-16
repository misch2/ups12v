# Phase5.4 — shopping list by supplier

Quick start: review the exact identities and quantities below, then close L3 allocation and Czech delivery terms before ordering. See [decisions](OPEN_DECISIONS.md) and [cost comparison](PHASE5_4_COMMERCIAL_REVIEW.md).

Dated 19 October 2026. 66 electronics planning lines + 8 exact harness lines. Additional C32 stock is separate below: it would be electronics line 67 after approval. Five F5 boards contain 655 actual physical components. No testpoint hardware or always-DNP purchases.

**All prices are public page allowances, excluding freight, VAT and import/handling unless explicitly stated. None is a firm supplier quotation or allocated stock.** Each exact URL, cache age, alternative and remaining note is retained in [the CSV](SHOPPING_LIST_BY_SUPPLIER.csv).

Fit/spare/excess are distinct; R5 stock rows have zero additional fitted positions. A = owner approved; P = approved for prototype; R = exact identity for owner review; Q = supply/delivery open. A/P do not authorize an order. Ordinary R rows can be approved together using EXACT_IDENTITIES_FOR_OWNER_REVIEW.csv; no new engineering audit is required.

## Coilcraft Europe (quote needed)

| Refs / line | Manufacturer and exact MPN | Supplier SKU / buy link | Fit | Spare | MOQ × multiple | Order | Excess | Unit | Extended | Stock / review |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| L3 (P030) | Coilcraft XAL5050-682MEC | [XAL5050-682MEC](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal50xx/xal5050-682/) | 5 | 0 | 1 × 1 | 5 | 0 | UNKNOWN  | UNKNOWN  | unknown; R;Q |

Goods allowance: UNKNOWN; exact L3 remains unpriced/unallocated.

## DigiKey

| Refs / line | Manufacturer and exact MPN | Supplier SKU / buy link | Fit | Spare | MOQ × multiple | Order | Excess | Unit | Extended | Stock / review |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| C39 (P012) | Murata GRM155R71H333KE14D | [490-11984-1-ND](https://www.digikey.com/en/products/detail/murata-electronics/GRM155R71H333KE14D/5403163) | 5 | 3 | 1 × 1 | 8 | 0 | 0.1 USD | 0.8 USD | 94406; R |
| C63 (P014) | YAGEO CC0603KRX7R9BB333 | [311-1429-1-ND](https://www.digikey.com/en/products/detail/yageo/CC0603KRX7R9BB333/2833735) | 5 | 3 | 1 × 1 | 8 | 0 | 0.12 USD | 0.96 USD | 48255; A |
| D1 (P016) | Micro Commercial Components BZT52C12-TP | [BZT52C12-TPMSCT-ND](https://www.digikey.com/en/products/detail/mcc-micro-commercial-components/BZT52C12-TP/806054) | 5 | 1 | 1 × 1 | 6 | 0 | 0.14 USD | 0.84 USD | 19003; R |
| J1 (P021) | Molex 1053131102 | [WM16893-ND](https://www.digikey.com/en/products/detail/molex/1053131102/7693174) | 5 | 0 | 1 × 1 | 5 | 0 | 1.03 USD | 5.15 USD | 26336; A |
| J2 (P022) | Molex 1053131103 | [WM16894-ND](https://www.digikey.com/en/products/detail/molex/1053131103/7693175) | 5 | 0 | 1 × 1 | 5 | 0 | 5.16 USD | 25.8 USD | 5659; A |
| J3 (P023) | Molex 1053132102 | [WM16900-ND](https://www.digikey.com/en/products/detail/molex/1053132102/7693181) | 5 | 0 | 1 × 1 | 5 | 0 | 1.14 USD | 5.7 USD | 14108; A |
| J8 (P027) | Molex 1053132103 | [WM16901-ND](https://www.digikey.com/en/products/detail/molex/1053132103/7693182) | 5 | 0 | 1 × 1 | 5 | 0 | 1.26 USD | 6.3 USD | 3721; A |
| L1 (P028) | Eaton DR125-2R2-R | [513-1662-1-ND](https://www.digikey.com/en/products/detail/eaton-electronics-division/DR125-2R2-R/667148) | 5 | 0 | 1 × 1 | 5 | 0 | 0.83 USD | 4.15 USD | 156; A |
| R5 (P037) | YAGEO RC0805FR-0727KL | [311-27.0KCRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0805FR-0727KL/730727) | 5 | 5 | 1 × 1 | 10 | 0 | 0.034 USD | 0.34 USD | 29978; R |
| R6 (P038) | YAGEO RC0805FR-075K6L | [311-5.60KCRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0805FR-075K6L/728002) | 5 | 3 | 1 × 1 | 8 | 0 | 0.1 USD | 0.8 USD | 115254; R |
| R12 (P043) | Vishay CRCW12062R00JNEAHP | [541-2.0UACT-ND](https://www.digikey.com/en/products/detail/vishay-dale/CRCW12062R00JNEAHP/2228087) | 5 | 1 | 1 × 1 | 6 | 0 | 0.35 USD | 2.1 USD | 14909; R |
| R23 (P047) | YAGEO RC0402FR-078K2L | [311-8.20KLRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0402FR-078K2L/726662) | 5 | 3 | 1 × 1 | 8 | 0 | 0.1 USD | 0.8 USD | 342368; R |
| R33 (P050) | TE Connectivity RN73C1E10KBTD | [A121671CT-ND](https://www.digikey.com/en/products/detail/te-connectivity-passive-product/RN73C1E10KBTD/5247931) | 5 | 3 | 1 × 1 | 8 | 0 | 0.68 USD | 5.44 USD | 29014; R |
| R60 (P053) | KOA Speer RN73R1JTTD5302B25 | [2019-RN73R1JTTD5302B25CT-ND](https://www.digikey.com/en/products/detail/koa-speer-electronics-inc/RN73R1JTTD5302B25/10018802) | 5 | 3 | 1 × 1 | 8 | 0 | 0.1 USD | 0.8 USD | 4914; R |
| R63 (P056) | YAGEO RC0603FR-0738K3L | [311-38.3KHRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0603FR-0738K3L/727191) | 5 | 3 | 1 × 1 | 8 | 0 | 0.1 USD | 0.8 USD | 94960; R |
| U1 (P058) | Espressif ESP32-C3-MINI-1-N4X | [1965-ESP32-C3-MINI-1-N4XCT-ND](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-C3-MINI-1-N4X/27525554) | 5 | 0 | 1 × 1 | 5 | 0 | 3.26 USD | 16.3 USD | 1800; R |
| R5 (alternative stock only) (R5-2S) | YAGEO RC0805FR-078K2L | [311-8.20KCRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0805FR-078K2L/731094) | 0 | 0 | 1 × 1 | 10 | 0 | 0.034 USD | 0.34 USD | 123118; R |
| R5 (alternative stock only) (R5-3S) | YAGEO RC0805FR-0713K7L | [311-13.7KCRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0805FR-0713K7L/727588) | 0 | 0 | 1 × 1 | 10 | 0 | 0.034 USD | 0.34 USD | 4063; R |
| J2 (H02) | Molex 1053071203 | [WM14959-ND](https://www.digikey.com/en/products/detail/molex/1053071203/6131601) | 5 | 1 | 1 × 1 | 6 | 0 | 0.41 USD | 2.46 USD | 25236; A |
| J3 (H03) | Molex 1053072202 | [WM15015-ND](https://www.digikey.com/en/products/detail/molex/1053072202/6164104) | 5 | 1 | 1 × 1 | 6 | 0 | 0.45 USD | 2.7 USD | 23486; A |
| J8 (H04) | Molex 1053072203 | [WM15016-ND](https://www.digikey.com/en/products/detail/molex/1053072203/6164105) | 5 | 1 | 1 × 1 | 6 | 0 | 0.48 USD | 2.88 USD | 44902; A |

Goods allowance: 85.8 USD.

## LCSC

| Refs / line | Manufacturer and exact MPN | Supplier SKU / buy link | Fit | Spare | MOQ × multiple | Order | Excess | Unit | Extended | Stock / review |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| C1 C2 C23 (P001) | Murata GCM155R71E473KA55D | [C126529](https://www.lcsc.com/product-detail/Multilayer-Ceramic-Capacitors-MLCC-SMD-SMT_Murata-Electronics_C126529.html) | 15 | 3 | 50 × 50 | 50 | 32 | 0.0103 USD | 0.515 USD | 200; R |
| C3 C27 (P002) | Murata GRM21BR71E475KA73L | [C162427](https://www.lcsc.com/product-detail/C162427.html) | 10 | 3 | 5 × 5 | 15 | 2 | 0.1365 USD | 2.0475 USD | 8485; R |
| C4 C10 C11 C14 C17 C19 C21 C30 (P003) | Murata GRJ21BR61E106KE01K | [C5646740](https://www.lcsc.com/product-detail/C5646740.html) | 40 | 8 | 5 × 5 | 50 | 2 | 0.1077 USD | 5.385 USD | 5435; R |
| C5 C6 C7 C9 C28 C31 C37 C40 C43 C47 C48 (P004) | Murata GRM155R71H104KE14D | [C77020](https://www.lcsc.com/product-detail/C77020.html) | 55 | 11 | 50 × 50 | 100 | 34 | 0.0106 USD | 1.06 USD | 2167600; R |
| C8 (P005) | Murata GCM1555C1H102JA16D | [C437434](https://www.lcsc.com/pl/product-detail/Multilayer-Ceramic-Capacitors-MLCC-SMD-SMT_Murata-Electronics-GCM1555C1H102JA16D_C437434.html) | 5 | 3 | 100 × 100 | 100 | 92 | 0.0094 USD | 0.94 USD | 42600; R |
| C12 C13 C15 C16 C18 C60 C61 (P006) | Murata GRM32ER71H106KA12L | [C77102](https://www.lcsc.com/product-detail/C77102.html) | 35 | 1 | 5 × 5 | 40 | 4 | 0.3827 USD | 15.308 USD | 136545; R |
| C26 (P007) | KEMET C1210C225K1RACTU | [C2168116](https://www.lcsc.com/product-detail/C2168116.html) | 5 | 1 | 1 × 1 | 6 | 0 | 0.2408 USD | 1.4448 USD | 10; R |
| C29 (P008) | Murata GRM155R61C105KA12D | [C77006](https://www.lcsc.com/product-detail/C77006.html) | 5 | 3 | 50 × 50 | 50 | 42 | 0.0157 USD | 0.785 USD | 81450; R |
| C32 (P009) | YAGEO CC0805KKX7R9BB225 | [C125847](https://www.lcsc.com/product-detail/C125847.html) | 5 | 3 | 5 × 5 | 10 | 2 | 0.1274 USD | 1.274 USD | 105915; P |
| C33 C45 C64 C65 (P010) | TDK C3216X5R1V226MTJ00E | [C342620](https://www.lcsc.com/product-detail/C342620.html) | 20 | 1 | 10 × 10 | 30 | 9 | 0.3642 USD | 10.926 USD | 92160; P |
| C35 C36 (P011) | Murata GRM21BR61E226ME44L | [C86816](https://www.lcsc.com/product-detail/C86816.html) | 10 | 3 | 5 × 5 | 15 | 2 | 0.2263 USD | 3.3945 USD | 66730; P |
| C62 C66 C67 C68 C69 (P013) | Murata GRM188R71H104KA93D | [C77055](https://www.lcsc.com/product-detail/C77055.html) | 25 | 5 | 50 × 50 | 50 | 20 | 0.0139 USD | 0.695 USD | 336900; R |
| C70 C71 (P015) | TDK C1608X7R1C105K080AC | [C2167399](https://www.lcsc.com/product-detail/C2167399.html) | 10 | 3 | 10 × 10 | 20 | 7 | 0.0551 USD | 1.102 USD | 170; A |
| D3 D4 (P018) | Nexperia BAS116H,115 | [C74210](https://www.lcsc.com/de/product-detail/C74210.html) | 10 | 1 | 10 × 10 | 20 | 9 | 0.0669 USD | 1.338 USD | 55050; R |
| F1 (P019) | Littelfuse 0451005.MRL | [C48467](https://www.lcsc.com/product-detail/C48467.html) | 5 | 1 | 5 × 5 | 10 | 4 | 0.2483 USD | 2.483 USD | 22225; R |
| IC1 (P020) | Texas Instruments BQ25798RQMR | [C2876593](https://www.lcsc.com/product-detail/C2876593.html) | 5 | 0 | 1 × 1 | 5 | 0 | 2.8576 USD | 14.288 USD | 2913; A |
| J4 (P024) | JST S6B-XH-A(LF)(SN) | [C157919](https://www.lcsc.com/product-detail/C157919.html) | 5 | 0 | 5 × 5 | 5 | 0 | 0.1427 USD | 0.7135 USD | 20450; A |
| J6 (P025) | JST S2B-XH-A-1(LF)(SN) | [C163035](https://www.lcsc.com/product-detail/C163035.html) | 5 | 0 | 5 × 5 | 5 | 0 | 0.0995 USD | 0.4975 USD | 113545; A |
| J7 (P026) | GCT USB4085-GF-A | [C7095263](https://www.lcsc.com/product-detail/C7095263.html) | 5 | 0 | 1 × 1 | 5 | 0 | 1.4204 USD | 7.102 USD | 1482; A |
| L2 (P029) | Coilcraft XAL5030-472MEC | [C7432409](https://www.lcsc.com/product-detail/C7432409.html) | 5 | 0 | 1 × 1 | 5 | 0 | 5.9335 USD | 29.6675 USD | 1174; R |
| Q1 Q2 Q10 (P031) | Alpha & Omega Semiconductor AON7528 | [C5297617](https://www.lcsc.com/product-detail/C5297617.html) | 15 | 1 | 1 × 1 | 16 | 0 | 0.7032 USD | 11.2512 USD | 3475; R |
| Q3 Q8 Q9 (P032) | Alpha & Omega Semiconductor AO3400A | [C20917](https://www.lcsc.com/product-detail/C20917.html) | 15 | 1 | 5 × 5 | 20 | 4 | 0.098 USD | 1.96 USD | 488750; A |
| Q4 Q6 Q7 (P033) | Nexperia BC847B,215 | [C57668](https://www.lcsc.com/product-detail/C57668.html) | 15 | 1 | 50 × 50 | 50 | 34 | 0.0087 USD | 0.435 USD | 521350; R |
| R1 (P035) | YAGEO RC0805FR-07270RL | [C137558](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_yageo-rc0805fr-07270rl_C137558.html) | 5 | 3 | 100 × 100 | 100 | 92 | 0.0064 USD | 0.64 USD | 50800; R |
| R4 (P036) | YAGEO RC0805FR-07100RL | [C105577](https://www.lcsc.com/product-detail/C105577.html) | 5 | 3 | 100 × 100 | 100 | 92 | 0.0044 USD | 0.44 USD | 421700; R |
| R7 (P039) | YAGEO RC0805FR-0733KL | [C141696](https://www.lcsc.com/product-detail/C141696.html) | 5 | 3 | 100 × 100 | 100 | 92 | 0.0088 USD | 0.88 USD | 26200; R |
| R8 (P040) | YAGEO RC0805FR-072K2L | [C114561](https://www.lcsc.com/product-detail/C114561.html) | 5 | 3 | 100 × 100 | 100 | 92 | 0.0069 USD | 0.69 USD | 1005000; R |
| R9 R10 (P041) | YAGEO RT0805BRD0710KL | [C110775](https://www.lcsc.com/product-detail/C110775.html) | 10 | 3 | 20 × 20 | 20 | 7 | 0.039 USD | 0.78 USD | 677880; R |
| R11 (P042) | YAGEO RC0805FR-074K7L | [C60816](https://www.lcsc.com/product-detail/C60816.html) | 5 | 3 | 100 × 100 | 100 | 92 | 0.0073 USD | 0.73 USD | 3884800; R |
| R13 R14 (P044) | YAGEO RC0402FR-075K1L | [C105872](https://www.lcsc.com/product-detail/C105872.html) | 10 | 3 | 100 × 100 | 100 | 87 | 0.0025 USD | 0.25 USD | 2179200; R |
| R15 R16 R17 R18 R28 R29 R35 R53 (P045) | YAGEO RC0402FR-0710KL | [C60490](https://www.lcsc.com/product-detail/C60490.html) | 40 | 8 | 100 × 100 | 100 | 52 | 0.0024 USD | 0.24 USD | 444400; R |
| R19 R20 R21 R22 R24 R31 R46 (P046) | YAGEO RC0402FR-074K7L | [C105871](https://www.lcsc.com/product-detail/C105871.html) | 35 | 7 | 100 × 100 | 100 | 58 | 0.0029 USD | 0.29 USD | 7574800; R |
| R25 R30 R36 R44 R47 R50 R51 R52 (P048) | YAGEO RC0402FR-07100KL | [C60491](https://www.lcsc.com/product-detail/C60491.html) | 40 | 8 | 100 × 100 | 100 | 52 | 0.0023 USD | 0.23 USD | 8087600; R |
| R37 (P051) | YAGEO RC0402FR-0738K3L | [C273719](https://www.lcsc.com/product-detail/C273719.html) | 5 | 3 | 100 × 100 | 100 | 92 | 0.0023 USD | 0.23 USD | 4700; R |
| R48 R49 (P052) | YAGEO RC0402JR-070RL | [C60485](https://www.lcsc.com/product-detail/C60485.html) | 10 | 3 | 100 × 100 | 100 | 87 | 0.0024 USD | 0.24 USD | 8252000; R |
| R61 (P054) | YAGEO RT0603BRD0710KL | [C95204](https://www.lcsc.com/product-detail/C95204.html) | 5 | 3 | 20 × 20 | 20 | 12 | 0.0332 USD | 0.664 USD | 389460; R |
| R62 (P055) | YAGEO RC0603FR-07100KL | [C14675](https://www.lcsc.com/product-detail/C14675.html) | 5 | 3 | 100 × 100 | 100 | 92 | 0.0027 USD | 0.27 USD | 7993900; R |
| U2 (P059) | Texas Instruments TPD2EUSB30ADRTR | [C94934](https://www.lcsc.com/product-detail/C94934.html) | 5 | 1 | 1 × 1 | 6 | 0 | 0.5219 USD | 3.1314 USD | 16537; A |
| U3 U7 (P060) | Texas Instruments TPS62933DRLR | [C3200405](https://www.lcsc.com/product-detail/C3200405.html) | 10 | 1 | 1 × 1 | 11 | 0 | 0.3933 USD | 4.3263 USD | 17611; R |
| U4 (P061) | Diodes Incorporated AP7361C-33E-13 | [C500795](https://www.lcsc.com/product-detail/C500795.html) | 5 | 1 | 1 × 1 | 6 | 0 | 0.9791 USD | 5.8746 USD | 2943; R |
| U5 (P062) | Texas Instruments TPS2116DRLR | [C3235557](https://www.lcsc.com/product-detail/C3235557.html) | 5 | 1 | 1 × 1 | 6 | 0 | 0.4022 USD | 2.4132 USD | 61297; R |
| U6 (P063) | Texas Instruments TCA9517DGKR | [C544515](https://www.lcsc.com/product-detail/C544515.html) | 5 | 1 | 1 × 1 | 6 | 0 | 0.8536 USD | 5.1216 USD | 280; R |
| U8 (P064) | Texas Instruments LM74700QDBVTQ1 | [C2653623](https://www.lcsc.com/product-detail/C2653623.html) | 5 | 1 | 1 × 1 | 6 | 0 | 2.715 USD | 16.29 USD | 2394; A |
| J1 (H01) | Molex 1053071202 | [C505029](https://www.lcsc.com/product-detail/C505029.html) | 5 | 1 | 5 × 5 | 10 | 4 | 0.2355 USD | 2.355 USD | 12400; A |
| J1 J2 J3 J8 (H05) | Molex 1053002100 | [C505323](https://www.lcsc.com/product-detail/C505323.html) | 40 | 10 | 10 × 10 | 50 | 0 | 0.0636 USD | 3.18 USD | 6430; A |
| J4 (H06) | JST XHP-6 | [C144405](https://www.lcsc.com/product-detail/C144405.html) | 5 | 1 | 20 × 20 | 20 | 14 | 0.0323 USD | 0.646 USD | 18980; A |
| J6 (H07) | JST XHP-2 | [C144401](https://www.lcsc.com/product-detail/C144401.html) | 5 | 1 | 50 × 50 | 50 | 44 | 0.0246 USD | 1.23 USD | 62950; A |
| J4 J6 (H08) | JST SXH-001T-P0.6 | [C140573](https://www.lcsc.com/product-detail/C140573.html) | 40 | 10 | 100 × 100 | 100 | 50 | 0.013 USD | 1.3 USD | 781800; R |

Goods allowance: 167.0546 USD.

## Mouser

| Refs / line | Manufacturer and exact MPN | Supplier SKU / buy link | Fit | Spare | MOQ × multiple | Order | Excess | Unit | Extended | Stock / review |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| R32 (P049) | TE Connectivity RN73C1E31K6BTD | [279-RN73C1E31K6BTD](https://www.mouser.lt/en/ProductDetail/TE-Connectivity-AMP/RN73C1E31K6BTD?qs=sGAEpiMZZMtlubZbdhIBIFl9NVT0tk6Fnfv9LT%252Bs5DY%3D) | 5 | 3 | 1 × 1 | 8 | 0 | 0.8 EUR | 6.4 EUR | 3207; R;Q |

Goods allowance: 6.4 EUR.

## TME

| Refs / line | Manufacturer and exact MPN | Supplier SKU / buy link | Fit | Spare | MOQ × multiple | Order | Excess | Unit | Extended | Stock / review |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| D2 (P017) | Dialight 597-3605-607F | [597-3605-607F](https://www.tme.eu/en/details/597-3605-607f/smd-colour-leds/dialight/) | 5 | 3 | 1 × 1 | 8 | 0 | 0.39 USD | 3.12 USD | 2434; R |
| Q5 (P034) | Nexperia BC857B,215 | [BC857B.215](https://www.tme.eu/en/details/bc857b.215/pnp-smd-transistors/nexperia/bc857b-215/) | 5 | 1 | 1 × 1 | 6 | 0 | 0.12 USD | 0.72 USD | 224724; R |
| SW1 SW2 (P057) | Panasonic EVQP0Q02Q | [EVQP0Q02Q](https://www.tme.eu/en/details/evqp0q02q/microswitches-tact/panasonic/) | 10 | 1 | 1 × 1 | 11 | 0 | 0.28 USD | 3.08 USD | 28; A |

Goods allowance: 6.92 USD.

## Additional C32 comparison stock — PENDING OWNER APPROVAL

| Refs | Exact part | Supplier / SKU | Fit | Comparison stock | MOQ / multiple | Order | Unit | Extended | Observed stock |
|---|---|---|---:|---:|---|---:|---:|---:|---:|
| C32 alternative only | TDK C2012X7R1H225K125AC | [DigiKey 445-5968-1-ND](https://www.digikey.com/en/products/detail/tdk-corporation/C2012X7R1H225K125AC/2443446) | 0 | 10 | 1 / 1 | 10 | USD0.322 | USD3.22 | 476200; last-week cache |

2.2 µF ±10%, 50 V, X7R, 0805; same 2.0×1.25×1.25 mm nominal body as Yageo. Manufacturer CSV supports about 1.19 µF typical at 18 V by interpolation, compared with Yageo 0.5–0.6 µF typical. Both are 50 V: the recommendation follows bias evidence. See [exact evidence](PHASE5_4_C32_COMPARISON.md). No replacement or additional purchase is approved.

Alternatives: L2 exact Coilcraft combined-order indication EUR 11.90 / 5; R32 optional ten-piece tier EUR 5.62 instead of EUR 6.40 / 8. Neither changes default quantities. C63 stays eight and each R5 profile stays ten as explicitly approved. D2 exact supply is still advertised; no substitute is needed at this checkpoint.

External cells/BMS, pack thermistor/profile, external PD converter, unselected wire/consumables and owned tools remain in [the separate deferred list](DEFERRED_AND_OWNER_INVENTORY.csv). These unknown costs are excluded, never treated as zero. Already ordered PCB/stencil is not ordered again. **STOP for owner review; no checkout or order.**
