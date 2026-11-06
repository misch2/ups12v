# Phase5.1 compatibility and procurement evidence

**Superseded where conflicting by Phase5.3:** AO3400A approved; C35/C36
approved for prototype; all testpoint hardware/wire fabrication and purchase
requirements cancelled; actual assembly655. See OPEN_DECISIONS.md and
PHASE5_3_COMPATIBILITY_REVIEW.md for current TDK identity and supply work.

**Historical Phase5.1 evidence.** Phase5.2 owner approval closes the U8 and
C70/C71 selection gates below. Current qualification, corrected Q3 drive,
PMV16XNR sourcing, TDK numerical bias data and wire-loop proposal are in
[Phase5.2 compatibility](PHASE5_2_COMPATIBILITY_REVIEW.md). Other historical
statements below are superseded where the newer report explicitly says so.

2026-10-19. Read-only comparison against the accepted board; no CAD operations.
The 196-file preservation manifest is unchanged. Physical dimensions below come
from the accepted Phase4.21 export, whose component lands were preserved by the
accepted later paste-only adoption. See
[pad/net extracts](../evidence/phase5-1-sourcing/accepted-export-pad-fit.json).
This is a procurement comparison, not measured assembly/power-up qualification.

## U8: available package-ordering option

TI [LM74700-Q1 RevG §5 and ordering appendix](https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf)
lists LM74700QDBVRQ1 and LM74700QDBVTQ1 as active, production, six-pin DBV
SOT-23 devices. R is3000/reel; T is250/reel. The T option uses NIPDAU, one of
the finishes listed for R. Electrical device and DBV0006A geometry are shared.
This is a packaging/finish ordering option, not a different controller.

The actual PCB pin map is1F5_VCAP,2PGND,3F5_RAW,4F5_5V_OUT,5F5_GATE,6F5_RAW;
it agrees with1VCAP,2GND,3EN,4CATHODE,5GATE,6ANODE. Accepted 0.95mm pitch and
SOT-23-6 footprint remain. Do not use the eight-pin DDF variant.

[LCSC C2653623](https://www.lcsc.com/product-detail/C2653623.html) displayed2394,
MOQ/multiple1, USD2.715 at1 on a today-cached page retrieved2026-10-19.
Conditional order6=5fit+1spare, USD16.29 net before freight. Original R option
C2941042 is unavailable. **Recommend owner acceptance of DBVTQ1**; no automatic
substitution has been made. Source: critical-current.txt/current-09-1.txt.

## C33/C45/C64/C65: identity family is verified; exact suffix is not

The [TDK catalog page](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3216X5R1V226M160AC)
shows Production,22uF35V X5R20%,3.2±0.2×1.6±0.2×1.6±0.2mm, and internal
item-description family C3216X5R1V226MT****. Actual1206 lands have2.95mm centres
and1.15×1.8mm copper bounding boxes, consistent with the retained part class.

TDK's [ordering FAQ](https://product.tdk.com/en/contact/faq/capacitors-0117.html)
distinguishes catalog ordering numbers from OEM/internal descriptions. Its
[part-number FAQ](https://product.tdk.com/en/contact/faq/capacitors-0116.html)
also distinguishes customer specifications from the distributor standard.
Consequently, matching wildcard family and supplier nominal data do **not** prove
that exact OEM suffixTJ00E has the same controlled standard specification as
catalog160AC. Do not call this a fully verified equivalent or rename the source BOM.

[LCSC C342620](https://www.lcsc.com/product-detail/C342620.html) displays the exact
TJ00E code,92160stock, MOQ/multiple10, USD0.3642 at10. For5F5:20fit+1spare+9MOQ
excess=30, USD10.926 conditional. Current original catalog stock remains unresolved.
Recommend obtaining an explicit catalog-to-full-item-description confirmation,
then accepting this existing nominal/package candidate if Ceff also qualifies.

The manufacturer's bias graph did not load; characteristic-sheet access failed
via the web tool and direct download(403). The saved official LTspice bias model
is encrypted; it was not reverse-engineered or simulated. No numeric Ceff claim
is made for the3.3V or5V banks. The retained F5 pair's25uF effective reference
basis must be checked with actual manufacturer curves/tolerance/temp/aging.
These are existing capacitor requirements; no additional circuitry is proposed.

## C70/C71: in-production nominal/package replacement

[TDK C1608X7R1C105K080AC](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X7R1C105K080AC)
is Production:1uF±10%,16V,X7R±15%,-55..125°C;1.60±0.10×0.80±0.10×0.80±0.10mm.
It matches the retained Murata nominal electrical grade and nonpolar local bypass
role. C70MAIN_3V3 and C71USB3V3 operate at3.3V. Their0603 lands have1.55mm centre
spacing and0.90×0.95mm copper bounding boxes; terminal ends overlap those lands.
No new guaranteed1uF-effective requirement is inferred for these local bypasses.

[LCSC C2167399](https://www.lcsc.com/product-detail/C2167399.html), today-cached
2026-10-19:170stock, MOQ/multiple10, USD0.0551. Conditional order20=10fit+3spare+
7MOQ excess, USD1.102. Original GRM188R71C105KA12D is obsolete/unavailable.
**Recommend owner acceptance of the exact TDK catalog code**. Its internal
item-description suffix is not substituted for the catalog number. Hardware
transient behavior remains part of later prototype validation.

## Q3/Q8/Q9: EOL original and two separately reviewed candidates

Nexperia PMV16UN is EOL. The legacy DigiKey original page lists substitutes;
their stock counts are not stock of PMV16UN. No reliable exact small-order supply
was established. Do not use anonymous broker availability as an approved basket.

[Nexperia PMV16XN](https://www.nexperia.com/product/PMV16XN) is Production.
Its [manufacturer datasheet](https://assets.nexperia.com/documents/data-sheet/PMV16XN.pdf),
11November2014, retains20V and G1/S2/D3 SOT23, VGS±12V,24mΩmax at2.5V and
33mΩmax at1.8V. Static logic operation is suitable; no trusted small-order quote
was established, so it is a less actionable procurement option.

[AOS AO3400A](https://www.aosmd.com/products/mosfets/low-voltage-mosfets-12v-30v/ao3400a)
has a current product page and [Rev3.1 July2023 datasheet](https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf):
30V N-channel, VGS±12V,48mΩmax at2.5V. The top-view G/S/D drawing matches
G1/S2/D3 on the accepted SOT-23. Q3 drains CE_N through10k pull-up; Q8/Q9 drain
NEN/TCA_EN with100k3.3V logic pull-ups. Sources are PGND; nominal gate drive3.3V.
These are low-current logic switches, so the candidate's larger resistance than
PMV16UN is negligible for static low levels. Gate/drain ratings exceed retained
requirements. Do not infer high-current power-FET interchangeability from this.

[AOS package PO-00001N](https://www.aosmd.com/sites/default/files/res/package/SOT23.pdf)
specifies0.95mm pitch,1.90mm outer-pin spacing, body2.8..3.1×1.4..1.8mm,
overall lead span2.6..3.0mm and0.30..0.50mm lead widths. The exported pads are
1.475×0.600mm with1.90mm spacing and1.875mm row-centre separation. The long
accepted lands overlap the required lead/toe envelope; all three transistor
positions retain the same G/S/D assignment. No footprint remap is proposed.

[LCSC C20917](https://www.lcsc.com/product-detail/C20917.html) today-cached:
508820stock, MOQ/multiple5, USD0.098 at5. Conditional20=15fit+1spare+4excess,
USD1.96. **Recommend AO3400A for owner review** because it has a usable source.
It remains a different die: gate capacitance/charge and temperature-dependent
leakage differ. Startup/release timing is not measured or claimed equivalent;
review the candidate for these slow controls and qualify on the prototype.
Neither candidate has been placed into the approved basket or source schematic.

## TP1/TP3/TP4: exact physical hardware still blocked

Actual exported pads are circular2.00mm with1.00mm drills. The beaded-loop
footprint is TestPoint:TestPoint_Loop_D1.80mm_Drill1.0mm_Beaded; courtyard3.6mm.
Fitted quantity15, suggested spare1. These real parts are retained in purchasing.

The [Vero manufacturer drawing](https://www.farnell.com/datasheets/2042719.pdf)
specifies1.02mm holes for20-313137/20-2137 on1.6mm boards. Common Keystone5000
also specifies a1.02mm mounting hole. Their apparent similarity does not guarantee
fit in this1.00mm finished drill, including PCB/hardware tolerances. HarwinS1751-46
is SMT and D3082-01 is a shunt link; neither is a drop-in beaded testpoint.

Recommended options: source a documented single-hole loop whose insertion envelope
fits the accepted finished-hole tolerance; or explicitly approve a hand-formed,
tinned wire loop with an assembly instruction and strain-relief/clearance check.
The latter changes the hardware realization and remains unselected, unpriced.
Do not force-fit, enlarge holes, omit15 fitted references or invent an exact MPN.

## C32/C35/C36: manufacturer bias evidence, calculations and limits

Saved source PDFs and rendered curves are under phase5-1-sourcing. Graph readings
are approximate typical values, not minimum guaranteed production specifications.

| Reference / rail | Exact proposed part and evidence | Result / procurement disposition |
|---|---|---|
| C32 SYS, evaluate18V | Yageo CC0805KKX7R9BB225,2.2uF50V X7R10%; manufacturer spec sheet9March2023p3, [distributor-hosted original](https://store.comet.bg/download-file.php?id=27307) | Curve near18V is about-75%, roughly0.5–0.6uF typical. With0.9 tolerance×0.85 temperature×assumed0.9 aging, illustrative0.38uF using0.25 bias fraction. Nominal50V rating does not establish input Ceff. **HOLD** |
| C35 USB3V3,3.3V | Murata GRM21BR61E226ME44L,22uF25V X5R20%; [manufacturer-authored EC sheet12/2020 hosted by TI](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/GRM21BR61E226ME44_5F00_EC_5F00_22uF_5F00_0805.pdf),§4/5 | Approximately12–14uF typical at3.3V and0.5Vrms. Conservative illustrative screen22×0.50bias×0.80tolerance×0.85temperature×0.90assumed aging×0.70small-AC allowance=4.7124uF, above retained2.2uF floor. Typical curves and independently multiplied factors are not a guaranteed combined bound |
| C36 MCU3V3,3.3V | Same Murata identity and0805 body2.0±0.2×1.25±0.2×1.25±0.2mm; maximum thickness1.45mm | Same typical bias result. Remains22uF nominal bulk; no new2.2uF minimum or other performance gate invented. Prototype mux/MCU transient behavior is not proven by the curve |

The0.9 aging factor is an explicitly chosen screening allowance, not a guaranteed
manufacturer limit or an owner-approved service life. AC and DC effects are not
strictly separable; numerical margin is evidence for a prototype proposal, not
production qualification. Murata's current SimSurfing list separately confirms
the part family is in production; its graph/export UI became unresponsive, so
the saved dated manufacturer sheet is used with its age explicit.

[TPS62933 RevD §10.2.2.9](https://www.ti.com/lit/ds/symlink/tps62933.pdf)
recommends10uF input decoupling plus0.1uF and explicitly requires accounting for
bias. This recommendation is not an invented mandatory10uF-effective criterion.
Actual SYS also has C21(10uF nominal); C43 is the local0.1uF. C21's capacitance and
electrical distance/ripple contribution cannot be presumed to replace missing
local capacitance. C32 therefore needs a justified input-network/ripple bound or
a qualified same-value/same-footprint part before purchasing acceptance; no CAD or
architecture change is authorized. The same concern should inform other SYS
input capacitor qualification, rather than claiming voltage rating alone closes it.

[AP7361C output requirement](https://www.diodes.com/assets/Datasheets/AP7361C.pdf)
retains the existing2.2uF ceramic minimum. The new Murata evidence supports C35's
prototype proposal with stated assumptions; owner acceptance of the exact proposed
MPN and its qualification limits is still needed. No further architecture gate
is introduced. C32, unlike C35, does not have adequate captured justification yet.

## Exact Coilcraft small-order supply

Keep XAL5030-472MEC and XAL5050-682MEC;5each, no automatic spare. Manufacturer
catalog pages retain these exact identities and established electrical/package
evidence. Coilcraft Europe states no minimum order, so five pieces are supported
as an order size in principle, but exact stock, shipping and arrival are unquoted.
Retained indicative USD13.70+15.10 is not a live delivered quote.

Farnell cut-tape codes2289069(L2) and2289071(L3) are exact fallback identities.
Current Czech product access was unavailable; Ireland L3 page is cached4months.
New Farnell5131620 is full-reel MOQ400, unsuitable for five boards. Old DigiKey
L3 Marketplace21381690 is unavailable; do not substitute an unreviewed new suffix.
Recommend one combined exact-MEC Coilcraft Europe quote, compared with Farnell
Czech cut tape including freight/VAT/import. No RFQ was transmitted on the owner’s behalf.
