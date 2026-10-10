# V4 supported-adapter hot-plug part review

2026-10-10; **Phase 2.6 provisional branch implemented; owner review pending**.
The phase 2.5 discovery/screening sections below are historical. Current decision,
package checks, sourcing observations and prototype gates are recorded in
[phase2-6-hotplug-envelope.md](evidence/phase2-6-hotplug-envelope.md).
Owner prioritizes a technically sound prototype schematic over exhaustive
pre-prototype qualification: R12/C26 remain PROPOSED, not release-approved.
No guaranteed minimum Ceff is imposed; actual damping must be measured with the
eventual adapter/cable, which the owner confirms are not fixed. Preserve the 20 V nominal
+5% = 21 V envelope; this is not an active OVP redesign.

## Requirement and calculation limits

[TI BQ25798 SLUSDV2C, June 2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf),
Figure 8-1 p.130 recommends a 2 ohm resistor in series with a 2.2 uF shunt
capacitor at VIN for hot-plug above 15 V. Phase 2.6 now implements this shunt on
fused VIN1 ahead of the input FETs; see the final review netlist and verification.

Ideal 0-to-21 V step, initially discharged nominal 2.2 uF, ideal 2 ohm:
I(0)=10.5 A, P(0)=220.5 W, RC=4.4 us, resistor energy=CV²/2=0.4851 mJ.
These are calculations, not measured pulse stress. Recalculate for resistor
minimum tolerance, capacitance maximum, source envelope, repetitive contact
bounce and cable inductance. Rated steady watts or a high limiting voltage
alone do not qualify this low-resistance pulse application.

## Exact discovery candidates, not accepted choices

| Candidate | Manufacturer evidence | Preferred supplier / outstanding gates |
| --- | --- | --- |
| Panasonic ERJP08J2R0V, 2 ohm 5%, 1206, 0.66 W | [Official exact model](https://industrial.panasonic.com/ww/products/pt/small-and-high-power-chip-resistors/models/ERJP08J2R0V); [ERJ-P datasheet](https://industrial.panasonic.com/cdbs/www-data/pdf/RDO0000/AOA0000C331.pdf), 2026-03-28, pp.1-5; [pulse reference](https://industrial.panasonic.com/cdbs/www-data/pdf/RDO0000/ast-ind-161285.pdf). | [TME exact listing](https://www.tme.eu/en/details/erjp08j2r0v/smd-resistors/panasonic/) found, cached observation shows zero stock and 5000 order multiple; current stock/price/MOQ UNVERIFIED. No exact LCSC match established. Practical hobby-order suitability unresolved. Pulse graph not yet accepted. |
| Vishay CRCW12062R00JNEAHP, 2 ohm 5%, 1206, 0.75 W | [Official CRCW-HP e3 product](https://www.vishay.com/en/product/20043/), datasheet 20043 link; [manufacturer overview](https://www.vishay.com/doc?48634=) gives single-pulse family examples. | Full datasheet retrieval failed; overview alone is insufficient. No exact TME/LCSC orderable identity confirmed. No current price/stock/MOQ verified; other distributor discovery does not justify selection. |
| Murata GRM32ER72A225KA35L, 2.2 uF 100 V X7R 10%, 1210 | [Manufacturer reference GRM32ER72A225KA35-12A](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM32ER72A225KA35-12A.pdf) discovered; manufacturer model list corroborates nominal identity. | [LCSC C86054](https://www.lcsc.com/product-detail/C86054.html) exact identity discovered. Current price/stock/MOQ UNVERIFIED. Read exact current reference and DC-bias/Ceff evidence, confirm package/lands before acceptance. |
| KEMET C1210C225K1RACTU, 2.2 uF 100 V X7R 10%, 1210 | Discovery alternative only; exact manufacturer reference/Ceff not accepted. | [TME exact listing](https://www.tme.eu/no/en/details/c1210c225k1rac/mlcc-smd-capacitors/kemet/c1210c225k1ractu/) found. Cached stock is not current availability; price/MOQ/stock UNVERIFIED. |

Panasonic pulse reference is explicitly reference-only, not a guaranteed
specification: 1 us to 1 s pulse duration, >=10 s period, <=1000 cycles at room
temperature, resistance change <=5%, graph peak-power and maximum-overload
voltage conditions both apply. Datasheet maximum overload voltage is a ceiling,
not authority to apply it to 2 ohm: rated voltage is limited by sqrt(P*R).
The actual hot-plug exponential/contact-bounce waveform must be assessed against
applicable pulse evidence and repetition conditions. Do not compare nominal
energy alone or use a constant-power graph without stating the conversion.

Konnect catalog query failed with local database not found, not zero stock.
Panasonic pulse PDF direct shell retrieval failed (initial DNS failure; approved
retry ended with remote connection closure); web text was accessible but graph
inspection was not completed. No curve values or qualification are invented.

## Historical phase 2.4 next step

Obtain readable manufacturer pulse curves and exact capacitor DC-bias data;
resolve a practical small-quantity source, calculate conservative pulse envelope,
verify symbol/pad/body/land mapping and record acceptance. Only then add the
series-R/shunt-C VIN-to-PGND branch via Konnect, update BOM/partition assertions,
run fresh ERC/export/render/diff. Retain AON7528 SOA/clamp, cable/source/BMS and
matching-hardware hot-plug tests as separate unresolved qualification items.

## Phase 2.5 pulse/Ceff screening checkpoint — 2026-10-10

Read [source observations](evidence/phase2-5-source-observations.md) and
[calculation output](evidence/phase2-5-hotplug-screen.json) before resuming.
This supersedes the earlier statement that the pulse graphs could not be read.
The CAD is unchanged; no damping branch or fitted BOM quantity was added.

- **Do not select Murata GRM32ER72A225KA35L:** exact live SimSurfing result is
  **NRND**. Its reference sheet -12A (2026-06-26) was recovered, but lifecycle
  now prevents accepting it as the preferred new-design choice.
- Vishay CRCW12062R00JNEAHP is the stronger resistor candidate from this bounded
  screen. Datasheet 20043 Rev.17-Mar-2026 pp.5-6 and application note 28810
  Rev.30-Jun-2023 sections 1/2.2 were inspected. Use equal peak **and** energy:
  exponential voltage decay has rectangular duration RC/2. Conservatively
  combine the largest duration and peak across tolerances; they need not occur
  in the same resistor. With 5% tolerance, +/-200 ppm/K across the stated
  sensitivity range and 2.783 uF maximum reference-condition capacitance:
  **236.84 W**, **2.981 us**, **0.614 mJ**. Rounded 3 us curve reads (500 W
  single, 300 W continuous) pass this preliminary screen. That does not accept
  arbitrary ringing, pulse film temperature or repeated-contact service life.
- Panasonic ERJP08J2R0V remains unaccepted: its pulse reference is conditional,
  not a guaranteed specification, and a practical small-quantity preferred
  source remains unresolved. Do not invent a 1% 2-ohm ERJP08 alternative: the
  current datasheet's 1% range starts at 10 ohm.
- KEMET C1210C225K1RACTU now has exact manufacturer bias/temp/AC/aging evidence
  (sheet generated 2026-10-10), not just a distributor nominal description.
  At 21 V the typical DC-bias plot loses roughly 11-13%. The reproducible
  10-year sensitivity calculation, using explicit additional bias/AC margins,
  gives **1.226 uF** after tolerance/temp/aging. This is **not a guaranteed Cmin**
  and not a failed requirement: TI's cited application figure does not specify
  an effective-capacitance minimum. Actual damping adequacy must be established.
  LCSC C2168116 was checked live: 10 stock, MOQ/multiple 1, USD 0.2408 at 1+;
  refresh before ordering. Manufacturer lifecycle and physical lands remain open.
- Repetition cannot be accepted from a single-pulse curve: the upper-envelope
  energy gives 0.0614 W at 100 Hz and 0.614 W at 1 kHz. Vishay's ambient-derated
  0.75 W rating at 125 C is 0.265 W. These are sensitivity examples, not measured
  bounce frequencies or an approved 125 C operating point.

Reproduce with the bundled Python or another Python 3 runtime:
`python hardware/v4/evidence/calculate_hotplug_screen.py`.
It reads locally cached manufacturer PDFs solely to record their hashes and
writes the screening JSON; it never reads or writes serialized CAD.

### Next bounded step

Resolve exact current Vishay sourcing/lifecycle and KEMET lifecycle/land mapping;
compare delivered prototype cost at TME/LCSC and a justified fallback. Establish
the damping acceptance envelope using the real supported source/cable and the
capacitance sensitivity above, or qualify a current alternative with stronger
Ceff evidence. Do not repeat nominal CV-squared/2 calculations or re-select the
NRND Murata candidate. Only after component acceptance add the branch through
Konnect, extend all-pin assertions and run ERC/export/render/diff. Full charger-
stage owner review remains pending; MCU/USB and real PCB work remain deferred.
