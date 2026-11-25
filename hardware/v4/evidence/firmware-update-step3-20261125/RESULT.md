# Firmware update checkpoint B3 - 2026-11-25

Baseline: 5c2f0c5 (universal-firmware), FIRMWARE_VERSION 20261125.7 preserved.
Implementation is uncommitted working-tree code; local release assembly uses an
all-zero synthetic commit marker and is not published.

## Behavior

- Standard HA MQTT Update discovery/state uses the existing stable device identity.
  JSON templates separate supported Update fields from status/error attributes.
  HA owns Skip. Install capability is advertised only for an eligible newer offer.
- Install commands bind the successfully advertised version to a fresh per-MQTT-
  connection 128-bit token. Old sessions, old versions and malformed commands do
  not queue installation; a changed offer cannot be installed by an older request.
- Retained state/config, non-retained commands, initial unknown-feed availability,
  version/progress/release information and retry after failed publications.
  Progress sends at most once per second; transitions are immediate and idle state
  comparison avoids repeated JSON allocation.
- Web /firmware and read-only /firmware/status; protected POST check/install/cancel.
  Web install waits for full response completion plus deferred action dispatch.
  An interrupted response queues no installation. Version validation repeats at
  dispatch. In-flight reset/action replies gate competing installs. Read access
  remains during reservation; cancellation applies before flashing only.
- Device availability has its own LWT. Charger entities require device and charger
  readiness; firmware works without charger readiness. Legacy identities, telemetry
  topics, operating settings and NVS schema are preserved. Charger/ARM service is
  not paused for downloading/flashing. B2 TLS/slot/chip/length/hash guards remain.

## Validation performed

Ten C++11 native suites pass using real production modules and substituted
platform services: charge_current, charge_profile, settings_store, boot_network,
settings_service, config_web, recovery, firmware_update, firmware_update_worker,
firmware_update_mqtt. New cases cover actual JSON output, retained flags, stable
identifiers, split availability, stale version/session rejection, blocked states,
progress cadence/reset/success, publication failures, CSRF/origin gates, escaped
release notes, response-before-install, queued cancellation, changed offers and
unfinished/dropped action replies. No source-extraction harnesses were added.

Thirteen Python packaging/root-data tests pass. Three firmware targets build with
the pinned platform/core/dependencies in the prepared ignored workspace cache.

| Target | Final bytes | Minimum generated OTA slot | Spare |
| --- | ---: | ---: | ---: |
| ups_v1_esp32 | 1295120 | 1310720 | 15600 |
| ups_v3_sys_esp32 | 1293584 | 1310720 | 17136 |
| ups_v4_esp32c3 | 1484944 | 1966080 | 481136 |

Production release staging accepts all actual images against both generated slots;
complete three-variant bundle assembly succeeds. sizes.json records hashes.
Full final compiler log and native/Python results are retained here.

Public https://misch2.github.io/ups12v/firmware/stable.json reports 20261125.7. All
three public images were downloaded through release redirects with only the
embedded CA roots and match manifest lengths/SHA-256 (chip IDs 0/0/5). This public
release predates B3 and was not changed. See public-release.json.

No firmware upload, live HA registration, ESP32 HTTPS installation, power timing,
flash interruption, boot recovery or actual installed-slot readout was performed.
Native SDK/RTOS/network/flash are simulated. Desktop TLS verifies current public
delivery only. The new UI still needs owner acceptance on UPS4; bootstrap and the
later-version install/skip procedure are in FIRMWARE_UPDATE_CONTROLS.md.

Protocol references:
- https://www.home-assistant.io/integrations/update.mqtt/
- https://www.home-assistant.io/integrations/update/
