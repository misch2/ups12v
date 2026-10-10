# Phase 2.5 primary-source and procurement observations

Observed 2026-10-10. These are document/UI observations, not hardware measurements.

## Manufacturer documents

- Vishay 20043, CRCW-HP e3, **17-Mar-2026**, pp.5-6:
  <https://www.vishay.com/docs/20043/crcwhpe3.pdf>. Both single and continuous
  pulse-power curves and the independent pulse-voltage limit were visually
  inspected. At 3 us, conservative manual reads for CRCW1206-HP are 500 W
  single / 300 W continuous; pulse voltage ceiling is about 700 V. These rounded
  reads have deliberately limited precision and are screening inputs only.
  Single-pulse conditions include n < 1000 and vanishing average power.
  Continuous pulses additionally require average power within the ambient-
  derated rating. Film temperature and PCB thermal conditions still apply.
- Vishay 28810, **30-Jun-2023**, section 1 and section 2.2:
  <https://www.vishay.com/docs/28810/pulseloadhandling.pdf>. Transform a
  nonrectangular pulse into a rectangle with the same peak power and energy.
  An exponential voltage pulse with time constant RC therefore has equivalent
  rectangular duration RC/2. This is manufacturer methodology, not an invented
  energy-only acceptance criterion. It applies here as a preliminary ideal-step
  screen; it does not model cable ringing or arbitrary contact bounce.
- Panasonic ERJ-P, **28-Mar-2026**, pp.1-2, and undated single-page pulse reference:
  <https://industrial.panasonic.com/cdbs/www-data/pdf/RDO0000/AOA0000C331.pdf>
  and <https://industrial.panasonic.com/cdbs/www-data/pdf/RDO0000/ast-ind-161285.pdf>.
  Pulse graph is now readable. It remains reference-only at room temperature,
  >=10 s period and <=1000 cycles. Do not transfer Vishay's methodology into a
  guaranteed Panasonic qualification. ERJP08 at 2 ohm is a 5% selection; the 1%
  range starts at 10 ohm. Low-resistance TCR is -100 to +600 ppm/K.
- Murata **GRM32ER72A225KA35-12A**, reference sheet dated **Jun.26,2026**, pp.2,
  6, 11-12: exact 2.2 uF/100 V X7R, 1210; 3.2 +/-0.3 by 2.5 +/-0.2 mm,
  thickness 2.5 +/-0.2 mm. Reference sheet alone is not DC-bias/Ceff evidence.
  <https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM32ER72A225KA35-12A.pdf>.
- KEMET **C1210C225K1RACTU**, exact generated sheet **10/10/2026**, pp.1-4:
  <https://search.kemet.com/component-documentation/download/specsheet/C1210C225K1RACTU>.
  2.2 uF/100 V X7R 10%, 1210; 3.2 +/-0.3 by 2.5 +/-0.2 by 2.0 +/-0.2 mm.
  Aging: 3% loss/decade hour, reference 48 h. Page 2's typical DC-bias curve
  indicates approximately 11-13% loss at 21 V. Page 3's temperature and AC
  curves were also inspected. Page 4 explicitly identifies simulations as
  typical behavior, not guaranteed performance. Footprint lands, lifecycle and
  assembled pulse reliability have not been accepted.

Full downloaded documents and inspection renders are retained under ignored
`evidence/references/`; hashes/sizes are in `phase2-5-hotplug-screen.json`.
The source links, revisions, observations and calculation script are retained
as review evidence even if that local download cache is absent.

## Live UI observations

- Murata SimSurfing exact filter `GRM32ER72A225KA35` displayed:
  `GRM32ER72A225KA35 ... NRND 2.2uF 100 ... 125 X7R 3225M/1210 2.7 +/-10%`.
  <https://ds.murata.com/simsurfing/mlcc.html?oripartnumbers=%5B%22GRM32ER72A225KA35L%22%5D&partnumbers=%5B%22GRM32ER72A225KA35%22%5D>.
  The owner explicitly authorized accepting its software license during this
  session. **Reject this candidate for new V4 selection** under AGENTS.md's
  lifecycle preference; stock does not reverse the NRND status.
- LCSC exact KEMET listing <https://www.lcsc.com/product-detail/C2168116.html>
  was checked in the live browser. It displayed exact MPN/manufacturer,
  1210, 2.2 uF/100 V X7R 10%; stock **10**, MOQ **1**, multiple **1**,
  USD **0.2408 at 1+**, **0.194 at 10+**. This is a dated observation, not a
  reservation. Shipping, tax and delivered cost were not quoted. One part per
  proposed damping branch; fitted quantity remains zero until drawn/accepted.

## Cached observations, not current availability

- Panasonic ERJP08J2R0V TME listing: zero stock, 5000 multiple; source crawl
  five months old. <https://www.tme.eu/en/details/erjp08j2r0v/smd-resistors/panasonic/>.
  It does not establish a practical prototype purchase or current stock.
- Vishay CRCW12062R00JNEAHP DigiKey listing showed USD 0.30 at 1+, 9131 stock,
  but its source crawl was 1.2 years old: **current stock/price UNVERIFIED**.
  <https://www.digikey.com/en/products/detail/vishay-dale/CRCW12062R00JNEAHP/2826105>.
  No exact TME/LCSC orderable identity was established. A fallback supplier can
  be justified if preferred suppliers cannot supply a suitable pulse part;
  a dedicated shipment for this resistor has not been costed or accepted.

## Acceptance boundary

No component has gained APPROVED status and no CAD mutation occurred.
The Vishay/KEMET combination now has a reproducible electrical screen, but
current resistor sourcing, lifecycle/physical lands and damping at the real
minimum Ceff remain open. The 10-year aging scenario and -55..125 C sensitivity
range are engineering screens, not newly approved UPS lifetime/ambient limits.
