# Goal

A hobby project to create a simple UPS to back up my router and mini PC. Both appliances use 12 volts on input. Version 4 is the current development version.

This UPS:
 - should be powered by two or four 18650 batteries in series, with a suitable protected and balanced battery pack
 - does not need to run for a long time, 15 minutes is perfectly OK, 30 minutes is luxury
 - should allow monitoring using Home Assistant, including charts of battery voltage, current, temperature and power
 - should support a router or a mini PC, with a target of 12 V / 3 A for the mini PC using a four-cell pack and an external converter
 - should run from the main source while it is available, charge the batteries within the available power budget and keep the load running when the main source fails

# Features

 - One PCB with assembly options for **BQ25792 or BQ25798** and **2S or 4S Li-ion packs**
 - Battery-backed **SYS output**, with an external converter selected for the attached device
 - Optional onboard **5 V / 2 A output** (F5 assembly); F0 leaves out the complete 5 V block
 - **ESP32-C3** monitoring and control, with MQTT discovery for Home Assistant
 - Battery voltage, charge/discharge current, temperature, charger state and fault monitoring
 - Configurable full-charge and reduced-voltage charge profiles, with a battery-specific charge-current limit
 - Charging disabled by hardware at startup, then enabled by firmware after configuration and readback checks
 - USB-C for initial programming, serial diagnostics and recovery; OTA for routine firmware updates

The output ratings above are prototype targets. Available load power and charging current share the same source, battery and thermal budget; the optional 5 V output does not add an independent power allowance.

# Version 4

V4 uses a **BQ25792 or BQ25798** buck-boost battery charger from Texas Instruments. It combines battery charging, a system power path and I2C monitoring on one board. An **ESP32-C3-MINI-1** module runs the monitoring and control firmware.

The same physical PCB supports two or four cells in series. The charger IC, cell-count resistor and optional 5 V block are selected when assembling the board; these are assembly variants, not separate PCB designs.

Product info: [BQ25792](https://www.ti.com/product/BQ25792), [BQ25798](https://www.ti.com/product/BQ25798).

## Principle

### Main power available

The main adapter supplies the charger, which powers the load through **SYS** and charges the battery with the remaining available power. Charging current must be reduced when the source cannot support both the load and charging.

The main input is intended for regulated 5, 9, 12, 15 or 20 V adapters, within the limits of the selected assembly and load. A USB-PD adapter can be used with an **external PD trigger** connected to the main input. The service USB-C connector is separate from this input.

### Main power lost

The battery supplies SYS through the charger's battery power path. SYS follows the battery/system operating voltage, so it is **not a fixed 12 V output**. An external converter provides the voltage required by the attached device and must tolerate the full SYS range.

This is the normal UPS power path. The BQ25798's separate PMID backup mode is not used in the current V4 configuration.

## Power options

 - **Two cells (2S1P):** intended for smaller loads, including the optional 5 V output. A 12 V / 2 A main adapter is the planning choice for the 5 V / 2 A load target. Lower-power adapters require reduced load and charging current.
 - **Four cells (4S1P):** intended for higher-power loads through an external converter. A 20 V / 3 A main adapter is the planning choice for the external 12 V / 3 A load target; charging may still need to be reduced at full load.

Both options require a suitable pack BMS, balancing and temperature sensing. The charger does not replace the pack BMS. Runtime depends on the actual cells, load and conversion losses.

## Software and Home Assistant

The V4 firmware is in [software/ups](software/ups). It uses **Arduino and PlatformIO**, with the BQ25798 library for charger access and MQTT for Home Assistant integration.

Home Assistant discovers the device and its sensors automatically through MQTT. The firmware reports electrical measurements, battery temperature, charger state and diagnostics. Battery percentage is estimated from voltage; it is not a measured remaining-capacity value.

The firmware supports a full-charge profile and a reduced-voltage profile named `APPROX_80`. The reduced target is configured for the particular battery; it does not guarantee an exact 80% state of charge.

See the [firmware README](software/ups/README.md) for board configuration, first USB upload, Wi-Fi setup, OTA and operating details.

## Development progress

V4 is at the prototype stage. USB programming, Wi-Fi, MQTT, OTA and Home Assistant discovery have been exercised on the prototype, and charging has been observed with a four-cell pack. Full load, runtime, thermal behavior and source-transition qualification remain to be completed; the different assembly options are not all hardware-qualified.

The hardware project is in [hardware/v4/ups_v4](hardware/v4/ups_v4), using KiCad 10:

 - [KiCad project](hardware/v4/ups_v4/ups12v_v4.kicad_pro)
 - [Schematic](hardware/v4/ups_v4/ups12v_v4.kicad_sch)
 - [PCB](hardware/v4/ups_v4/ups12v_v4.kicad_pcb)

Detailed design and current work are documented separately:

 - [Requirements](hardware/v4/V4_REQUIREMENTS.md)
 - [Architecture](hardware/v4/V4_ARCHITECTURE.md)
 - [Assembly variants](hardware/v4/V4_VARIANTS.md)
 - [BOM and sourcing review](hardware/v4/V4_BOM_REVIEW.md)
 - [Current development handover](hardware/v4/V4_HANDOVER.md)
