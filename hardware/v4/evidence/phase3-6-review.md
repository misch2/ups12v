# Phase 3.6 — bounded schematic completion for owner review

2026-10-10. Calculations and exported CAD evidence, **not hardware measurements or release approval**. Source SHA256 `4b53fa435f88b5aab99067b64ff83778d152d60264b3dd2ea7cb19cba5996c47`. KiCad 10.0.7, CAD mutations through Konnect. No PCB layout, commit/push or firmware build performed. Existing project edits preserved; title block unchanged.

## Result and scope

Added independent F5 SYS 6–18 V → 5 V/2 A converter, reverse-current blocker and connector. The four charger/cell profiles each have F0/F5 population overlays on one physical PCB. Added thirteen physical copper testpads. Corrected normal-buck feedback using owner-authorized full-budget selection. Existing electrical connections remain unchanged. New local circuits predominantly use direct wires; existing dense presentation was retained.

Fresh [PDF](phase3-6-final.pdf), [PNG](phase3-6-final.png), [true XML](phase3-6-final.net.xml), [ERC](phase3-6-final-erc.json), [independent verification and hashes](phase3-6-verification.json), [population projection](phase3-6-population.csv), [footprint readbacks](phase3-6-footprints.json), [Konnect change record](phase3-6-konnect-changes.json). Visual inspection of the new F5/testpad areas found the circuit readable; passive labels remain compact.

## Normal buck correction

R32 = 31.6 kΩ, R33 = 10 kΩ; both **0.1%, 10 ppm/°C or better**, 0402. Owner authorized choosing a value from the complete tolerance budget instead of fixing the provisional 31.2 kΩ. Nominal MAIN_3V3 is 3.328 V. Using reference 0.784–0.816 V over the datasheet temperature range, independent opposite resistor tolerance/drift over 125 °C from 25 °C, and ±0.15 µA FB leakage screening gives 3.24559–3.41094 V static. The leakage figure is a screening assumption, not a guaranteed signed min/max.

At 1 A, allocating 74 mΩ mux resistance, ±20 mV ripple, 5 mV PCB drop and ±5 mV additional regulation gives MCU3V3 **3.14159–3.43594 V**, within 3.135–3.465 V. Lower calculated reserve is only 6.6 mV: the allocated ripple/drop/regulation and temperature assumptions require later verification. A 31.2 kΩ/25 ppm screening case reaches about 3.1013 V and was rejected. Do not substitute ordinary 1%/100 ppm feedback resistors.

C33/C45 remain 22 µF each but change from generic 0805 to **TDK C3216X5R1V226M160AC, 22 µF/35 V X5R 20%, 1206**. This deliberate footprint/grade change supports the ripple budget. Ceff is not established by nominal capacitance. C32/C43 normal-buck input Ceff remains an existing qualification item.

## F5 topology and mappings

U7 TPS62933DRLR: pin 1 RT intentionally floating (500 kHz nominal); 2 EN = F5_EN; 3 VIN = SYS; 4 GND = PGND; 5 SW = F5_SW; 6 BST = F5_BST; 7 SS = F5_SS; 8 FB = F5_FB. L3 links SW to F5_RAW. R60/R61 sense RAW, before the blocker; R62/R63 enable the buck from SYS. C62 is BST-to-SW, C63 SS-to-PGND.

U8 LM74700QDBVRQ1: pin 1 VCAP = F5_VCAP, 2 GND = PGND, 3 EN and 6 ANODE = F5_RAW, 4 CATHODE = F5_5V_OUT, 5 GATE = F5_GATE. C67 is **VCAP-to-ANODE**, not ground. Q10 AON7528: pins 1–3 source = RAW, 4 gate, 5–9 drain = OUT including exposed drain pad. Its body diode conducts RAW→OUT and blocks OUT→RAW when off. J8 pin 1 = OUT, pin 2 = PGND. Connector and transistor physical pads were read back independently from assigned footprints.

An ideal-diode controller plus one MOSFET is used to meet reverse blocking without the voltage loss of a simple Schottky. No extra eFuse, latch, supervisor, firmware control or MCU/USB connection is added. With SYS absent and external voltage on J8, the MOSFET orientation/controller provide reverse blocking; feedback is on RAW and does not bypass the blocker. Leakage and finite reverse turn-off transients are not zero. Datasheet reverse-response specifications apply only under their stated conditions; hot-plug/reverse-current waveforms remain hardware qualification.

All **19 fitted F5 parts** are omitted in F0: U7/U8/Q10/L3/R60–R63/C60–C69/J8. TP17 is isolated copper in F0. No bypass link is fitted. The XML assembly projection confirms F5 attaches to the retained circuit only at SYS and PGND. This is a population/net-connectivity projection, not a separately ERC-checked F0 schematic. Existing charger/cell and backup-DNP rules still apply.

## F5 calculated envelope and limitations

R60 = 53 kΩ, R61 = 10 kΩ, both 0.1%/25 ppm/°C or better. Nominal RAW = 5.04 V; full-temperature static screen = **4.89714–5.18461 V** using the same reference/leakage method. At 2 A, allocations of blocker ≤50 mV, ripple ±20 mV, PCB loss ≤30 mV and additional regulation ±10 mV yield **4.78714–5.21461 V at J8**, within 4.75–5.25 V. These are design allocations, not newly imposed product gates or measured guaranteed limits.

L3 Coilcraft XAL5050-682MEC: 6.8 µH ±20%, DCR max 29.45 mΩ at 25 °C, Isat 6 A at 30% inductance loss, Irms 4.7 A at 20 °C rise. At SYS18 V, fmin 423 kHz (450 kHz lower bound with −6% temperature screen), Lmin5.44 µH: ripple 1.604 A p-p, peak 2.802 A, rms 2.053 A. Compare minimum HS current limit 4.2 A and minimum LS **valley** limit 2.9 A against peak/valley respectively. The 5.8 A maximum current-limit case versus room-temperature Isat is not a hot fault qualification. Hot copper sensitivity at125 °C gives DCR41.0 mΩ and loss0.173 W.

C64/C65 are the same 2×22 µF/35 V TDK pair as the TI 5 V reference design. TI's example uses 25 µF effective output capacitance; at 25 µF/2 mΩ ESR the calculated ripple is22.2 mV p-p, and at15 µF it is34.8 mV p-p. Manufacturer bias/aging/temperature curves were not successfully retrieved, so these remain sensitivities rather than a guaranteed capacitor bound. X5R capacitor body temperature must stay within its −55…85 °C rating. Buck junction-temperature capability does not extend capacitor rating. Stability, startup and load-step behavior require the final PCB and actual capacitors.

C60/C61 = 2×10 µF/50 V X7R Murata GRM32ER71H106KA12L. A conservative input-Ceff screen uses 0.9 tolerance ×0.52 bias factor (published ADI example at28 V, reused conservatively at18 V) ×0.85 temperature ×0.9 aging, giving7.16 µF and about0.165 V p-p input ripple. This is not a manufacturer-guaranteed combined bound. Local layout and measured SYS/source ripple must validate it.

At SYS6 V the converter must use near-dropout frequency foldback. A hot sensitivity doubling typical HS/LS Rds(on)76/32 mΩ, hot L3 DCR,100 mV input ripple peak and20 mV input trace loss gives required duty0.9458. Typical extended on-time7 µs/off-time140 ns permits0.9804 and calculated RAW maximum5.382 V, above the5.185 V high setpoint. This supports feasibility; typical switch resistance/on-time are not guaranteed production extremes. TI's 5V/3A reference specifies input down to5.5 V and documents foldback/dropout. Confirm6 V/2 A at hot conditions on matching hardware.

R62/R63 =100 kΩ/38.3 kΩ1%, yielding EN≈5.043 V at SYS18 V and nominal start≈4.3 V. Divider tolerance/drift must retain the5.5 V EN limit; no externally driven EN net exists. C63=33 nF gives typical4.8 ms soft start. LM74700 typical linear-drop regulation has datasheet range13–29 mV; Q10 has2 mΩ maximum at10 V gate/25 °C and2.9 mΩ at125 °C. A50 mV total blocker allowance gives≤0.1 W at2 A. Controller VCAP maximum13.9 V is below Q10±20 V gate rating; C67=100 nF/50 V.

Thermal sensitivity: assumed buck loss0.85 W includes doubled typical conduction resistance, assumed40 ns summed switching transition at18 V/2 A and switching frequency up to583 kHz, plus switching/gate/dead-time allowance. These transition/loss assumptions are not guaranteed datasheet maxima. At50 °C ambient, TI EVM60.2 °C/W gives junction≈101 °C; JEDEC112.2 °C/W gives≈145 °C. TI warns JEDEC thermal metrics do not predict the actual board. Proper local loops/copper and measured temperatures are essential; this calculation does not approve continuous2 A on an unspecified layout.

## Service and power test access

TP5 TX, TP6 RX, TP7 PGND, TP8 MCU3V3 sense, TP9 MCU_EN/RESET, TP10 MCU_BOOT. Proposed top-side PCB-edge row in that order,2.54 mm pitch,1.5 mm copper pads; triangle atTP5 and asymmetric fixture key. Near-board-edge access is required; final edge setback/keepouts/access must account for routing, mounting holes and the ESP32 antenna keepout during PCB work. Schematic coordinates are not placement instructions.

Secondary MCU group: TP11 SDA, TP12 SCL, TP13 MAIN_3V3. TP14 CE_N is a separate **charger-domain passive probe**, outside the MCU fixture. High-energy group TP15 VIN1, TP16 BATTERY and existing TP4 SYS must be physically separated from the logic row, with clear labels and probe clearance. TP17 OUT belongs near J8. All are bare copper footprints with no paste, not fitted components or authorized power inputs. Fixture must remain high impedance until target MCU3V3 is valid, use existing main/USB power, and avoid injecting UART/I²C/RESET/BOOT into an unpowered MCU. Existing isolation circuitry is unchanged; direct test access does not add automatic injection protection.

## Verification and next boundary

Independent `verify_phase3_6.py` compares entry XML against the accepted Phase3.5 netlist, then checks final XML: **156 components, all375 retained pin nets preserved**, prior component properties preserved except the explicit R32/R33/C33/C45 metadata allowlist; new F5 pin maps and F0 projection pass. Fresh ERC: **0 errors /4 existing isolated-label warnings** (MCU_STATUS_LED, MCU_GPIO1, MCU_GPIO7, MCU_GPIO10). UART warnings are resolved by physical pads. PDF/PNG were exported after the last CAD mutation and checked visually. Q10 inherited external footprint has no courtyard; add/qualify its courtyard and manufacturer land pattern through Konnect during footprint/layout work. U7/U8/L3/J8/testpad pad identities pass readback; this does not establish routing, mechanical or thermal correctness.

No V4 PCB exists: DRC and schematic/PCB parity are **not applicable yet**, mandatory before release. Ordinary sourcing remains provisional, especially feedback resistors and L3 preferred-supplier availability. Footprint-defining connector/NTC/harness choices must be resolved before freeze. The schematic is ready for provisional owner review and a separately authorized PCB milestone. **VAC1 hot-plug fabrication/power-up block and BQ25792 2S default2A risk remain OPEN**, unchanged by this work. No hardware validation performed. `git diff --check` is clean for documentation/scripts; full CAD diff flags tab-only blank lines emitted by Konnect serialization. They were not manually edited under the CAD-only-through-Konnect rule; connectivity/ERC evidence is unaffected. Full schematic diff also includes serializer reordering and preserved prior changes; the independent XML comparison is the electrical scope check.

## Primary references reviewed 2026-10-10

- [TI TPS62933 datasheet](https://www.ti.com/lit/ds/symlink/tps62933.pdf), SLUSEA4D RevD Aug2022: pinout/limits, electrical characteristics, dropout/foldback, application table10-2 and layout. Reference capacitance is an example, not an actual-board measurement.
- [TI LM74700-Q1 datasheet](https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf), SNOSD17G RevG Dec2020: DBV pinout, limits/electrical table, sections9.3/10.1/12.
- [AOS AON7528 datasheet](https://www.aosmd.com/res/data_sheets/AON7528.pdf), Rev1.0 Oct2023 pp1–3: pinout, voltage/current/gate resistance and thermal conditions.
- [Coilcraft XAL50xx](https://www.coilcraft.com/getmedia/49bc46c8-4b2c-45b9-9b6c-2eaa235ea698/xal50xx.pdf), Document908-1 revised2026-02-26: XAL5050-682MEC table, saturation/rise definitions and mechanical drawing.
- [TI TPS2116](https://www.ti.com/lit/ds/symlink/tps2116.pdf), SLVSFG1A RevA May2021, electrical characteristics: mux resistance;74 mΩ used conservatively instead of59 mΩ at3.3 V.
- [Phoenix1757242](https://www.phoenixcontact.com/fr-pc/produits/connecteur-pour-ci-mstba-25-2-g-508-1757242):12 A,5.08 mm pitch,1.4 mm drill.
- [ADI MAXREFDES1102](https://www.analog.com/en/resources/reference-designs/maxrefdes1102.html), input capacitor discussion: Murata10 µF part bias example. Used as an explicitly conditional screening factor.

Exact source identities, supplier observations and unresolved alternatives are in [BOM review](../V4_BOM_REVIEW.md). Re-run exports/ERC/independent verification after any subsequent CAD change.
