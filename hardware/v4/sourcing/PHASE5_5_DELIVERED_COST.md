# Phase 5.5 — goods and delivered-cost budget

Quick start: budget **USD256.3480 net goods**, plus the actual LCSC freight,
VAT/import/handling and TME delivery. This includes all78 proposal rows:
74 original component/harness rows, optional C32 comparison stock and wire.
There is no firm delivered quotation and no supplier cart or reservation.

| Goods | USD net | Evidence level |
|---|---:|---|
| LCSC71 lines |231.0980|Live public USD product pages20Oct2026; not a quote|
| TME3 original electronics lines |6.9200|Dated Phase5.4 cache|
| Optional exact TDK C32 x10 |3.1000|20Oct retrieval,today cache;0.31 tier10|
| TME red/black wire5m each |9.2500|4-month cached regional pages;0.92/0.93 per metre|
| TME signal wire2x10m rolls |5.9800|3-week cache;2.99/roll|
| **TME total7 lines** |**25.2500**|Live TME blocked/unavailable; Czech/account pricing unconfirmed|
| **All goods** |**256.3480**|Public allowances, not confirmed invoice cost|
| Goods excluding optional TDK C32 |253.2480|Other quantities unchanged|

Every extension uses its actual purchase tier and MOQ/multiple. R33 ten pieces
cost less in total than eight. R5 MOQ100 creates extra stock but costs only
USD0.22–0.29/profile. No artificial purchases to meet a shipping threshold.
L2/L3 now total USD14.1980 versus the retained LCSC exact L2 fallback alone
USD29.6675; an additional Coilcraft shipment is avoided. L1 exact LCSC0.7087
also beats its cached TME0.78 allowance. This optimizes these practical routes;
it is not an exhaustive global supplier price optimum.

## Freight, VAT and import

| Item | Confirmed public rule / amount | Unknown |
|---|---|---|
| TME standard CZ shipment≤20kg |CZK140 net /169.40 incl21%VAT|Actual basket weight/service/account adjustment;1–2 working days is transit after dispatch|
| LCSC China→CZ freight |No price established|Carrier,weight,shipping method,DDP/DAP,consolidation and final quote|
| Czech VAT |21% standard planning rate; import base includes goods+freight+applicable duty|Actual invoice/FX/tax collection mechanism|
| LCSC import duty |Cannot assume zero|HS/TARIC classification,customs value and duty by product category|
| Clearance/carrier fees |Not quoted|Carrier/broker handling;DDP prepaid amounts if offered|
| FX and payment |All goods observed in USD|Final TME currency/account price,card FX/spread|
| Owner finishing materials |Existing/local consumables or later TME additions|Labels/ties/heatshrink and external-pack mate if required; not silently zero|

The old blanket assumption “under EUR150 means duty free” is obsolete for an
October2026 order. EU rules introduced temporary EUR3 duty per product category
for qualifying low-value consignments from1Jul2026. It is not EUR3 per component
or automatically per shopping-list row. The LCSC goods amountUSD231.098 will
exceed EUR150 at any USD/EUR conversion above0.6491EUR/USD. Above that threshold,
the normal tariff route applies; category-specific duties still need the actual
customs declaration. Do not split orders merely to assume a cheaper duty regime.

Sources: [TME Czech transport](https://www.tme.eu/cz/how-to-buy/7328/zpusoby-a-ceny-dopravy/),
[European Commission29Jun2026](https://commission.europa.eu/news-and-media/news/ensuring-fairness-and-safety-eur3-customs-duty-low-value-parcels-2026-06-29_en),
[Council small-parcel policy](https://www.consilium.europa.eu/en/policies/eu-action-influx-of-small-parcels/),
[Czech Customs VAT basis](https://celnisprava.gov.cz/cz/faq/Stranky/neobchodmi-zasilka.aspx).
Only the VAT-base rule is reused from the older customs FAQ; its former duty
exemption must not override the2026 EU changes. Full source responses are saved
under Phase5.5 evidence(research54/58/60).

## Explicit scenarios, not freight quotations

Let F be actual LCSC freight USD, D applicable import duty USD, H handling CZK,
K owner consumables CZK, and r final CZK/USD conversion. For an ordinary
non-prepaid import with the assumed21% VAT treatment:

`delivered CZK ≈ (256.3480 + F + D) × 1.21 × r + 169.40 + H + K`

TME goods are included at net USD allowances and receive VAT in this formula;
TME delivery169.40 is already gross. Adjust for actual TME currency conversion.
If LCSC offers tax/duty-paid freight, reconcile the prepaid lines rather than
adding tax/duty twice. H and K are their final payable amounts.

For **illustrative** r=22CZK/USD, with duty/handling/consumables left outside:

| Assumed LCSC freight | Goods+assumed freight+21%VAT | Plus TME gross delivery | Outstanding additions |
|---|---:|---:|---|
| USD10 |USD322.2811|CZK7,259.58|+26.62×D+H+K CZK|
| USD25 |USD340.4311|CZK7,658.88|+26.62×D+H+K CZK|
| USD40 |USD358.5811|CZK8,058.18|+26.62×D+H+K CZK|

These are conditional budgets, **not a confirmed delivered range or upper
bound**. Freight and FX values are explicit assumptions, not verified quotes.
No unknown cost is represented as zero in the final delivered total.

**STOP for approval of identities and baskets. Final checkout totals remain
unknown until the owner requests/opens actual supplier order quotations.**
