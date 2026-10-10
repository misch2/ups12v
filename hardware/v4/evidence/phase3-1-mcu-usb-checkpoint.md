# Phase 3.1 MCU/native-USB schematic checkpoint

Date: 2026-10-10  
Scope owner: schematic build checkpoint  
Status: **INCOMPLETE bounded checkpoint; power-domain integration, preservation
projection and package qualification remain open**

## Scope

This checkpoint adds the ESP32-C3-MINI-1 native USB/recovery boundary to the
accepted charger/power-stage schematic. It intentionally stops before the
VSYS-derived 3.3 V buck, USB-derived 3.3 V buck, TPS2116 mux and TCA9517 I2C
isolation. `MCU3V3` is therefore a reserved input net only, and `USB_VBUS` is
the USB connector input before the deferred USB regulator.

## CAD changes

- Added U1 custom `ESP32-C3-MINI-1` symbol with all 53 module pins and the
  manufacturer pin map from Espressif ESP32-C3-MINI-1/MINI-1U Datasheet v2.2,
  Table 3-1 / Figure 3-1.
- Connected U1 3V3 to `MCU3V3`, all 22 module GND lands to `PGND`, native USB
  GPIO18/USB_D- (pin 26) to `USB_DN` and GPIO19/USB_D+ (pin 27) to `USB_DP`.
- Added the USB-C receptacle J7 and rail-less TI TPD2EUSB30A ESD device U2.
  TI TPD2EUSB30A (SLVSAC2G Rev. G, June 2021, §5/Table 5-1) maps D+ to
  pin 1, D- to pin 2 and GND to pin 3; it has no VBUS clamp pin. CC pulldowns
  are R13/R14, USB VBUS capacitors are C27/C28, BOOT/RESET switches are
  SW1/SW2, strap/reset resistors are R15-R18 and EN capacitor C29 is 1 uF
  provisional per the Espressif C3 schematic checklist.
- Added local `MCU3V3` decoupling C30 (10 uF) and C31 (100 nF), each with a
  `PGND` return. Exact capacitor MPNs remain open.
- Added USB SBU no-connect markers and no-connect markers for the module NC
  pins. GPIO2/GPIO8/GPIO9 and EN remain explicitly labelled for the next
  firmware/power-domain qualification.
- Added a visible phase-boundary note on the sheet. No PCB synchronization or
  footprint placement was performed.

## Validation evidence

All paths below are relative to `hardware/v4/`:

- `evidence/phase3-1-mcu-usb.net.xml`: fresh KiCad netlist export.
- `evidence/phase3-1-mcu-usb.bom.csv`: fresh BOM export including MPN,
  manufacturer, population and approval fields.
- `evidence/phase3-1-mcu-usb.png` and `evidence/phase3-1-mcu-usb.pdf`: fresh
  render/export inspected for placement and overlap at checkpoint scale.
- `evidence/phase3-1-erc.json`: KiCad 10.0.7 ERC response at warning severity.
  It reports 1 error and 10 warnings. The sole error is expected at this
  boundary: U1 pin 3 (`MCU3V3`) is not yet driven because its buck/mux source
  is deferred. The ten warnings are isolated labels for intentionally reserved
  UART/GPIO/service interfaces. Avoidable off-grid, dangling no-connect,
  missing-footprint and rail-clamp warnings were removed.
- `evidence/phase3-1-erc-errors.json`: error-only ERC evidence, 1 error (the
  deferred `MCU3V3` source).

Fresh structural checks after the final MCU pin-grid and USB routing repair:

| Check | Result |
| --- | --- |
| `validate_component_connections` (U1, J7, U2, SW1/2, R13-R18, C27-C31) | valid; 0 unconnected pins |
| `validate_wire_connections` | valid; 0 floating endpoints |
| `USB_VBUS` | J7 VBUS x4 and C27/C28; U2 intentionally has no VBUS pin |
| `USB_DP` / `USB_DN` | J7 duplicated D+/D- contacts, U2 pins 1/2 and U1 GPIO19/GPIO18 respectively |
| `USB_CC1` / `USB_CC2` | each connector CC contact to a 5.1 kOhm pulldown |
| `MCU_BOOT`, `MCU_EN`, `MCU_BOOT_STRAP2`, `MCU_BOOT_STRAP8` | U1, bias/control parts and GND switches connected |
| `MCU3V3` local bypass | U1 pin 3, C30/C31 pin 1; C30/C31 pin 2 to PGND |

`find_single_pin_nets` reports ten one-pin global-label nets (`MCU_CHG_ARM`,
`MCU_GPIO0`, `MCU_GPIO1`, `MCU_GPIO10`, `MCU_INT`, `MCU_SCL`, `MCU_SDA`,
`MCU_STATUS_LED`, `UART_RX`, `UART_TX`). These are intentional reserved
interfaces for the deferred charger-control/I2C and service-interface blocks,
not claimed end-to-end connections.

## Open items carried forward

1. The current global `Modules_MCU:ESP32-C3-MINI-1` footprint readback is
   **blocked pending exact land-pattern comparison**. The physical readback
   records 62 pads, 60 unique pad numbers (duplicate ground numbers) and no
   courtyard; this count alone does not establish invalidity. Compare every
   physical land and mechanical feature with the selected Espressif suffix,
   then replace or qualify the footprint before any PCB work.
2. The source for `MCU3V3` is intentionally absent in this checkpoint. The
   next checkpoint must add the VSYS and USB buck outputs, normal-priority
   mux, and power-good/current-domain evidence before ERC can be considered
   clean.
3. USB VBUS input capability, ESD placement, USB-C connector suffix, switch
   exact MPN, pull-up/pull-down tolerances, reset timing and native USB
   firmware behavior remain schematic/provisional. The TPD2EUSB30A pin map
   is supported by the cited TI revision; procurement and package approval are
   still open.
4. No hardware measurement, USB enumeration, power-domain leakage test or
   partial-power/back-power qualification is claimed.

No PCB layout, fabrication output or hardware power-up is authorized by this
checkpoint. Parent preservation projection passed on the final fresh XML:
57 original references / 157 connected pins retain every prior partition;
existing values, footprints and exported fields are unchanged. See
`phase3-1-preservation.json`. The deferred power-domain checkpoint and module
footprint qualification remain required before the overall milestone is complete.
