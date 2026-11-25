# Universal firmware implementation plan

Replace per-device binaries with hardware variants and persistent configuration,
while preserving installed devices, charger behavior and Home Assistant identity.
Execute one numbered checkpoint at a time, review its result and update the
handover before continuing. Checkpoints 1-3 are implemented, with native coverage
of persistence, boot, discovery and connection ownership using simulated platform
services. Owner firmware builds/live validation remain pending. Checkpoints 4-8
have not started.

Baseline: branch `universal-firmware`, commit
`0119bcbdef45618b867268590487f3cbcb1b49cd`, inspected 2026-11-25.

## Agreed design

- A hardware variant fixes the MCU, pins, USB/flash settings and hardware
  version/power-path topology. Hardware version and topology are one choice.
- Share each variant's binary between 2S and 4S. Continue reading the charger's
  `CELL` setting; do not infer cell count from voltage or write `CELL` as part
  of provisioning.
- Keep the TS divider common to all variants. Distinguish those fixed resistor
  values from configurable NTC characteristics if different thermistors are used.
- Provision the existing device identifier once. It supplies MQTT namespaces,
  HA device identifiers, entity unique IDs and default entity IDs. Customize
  display names in HA; no separate firmware display-name feature is needed.
- Provide a dedicated web form on the normal LAN for Wi-Fi, syslog, MQTT and
  device ID, plus operating settings. Use the same form for first setup/recovery.
- Expose operating settings through HA using the same configuration service.
  Network credentials and device identity belong in web setup.
- Retain the current battery cell/pack structure and all existing telemetry,
  including the 20% warning, 80% target diagnostics and temporary power overrides.

## Changes in the merged baseline

`platformio.ini` now has eight installed-device environments (`ups1` through
`ups8`), plus base/example environments. The profiles map to three target variants:

| Proposed environment | Current devices | Hardware and power path | SDA / SCL / LED / CHARGE_ARM |
| --- | --- | --- | --- |
| `ups_v1_esp32` | UPS1 | V1.0, PMID switchover | 21 / 22 / 2 / absent |
| `ups_v3_sys_esp32` | UPS2, UPS3 | V3.3b SYS modification, SYS | 21 / 22 / 2 / absent |
| `ups_v4_esp32c3` | UPS4 through UPS8 | V4.0, SYS | 4 / 5 / absent / 0 |

Names are proposed; preserve the actual board definitions and LED/ARM polarities.
The example is a template, not a fourth installed hardware variant.

Commit `c7ea19e` moved cell identity, per-cell voltage presets and diagnostic
override limits under `battery.cell`, and capacity/current ceiling under
`battery.pack`. Commit `8390be3` added the almost-depleted warning and voltage
presets. Use these current fields and values throughout migration; do not restore
the older flat battery model or older presets.

At that baseline, runtime settings storage and a general web configuration server
were absent. `haClient` copied identity during global construction. `HOSTNAME` selected
the Wi-Fi/OTA hostname and MQTT client ID. `setupCommunication()` waited
for WiFiManager before the first charger service. The `VAC2_ADC_DIS` marker skips
some charger initialization, so saving new values alone cannot apply all settings.

## Checkpoint 1 Separate hardware and runtime configuration

**Status 2026-11-25:** Implemented. See the [field inventory and preserved device
values](CONFIGURATION.md). Hardware profiles and owned runtime text are separated;
all nine adapters retain their values. Generic MQTT credentials are now empty;
installed adapters still use their local credentials. Source/diff review is
complete; builds and live checks remain owner-run. Next is checkpoint 2 after
review of this change.

**Change:** Introduce an immutable hardware profile and an owned runtime settings
model. Keep the existing device environments as adapters, with identical effective
values. Inventory every current configuration field, including inherited local
defaults, without copying credentials into tracked documents.

| Group | Treatment |
| --- | --- |
| Hardware version, topology, pins, USB/flash settings | Compiled profile |
| TS divider resistors | Common fixed values |
| Device ID, Wi-Fi, MQTT, syslog | Provisioned settings |
| `battery.cell` and `battery.pack` | Persistent operating settings; preserve the split |
| Charge profile, full voltage, recharge offset, requested ICHG | Persistent operating settings |
| Input limits, adapter retry, applicable output/backup settings, AC recovery delay | Persistent settings with hardware applicability |
| Legacy charge thresholds, percent-estimate endpoints, NTC resistance/beta | Advanced settings; preserve existing values and meaning |
| Active diagnostic overrides, register cache, availability | Runtime state, never restored as saved ON requests |
| Debug telemetry flag | Development build option, not a per-device deployment variant |

Use owned strings or buffers for values that will later load from storage; avoid
temporary `c_str()` pointers in the current `const char*` configuration fields.
Generic defaults must not contain deployment credentials. Local secrets remain
available only to the transitional device adapters.

**Check:** Compare effective non-secret settings for all eight profiles before and
after the refactor. Include UPS2 input limits, UPS3 requested current and the
current UPS4-8 cell presets. Preserve MQTT payloads and existing charger behavior.

**Finish:** Hardware/runtime ownership is explicit; no storage or UI yet. Review
the field inventory and three-variant mapping before moving on.

## Checkpoint 2 Add persistent settings and a migration bridge

**Status 2026-11-25:** Implemented on the checkpoint 1 baseline `e542e03`. The
[migration bridge and schema](PERSISTENT_SETTINGS.md) use one native NVS blob,
seed only on absence, protect incompatible/unsupported records and provide
credential-free export/import codecs. Production modules pass native behavioral
tests with simulated text/BQ/NVS dependencies and real ArduinoJson headers.
Compiled settings still run the application; saved-settings startup is checkpoint
3. Firmware builds, uploads and real NVS persistence remain owner checks.

**Change:** Add a versioned settings codec, validation and a small storage adapter.
Use ESP32 Preferences/NVS as the proposed backend. Keep a complete, explicitly
serialized settings record; do not store raw C++ structs or pointers. Define
complete-record replacement and write-error behavior so a failed save cannot
silently produce a mixture of settings.

While device adapters still exist, add a bridge path that seeds an absent record
from that device's current effective configuration and exact identifier. Reuse
its existing saved Wi-Fi connection. Establish one authoritative source for Wi-Fi
settings and coordinate SDK credential storage instead of allowing conflicting
copies. Do not erase the entire NVS partition.

Distinguish absent settings, a supported older schema, invalid data and a newer
unsupported schema. Never overwrite an existing record with compiled defaults
on ordinary boot or downgrade. Export/import the complete operating configuration
and hardware compatibility metadata; keep normal exports free of passwords and
explain how credentials are restored separately.

**Check:** Behavioral tests of the production codec/store interface for round trips,
first seed, existing-record preservation, malformed/unsupported records and failed
writes. Owner checks NVS persistence on reboot and a bridge upload on one device.

**Finish:** Existing settings can be carried into a later universal image. Keep
the bridge images/profile inputs available until all installations are migrated.

## Checkpoint 3 Load settings before identity and network startup

**Status 2026-11-25:** Implemented on checkpoint 2 baseline `5086657`. See
[startup and recovery](STARTUP.md). Saved records activate before session identity
and clients; invalid/unsupported records cannot fall back to compiled operation.
Charger service starts before Wi-Fi, while DNS/MQTT handshakes use an exclusive
worker handoff. The actual discovery serializer and boot/worker modules pass
native tests; persistence regression tests pass. Wi-Fi uses SDK-saved credentials;
the blocking portal is no longer entered, with new forms deferred to 5/6. Target
builds, real networking, RTOS/heap and hardware behavior remain owner checks.

**Change:** Load settings before assigning identity to HA, MQTT, OTA and syslog.
Replace compile-time `HOSTNAME` uses and the HA client's early name copy with an
explicit initialization step. Keep identity fixed for the running session.

Preserve the exact identifier, topics, unique IDs, keys and the `888d02c`
`default_entity_id` normalization rule. Do not publish discovery under a generic
or temporary setup identifier. Validate newly entered IDs against hostname/topic
requirements and normalization collisions; keep existing valid IDs unchanged.
Do not offer ordinary device-ID editing after commissioning.

Reorder startup and use cooperative network connection attempts so saved charger
operation does not depend on Wi-Fi, MQTT or syslog being reachable. Maintain the
early V4 CHARGE_ARM LOW action and charger readback checks. A blank/invalid
configuration must remain serviceable for setup without claiming charger readiness;
on legacy boards distinguish software EN_CHG control from V4's physical ARM gate.

**Check:** Verify unchanged discovery identity for a migrated device, no discovery
before commissioning, two distinct device identities, offline boot and reconnect.
Check that long setup/network waits cannot prevent charger servicing.

**Finish:** Runtime identity and saved settings work independently of the new UI.

## Checkpoint 4 Add one service for configuration changes

**Status:** Implemented on baseline `981d1fc`; native behavioral tests pass.
See [service behavior and validation boundaries](SETTINGS_SERVICE.md). Target
builds and live checks remain owner-run. No web/HA configuration endpoint is added.

**Change:** Provide one typed operation used later by HTTP and MQTT: propose a
candidate, validate it, save the complete desired configuration, then schedule its
application in the main loop. A storage failure leaves the current configuration
unchanged. Report desired values separately from hardware application status.

Apply metadata changes directly. Apply charger changes through existing current
limit/profile logic with fresh readback, respecting topology and diagnostic
overrides. Explicitly handle input/output settings skipped by the initialization
marker. Do not reset the whole charger for every edit or reconfigure backup/OTG
blindly while supplying the load. Classify changes as immediate, deferred until a
suitable power state, or requiring a network restart.

If the charger is absent, retain a valid desired configuration as pending. If a
write/readback fails, report the failure, preserve existing inhibit/ARM behavior
and retry through recovery; never claim the requested registers are active.
Reuse current validation rules and IC limits; propose any new restrictions for
review. Preserve legacy mode semantics, including its lack of VREG restoration.

**Check:** Behavioral tests with charger/storage substitutes cover rejected input,
dependent field updates, save failures, I2C failures, unavailable hardware,
already-initialized recovery, current ceilings and both 2S/4S calculations. Test
production modules directly; no source-text checks or extracted-function harnesses.

**Finish:** Both future interfaces have one authoritative validation/apply path.

## Checkpoint 5 Add LAN web configuration

**Change:** Add a small server-rendered form, using the Arduino core WebServer
as the first candidate. Serve it from firmware without a separate filesystem image
or frontend build toolchain. Review the server's timing against the installed core.

Provide network setup (Wi-Fi, syslog, MQTT, device ID before commissioning), battery
cell/pack settings, applicable operating settings, save/apply feedback and settings
export/import. Display the hardware variant and charger-reported cell count as
read-only values. Leave display-name customization to HA.

Agree on lightweight LAN write protection before enabling configuration writes.
Do not return passwords in status/export responses, echo them into forms, or log
configuration request bodies. Handle network changes after returning the response,
with a clear reconnection/recovery path. Unchanged password fields preserve their
stored values; distinguish that from an explicit clear operation.

**Check:** Owner browser checks from the normal LAN: load, invalid submissions,
save/reload, credentials preservation, cross-field errors and changed broker/Wi-Fi
settings. Confirm OTA and charger service remain available during web use.

**Finish:** Routine configuration works in a normal browser without entering an AP.

## Checkpoint 6 Add first setup and recovery and remove WiFiManager

**Change:** Reuse the same web form for initial setup and lost-network recovery.
Proposed mechanism: a device-specific setup AP for an unconfigured unit and a
deliberate recovery entry point for configured units. Review the on-demand trigger
and network-failure fallback policy here; do not invent a spare button/GPIO or
erase settings just because a network is unavailable. An initial AP is reachable
from a laptop as well as a phone; routine configuration stays on the LAN.

Implement the chosen Wi-Fi/recovery state machine without blocking power control
or repeatedly rebooting on connection failure. Remove the WiFiManager dependency
after its provisioning role is replaced. Define reset-network versus full-settings
reset separately, including the consequences for the provisioned identifier.

**Check:** Owner checks blank first boot, wrong Wi-Fi credentials, recovery on
demand, AP-to-LAN transition, lost network and reboot with valid saved settings.
The setup AP must not cause MQTT discovery under an interim name.

**Finish:** A generic blank image can be commissioned and recovered without a
device-specific build. The recovery trigger/policy is the remaining design choice
for this checkpoint, not an implementation prerequisite for checkpoint 1.

## Checkpoint 7 Add Home Assistant configuration controls

**Change:** Extend discovery and command handling for acknowledged MQTT `number`,
`select` and appropriate `text`/`switch` configuration entities. Start with charge
profile and requested charge current, review that slice, then add remaining
operating settings from checkpoint 1. Keep identity and network secrets web-only.

Use distinct configuration keys such as `cfg_charge_profile`, because entity
unique IDs currently share one device/key namespace across domains. Preserve
existing read-only sensors and their state keys. Do not make all BQ registers
writable. Supply appropriate options, units, ranges and steps from the validated
settings definitions; apply the HA `config` category only to supported domains.

Route commands through checkpoint 4, outside direct charger writes in the MQTT
callback. Publish accepted desired values and pending/error status separately
from actual register telemetry. HA controls must also work when the charger is
absent; the current blanket `!chargerReady` command guard needs selective routing.
Use non-retained commands, retained accepted configuration states, reconnect
republishing and the existing telemetry policy. Do not persist transient test ON
requests. Web changes update HA and HA changes update the web view.

**Check:** Discovery serialization, unique-key collisions and MQTT packet sizes;
owner checks both directions of synchronization, invalid commands, restart,
reconnect, pending application and unchanged existing HA/Grafana entities.

**Finish:** Both configuration interfaces use the same stored settings and rules.

## Checkpoint 8 Consolidate builds and migrate installations

**Change:** Finalize the three hardware environments above, without device names,
battery presets, credentials or fixed OTA destination addresses in their binary
configuration. Keep destination selection in the upload command/local tooling.
Remove installed-device environments only after bridge migration and backup.
Keep the same partition layout unless size evidence requires a separate change.

Prepare a per-device migration checklist for UPS1-8: exact identifier, variant,
configuration saved by the bridge, credential handling, backup and rollback image.
Migrate one owner-selected V4 unit first, then the remaining V4 units and the
legacy variants after their checks. Unmigrated devices remain on their old images.
An old binary may ignore NVS settings: rollback must state which compiled settings
will become active and how newer stored schemas are preserved.

**Check:** Owner builds each hardware environment and checks final binary sizes
against both installed OTA slots before upload. A partition change requires an
explicit full-flash migration path; an application OTA does not replace the
partition table. Verify the shared image on matching 2S and 4S hardware, cold boot,
charger reconnect, source loss/recovery, charging limits and network outages.
Record revision, battery, source, load and evidence for power tests. Verify no
duplicate HA devices, changed entity IDs or lost telemetry history references.

**Finish:** Three hardware binaries replace eight installed-device configurations.
Publish concise setup/update instructions in the firmware README; keep developer
details and migration evidence linked separately. Review the final checkpoint
with the owner before removing transitional inputs.

## Execution and validation boundaries

Checkpoints 1-4 are implemented; owner build/live validation is pending.
Checkpoint 5 is the next implementation task after review. Later checkpoints are
separate changes, not authorization to execute the entire migration. Update this plan and
`hardware/v4/V4_HANDOVER.md` with the completed checkpoint and next action.

Firmware builds, uploads and live power tests remain owner-run under the existing
workflow. Proportionate behavioral tests are planned for configuration and charger
logic; source/diff checks alone do not establish target compilation or hardware
behavior. No CAD changes are part of the firmware configuration refactor.

## Implementation references

- Current code: [`config.h`](include/config.h), [`platformio.ini`](platformio.ini),
  [`UPS.ino`](src/UPS.ino), [`homeassistant_mqtt.cpp`](src/homeassistant_mqtt.cpp),
  [`charge_profile.h`](include/charge_profile.h) and
  [`charge_current.h`](include/charge_current.h).
- [ESP32 Preferences](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/preferences.html)
  provides NVS persistence. Verify APIs against the installed core when implementing.
- [Arduino ESP32 WebServer](https://github.com/espressif/arduino-esp32/tree/master/libraries/WebServer)
  is the proposed form server; no additional asynchronous server library is assumed.
- HA documents [MQTT number](https://www.home-assistant.io/integrations/number.mqtt/),
  [MQTT select](https://www.home-assistant.io/integrations/select.mqtt/) and
  [default entity IDs](https://www.home-assistant.io/integrations/sensor.mqtt/#default_entity_id).
  A default entity ID with a unique ID is used at initial entity registration;
  changing it later is not an entity migration mechanism.
