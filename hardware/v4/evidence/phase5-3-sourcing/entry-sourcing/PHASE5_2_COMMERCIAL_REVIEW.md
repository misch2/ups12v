# Phase5.2 — commercial evidence, missing quotes and Czech delivery

2026-10-19. Quick start: use SUPPLIER_BASKETS.md and the grouped CSV for quantities.
All67master lines were refreshed or their exact-source lookup attempted. Eight
exact harness/contact identities were also refreshed. Raw responses remain under
evidence/phase5-2-sourcing; supplier cache dates are recorded per observation.
No page observation is reserved inventory or an executable delivered quote.
No cart, checkout, RFQ transmission, order or supplier message was created.

## Remaining missing/insufficient offers

| Refs / exact identity | Request with spares | Current result and remaining quote |
|---|---:|---|
| C8 GCM1555C1H102JA16D, LCSC C437434 | 5fit+3spares=8 |4-month cached42,600 and first100+USD0.0094; explicit MOQ/multiple absent. Do not infer100 MOQ solely from first price tier. Need small-order terms and refreshed price/stock |
| C33/C45/C64/C65 C3216X5R1V226M160AC |20fit+1spare=21 |TME stock0;10+tierUSD0.44 is unavailable reference price, excluded from usable total. LCSC C342620 TJ00E30piecesUSD10.926 remains held for manufacturer identity and Ceff, not a quote for retained identity |
| C63 GRM188R71H333KA61D |5+3=8 |TME/retained source incomplete; DigiKey exact product702550 located but no usable exact cut-tape quote. Need SKU/stock/MOQ/price; substitute rows are not stock of C63 |
| L1 DR125-2R2-R |5, no spare |TME current commercial fields unavailable; LCSC C5337632 identity only, without usable stock/MOQ/price. Owner-approved MPN, not an approved available offer |
| Q3/Q8/Q9 PMV16UN,215 |15+1=16 |EOL original no trusted stock. Conditional AO3400A C20917 order20USD1.96 or PMV16XNR C110920 order20USD2.988; owner selection still required, alternatives never both ordered |
| R6 RC0805FR-075K6L |5+3=8 |TME cached1906 and conflicting6/8-month cachedUSD0.06/0.11 one-piece observations. Current parser chooses the saved6-month source; explicit MOQ absent. Reconfirm actual small-order terms; price is indicative |
| R12 CRCW12062R00JNEAHP |5+1=6 |DigiKey CT541-2.0UACT-ND established. Refreshed USD page1.2years cached9131 has no price/MOQ. Prior verified10Oct2026quote7.47CZKnet/pc,6=44.82CZK is indicative, outside USD total. Need fresh Czech price/terms |
| R23 RC0402FR-078K2L |5+3=8 |TME2-month cached9270/USD0.04 but explicit minimum absent; confirm MOQ/packaging |
| R32 RN73C1E31K6BTD |5+3=8 |Exact TE identity; direct regional refresh unavailable/unpriced. Need exact cut-tape SKU/stock/MOQ/price |
| TP1/TP3/TP4 loop proposal |15fit+1spare |Exact hardware realization not owner-selected. Proposed0.5m0.30mm tinned copper requires supplier SKU, overall-diameter tolerance, quantity/price. No fictitious catalog MPN |
| D3/D4 BAS116H,115, TME BAS116H.115 |10fit+1spare=11 |Today-cached stock3 is insufficient.11×USD0.12=USD1.32 is a line-price allowance only; restock or another exact source required. Not order-ready |
| L3 XAL5050-682MEC |5, no spare |DirectUSD3.02 is indicative; exact available stock and lead time not established. Farnell2289071 cut tape has no Czech quote. Swiss cached26Feb2027 delivery is not a Czech commitment |

For all other rows, master/checklist records the exact manufacturer identity,
distributor SKU where established, displayed stock, MOQ/multiple, standard
packaging, selected price tier, rounded request, spares/excess and direct URL.
Most prices are cachedUSD regional observations, not tax-inclusive Czech quotes.
Missing fields remain blank/unknown. Owner approval of a value/package does not
approve every exact Phase5.0 passive MPN. R5 remains10each as requested; confirmed
DigiKey cut tape MOQ/multiple1 avoids LCSC's unnecessary100-piece resistor packs.
No Digi-Reel service or extra reeling fee is selected.

D2 **597-3605-607F** is [discontinued by Dialight](https://www.dialightsignalsandcomponents.com/597-smd-led-0805pkg-blue-w-zener-lc-2ma-7-reel/).
The exact [TME page](https://www.tme.eu/en/details/597-3605-607f/smd-colour-leds/dialight/)
retrieved today has last-week cached2434, MOQ/multiple1, USD0.39 at1; requested
8=5fit+3spares, USD3.12. This is an available last-stock proposal, not evidence of
active manufacture. No LED replacement or CAD change is selected.

## L2/L3 procurement strategy

L2 exact [LCSC C7432409](https://www.lcsc.com/product-detail/C7432409.html)
is now a useful small-order fallback:3-day cache1174, MOQ/multiple1,
5×USD5.9335=USD29.6675. Standard reel400does not require purchasing400.
Coilcraft direct5L2=USD13.70 and5L3=USD15.10 remain indications pending actual
UK availability/configuration and delivered quote. Generic “in stock” text and
“configuration not available” coexist in the static pages; no stock claim is made.
Europe's no-minimum policy establishes that five is a supported order size in
principle, not that these ten parts are available.

Farnell2289069/2289071 are exact cut-tape options. A Danish L2 last-month stock
observation2374 is not a Czech allocation. Full reels5131620MOQ400 and5131621MOQ250
are excluded. The old DigiKey Marketplace L3 remains unavailable. No suffix,
inductance or footprint substitution is proposed.

## Delivered strategies for the Czech Republic

| Strategy | Allocation | Practical comparison / remaining unknowns |
|---|---|---|
| A: preferred sources with exact fallbacks |LCSC main electronics+L2; TME small set; DigiKey headers/precision/R5; Coilcraft L3 |Four supplier shipments and incomplete supply. TME standard≤20kg140CZKnet/169.40gross; DigiKey600CZKbelow1800CZK, free at/above1800CZK. LCSC and UK freight/tax/handling unknown |
| B: three-shipment target |LCSC +DigiKey including remaining exact TME lines +Coilcraft combined5L2/5L3 |Avoid TME169.40CZKgross only if transfer premiums after FX/tax are smaller. Direct L2 indication isUSD15.9675lower than LCSC line, but requires confirmed stock and combined freight; no executable saving claimed |
| C: EU cut-tape consolidation |LCSC +DigiKey +Farnell2289069/2289071 with eligible exact TME lines |Could avoid UK-direct shipment. Czech exact stock/lead time, small-order line prices and Farnell freight absent; regional backorder date does not close this strategy |

Preferred next quote work: combined exact-MEC Coilcraft Europe and Farnell Czech
cut tape, then exact TME-to-DigiKey transfers. Compare each incremental premium
with avoided shipment fees; do not purchase unwanted components just to reach
a free-shipping threshold. If L3 still requires a separate supplier, moving L2
to LCSC does not by itself save that shipment. Existing JLCPCB order was already
submitted; do not assume it can absorb an LCSC parcel. No fully supplied cheapest
delivered strategy is established.

Sources refreshed19October2026: [TME Czech transport](https://www.tme.eu/cz/how-to-buy/7328/zpusoby-a-ceny-dopravy/)
(cache yesterday), [DigiKey Czech delivery](https://www.digikey.cz/cs/help-support/delivery-information)
(cache3months), [Coilcraft Europe](https://www.coilcraft.com/en-us/contact/saleslocations/europe-and-africa/)
(cache today). TME/DigiKey transit indications are not guaranteed arrival dates.
DigiKey UPS DDP versus other carrier terms must be chosen in the eventual quote.
LCSC freight/method/transit, VAT collection, import duty/brokerage, UK incoterms
and card/FX fees remain unknown. No assumption of zero tax/duty or customs-law
determination is included. USD andCZK figures are never summed without FX.

## Separate harness and assembly materials

H01–H08 pages were refreshed and exact connector/contact cached terms retained
in HARNESS_AND_ASSEMBLY_BOM.csv.20power harnesses require40Nano-Fit contacts
+10trial/rework spares. JST40fit+10spares rounds to100with50MOQ excess.
H08 SXH-001T-P0.6 remains a proposed exact contact, not owner-approved by its
commercial refresh. Confirm20AWG insulation OD/crimp range and lengths,
XT30 contact gender/polarity, strain relief, paste/flux/process and owned tools.
Unselected wire/XT30/consumables/tools have no exact SKU quote; their blank prices
are not zero. Historical Bought never proves current owner stock.
Battery/BMS/NTC-pack decisions and externalPD converter remain separate/out of scope.

## Unsent quote/confirmation requests

No supplier has been contacted. The next concrete requests are:

1. Coilcraft Europe:5 XAL5030-472MEC +5 XAL5050-682MEC; exact configuration,
   available allocation, dispatch date/lead time, small-order packaging, currency,
   Czech delivery freight, incoterms and all handling/tax collection.
2. Farnell Czech: same5+5 under2289069/2289071 plain cut tape; same delivered fields,
   no full-reel or re-reeling substitution.
3. TDK technical: controlled full-code mapping160AC↔TJ00E, mechanical/terminal
   drawing and electrical/bias construction identity, minC under3.3/5V across
   tolerance/temp/aging/actual smallAC, ripple self-heating. Explain the retained
   25µFpair basis; a wildcard family statement is insufficient.
4. Exact distributor quotes for the missing/short rows in the table, followed by
   LCSC Czech shipment quote for the reviewed basket and a DigiKey transfer quote.

**STOP for owner review. Purchases remain unauthorized.**
