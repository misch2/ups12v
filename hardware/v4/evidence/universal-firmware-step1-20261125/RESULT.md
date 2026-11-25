# Universal firmware checkpoint 1

Date: 2026-11-25. Source baseline: `0119bcbdef45618b867268590487f3cbcb1b49cd`.
Scope: separate hardware profiles and runtime settings, retaining existing device
environments and source configuration values. Storage, provisioning and UI are
outside this checkpoint.

## Implementation

- Added `Hardware::Profile` with immutable version/pins and version-derived
  MCU/power path. Three shared profiles preserve the previous pins and polarity.
- Moved the common 5600/33000 ohm TS divider into hardware constants.
- Added `RuntimeSettings`, preserving the battery cell/pack split, all operational
  numeric defaults and per-device overrides. Text uses owned Arduino String.
- Kept `Config` as a runtime-settings alias for local shared settings. Removed
  hardware fields from runtime settings and redundant pin assignments from the
  ignored shared config. Its remaining content was verified unchanged without
  recording or exposing its credentials.
- Updated all nine adapters, including the example, and C-string API boundaries.
  Generic MQTT username/password defaults are empty; each existing adapter supplies
  its credentials from local settings or explicit example placeholders.

## Source review

The [complete field inventory and device table](../../../../software/ups/CONFIGURATION.md)
includes inherited defaults and the local shared configuration. Review of all
nine adapter diffs shows no changes to their operational values or identifiers.
The old per-device hardware selections map to the three shared profiles.

Reviewed details include UPS2's 1500 mA / 4700 mV input limits, UPS3's 1000 mA
requested charge current (still subject to its 700 mA pack ceiling), and UPS4-8's
3955/3300 mV cell presets. Unused SYS-path IOTG values are preserved as well.

`UPS.ino` changes replace hardware accessors and adapt owned strings at C API
boundaries. Charge-current/profile helpers, readback/ARM sequencing, chip CELL
handling, Wi-Fi/OTA hostname macros and startup order remain the same. No MQTT
serializer, entity key, topic, unique-ID or default-entity-ID changes were made.
`platformio.ini`, telemetry policy and the existing behavioral tests are unchanged.

Reference review found no remaining old mutable hardware accesses in firmware or
adapters. Modified/new firmware source respects the 160-column limit. Whitespace
and local documentation-link checks pass.

## Validation boundary and next action

These are source/diff checks, not an executable effective-settings comparison.
No firmware builds, compiled tests, uploads, broker operations or hardware tests
were run under the owner-run build boundary. Target compilation and live
MQTT/HA/charger behavior remain pending. Owned strings may change memory usage;
binary sizes and free heap have not been measured.

Owner validation uses the existing `ups1` through `ups8` environments (and the
example if needed). Before uploading any result, check its final binary against
the installed partition slots. Review checkpoint 1 before authorizing checkpoint
2, which adds persistence and the migration bridge.
