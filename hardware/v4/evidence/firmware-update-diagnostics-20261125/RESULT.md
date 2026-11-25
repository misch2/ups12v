# Firmware Update template fix and network diagnostics - 2026-11-25

Baseline: 3c648a3 with owner's version 20261125.8 retained. UPS4 owner boot logs
identify HW 4.0 / ESP32-C3. The owner reports Arduino OTA boot, Wi-Fi, MQTT and
the FW/HW banner working; manifest checks fail with a generic HTTPS/read error.

## Changes

- Fixed discovery's `value_json.update` lookup: Jinja resolves that to the
  dictionary method. Explicit bracket lookups select the actual JSON objects.
  Reconnecting MQTT republishes corrected retained discovery with the same IDs.
- The native MQTT suite exports actual production discovery/state JSON, then
  four Jinja immutable-sandbox tests render it. The original dot lookup is a
  negative control reproducing the TypeError. Startup, available and failed
  recheck states are covered. CI installs Jinja2 3.1.6.
- Worker results carry the failing network stage, HTTP status, SDK and TLS error
  codes, certificate verify flags and socket errno before HTTP cleanup. They
  reach `details.network` in web/MQTT status and a main-thread syslog diagnostic
  line including UTC. The worker does not log or access mutable app services.
- Tests inject connect/TLS, HTTP 404 and read failures and verify error capture
  and cleanup. A same-error retry publishes updated diagnostics even if MQTT
  never observes the intermediate checking state.

## Validation boundary

Desktop TLS 1.2 with only the firmware PEM roots returns HTTP 200 and stable
version 20261125.8. This establishes current feed accessibility from this PC,
not ESP32 connectivity. No CA, hostname or transport verification was relaxed.

The real UPS HTTPS cause remains unknown until the diagnostic build runs there.
No device upload, on-device TLS/flash test or live HA test was performed by the
agent. Owner-provided boot logs are distinct from local test evidence. Fixture
versions and device names in the emitted JSON are synthetic native-test inputs.

The Arduino OTA numeric response `464` preceding final `OK` is a final short
chunk byte-count acknowledgement: the owner's previous V4 image was 1,484,240
bytes, whose remainder modulo 1024 is 464. Final `OK` reports updater success.
No uploader change was made.

## Local verification

Ten native suites, four Jinja rendering checks and thirteen Python packaging/CA
tests pass. Target builds and final-byte staging are recorded below.

All three target builds pass, including final-byte staging against both generated
OTA slots and local bundle assembly. No partition layout changes. Local assembly
uses a zero commit ID to denote verification of uncommitted code; it is not a
published release. Binary hashes are in [final-image-sizes.json](final-image-sizes.json).

| Target | Final bytes | OTA slot bytes | Spare bytes |
| --- | ---: | ---: | ---: |
| ups_v1_esp32 | 1297056 | 1310720 | 13664 |
| ups_v3_sys_esp32 | 1295504 | 1310720 | 15216 |
| ups_v4_esp32c3 | 1487168 | 1966080 | 478912 |

Logs: [build](build.log), [native and Jinja tests](native-tests.log),
[emitted MQTT fixture](firmware-update-wire.json), [desktop HTTPS](desktop-https.json).
