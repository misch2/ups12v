# Stage 2.2 component acceptance

2026-10-10. Schematic acceptance only; no V4 PCB placement/routing or manufacturing approval.

## CE parts

Q3: Nexperia **PMV16UN**, SOT23/TO-236AB. [Manufacturer datasheet](https://assets.nexperia.com/documents/data-sheet/PMV16UN.pdf), Rev.1, 2011-04-04, pp.2/3/6/11/12. VDS20V, VGS±8V; RDS(on) max23mΩ at2.5V/25°C. Drain leakage max20µA at20V/150°C. These limits apply to the CE circuit, never to the21V adapter rail. Packaging/orderable reel suffix and a TME listing remain unverified; do not substitute another transistor by name alone.

Selected existing symbol `Transistor_FET:2N7002` is used only as a verified G/S/D drawing; instance value, description and datasheet must identify PMV16UN. Footprint `Package_TO_SOT_SMD:SOT-23`.

| Physical lead | Function / symbol pin / type | Pad | Local X,Y mm | View and evidence |
| --- | --- | --- | --- | --- |
| 1 | G /1 /input | 1 | -0.9375,-0.95 | Component top, Fig.18 rotated90° clockwise; p.2 Table2 |
| 2 | S /2 /passive | 2 | -0.9375,+0.95 | Same top view |
| 3 | D /3 /passive | 3 | +0.9375,0 | Same top view |

Three leads, three symbol pins, three SMD pads; no exposed/mechanical/duplicate pads. Pad sizes1.475×0.6mm, F.Cu/F.Mask/F.Paste, no drill. Pin1 triangle and fab chamfer checked in disposable board render and pad readback.

D3/D4: Nexperia **BAS116H,115**, SOD123F. [Manufacturer datasheet](https://assets.nexperia.com/documents/data-sheet/BAS116H.pdf), Rev.3, 2011-05-31, pp.1/3/5/6. 75V reverse; leakage max80nA at75V/150°C; VF max0.90V at1mA/25°C. Cold-ramp forward voltage remains a prototype check. [Verified TME identity](https://www.tme.eu/en/details/bas116h.115/smd-universal-diodes/nexperia/bas116h-115/); no price/stock claim.

| Physical lead | Function / symbol pin / type | Pad | Local X,Y mm | View and evidence |
| --- | --- | --- | --- | --- |
| 1 | K /1 /passive | 1 | -1.4,0 | Component top; cathode bar; Fig.6 rotated90° counterclockwise; Table2 |
| 2 | A /2 /passive | 2 | +1.4,0 | Same top view |

Symbol `Device:D`, footprint `Diode_SMD:D_SOD-123F`: two leads/pins/pads, no duplicates/mechanical pads. Pads1.1×1.1mm, F.Cu/F.Mask/F.Paste, no drill. Cathode silk/fab marker, orientation and readback checked against Fig.7.

## High-voltage ceramics

**GRM32ER71H106KA12L**, Murata10µF50V X7R±10%,1210. Manufacturer reference sheet **GRM32ER71H106KA12-01**, 2016-03-07, pp.1/2/5, [manufacturer document hosted by TME](https://www.tme.eu/Document/80ae9f13e6a19298661071c8333727d9/GRM32ER71H106KA12-01.pdf); [TME identity](https://www.tme.eu/en/details/grm32er71h106ka12l/mlcc-smd-capacitors/murata/). Body3.2±0.3×2.5±0.2mm. Symbol `Device:C`, footprint `Capacitor_SMD:C_1210_3225Metric`.

| Physical termination | Symbol / type | Pad | Local X,Y mm | View |
| --- | --- | --- | --- | --- |
| Either end | 1 /passive | 1 | -1.475,0 | Component top, interchangeable nonpolar ends |
| Other end | 2 /passive | 2 | +1.475,0 | Same |

Two terminations/pins/pads; no duplicates/mechanical features. Pads1.15×2.7mm, F.Cu/F.Mask/F.Paste, no drill. Body/fab/courtyard and disposable readback/render checked. Nominal bank totals are not guaranteed effective capacitance at21V: DC-bias, tolerance, temperature, aging and ripple/load response remain qualification items.

**GRM155R71H104KE14D**, Murata100nF50V X7R±10%,0402. [TME identity and manufacturer document link](https://www.tme.eu/en/details/grm155r71h104ke14d/mlcc-smd-capacitors/murata/); independently listed in [TI TIDA-01444 BOM](https://www.ti.com/lit/pdf/tidrrk9). Existing0402 footprint unchanged; nonpolar end assignments unchanged. No claim of new package geometry acceptance is needed for this field-only substitution.

Evidence: `evidence/phase2-package-sch.png`, `phase2-package.svg`, `phase2-package-detail.png`, and `phase2-package-readback.json`. Disposable CAD stays ignored under `ups_v4/.validation/`; owner explicitly authorized closed-file footprint checks there. Main V4 live-PCB path verification remains outstanding.
