# Hardware profiles and runtime settings

Checkpoint 1 separates compiled hardware from mutable settings. Existing
PlatformIO environments and device identifiers remain in use. Persistence,
runtime provisioning and configuration controls are later checkpoints in the
[implementation plan](UNIVERSAL_FIRMWARE_PLAN.md).

## Compiled hardware

[`hardware_profile.h`](include/hardware_profile.h) defines immutable profiles.
Each `board_config.h` selects one profile as `constexpr Hardware::Profile hardware`.
Pin arguments remain explicit in the shared definitions, and the firmware checks
pin conflicts at compile time. Version selects MCU and power path together.

| Profile | Adapters | Version | MCU | Power path | SDA / SCL / LED / ARM |
| --- | --- | --- | --- | --- | --- |
| `Hardware::kV1Esp32` | example, UPS1 | `1.0` | ESP32 | PMID switchover | 21 / 22 / 2 / -1 |
| `Hardware::kV3SysEsp32` | UPS2, UPS3 | `3.3b-SYSmod` | ESP32 | SYS | 21 / 22 / 2 / -1 |
| `Hardware::kV4Esp32C3` | UPS4-8 | `4.0` | ESP32-C3 | SYS | 4 / 5 / -1 / 0 |

LED polarity is active HIGH; V4 ARM is active HIGH. `-1` means absent.
TS divider resistors are common constants, 5600 ohm to REGN and 33000 ohm to
ground. They are no longer mutable temperature settings. NTC resistance and beta
remain runtime settings.

MCU board/toolchain, USB CDC flags, CPU/flash settings and partition selection
remain in `platformio.ini`, unchanged. The three profiles are not yet replacement
PlatformIO environments. The same code continues to read `CELL` from the charger;
no cell-count field or register write was added.

## Runtime field inventory

[`runtime_settings.h`](include/runtime_settings.h) owns mutable settings.
The device adapters still construct `RuntimeSettings config` from the local
shared settings and their existing overrides. [`config.h`](include/config.h)
retains `Config` as a type alias for that local shared configuration.

All text fields use Arduino `String`, so copies own their text. Calls to C-string
and printf-style APIs use `c_str()`. These pointers are borrowed, not independent
copies: future settings application must rebuild clients that retain a pointer
when replacing its backing text. The HA client still copies identity during
global construction; changing that startup order belongs to checkpoint 3.

The table records every current configuration field and the intended ownership.
Defaults are generic defaults; installed-device overrides are below. No new
validation rules or numeric limits are introduced here.

| Runtime field | Default or installed source | Meaning and applicability |
| --- | --- | --- |
| `network.syslog.serverHostname` | `logserver.localnet`; overridden locally | Syslog endpoint |
| `network.syslog.serverPort` | 514 | Syslog port |
| `network.syslog.myHostname` | `default`; each adapter supplies BOARD_NAME | Existing syslog host label |
| `network.syslog.myAppname` | `ups`; each adapter supplies DEVICE_NAME | Existing syslog application label |
| `network.mqtt.serverHostname` | `mqtt.localnet`; overridden locally | Broker endpoint |
| `network.mqtt.serverPort` | 1883 | Broker port |
| `network.mqtt.user`, `password` | Empty; installed values supplied locally | No deployment credentials in generic defaults |
| `network.mqtt.haDeviceName` | `default-ups`; each adapter supplies HOSTNAME | Stable discovery/topic/device identifier |
| `temperatureSensor.resistance_25degC` | 10000 ohm | NTC characteristic |
| `temperatureSensor.beta` | 3435 | NTC characteristic |
| `battery.cell.name` | `Unspecified`; each adapter overrides | Cell identity, not pack capacity |
| `battery.cell.approx80PercentCapacity_mV` | 0; each installed adapter overrides | APPROX_80 target per cell |
| `battery.cell.approx20PercentCapacityUnderMaxLoad_mV` | 0; V4 adapters override | Almost-depleted warning per cell; 0 unspecified |
| `battery.cell.overrideLimits.stopCell_mV` | 3600 | Existing diagnostic test stop threshold |
| `battery.cell.overrideLimits.startCell_mV` | 3700 | Existing diagnostic test start threshold |
| `battery.pack.capacity_mAh` | 0; each installed adapter overrides | Nominal pack capacity; informational |
| `battery.pack.maxChargeCurrent_mA` | 0; each adapter overrides | Pack charge-current ceiling; 0 inhibits charging |
| `power.input.retryUnqualifiedAdapter` | false; true on V4 adapters | Existing V4 input-detection retry |
| `power.input.IINDPM_mA` | 1000 | Input current DPM limit |
| `power.input.VINDPM_mV` | 11500 | Input voltage DPM limit |
| `power.input.VBUSBackupPercentage` | `PCT_VBUS_BACKUP_80` | PMID backup setting; unused on SYS path |
| `power.charger.chargeProfile.mode` | LEGACY; APPROX_80 on installed adapters | Charge-control mode |
| `power.charger.chargeProfile.fullCell_mV` | 4200 | Managed full-charge voltage per cell |
| `power.charger.chargeProfile.rechargeOffset_mV` | 0 | Pack-level offset; 0 preserves chip setting |
| `power.charger.minCellVoltage_mV` | 3200 | Legacy percent-estimate endpoint |
| `power.charger.maxCellVoltage_mV` | 4200 | Legacy percent-estimate endpoint |
| `power.charger.vbatChgEnableIfCellBelow_mV` | 4100 | Legacy charging threshold per cell |
| `power.charger.vbatChgDisableIfCellAbove_mV` | 4155 | Legacy charging threshold per cell |
| `power.charger.ICHG_mA` | 1000 | Requested charge current, limited by pack ceiling |
| `power.output.IOTG_mA` | 1200 | PMID/OTG output limit; unused on SYS path |
| `power.output.VOTG_mV` | 12000 | PMID/OTG output voltage; unused on SYS path |
| `ACRecoveryPeriodSeconds` | 30 | PMID source recovery delay |

Wi-Fi credentials currently remain managed by WiFiManager/the ESP32 Wi-Fi stack;
they are not yet duplicated into `RuntimeSettings`. `HOSTNAME`, `BOARD_NAME` and
`DEVICE_NAME` remain adapter macros for current startup compatibility. Later
checkpoints provide runtime identity/network initialization and Wi-Fi ownership.

Transient diagnostic ON requests, register caches, availability and retry state
remain runtime state, not configuration. `DEBUG_BQ25798_SETTINGS` remains a
development build option. There is no mutable hardware version, pin mapping,
power-path selector or TS-divider resistor field in `RuntimeSettings`.

## Installed values preserved by checkpoint 1

This is a source-level before/after inventory, including generic defaults and
the local shared config. It is not a compiled or on-device snapshot. The local
shared config overrides only network values and previously supplied redundant
pins; its non-pin content is unchanged. No credentials are recorded here.

All eight installed profiles retain APPROX_80, a 700 mA pack current ceiling,
4200 mV/cell full target, zero recharge-offset override and 30 s recovery delay.
The current-limit calculation remains unchanged: UPS3's 1000 mA request is
limited to 700 mA; the other devices request 500 mA.

| Device ID | Hardware | Cell / pack mAh | 80% / warning mV per cell | Requested ICHG mA | IINDPM mA / VINDPM mV | Retry input detection | IOTG mA |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `esp18-bq25798-ups1` | V1/PMID | GeB / 3200 | 3920 / 0 | 500 | 3000 / 11500 | false | 3200 |
| `esp27-bq25798-ups2` | V3/SYS | GeB / 3200 | 3920 / 0 | 500 | 1500 / 4700 | false | 1200 |
| `esp19-bq25798-ups3` | V3/SYS | GeB / 3200 | 3920 / 0 | 1000 | 1000 / 11500 | false | 1200 |
| `esp76-bq25798-ups4` | V4/SYS | Liitokala / 3400 | 3955 / 3300 | 500 | 3000 / 11500 | true | 3200 |
| `esp77-bq25798-ups5` | V4/SYS | Liitokala / 3400 | 3955 / 3300 | 500 | 3000 / 11500 | true | 1200 |
| `esp78-bq25798-ups6` | V4/SYS | Liitokala / 3400 | 3955 / 3300 | 500 | 3000 / 11500 | true | 1200 |
| `esp79-bq25798-ups7` | V4/SYS | Liitokala / 3400 | 3955 / 3300 | 500 | 3000 / 11500 | true | 1200 |
| `esp80-bq25798-ups8` | V4/SYS | Liitokala / 3400 | 3955 / 3300 | 500 | 3000 / 11500 | true | 1200 |

All retain the common runtime defaults above except their listed overrides.
VOTG remains 12000 mV, including unused SYS-path values. Ports remain 514/1883.
Syslog labels remain each adapter's BOARD_NAME and DEVICE_NAME. Wi-Fi/OTA
hostnames, MQTT client IDs and HA IDs continue to use the same existing strings.

The example adapter retains V1/PMID, `board01-test-bq25798-ups1`, its explicit
placeholder endpoints/credentials, 500 mA pack ceiling/request, LEGACY mode,
4150/4155 mV legacy charge thresholds, 3000/12000 input limits and 3200 mA IOTG.
Its capacity and cell presets remain unspecified. Generic MQTT credential defaults
are intentionally empty; this does not change an adapter that supplies them.

## Migrating external local profiles

Select `constexpr Hardware::Profile hardware = Hardware::kV1Esp32` (or the matching
V3/V4 profile) instead of declaring `Config::Pins boardPins` and assigning
`cfg.pins`, `cfg.hardwareVersion` or `cfg.power.backupMode`. Custom pin assignments
can use `Hardware::Profile{Hardware::Version::V1_0, Hardware::Pins{...}}` with all
five pin arguments. Keep power-path selection tied to the actual hardware version.

Remove redundant `cfg.pins.*` assignments from local shared settings. The local
`Config` alias remains valid for their runtime fields. Remove TS-divider resistor
assignments because the common hardware constants now supply them; NTC
resistance/beta fields remain available. New direct uses of runtime text with
C-string/printf-style APIs must pass `c_str()`.

Firmware builds, heap usage, upload and live MQTT/HA/power behavior remain
owner checks. Owned strings add RAM ownership that the old borrowed pointers
did not have; no binary-size or heap result is claimed by the source inventory.
