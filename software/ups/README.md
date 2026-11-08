# UPS firmware

## Board profiles

`platformio.ini` selects a board through its include path. Every `board_config.h`
must declare all four pin arguments explicitly:

```cpp
constexpr Config::Pins boardPins{21, 22, 2, true};  // SDA, SCL, LED, LED active HIGH
```

Set LED to `-1` when absent. Missing arguments or a missing `boardPins` declaration
fail compilation. I2C pins must be nonnegative and distinct; an LED must use a
separate pin. Assign `cfg.pins = boardPins` in the board configuration; GPIO
initialization uses the mandatory `boardPins` declaration directly.

| Environment | MCU | SDA | SCL | LED |
| --- | --- | --- | --- | --- |
| esp32dev (example), ups1, ups2, ups3 | ESP32 | 21 | 22 | 2, active HIGH |
| ups4, ups4_ota | ESP32-C3 | 4 | 5 | absent (`-1`) |

The V4 pin mapping comes from the exported V4 netlist:
`hardware/v4/evidence/implicit-nets-2026-11-08/current.net` (U1.18 GPIO4,
U1.19 GPIO5). `MCU_STATUS_LED` is an unconnected GPIO3 net, not a fitted LED.
Legacy profiles retain their previous effective pin values. Local profiles
`ups1_esp18`, `ups2_esp27`, `ups3_esp19` and `secret/michal_config.h` are ignored
by Git; keep their credentials local. Copy the mandatory pin declaration into
any additional local board profiles.

## V4 build and service USB

V4 uses the C3 target and flash settings already used by `software/i2c_test`:
160 MHz CPU, 4 MB DIO flash at 40 MHz. `Serial` uses the native USB Serial/JTAG
controller as a serial port (`ARDUINO_USB_MODE=1`, `ARDUINO_USB_CDC_ON_BOOT=1`).
No JTAG debugger or USB-to-UART adapter is needed. Firmware does not wait for a
serial monitor to connect. BOOT/RESET remain available for recovery.

The C3 base environment selects the bundled `min_spiffs.csv`: two 1920 KiB
application slots for OTA, 128 KiB filesystem, NVS and coredump within 4 MB.
The application currently does not use SPIFFS/LittleFS. The default 1280 KiB
application slot is too small for the corrected-toolchain firmware (1313904
bytes reported on 2026-11-08). When changing this partition layout, rebuild and
perform a full normal USB/esptool upload so the partition table is updated too;
an application-only OTA upload cannot migrate the partition table. NVS retains
its existing offset and size; no full-flash erase is required by this change.

From the repository root (replace `COMx` with the actual port):

```powershell
pio run -d software/ups -e ups4
pio run -d software/ups -e ups1 -e ups2 -e ups3
pio run -d software/ups -e ups4 -t upload --upload-port COMx
pio device monitor -d software/ups -e ups4 --port COMx
```

After Wi-Fi provisioning, routine OTA upload uses:

```powershell
pio run -d software/ups -e ups4_ota -t upload
```

## Operation without a charger

Missing/unpowered charger or failed I2C reads stop charger telemetry and commands,
while USB logging, Wi-Fi, MQTT, uptime and OTA continue. Connection is retried
every five seconds. Charger register-reset polling is limited to five seconds.
Communication recovery does not request a register reset; the existing
configuration logic still runs when its initialization marker is absent.

Home Assistant charger entities use a retained charger availability topic;
uptime is independent. MQTT publishes an offline last will. Successful charger
reconnection republishes discovery with the detected model. Invalid temperature
calculations and unknown cell counts are not published as valid measurements.

## Configurable charge profiles (all boards)

Set `cfg.power.charger.chargeProfile` in the selected `board_config.h`, after
copying shared settings. The default is `ChargeControl::Mode::LEGACY`, preserving
each board's original charging thresholds and behavior. No board has been
automatically switched to a reduced voltage.

| Mode | Behavior |
| --- | --- |
| `LEGACY` | Existing software enable/disable thresholds; no VREG/recharge writes by the profile controller. |
| `FULL` | Native CC/CV charging to `fullCell_mV` per cell (default 4200). |
| `APPROX_80` | Native CC/CV charging to explicitly configured `approx80Cell_mV`; no universal 80%-to-voltage conversion. |

For example, selecting the reduced profile requires both settings:

```cpp
cfg.power.charger.chargeProfile.mode = ChargeControl::Mode::APPROX_80;
cfg.power.charger.chargeProfile.approx80Cell_mV = 0; // Replace with the verified voltage for your cells. Zero is rejected.
```

An unconfigured reduced voltage is deliberately rejected instead of guessing a
battery-specific value. Choose/calibrate it from the cell manufacturer's data
and actual pack measurements. The label "Approx. 80%" describes the selected
profile, not a measured state of charge. Existing Battery Percent remains the
original voltage-based estimate and is not used for charge control or rescaled
to make the reduced target appear as 100%.

To explicitly restore full charging:

```cpp
cfg.power.charger.chargeProfile.mode = ChargeControl::Mode::FULL;
cfg.power.charger.chargeProfile.fullCell_mV = 4200; // For the project's 4.2 V-rated Li-ion cells.
```

`LEGACY` leaves the current VREG untouched, including any value retained from a
previous firmware. Use `FULL` to deliberately restore the configured full-charge
voltage rather than assuming a change to LEGACY resets the charger registers.

Managed profiles support the project's 1–4S, 4.2 V maximum-rated Li-ion packs
with a verified BQ25798. They use the existing CELL register, never change CELL,
and never infer the correct cell count from terminal voltage. Per-cell settings
must be 3000–4200 mV, with the reduced value strictly below full. Pack VREG is
rounded down to a 10 mV step. `rechargeOffset_mV` is optional: zero preserves the
IC's existing setting; otherwise it is a **pack-level** offset below VREG,
50–800 mV in 50 mV steps. The IC handles termination and restart hysteresis;
legacy software thresholds are bypassed in both managed modes.

The profile is applied even when the old initialization marker is already set,
after configuration/reconnection, and checked against each fresh register
snapshot during operation. Voltage changes disable charge first, verify VREG,
CELL and any configured recharge offset, and enable charge only with forward
input power outside OTG/backup mode. Invalid configuration or failed readback
requests EN_CHG off and leaves charger service unavailable for retry; an I2C
failure can prevent this request reaching the hardware. Current limits, CE GPIO,
temperature protection, CELL and OTG/backup settings are not changed by the
profile controller. It does not actively discharge an already fuller battery.

Home Assistant gets read-only `Charge profile` and `Charge voltage limit`
sensors; the voltage is the actual pack VREG readback. No HA control is added.

The register settings are volatile. POR/register reset/watchdog can restore
defaults before running firmware reapplies its profile. This feature is not an
independent hardware ceiling or a substitute for existing pack/BMS protection.
V4 CE authorization and BQ25792 support remain separate work.

Manufacturer basis: TI BQ25798 datasheet SLUSDV2C, revision C (June 2026),
sections 7.5.1.2 (`REG01`, VREG 3000–18800 mV/pack, 10 mV steps) and 7.5.1.8
(`REG0A`, recharge offset 50–800 mV/pack, 50 mV steps):
https://www.ti.com/lit/ds/symlink/bq25798.pdf
SOC limitations: https://www.analog.com/en/resources/technical-articles/2022/07/16/09/50/battery-fuel-gauges-accurately-measuring-charge-level.html

Host tests (with WSL g++, from the repository root):

```powershell
wsl.exe --exec sh -c 'g++ -std=c++11 -Wall -Wextra -Werror -fsanitize=undefined -Isoftware/ups/include software/ups/tests/charge_profile_test.cpp -o /tmp/ups12v-charge-profile-test && /tmp/ups12v-charge-profile-test'
```

Host tests cover 1–4S scaling, downward quantization, invalid configuration,
unchanged legacy state, return to full, reset recovery, forward versus
battery/backup enable, recharge offset and injected write/readback failures.
Firmware builds and on-board CC/CV termination/recharge remain owner checks.

## Current scope — 2026-11-08

Owner deferred V4 CE control, assembly/pack authorization, current-limit changes
and BQ25792 support review. The V4 profile still requests 1000 mA and retains its
existing source/temperature settings. This checkpoint adapts the MCU and
communication path; it does not qualify battery charging on V4.

Owner reports the V4 build passed (2026-11-08). Legacy builds, upload and hardware
runtime were initially unverified. Owner subsequently confirmed flash and USB
startup, then reported a captive portal crash. Diagnosis found missing C3
runtime files in the local toolchain, causing fallback to an incompatible
default libstdc++. Missing files have been restored and library selection checked;
a subsequent firmware exceeded the default app partition, resolved by selecting
`min_spiffs.csv`. Owner then confirmed successful captive portal provisioning,
Wi-Fi connection, OTA service startup, syslog resolution/client creation and
MQTT connection. Owner subsequently confirmed actual OTA upload and the device
with its discovered entities in Home Assistant. Charger entities are unavailable
while the charger is not detected. Owner then connected main power and confirmed
automatic charger detection, successful reset/configuration and live MQTT/HA
register telemetry (BQ25798, 4-cell configuration, 750 kHz). Battery operation,
charging and recovery after loss of an established charger session remain
unverified. See
`hardware/v4/evidence/firmware-c3-portal-2026-11-08/RESULT.md`.
Check USB-only start and serial,
Wi-Fi/MQTT/OTA without a charger, then charger loss/reconnection and legacy
V1–V3 builds. Battery charging requires the deferred follow-up.
