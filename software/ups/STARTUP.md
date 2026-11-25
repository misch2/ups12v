# Saved settings and cooperative startup

Checkpoint 3 activates the settings record before assigning identity or starting
network clients. Existing device environments remain the migration inputs; web
configuration and live settings changes are later checkpoints.

## Boot configuration and identity

Startup preloads V4 CHARGE_ARM LOW, starts Serial and loads `ups-settings/config`.
A valid record is authoritative, even if its settings or identifier differ from
current adapter defaults. Only absent storage can be seeded from a valid adapter,
then reloaded. `default-ups` is not commissioned and is never seeded or announced
by this startup path.

Malformed, unsupported, oversized or incompatible records and storage errors do
not fall back to compiled operating settings. Normal charger initialization and
MQTT stay disabled. V4 ARM remains LOW; legacy boards receive best-effort EN_CHG-off
writes/readback when the charger is reachable. An I2C failure cannot establish an
independent cutoff on legacy hardware. No code clears the record, changes CELL or
substitutes another power-path topology.

After successful activation, charger service runs before Wi-Fi starts. Existing
current ceilings, readback/ARM sequence, initialization marker and profile logic
remain in use. Loading desired settings does not prove every register matches:
reapplication of settings skipped by the marker and runtime changes are checkpoint
4 work.

[`DeviceIdentity`](include/device_identity.h) binds once per session. HA, MQTT
client ID, Wi-Fi hostname and OTA use that loaded identifier. Syslog uses its saved
host/application labels. Adapter `HOSTNAME` macros are no longer read by runtime
startup, and the HA client does not copy identity during global construction.

IDs contain ASCII letters/digits and interior hyphens, without leading/trailing
hyphens. The limit is 31 characters: the installed Arduino NetworkManager copies
into a 32-byte hostname buffer. Valid stored case is preserved. New IDs must be
lowercase; rejecting uppercase aliases and underscores avoids those normalization
collisions. IDs must still be unique across installations; there is no broker
registry lookup here. Installed UPS1-8 identifiers satisfy the policy unchanged.

Discovery/state/command/availability topic formulas, entity unique IDs and the
`888d02c` default-entity-ID normalization are unchanged. Display names stay
HA-managed. Publication/removal is gated until identity and transport are ready,
so setup hosts cannot create temporary HA entities.

## Connection waits and client ownership

Wi-Fi starts with SDK-saved credentials, retries without waiting for an IP and
does not reboot on connection failure. OTA starts after an IP is available and
restarts after Wi-Fi recovery. DNS and TCP/MQTT handshakes run in one FreeRTOS
worker, with a 4096-byte stack and two single-item queues. ESP-IDF task stack sizes
are in bytes. [ESP-IDF FreeRTOS](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/freertos_idf.html)

Before queuing an attempt, the main loop gates every MQTT publisher and gives the
worker exclusive access to PubSubClient and its Wi-Fi socket. No main-loop client
access or socket stop occurs until the result queue returns ownership. The worker
does not touch I2C, application logging, HA publication or mutable settings. The
main loop then subscribes and republishes discovery/state. MQTT retry delay is
60 seconds, with immediate retry after detected recovery; Wi-Fi retry is 30 s.
Unsigned timing handles millis rollover.

Syslog DNS shares that worker; its client is created on the main loop from the
resolved IP. Configured power service and OTA do not wait for broker/syslog
reachability. If buffer/task allocation fails, MQTT stays disabled and configured
charger service continues.

This isolates connection waits, not every network operation. Routine publishing,
MQTT callbacks, UDP syslog and OTA still use the existing main-loop libraries and
can have their own bounded waits. Native tests are not a hard real-time guarantee.
The worker references immutable session settings; later configuration application
must wait for client handoff before changing network settings/rebuilding clients.

## Recovery during this intermediate checkpoint

An unconfigured unit uses `ups-setup-<12 hex MAC digits>` only as a local service
hostname. It can reconnect with SDK-saved Wi-Fi and offer OTA there, but never
connects to MQTT or publishes discovery under that name. USB recovery remains
available without Wi-Fi. An older bridge image uses its own compiled settings
and does not erase the protected record.

The blocking WiFiManager boot portal no longer runs. Network access at this
checkpoint requires saved Wi-Fi; a fresh unit without credentials needs the
existing USB/bridge provisioning path. Dedicated LAN and initial AP/recovery
forms arrive in checkpoints 5/6. The PlatformIO dependency stays until that later
cleanup. No replacement AP form is claimed here.

## Native tests and owner checks

[`boot_network_test.cpp`](tests/boot_network_test.cpp) compiles the production boot
loader, HA serializer, connection state and worker with real ArduinoJson. Text,
MQTT/Wi-Fi, logging and queue/task services are substituted. Delayed task completion
is simulated; no ESP32 scheduler, live broker or local credentials are involved.

Run from the repository root:

```powershell
$env:PATH = 'C:\msys64\ucrt64\bin;' + $env:PATH
$jsonInclude = (Resolve-Path software/ups/.pio/libdeps/ups8/ArduinoJson/src).Path
New-Item -ItemType Directory -Force .tmp/universal-firmware-step3 | Out-Null
& 'C:/msys64/ucrt64/bin/g++.exe' -std=c++11 -Wall -Wextra -Werror -Isoftware/ups/tests/support -Isoftware/ups/include -I $jsonInclude software/ups/tests/boot_network_test.cpp software/ups/src/boot_settings.cpp software/ups/src/settings_codec.cpp software/ups/src/settings_store.cpp software/ups/src/homeassistant_mqtt.cpp software/ups/src/network_worker.cpp -o .tmp/universal-firmware-step3/boot_network_test.exe
& ./.tmp/universal-firmware-step3/boot_network_test.exe
```

Tests cover stored-settings precedence, guarded seeding, blank/protected/error
paths, identity validation/locking, two distinct legacy discovery namespaces,
actual unique/default ID serialization, client isolation during pending work,
DNS/task failures, retry timing and rollover. Checkpoint 2 persistence tests also
pass with the expanded adapters. No source extraction or source-text assertions
are used.

Owner checks remain: affected firmware builds, final binary/OTA-slot sizes, real
boot/NVS loading, unchanged HA registry IDs, Wi-Fi/broker outage recovery,
charger/I2C recovery, matching 2S/4S hardware, heap and worker stack margin. Record
BOM/revision, cells, source and load for power checks. Check invalid-record/USB
operation on V4 and legacy boards separately. No firmware build/upload or live
hardware/network operation was performed by the agent.
