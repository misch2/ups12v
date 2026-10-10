# Phase 3.2 MCU power-domain and isolation checkpoint

Date: 2026-10-10  
Status: schematic checkpoint; no PCB, fabrication, or power-up approval.

## Implemented topology

- U3 is a TI TPS62933DRLR 3 A buck candidate from SYS to MAIN_3V3.
- U4 is an independent TPS62933DRLR 3 A buck candidate from USB_VBUS to
  USB3V3. The two switch nodes, bootstrap capacitors, soft-start capacitors,
  feedback dividers and input/output capacitors are separate.
- U5 is a TPS2116DRL mux. VIN1 and MODE are MAIN_3V3, VIN2 is USB3V3, and
  VOUT is MCU3V3. The former PR1 divider was removed. R23 is now a 10 kOhm
  pull-up from MAIN_3V3 to the digital MUX_PR1/MAIN_VALID node. U7 is a
  TPS389033DSET fixed 3.17 V supervisor powered from MAIN_3V3; its independent
  SENSE and MR inputs also monitor MAIN_3V3, and its open-drain RESET sinks PR1
  below the valid-main threshold. MAIN-powered MR/VDD avoids a normal-only
  startup deadlock: the supervisor is off while MAIN is absent and releases
  PR1 only after MAIN is valid.
- U6 is the original (non-A) TCA9517DGKR, Rev. D. VCCA/A and its 4.7 kOhm
  pull-ups are MAIN_3V3 for the charger-facing BQ25798 bus; VCCB/B and its
  4.7 kOhm pull-ups are MCU3V3 for the ESP32-C3 bus. The original Rev. D data
  sheet does not impose the later VCCA <= VCCB restriction. EN is `TCA_EN`,
  driven by a fail-low two-MOS network: Q8 pulls `NEN` low from MAIN_VALID,
  and Q9 pulls `TCA_EN` low while MAIN_VALID is absent; R51/R52 pull both
  nodes to MCU3V3. This contains the TCA9517 internal EN pull-up on the MCU
  domain during USB-only operation. BQ25798 Rev. C section 6.5 gives a
  0.4 V I2C VIL maximum under its 1.8 V test condition, while the TCA9517
  A-side low-level specification is the safer charger-facing side; the
  B-side ESP32 VOL margin and the 3.3 V pull-up condition remain a hardware
  qualification item. Partial-power R07 leakage is not fully specified.
- Q5/Q6/Q7 gate the existing charger CE sink. Q5 can source CHG_GATE only
  from MAIN_3V3; U7-released MUX_PR1 (MAIN_VALID) drives Q6 through R50 and
  Q7 accepts firmware MCU_CHG_ARM through R46, forming a series authorization
  path through CHG_AND. R53 (10 kOhm) now limits Q5 base current between Q6
  and the Q5 base node; R44 remains the Q5 base-emitter pull-up. R47 provides
  a 100 kOhm default pulldown on the firmware transistor base. MCU_CHG_ARM is
  assigned to ESP32-C3 GPIO0/pad 12; GPIO7/pad 21 is retained as MCU_GPIO7.
  R11.2 is a no-connect DNP service sense, so external J4 CHG_REQ cannot
  enable charging. Thus both a normal valid domain and firmware authorization
  are required; neither USB-only VBUS nor a reset/high-impedance MCU GPIO can
  enable charging. U8 is a second TPS389033DSET, powered by MCU3V3 but
  sensing MAIN_3V3 independently. Its open-drain `CHG_LATCH_CLR_N` output
  asynchronously clears U9, an SN74LVC1G74DCTR edge latch. U9 has D and /PRE
  tied high, CLK on the fresh rising edge of GPIO0, and Q feeding the existing
  R46/R47 live-arm node. A retained GPIO-high level therefore cannot
  re-enable CE when MAIN returns: MAIN loss clears Q, and a new firmware arm
  edge is required. Q10 is a third BC847 sink in series with Q7, driven by
  the live GPIO0 path through R46 and held low by R55; this makes the latch
  authorization and the current firmware level independent series permissions.
  D5 also clears the latch when MCU_EN is asserted low. U12 is an
  SN74LVC1G17 Schmitt buffer between the U8/R54 open-drain clear node and U9
  /CLR, satisfying the SN74LVC1G74 input-transition requirement during the
  slow supervisor release.
- U11 is a TI TPS389001DSET adjustable MCU3V3 supervisor. R56/R57 (16.7 kOhm
  / 10 kOhm, 0.1%) set the nominal 3.0705 V falling / 3.0892 V rising
  threshold and drive MCU_EN low during U10 startup or MCU rail collapse.
  This is a real MCU-domain brownout gate; the prior unverified TPS389031
  fixed-part suggestion is not used.
- U5 now feeds `MCU_PRE3V3`; U10 is a TPS22975DSGR post-mux slew-controlled
  load switch with VIN/VBIAS/ON on that pre-rail and VOUT on MCU3V3. C51 is
  22 uF before U10, C49 is a 470 uF 6.3 V hold-up fit candidate after U10,
  and C50 is the 47 nF, 30 V CT candidate. This keeps mux/source input
  capacitance small for USB startup while providing a controlled output
  charge path. The TPS22975 rise-time equation is specified for VBIAS=5 V;
  the 3.3 V ramp, effective C49, ESR, switch RON and source-removal margin
  remain qualification gates, so this checkpoint does not claim reset-free
  transfer yet.

## Electrical checks and limits

TI TPS62933 Rev. D (August 2022), Sections 5-8 and 10.2.2.5/10.3, specifies
3.8-30 V input operation, 3 A output capability, a 0.8 V feedback reference,
precision EN thresholds, and the bootstrap/soft-start requirements. The
schematic uses 100 kOhm/38.3 kOhm normal-EN and 100 kOhm/47 kOhm USB-EN
dividers, 32.2 kOhm/10 kOhm 0.1%
feedback dividers, 4.7 uH inductors, 2.2 uF plus 100 nF input decoupling, two 22 uF
output candidates per buck, 100 nF 25 V bootstrap capacitors and 33 nF
soft-start capacitors. MCU3V3 has C36 22 uF local bulk, the ESP32 10 uF plus
100 nF local bypasses and the TCA9517 100 nF VCCB bypass. C49 is a 470 uF
6.3 V fit candidate (DNP=NO) after U10 for source-removal testing. The
two 22 uF output parts provide a 44 uF nominal bank against the datasheet's
40 uF typical 3.3 V/500 kHz recommendation; their DC-bias effective
capacitance, ripple current, thermal loss, USB inrush and ESP32-C3 RF/USB
burst load still require measurement. With 500 kHz and 4.7 uH, the inductor
ripple estimate is `dI = (3.3 V / (4.7 uH * 500 kHz)) * (1 - 3.3 V/VIN)`:
about 0.19 A at 3.8 V, 0.48 A at 5 V and 1.02 A at 12 V. The 3 A buck
class and 2.5 A mux class therefore have ample prototype current class for
the ESP32-C3 burst, subject to current-limit, thermal, Ceff and trace
validation; this does not claim a measured module peak. The USB regulator
therefore has nominal cable-drop headroom that the previous 4.75 V
minimum-input candidate did not have.

The TPS62933 Rev. D EN table gives a 1.21 V minimum / 1.28 V maximum rising
threshold and 0.7 uA typical EN pull-up current at 1.0 V. The USB divider's
100 kOhm/47 kOhm choice gives about 3.79 V at the typical threshold and about
4.01 V at the maximum threshold before resistor tolerance and pull-up-current
effects; this is materially below a 4.4 V legacy USB/cable-drop case. The
normal 100 kOhm/38.3 kOhm divider remains about 4.38 V typical and is used for
the 3.8 V minimum SYS buck input. Both EN nodes stay below the 5.5 V absolute
domain under the 21 V input case; exact tolerance/current corners remain part
of converter startup qualification.

For the TPS62933 full-temperature 0.784-0.816 V feedback range, 32.2 kOhm
and 10 kOhm 0.1% dividers give a conservative 3.299-3.454 V range after
including the 0.15 uA feedback leak (about 4.83 mV across 32.2 kOhm) and
resistor tolerance. Allowing the TPS2116 74 mOhm maximum on-resistance at 1 A
and a conservative 34 mOhm post-mux switch allowance gives about 3.191 V at
MCU3V3 before PCB trace drop. This leaves about 56 mV to the 3.135 V MCU
minimum. The TPS22975 16 mOhm value is typical, not a guaranteed maximum, so
the normal rail setpoint, load-switch RON, trace drop and 2.5 A transient
must be measured together. MAIN must still exceed the TPS389033 3.220 V
release maximum for normal startup, and U11 holds MCU_EN low until its
approximately 3.09 V rising threshold is met. Source-removal/reset-free
behavior remains an explicit hardware gate.

TI TPS2116 Rev. A (May 2021), Sections 5-8, specifies a 0.92-1.08 V PR1
reference, reverse-current blocking, break-before-make operation and a typical
2 us response. The earlier 19.1 kOhm/10 kOhm divider was removed because its
reference tolerance could not guarantee the required selection window. R23 is
now a 10 kOhm pull-up from MAIN_3V3 to the digital MUX_PR1/MAIN_VALID node;
U7's open-drain RESET holds that node low until its fixed 3.17 V falling /
3.189 V rising threshold is met. R50 loads the node only through the Q6 base
(about 20-25 uA in the candidate digital bias model), leaving PR1 well above the TPS2116
1.08 V maximum reference at the minimum valid MAIN rail. U7's 18 us typical
falling propagation and 10 nF CT delay are recorded in the schematic.
Normal startup is autonomous because U7 VDD/MR are MAIN-powered. U10's
47 nF CT is a starting candidate: applying the data-sheet VBIAS=5 V slope
equation (`0.43*47000 pF + 26`) gives about 20.236 ms/V; using the
data-sheet 0.8*VIN*SR approximation gives about 53.4 ms for a 3.3 V ramp,
or roughly 29 mA into 470 uF before ESR and converter behavior. The equation's table is
for a steady VIN/VBIAS before ON, so VBIAS=3.3 V and the actual pre-rail ramp
must be qualified. C49 effective capacitance, ESR, USB host inrush, mux
break-before-make and worst-case supervisor timing still require matching
hardware. No reset-free claim is made from the nominal C49 value alone.

U8/U9 source-return sequence is deliberate: while USB-only, MAIN is absent
and U8 holds `CHG_LATCH_CLR_N` low, so Q=0 even if firmware retained GPIO0
high. When MAIN returns, U8 releases CLR only after its MAIN sense threshold,
but U9 remains cleared until firmware issues a new GPIO0 rising edge after
charger configuration. A firmware reset that leaves GPIO0 low disables the
third sink Q10 through R46/R55; D5 provides the MCU_EN-low clear path.

TI TCA9517 original Rev. D, Sections 3, 5, 7.5 and 9, specifies the 0.9-5.5 V
VCCA domain, 2.7-5.5 V VCCB domain, EN behavior and powered-off high-Z
operation; the original revision does not carry the later A-revision
VCCA <= VCCB restriction. MAIN_3V3 is on VCCA/A and MCU3V3 is on VCCB/B.
The Q8/Q9/R51/R52 network drives EN from the MCU rail but forces it low when
MAIN_VALID is absent, so the internal EN pull-up cannot back-bias MAIN during
USB-only operation. The charger-facing A-side low-level margin must be checked
against BQ25798 Rev. C section 6.5 (0.4 V VIL test condition); the ESP32 B-side
VOL margin, FET gate leakage, EN timing and aggregate R07 partial-power limit
remain bench items. With 4.7 kOhm pull-ups, the nominal sink is about 0.70 mA.
The TCA9517 A-side VOL(max) 0.2 V at 6 mA is below the charger VIL(max) 0.4 V;
the B-side VOL(max) 0.6 V is below the ESP32-C3 VIL(max) 0.25*VDD at a 3.0 V
rail. Using `t_r ~= 0.8473*R*C`, 400 kHz's 300 ns rise-time budget supports
about 75 pF total bus capacitance and 100 kHz's 1 us budget supports about
250 pF. Firmware should begin at 100 kHz and select 400 kHz only after measured
bus capacitance and edge timing support it.

## USB recovery and cross-domain review

USB D+/D- remain a matched logical pair with the rail-less TPD2EUSB30A
candidate shunting to PGND on the connector-side pair; U2 uses the exact
`Package_TO_SOT_SMD:Texas_DRT-3` footprint and TI SLVSAC2G Rev. G pin map
(D+ 1, D- 2, GND 3). R48/R49 are populated
0 Ohm default series links between that pair and U1 USB_D+/USB_D-, with 22 Ohm
as an optional signal-integrity value; this preserves native USB recovery in
the default assembly. USB-C CC pulldowns, BOOT
straps and EN/RESET controls remain in the Phase 3.1 schematic. The USB path
is USB_VBUS -> U4 -> USB3V3 -> U5 VIN2 -> MCU3V3;
there is no USB path to SYS, BATTERY, REGN or MAIN_3V3. Charger
configuration is gated by U7-released MAIN_VALID and firmware MCU_CHG_ARM;
the external J4 CHG_REQ branch is DNP service sense only.

UART, INT, I2C, strap and charger GPIO paths were checked for direct clamp
paths into the normal domain. The isolated INT transistor remains on its
existing path. TCA9517 EN is fail-low and MCU-powered through Q8/Q9/R51/R52;
the charger request resistors feed transistor bases only. GPIO0/pad12 is the
charge arm and firmware must leave it input/low until charger configuration;
GPIO7/pad21 is no longer the charge arm, avoiding a ROM/JTAG default-high
assumption.

## Module and verification status

The exact orderable module target is Espressif ESP32-C3-MINI-1-N4X. Espressif
Datasheet v2.2 Table 1-1 marks N4X as recommended and the older N4 as NRND.
Section 11.1 Figure 11-1 calls for 48 edge lands of 0.4 x 0.8 mm, four
0.7 mm corner lands and nine segmented central ground lands, all electrically
pad 49. The project-local ups_v4:ESP32-C3-MINI-1-N4X footprint was created
through Konnect with 61 physical pads (53 unique pad numbers, including nine
pad-49 segments at +/-1.975 mm centers forming the 5.4 mm central array) and
a courtyard. The prior global footprint with pads 54-60 and duplicate
non-symbol numbers is no longer used. The geometric comparison source is
`evidence/references/esp32-c3-mini-1-v2.2.pdf` and its extracted
`esp32-c3-mini-1-v2.2-land.png`; PCB placement and antenna keepout review
remain deferred.

Fresh KiCad 10.0.7 ERC reports 0 errors and six intentional isolated-label
warnings for UART_RX, UART_TX, MCU_STATUS_LED, MCU_GPIO7, MCU_GPIO1 and
MCU_GPIO10. Konnect connectivity validation reports zero floating wire ends
and zero unconnected component pins. The current schematic SHA256 is
`16fac2064661cb20d4dc02f98dfe73389b993f50588e46b57c967e7c445d651a`.
Fresh XML, BOM, preservation evidence and render are kept beside this file;
verify_phase3_2_preservation.py records the complete Phase 2.6 partition check,
the intentional R11.2 service no-connect, the MAIN_VALID/R50 addition and the
explicit U6/Q8/Q9/U1 GPIO cross-domain rewires.

## Deferred gates

- Prove source-removal and insertion do not reset the MCU across the intended
  VSYS/USB voltage and load envelope, including the TPS2116 response, C49
  effective hold-up and worst-case timing.
- Measure TCA9517 partial-power leakage/back-bias, Q8/Q9 EN timing and confirm
  both-side I2C pull-up behavior and BQ25798 VIL/VOL margin with no battery or
  adapter.
- Confirm the 61-physical-pad/53-unique-pad N4X project footprint, including
  all nine pad-49 center segments and the 5.4 mm center array, against the
  manufacturer land-pattern source before any PCB work.
- Keep the unresolved VAC1 hot-plug transient issue as a later
  fabrication/power-up gate.
