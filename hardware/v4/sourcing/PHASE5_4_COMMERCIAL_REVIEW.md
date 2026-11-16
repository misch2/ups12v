# Phase 5.4 — procurement and Czech delivery

Quick start: use [the supplier shopping list](SUPPLIER_BASKETS.md). Retain L2 at
LCSC until the combined Coilcraft route has allocated stock. Close L3 supply and
R32 Czech delivery before treating the list as complete. Requests below are unsent.

## Supplier goods and delivery

| Supplier | Electronics goods | Separate exact harness | Delivery evidence and unknowns |
|---|---:|---:|---|
| LCSC | USD 158.3436; 43 lines including L2 | USD 8.7110; 5 lines | Freight, transit, handling and import total unknown. No merger with the submitted JLCPCB order assumed |
| DigiKey | USD 77.7600; 18 lines | USD 8.0400; 3 lines | Czech page: typically 48 hours; free delivery at CZK 1,800+, otherwise CZK 600. Actual regional basket value must establish eligibility |
| TME | USD 6.9200; 3 lines | — | Standard ≤20 kg: CZK 140 net / 169.40 gross; 1–2 working days after dispatch. Ordinary parcel dimensions and prepaid payment assumed |
| Mouser | R32: EUR 6.40 / 8; 1 line | — | Cached Lithuania offer; Czech price, dispatch, freight and tax collection unknown |
| Coilcraft Europe | L3 excluded from usable total | — | Live UK/EUR indication EUR 13.10 / 5; no allocation, dispatch/build lead time or Czech delivered quote |

Known-price goods: **USD 259.7746 + EUR 6.40, excluding L3**. The extra C32 stock
adds USD 3.22 only after approval. Wire, consumables, missing tools and external
pack/PD items are separate and unpriced. **No firm supplier quotations were
received.** Public prices, cached listings and live indications are distinguished
from allocated stock and delivered quotations throughout the list.

| Supplier combination | Conditional goods comparison | Established shipping | Unresolved costs and feasibility |
|---|---|---|---|
| A: LCSC L2; direct Coilcraft L3 | USD 259.7746 + EUR 19.50, including indicative L3 EUR 13.10 and R32 EUR 6.40 | TME CZK 140 net; DigiKey conditional CZK 0/600 | L3 unallocated; LCSC/Coilcraft/Mouser freight, VAT, import, FX and unselected materials unknown |
| B: L2 and L3 together from Coilcraft | USD 230.1071 + EUR 31.40, including indicative L2+L3 EUR 25.00 and R32 EUR 6.40 | Same conditions | Both five-piece allocations and combined freight unquoted |
| C: LCSC L2; Farnell L3 | USD 259.7746 + EUR 36.45, using historical DE L3 EUR 30.05 and R32 EUR 6.40 | Same conditions | Czech Farnell quote/freight open; old DE backorder 26 February 2027; no timely stock established |

These conditional totals include unusable price indications solely to compare
routes. The usable subtotal remains USD 259.7746 + EUR 6.40 **plus unknown L3**.
Moving L2 removes USD 29.6675 from LCSC and adds EUR 11.90 to Coilcraft. Compare
actual invoice FX and any freight/tax increase against that difference after
allocation. A combined parcel may help, but its freight is not assumed unchanged.
Do not buy filler to reach a shipping threshold. No cheapest delivered route can
be established from the remaining unknowns.

Delivery sources retrieved 19 October 2026:

- [DigiKey Czech delivery](https://www.digikey.cz/en/help-support/delivery-information), last-week cache: UPS prepaid DDP; FedEx/DHL CPT; Marketplace CPT with possible extra freight. Regional basket eligibility must be checked; USD product prices are not converted into a confirmed free-shipping entitlement.
- [TME Czech delivery](https://www.tme.eu/cz/how-to-buy/7328/zpusoby-a-ceny-dopravy/), yesterday cache: the quoted CZK 169.40 gross includes VAT on the CZK 140 shipping charge. COD adds CZK 35 net and is not selected.
- [LCSC import notice](https://www.lcsc.com/help-center/notice/eu-low-value-import-regulations-2026), modified 17 June 2026, yesterday cache: the supplier describes a EUR 3 duty per applicable first-level category for B2C parcels ≤EUR 150 from 1 July 2026, with VAT additional. Supplier classification, declared parcel value, collection and final charges remain unconfirmed. **Do not calculate 66 × EUR 3.**

Unknown freight, tax, import and handling are never zero. Avoid double counting
DDP/prepaid charges. A US tariff notice on a USD product page does not establish
a tariff on the Czech order.

## Exact L3 and L2 supply

| Route | Exact five-piece evidence | Disposition |
|---|---|---|
| Coilcraft Europe / UK | L3 EUR 2.62 each; L2 EUR 2.38 each. Both stock fields blank after selecting quantity five | First combined quote route; price only |
| Farnell cut tape 2289071 | Earlier DE EUR 6.01 each, MOQ 1, backorder 26 February 2027. UK July 2026 date is stale | No current allocation; Czech page inaccessible |
| Farnell 5131621 | Current country listings use full-reel MOQ 250 | Reject for five-piece requirement |
| DigiKey 2457-XAL5050-682MEC-ND | Older search snapshot: 3,944 stock, USD 4.53 each, about four days, USD 10 freight. Newer fetched page: no longer available | Reject stale offer |
| Mouser 994-XAL5050-682MEC | Regional restriction / previous-part-number listing without verified five-piece stock | No executable offer |
| Avnet Silica | Manufacturer lists it as an authorized Czech route; no public exact five-piece offer found | Enquiry route, with no quote or stock claim |

Manufacturer [European sales locations](https://www.coilcraft.com/en-us/contact/saleslocations/europe-and-africa/)
identify authorized routes. Aggregator or broker stock does not prove authorized
allocation. No MRC, XGL, inductance, series or termination substitution is selected.
See the [live lookup record](../evidence/phase5-4-sourcing/LIVE_COILCRAFT_CHECK.md).

**Unsent Coilcraft request:** five XAL5050-682MEC in ordinary loose tape, plus a
combined alternative of five XAL5030-472MEC and five XAL5050-682MEC. Confirm exact
allocatable stock, dispatch or build lead time, MOQ/multiple, EUR net line prices,
Czech prepaid freight, tax/import/handling and combined shipment. No paid leaders
or reeling. Farnell CZ and Avnet are the next authorized enquiry routes.

L2's retained fallback is [LCSC C7432409](https://www.lcsc.com/product-detail/C7432409.html):
five × USD 5.9335 = USD 29.6675, MOQ/multiple 1, three-day cached stock 1,174.
That is stronger supply evidence than an unallocated combined price indication.

## R32 quote and consolidation

Retain exact TE **RN73C1E31K6BTD**, 0402, 31.6 kΩ, 0.1%, 10 ppm/°C,
62.5 mW, 25 V. The
[Mouser 279-RN73C1E31K6BTD EU listing](https://www.mouser.lt/en/ProductDetail/TE-Connectivity-AMP/RN73C1E31K6BTD?qs=sGAEpiMZZMtlubZbdhIBIFl9NVT0tk6Fnfv9LT%252Bs5DY%3D)
has last-month indexed stock 3,207, MOQ/multiple 1, and eight × EUR 0.80 =
**EUR 6.40**. Direct regional fetches failed; this is an indicative supplier
listing, not a Czech firm quotation. Ten × EUR 0.562 = **EUR 5.62** is an optional
cheaper tier. Default order remains eight. Select cut tape, avoiding EUR 5 MouseReel.

Exact DigiKey/TME/LCSC/Farnell small-order supply was not found after exact MPN
and TE alias 1-2176263-2 searches. RQ73, 25 ppm or differently sized parts are not
the requested exact identity. Do not transfer already-priced R33 or other parts
to an unquoted supplier merely to claim consolidation.

**Unsent request:** ask existing DigiKey/TME to source eight, or economically ten,
exact RN73C1E31K6BTD on the existing shipment. Compare their sourcing premium with
Mouser's Czech delivered total. Otherwise the owner chooses a separate exact
Mouser shipment. Earlier AUD/HUF prices are evidence only; no silent USD conversion.

## D2, D3/D4 and the remaining lines

Exact discontinued Dialight **597-3605-607F** still has a
[TME offer](https://www.tme.eu/en/details/597-3605-607f/smd-colour-leds/dialight/)
for eight × USD 0.39 = **USD 3.12**, MOQ/multiple 1, last-week cached stock 2,434.
Keep it on the TME parcel with Q5 and SW1/SW2. Standard 1–2 day transit is an
estimate after dispatch, not a D2 allocation or dispatch guarantee. No substitute
is necessary while exact supply covers eight. If that stock disappears, return
for owner review of a specific blue 0805 LED with matching polarity/protection;
no alternate or redesign is silently approved.

Exact Nexperia **BAS116H,115**, [LCSC C74210](https://www.lcsc.com/de/product-detail/C74210.html),
twenty × USD 0.0669 = **USD 1.338**, MOQ/multiple ten, today-cached stock 55,050
and ships-now text. The German page quotes USD. TME's shortage does not require
a diode substitution.

All 66 electronics and eight exact harness lines have saved refresh attempts.
C26 now advertises ten versus six ordered; C70/C71 170 versus twenty; U6 280
versus six. No priced line uses insufficient advertised stock. C8's English page
shows MOQ/multiple 100, USD 0.0094 and 42,600 stock in a four-month cache,
conflicting with the earlier newer-cache MOQ 50 / USD 0.0133 / 8,450 stock.
The shopping list conservatively plans 100 and flags the conflict. R12, R60,
R33 and some other pages also have older caches; each row retains its actual age.

Optional ten-piece tiers reduce cost for C39, D1, D2, Q5, R6, R12, R23, R60 and R63.
Defaults are preserved; **C63 stays eight and R5 stays ten each**. The separate
PRICE_BREAK_OPTIONS.csv quantifies these optional savings. No new reliability
gate follows from a commercial stock refresh.

**STOP for owner review. No supplier contact, cart, checkout or order.**
