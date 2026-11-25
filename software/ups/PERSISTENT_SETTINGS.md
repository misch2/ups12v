# Persistent settings and migration bridge

Checkpoint 2 saves the current device configuration once. Checkpoint 3 now
[loads that record before startup](STARTUP.md); compiled adapter values seed only
missing storage. The original checkpoint 2 bridge ran from compiled settings.
Checkpoint 5 adds [web configuration](WEB_CONFIGURATION.md); new serial/MQTT
configuration endpoints are not part of this checkpoint. Wi-Fi changes stage in a
separate private `ups-settings/wifi-pending` blob before SDK activation on restart.

## Storage and first boot

The bridge runs after Serial starts, with V4 CHARGE_ARM already LOW. It reads the
`ups-settings` NVS namespace and its `config` blob. If the namespace/key is absent,
it validates and serializes the current adapter settings, writes one complete
blob, commits and verifies the bytes by reading them back. Later boots preserve
the existing record even if compiled defaults have changed.

The adapter uses the native `nvs_open`, `nvs_get_blob`, `nvs_set_blob` and
`nvs_commit` calls also used by ESP32 Preferences. Native read-only open lets it
distinguish a missing namespace from an I/O error without creating storage on a
read. It never initializes/erases NVS, clears namespaces, changes partitions or
resets networking. See [Espressif NVS documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/storage/nvs_flash.html).

Wi-Fi credentials remain owned by the ESP32 Wi-Fi stack and WiFiManager. They
are not copied into the UPS record, so the bridge reuses the installed Wi-Fi
connection. Keep that single source until the later network setup checkpoint.
MQTT credentials are included in the private NVS record to preserve the current
configuration. They are never logged or included in normal exports.

The checkpoint 2 bridge reported `Settings bridge: created and verified` or
`existing valid record`; current startup reports `Settings startup` and its
configured flag. Errors identify a status and static field/operation name, without
printing values. The original checkpoint 2 bridge continued with compiled settings
on failure. Checkpoint 3 preserves the record and disables normal charger startup
and MQTT instead; [local recovery remains available](STARTUP.md).

## Schema and compatibility

Schema 1 is the first persisted format. It is JSON, explicitly encoded field by
field, not a memory dump of C++ structs or pointers. Its four top-level members are
`schema`, `credentials_included`, `hardware` and `settings`.

The hardware metadata records version, MCU, power path, SDA/SCL/LED/ARM and LED
polarity. Import/load requires an exact match with the selected compiled profile.
These values are compatibility metadata, never mutable hardware settings. The
shared image still uses the charger's CELL setting; no cell count is stored or
programmed by this module.

The settings object uses the dotted field paths from the
[configuration inventory](CONFIGURATION.md) as JSON keys. It contains all 33
runtime fields, including settings unused by a particular power path. The private
format includes MQTT user/password; the export format omits those two fields and
sets `credentials_included` to false. Enum settings are stored as their integer
values: LEGACY/FULL/APPROX_80 are 0/1/2, and VBUS backup 40/60/80/100% is 0/1/2/3.

Decoding requires all expected fields with their declared types. Unknown fields,
truncated JSON, trailing non-whitespace, integer overflow, invalid enum values and
embedded NUL characters in text are rejected. Records larger than 8192 bytes are
rejected before parsing/allocation; this is an internal resource bound.

Validation uses the existing charge-current, charge-profile and diagnostic
override rules, and checks port ranges, finite positive NTC parameters, nonnegative
capacity/presets and consistent legacy voltage endpoints. A zero pack current
ceiling remains valid configuration representing inhibited charging. Managed
profiles are checked for both 2S and 4S without programming the chip. Existing
nonpositive input/output "do not write" values remain representable.

This is stored-data validation, not confirmation of battery ratings or charger
register application. Hardware applicability, live register readback and deferred
changes are handled by the [checkpoint 4 service](SETTINGS_SERVICE.md).
The codec requires a nonempty device ID; startup
applies the stricter identifier/commissioning rules in [checkpoint 3](STARTUP.md).

## Protected records and failed writes

| Read result | Bridge/save action |
| --- | --- |
| Missing namespace/key | Bridge may seed current compiled settings |
| Valid schema 1, matching hardware/identity | Preserve it; explicit `save` may update settings |
| Different device identifier | Preserve it and report identity mismatch |
| Invalid JSON/settings, wrong NVS type or oversized record | Preserve it and report failure |
| Older schema | Preserve it; there is no older supported format to migrate yet |
| Newer schema | Preserve it; downgrading firmware does not replace it with defaults |
| Incompatible hardware | Preserve it; no pin/topology substitution |
| Storage read/open error | Report it; do not interpret it as absence |

`Store::save` reads and validates the existing record before replacement and
rejects a changed commissioned identifier. No reset/force-overwrite operation is
provided here. The application uses one settings writer; concurrent writes are
not part of this API.

A replacement is one blob update and commit, followed by readback, rather than
separate field writes. A reported write/commit/readback failure can leave the old
or a complete new record; the caller must not claim successful application or
rollback. NVS documents recovery from interrupted writes, but physical flash and
power-loss behavior still require device validation. No code erases storage in
response to an error. [Espressif NVS robustness](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/storage/nvs_flash.html#security-tampering-and-robustness)

## Export and restore API

[`settings_store.h`](include/settings_store.h) exposes `Store::load`,
`seedIfMissing` and guarded `save`, plus four codec functions:

- `encodePrivate` / `decodePrivate` handle the full internal record.
- `encodeExport` omits MQTT user/password and all Wi-Fi credentials.
- `decodeExport` replaces operating settings while preserving the destination's
  separately supplied MQTT credentials. It rejects injected credential fields.

Codec output is replaced only on success. Decoding completes into a candidate,
checks it, then moves it into the destination. None of these functions applies
charger settings or changes network clients.

For a future restore onto an existing device, load its current settings, decode
the export into that candidate, then use guarded `save`. Identity must still
match. For commissioning a blank device, provide MQTT credentials separately;
restore Wi-Fi through its own setup path. Never treat a private NVS record as an
ordinary shareable export. The browser/import UI is a later checkpoint.

## Native behavioral tests

[`tests/settings_store_test.cpp`](tests/settings_store_test.cpp) compiles the
production codec, store and NVS adapter against the real cached ArduinoJson
headers. Test substitutes supply owned text, the one required BQ enum and NVS
calls. They do not emulate ESP32 flash, Wi-Fi, Arduino allocation behavior or
charger hardware, and do not read local credentials or extract production source.

Verified Windows command, from the repository root (adjust compiler/ArduinoJson
cache paths if needed):

```powershell
$env:PATH = 'C:\msys64\ucrt64\bin;' + $env:PATH
$jsonInclude = (Resolve-Path software/ups/.pio/libdeps/ups8/ArduinoJson/src).Path
New-Item -ItemType Directory -Force .tmp/universal-firmware-step2 | Out-Null
& 'C:/msys64/ucrt64/bin/g++.exe' -std=c++11 -Wall -Wextra -Werror -Isoftware/ups/tests/support -Isoftware/ups/include -I $jsonInclude software/ups/tests/settings_store_test.cpp software/ups/src/settings_codec.cpp software/ups/src/settings_store.cpp software/ups/src/settings_nvs.cpp -o .tmp/universal-firmware-step2/settings_store_test.exe
& ./.tmp/universal-firmware-step2/settings_store_test.exe
```

The tests cover complete field round trips across all three profiles, malformed
and protected records, credential redaction/preservation, first-seed failure and
retry, reboot/load, guarded saves, readback errors and the production NVS adapter
with simulated calls. This native executable is not a firmware target build.

## Checkpoint 3 startup

The seed/store/codec APIs above are unchanged. The current firmware uses
`loadForBoot` to activate a validated saved record before any network identity is
assigned; only absent storage may be seeded from a valid adapter. Placeholder or
invalid IDs are rejected for commissioning. See [startup and recovery](STARTUP.md)
for current boot and recovery behavior.

## Owner device validation

Build the existing selected device environment, check the final binary against
both installed OTA slots, and upload through the established path. No partition
change is required by this checkpoint. On first boot with missing storage, confirm
the seed/startup log, then reboot and confirm an existing valid record without
another write. Current startup must report `configured=1` for valid settings.
Verify the loaded identity, Wi-Fi/OTA and charger behavior using [checkpoint 3
checks](STARTUP.md). No agent upload or live broker operation is part of this work.

Keep the device-specific bridge image and local settings available until the
later universal image has loaded and verified the record. An older image ignores
these records and runs its own compiled settings; reverting its firmware does not
restore a newer runtime configuration. Firmware size, heap usage and real NVS
persistence remain owner checks.
