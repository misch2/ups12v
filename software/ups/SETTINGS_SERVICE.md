# Configuration change service

Checkpoint 4 provides the configuration operation exposed by checkpoint 5's
[LAN interface](WEB_CONFIGURATION.md). The owner intentionally skipped checkpoint
7's additional HA/MQTT configuration controls; existing telemetry/controls remain.
Existing device IDs, topics, hardware variants and PlatformIO environments remain.

## Proposal and application

[`Settings::Service`](include/settings_service.h) owns the desired settings and
application status. Call `propose(candidate)` with a complete `RuntimeSettings`
candidate derived from `desired()`, including unchanged credentials. Validate the
whole candidate together so dependent fields can change in one operation.

The service validates identity, hardware applicability and representable register
values, prepares owned strings, then saves through the guarded checkpoint 2 store.
A failed save leaves desired settings, active RAM settings and status unchanged.
As documented for the store, a failed storage acknowledgement does not guarantee
that flash still contains the old record. No charger or network operation runs
inside `propose()`; callers must serialize proposals in the main-loop context.

`tick(application, millis())` performs application outside request callbacks.
Metadata updates take effect there without requiring a charger. Charger settings
remain pending until a suitable input state and verified application. Deferred or
failed applications retry every five seconds; charger recovery/reset invalidates
the previous verification. Revision counters describe this session, not NVS schema.

| Status | Meaning |
| --- | --- |
| `UNCONFIGURED` | No active boot configuration; a valid first proposal requires restart. |
| `PENDING` | Desired power settings await verification. |
| `DEFERRED` | Charger/input unavailable, detection/HiZ/OTG/backup active, or battery-supply test active. |
| `FAILED` | A charger operation or fresh readback failed; desired settings remain saved. |
| `APPLIED` | Latest power transaction passed fresh readback. |

`desiredRevision` and `appliedRevision` distinguish saved intent from application.
`restartRequired` separately reports saved network changes. MQTT/syslog strings
remain unchanged in the active configuration until reboot, preserving the network
worker's borrowed references. A power transaction can be `APPLIED` while a network
restart is still required; the full desired revision is then not marked applied.
These internal objects include credentials: expose only an explicitly filtered
status/export representation in later interfaces. The provisioned ID is immutable.

## Power transaction

[`applyPowerSettings`](include/settings_apply.h) uses the production charge-current
and voltage-profile helpers. It revokes V4 ARM through its caller, disables and
verifies charging, applies values, then reads actual registers before restoring
charge permission. It handles input/output settings even when the old initialization
marker is set. Partial failures retain the desired power policy for recovery and
keep ARM LOW; legacy boards have only best-effort I2C charge disable on an I2C fault.

The runtime transaction does not reset the IC, change CELL, enable OTG/backup or
change HiZ. Initial boot/reset setup retains its existing responsibilities. SYS
hardware rejects changes to inactive PMID output/backup-ratio fields. Positive
register requests must match the IC step/range; existing nonpositive skip-write
values remain supported. A zero pack current ceiling inhibits charging.

Current limits apply for both 2S and 4S, using chip-reported CELL. Diagnostic charge
inhibition remains effective. LEGACY leaves VREG untouched and preserves its charge
enable state until the existing voltage hysteresis logic acts. Battery-only and
unsafe input states defer writes. An external ILIM clamp is accepted only with
EN_EXTILIM enabled and a lower valid readback; status reports the effective input
limit and `inputClamped`, rather than claiming the requested current was achieved.

Register limits follow [TI BQ25798 SLUSDV2C revision C](https://www.ti.com/lit/ds/symlink/bq25798.pdf),
sections 7.5.1.4/.5/.9/.10; external input limiting is described in 7.3.4.3.
IOTG validation uses 160..3320 mA in 40 mA steps: the common range of the datasheet
(120..3320) and installed library (160..3360). Existing device values fit. These
are register representation limits, not qualification of the board, battery or load.

## Verification

[`settings_service_test.cpp`](tests/settings_service_test.cpp) executes production
service/codec/store and power helpers with simulated storage and charger registers.
It covers save failures, dependent updates, metadata, immutable active network
settings, identity, deferred/failed retries, 2S/4S, current ceilings, ignored writes,
fresh readback, external limiting, diagnostic inhibition and LEGACY behavior.

Run from the repository root with the same host toolchain as earlier checkpoints:

```powershell
$env:PATH = 'C:\msys64\ucrt64\bin;' + $env:PATH
$jsonInclude = (Resolve-Path software/ups/.pio/libdeps/*/ArduinoJson/src | Select-Object -First 1).Path
New-Item -ItemType Directory -Force .tmp/universal-firmware-step4 | Out-Null
& 'C:/msys64/ucrt64/bin/g++.exe' -std=c++11 -Wall -Wextra -Werror -Isoftware/ups/tests/support -Isoftware/ups/include -I $jsonInclude software/ups/tests/settings_service_test.cpp software/ups/src/settings_service.cpp software/ups/src/settings_codec.cpp software/ups/src/settings_store.cpp -o .tmp/universal-firmware-step4/settings_service_test.exe
& ./.tmp/universal-firmware-step4/settings_service_test.exe
```

Target builds, real NVS, RTOS/network interaction and electrical behavior remain
owner checks. On matching hardware check forward-input application, reconnect and
IC reset, unavailable charger, diagnostic inhibit, 2S/4S charge limits, LEGACY and
PMID/SYS behavior. No firmware upload or live power test was performed here.
