# Firmware update checkpoint B2 - 2026-11-25

Baseline: universal-firmware, owner commits through `efacf860`; working-tree
implementation. Owner version `20261125.4` preserved. No tags/pushes/deployments.

Implemented the device HTTPS checker/downloader and main-loop coordination.
HA Update entity and web install controls remain the next checkpoint. Existing
shared 2S/4S targets, stable identifiers, charging rules and NVS are preserved.

## Checks actually performed

- Nine native C++11 production-module suites passed with MSYS2 UCRT64 g++,
  `-Wall -Wextra -Werror`, and cached real ArduinoJson headers: charge_current,
  charge_profile, settings_store, boot_network, settings_service, config_web,
  recovery, firmware_update, firmware_update_worker.
- New service and worker suites were rerun after the final state-name change.
  Runner: `software/ups/tests/run_native_tests.py`. Build/run logs are retained
  locally in `.tmp/firmware-update-step2/native/`; run output is captured here.
- Twelve Python release/partition packaging tests passed, including the shared
  32-bit version-revision bound. Images, partitions and HTTP responses are fixtures.
- Inspected installed SDK headers for HTTP transport/redirect API, mbedTLS SHA-256
  calls, enabled certificate bundle, OTA partition and Update APIs. Checked ESP
  image chip-ID offset against installed esptool. This is not a target build.

New behavioral coverage includes all hardware identities, numeric versions,
manifest bounds/trailing data, fixed release URLs, actual-slot rejection, exact
request version, delayed workers, six-hour scheduling/rollover, transient retry,
conflicting operations, SHA-before-finalize ordering, wrong chip/header, fragmented
and chunked reads, truncated/extra data, hash/flash failures, foreign Update
ownership, HTTPS configuration and redirect downgrade rejection. Settings/web
suites exercise the new write locks and continued read access.

The worker tests compile the real backend using simulated ESP-IDF, FreeRTOS,
mbedTLS and Update interfaces. They do not establish real cryptographic correctness,
certificate connectivity, flash persistence, latency, reset recovery or electrical
safety. No firmware build, upload, live-device interaction or real HTTPS/flash
installation was performed. Final image fit and all target builds remain CI/owner
checks. No post-boot health/rollback mechanism is claimed.

The initial public feed returned 404 to the owner. Prior diagnosis and the branch
CI trigger are documented in V4_HANDOVER.md; a successful public deployment has
not been observed in this checkpoint. The updater will report/retry a missing feed.
