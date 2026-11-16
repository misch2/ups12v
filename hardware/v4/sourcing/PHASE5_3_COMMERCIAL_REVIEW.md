# Phase5.3 — supplier coverage, remaining quotes and ordering review

2026-10-19. Quick start: review the66-line PROPOSED_ORDERING_CHECKLIST.csv and
SUPPLIER_BASKETS.md. Approve the exact prototype proposals separately from any
future purchase. No cart, checkout, purchase, RFQ or supplier message was sent.

## New or resolved supply work

| Refs | Exact proposed source / purchase | Evidence and remaining limitation |
|---|---|---|
| Q3/Q8/Q9 |AO3400A/C20917,20,USD1.96 |Owner APPROVED; Phase5.2 dated quote reused, not a new stock refresh |
| C35/C36 |GRM21BR61E226ME44L/C86816,15,USD3.3945 |Owner APPROVED FOR PROTOTYPE; Phase5.2 quote reused |
| TP1/TP3/TP4 |0pieces,0spares,0wire |No procurement/fabrication requirement; owner inventory optional |
| C32 |YAGEOCC0805KKX7R9BB225/[C125847](https://www.lcsc.com/product-detail/C125847.html),10,USD1.39 |Last-week cached81,765;MOQ/multiple5; prototype risk acceptance pending |
| C33/C45/C64/C65 |TDKC3216X5R1V226MTJ00E/[C342620](https://www.lcsc.com/product-detail/C342620.html),30,USD10.926 |Today-cached92,160,MOQ/multiple10. Manufacturer full-code mapping found; Ceff prototype acceptance pending |
| D3/D4 |ExactBAS116H,115/[LCSCC74210](https://www.lcsc.com/de/product-detail/C74210.html),20,USD1.338 |Today-cached55,050;MOQ/multiple10.10fit+1spare+9excess. No diode substitution; TME shortage no longer blocks this line |
| C8 |ExactGCM1555C1H102JA16D/LCSCC437434,50,USD0.665 |Last-month cached8,450;MOQ/multiple50.5fit+3spare+42excess; source/price in master |
| L1 |ExactDR125-2R2-R/[DigiKey513-1662-1-ND](https://www.digikey.com/en/products/detail/eaton-electronics-division/DR125-2R2-R/667148),5,USD4.15 |2-week cache57;MOQ/multiple1. LCSC regional pages disagree, so use the explicitDigiKey exact offer |
| R6 |RC0805FR-075K6L/DigiKey311-5.60KCRCT-ND,8,USD0.80 |2-week cache134,765;MOQ/multiple1. Optional10-tier reduces total toUSD0.34; master retains8 |
| R23 |RC0402FR-078K2L/DigiKey311-8.20KLRCT-ND,8,USD0.80 |Yesterday cache342,368;MOQ/multiple1. Optional10-tier reduces total toUSD0.21; master retains8 |
| R12 |ExactCRCW12062R00JNEAHP/[DigiKey541-2.0UACT-ND](https://www.digikey.com/en/products/detail/vishay-dale/CRCW12062R00JNEAHP/2228087),6,USD2.10 |5-month cached14,909;MOQ/multiple1. Dated allowance needs refresh; preserveHP rating. OldCZK quote kept separate |
| C63 |ProposedYAGEOCC0603KRX7R9BB333/[DigiKey311-1429-1-ND](https://www.digikey.com/en/products/detail/yageo/CC0603KRX7R9BB333/2833735),8,USD0.96 |OriginalMurata obsolete/no stock. Yesterday cache48,255;MOQ/multiple1. Manufacturer nominal/dimension evidence recorded; owner exact-MPN approval pending. Optional10tierUSD0.65 |

All observations retrieved19October2026. Cache age is explicit, not a claim of
reserved or executable checkout stock. Rows not refreshed here retain dated
Phase5.2/earlier observations. Complete manufacturer/SKU/URL/quantity/tier and
evidence fields for every line are in the master/checklist.

## Exact L2/L3 and regional delivery

**L2:** retainXAL5030-472MEC,5pieces, no spare. Existing
[LCSCC7432409](https://www.lcsc.com/product-detail/C7432409.html)5×USD5.9335=USD29.6675,
MOQ/multiple1,3-day cached1,174 remains a concrete fallback. Coilcraft's prior
USD2.74 indication is not an allocated5-piece quote.

**L3:** retainXAL5050-682MEC,5pieces, no spare. A live browser check of the
[manufacturer page](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal50xx/xal5050-682/)
used UKWarehouse/EUR, M/E/Cselected and quantity5. The visible1+tier wasEUR2.62
(5pieces arithmeticEUR13.10). After quantity update the stock/dispatch quantity
was blank. The page also displayed250per7inch reel, which is packaging, not
proof of a250piece minimum. No AddToCart action was taken. This improves the
regional price indication but **does not establish five available pieces or a
delivered quote**. Text evidence is saved in Phase5.3. The old generic static
in-stock phrase and unavailable-configuration dialog cannot prove allocation.

[FarnellDE2289071](https://de.farnell.com/coilcraft/xal5050-682mec/induktivit-t-6-8uh-6-4a-20-leist/dp/2289071)
has3-week cachedbackorder26February2027,42-week standard lead time,MOQ/multiple1,
EUR6.01/pc indication (5=EUR30.05). EnglishDEcached priceEUR6.31 differs; neither
is a Czech commitment. Czech page fetch failed. UKcached2026July dates are stale,
not reliable current supply. MouserMEC page reports restricted regional supply,
previouspartnumber and no cut tape; it does not establish anMRC replacement.
Do not buy full reels or change inductance/series/termination to hide the gap.

**Concrete unsent request:** CoilcraftEurope:5XAL5050-682MEC in loose tape, plus
an alternative combined5XAL5030-472MEC+5XAL5050-682MEC quote. Confirm exactMPNs,
allocatable stock or build lead time, dispatch date, pieceMOQ/multiple, ordinary
tape without paid leaders, EUR net line totals, Czech freight and tax/handling
collection. FarnellCzech2289069/2289071 is the fallback request. If no exactL3
can be supplied in a practical time, obtain an owner decision before a different
inductor assessment. No such redesign/substitution is within this checkpoint.

## D2 and precision R32

D2exactDialight597-3605-607F remains discontinued but has a retainedTME offer:
8=5fit+3spare,USD0.39each/USD3.12,MOQ/multiple1,last-week cached2,434 fromPhase5.2.
The new older4-month search observation2,437/USD0.40 is not promoted over that
newer observation. Refresh exact allocation before purchase. A newLED is not
needed while exact supply works; no color, polarity or footprint substitute is
approved. If stock fails, same-footprint0805blue alternatives need manufacturer
pin1K/pin2A, low-current brightness/Vf and reverse-protection review before use.

R32 **TE RN73C1E31K6BTD**,8pieces,0402/31.6k/0.1%/10ppm:
[Mouser279-RN73C1E31K6BTD](https://au.mouser.com/en/ProductDetail/TE-Connectivity-AMP/RN73C1E31K6BTD?qs=sGAEpiMZZMvdGkrng054t3JR9pTAeVpLheHvv27vnVmmmus07uyG1g%3D%3D)
Australia last-month page identifies3,207stock and cut-tapeMOQ/multiple1.
Exact source is now established; usableUSD/Czech delivered price is not. The
master therefore has quantity8 with blankUSD price. Request its regional price
and compare both exactR32/R33 on one existing shipment; no25ppm substitution.
An Australian or Indian price is not silently converted toUSD or assumed to shipCZ.

## Consolidation and cost boundary

Partial electronics **USD244.1846**, now onlyL3andR32unpriced. Separate harness
**USD16.7510**; combined partial **USD260.9356**. This includes proposed exact
identities and cached prices, not purchase release. The15-line owner-accepted
dated-price subset is **USD98.6589**. Removed unquotedL3USD15.10; replaced the
unavailableTDK reference with the mappedLCSC offer andTMEdiode shortage with
the exactLCSC offer. No numeric comparison with previous partial totals is a
claim of a fully supplied saving. All66planning rows have MOQ/multiple support.

Preferred provisional allocation: LCSC main electronics/L2; DigiKey exactL1,
R5,precision/header parts and proposedC63; TMEexactD2 and remaining suitable
lines; CoilcraftL3. R32Mouser may add a fifth parcel unless exactR32/R33 can
transfer economically. First closeL3/R32regional quotes, then compare transfer
premiums with each avoided shipment. PriorTME/DigiKey transport observations
remain context, not fresh delivered quotes. LCSC/UK/FX/tax/handling unknowns stay
unknown; the already submittedJLCPCB order is not assumed combinable withLCSC.
No cheapest-route or complete delivered-total claim.

Review connector/harness lengths, wire/crimp dimensions, mating gender, owned
tools and paste/flux together with HARNESS_AND_ASSEMBLY_BOM.csv. Blank prices
are not free materials. No TP wire or loops belong in that list. External cells,
BMS andPD converter/firmware remain excluded. Supplier requests above are drafts
for owner review, not messages sent on the owner's behalf.

**STOP for owner review before purchases.**
