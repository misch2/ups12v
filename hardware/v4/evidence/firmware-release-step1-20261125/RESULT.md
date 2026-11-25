# Firmware release pipeline checkpoint 1

Date: 2026-11-25. Baseline: `53c56d4`.

Implemented `.github/workflows/firmware-release.yml`, pinned platform/direct
dependencies and released CI CLI, release packaging, feed promotion and documented
manifest schema 1. This is only the first of the three agreed update checkpoints.
No device installer or HA Update entity is claimed implemented.

## Verification performed

- Twelve Python behavioral tests pass: version/tag/calendar gate; complete three-
  variant bundle; exact lengths/hashes/checksums/URLs; missing/unexpected artifacts;
  mixed commit/version/hardware and altered bytes; oversize/invalid images and bad
  partition tables; older/same-version feed promotion; HTTPS fetch/error handling;
  actual version/assemble CLI invocation; previous OTA-capacity regressions.
- Full test output: [packaging-tests.log](packaging-tests.log). Fixtures are
  synthetic; HTTP fetches are substituted. Tests execute production modules,
  with no source-text assertions or extracted-function harnesses.
- Workflow YAML parses and its five-job dependency graph is acyclic/complete.
  All seven shell run blocks pass Bash syntax checking. See
  [workflow-validation.log](workflow-validation.log); this is not an Actions run.
- Installed PlatformIO resolves three hardware variants with explicit platform/
  direct library dependencies. Saved metadata:
  [resolved-dependencies.json](resolved-dependencies.json).

Local inspection found pioarduino 55.03.311, Arduino-ESP32 3.3.11, PlatformIO
6.2.0.post1, timer 3.0.1, Syslog 2.0.1, BQ25798 1.5.3 (clean cached commit
00c12a2504bbaa6f8b6f56146b027fec43831c98), PubSubClient 2.8 and ArduinoJson 7.4.3.
CI uses published PlatformIO 6.2.0, not an assumed available post-release wheel.
This pins intended dependencies; it does not prove byte-for-byte reproduction.

## Limits and activation

No target firmware build, installed partition capture, device upload, live network/
power test, GitHub workflow run, release publication or Pages deployment occurred.
Public release URLs are the proposed contract until an owner-triggered workflow
succeeds. Existing V4 build artifacts were not repackaged as a new release.
The owner's local FIRMWARE_VERSION edit was preserved.

The workflow requires Pages source = GitHub Actions and suitable github-pages
environment deployment rules for fw-* tags. It owns the deployed Pages artifact;
combine existing site content before activation if applicable. A version-matching
tag publishes only after all builds/package checks pass. Generated layout fit is
not installed-device compatibility; the next device checkpoint must enforce actual
inactive-slot capacity and preserve settings/power control. See
[FIRMWARE_UPDATES.md](../../../../software/ups/FIRMWARE_UPDATES.md).
