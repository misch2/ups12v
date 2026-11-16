# Phase5.3 — purchasing identities and practical prototype acceptance

2026-10-19. Quick start: the three explicit owner decisions below are closed.
C32 and the TDK output banks have concrete purchasing proposals and bounded
prototype assessment plans for owner review. No physical tests were performed.
No CAD, footprints, population files, manufacturing data or firmware changed.

## Owner decisions applied

| Refs | Purchasing identity / quantity | Disposition |
|---|---|---|
| Q3/Q8/Q9 | Alpha & Omega Semiconductor AO3400A, LCSC C20917;20=15fit+1spare+4MOQ excess | APPROVED. Replaces PMV16UN,215 only in purchasing. Existing SOT-23 footprint and Phase5.2 CE/I2C OFF-state, leakage and rail-ramp prototype checks retained. No hardware/whole-temperature qualification claimed |
| C35/C36 | Murata GRM21BR61E226ME44L, LCSC C86816;15=10fit+3spare+2MOQ excess | APPROVED FOR PROTOTYPE. Documented typical12–14µF at3.3V and illustrative4.7124µF screen remain non-guaranteed. No minimumCeff guarantee or completed hardware qualification claimed; C35's existing LDO requirement remains |
| TP1/TP3/TP4 | No purchased or obligatorily fitted part | Existing pads/plated holes suffice for probing. Owner has optional loops in inventory. Remove all proposed wire-loop fabrication, fit, spare and purchase requirements. Geometry preserved |

Reuse [Phase5.2 comparison](PHASE5_2_COMPATIBILITY_REVIEW.md) for the approved FET
and Murata evidence; do not repeat those closed selection reviews.

## C32 — recommend the known exact Yageo for a bounded prototype evaluation

**Proposed purchase:** YAGEO CC0805KKX7R9BB225,2.2µF±10%,50V X7R/0805,
[LCSC C125847](https://www.lcsc.com/product-detail/C125847.html),10pieces:
5fit+3spares+2MOQ excess; USD0.139/pc, USD1.39 page allowance. No nominal value
or footprint change. The saved manufacturer specification9March2023 and curve
are in Phase5.1 evidence; the actual6–18V/1A/500kHz network analysis is in Phase5.2.

Known uncertainty is explicit: approximately0.5–0.6µF **typical** at18V.
For D=3.3/18, IOUT=1A and500kHz, the ideal C32-only calculation is
ΔVIN=IOUT·D(1−D)/(f·C)=0.50–0.60Vpp. This excludes ESR/ESL/source impedance
and concurrent charger/F5 current. Calculated capacitorRMS including ideal
inductor ripple is about0.515A at6V and0.412A at18V. These are screening
calculations, not measurements, failure proof or capacitor ripple ratings.
RemoteC21 and C60/C61 are not added as ideal local decoupling.

[TI TPS62933 SLUSEA4D Rev.D §10.2.2.9](https://www.ti.com/lit/ds/symlink/tps62933.pdf)
uses10µF as a typical input recommendation with bias/ripple accounting. It does
not establish a mandatory10µF-effective minimum for this board. Existing approved
requirements do not allocate an input-ripple limit; none is invented here.

**Owner-review proposal:** accept the exact part for prototype purchasing with
this known uncertainty, then assess the actual network on matching hardware.
A signed joint capacitance guarantee is not a prerequisite for this prototype
proposal. Later, separately authorized hardware work should:

1. Record revision/BOM/cells/source/cable/load/ambient; measure SYS at U3 VIN
   relative to its local PGND using a short probe return, and MCU3V3 concurrently.
2. Sweep the already approved6–18V input and load up to the required1A; include
   source insertion/removal, load steps and simultaneous F5/charger operation
   where populated. Check ripple/ringing, regulation, start-up, resets and heating.
3. Assess against existing operating/electrical limits and project regulation
   requirements. If the actual network violates them, stop and return evidence
   for owner review; no capacitor addition, copper change or waiver is implied.

No numericalCmin or new test pass threshold is asserted. Purchasing acceptance
would accept a prototype investigation, not prove that the input network passes.

An alternative research lead is **TDK C2012X7R1H225K125AC** (correct catalog
suffixAC, not the previously investigatedAB). Its
[manufacturer characterization sheet,3Jan2016](https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/charasheet/c2012x7r1h225k125ac.pdf)
lists2.0±0.2×1.25±0.2×1.25±0.2mm,50V/X7R/±10%, with bias and ripple-rise graphs.
[DigiKey445-5968-1-ND](https://www.digikey.com/en/products/detail/tdk/C2012X7R1H225K125AC/2444009)
shows a small-order source,8pieces atUSD0.53=USD4.24 (last-month cache).
No numerical graph extraction or betterCeff is claimed, and no automatic
replacement or additional purchase is proposed. Reusing the characterized Yageo
avoids treating another nominally identical2.2µF as a proven cure.

## C33/C45/C64/C65 — exact TDK identity mapping closed

**New primary evidence:** TDK Corporation of America, Ceramic Capacitor Supply
Status Update, **12Jan2023**, attachment **PDF page12**, columns CatalogPN/TDKPN:
**C3216X5R1V226M160AC → C3216X5R1V226MTJ00E**. The document is manufacturer-authored,
hosted in [Future Electronics' PCN archive](https://media.futureelectronics.com/PCN/95306_SPCN.PDF).
The downloaded original and visually checked page12 are saved in Phase5.3 evidence.
This is explicit full-code mapping, stronger than the earlier wildcard/retailer
alias. Its old supply-status discussion is not used as current stock evidence.

Use the mapped TDK ordering identity in the purchasing proposal, retaining160AC
in original-MPN fields and in untouched CAD. Existing accepted1206 geometry and
nominal22µF±20%/35V/X5R part remain. No new stack-up or physical alternative is
inferred. [LCSC C342620](https://www.lcsc.com/product-detail/C342620.html) shows
92,160pieces,MOQ/multiple10,USD0.3642;30=20fit+1spare+9MOQ excess,USD10.926
(today-cached page, not reserved). **Exact naming hold is closed.**

Reuse the official Phase5.2 DC-biasCSV: pair33.343µFtyp at3.3V and25.7182µFtyp
at5V. Illustrative×0.8tolerance×0.85temperature gives22.673/17.4884µF; those
factors are not a guaranteed combined bound and omit other uncertainty. The
retained25µF bank design basis remains unproven across conditions. TI Rev.D
table10-2 minima15µF at3.3V/4.7µH and10µF at5V/6.8µH support the plausibility
of prototype evaluation; they do not silently replace the project's25µF basis.

**Owner-review proposal:** accept purchasing the mapped exact TDK part for
prototype evaluation with the documentedCeff gap. Do not demand a production
minimum guarantee or further full-code mapping to proceed with that decision.
No guaranteed25µF or final qualification is claimed. Later authorized bench work
should capture both output banks' startup, regulation, ripple and load-step
response at approved supply/load/ambient conditions, alongside converter/input
heating. Biased small-signal capacitance measurements may help explain results
but do not replace power-stage measurements. If the measured assembly cannot
meet existing requirements, return the data for owner review before a design
change or revised bank basis. Buying the prototype is not a production release.

## Other procurement findings without redesign

L2 remains exactXAL5030-472MEC,5pieces; L3 remains exactXAL5050-682MEC,5pieces.
L3 supply is still a genuine commercial hold. No MRC, other inductance, XGL
series, footprint or termination substitution is silently selected.

D3/D4 remain NexperiaBAS116H,115 with the existingSOD-123F/polarity/electrical
review. A20-piece exactLCSC offer bypasses TME's3-piece shortage; no substitute
review is needed. D2 exactDialight597-3605-607F last-stock offer remains the
first choice; check availability before purchase. No color/footprint change.

**Additional genuine supply issue:** originalC63 MurataGRM188R71H333KA61D is now
reported obsolete/no stock by DigiKey. The master contains a clearly unapproved
same-value proposal **YAGEO CC0603KRX7R9BB333**. Its
[exact manufacturer specification generated17Oct2026,p1](https://www.yageogroup.com/download/specsheet/CC0603KRX7R9BB333)
gives33nF±10%,50V X7R; body1.6±0.1×0.8±0.1×0.8±0.1mm, tin terminations,
−55..125°C, IR10GΩ. Nominal grade and0603 class match the retainedSS capacitor;
start-up timing remains part of prototype observation. No CAD change is proposed.
[DigiKey311-1429-1-ND](https://www.digikey.com/en/products/detail/yageo/CC0603KRX7R9BB333/2833735)
offers8pieces atUSD0.12=USD0.96; compare10-piece tierUSD0.65 total.
Owner acceptance of this exact purchasing proposal is still pending.

**STOP for owner review before purchases. No power-up or hardware qualification
is authorized by this document.**
