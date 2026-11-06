# Phase5.1 sourcing summary — five F5 purchase capacity

Quick start: read [open decisions](OPEN_DECISIONS.md), review the
[master BOM](MASTER_PURCHASING_BOM.csv) and [supplier baskets](SUPPLIER_BASKETS.md).
This is procurement preparation; **STOP for owner review before purchasing**.

- **67 purchasing planning lines**, covering 65 reference groups plus two additional
  R5 profile stock lines. Five F5 boards require **670 fitted parts**. Counts 115 F0 / 
  134 F5 and 19 F5-only preserved; four DNP and16 PCB-only refs excluded.
- **5×TI BQ25798RQMR**, LCSC C2876593, displayed 2913 on2026-10-19;
  5×USD2.8576=**USD14.2880**, MOQ/multiple1. Owned BQ25792 is separate inventory.
- R5: **10 each: 8.2 kΩ / 13.7 kΩ / 27 kΩ, 0805, 1%**,750 kHz. DigiKey exact Yageo CT codes
  proposed, indicative USD 0.34 per10/totalUSD 1.02. Cached stock ages 5 days–2 months
  are explicit. Thirty purchased resistors represent **five positions**, not 30 fitted parts.
- Priced/indicative PCBA subtotal **USD193.50** with **19 unpriced lines**;
  partial fitted F0/F5 **USD28.09/USD34.81**.
  This excludes unknown parts/tax/freight/handling. Separate priced harness portion
  **USD16.75**; combined incomplete allowance **USD210.25**.
- Four held priced candidates would add USD 30.28, taking the conditional PCBA
  allowance to USD 223.78, still15 unpriced lines. They remain excluded from
  the accepted basket. **No complete delivered total can yet be quoted.**
- Preferred split: LCSC 36 lines / TME 11 / DigiKey 14 / 
  Coilcraft 2, plus 4 unresolved-supply groups. Recommended
  consolidation quote target: LCSC+DigiKey+Coilcraft or Farnell; transfer exact TME
  parts only if delivered savings are demonstrated. TME Czech standard shipment
  CZK 169.40 gross; DigiKey free at CZK 1800, otherwise CZK 600. Other freight/import costs unknown.

U8 DBVTQ1 is an available, verified package-ordering option awaiting owner acceptance.
C70/C71 TDK in-production nominal/package candidate also awaits acceptance.
PMV16UN is EOL; AO3400A is a sourced static/package candidate, PMV16XN has no verified
small-order source. C33/45/64/65 exact TDK suffix equivalence and Ceff remain open.
TP1/3/4 exact hardware remains open:1.00 mm PCB drill versus1.02 mm recommended holes
for common beaded parts. Do not force-fit or enlarge ordered boards.

Bias evidence is now saved: C35/C36 roughly 12–14 µF typical at 3.3 V; an explicitly
assumed conservative screen gives 4.71 µF, above C35's 2.2 µF floor, not a guaranteed
combined manufacturer bound. C32 proposed 2.2 µF falls to roughly 0.5–0.6 µF typical
at 18 V; hold its selection pending a justified input-network requirement or a
qualified same-footprint part. See [compatibility review](PHASE5_1_COMPATIBILITY_REVIEW.md).

Harness capacity: 20 Nano-Fit power harnesses, 40 tin power contacts + 10 trial spares;
5 each exact mating housing+1spare (MOQ excess separate);5 J4/J6 cable pairs and
40 JST contacts + 10 spares (MOQ 100 creates 50 excess). Illustrative 5 m red + 5 m black 20 AWG,
11 m signal wire include spares; lengths/OD/tool ownership still need confirmation.
Battery cells, 2S/3S/4S BMS and NTC remain separate decisions. SYS reset on exceptional
pack disconnection is accepted; no architecture changes. External SYS PD converter
and 3S firmware are deferred. No battery configuration selected.

Only 10 explicitly accepted exact/dated-quoted lines are in
APPROVED_PURCHASING_BASKET.csv; all selection/quote holds remain visible elsewhere.
No order/cart/CAD/firmware/manufacturing/commit/push. Protected 196 files unchanged;
full population/group/owner-quantity checks pass in
[consistency evidence](../evidence/phase5-1-sourcing/consistency.json).
