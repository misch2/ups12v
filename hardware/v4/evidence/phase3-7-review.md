# Phase 3.7 — minimal emergency UART access

2026-10-10. Implements the latest owner clarification, superseding the Phase3.6 six-pad service row and additional RESET/BOOT/I²C pads. No PCB/layout, firmware, commit/push or hardware activity. CAD changes made exclusively through Konnect on the existing V4 branch.

Native ESP32-C3 **USB Serial/JTAG is the primary and sufficient interface** for programming, serial logging and debugging. USB-C continues to power the MCU during USB-only service. The USB circuit, mux, power-domain isolation, BOOT and RESET buttons are unchanged.

## Saved schematic changes

- Retain only optional emergency UART copper group: **TP5 ESP_TX (GPIO21), TP6 ESP_RX (GPIO20), TP7 GND**, in that order at2.54mm pitch near a board edge. No fitted header or VCC contact. Top-side view, triangle atTP5; fixture key/orientation must prevent reversed attachment. Final placement must respect mounting holes, routing and ESP32 antenna keepout.
- Remove TP9 MCU_EN, TP10 MCU_BOOT, TP11 MCU_SDA, TP12 MCU_SCL and their dedicated wire stubs/labels. Keep the existing BOOT/RESET buttons and MCU-domain I²C circuitry.
- Move TP8 MCU3V3 and TP13 MAIN_3V3 to a separate, clearly labeled voltage-measurement area in the schematic. In PCB layout they must be elsewhere, outside the UART row/fixture footprint. Neither is a supply input.
- Retain TP14 CE_N as the sole additional signal pad: a separate passive charger-domain probe useful for verifying charging remains disabled during reset/USB-only operation and enable sequencing. It is not connected to the UART fixture or an MCU pin. Existing power measurements TP4 SYS, TP15 VIN1, TP16 BATTERY and TP17 F5_OUT remain; high-energy probes stay separate from UART/logic access.

All nine retained Phase3.6 pads (TP5–TP8,TP13–TP17) are1.5mm bare copper footprints, no paste or purchased component. Missing reference numbers intentionally record removed pads; do not renumber unrelated references.

UART direction is from the ESP: TP5 connects to adapter RX, TP6 to adapter TX, TP7 to ground. Use3.3V logic with a powered target; connect no adapter VCC and keep external outputs high impedance while the target is unpowered. Target power comes from the established main or USB path. Direct GPIO pads have no automatic powered-off injection protection; the documented powered-target operating constraint prevents misuse without adding an unrequested isolation circuit. No UART connection reaches charger-side I²C/CE or bypasses existing power-domain isolation. No additional external supply path exists.

## Verification

Fresh KiCad10.0.7 ERC: **0 errors,4 unchanged isolated-label warnings** (MCU_STATUS_LED, MCU_GPIO1, MCU_GPIO7, MCU_GPIO10). TrueXML independent comparison against Phase3.6: **152 components,439 remaining exported pin entries unchanged**, exactly four removed testpoint instances/pins, no added pin connections. All non-pad component values/footprints/procurement fields remain identical; only TP5/TP6 displayed values and explicit pad-role metadata change. U1 pin31/TX/GPIO21 and pin30/RX/GPIO20 mappings checked from saved XML against the existing accepted module mapping. Each UART signal net contains only its intended MCU pin and pad. BOOT/RESET button connections, native USB, USB-only supply, F5 and the existing isolation circuit are preserved.

The original375 accepted Phase3.5 pin entries remain preserved transitively through the Phase3.6 baseline. F5 remains19 fitted parts inF5 and zero inF0, with only SYS/PGND joining the retained base; TP17 is isolated copper inF0. Voltage/thermal calculations and component pin-map evidence from [Phase3.6](phase3-6-review.md) remain applicable because every power component/property and remaining pin net is unchanged. They remain calculations, not hardware qualification.

Fresh [PDF](phase3-7-final.pdf), [PNG](phase3-7-final.png), [XML](phase3-7-final.net.xml), [ERC](phase3-7-final-erc.json), [verification/hashes](phase3-7-verification.json), [population](phase3-7-population.csv). Reproduce with `python hardware/v4/evidence/verify_phase3_7.py`. The service-area render was inspected and the three-pad UART row and separate voltage measurements are readable. Full evidence remains on disk; no obsolete pad groups are present in the current export. Documentation/script diff whitespace check passes; CAD serialization whitespace from the preceding checkpoint is unchanged in principle and is not hand-edited.

No V4 PCB exists, so DRC/parity remain not applicable yet and mandatory before release. This correction introduces no new schematic blocker for PCB planning; owner authorization is still required before layout. Existing footprint-defining harness/connector/NTC decisions, Q10 courtyard and procurement questions remain to resolve before freeze. **VAC1 hot-plug fabrication/power-up block and BQ25792 2S default2A risk remain OPEN.** No hardware measurements are claimed.
