# Phase 5.5 — replacement review for owner approval

Quick start: approve the proposed identities below, the **paired** feedback changes,
and [final quantities](PHASE5_5_SUPPLIER_BASKETS.md) together. Nothing here changes
CAD or an existing approval automatically. Five F5 boards; ordered PCB immutable.

## Proposed MPN changes

| Refs | Original MPN | Proposed manufacturer / exact MPN | LCSC SKU | Compatibility and disposition |
|---|---|---|---|---|
| L2 | Coilcraft XAL5030-472MEC | Coilank AAPS0530M4R7F | C49261457 | Same4.7µH±20%; original lands fit; prototype proposal with stated drawing/thermal limits below |
| L3 | Coilcraft XAL5050-682MEC | Bourns SRP5050FA-6R8M | C3223092 | Same6.8µH±20%; original lands fit; prototype proposal |
| R32 | TE RN73C1E31K6BTD | Viking ARG02BTC3162 | C2681601 | 31.6kΩ,0.1%,25ppm/°C,0402; approve with R33 below |
| R33 | TE RN73C1E10KBTD | RESI PTFR0402Q10K0N9 | C52677569 | 10kΩ,0.02%,10ppm/°C,0402; tighter tolerance preserves the rail budget |
| R60 | TE RN73R1JTTD5302B25 | Yageo RT0603BRD0716KL | C326732 | 53kΩ→16kΩ,0.1%,25ppm/°C,0603; **paired value change** |
| R61 | Yageo RT0603BRD0710KL | Yageo RT0603BRD073K01L | C705772 | 10kΩ→3.01kΩ,0.1%,25ppm/°C,0603; only with R60 change |
| U1 | Espressif ESP32-C3-MINI-1-N4X | Espressif ESP32-C3-MINI-1-H4X | C41349510 | Same PCB antenna,4MB quad-SPI flash,chip v1.1,pins and module outline; wider upper temperature grade |
| C39 | Murata GRM155R71H333KE14D | Yageo CC0402KRX7R9BB333 | C106862 | Same33nF±10%,50V,X7R,0402; same soft-start function |
| R5 4S | Yageo RC0805FR-0727KL | Uni-Royal0805W8F2702T5E | C17593 | Same27kΩ,1%,0805,125mW;100ppm/°C |
| R5 2S stock | Yageo RC0805FR-078K2L | Uni-Royal0805W8F8201T5E | C17828 | Same8.2kΩ,1%,0805,125mW;100ppm/°C; alternative population only |
| R5 3S stock | Yageo RC0805FR-0713K7L | Uni-Royal0805W8F1372T5E | C17448 | Same13.7kΩ,1%,0805,125mW;100ppm/°C; alternative population only |
| R23 | Yageo RC0402FR-078K2L | Uni-Royal0402WGF8201TCE | C25924 | Same8.2kΩ,1%,0402,62.5mW,50V;100ppm/°C; MAIN priority divider |
| R63 | Yageo RC0603FR-0738K3L | Uni-Royal0603WAF3832T5E | C23034 | Same38.3kΩ,1%,0603,100mW;100ppm/°C; F5 enable divider |

These are sourcing proposals, not CAD replacements. Ordinary resistor grades
retain nominal values, tolerance, footprint and adequate working ratings; their
100ppm grade does not relax the original general-purpose divider class.
Live exact-product descriptions and tier/stock observations are saved in
[browser-live.json](../evidence/phase5-5-sourcing/browser-live.json). The R12
pulse-proof **CRCW12062R00JNEAHP is retained exactly**, not replaced with an
ordinary1206 resistor. D1,D2,R6,L1 and all keyed connectors are also exact.

## Inductors — original ordered copper and drawings

The [export-only fit check](../evidence/phase5-5-sourcing/fit-v4/fit.json) binds the
current board SHA256 `d0a8c95a…42b8ac2b`, accepted native preservation proof and
original ordered ZIP SHA256 `04de5b71…e6c4128ec4`. It compares the actual rounded
native pad polygons against ordered Gerber flashes. The established toolkit
0.25µm tessellation tolerance removes only numerical curve approximation; there
is zero geometry outside that tolerance. No native KiCad process was launched.

Both original lands are1.18×4.70mm, center pitch3.31mm, inner gap2.13mm.
Drawings are oriented with the terminal gap along the original pad pair:
L3 along X; L2 along Y at its existing−90° board angle. Both are nonpolar.
The manufacturer bottom views are rotated90° into this local pad coordinate
system; the drawn maximum body is5.5mm along the terminals ×5.7mm transverse.

| Result | L2 Coilank | L3 Bourns |
|---|---:|---:|
| Maximum height |3.1mm|5.0mm(4.8±0.2)|
| Minimum body reserve inside existing courtyard |0.235mm|0.235mm|
| Nearest neighboring courtyard clearance |C43:0.345mm;C33:0.355mm|C62:0.375mm;C64:0.605mm|
| Nominal overlap, each terminal |4.70833mm²|4.70833mm²|
| Minimum overlap at published dimensional corners |3.16033mm²*|3.44000mm²|
| Minimum fraction of terminal area at those corners |67.50%*|74.41%|
| Nominal geometry with±0.10mm XY placement sensitivity |≥4.27611mm²/terminal|≥4.27611mm²/terminal|
| Minimum terminal-to-opposite-terminal gap |2.00mm|2.05mm|
| Swept terminals intersect other-net exposed ordered copper |0mm²|0mm²|
| Minimum other-net exposed-copper clearance |0.61584mm|1.02500mm|

Nominal terminals are1.1×4.3mm:99.54% of that area overlaps the original lands.
The corner results separately include terminal depth/gap/width tolerances;
they do not claim that all terminal metal must be supported by PCB copper.
Short checking includes the **opposite inductor net**, not just unrelated nets.
The centered maximum body stays inside the previously accepted courtyard and
does not touch neighboring courtyards. Maximum heights fit the PCB component
area; an enclosure ceiling has not been specified or measured.

*Coilank publishes D=4.3mm as **typical**, without a guaranteed minimum/maximum.
Its overlap result therefore covers published E/F extremes with D typical,
and is not a guaranteed production-tolerance area bound. This is a bounded
prototype fit qualification for owner review. Bourns specifies D4.3±0.3,
E1.1±0.2,F2.3±0.25mm; Coilank specifies E1.1±0.3,F2.3±0.3mm.
Nominal placement sensitivity is separate from dimensional corners; it is
not a combined assembly-process guarantee. No pad, paste or PCB edits proposed.
Both [L2 overlay](../evidence/phase5-5-sourcing/fit-v4/L2-overlay.svg) and
[L3 overlay](../evidence/phase5-5-sourcing/fit-v4/L3-overlay.svg) were rasterized
and visually inspected against the calculated orientation.

Manufacturer bases:

- [Bourns SRP5050FA datasheet](https://www.bourns.com/docs/product-datasheets/srp5050fa.pdf),REV04/22,pp1–2; saved PDF and inspected drawing under Phase5.5 evidence.
- [Coilank AAPS-F manufacturer document hosted by LCSC](https://datasheet.lcsc.com/datasheet/pdf/db0306ba92d8c07b239ddfd67f0cd388.pdf?productCode=C48783469),pp1–2 and exact AAPS0530M4R7F row p5; revision not stated in retrieved document. Retrieved20Oct2026; saved provider extraction in research files. Direct PDF retrieval failed; no claim of a locally complete Coilank PDF.
- [Coilcraft XAL50xx](https://www.coilcraft.com/getmedia/49bc46c8-4b2c-45b9-9b6c-2eaa235ea698/xal50xx.pdf),Doc908 revised26Feb2026; original geometry is independently bound to ordered copper rather than inferred from a replacement footprint.

## Inductor electrical screen

| Parameter | L2 original XAL5030-472MEC | L2 Coilank | L3 original XAL5050-682MEC | L3 Bourns |
|---|---:|---:|---:|---:|
| Nominal inductance |4.7µH|4.7µH±20%|6.8µH|6.8µH±20%|
| DCR maximum at25°C |40mΩ|36.3mΩ|29.45mΩ accepted baseline|28.6mΩ|
| Isat typical |6.7A at30% L drop|7A at**40%** drop|6A at30% drop accepted baseline|7.8A at30% drop|
| Irms typical at40°C rise |5.9A|5.9A|retain accepted original basis|6.4A|
| Irms typical at20°C rise |4.3A|not specified|4.7A accepted baseline|4.8A|

Coilank's7A figure is **not equivalent to Coilcraft's30%-drop definition**.
Bourns and Coilank maximum155°C includes self-heating; they are not155°C ambient
parts at rated current. Coilank measurements are at25°C,100kHz/0.1V for L.
Its55V rating exceeds the accepted18V input screen. Bourns6R8 SRF is18MHz typical.
Neither selected document gives a guaranteed hot-Isat or numerical total AC/core
loss bound for this application. This limits the proposal to the accepted
prototype validation basis; it does not establish hot fault survival.

[Calculations](../evidence/phase5-5-sourcing/electrical-calculations.json) use the
accepted load assumptions MAIN1A/F5 2A, Vin18V, L−20%, frequency423kHz
(450kHz×0.94 temperature sensitivity), and each proposed divider's maximum
static output. TPS62933 RT remains open/nominal500kHz.

| Calculation | L2 | L3 |
|---|---:|---:|
| Peak-to-peak ripple |1.73929A|1.60546A|
| Peak current |1.86964A|2.80273A|
| RMS current |1.11897A|2.05300A|
| Winding copper loss at25°C DCR max |45.45mW|120.54mW|
| Winding copper loss at125°C sensitivity |63.31mW|167.92mW|

Both normal-load peaks are below the TPS62933 minimum4.2A high-side limit;
its low-side limit is a **valley** limit(min2.9A), not a peak limit. The maximum
high-side limit5.8A and typical25°C saturation ratings do not establish a
temperature-independent protection guarantee. Further L-decline sensitivity
(40% Coilank/30% Bourns), winding Rac/Rdc ratios1/3/5, and skin depth≈0.102mm
at423kHz are recorded in the JSON. Rac assumptions are sensitivities; core loss
remains unknown, not zero. Current-rise ratings cannot be linearly extrapolated
into a measured board temperature. Existing matched-hardware bring-up and ripple
limitations remain accepted; no new broad architecture audit or power-up here.

TI basis: [TPS62933 datasheet](https://www.ti.com/lit/ds/symlink/tps62933.pdf),
SLUSEA4D RevD Aug2022, current-limit/electrical table and§9.3.3–9.3.5,p19.

## Feedback tolerance and temperature

Reuse the accepted Phase3.6 budget, including independent opposite tolerance
and TCR over Δ125°C from25°C, Vref0.784…0.816V, and±0.15µA FB-leakage screening
assumption. The leakage value is a retained screen, not a guaranteed new TI limit.
MAIN low-side allocations total104mV and high-side25mV; F5 low-side110mV and
high-side30mV. These are calculations, not new measurements.

| Divider | Nominal V | Existing allocated rail interval | Existing limits | Result |
|---|---:|---:|---:|---|
| Original MAIN31.6k/10k,both0.1%,10ppm |3.328|3.14159…3.43594|3.135…3.465|Retained baseline|
| Viking R32+0.1%,10ppm R33 |3.328|3.13696…3.44079|same|Pass,1.96mV lower reserve|
| Both0.1%,25ppm |3.328|3.13237…3.44568|same|Reject:−2.63mV lower reserve|
| **Viking R32+RESI R33 0.02%,10ppm** |3.328|**3.13893…3.43872**|same|**Pass,3.93mV lower reserve**|
| **F5 R60/R61=16k/3.01k,both0.1%,25ppm** |5.05249 RAW|**4.80481…5.22188 at J8**|4.75…5.25|**Pass,54.81mV/28.12mV reserves**|

R32 Viking total resistor error is0.4125%; RESI R33 is0.145% over this screen.
The [Viking exact part page](https://www.viking.com.tw/en/product/ARG02BTC3162.html)
confirms0402,31.6kΩ,0.1%,25ppm/°C,1/16W; family RevA5/22May2019 is the
retrieved family basis. RESI manufacturer document **C16003 V7,20Apr2023**,
ordering-code/dimensions sections, identifies Q=0.02%,N=10ppm and
1.00±0.05×0.50±0.05×0.35±0.05mm body; saved as
[RESI-drawing.pdf](../evidence/phase5-5-sourcing/live-http/RESI-drawing.pdf).
Both use the existing0402 pads. Divider dissipations are far below package ratings.

Exact53kΩ C2506990 and five same-value LCSC leads returned zero live stock;
TME's exact RN73R53k search also gave zero cached stock. The proposed paired
16k/3.01k combination stays within TI's10k…300k recommended top-resistor range.
Bottom10k is a recommendation for most applications, not a mandatory minimum;
TI explicitly allows selecting divider current. New divider current265.78µA
versus80µA adds185.78µA(about0.94mW) for availability. Inductor current screening
above includes the new output corner. **Do not fit either changed resistor alone.**

## ESP32, connectors, C32 and harness

Espressif **ESP32-C3-MINI-1 & MINI-1U datasheet v2.2,6May2026**,Table1-1,
pin description and physical dimensions(ch3/10/11), compares N4X/H4X:
4MB Quad flash,chip v1.1,PCB antenna,13.2×16.6×2.4mm,same pinout;
H4X−40…105°C versus N4X−40…85°C. No external-antenna MINI-1U or different
flash variant substituted. [Manufacturer datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf).

All four Nano-Fit headers and all four matching housings retain **exact MPNs**:
J1/J2 black key-A1053131102/1103 with1053071202/1203;
J3/J8 natural key-B1053132102/2103 with1053072202/2203.
The approved1053002100 contacts are retained; no gold/tin, key or orientation
swap. JST headers/housings and SXH-001T-P0.6 contacts also retain exact identities.
See [every former external-supplier line](PHASE5_5_EXTERNAL_LINES.md).

Wire proposal adds TME5m each BQ FLRY-B0.50-RD/1 and BK/1,Cu stranded0.5mm²,
OD1.4…1.6mm,60V,−40…105°C. Molex1053002100 specifies20/22AWG and1.60mm
insulation diameter;0.5mm² is the metric20AWG-class conductor. Retain the normal
crimp-fit inspection for a chosen wire/contact combination; an8A contact catalog
rating is not an8A harness system guarantee. Signal wire: two10m rolls Donau
118-5,Cu0.14mm²,OD1mm,60V,−10…85°C. This fits the **non-N**
SXH-001T-P0.6 range0.08…0.33mm²/OD0.9…1.9mm; the N contact variant has a
different insulation range and is not substituted. Signal wires are white,
requiring identification at both ends. Length allowances remain the earlier
5m red/5m black/11m signal planning assumptions, not measured enclosure lengths.
Sources: [Molex](https://www.molex.com/en-us/products/part-detail/1053002100),
[JST XH](https://order.jst-mfg.com/InternetShop/app/pdf_show.php?kbn=1&key=eXH.pdf),
and exact TME pages linked in the shopping list.

Additional C32 TDK **C2012X7R1H225K125AC**, TME symbol**C2012X7R1H225KAC**,
is the exact same manufacturer part, not a shortened-MPN substitute. Buy10 at
cached USD0.31=3.10; stock22,076 in today's cache, MOQ/multiple1. No DigiKey
shipment. Retain Phase5.4 manufacturer bias evidence: typical1.19085µF at18V,
versus approved Yageo0.5…0.6µF; neither is a guaranteed minimum/measurement.
Approved Yageo C32 x10 and TDK bulk bank x30 remain in the main basket.

**STOP for owner approval of all proposed replacements, wire choices, optional
C32 comparison stock and final baskets. No CAD adoption or ordering performed.**
