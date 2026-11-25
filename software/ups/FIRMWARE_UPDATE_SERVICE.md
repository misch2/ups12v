# Device firmware update service

Checkpoint B2 implements the shared release checker and installer. Checkpoint B3
will connect it to a standard Home Assistant MQTT Update entity and web controls.
There is currently no user-facing install action. No release installs automatically.
Existing telemetry, identifiers and charger behavior are preserved.

## Checks and trust

The service checks `https://misch2.github.io/ups12v/firmware/stable.json` after
Wi-Fi and a plausible system clock are available, then every six hours. Network
and worker failures retry after one minute; an explicit check can run sooner.
SNTP starts asynchronously using `pool.ntp.org` and `time.cloudflare.com`.
A missing feed is a check failure, not an empty release. A previous validated
offer remains available after a failed check.

HTTPS uses [embedded GitHub trust roots](certs/README.md), hostname verification
and encrypted transport, including redirects (at most five). The full SDK root
bundle is omitted to fit legacy OTA slots. There is no insecure fallback.
The manifest is limited to 8192 bytes. The selected variant must match the
compiled hardware version, MCU and power-path topology. Version comparison uses
calendar date and numeric revision; same-version installs and downgrades are
rejected. The revision is an unsigned 32-bit integer in both producer and device.
Only the expected versioned URLs in `misch2/ups12v` releases are accepted.

Before flashing, the service checks the actual installed inactive partition and
refuses a missing slot or the running partition. It checks content length when
supplied, exact streamed length in all cases, ESP image magic and target chip,
and SHA-256 over the downloaded bytes. Only after the digest matches does
`Update.end(false)` finalize and select the next boot image. Errors abort the
owned transaction and do not request a reboot. NVS and the partition layout are
not rewritten. This does not add a post-boot health check or automatic rollback;
retain the [migration and recovery record](MIGRATION.md).

## Main-loop coordination

`FirmwareUpdate::Service` owns scheduling, the validated offer, status, errors
and progress. Its `requestInstall(version)` binds a request to the exact offered
newer version; `cancelQueuedInstall()` can cancel before the worker starts.
Integration must use `requestFirmwareInstall()` in `UPS.ino`, which also checks
push OTA, pending web actions and the battery-supply diagnostic override.

The worker has a 12288-byte FreeRTOS stack and owned, fixed-size job/result
messages; progress uses a separate overwrite queue. It accesses HTTPS and flash,
without accessing charger registers, MQTT, the application logger or mutable
settings. Network read timeouts are five seconds, with overall manifest/download
budgets of 20/180 seconds; SDK calls can take their own timeout to return.
The main loop continues charger servicing, timers, recovery and telemetry.

A queued installation waits for pending power settings to finish and for Wi-Fi,
clock and override readiness. From reservation through completion, configuration
writes, reset/recovery actions and Arduino push OTA are blocked; reads remain
available. Charger diagnostic commands are blocked while flashing or waiting to
reboot. Existing charging/ARM rules continue to operate during the download.
Successful installation schedules a main-loop restart after one second.

## Validation

Run production-module behavioral tests from the repository root with a host C++11
compiler and resolved ArduinoJson headers:

```text
python software/ups/tests/run_native_tests.py --compiler g++ --json-include software/ups/.pio/libdeps/ups_v4_esp32c3/ArduinoJson/src
```

The runner supports `--suite firmware_update`, `--suite firmware_update_worker`
and `--output <directory>`. It captures compile/run logs. The worker suite compiles
the actual ESP32 backend against simulated SDK, RTOS, network, digest and flash
interfaces. These tests establish control flow and failure handling, not real
TLS, cryptography, flash timing, electrical operation or boot recovery.

The worker suite and thirteen Python tests (packaging plus trust-root data) pass
after the size correction. All nine native suites also passed on the preceding
self-hosted build. Firmware builds
and final-image size checks remain owner/CI-run; actual HTTPS installation and
power-service timing remain unverified on hardware. See
[checkpoint evidence](../../hardware/v4/evidence/firmware-update-step2-20261125/RESULT.md).
