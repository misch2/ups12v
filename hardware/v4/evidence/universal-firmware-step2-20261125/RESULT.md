# Universal firmware checkpoint 2

Date: 2026-11-25. Baseline: `e542e03` on `universal-firmware`.
Scope: versioned settings storage, a seed-once migration bridge and codec APIs.
Saved-settings startup and external configuration interfaces remain later work.

## Implemented behavior

- Schema 1 explicitly encodes all 33 current runtime fields plus hardware
  compatibility metadata. No C++ struct dumps or stored pointers.
- Native NVS adapter uses read-only lookup and a single `ups-settings/config`
  blob update/commit. It distinguishes absence, wrong type, excessive size and
  I/O errors, and never erases/initializes NVS or changes partitions.
- The bridge seeds only missing storage from the current adapter, with exact
  device identity, and verifies written bytes. It does not consume saved settings
  into the running configuration. The early V4 charge-arm inhibit is preserved.
- Store APIs protect existing incompatible, damaged and unsupported-schema
  records, and reject identity changes on explicit save. Errors never cause an
  automatic fallback write or a claimed rollback.
- Normal exports omit MQTT username/password. Imports preserve destination
  credentials and reject injected credential fields. Wi-Fi credentials stay
  solely with the existing SDK/WiFiManager setup. Private records are not exports.
- Typed parsing rejects incomplete/unknown fields, malformed/trailing data,
  embedded NULs, integer overflow, invalid enums and invalid existing charge
  constraints. Parsing is bounded to 8192 bytes. Decoder output is committed by
  moving a fully validated candidate, not by copying fields into active settings.

## Native behavioral validation

Five test groups pass in the final Windows native test executable. Full compact
output: [native-tests.txt](native-tests.txt). The test command is maintained in
[`PERSISTENT_SETTINGS.md`](../../../../software/ups/PERSISTENT_SETTINGS.md).

The tests compile the actual `settings_codec.cpp`, `settings_store.cpp` and
`settings_nvs.cpp`, using cached ArduinoJson 7.4.3 and dependency substitutes for
owned text, the BQ backup enum and NVS calls. C++11, `-Wall -Wextra -Werror` pass.
No source-text tests, function extraction or copies of production logic are used.
Fixtures are synthetic and do not include device headers or local credentials.

Coverage includes every-field round trips on all three hardware profiles,
unconfigured/inhibited defaults, escaped text, invalid payloads/types, older/newer
schemas, hardware mismatch, unchanged failed-decode output, redacted export,
credential preservation/injection rejection, first-seed failure/retry, one-time
seeding after source defaults change, reboot/load, guarded save, storage/readback
failure and an error after a complete write. The NVS adapter itself is exercised
with simulated missing/type/size/open/get/set/commit errors and handle closure.

The SDK NVS declarations and String move operations were checked against the
installed Arduino framework headers. A WSL test compile was denied before
compilation; native MSYS2 g++ supplied the working host path. No escalation or
firmware build was used. Diff/whitespace and documentation-link checks pass.

## Pending owner checks

Native tests do not establish target compilation, Arduino String allocation
behavior, physical NVS persistence or power-loss recovery. Build the intended
existing device environment, check its final binary against installed OTA slots,
and upload through the established owner workflow. Confirm a successful first
seed and preserved record after reboot, along with unchanged Wi-Fi, MQTT/HA and
charger operation. Measure binary/heap effects on hardware as appropriate.

There was no firmware target build/upload, live broker operation, NVS access on
hardware, charger setting change or CAD change. Keep bridge images/local adapter
inputs for later migration. Checkpoint 3 requires separate owner authorization.
