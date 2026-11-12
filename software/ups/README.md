# UPS firmware

## MQTT publication policy

[`include/telemetry_policy.h`](include/telemetry_policy.h) is the explicit
production allowlist for register telemetry. New library settings default to excluded.
All selected entities publish initially, after MQTT reconnect/charger recovery,
and when their published value changes. Comparisons use the last successfully
sent value; failed sends are retried, including when the next sample is unchanged.
The former 10% previous-sample threshold is removed.

| Group | Entities | Unchanged values |
| --- | --- | --- |
| Core measurements | IBUS, IBAT, VBUS, VAC1, VBAT, VSYS, TS and die-temperature ADCs; calculated PBUS, PBAT, battery temperature and battery percent; uptime | Refresh after 60 seconds since last successful send |
| Core states | PG, AC1/VBUS/battery presence, CHG_STAT, VBUS_STAT, EN_CHG, EN_BACKUP, EN_OTG, DIS_ACDRV, EN_ACDRV1, VINDPM_STAT | Same 60-second refresh |
| Configuration and diagnostics | Applied voltage/current limits, cell count/type, charge profile, termination/recharge, watchdog, other limiting and live fault states (exact list in the allowlist) | No periodic refresh; startup/reconnect and changes only |
| Excluded registers | MPPT/VOC, interrupt flags/masks, reset/trigger commands, ADC setup, D+/D- controls and other registers absent from the allowlist | No discovery or state publications |

There is no time jitter or artificial change to measured values. Only the two
core groups use HA `force_update: true` and a 300-second expiry. Change-only
entities have neither forced updates nor expiry. States are retained so HA can
restore them after restarting. Charger availability continues to gate charger
entities. Discovery republication deletes the previous configs of excluded
registers, including legacy enum views. Existing selected entity IDs/topics and
enum numeric/binary views are preserved. This policy changes telemetry only;
charger register polling and control are unchanged.

The owner's Grafana series remain available without the debug flag: all 18
register-backed series have periodic refresh, alongside `battery_percent`,
`battery_temperature`, `PBAT` and `PBUS`. In particular, `DIS_ACDRV` and
`EN_ACDRV1` are included, and `TS_ADC`/`VINDPM_STAT` use periodic refresh.
`esp_internal_chip_temperature`, `internal_chip_temperature` and `ts_zone_numeric`
are owner-confirmed Grafana templates/older definitions, not additional sensors
published by this firmware.

Define `DEBUG_BQ25798_SETTINGS` to expose **all** library settings, including
MPPT, interrupt masks/flags, ADC setup and trigger/reset-bit readbacks. Extra
debug entities publish initially/reconnect and on change only; the existing
core groups keep their fixed 60-second refresh. The flag changes telemetry,
not charger settings. Debug discovery uses more heap and MQTT traffic. Read-cleared
flags are sampled ON/OFF snapshots, not a guaranteed interrupt event history.
Returning to a build without the flag removes the debug-only HA discovery.

Append `-DDEBUG_BQ25798_SETTINGS` to the chosen environment's existing
`build_flags`, preserving its board include path and USB flags. For example,
an optional environment in `platformio.ini` can inherit the complete UPS4 flags:

```ini
[env:ups4_debug]
extends = env:ups4
build_flags =
    ${env:ups4.build_flags}
    -DDEBUG_BQ25798_SETTINGS
```

`battery_percent` is rounded to a whole percent in its MQTT payload and declares
`suggested_display_precision: 0` in discovery. It remains a voltage-derived
estimate, not a fuel gauge.

Host regression check (Windows, Python and MSVC/Windows SDK installed):
`python software/ups/tests/telemetry_host_check.py` from the repository root.
It compiles the real MQTT implementation with transport/JSON stubs and checks
change-only/periodic delivery, retention, retries, reconnect, rollover and discovery
fields in production and debug modes. It also checks the production allowlist
against the installed ups4 library. It does
not validate Arduino JSON serialization, the target firmware or a live broker/HA.

## MQTT enum telemetry

Register enums are exposed as read-only MQTT sensors with `device_class: enum`.
Their discovery key, unique ID suffix and state topic key use `<setting>_enum`;
states are labels from the library's `Setting::strings_vector`. Discovery lists
the distinct labels in `options` and omits units and `state_class`.
The numeric representation and binary representation for two-value enums remain
available. Discovery republication removes the former retained `text` entries.
The MQTT buffer is 2 KiB to accommodate enum options and device metadata.

Register discovery uses BQ25798 v1.5.2's `getHomeAssistantInfo(i)` for the primary
entity's component, entity category, icon, device class and state class. A null
or empty component falls back to `binary_sensor` for BOOL settings and `sensor`
otherwise. Auxiliary numeric/binary enum views keep their fixed components.
Numeric measurements use
the library's state class instead of assigning `measurement` to every register.
Enum label sensors keep HA's `enum` class; their numeric and binary views keep
generic device classes because the metadata describes the labels. Binary
sensors omit units/state class and unsupported legacy `status`/`control`
classes. Application-specific sensors retain their own metadata.

## Board profiles

`platformio.ini` selects a board through its include path. Every `board_config.h`
must declare all five pin arguments explicitly:

```cpp
constexpr Config::Pins boardPins{21, 22, 2, true, -1};  // SDA, SCL, LED, LED active HIGH, CHARGE_ARM
```

Set LED and CHARGE_ARM to `-1` when absent. Missing arguments or a missing `boardPins` declaration
fail compilation. I2C pins must be nonnegative and distinct; an LED must use a
separate pin. Assign `cfg.pins = boardPins` in the board configuration; GPIO
initialization uses the mandatory `boardPins` declaration directly.

V4 (`boards/v4/ups4_esp76`) declares CHARGE_ARM as GPIO0, active HIGH. Startup
preloads its output latch LOW through `gpio_set_level()` before enabling the
output, before Serial, I2C or networking. Arduino `digitalWrite()` cannot preload
an unconfigured GPIO on the current ESP32 core.
The existing `VAC2_ADC_DIS` marker still skips the one-time BQ configuration;
the existing cell-count handling and selected charge profile are preserved.
Before arming V4, firmware applies battery-limited ICHG, disables the watchdog if needed,
reads back the charge parameters, sets EN_CHG=1, then reads back and verifies again.
Only then does GPIO0 go HIGH. Reset/reconfigure and detected charger communication
loss return it LOW; recovery repeats the setup sequence. Older boards also enforce
the battery current limits and have no CHARGE_ARM GPIO operations.
This is startup sequencing, not an independent hardware watchdog or protection
against an undetected charger-only reset while GPIO0 remains HIGH.

V4 also enables `cfg.power.input.retryUnqualifiedAdapter`. After VAC1 has remained
present for 60 seconds, a Power Good source still classified as `Not qualified
adaptor` triggers FORCE_INDET, provided the charger is outside OTG/backup and
neither FORCE_INDET nor DPDM detection is already active. Further attempts are
spaced at least 60 seconds apart and stop when classification changes. Input loss
or charger communication loss restarts the settling wait. All timing is
nonblocking and handles millis rollover; older profiles leave the option OFF.

Once both detection indicators clear, firmware reapplies configured IINDPM when
positive and freshly reads the registers. The log records classification and
detected/configured/actual current limits. EN_EXTILIM is preserved, so hardware
may clamp readback below the configured value. A pending restore survives source
loss or communication recovery; restoring IINDPM does not enable charging.
This is D+/D- source classification, not USB-PD renegotiation by the external
trigger. Reference: TI BQ25798 SLUSDV2C rev. C, sections 7.3.4.5 and 7.3.6.1.

| Environment                          | MCU      | SDA | SCL | LED            |
| ------------------------------------ | -------- | --- | --- | -------------- |
| esp32dev (example), ups1, ups2, ups3 | ESP32    | 21  | 22  | 2, active HIGH |
| ups4, ups4_ota                       | ESP32-C3 | 4   | 5   | absent (`-1`)  |

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

## Battery identity and charge-current limit (all boards)

Set battery properties independently of the charger's requested current:

```cpp
cfg.battery.name = "My battery pack";
cfg.battery.capacity_mAh = 3400; // Nominal pack capacity, independent of the charge-current ceiling.
cfg.battery.maxChargeCurrent_mA = 500;
cfg.power.charger.ICHG_mA = 2000; // Requested current; firmware programs 500 mA.
```

`battery.name` is also reported as the read-only text-valued MQTT sensor
**Battery type** (`battery_type`), with diagnostic category and no units or
device/state class. Discovery and its value are republished on MQTT reconnect;
the value refreshes every 60 seconds, including when the charger is unavailable.
Its state topic is `bq25798ups/<device>/state/battery_type`.

`battery.capacity_mAh` is the nominal **pack** capacity, not remaining charge.
Series-connected 3400 mAh cells form a 3400 mAh pack; parallel strings add capacity.
The diagnostic sensor **Battery capacity** (`battery_capacity`, unit `mAh`) is
published retained initially and after discovery/MQTT reconnect, without periodic
refresh. Failed publications retry. It is available independently of the charger.
Zero/unconfigured capacity publishes `unknown`. Capacity is informational and does
not change charging limits or the voltage-derived battery percentage. UPS4/5 use
`name = "Liitokala"`, `capacity_mAh = 3400`; local GeB profiles use 3200 mAh.

## Temporary power-test overrides

Home Assistant exposes two acknowledged MQTT switches (ON/OFF commands):

| Switch / command key | ON | OFF |
| --- | --- | --- |
| Inhibit charging / `charge_inhibit` | EN_CHG=0; V4 CHARGE_ARM LOW | Return charging to its configured automatic profile |
| Force battery supply / `force_battery_supply` | EN_HIZ=1; also inhibit charging | Exit test HiZ; resume normal source selection |

The battery-supply switch is exposed only for `VSYS_UNINTERRUPTED` configurations,
including UPS4/5. It tests the SYS battery path with the adapter still connected;
it does not exercise PMID/OTG backup or replace a physical source-loss test.
Both switches can be active together: releasing HiZ keeps an independently
requested charge inhibit active, and releasing charge inhibit during HiZ does
not enable charging.

Both requests are **RAM-only**. ESP32 restart returns to automatic operation;
MQTT disconnect/reconnect preserves active requests. HA sends non-retained commands;
do not publish retained commands to these topics. Existing read-only register
entities (EN_CHG and EN_HIZ) report register readback, separately from test requests.
Commands use `bq25798ups/<device>/command/<key>` and states use
`bq25798ups/<device>/state/<key>`. Rejected commands republish the actual request
state; OFF cancels a request even while charger communication is unavailable.

The voltage guard belongs to the battery configuration:

```cpp
cfg.battery.overrideLimits.stopCell_mV = 3600;  // Cancel both tests at or below this average.
cfg.battery.overrideLimits.startCell_mV = 3700; // Allow manual ON at or above this average.
```

These defaults are conservative test settings, not measured SOC or cell protection
limits. The guard compares fresh BQ pack voltage against CELL times the threshold,
without rounding down individual cells. A valid, present battery and continuous
VBAT ADC are required. At/below the stop threshold, invalid measurements or I2C
failure, both requests are cancelled. They stay OFF after voltage recovery until
explicitly requested again. This measures the **pack average**, not the weakest
cell; the BMS remains responsible for individual-cell protection. Without an
available input, ending a test cannot itself stop normal battery discharge.

Control is checked in the normal charger-service loop independently of MQTT and
the 60-second publication cadence. HiZ entry disables the BQ ADC, so firmware
reenables it and verifies readback. I2C failure revokes V4 CHARGE_ARM; an owned HiZ
exit is retried after communication recovery. No software can guarantee a register
write during loss of I2C. During normal operation, existing protection-triggered
HiZ is not adopted or cleared by the test controller. At the first connection
after ESP32 boot, SYS mode explicitly clears retained HiZ and restarts ADC even
when the old initialization marker is present; boot therefore also retries a
pre-existing HiZ condition. Charge limits and profiles still apply, and V4
charge permission is freshly validated before restoration. Legacy charge control
resumes on its normal 30-second check.

References: [TI BQ25798 SLUSDV2C rev. C, June 2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf),
sections 7.3.6.5 (HiZ, SYS battery support and ADC disable), 7.3.8 (power paths),
7.5.1.16 (EN_CHG/EN_HIZ) and 7.5.1.42 (ADC control). This is a firmware test
facility; behavior on matching hardware still needs owner validation.

For a 12 V to 5 V efficiency test, turn ON **Inhibit charging**, keep HiZ OFF,
and verify negligible battery current. `PBUS` already reports VBUS times IBUS.
Measure actual 5 V output voltage/current externally and calculate
`efficiency = 100 * (Vout * Iout) / Pin` from settled readings. BQ VBUS/IBUS covers
its input measurement point; use an external input measurement at the UPS connector
to include upstream losses/other supply branches. No output-power or efficiency
sensor is synthesized from the load setpoint.

Host validation: `python software/ups/tests/charge_arm_host_check.py` generates the
actual startup/override functions for a native C++17 check. Compile/run the generated
`.pio/charge-arm-check/check.cpp` with `include/` on the include path. The check covers
managed/legacy paths, both voltage boundaries, concurrent requests, HiZ ADC restart,
readback mismatch and injected bus failures. MQTT discovery/delivery and input
detection checks cover the switch controls and HiZ detection pause separately.

## Charge-current limit details

The effective ICHG is the lower of the requested current and the pack maximum,
capped at 5000 mA and rounded down to a 10 mA step. Precharge current is also
reduced when necessary, rounded down to its 40 mA step; a lower existing
precharge setting is preserved. This applies to every board and charge profile,
including saved initialization markers, resets/reconfiguration and runtime
recovery. Changed current registers are freshly read back before proceeding.
Failures disable EN_CHG as a best effort, revoke V4 CHARGE_ARM and mark the
charger unavailable. A missing/invalid battery maximum inhibits charging;
there is no fallback to unrestricted ICHG. Requested ICHG below 50 mA or a pack
maximum below the chip's fixed 100 mA trickle current is rejected.

These are programmed current limits, not guarantees about analog current
tolerance or protection while the MCU is not in control. Reference: [TI BQ25798
SLUSDV2C rev. C](https://www.ti.com/lit/ds/symlink/bq25798.pdf), sections 6.5,
7.3.9.1, 7.5.1.3 (ICHG) and 7.5.1.6 (IPRECHG). Choose the pack maximum with
the cell manufacturer's charging limits and charger tolerance in mind.
The local UPS1-3 profiles use the owner's GeB 3200 mAh / 3000 mA values;
their requested ICHG remains 500/500/1000 mA. The owner's current UPS4 profile
uses Liitokala 3400 mAh / 700 mA with requested ICHG still at 500 mA.
These configuration values do not constitute new verification of cell ratings.

## Configurable charge profiles (all boards)

Set `cfg.power.charger.chargeProfile` in the selected `board_config.h`, after
copying shared settings. The default is `ChargeControl::Mode::LEGACY`, preserving
each board's original charging thresholds and behavior. No board has been
automatically switched to a reduced voltage.

| Mode        | Behavior                                                                                                  |
| ----------- | --------------------------------------------------------------------------------------------------------- |
| `LEGACY`    | Existing software enable/disable thresholds; no VREG/recharge writes by the profile controller.           |
| `FULL`      | Native CC/CV charging to `fullCell_mV` per cell (default 4200).                                           |
| `APPROX_80` | Native CC/CV charging to explicitly configured `cfg.battery.approx80PercentCapacity_mV`; no universal 80%-to-voltage conversion. |

For example, selecting the reduced profile requires both settings:

```cpp
cfg.power.charger.chargeProfile.mode = ChargeControl::Mode::APPROX_80;
cfg.battery.approx80PercentCapacity_mV = 0; // Replace with the verified voltage for your cells. Zero is rejected.
```

`cfg.battery.approx80PercentCapacity_mV` is a per-cell voltage, stored with the
battery's identity and current limit. An unconfigured reduced voltage is
deliberately rejected instead of guessing a
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

V4 startup fault-injection check (no hardware or credentials):

```powershell
python software/ups/tests/charge_arm_host_check.py
```

Compile the generated `software/ups/.pio/charge-arm-check/check.cpp` with a C++17
compiler and `software/ups/include` on its include path, then run it. It extracts
the actual startup functions and covers marker/forced initialization, LOW-before-
output ordering, old boards, ignored writes, readback drift and I2C failures.

Input detection retry tests:

```powershell
python software/ups/tests/input_detection_host_check.py
```

Compile `software/ups/tests/input_detection_test.cpp` with C++17 and both
`software/ups/include` and `software/ups/.pio/input-detection-check` on the include
path, then run it. The fixture compiles the actual `serviceInputDetection` body
and tests settling/retry boundaries, source loss, Power Good/OTG/backup gates,
millis rollover, detection completion, hardware current clamping and I2C errors.

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
