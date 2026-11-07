# Phase 4.19 bounded sourcing observations

Retrieved2026-10-18. Page observations only, not reserved inventory, a complete
shopping basket, replacement approval or an order. CurrencyUSD; tax/shipping
and total small-order economics not quoted. Old BOM entries remain unchanged
under the explicit read-only authorization. Recheck at purchase time.

| Ref / exact item | Primary supplier page observation | Release relevance |
| --- | --- | --- |
| U3/U7 TPS62933DRLR | [LCSC C3200405](https://www.lcsc.com/product-detail/C3200405.html): page reports22,018in stock, MOQ/multiple1,1-pieceUSD0.5134; SOT583 listing. | No observed small-order stock blocker for this exact SKU in the retrieved snapshot. It does not qualify electrical claims or assembly. |
| U8 LM74700QDBVRQ1 | [LCSC C2941042](https://www.lcsc.com/product-detail/C2941042.html): **Out of Stock**, MOQ/multiple1,USD2.4767 explicitly reference only. | Concrete F5 assembly sourcing blocker at this preferred supplier; no substitute selected. A TME exact listing was not established by the bounded search, which does not prove absence. |
| J7 GCT USB4085-GF-A | [LCSC C7095263](https://www.lcsc.com/product-detail/C7095263.html): page reports1,678in stock, MOQ/multiple1,1-pieceUSD1.4204; THT listing. | Exact approved item remains listed. Older search snippets gave different stock/prices and were not used as the observation. |
| L3 Coilcraft XAL5050-682MEC | [Manufacturer exact product](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal50xx/xal5050-682/) found; bounded TME/LCSC exact searches did not establish a supplier basket. [DigiKey exact listing](https://www.digikey.com/en/products/detail/coilcraft/XAL5050-682MEC/21381690) exists, with current price/MOQ/stock not verified. | Prefer TME/LCSC if practical; a nonpreferred source is reasonable if exact preferred supply remains unavailable. Approve the basket/ship cost; do not silently substitute footprint/inductance. |
| J1/J2/J3/J8 Nano-Fit set; mate housings/1053002100 contacts | Preserve exact owner-approved part/key/color/pin mapping in [existing selection](../nanofit-connector-selection.md). Current TME/LCSC quantities and complete harness basket not established here. | Existing `Bought` values are not proof that the newly selected Molex set is owned. Finished tolerance,20AWG wire/crimp/current and housing compatibility require explicit assembly disposition. |
| R60–R63 / open common passives, protection parts, pack/NTC | Exact open items are identified in [independent review](INDEPENDENT_REVIEW.md), unchanged BOM and [population export](population.json). | Freeze exact value/tolerance/voltage/package identities before assembly; resolve anything requiring a footprint change before fabrication. No new selection is made. |

The [DigiKey LM74700 exact listing](https://www.digikey.com/en/products/detail/texas-instruments/LM74700QDBVRQ1/10434692)
search snapshot also showed zero stock and an expected2026-10-27 delivery; it
was not independently refreshed to confirm an arrival date and is **not** a
procurement commitment. No assertion of worldwide shortage or all-supplier
unavailability is made. F0 omits U8; this does not remove any approved F5 profile.

No component was selected solely for an assembly library. Preferred sourcing
remains TME.eu/LCSC.com with hand assembly; price/MOQ/shipping must be considered
for the actual combined small order.
