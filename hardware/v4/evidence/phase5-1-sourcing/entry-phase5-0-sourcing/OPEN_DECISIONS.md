# Phase 5.0 — outstanding procurement decisions

2026-10-19. No order is authorized. Approved SW1/SW2, L1, U2, Nano-Fit set,
accepted prototype lands and the completed PCB/stencil order are not reopened.

## Owner choices before an order

1. **Assembly count and spares.** Set N_F0/N_F5 (sum≤5) and accept or trim the
   separately itemized spares.1+1 is a planning example only. Confirm actual
   inventory of exact parts, wire, tools and consumables; historical Bought is
   not evidence of present stock.
2. **Wait for retained parts or review replacements.** Common-board blockers
   are C70/C71's unavailable/obsolete GRM188R71C105KA12D ordering code,
   unconfirmed exact supply of C33/C45's TDK22uF35V part and PMV16UN Q3/Q8/Q9.
   F5 additionally needs U8. Concrete capacitor candidates and the U8 packaging
   option appear below; none is selected in the main purchase BOM. Any electrical
   or footprint-changing replacement needs separate review. No CAD changes are
   part of this proposal.
3. **Harness scope and owned equipment.** Decide which boards need the optional
   J4 service cable, cable lengths, and any missing assembly/crimp equipment.
   The harness CSV gives full-service upper-bound quantities and illustrative
   wire lengths. Existing stencil quantity is zero to purchase.
4. **Battery configuration, separately.** Choose2S1P or4S1P and approve matching
   chemistry/cells, BMS/protection/current/temperature, NTC R25/B/tolerance/thermal
   attachment, fuse/wire and charger profile before any battery purchase or
   construction. F0/F5 does not make this choice. No cell, BMS or NTC is selected.

## Procurement / data work still needed (not additional owner architecture decisions)

| Item | Evidence / exact uncertainty | Concrete next action / option |
|---|---|---|
| U8 LM74700QDBVRQ1 | [LCSC C2941042](https://www.lcsc.com/product-detail/C2941042.html) out of stock; [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/LM74700QDBVRQ1/10434692)0, displayed incoming2026-10-27 is unconfirmed; Mouser cached0; usable TME/Farnell exact offer not established | Recheck exact backorder/date. LM74700QDBVTQ1 is a **not-approved** packaging-only lead with DBV6, not a new8-pin controller. Confirm actual manufacturer/package identity and loose cut-tape terms before owner acceptance. F0 omits it. |
| C33/C45/C64/C65 C3216X5R1V226M160AC | LCSC not available; TME/DigiKey0. TDK lists Production. Current [Farnell2525173](https://uk.farnell.com/tdk/c3216x5r1v226m160ac/cap-22-f-35v-20-x5r-1206/dp/2525173) says Available to Order, deliveries07/05/2027, cut tape min/multiple5; no near-term stock commitment | Quote exact small quantity. Concrete alternative name C3216X5R1V226MTJ00E/LCSC C342620 has matching nominal22uF35V X5R20%1206 and current stock; establish full TDK naming equivalence and bias/package identity before accepting. Do not buy a2000-piece reel to satisfy a prototype. |
| C70/C71 GRM188R71C105KA12D | [DigiKey exact code](https://www.digikey.com/en/products/detail/murata-electronics/GRM188R71C105KA12D/965914) obsolete; LCSC C97890 unavailable. J suffix is also marked obsolete in retained supplier result | Candidate TDK C1608X7R1C105K080AC/LCSC C2167399,1uF16V X7R10%0603: supplier package/ratings verified, primary page retrieval incomplete. Finish manufacturer comparison and obtain replacement approval; main BOM retains original. |
| Q3/Q8/Q9 PMV16UN | Accepted core type is known. Provisional215 suffix has legacy NXP DigiKey obsolete flag; Mouser Nexperia771-PMV16UN215 says EOL and region restriction. Current Nexperia core page does not establish stock | Seek exact traceable Nexperia/legacy stock with confirmed ordering identity, or propose a separately checked same-pad MOSFET. No unreviewed replacement has been selected. No assertion of worldwide absence. |
| TP1/TP3/TP4 | Real fitted loop/bead hardware, generic1.8mm loop/1.0mm drill; no exact manufacturer MPN proven | Verify a physical sample or manufacturer drawing against accepted lead/body envelope. Keystone5000/Vero20-313137 are investigation leads, not confirmed drop-ins; their1.02mm-hole recommendation is not silently waived. Preserve all3 fitted counts. |
| C32/C35/C36 conditional passive proposals | Exact nominal grade/package known; no exported manufacturer DC-bias curve/combined Ceff bound | Complete curve review at actual operating voltages and retained design assumptions. C35 retains AP7361C2.2uF effective output minimum; no new C32 threshold invented. Same-package proposals remain conditional; report a blocker if evidence requires a different package. |
| Exact quote gaps | MASTER_PURCHASING_BOM.csv explicitly leaves unavailable stock, MOQ, multiple, price and extended costs blank; source URLs are retained where known. Smaller gaps include ordinary resistors/caps/diodes, R32/R33 cut tape, L1 price, paste/wire/tools | Get exact supplier quotations and confirm stock at order time. These are commercial tasks, not reasons to change PCB or waive electrical compatibility. Coilcraft Europe must confirm L2/L3 stock, exact MEC fulfillment, freight/import/VAT. |
| Delivered price | LCSC freight/handling/customs categories, Coilcraft delivery, local supplier VAT and actual checkout totals unknown | Compare the delivered strategies in SUPPLIER_BASKETS.md after exact quotations. No shipping consolidation with the already-submitted JLCPCB order is assumed. |

The remaining hardware qualification (hot-plug, thermal, back-power, pack and
assembly yield) is retained project work, not a new selection request or a claim
that passing ERC/DRC establishes electrical performance. Procurement preparation
does not authorize powering a prototype.
