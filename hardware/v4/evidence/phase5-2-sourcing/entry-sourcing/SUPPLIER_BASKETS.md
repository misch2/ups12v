# Phase5.1 supplier baskets — STOP before purchasing

2026-10-19. Owner purchasing basis **N_F0=0,N_F5=5**. Assembly split remains open;
purchase capacity is all five F5 PCBs. No cart, RFQ transmission or order created.

Quick start: review OPEN_DECISIONS.md, then the master CSV and separate R5 file.
**67 planning lines =65 reference groups +2 extra R5 stock options**. The five R5
positions are counted once; purchase 10 each 8.2k/13.7k/27k,30 pieces total. IC1 is
exactly 5 BQ25798RQMR, no automatic spare or deduction for owned BQ25792.

## Cost boundary

The planning worksheet has **USD193.5038 priced/indicative PCBA subtotal**
and **19 unpriced lines**. Fitted-only partial F0/F5 costs are
USD28.0861/USD34.8079.
These are incomplete estimates, not complete board prices. Keep all missing parts,
tax, freight, handling and FX outside the subtotal. Price/cache dates in the CSV
control; historical page stock is not presented as today's stock. Coilcraft's
USD28.80 for 5 + 5 inductors is a retained indicative allowance without a current
stock/delivery quote. Plain cut tape avoids Digi-Reel service fees; none selected.

Separate harness known/indicative connector/contact subtotal **USD16.7510**;
wire, XT30, labels, paste, flux, tools and other blank quotes are additional.
Combined documented partial allowance is **USD210.2548 before tax/freight**.
Applying 21% solely as an illustrative VAT calculation gives USD254.4083;
this is not a delivered quote or a claim that every supplier collects tax this way.

APPROVED_PURCHASING_BASKET.csv contains only **10 explicitly owner-accepted
exact identities with dated price/quantity observations**, subtotal USD 72.3124.
It is a subset, not a complete assembly basket or authorization to order. Its stock
freshness still needs checkout-time verification. All remaining master rows stay
on hold for engineering selection or procurement closure. Owner review of Phase5.0
did not silently approve its many PROPOSED identities.

## Delivered strategies to compare

| Strategy | Allocation and suppliers | Verified delivered-cost terms | Missing quote / practical assessment |
|---|---|---|---|
| A: preferred TME+LCSC with exact fallbacks | TME: 11 current master lines; LCSC: main semiconductor/passive lines; DigiKey: Nano-Fit headers/mates,N4X,R5 cut tape,precision parts; Coilcraft Europe: L2/L3 | TME standard <=20kg CZK140 net/169.40 gross, indicative 1–2 working days. DigiKey Czech standard UPS DDP:free atCZK 1800+, otherwise CZK 600, typical 48 h | Four supplier shipments plus unresolved exact items; LCSC freight/VAT/duty/handling and Coilcraft UK delivery not quoted. Do not combine with already-submitted JLCPCB shipment |
| B: fewer shipments, conditional recommendation | LCSC+DigiKey+Coilcraft; move TME exact switch/diodes/L1/passives into DigiKey shipment if exact stock/price confirmed | Avoiding TME can save its 169.40 CZK gross shipment, subject to package terms. DigiKey fee threshold as above | Three suppliers is a quote target, not verified complete availability. Accept a DigiKey line-price premium only if below avoided TME delivered charge after FX/tax. Exact transfer prices absent; no defensible cheapest-total claim |
| C: EU consolidation quote target | LCSC+DigiKey+Farnell, with Farnell2289069/2289071 exact Coilcraft cut-tape lines plus eligible TME parts | Exact Coilcraft family/distributor identities established; current Czech cut-tape quote not captured | May eliminate UK direct freight/import handling. Farnell freight/stock and 5-piece line prices missing. Full-reel Farnell5131620 MOQ 400 is rejected for this order |

TME line count above is checked against the allocation table below; use its generated
count if source allocation changes. No separate Mouser shipment is justified by
verified current supply in this checkpoint. Mouser remains a fallback quote source.

Sources: [TME Czech shipping](https://www.tme.eu/cz/how-to-buy/7328/zpusoby-a-ceny-dopravy/),
[DigiKey Czech delivery](https://www.digikey.cz/cs/help-support/delivery-information).
DigiKey's UPS DDP option differs from its FedEx/DHL CPT options; obtain the actual
Czech VAT invoice and choose standard distributor stock. Marketplace extra freight
is unquoted, so no marketplace offer is used as a confirmed fallback.
[LCSC's current EU import notice](https://www.lcsc.com/help-center/notice/eu-low-value-import-regulations-2026)
flags VAT and low-value import duty changes. The category count, duty collection,
carrier brokerage and tax base for this basket are **unknown**; do not assume the
old duty-free allowance or invent a fixed charge. LCSC shipping method/transit,
IOSS/DDP applicability and final tax must be quoted. No customs-law determination
is made from a supplier notice. Czech currency conversion/card FX fees unknown.
[Coilcraft Europe](https://www.coilcraft.com/de-de/contact/saleslocations/europe-and-africa/)
states no minimum order and UK warehouse stock generally; this does not establish
stock of either selected part. Quote 5 each exact MEC suffix together, incoterms,
VAT/import/clearance and delivery. All arrival dates remain supplier estimates.

## Conditional replacements — excluded from accepted basket

| References | Proposed exact candidate | Fit/spare/MOQ excess -> conditional order | USD page allowance | Disposition |
|---|---|---|---:|---|
| U8 | [LM74700QDBVTQ1](https://www.lcsc.com/product-detail/C2653623.html) C2653623 | 5+1+0 -> 6 | 16.29 | VALIDATED_PACKAGE_ORDERING_OPTION_OWNER_ACCEPTANCE_REQUIRED |
| C33 C45 C64 C65 | [C3216X5R1V226MTJ00E](https://www.lcsc.com/product-detail/C342620.html) C342620 | 20+1+9 -> 30 | 10.926 | HOLD_EXACT_SUFFIX_AND_CEFF_CONFIRMATION |
| C70 C71 | [C1608X7R1C105K080AC](https://www.lcsc.com/product-detail/C2167399.html) C2167399 | 10+3+7 -> 20 | 1.102 | VALIDATED_NOMINAL_AND_PACKAGE_CANDIDATE_OWNER_ACCEPTANCE_REQUIRED |
| Q3 Q8 Q9 | [AO3400A](https://www.lcsc.com/product-detail/C20917.html) C20917 | 15+1+4 -> 20 | 1.96 | STATIC_ELECTRICAL_AND_PACKAGE_CANDIDATE_OWNER_REVIEW_REQUIRED |
| Q3 Q8 Q9 | [PMV16XN,215](https://www.nexperia.com/product/PMV16XN)  | 15+1+ -> unquoted | unquoted | HOLD_NO_VERIFIED_SMALL_ORDER_SOURCE |

The four priced candidates add USD 30.2780 only if their original unpriced lines
are replaced after the listed approval/evidence gates. This makes an illustrative
partial PCBA allowance USD 223.7818, still15 unpriced lines;
with the priced harness portion, USD240.5328 before tax/freight.
PMV16XN is an alternative to AO3400A, never a second purchase. Exact TDK suffix
equivalence remains unvalidated, so even this conditional sum is not an approved
basket. C32 qualification is not repaired by adding these candidate costs.

## Complete planning allocation

Quantities: fitted + spare + alternative-profile stock = desired, then separately
MOQ-rounded requested purchase. A blank order means terms missing; use the desired
quantity for obtaining the quote. An unavailable line's numeric quantity is a
planning target only. Prices do not authorize PROPOSED parts.

### LCSC: 36 lines, USD98.1638 priced/indicative

| ID / refs | Exact selected MPN / SKU | Fit+spare+option | Order / MOQ excess | USD extended | State |
|---|---|---:|---:|---:|---|
| P001 C1 C2 C23 | [GCM155R71E473KA55D](https://www.lcsc.com/product-detail/Multilayer-Ceramic-Capacitors-MLCC-SMD-SMT_Murata-Electronics_C126529.html);C126529 | 15+3+0 | quote needed / ? | unpriced | UNVERIFIED;PROPOSED |
| P002 C3 C27 | [GRM21BR71E475KA73L](https://www.lcsc.com/product-detail/C162427.html);C162427 | 10+3+0 | 15 / 2 | 2.0475 | PAGE_IN_STOCK;PROPOSED |
| P003 C4 C10 C11 C14 C17 C19 C21 C30 | [GRJ21BR61E106KE01K](https://www.lcsc.com/product-detail/C5646740.html);C5646740 | 40+8+0 | 50 / 2 | 6.54 | PAGE_IN_STOCK;PROPOSED |
| P004 C5 C6 C7 C9 C28 C31 C37 C40 C43 C47 C48 | [GRM155R71H104KE14D](https://www.lcsc.com/product-detail/C77020.html);C77020 | 55+11+0 | 100 / 34 | 1.06 | PAGE_IN_STOCK;PROPOSED |
| P005 C8 | [GCM1555C1H102JA16D](https://www.lcsc.com/product-detail/C437434.html);C437434 | 5+3+0 | quote needed / ? | unpriced | PAGE_IN_STOCK;RETAINED_PROVISIONAL |
| P006 C12 C13 C15 C16 C18 C60 C61 | [GRM32ER71H106KA12L](https://www.lcsc.com/product-detail/C77102.html);C77102 | 35+1+0 | 40 / 4 | 15.308 | PAGE_IN_STOCK;RETAINED_PROVISIONAL |
| P007 C26 | [C1210C225K1RACTU](https://www.lcsc.com/product-detail/C2168116.html);C2168116 | 5+1+0 | 6 / 0 | 1.4448 | PAGE_IN_STOCK;RETAINED_PROVISIONAL |
| P008 C29 | [GRM155R61C105KA12D](https://www.lcsc.com/product-detail/C77006.html);C77006 | 5+3+0 | 50 / 42 | 0.785 | PAGE_IN_STOCK;PROPOSED |
| P009 C32 | [CC0805KKX7R9BB225](https://www.lcsc.com/product-detail/C125847.html);C125847 | 5+3+0 | 10 / 2 | 1.274 | PAGE_IN_STOCK;PROPOSED_CONDITIONAL |
| P011 C35 C36 | [GRM21BR61E226ME44L](https://www.lcsc.com/product-detail/C86816.html);C86816 | 10+3+0 | 15 / 2 | 3.3945 | PAGE_IN_STOCK;PROPOSED_CONDITIONAL |
| P013 C62 C66 C67 C68 C69 | [GRM188R71H104KA93D](https://www.lcsc.com/product-detail/C77055.html);C77055 | 25+5+0 | 50 / 20 | 0.695 | PAGE_IN_STOCK;RETAINED_PROVISIONAL |
| P019 F1 | [0451005.MRL](https://www.lcsc.com/product-detail/C48467.html);C48467 | 5+1+0 | 10 / 4 | 2.483 | PAGE_IN_STOCK;RETAINED_PROVISIONAL |
| P020 IC1 | [BQ25798RQMR](https://www.lcsc.com/product-detail/C2876593.html);C2876593 | 5+0+0 | 5 / 0 | 14.288 | PAGE_IN_STOCK;OWNER_APPROVED |
| P024 J4 | [S6B-XH-A(LF)(SN)](https://www.lcsc.com/product-detail/C157919.html);C157919 | 5+0+0 | 5 / 0 | 0.7135 | PAGE_IN_STOCK;OWNER_APPROVED |
| P025 J6 | [S2B-XH-A-1(LF)(SN)](https://www.lcsc.com/product-detail/C163035.html);C163035 | 5+0+0 | 5 / 0 | 0.4975 | PAGE_IN_STOCK;OWNER_APPROVED |
| P026 J7 | [USB4085-GF-A](https://www.lcsc.com/product-detail/C7095263.html);C7095263 | 5+0+0 | 5 / 0 | 7.102 | PAGE_IN_STOCK;OWNER_APPROVED |
| P031 Q1 Q2 Q10 | [AON7528](https://www.lcsc.com/product-detail/C5297617.html);C5297617 | 15+1+0 | 16 / 0 | 13.7216 | PAGE_IN_STOCK;RETAINED_PROVISIONAL |
| P033 Q4 Q6 Q7 | [BC847B,215](https://www.lcsc.com/product-detail/C57668.html);C57668 | 15+1+0 | 50 / 34 | 0.435 | PAGE_IN_STOCK;PROPOSED |
| P035 R1 | [RC0805FR-07270RL](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_yageo-rc0805fr-07270rl_C137558.html);C137558 | 5+3+0 | quote needed / ? | unpriced | UNVERIFIED;PROPOSED |
| P036 R4 | [RC0805FR-07100RL](https://www.lcsc.com/product-detail/C105577.html);C105577 | 5+3+0 | 100 / 92 | 0.44 | PAGE_IN_STOCK;PROPOSED |
| P039 R7 | [RC0805FR-0733KL](https://www.lcsc.com/product-detail/C141696.html);C141696 | 5+3+0 | 100 / 92 | 0.88 | PAGE_IN_STOCK;PROPOSED |
| P040 R8 | [RC0805FR-072K2L](https://www.lcsc.com/product-detail/C114561.html);C114561 | 5+3+0 | 100 / 92 | 0.69 | PAGE_IN_STOCK;PROPOSED |
| P042 R11 | [RC0805FR-074K7L](https://www.lcsc.com/product-detail/C60816.html);C60816 | 5+3+0 | 100 / 92 | 0.73 | PAGE_IN_STOCK;PROPOSED |
| P044 R13 R14 | [RC0402FR-075K1L](https://www.lcsc.com/product-detail/C105872.html);C105872 | 10+3+0 | 100 / 87 | 0.25 | PAGE_IN_STOCK;PROPOSED |
| P045 R15 R16 R17 R18 R28 R29 R35 R53 | [RC0402FR-0710KL](https://www.lcsc.com/product-detail/C60490.html);C60490 | 40+8+0 | 100 / 52 | 0.24 | PAGE_IN_STOCK;PROPOSED |
| P046 R19 R20 R21 R22 R24 R31 R46 | [RC0402FR-074K7L](https://www.lcsc.com/product-detail/C105871.html);C105871 | 35+7+0 | 100 / 58 | 0.29 | PAGE_IN_STOCK;PROPOSED |
| P048 R25 R30 R36 R44 R47 R50 R51 R52 | [RC0402FR-07100KL](https://www.lcsc.com/product-detail/C60491.html);C60491 | 40+8+0 | 100 / 52 | 0.23 | PAGE_IN_STOCK;PROPOSED |
| P051 R37 | [RC0402FR-0738K3L](https://www.lcsc.com/product-detail/C273719.html);C273719 | 5+3+0 | 100 / 92 | 0.23 | PAGE_IN_STOCK;PROPOSED |
| P052 R48 R49 | [RC0402JR-070RL](https://www.lcsc.com/product-detail/C60485.html);C60485 | 10+3+0 | 100 / 87 | 0.24 | PAGE_IN_STOCK;PROPOSED |
| P054 R61 | [RT0603BRD0710KL](https://www.lcsc.com/product-detail/C95204.html);C95204 | 5+3+0 | 20 / 12 | 0.664 | PAGE_IN_STOCK;PROPOSED |
| P055 R62 | [RC0603FR-07100KL](https://www.lcsc.com/product-detail/C14675.html);C14675 | 5+3+0 | 100 / 92 | 0.27 | PAGE_IN_STOCK;PROPOSED |
| P060 U2 | [TPD2EUSB30ADRTR](https://www.lcsc.com/product-detail/C94934.html);C94934 | 5+1+0 | 6 / 0 | 3.1314 | PAGE_IN_STOCK;OWNER_APPROVED |
| P061 U3 U7 | [TPS62933DRLR](https://www.lcsc.com/product-detail/C3200405.html);C3200405 | 10+1+0 | 11 / 0 | 5.6474 | PAGE_IN_STOCK;RETAINED_PROVISIONAL |
| P062 U4 | [AP7361C-33E-13](https://www.lcsc.com/product-detail/C500795.html);C500795 | 5+1+0 | 6 / 0 | 4.9068 | PAGE_IN_STOCK;RETAINED_PROVISIONAL |
| P063 U5 | [TPS2116DRLR](https://www.lcsc.com/product-detail/C3235557.html);C3235557 | 5+1+0 | 6 / 0 | 2.4132 | PAGE_IN_STOCK;RETAINED_PROVISIONAL |
| P064 U6 | [TCA9517DGKR](https://www.lcsc.com/product-detail/C544515.html);C544515 | 5+1+0 | 6 / 0 | 5.1216 | PAGE_IN_STOCK;RETAINED_PROVISIONAL |

### TME: 11 lines, USD4.6700 priced/indicative

| ID / refs | Exact selected MPN / SKU | Fit+spare+option | Order / MOQ excess | USD extended | State |
|---|---|---:|---:|---:|---|
| P010 C33 C45 C64 C65 | [C3216X5R1V226M160AC](https://www.tme.eu/en/details/c3216x5r1v226mac/mlcc-smd-capacitors/tdk/c3216x5r1v226m160ac/);C3216X5R1V226MAC | 20+1+0 | 21 / 0 | unpriced | OUT_OF_STOCK;RETAINED_PROVISIONAL |
| P014 C63 | [GRM188R71H333KA61D](https://www.tme.com/us/en-us/details/grm188r71h333ka61d/mlcc-smd-capacitors/murata/);GRM188R71H333KA61D | 5+3+0 | quote needed / ? | unpriced | UNVERIFIED;RETAINED_PROVISIONAL |
| P016 D1 | [BZT52C12-TP](https://www.tme.eu/cz/en/details/bzt52c12-tp/smd-zener-diodes/micro-commercial-components/);SKU missing | 5+1+0 | quote needed / ? | unpriced | UNVERIFIED;PROPOSED |
| P017 D2 | [597-3605-607F](https://www.tme.eu/cz/details/597-3605-607f/diody-led-smd-barevne/dialight/);SKU missing | 5+3+0 | quote needed / ? | unpriced | UNVERIFIED;PROPOSED |
| P018 D3 D4 | [BAS116H,115](https://www.tme.eu/en/details/bas116h.115/smd-universal-diodes/nexperia/bas116h-115/);BAS116H.115 | 10+1+0 | quote needed / ? | unpriced | UNVERIFIED;RETAINED_PROVISIONAL |
| P028 L1 | [DR125-2R2-R](https://www.tme.eu/cz/details/dr125-2r2-r/tlumivky/eaton-electronics/);DR125-2R2-R | 5+0+0 | quote needed / ? | unpriced | UNVERIFIED;OWNER_APPROVED |
| P034 Q5 | [BC857B,215](https://www.tme.eu/en/details/bc857b.215/pnp-smd-transistors/nexperia/bc857b-215/);BC857B.215 | 5+1+0 | 6 / 0 | 0.72 | PAGE_IN_STOCK;PROPOSED |
| P038 R6 | [RC0805FR-075K6L](https://www.tme.eu/en/details/rc0805fr-075k6/0805-smd-resistors/yageo/rc0805fr-075k6l/);RC0805FR-075K6 | 5+3+0 | quote needed / ? | unpriced | UNVERIFIED;PROPOSED |
| P041 R9 R10 | [RT0805BRD0710KL](https://www.tme.eu/cz/en/details/rt0805brd0710k/smd-resistors/yageo/rt0805brd0710kl/);SKU missing | 10+3+0 | quote needed / ? | unpriced | UNVERIFIED;PROPOSED |
| P047 R23 | [RC0402FR-078K2L](https://www.tme.eu/en/details/rc0402fr-078k2l/smd-resistors/yageo/);RC0402FR-078K2L | 5+3+0 | 8 / 0 | 0.32 | PAGE_IN_STOCK;PROPOSED |
| P057 SW1 SW2 | [EVQP0Q02Q](https://www.tme.eu/en/details/evqp0q02q/microswitches-tact/panasonic/);EVQP0Q02Q | 10+1+0 | 11 / 0 | 3.63 | PAGE_IN_STOCK;OWNER_APPROVED |

### DigiKey: 14 lines, USD61.8700 priced/indicative

| ID / refs | Exact selected MPN / SKU | Fit+spare+option | Order / MOQ excess | USD extended | State |
|---|---|---:|---:|---:|---|
| P012 C39 | [GRM155R71H333KE14D](https://www.digikey.com/en/products/detail/murata-electronics/GRM155R71H333KE14D/5403163);SKU missing | 5+3+0 | quote needed / ? | unpriced | UNVERIFIED;PROPOSED |
| P021 J1 | [1053131102](https://www.digikey.com/en/products/detail/molex/1053131102/7693174);WM16893-ND | 5+0+0 | 5 / 0 | 5.15 | PAGE_IN_STOCK;OWNER_APPROVED |
| P022 J2 | [1053131103](https://www.digikey.com/en/products/detail/molex/1053131103/7693175);WM16894-ND | 5+0+0 | 5 / 0 | 25.8 | PAGE_IN_STOCK;OWNER_APPROVED |
| P023 J3 | [1053132102](https://www.digikey.com/en/products/detail/molex/1053132102/7693181);WM16900-ND | 5+0+0 | 5 / 0 | 5.7 | PAGE_IN_STOCK;OWNER_APPROVED |
| P027 J8 | [1053132103](https://www.digikey.com/en/products/detail/molex/1053132103/7693182);WM16901-ND | 5+0+0 | 5 / 0 | 6.3 | PAGE_IN_STOCK;OWNER_APPROVED |
| P037 R5 | [RC0805FR-0727KL](https://www.digikey.com/en/products/detail/yageo/RC0805FR-0727KL/730727);311-27.0KCRCT-ND | 5+5+0 | 10 / 0 | 0.34 | PAGE_IN_STOCK;SPEC_OWNER_APPROVED_MPN_PROPOSED |
| P043 R12 | [CRCW12062R00JNEAHP](https://www.digikey.com/en/products/detail/vishay-dale/CRCW12062R00JNEAHP/2826105);SKU missing | 5+1+0 | 6 / 0 | unpriced | PAGE_IN_STOCK;RETAINED_PROVISIONAL |
| P049 R32 | [RN73C1E31K6BTD](https://www.digikey.com.br/pt/products/detail/te-connectivity-passive-product/RN73C1E31K6BTD/6558319);SKU missing | 5+3+0 | quote needed / ? | unpriced | UNVERIFIED;RETAINED_PROVISIONAL |
| P050 R33 | [RN73C1E10KBTD](https://www.digikey.com/en/products/detail/te-connectivity-passive-product/RN73C1E10KBTD/5247931);SKU missing | 5+3+0 | quote needed / ? | unpriced | UNVERIFIED;RETAINED_PROVISIONAL |
| P053 R60 | [RN73R1JTTD5302B25](https://www.digikey.com/en/products/detail/koa-speer-electronics-inc/RN73R1JTTD5302B25/10018802);2019-RN73R1JTTD5302B25CT-ND | 5+3+0 | 8 / 0 | 0.8 | PAGE_IN_STOCK;PROPOSED |
| P056 R63 | [RC0603FR-0738K3L](https://www.digikey.com/en/products/detail/yageo/RC0603FR-0738K3L/727191);311-38.3KHRCT-ND | 5+3+0 | 8 / 0 | 0.8 | PAGE_IN_STOCK;PROPOSED |
| P059 U1 | [ESP32-C3-MINI-1-N4X](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-C3-MINI-1-N4X/27525554);1965-ESP32-C3-MINI-1-N4XCT-ND | 5+0+0 | 5 / 0 | 16.3 | PAGE_IN_STOCK;VERIFIED_RETAINED |
| R5-2S R5 (alternative stock only) | [RC0805FR-078K2L](https://www.digikey.com/en/products/detail/yageo/RC0805FR-078K2L/731094);311-8.20KCRCT-ND | 0+0+10 | 10 / 0 | 0.34 | PAGE_IN_STOCK;SPEC_OWNER_APPROVED_MPN_PROPOSED |
| R5-3S R5 (alternative stock only) | [RC0805FR-0713K7L](https://www.digikey.com/en/products/detail/yageo/RC0805FR-0713K7L/727588);311-13.7KCRCT-ND | 0+0+10 | 10 / 0 | 0.34 | PAGE_IN_STOCK;SPEC_OWNER_APPROVED_MPN_PROPOSED |

### Unresolved exact supply: 4 lines, USD0.0000 priced/indicative

| ID / refs | Exact selected MPN / SKU | Fit+spare+option | Order / MOQ excess | USD extended | State |
|---|---|---:|---:|---:|---|
| P015 C70 C71 | [GRM188R71C105KA12D](https://www.lcsc.com/product-detail/C97890.html);C97890 | 10+3+0 | 20 / 7 | unpriced | NOT_AVAILABLE;VERIFIED_RETAINED |
| P032 Q3 Q8 Q9 | [PMV16UN,215](https://www.digikey.com/en/products/detail/nxp-usa-inc/PMV16UN-215/2704843);SKU missing | 15+1+0 | quote needed / ? | unpriced | NOT_AVAILABLE;PROPOSED |
| P058 TP1 TP3 TP4 | OPEN_LOOP_1.8MM;SKU missing | 15+1+0 | quote needed / ? | unpriced | UNVERIFIED;OPEN |
| P065 U8 | [LM74700QDBVRQ1](https://www.lcsc.com/product-detail/C2941042.html);C2941042 | 5+1+0 | 6 / 0 | unpriced | OUT_OF_STOCK;RETAINED_PROVISIONAL |

### Coilcraft Europe: 2 lines, USD28.8000 priced/indicative

| ID / refs | Exact selected MPN / SKU | Fit+spare+option | Order / MOQ excess | USD extended | State |
|---|---|---:|---:|---:|---|
| P029 L2 | [XAL5030-472MEC](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal50xx/xal5030-472/);XAL5030-472MEC | 5+0+0 | 5 / 0 | 13.7 | QUOTE_REQUIRED;RETAINED_PROVISIONAL |
| P030 L3 | [XAL5050-682MEC](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal50xx/xal5050-682/);XAL5050-682MEC | 5+0+0 | 5 / 0 | 15.1 | QUOTE_REQUIRED;RETAINED_PROVISIONAL |

## Quotes still missing

| ID / refs | Exact MPN | Requested minimum with spares | Gap |
|---|---|---:|---|
| P001 C1 C2 C23 | GCM155R71E473KA55D | 18 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P005 C8 | GCM1555C1H102JA16D | 8 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P010 C33 C45 C64 C65 | C3216X5R1V226M160AC | 21 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P012 C39 | GRM155R71H333KE14D | 8 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P014 C63 | GRM188R71H333KA61D | 8 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P015 C70 C71 | GRM188R71C105KA12D | 13 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P016 D1 | BZT52C12-TP | 6 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P017 D2 | 597-3605-607F | 8 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P018 D3 D4 | BAS116H,115 | 11 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P028 L1 | DR125-2R2-R | 5 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P032 Q3 Q8 Q9 | PMV16UN,215 | 16 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P035 R1 | RC0805FR-07270RL | 8 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P038 R6 | RC0805FR-075K6L | 8 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P041 R9 R10 | RT0805BRD0710KL | 13 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P043 R12 | CRCW12062R00JNEAHP | 6 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P049 R32 | RN73C1E31K6BTD | 8 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P050 R33 | RN73C1E10KBTD | 8 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P058 TP1 TP3 TP4 | OPEN_LOOP_1.8MM | 16 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |
| P065 U8 | LM74700QDBVRQ1 | 6 | Price and/or usable availability/MOQ/multiple missing; see master uncertainty field |

Also refresh R5 cached quotes, exact Coilcraft stock/lead times and all shipment
charges. No supplier-import CSV is generated: supported import schema remains
unverified. REVIEW worksheets are not claimed shopping carts.
