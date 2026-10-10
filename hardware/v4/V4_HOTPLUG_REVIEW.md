# V4 supported-adapter hot-plug part review

2026-10-10; **OPEN, no new damping parts selected or drawn**. This advances
the unfinished charger schematic milestone. Preserve the approved 20 V nominal
+5% = 21 V envelope; this is not an active OVP redesign.

## Requirement and calculation limits

[TI BQ25798 SLUSDV2C, June 2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf),
Figure 8-1 p.130 recommends a 2 ohm resistor in series with a 2.2 uF shunt
capacitor at VIN for hot-plug above 15 V. The present note is not that circuit.

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

## Next concrete step

Obtain readable manufacturer pulse curves and exact capacitor DC-bias data;
resolve a practical small-quantity source, calculate conservative pulse envelope,
verify symbol/pad/body/land mapping and record acceptance. Only then add the
series-R/shunt-C VIN-to-PGND branch via Konnect, update BOM/partition assertions,
run fresh ERC/export/render/diff. Retain AON7528 SOA/clamp, cable/source/BMS and
matching-hardware hot-plug tests as separate unresolved qualification items.
