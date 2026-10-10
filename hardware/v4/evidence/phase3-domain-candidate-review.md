# Power-domain candidate review: qualification remains OPEN

2026-10-10. Bounded read-only check of the architecture's existing candidates; no new component selection, sourcing sweep or CAD changes. This note does not approve the candidates or change R07.

## TPS2116DRLR

TI SLVSFG1A, revised May 2021, verified at https://www.ti.com/lit/gpn/tps2116 . Sections 5 and 7.6.1 support a hardware-priority topology: normal3V3 on VIN1, USB3V3 on VIN2, MODE on VIN1 and a VIN1-owned PR1 divider; MCU supply on VOUT. ST should remain unconnected unless its powered-domain treatment is justified.

Section 7.3.4 describes finite reverse-blocking thresholds. Section 6.5's IREV test condition is VOUT=5.5 V, one input=0 V, the other open; this alone does not establish maximum total board injection in the actual USB-powered topology. Do not substitute typical leakage for a guaranteed maximum.

Section 7.4 warns that collapse faster than 1 V/10 us needs the surviving supply at least 2.5 V to prevent device reset. Section 7.6.1 uses break-before-make; hold-up capacitance, actual peak MCU current, source mismatch and switchover duration must support the minimum MCU voltage. The regulator voltage-error budget must include mux resistance and interconnect drop.

Status: architecture candidate retained; worst-case leakage, transition reverse pulses and reset-free transfer remain unqualified.

## TCA9517DGKR

TI SCPS242D, revised July 2017, verified at https://www.ti.com/lit/gpn/tca9517 . Section 3 specifies powered-off high-impedance I2C pins; sections 3/9 describe supply ownership and enable behavior. The proposed split is A supply/pull-ups on MCU3V3 and B supply/pull-ups on MAIN_3V3, with a main-owned safe enable. This is signal separation, not galvanic isolation.

Section 7.5 gives output-high leakage of 10 uA per I2C pin under VCCB=2.7–5.5 V. That entry is not an explicit VCCB=0 partial-power injection bound. It must not be used to assert the whole-board <=10 uA R07 target. Powered-high leakage is not automatically current injected into the main rail either. Establish the actual paths and applicable maximum limits before claiming a budget pass.

The B-side output offset also requires checking against BQ input-low thresholds, pull-up currents, rise time and cascaded-buffer restrictions. The architecture candidate remains provisional; any missing guaranteed off-state bounds need further manufacturer evidence, a suitable alternative, or an explicit requirement review. No relaxation is made here.

## Required schematic and prototype evidence

- Keep USB/main converter outputs separate before the mux. No USB/main wire, shared pull-up or control connection may bypass it.
- Check both partial-power directions for I2C, CE request, INT, straps, reset, UART/test headers and any source/status sensing. Gate insulation alone does not establish maximum leakage or harmless dynamic coupling.
- ROM USB recovery must remain independent of the charger and a stuck bus. UART is a powered-target interface with MCU3V3 sense, not an external power input; enforce this if no Ioff isolation is fitted.
- Account for every injected current at 25 C and worst operating temperature. Validate the absent-source rail with the specified temporary 10 kohm load, and record dynamic pulses separately. No hardware measurement or electrical acceptance is claimed.
