# Phase5.3 — owner review before purchases

2026-10-19. Quick start: review the two prototype dispositions and remaining
commercial items against SUPPLIER_BASKETS.md. No purchase is authorized.

## Closed owner decisions — do not reopen

- Purchase capacity0F0+5F5; exactly5TI BQ25798RQMR/C2876593; R5exactly10each
  8.2k/13.7k/27k0805/1%, with one mutually exclusive position per board.
- U8TI LM74700QDBVTQ1/C2653623 and C70/C71TDK C1608X7R1C105K080AC/C2167399.
- Q3/Q8/Q9 **AO3400A/C20917,20pieces APPROVED**. Purchasing-only replacement
  of obsoletePMV16UN; existingSOT-23 and documented prototype checks retained.
- C35/C36 **MurataGRM21BR61E226ME44L APPROVED FOR PROTOTYPE**. Purchase15,
  10fit+3spare+2MOQ excess. KnownCeff uncertainty accepted; no guarantee or
  completed hardware qualification claimed.
- **No TP1/TP3/TP4hardware required**. Zero purchase/spare/fabrication requirement.
  Existing pads/holes suffice; optional loops already owned. Actualassembly655
  =670historicalCADpositions−15optionalTPloops. AllCAD/manufacturing unchanged.
- Four always-DNP capacitors buy zero. Accepted architecture and exceptionalSYS
  reset remain closed. External cells/BMS/PD converter and firmware remain excluded.

## Concrete purchasing proposals for owner review

| Item | Recommended practical disposition | Evidence limit |
|---|---|---|
| C32 |Accept retainedYAGEO CC0805KKX7R9BB225/C125847 for prototype;10pieces,USD1.39 |Known0.5–0.6µFtyp at18V; idealC32-only0.50–0.60Vpp screening at1A/500kHz. Actualnetwork later measured under approved requirements. No inventedCmin, ideal addition of remoteC21, guarantee or redesign |
| C33/C45/C64/C65 |Accept mappedTDK C3216X5R1V226MTJ00E/C342620 for prototype;30pieces,USD10.926 |Full160AC↔TJ00E mapping now closed byTDK12Jan2023p12. KnownCeffgap remains: pair25.7182µFtyp5V; retained25µFbasis not guaranteed. Accept prototype uncertainty without claiming production qualification or silently changing bank basis |
| Other exact proposals |Review nonapproved exact identities in the66-line master as one coherent list |Includes newC63YAGEO CC0603KRX7R9BB333 instead of obsoleteMurata, plus preceding ordinary passive/BJT/R5/contact proposals. Evidence does not automatically promote an MPN to owner approval |

The bounded assessment in PHASE5_3_COMPATIBILITY_REVIEW.md replaces the earlier
demand for production-style joint guarantees as a prerequisite to deciding on a
prototype. Later physical testing still needs its own authorized milestone.

## Genuine commercial work still required

1. **L3exactXAL5050-682MEC,5pieces:** liveCoilcraftUK/EUR page givesEUR2.62 at1+,
   but no stock/dispatch quantity after setting5. Need exact allocation/lead time
   and Czech delivered quote. FarnellDEcached26Feb2027backorder is not confirmed
   timely supply. No different inductor automatically selected.
2. **R32TE RN73C1E31K6BTD,8pieces:** Mouser exact source/MOQ1/stock3,207 found,
   but Czech line price/delivery missing. Compare exactR32/R33 on an existing
   supplier parcel; preserve0402/0.1%/10ppm.
3. Refresh D2exactDialight last-stock allocation; D3/D4exactLCSC source now covers
   the20-piece request without alternatives. L2exactLCSC5-piece fallback retained;
   compare combinedCoilcraft5+5 quote.
4. Confirm regional prices/stock, packaging, shipping, tax/handling/FX and remaining
   harness/material choices. All66planning quantities have MOQ/multiple support;
   L3's supported order size is not a stock promise.

Partial electronicsUSD244.1846,2unpricedUSDlines (L3/R32); harnessUSD16.7510;
combinedpartialUSD260.9356 before unknown charges/materials.15-line accepted
dated-price subsetUSD98.6589 is incomplete. L3unquotedUSD15.10 removed from total.
No executable complete basket or cheapest delivered route is claimed.

**STOP for owner review before purchases. NoCAD, PCB redesign, firmware,
manufacturing changes, assembly, power-up, order, checkout, commit or push.**
