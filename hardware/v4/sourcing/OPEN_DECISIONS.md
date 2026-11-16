# Phase 5.4 — owner review before purchasing

Quick start: review [the shopping list](SUPPLIER_BASKETS.md), decide on the extra
C32 stock and remaining proposed identities, then close supplier delivery gaps.

## 1. Parts ready for owner review and purchase preparation

All previous approvals remain valid. These new purchasing approvals are applied:

| References | Approved purchase |
|---|---|
| C33/C45/C64/C65 | TDK C3216X5R1V226MTJ00E, LCSC C342620, 30 pieces; prototype |
| C63 | Yageo CC0603KRX7R9BB333, 8 pieces |
| C32 | Yageo CC0805KKX7R9BB225, LCSC C125847, 10 pieces; prototype |

The accepted DC-bias limitations remain documented for bring-up. The original
25 µF bank basis is **not guaranteed**. No new purchasing qualification gate is
introduced. Five BQ25798RQMR, ten of each R5 profile, 655 assembled parts,
66 electronics planning lines and zero TP/always-DNP purchases are preserved.

There are 64 electronics lines with USD price allowances and eight exact harness
lines with USD allowances. Eighteen electronics lines have explicit approval of
their exact identities. The other 48 retain their previous selection statuses;
review them together in [EXACT_IDENTITIES_FOR_OWNER_REVIEW.csv](EXACT_IDENTITIES_FOR_OWNER_REVIEW.csv).
This list includes L2/L3/R32 and the proposed exact Yageo R5 identities. Approval
of R5 values, grades and quantities is preserved; it does not invent an approval
of every proposed manufacturer identity. No accepted architecture is reopened.

## 2. Exact final decisions and supplier gaps

| Item | Concrete choice or unresolved fact |
|---|---|
| Extra C32 stock | Approve or decline **10 TDK C2012X7R1H225K125AC**, DigiKey 445-5968-1-ND, **USD 3.22 goods**. Same 2.2 µF/50 V/X7R/0805 body; about 1.19 µF typical at 18 V versus Yageo's 0.5–0.6 µF. Separate stock only; approval pending. [Comparison](PHASE5_4_C32_COMPARISON.md) |
| L3 | No allocatable five-piece offer established. Request exact XAL5050-682MEC ×5 from Coilcraft Europe, Farnell CZ or Avnet: price, allocation, dispatch/build lead time, freight and tax collection. No substitute selected |
| L2 supplier | Retain LCSC C7432409 ×5 / USD 29.6675 until a combined Coilcraft offer is confirmed. Combined L2+L3 goods indication is EUR 25.00; allocation and freight remain open |
| R32 supplier | Exact Mouser 279-RN73C1E31K6BTD ×8 / EUR 6.40 dated EU allowance; optional ten-piece tier EUR 5.62. Prefer sourcing through existing DigiKey/TME shipment if possible. Czech delivered quote and acceptance of an extra Mouser parcel remain open |
| Remaining exact identities | Review the 48 existing proposed/retained lines as one batch; no automatic substitutions or new audit |
| Purchase | Owner reviews final Czech stock, shipping, taxes and FX. No firm quotations or stock reservations were obtained |

D2's exact discontinued Dialight part still has a dated TME offer for 2,434
pieces, covering the requested eight. D3/D4's exact LCSC offer covers twenty.
Neither needs a new engineering review while exact supply remains available.

## 3. External and deferred items

External cells/BMS, pack NTC and configuration, the external PD converter and
firmware remain deferred. Final wire lengths/MPNs, conditional XT30 mate,
heat-shrink, labels, paste/flux/solder and missing tools remain separate. Check
owner inventory before buying. The already ordered PCB/stencil is not reordered.
Unquoted costs are unknown, never zero. See
[DEFERRED_AND_OWNER_INVENTORY.csv](DEFERRED_AND_OWNER_INVENTORY.csv).

**STOP for owner review. No order, checkout, supplier message, CAD, manufacturing,
firmware, power-up, Git commit/push or branch checkout.**
