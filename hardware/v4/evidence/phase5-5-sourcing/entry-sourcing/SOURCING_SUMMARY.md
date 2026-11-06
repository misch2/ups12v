# Phase 5.4 — final sourcing and purchasing preparation

Quick start:

1. Review [supplier shopping list](SUPPLIER_BASKETS.md) or [full CSV](SHOPPING_LIST_BY_SUPPLIER.csv).
2. Review [remaining decisions](OPEN_DECISIONS.md) and [supplier combinations](PHASE5_4_COMMERCIAL_REVIEW.md).
3. Approve or decline the separate [C32 comparison stock](PHASE5_4_C32_COMPARISON.md).
4. Close exact L3 stock/dispatch and Czech supplier charges before placing orders yourself.

Five F5 capacity is unchanged: **655 assembled parts and 66 electronics planning lines**, plus a possible 67th C32 stock line. IC1 is exactly five BQ25798RQMR; R5 is ten pieces each for 2S/3S/4S. No TP hardware or always-DNP purchases.

Owner approvals applied: C32 Yageo ×10, mapped TDK output capacitors ×30 and C63 Yageo ×8. The TDK bank's original 25 µF basis remains unguaranteed; accepted prototype limitations stay in bring-up documentation and do not block these purchases.

All 66 electronics and eight exact harness lines had public-page refresh attempts. Sixty-four electronics lines have USD allowances; R32 has a dated EU EUR allowance; L3 remains without an allocatable offer. Cache ages are explicit. C8 has conflicting MOQ observations; the list conservatively requests 100 from the visible MOQ 100 offer.

Partial electronics goods: **USD 243.0236 + EUR 6.40**, excluding L3. Separate exact harness: **USD 16.7510**. Combined known-price goods: **USD 259.7746 + EUR 6.40**, plus unpriced L3, freight, VAT/import, FX and unselected materials. The 18 approved USD rows total USD 111.8189; this is an incomplete subset, not an order release. The extra C32 stock adds USD 3.22 only after approval.

L3: direct Coilcraft UK shows EUR 13.10 / 5 arithmetic but blank stock. Combined L2+L3 EUR 25.00 is indicative and unallocated. Farnell is a dated backorder lead; DigiKey Marketplace's newer unavailable page overrides its older stock/price snapshot. R32: exact Mouser eight × EUR 0.80 = EUR 6.40 from a Lithuania cached listing. Czech delivered quote and consolidation remain open; no exact existing-supplier small-order offer was verified.

Independent checks passed counts, prices, approvals, 196 protected CAD/library/manufacturing hashes and preservation of the unrelated config. No CAD, native KiCad, ERC/DRC rerun, manufacturing, firmware, hardware power-up, cart, supplier contact, order, checkout, commit or push. **STOP for owner review.**
