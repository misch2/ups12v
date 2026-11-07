# Phase5.2 — owner review and remaining purchasing holds

2026-10-19. Quick start: review the exact decisions below, then obtain the missing
supplier/technical quotes. No purchase or CAD authorization is implied.

**Closed decisions:** purchase capacity5fully populatedF5; exactly5TI
BQ25798RQMR/C2876593;10each8.2k/13.7k/27k0805/1%R5; no always-DNP purchases.
U8 **LM74700QDBVTQ1/C2653623** and C70/C71 **C1608X7R1C105K080AC/C2167399**
are now OWNER_APPROVED procurement identities. Original MPNs retained for traceability;
CAD identities unchanged. No further acceptance is requested for those two identities.
External cells/BMS, externalPD converter and firmware are outside this phase.
Accepted exceptional SYS reset and architecture remain closed.

## Exact owner decisions still needed

| Item | Preferred resolution to review | Limits / why still held |
|---|---|---|
| Q3/Q8/Q9 |Select **AO3400A**, LCSC C20917,20pieces=15fit+1spare+4MOQ excess |Static/pinout/actualSOT23-fit comparison supports these slow controls. Manufacturer5µAmax at55°C is not an85°C maximum; ramp/whole-temperature qualification remains. Alternative PMV16XNR C110920 is now sourced but has about2×typicalCiss; neither is approved |
| TP1/TP3/TP4 |Select documented hand-formed0.30mm tinned-copper loop, two tails in each existing1.00mm hole, max2mm eye width/max3.5mm height |15fit+1spare;0.5m wire proposal. No force-fit/hole enlargement. Exact wire SKU/tolerance/price and later assembly fit remain open. No assembly performed |
| C35/C36 |Review exact Murata GRM21BR61E226ME44L proposal with stated prototype qualification limits |Typical12–14µF at3.3V and assumed4.7124µFscreen support C35 relative retained2.2µFfloor; no guaranteed combined bound. C36 has no newly invented floor. Owner selection is distinct from manufacturer qualification |
| Other proposed identities |Accept/reject exact Phase5.0 passive/precision/BJT proposals as listed in master, including R5Yageo ordering codes and H08JST contact |Values/package/quantity approvals do not automatically approve every exact supplier identity. Review as one coherent list; no silent promotion |

The AO3400A decision can be made as a procurement proposal with explicit evidence
limits; it does not declare matching-hardware qualification. Choosing an FET is
not authorization to alter CAD, power hardware or implement additional circuitry.

## Engineering evidence still required; owner approval cannot replace it

| Item | Established in Phase5.2 | Remaining requirement / next action |
|---|---|---|
| C32 |Actual6–18V/1Anormal-buck network,500kHz,local2.2µF+100nF,remoteC21/sharedF5 capacitors distinguished; input ripple/current equations and Yageo typical0.5–0.6µF at18V evaluated |No approved input-ripple allocation/source-impedance model or measured network response. Cannot inventCmin or sum remote capacitors ideally. Prefer manufacturer-supported same2.2µF/0805 candidate and justified input-network assessment. Current Yageo remainsHOLD; proposed TDK lookup did not qualify an alternative |
| C33/C45/C64/C65 |New officialTDKCSV: pair33.343µFtyp at3.3V,25.7182µFtyp at5V; illustrativetol/temp22.673/17.488µF |Retained25µFpair basis not established across conditions. FullTJ00E↔160AC controlled mapping/terminal geometry/bias identity still absent. Obtain TDK confirmation and combinedCeff evidence; no relaxing25µF or approving C342620 by nominal22µF/35V/1206 |
| FET temperature/ramping |Steady OFF truth table and nonlinear-capacitance/timing limitations documented for all three types |Manufacturer hot-leakage support or later matching-hardware characterization across intended conditions; no new ambient limit, supervisor or waived OFF state |

See [qualification report](PHASE5_2_COMPATIBILITY_REVIEW.md) for source revisions,
exact pad/net constraints, calculations and assumptions. No claim of full closure
is made for these engineering holds.

## Commercial closure still required

10master lines lack a usableUSDextended price;9lack confirmedMOQ-derived quantity.
Complete per-reference gaps and unsent quote requests are in
[commercial review](PHASE5_2_COMMERCIAL_REVIEW.md). Also resolve:

- L3 exactXAL5050-682MEC5pieces stock/dispatch/lead-time and delivered cost; compare
  combined CoilcraftEurope5+5 with FarnellCzech2289069/2289071 cut tape.
- L2 exactXAL5030-472MEC5pieces LCSCoffer exists; decide direct-versus-LCSC only
  after the combined shipment quote. No automatic spare or suffix substitution.
- D3/D4 exactBAS116H,115: TMEstock3cannot satisfy11requested.
- D2 exactDialight597-3605-607F is discontinued; TMEcached last-stock proposal
  exists. Refresh allocation before order; no alternateLED is approved.
- Fresh Czech supplier totals, packaging, all cached quantities/prices, LCSC/UK
  freight, VAT/import/handling and FX. Three-shipment strategy is conditional.

Current incomplete allowances: electronicsUSD236.7896,10unpriced USD lines;
separate harnessUSD16.7510; combined partialUSD253.5406 before unknown charges.
These include unquotedL3USD15.10 and insufficient-stockD3/D4USD1.32 indications.
12-line owner-approved exact dated-price subsetUSD89.1544 is incomplete.
No complete executable/delivered cost is available.

Confirm wire lengths, crimp/insulation range, XT30 mating gender, strain relief,
owned tools and paste/flux details before selecting those separate materials.
Battery matching remains a separate decision; it does not block the shared PCBA
capacity and all three R5 stocks. Historical Bought is not current inventory.

**STOP for owner review. No schematic/PCB/footprint/manufacturing/firmware,
physical assembly, power-up, purchasing, checkout, Git commit or push.**
