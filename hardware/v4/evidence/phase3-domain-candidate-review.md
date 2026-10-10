# Power-domain candidate review: qualification remains OPEN

2026-10-10. Bounded review of the Phase 3.2 architecture and existing candidates;
CAD remains provisional and this note does not approve the candidates or change R07.

## TPS2116DRLR

TI SLVSFG1A, revised May 2021, verified at https://www.ti.com/lit/gpn/tps2116 . Sections 5 and 7.6.1 support a hardware-priority topology: normal3V3 on VIN1, USB3V3 on VIN2, MODE on VIN1 and a VIN1-owned PR1 divider; MCU supply on VOUT. ST should remain unconnected unless its powered-domain treatment is justified.

Section 7.3.4 describes finite reverse-blocking thresholds. Section 6.5's IREV test condition is VOUT=5.5 V, one input=0 V, the other open; this alone does not establish maximum total board injection in the actual USB-powered topology. Do not substitute typical leakage for a guaranteed maximum.

Section 7.4 warns that collapse faster than 1 V/10 us needs the surviving supply at least 2.5 V to prevent device reset. Section 7.6.1 uses break-before-make; hold-up capacitance, actual peak MCU current, source mismatch and switchover duration must support the minimum MCU voltage. The regulator voltage-error budget must include mux resistance and interconnect drop.

Status: architecture candidate retained; worst-case leakage, transition reverse pulses and reset-free transfer remain unqualified.

## MCU rail ramp, brownout and charge authorization

TI TPS22975 Rev.B (2017), Sections 5, 9.3 and 10.2, is provisionally placed
after the TPS2116. U5 output is `MCU_PRE3V3`; U10 VIN/VBIAS/ON use that rail,
U10 VOUT feeds `MCU3V3`, C51 is 22 uF before the switch and C49 is a 470 uF
fit candidate after it. C50 is 47 nF, 30 V on CT. The data-sheet slew
equation is specified for a steady 5 V VBIAS before ON; at 47 nF it estimates
20.236 ms/V and about 53.4 ms for 3.3 V using the stated approximation. The
3.3 V VBIAS startup, actual C49 effective capacitance/ESR, switch maximum RON,
USB inrush and source-removal hold-up remain qualification gates.

The previous unverified TPS389031 suggestion is not used. TI TPS3890 Rev.A
lists TPS389001DSET as an active adjustable 1.15 V reference option; U11 uses
R56=16.7 kOhm and R57=10 kOhm, both 0.1%, for a nominal 3.0705 V falling /
3.0892 V rising MCU3V3 threshold. A conservative reference, divider and sense
leakage budget must keep MCU_EN asserted until the rail is within the ESP32
operating range. U12 is a TI SN74LVC1G17DBVR Schmitt buffer between the U8
open-drain clear node and the U9 SN74LVC1G74 CLR input; this avoids violating
the LVC1G74 10 ns/V input-transition limit during supervisor release.

U9 D and /PRE are high and CLK is the fresh GPIO0 arm edge. Q drives Q7's
latch sink, while Q10 is a third BC847 sink driven by the live GPIO0 level
through R46 and held low by R55. MAIN loss clears U9 through U8; return of MAIN
does not re-enable CE until a fresh firmware edge, and a low/reset GPIO still
blocks the series path. D5 provides the MCU_EN-low clear path. This is a
hardware authorization topology; timing, leakage and CE behavior remain open.

## Buck enable and inductor candidates

TI TPS62933 Rev.D EN data gives 1.21 V minimum / 1.28 V maximum rising
threshold and 0.7 uA typical pull-up at 1.0 V. R38/R39 are now 100 kOhm/47
kOhm on USB_EN, giving approximately 3.79 V typical and 4.01 V at the maximum
threshold before tolerance/current effects, preserving USB startup headroom.
The normal EN divider remains 100 kOhm/38.3 kOhm. The feedback top resistors
R32/R34 are 32.2 kOhm 0.1% with 10 kOhm bottoms; the bounded full-temperature
output range is approximately 3.299-3.454 V before mux/load-switch/trace drop.

L2/L3 use the project library `Inductor_SMD:L_Coilcraft_XAL5030-XXX` with
Coilcraft XAL5030-472MEC as the prototype candidate. Coilcraft product page
and Doc 908 specify 4.7 uH +/-20%, DCR max 40 mOhm, typical 6.7 A at 30%
inductance drop and 4.3 A at 20 C temperature rise. The estimated 3 A plus
about 0.51 A ripple peak is below that starting envelope; saturation, thermal
rise and the exact library land pattern remain open.

## TCA9517DGKR

TI SCPS242D, revised July 2017, verified at https://www.ti.com/lit/gpn/tca9517 . Section 3 specifies powered-off high-impedance I2C pins; sections 3/9 describe supply ownership and enable behavior. The implemented provisional split is A supply/pull-ups on MAIN_3V3 and B supply/pull-ups on MCU3V3. The original Rev.D is retained because the later variant's VCCA <= VCCB restriction would conflict with the normal TPS2116 drop. This is signal separation, not galvanic isolation. EN is not tied to MAIN directly: Q8/Q9 PMV16UN, R51 and R52 form a fail-low MCU-powered control. When MAIN_VALID is absent, Q8 is off, R51 raises NEN, Q9 pulls TCA_EN low; when MAIN_VALID is valid, Q8 pulls NEN low, Q9 releases and R52 raises TCA_EN. This specifically prevents the TCA9517's internal EN pull-up on VCCB from back-biasing MAIN through the enable input during USB-only operation.

Section 7.5 gives output-high leakage of 10 uA per I2C pin under VCCB=2.7–5.5 V. That entry is not an explicit VCCB=0 partial-power injection bound. It must not be used to assert the whole-board <=10 uA R07 target. Powered-high leakage is not automatically current injected into the main rail either. Establish the actual paths and applicable maximum limits before claiming a budget pass.

The A-side output offset is checked against BQ25798 Rev.C section 6.5's 0.4 V VIL(max) test condition: TCA9517 VOL(max) 0.2 V at 6 mA has nominal margin. The B-side TCA9517 VOL(max) 0.6 V is checked against ESP32-C3 VIL(max) 0.25*VDD at a 3.0 V rail. With 4.7 kOhm pull-ups, the nominal sink is about 0.70 mA; `t_r ~= 0.8473*R*C` gives roughly 75 pF at 400 kHz/300 ns and 250 pF at 100 kHz/1 us. Firmware should start at 100 kHz and only use 400 kHz after measured bus capacitance/edge timing supports it. The architecture remains provisional; FET leakage, EN timing and R07 aggregate off-state bounds still need hardware evidence.

## Required schematic and prototype evidence

- Keep USB/main converter outputs separate before the mux. No USB/main wire, shared pull-up or control connection may bypass it.
- Check both partial-power directions for I2C, CE request, INT, straps, reset, UART/test headers and any source/status sensing. Gate insulation alone does not establish maximum leakage or harmless dynamic coupling.
- ROM USB recovery must remain independent of the charger and a stuck bus. UART is a powered-target interface with MCU3V3 sense, not an external power input; enforce this if no Ioff isolation is fitted.
- Account for every injected current at 25 C and worst operating temperature. Validate the absent-source rail with the specified temporary 10 kohm load, and record dynamic pulses separately. No hardware measurement or electrical acceptance is claimed.
