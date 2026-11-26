# Device firmware update service

Checkpoint B2 implements the shared release checker and installer. Checkpoint B3
connects it to a standard Home Assistant MQTT Update entity and web controls.
See [usage and testing](FIRMWARE_UPDATE_CONTROLS.md). No release installs automatically.
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
Integration uses the shared `FirmwareControls` implementation in `UPS.ino`, which
also checks push OTA, pending/in-flight web actions and the battery-supply
diagnostic override. It locks settings writes as soon as installation is queued.

The worker has a 12288-byte FreeRTOS stack and owned, fixed-size job/result
messages; progress uses a separate overwrite queue. It accesses HTTPS and flash,
without accessing charger registers, MQTT, the application logger or mutable
settings. Connection setup has a 15-second timeout, capped by the remaining
manifest/download budget on each redirect. After connecting, header and body reads
use a five-second socket timeout. A body read that times out with no data retries on
the existing connection within the 20-second manifest or 180-second download
budget. A read that reports a connection error or incomplete EOF still aborts
the transfer. SDK calls can take their own timeout to return.
The main loop continues charger servicing, timers, recovery and telemetry.

A queued installation waits for pending power settings to finish and for Wi-Fi,
clock and override readiness. From reservation through completion, configuration
writes, reset/recovery actions and Arduino push OTA are blocked; reads remain
available. Charger diagnostic commands are blocked while flashing or waiting to
reboot. Existing charging/ARM rules continue to operate during the download.
Successful installation schedules a main-loop restart after one second.

`firmware_update_mqtt.cpp` publishes a standard Update entity using the existing
stable device identity. Install payloads bind the advertised version to a fresh
128-bit token on each MQTT connection. Unsupported/stale payloads never select a
newer release implicitly. Configuration and state are retained; commands are not.
Progress publishes at most once per second, with state/error transitions sent
immediately. Unchanged state is detected before constructing JSON.

Web installation is scheduled only after its response finishes, then dispatched
after the existing 300 ms action delay. In-flight reset/action replies also block
competing HA installs. Dropped replies schedule nothing. The read-only firmware
page remains accessible during installation; queued installs can be cancelled.

MQTT's device LWT is now `bq25798ups/<id>/availability`. Charger-dependent entities
require both that topic and the existing `/charger/availability` topic to be
online. Firmware uses device availability plus a verified-feed state, so a charger
failure does not hide firmware updates. Entity IDs and existing state/command
topics are preserved; discovery is republished on reconnect.

## Validation

Classic ESP32 TLS setup also depends on application RAM headroom. HA entity
configuration borrows its labels/classes/units/icons and enum options from static
data or immutable charger metadata; these strings must outlive the configuration.
Computed keys and last-sent values remain owned. This reduces EntityConfig from
192 to 108 bytes on the classic target, plus avoided string/option allocations.
Measured on-device heap gain and recovery from allocation failures remain owner
checks; see [RAM verification](../../hardware/v4/evidence/firmware-tls-ram-20261125/RESULT.md).

Run production-module behavioral tests from the repository root with a host C++11
compiler, resolved ArduinoJson headers and the CI Python dependencies:

```text
python -m pip install -r software/ups/requirements-ci.txt
python software/ups/tests/run_native_tests.py --compiler g++ --json-include software/ups/.pio/libdeps/ups_v4_esp32c3/ArduinoJson/src
```

The runner supports `--suite firmware_update`, `--suite firmware_update_worker`
and `--output <directory>`. It captures compile/run logs. The worker suite compiles
the actual ESP32 backend against simulated SDK, RTOS, network, digest and flash
interfaces. These tests establish control flow and failure handling, not real
TLS, cryptography, flash timing, electrical operation or boot recovery.

Eleven native suites include MQTT discovery/state/command behavior and protected,
deferred firmware web actions. The MQTT suite also renders its actual emitted
discovery/state output in Jinja's immutable sandbox (four checks, including the
dictionary-method collision regression). Thirteen Python tests cover packaging and root
data. All three targets build and pass final-byte release staging
locally after the [size correction](SIZE_OPTIMIZATION.md); actual HTTPS installation
and power-service timing remain unverified on hardware. See
[current build verification](../../hardware/v4/evidence/firmware-update-step3-20261125/RESULT.md) and
[checkpoint evidence](../../hardware/v4/evidence/firmware-update-step2-20261125/RESULT.md).
