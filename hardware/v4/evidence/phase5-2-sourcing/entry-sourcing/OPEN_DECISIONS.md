# Phase5.1 — remaining purchasing holds

2026-10-19. All five boards are funded in quantities as F5:0F0+5F5. That decision,
5×BQ25798RQMR,30R5 option-stock pieces, accepted exceptional SYS reset, deferred
external PD converter and deferred3S firmware are **closed scope decisions**.
No purchase authorization is implied. Battery configuration is not needed to buy
the shared PCBA parts and all three R5 options.

Quick start: review the exact candidates below, then complete the supplier quotes.
[Compatibility evidence](PHASE5_1_COMPATIBILITY_REVIEW.md) gives the manufacturer
sources, actual footprints, limitations and recommended options.

## Owner selection review

| Item | Recommended decision / exact option | What is established / what remains |
|---|---|---|
| U8 | Accept TI LM74700QDBVTQ1 as the same-device DBV6 tape-ordering/finish option | Exact TI ordering/package/pin map verified; LCSC C2653623 displayed2394,6piecesUSD16.29. Original R code unavailable. Candidate held outside approved basket |
| C70/C71 | Accept TDK C1608X7R1C105K080AC | Production,1uF16VX7R10%,actual0603 overlap and3.3V bypass role checked. LCSC C2167399 displayed170,20piecesUSD1.102. Original Murata code obsolete |
| Q3/Q8/Q9 | Review AO3400A as sourced replacement for EOL PMV16UN | Static low-current3.3V operation,30V/G1S2D3/SOT23 pad overlap checked; LCSC C20917,20piecesUSD1.96. Different gate charge/hot leakage remain prototype timing considerations. PMV16XN is another manufacturer-Production candidate but has no verified small-order source |
| Other proposed exact identities | Accept/reject the documented Phase5.0 ordinary-passive and precision-part proposals as a coherent list | Phase5.1 review did not explicitly approve every Phase5.0 PROPOSED MPN. R5 values/package/10each are owner-approved; exact Yageo CT ordering codes are proposed. C35/C36 now have typical bias evidence and explicit screening assumptions; acknowledge their limits before accepting those exact MPNs |

These choices require owner acceptance because they select exact procurement
identities beyond the explicit accepted set. No candidate has been promoted to
the approved purchasing basket. Owner review cannot replace missing technical
evidence listed next.

## Evidence/procurement blockers to close

| Item | Exact unresolved requirement | Recommended next step |
|---|---|---|
| C33/C45/C64/C65 | TDK catalog C3216X5R1V226M160AC vs LCSC C3216X5R1V226MTJ00E full-suffix equivalence; Ceff at3.3/5V incl required F5 pair bound | Obtain full manufacturer/supplier standard-spec mapping and DC-bias data. Official wildcard family alone is insufficient. Candidate C34262030piecesUSD10.926; do not accept based solely on nominal value. Original exact catalog small-order stock remains unquoted |
| C32 | Proposed Yageo2.2uF50V loses about75% at18V; existing SYS/input network has no captured adequate Ceff/ripple justification | Hold C32 exact proposal; establish the required local input-network bound with existing C21/C43 and operating range, or validate a same-value/footprint low-bias alternative. No value/footprint/copper/architecture change authorized |
| TP1/TP3/TP4 | No exact documented loop hardware fit for1.00mm finished holes;15fit+1spare | Source compatible1.00mm hardware or present a concrete hand-formed tinned loop assembly proposal. Common1.02mm-hole Vero/Keystone parts are not guaranteed fits. Do not drill/force-fit or omit references |
| L2/L3 | Exact XAL5030-472MEC/XAL5050-682MEC5each, current stock and small-order delivered price | Compare combined Coilcraft Europe quote(no minimum generally) with Farnell cut tape2289069/2289071. Reject full-reel MOQ400 and unavailable old Marketplace listing. No suffix substitution |
| Remaining commercial fields |19master lines lack a usable extended price;15unknown MOQ/multiple-derived order quantities, plus shipment tax/handling/FX and cached-stock refresh | Use complete quote register in SUPPLIER_BASKETS.md and desired quantities in master. Each blank is unknown, not zero. Complete LCSC shipping/duty/VAT and Coilcraft or Farnell delivered quotes before deciding cheapest consolidated basket |

## Harness/assembly details needed before ordering those separate materials

Confirm actual cable lengths, enclosure strain relief and Nano-Fit20AWG insulation
OD/contact crimp range; illustrative5mred/5mblack and11msignal wire include spares.
Confirm XT30 mating contact gender/polarity against the eventual battery assembly.
Confirm owned tools and consumables, exact paste/flux lot/storage/process and crimp
tools before buying replacements. Historical Bought fields prove no current stock.
The20power-harness connector set and40+10tin contacts are not reduced for a smaller
initial build. JST mate/contact quantities cover all five boards.

Cells,2S/3S/4S BMS,NTC and programmed charging profile remain separate future
matching decisions, not extra PCBA approval gates. No pack,PD converter,firmware
profile or additional protection circuitry selected. **STOP for owner review.**
