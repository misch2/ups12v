# UPS V4 handover

## Firmware update checkpoint B3 - 2026-11-25

Implemented on baseline 5c2f0c5, owner version 20261125.7 preserved. Standard HA
Firmware Update entity and /firmware web controls now use the shared B2 service.
HA manages Skip; device never installs automatically. Exact version plus a fresh
128-bit MQTT session token prevents stale/retained install replay. State/config
are retained; commands are not. Progress is limited to 1 Hz; transitions publish
immediately and unchanged state avoids JSON allocation.

Web checks/install/cancel use existing CSRF/Host/origin/revision gates. Installation
waits for the full reply and 300 ms deferred dispatch; stale offers reject rather
than selecting a newer image. In-flight action replies also block competing HA
requests, preventing restart/installation deadlock. Reservation locks writes at
acceptance; normal charger service continues. Queued installation can be cancelled.

Device LWT moved to bq25798ups/<id>/availability; charger readiness keeps its old
topic. Charger-dependent discovery requires both online; Firmware requires device
online plus a verified manifest, independently of charger readiness. All existing
entity identifiers and state/command topics remain. Operating-settings HA
checkpoint 7 remains intentionally skipped.

All 3 target builds, actual final-byte staging and bundle assembly pass. Bytes/spare:
V1 1295120/15600; V3 1293584/17136; V4 1484944/481136. Ten native suites and 13 Python
tests pass. Public .7 feed plus all 3 assets were downloaded with only embedded CA
roots and match manifest lengths/SHA-256. Public .7 is pre-B3; do not replace it.
No device upload, real ESP TLS/flash or live HA registration was performed.
Owner test: one B3 bootstrap via existing OTA/USB, verify /firmware and Firmware
entity; .7 against stable .7 correctly has no Install. A later matching tag such as
.8 enables a real HA Install/Skip test. See
[test guide](../../software/ups/FIRMWARE_UPDATE_CONTROLS.md) and
[evidence](evidence/firmware-update-step3-20261125/RESULT.md).

## Avoid firmware metadata copies - 2026-11-25

On baseline 40d2db9, all three UPS.ino Setting locals now bind getSetting() with
const auto&: two trackChanges passes and HA register discovery. The pinned library
returns const Setting& backed by its existing settings list; global charger
lifetime covers all uses. Fields remain read-only; identifiers/telemetry unchanged.
Library toString() still copies its enum vector by value; that remains a separate
upstream optimization, with no dependency-cache edits or pin changes here.

All three generic verification builds and actual-image OTA staging/bundle assembly
pass. Final bytes/spare: V1 1285888/24832; V3 1284352/26368; V4 1472128/493952.
Savings versus immediately preceding binaries: 64/32/368 bytes respectively.
Primary benefit is avoiding temporary Setting/vector copies in frequently run
code; heap behavior has not been measured on hardware. No upload or publication.
See [evidence](evidence/firmware-metadata-copies-20261125/RESULT.md) and updated
software/ups/SIZE_OPTIMIZATION.md. Version 20261125.6 and unrelated edits preserved.

## Final-byte OTA capacity correction - 2026-11-25

**Completed locally.** Owner explicitly authorized verification builds as needed;
the earlier owner-only build preference no longer applies. All three generic
targets compile, stage against both generated OTA slots and assemble as a complete
local release bundle. Final bytes/spare: V1 1285952/24768; V3 1284384/26336;
V4 1472496/493584. No device upload or publication was performed.

The -Oz trial saved only 32 bytes and was removed. V1/V3 now use LTO with C++
exceptions disabled (-fno-exceptions; framework -fexceptions unflagged), retaining
normal -Os and return-code error handling. Compiled sources require no exception
handlers; exception-based recovery is not supported in those images. No product
feature, partition, TLS or telemetry reduction. Further measured candidates are
documented in software/ups/SIZE_OPTIMIZATION.md; no dependency-cache source edits.

Added FW/HW/MCU banner to serial immediately after Serial.begin and to syslog
immediately after attachment, before MQTT discovery; it also identifies reconnects.
Example: UPS firmware 20261125.6; HW 4.0; MCU ESP32-C3.

Local sandbox needs writable PlatformIO state: used ignored .tmp/pio-verify-core,
local tool wrappers/SDK build-script files and read-only references to installed
packages. Public Git fetch used process-local OpenSSL backend with TLS verification.
Global PlatformIO/Git configuration was not changed. Thirteen Python tests and
actionlint pass. Release staging used a synthetic zero commit marker locally;
these artifacts are verification only. CI must still run the committed source.

Historical diagnosis follows:

Run 45667258533 (e240bfc): all variants compile and V4 passes; V1/V3 staging fails
the final-byte OTA gate despite ELF program sizes 1303482 / 1302418. Downloaded
V1 CI ELF and repackaged it with installed esptool 5.3.0 (no compilation): final
image is 1328896 bytes, 18176 above its 1310720-byte slots. This is why the final
gate must remain. V3 final bytes not yet retrieved/reproduced.

The initial candidate used -Oz with LTO (-Os unflagged). Packaging errors include
exact image/capacity/excess per slot;
failure artifacts now retain firmware.bin and partitions.bin too. Thirteen Python
tests and actionlint pass. Owner subsequently authorized local builds, completed
as reported above.
Owner's version and unrelated files preserved. See
[evidence](evidence/firmware-final-size-fix-20261125/RESULT.md).

## HTTPS trust-store size correction - 2026-11-25

Run 45655231995 (fa9b7bc): V4 and all nine native suites pass; V1/V3 still exceed
1310720-byte OTA slots at 1370558 / 1369486. LTO saved about 40 KiB. Downloaded V1
diagnostic map identifies a 0x10d7b / 68987-byte SDK certificate blob. Replaced the
updater's full SDK bundle attachment with a 3678-byte embedded PEM store (including
NUL): ISRG X1/X2 and USERTrust ECC, with provenance/fingerprints documented in
software/ups/certs/README.md. Data alone shrinks by 65309 bytes; final fit remains
unmeasured until CI. No partition changes or TLS verification bypass.

Desktop TLS with only the embedded roots verifies Pages, github.com, release-assets
and objects hosts; a real release redirect returns 200. Worker behavioral suite and
13 Python tests pass; host objcopy verifies the embedded symbol; PlatformIO config
confirms all three variants embed the asset. This is not ESP32 TLS/flash or target
build validation. Existing OTA/USB can recover if GitHub later changes trust CAs.
See [evidence](evidence/firmware-tls-size-fix-20261125/RESULT.md).

## First self-hosted build failures - 2026-11-25

Run 45652188841 (3456bbf) reached ups12v-runner-1 / runner 2.337.0. V4 firmware
build passed (reported program size 1487371 / 1966080), then native settings_store
compilation failed under GCC 9 with deprecated-copy promoted to error. Explicit
default copy/move constructors and assignments added to the Arduino String test
substitute; warnings remain errors. All nine native suites pass locally (GCC 16.2);
GCC 9 confirmation remains CI-run.

V1/V3 reported program sizes 1411181 / 1409693 against 1310720-byte app slots.
Enabled -flto and removed -fno-lto for those two generic targets only. No partition,
TLS trust, image-capacity gate or runtime firmware changes. Effective PlatformIO
config confirms both flags and unchanged V4 layout; actual optimized size/target
build remains owner/CI-run and is not claimed resolved yet. Failed matrix jobs now
retain ELF/map and native logs in diagnostics artifacts if further reduction is
needed. actionlint passes. Owner's version 20261125.6 and unrelated files preserved.
See [evidence](evidence/firmware-ci-build-fix-20261125/RESULT.md).

## Self-hosted workflow validation correction - 2026-11-25

Owner reported no runs after 11100d6 / fw-20261125.5 and no published feed.
Remote branch and tag contain the updated workflow (confirmed through connector).
Found invalid runner.tool_cache context in jobs.build.env; GitHub's context table
does not permit runner there. Moved cache path evaluation to the preparation
step's env, then export PLATFORMIO_CORE_DIR through GITHUB_ENV for subsequent
steps. Earlier YAML/Bash checks did not validate Actions expression contexts.
No build/deployment log was available, so this is a confirmed workflow defect,
not an observed server-side rejection log. Branch runs still only build artifacts;
feed publication requires a new matching fw-* release tag containing the fix.
Published fw-20261125.5 was not moved and the version was not changed.
Official actionlint v1.7.7 reproduces the original context error and passes the
fixed workflow (ShellCheck/Pyflakes integrations disabled). Public API shows only
run 45643899719 on efac860; feed and .5 release URL both return HTTP 404. Owner
screenshot confirms the repository runner is registered/idle with matching labels;
no corrected workflow run was executed here. See
[validation](evidence/firmware-ci-context-fix-20261125/validation.txt).

## Firmware CI self-hosted runner - 2026-11-25

Firmware build matrix now uses [self-hosted, linux, x64] for pushes/manual runs,
matching the owner's other project workflows. PR builds remain GitHub-hosted;
lightweight checks/assembly/publication/Pages jobs remain ubuntu-24.04.
Each build creates a temporary Python venv for pinned PlatformIO and keeps a
project/variant-specific core directory under runner.tool_cache for reuse.
Requires runner access to this repository, current runner software, Bash/Git/g++,
Python setup support and writable tool cache. No target build or runner execution
was performed. Runner API lookup was unavailable because local gh config access
was denied; labels are inferred from existing owner workflows, not live inventory.
See [runner setup](../../software/ups/FIRMWARE_UPDATES.md#self-hosted-builds).

## Firmware update checkpoint B2 - 2026-11-25

Implemented the device checker/downloader on universal-firmware; B3 HA Update
entity and web controls remain pending. No install command/UI is exposed yet.
Boot/six-hour checks use verified HTTPS after asynchronous SNTP. Exact variant,
trusted versioned URL, numeric version, actual inactive-slot capacity, image
length/chip and SHA-256 gates precede boot selection. NVS/layout are preserved.
FreeRTOS worker owns HTTPS/flash; main-loop power service continues. Installation
reservation blocks settings/reset/recovery/push-OTA conflicts and waits for pending
power settings and diagnostic override readiness. No automatic installation.

Nine native production-module suites and twelve packaging tests pass. Worker SDK,
RTOS, digest and flash dependencies are simulated; no actual TLS/flash/boot/power
validation or firmware build was performed. CI runs native suites after the V4
build resolves dependencies. See [service details](../../software/ups/FIRMWARE_UPDATE_SERVICE.md)
and [evidence](evidence/firmware-update-step2-20261125/RESULT.md).
Owner's version and unrelated edits were preserved. Next is B3 using the shared
service and requestFirmwareInstall wrapper; keep operating-settings checkpoint 7
intentionally skipped. Public release/feed publication is still unverified here.

## Initial CI registration diagnosis - 2026-11-25

Owner pushed fw-20261125.3/.4, but Actions showed no workflow and the feed was 404.
Connector confirmed firmware-release.yml exists at remote tag fw-20261125.4;
remote main lacks the file and remote universal-firmware does not exist. No run
failure/log was observed, so do not claim a build or deployment failed.
Added an explicit universal-firmware branch-push build trigger and kept publishing
restricted to fw-* tag pushes. Owner must commit/push the branch to trigger a
visible CI check, then use a new matching version/tag for publication. Manual
dispatch UI needs the workflow on the default branch. Existing tags were not moved.
No computer-use/browser control was used; the owner explicitly prohibited it.
Device-update work resumed after this diagnosis; see checkpoint B2 above.

## Firmware update checkpoint 1 - 2026-11-25

On baseline `53c56d4`, implemented the first of three agreed update checkpoints:
GitHub release pipeline and manifest. Device HTTPS service and HA/web install
controls are not implemented yet. Agreed behavior: UPS checks at boot/periodically;
HA shows compatible updates and manages Install/Skip; installation is manual only.
This is separate from the intentionally skipped operating-settings HA controls.

Normal builds pin pioarduino 55.03.311 / Arduino 3.3.11 and the currently observed
direct library versions, including BQ25798 commit 00c12a2 (1.5.3). CI pins released
PlatformIO 6.2.0; local CLI is 6.2.0.post1. Owner's uncommitted FIRMWARE_VERSION edit
was preserved, not changed by the agent. Firmware builds remain owner/CI-run.

Workflow tests packaging, builds all three variants, checks final-image lengths
against generated slots, assembles matching version/commit/hash metadata, publishes
complete draft assets, then promotes a firmware-specific Pages feed. No repository
latest-release dependence; older/different same-version feed promotion is rejected.
Only tagged pushes publish. No push/release/deployment or private credential access
was performed here. Enable Pages Actions and allow fw-* deployment tags before use.

Twelve behavioral Python tests pass (synthetic ESP/partition fixtures and mocked
HTTP); YAML/job dependencies and PlatformIO config resolution checked. These are
not clean CI builds, installed-slot checks or hardware validation. See
[release guide](../../software/ups/FIRMWARE_UPDATES.md) and
[evidence](evidence/firmware-release-step1-20261125/RESULT.md).
Next checkpoint is the device checker/downloader with TLS, actual-slot/hash checks,
nonblocking power-service coordination and preserved NVS; then HA/web integration.

## Universal firmware checkpoints 7/8 - 2026-11-25

Owner intentionally skipped checkpoint 7: web configuration is sufficient, so no
new HA/MQTT configuration controls are added. Existing telemetry and diagnostic
controls remain. Owner declined further checkpoint-6 real-hardware checks; recovery
RF/OTA/power behavior is not claimed verified.

On baseline `1409d63`, normal `platformio.ini` now has exactly ups_v1_esp32,
ups_v3_sys_esp32 and ups_v4_esp32c3. One generic header supplies hardware selection
and unconfigured RuntimeSettings only. No per-device credentials, battery presets
or upload destinations. Both 2S/4S use each image. Board/flash settings are preserved.
`platformio.ota.ini` selects espota for the same three builds with an explicit port.

Eight bridge environments/adapters remain in optional platformio.migration.ini;
fleet records and rollback backups are unconfirmed, so these inputs are retained.
UPS4 has owner-confirmed bridge boot/HA identity/telemetry/controls and web Save/
Restart, but no supplied rollback/export bundle or shared-image migration result.
No other unit is claimed migrated. Credentials were not read/copied. Private future
backups have an ignored .migration-backups directory.

PlatformIO's actual config resolver confirms environment counts, matching USB/OTA
build settings and preserved board settings vs baseline, including all eight bridge
targets. The installed-partition capacity checker passes four behavioral tests.
No firmware build/upload, final binary size or physical fleet rollout is verified
here. Source consolidation and migration handover are complete; deployment remains
unperformed. See [migration checklist](../../software/ups/MIGRATION.md) and
[evidence](evidence/universal-firmware-step8-20261125/RESULT.md). Do not delete bridge
inputs until saved records/private rollback bundles are confirmed.

## Universal firmware checkpoint 6 - 2026-11-25

Implemented on baseline `46adb3e`. Owner approved immediate setup AP, manual
web/USB recovery and automatic fallback after two minutes without STA Wi-Fi/IP,
closing on recovery. WPA2 uses a random device-specific password persisted in
`ups-settings/recovery-ap`, shown on LAN/USB only; no password in syslog/MQTT/export.
Manual recovery stays on until stopped/restarted; setup AP stays until commissioned
with saved Wi-Fi and restarted. STA retries, charger service and OTA continue.
The same bounded HTTP transport works on AP at 192.168.4.1 without station Wi-Fi.

Forget Wi-Fi preserves ID/operating settings. Full settings reset stores a verified
commissioning marker, inhibits charging and clears Wi-Fi; old compiled defaults
cannot reseed the erased identity. Both retain the AP password and require exact
confirmation. Reset is explicit only; outages never erase configuration. SDK and
settings reset are not cross-store atomic; errors are reported without promising
rollback. No NVS partition erase or invented GPIO/button.

WiFiManager dependency removed. Blank setup-v1/v3/v4 targets have no device presets
or credentials; existing installed-device environments remain for checkpoint 8.
Native recovery, AP web/actions, service/power, NVS and boot/network suites pass
with simulated dependencies. Target builds, WPA2/STA coexistence, browser/OTA,
memory/latency and power checks remain owner-run. See
[guide](../../software/ups/RECOVERY.md) and
[evidence](evidence/universal-firmware-step6-20261125/RESULT.md).
Checkpoint 7 was intentionally skipped by owner; see the current entry above.

## Universal firmware checkpoint 5 - 2026-11-25

Implemented on baseline `f8960ee`. LAN HTTP configuration uses checkpoint 4's
typed service for complete validation/save and main-loop power application. The
form includes battery/charging/input/NTC settings, MQTT/syslog, one-time ID,
read-only hardware/cells, save/apply status and redacted JSON export/import.
Owner selected LAN access plus a request token; no password login or HTTPS.
Per-boot token, origin/host checks and stale-settings rejection protect submissions.

Installed core WebServer parsing can wait seconds on incomplete requests. The LAN
transport instead accepts one bounded request, uses one nonblocking socket transfer
per loop and closes clients after five seconds. No new task or MQTT-client sharing.
Service network settings remain immutable until explicit restart after the reply.
Wi-Fi changes are separately staged in `ups-settings/wifi-pending`, verified into
SDK storage at restart, then cleared. Wrong credentials still require USB recovery;
AP/recovery design remains checkpoint 6. Passwords are never returned or logged.

Native web/HTTP/Wi-Fi, service/power, storage and boot/network regression tests pass
with simulated dependencies and real ArduinoJson. Owner began browser testing;
Save/Restart were rejected with `Origin: null` because of `no-referrer`. Response
policy is corrected to `same-origin` while retaining token/origin checks; owner
confirmed Save/Restart now work. Remaining browser cases and hardware checks are
pending; firmware builds/uploads remain owner-run.
See [LAN guide](../../software/ups/WEB_CONFIGURATION.md) and
[evidence](evidence/universal-firmware-step5-20261125/RESULT.md).
Checkpoint 6 followed this checkpoint; see the current entry above.

Owner also confirmed checkpoint 4 UPS4 target build, OTA/boot, Wi-Fi, syslog, MQTT,
preserved HA identity, fresh telemetry and existing controls. These are owner
observations, not agent-run live tests or validation of all power transitions.

## Universal firmware checkpoint 4 - 2026-11-25

Implemented on baseline `981d1fc`: one typed Settings::Service validates and saves
a full candidate before scheduling main-loop application. Failed saves preserve
RAM configuration/status; desired revision, applied revision, power state and
network-restart status are separate. Active network strings remain untouched.
The provisioned ID stays immutable; web/HA configuration endpoints are later work.

Power transactions use existing current/profile helpers with fresh register
readback, including marker-skipped input/output values. No per-edit IC reset or
OTG/backup/HiZ mode change. Unsafe/unavailable input defers application; failures
retain desired settings for retry and revoke ARM. Zero current inhibits charging;
LEGACY retains VREG. Diagnostic inhibition and topology restrictions apply.
External input limiting reports its effective readback rather than requested current.

Native service/power and prior persistence/startup regression tests pass with
simulated dependencies. Builds, uploads, real NVS/RTOS/network and electrical
validation remain owner-run. See [service guide](../../software/ups/SETTINGS_SERVICE.md)
and [evidence](evidence/universal-firmware-step4-20261125/RESULT.md).
Checkpoint 5 followed this checkpoint; see the current entry above.

## Universal firmware checkpoint 3 - 2026-11-25

Checkpoint 3 is implemented on baseline `5086657`. Saved settings now activate
before session identity, clients and charger startup. Only missing storage may
be seeded from a valid adapter. Invalid/unsupported/incompatible records remain
untouched; normal charger initialization and MQTT stay disabled. V4 ARM stays LOW;
legacy EN_CHG-off/readback is best effort, with I2C failures reported.

Identity is fixed per session and supplies Wi-Fi/OTA hostnames and MQTT identity.
The HA serializer preserves existing topics, unique IDs and default entity IDs.
New IDs are lowercase hostname labels up to 31 characters, matching the installed
core's hostname buffer; valid stored case is preserved. All eight existing IDs fit.

Charger service starts before Wi-Fi. DNS/MQTT handshakes use one 4096-byte FreeRTOS
worker with exclusive queued client handoff; all main-loop publishers are gated
during attempts. The worker namespace is UpsNetwork to avoid Arduino's global
Network object. Ordinary publishing/callback/OTA library waits are not eliminated.

Wi-Fi uses SDK-saved credentials without the blocking WiFiManager portal or reboot
loop. Unconfigured units offer USB and, with saved Wi-Fi, OTA as ups-setup plus
their MAC. New LAN/AP forms remain checkpoints 5/6; fresh units need the existing
USB/bridge provisioning route until then. The dependency remains for later cleanup.

Boot/discovery/worker native tests and persistence regression tests pass with
simulated platform services and real ArduinoJson. Firmware builds, real NVS,
RTOS/heap/stack, network recovery and power behavior remain owner checks. See
[startup guide](../../software/ups/STARTUP.md) and
[evidence](evidence/universal-firmware-step3-20261125/RESULT.md).
Checkpoint 4 followed this checkpoint; see the current entry above.

## Universal firmware checkpoint 2 - 2026-11-25

Owner-authorized checkpoint 2 is implemented on the checkpoint 1 baseline
`e542e03`. [`settings_store.h`](../../software/ups/include/settings_store.h) and
its codec/store/NVS modules provide schema 1, all 33 runtime fields, exact hardware
compatibility metadata, guarded save, and credential-free export/import. The
private record includes MQTT credentials; Wi-Fi stays owned by the SDK/WiFiManager.
No local credentials were read/copied into tests or evidence.

The bridge seeds `ups-settings/config` only when the namespace/key is absent,
commits one complete blob and verifies readback. Existing, damaged, oversized,
unsupported-schema, incompatible-hardware and conflicting-identity records are
preserved. Storage errors never trigger erase or default replacement. Native NVS
APIs are used to distinguish missing namespaces from read errors. Save errors may
leave an old or complete new record; no rollback is claimed.

Startup only logs the seed result after Serial, with V4 ARM already LOW. The
application still uses compiled settings; global HA identity, network startup,
charger behavior, CELL handling and telemetry remain unchanged. Loading saved
settings is checkpoint 3, not part of this change.

Five native behavioral test groups pass with real ArduinoJson 7.4.3 and simulated
String/BQ/NVS platform dependencies, compiling production modules with C++11 and
`-Wall -Wextra -Werror` on Windows MSYS2 g++. This is not firmware or physical flash
validation. Firmware builds, binary/heap checks, upload and real NVS persistence
remain owner-run. WSL execution was denied; the native compiler path worked.
See the [migration/schema/test guide](../../software/ups/PERSISTENT_SETTINGS.md)
and [evidence](evidence/universal-firmware-step2-20261125/RESULT.md).

Checkpoint 3 is next after review. It must load saved settings before assigning
identity and network clients and preserve unsupported records. Later checkpoints
remain unstarted. The owner staged files during implementation; staging was left
untouched, so review both staged and unstaged changes before committing.

## Universal firmware checkpoint 1 - 2026-11-25

Owner-authorized checkpoint 1 is implemented on `universal-firmware`, based on
`0119bcb`. [`hardware_profile.h`](../../software/ups/include/hardware_profile.h)
defines three immutable hardware selections: ESP32 V1/PMID, ESP32 V3.3b/SYS and
ESP32-C3 V4/SYS. Version selects MCU/topology together; pins are explicit and
the TS divider is common. `RuntimeSettings` owns mutable settings and text using
Arduino String. `Config` remains a compatibility alias for local shared settings.

All nine adapters select hardware independently and keep their runtime values.
All eight installed identifiers, battery cell/pack values, presets and power
limits are preserved by source review. Consumers use immutable pins/topology;
charger algorithms, CELL handling, startup order and MQTT serializer are unchanged.
Generic MQTT credential defaults are empty; installed credentials remain local.
Only the redundant pin assignments were removed from the ignored shared config;
all its other content, including credentials, was verified unchanged.

The [configuration inventory](../../software/ups/CONFIGURATION.md) records every
field, per-device effective source values and external-profile migration.
Focused diff, reference and whitespace checks pass. No builds, compiled tests,
uploads, MQTT/HA operations or power tests ran. Owner builds/live checks, binary
size and heap effects of owned strings remain pending. Evidence:
[`universal-firmware-step1-20261125`](evidence/universal-firmware-step1-20261125/RESULT.md).

The [stepwise plan](../../software/ups/UNIVERSAL_FIRMWARE_PLAN.md) records checkpoint
1 implementation and next checkpoint 2 (persistent settings and migration bridge),
after review. Later startup, web/recovery, HA controls and build consolidation
have not started. Do not continue into them without the owner's next instruction.

## Battery cell/pack configuration split - 2026-11-25

`cfg.battery.cell` now owns the cell name, 20%/80% per-cell voltage presets and
the average-cell diagnostic override limits. `cfg.battery.pack` owns nominal
pack capacity and the pack charge-current ceiling. All nine board profiles,
runtime references and README examples are migrated; configured values and
charge-control behavior are preserved. Custom external board profiles need
the same field-path migration.

Custom battery sensor display names identify cell or pack values; existing
MQTT keys/topics, unique IDs and default entity IDs are preserved. Added
**Battery cell 80% voltage**, reporting the configured per-cell APPROX_80 target
in mV (state key `battery_cell_approx80_percent_capacity`), independently of
charger readiness and active charge profile. Like the 20% diagnostic it is
retained and change-only, republishes after discovery/reconnect and retries
failed sends. Unspecified/nonpositive values publish `unknown`. It is a
configured charging target, not an under-load threshold or measured SOC.

Focused diff/reference review and whitespace checks pass. No builds or compiled
tests were run under the existing owner-run build boundary. Firmware builds,
upload and live MQTT/HA validation remain pending with the owner.

## Battery almost-depleted warning - 2026-11-25

Added `battery.approx20PercentCapacityUnderMaxLoad_mV` (per-cell mV, default 0:
unspecified), a read-only MQTT threshold sensor, and the HA binary sensor
**Battery almost depleted**. The warning compares average cell voltage against
the threshold every 5 seconds while charger-ready, ON at or below it and OFF
above it. There is no hysteresis or load-current gate. Invalid battery/ADC samples
or an unspecified threshold yield unknown; charger availability is preserved.
Both entities use retained, change-only state publication and the existing
retry/discovery/reconnect behavior. See the firmware README for MQTT topics.

Owner supplied the UPS8 Liitokala/NCR18650B preset: 3955 mV/cell APPROX_80 target
and 3300 mV/cell almost-depleted warning. UPS4-7 now use the same voltage preset;
UPS8's owner edits are preserved. GeB UPS1-3 retain their existing 3920 mV target
and unspecified warning threshold: the GeB revision A datasheet has no discharge
curve to derive a 20% threshold. The paper's 3955 mV is rested OCV at 80%, not
validation of a CC/CV target at exactly that SOC; 3300 mV is an owner preset.
Sources, revisions and limitations:
[`battery-voltage-presets-20261125`](evidence/battery-voltage-presets-20261125/RESULT.md).
Focused diff/whitespace checks pass. Firmware builds, upload and live MQTT/HA
validation remain pending with the owner.

## Predictable Home Assistant entity defaults - 2026-11-18

Owner-approved firmware discovery now supplies `default_entity_id` from the
component and normalized configured device identifier/config key. For example,
UPS5 VBAT becomes `sensor.esp77_bq25798_ups5_vbat_adc`; AC1 presence keeps distinct
binary, numeric and `_enum` IDs. Existing unique IDs, MQTT topics and display
names are unchanged. HA applies these defaults on first registration; existing
registry entries retain their IDs. See the firmware README for the naming rule.

A scoped read-only broker capture obtained 134 retained UPS5 discovery configs.
Projected defaults have zero collisions and require at most 1,007 of the current
2,048 MQTT buffer bytes. This is a projection using existing broker payloads,
not execution of the modified serializer or evidence that the device is online.
No firmware build/upload or HA registry changes were performed. Owner build and
live discovery validation remain pending. Evidence:
[`ha-default-entity-id-20261118`](evidence/ha-default-entity-id-20261118/RESULT.md).

## Project-local footprint libraries consolidated — 2026-11-16

All seven current project-local footprints now live in
`ups_v4/ups_v4.pretty/`. Both `ups_v4` and `easyeda2kicad` library nicknames
resolve there through the project table, updated by Konnect. The two external
footprints were relocated byte-for-byte; the obsolete sibling library containing
only an older ESP32 footprint without its 3D model was removed. Keep the current
ESP32 model and existing imported-model environment references.

PCB, schematic, project settings, symbols, all seven retained footprint contents
and the project-local 3D model have unchanged hashes. Scratch-copy tools now
discover source `*.pretty` directories; copying current one-library and historical
two-library projects passed focused behavioral checks. ERC/DRC/parity finding
sets are exactly unchanged: no errors, 412 ERC warnings, 148 DRC warnings,
55 parity warnings and zero unconnected items. These include existing library
lookup limitations; this is preservation evidence, not a clean release check.
See [project layout](ups_v4/README.md) and
[consolidation result](evidence/library-consolidation-20261116/RESULT.md).

## Temporary evidence cleanup — 2026-11-16

Owner-authorized working-directory cleanup removed 629 temporary outputs,
duplicated captures, old automatic backups and Python cache files. Kept six
newest KiCad backup archives, all test inputs, tool dependencies, engineering
records and production CAD/libraries. All 3,015 protected files passed exact
hash preservation before the documentation notes were updated. No CAD or
firmware changes, tests, builds or new electrical checks were performed.

The latest [saved connectivity result](evidence/compare-2940936-20261116/RESULT.md)
retains compact pad-topology proof, hashes, ERC/DRC reports and a current design
snapshot. [Evidence index](evidence/README.md) records retention boundaries;
historical tool/test fixtures remain intentional inputs. The inaccessible old
comparison subtree was not touched.

## Reliable current path and completed passive hardware sweep - 2026-11-15

The owner reported another default-mode 0x12 timeout in
`tools/bench-efficiency/results/rk6006-atorch-20261115-201612-059506/` after
17 completed points. Across this and the 195614 run, 514 voltage requests had
no logged errors; 2 of 514 current requests timed out. Both missing responses
were followed by checksum-valid reports while source OFF was verified in cleanup.
These counts describe only those runs and do not establish a universal failure
probability or the physical reason for the missing replies.

The owner's subsequent `--load-readout reports` run
`results/rk6006-atorch-20261115-202220-867781/` completed all 40 points in 674.3 s,
with no recorded communication errors. The default `queries` mode has now been
repaired to use fresh checksummed report current (still 0.001 A) and query only
precise voltage (still 0.001 V). This removes the observed failing 0x12 path
without reducing voltage resolution. Source reads follow load arrival in both
modes, and paired timing/skew is logged. No untagged query retries were added.
Pure report mode remains optional with its explicitly marked 0.1 V steps.

All 64 offline tests pass, including a full default sweep with an injected
unused bad-current-query value and a sub-decivolt voltage-resolution check.
The modified default still requires its own hardware run; the owner was told
to run the normal command again. Do not present the passive success as live
validation of the new default. No COM port or instrument command was used by
the agent. Evidence: `evidence/auto-bench-efficiency-current-path-20261115/`.

## ATORCH query timeout and optional passive readout - 2026-11-15

Owner run `tools/bench-efficiency/results/rk6006-atorch-20261115-195614-434126/`
completed four points and stopped at 5 V / 0.75 A. Current query 0x12 received
no PX100 reply within one second, while a checksum-valid unsolicited report
arrived during the wait with 749 mA. RK6006 last read was also 749 mA and source
OFF was verified during cleanup. ATORCH emergency OFF was sent, with state
verification deliberately unavailable after lost synchronization; the warning
is accurate. Source settings restoration was verified. This differs from the
previous RK6006 read timeout, whose bounded retry fix was already active.

The run's `ANALYSIS.md` records timings/raw packet. Owner selected optional
passive readout while retaining precise queries as default. `--load-readout reports`
uses fresh checksum-valid reports (0.1 V load voltage, 0.001 A current), with
source reading close to arrival. Queued reports are discarded; partial frames
are completed/discarded before a new frame. A 3 s report deadline stops the run,
leaving no outstanding measurement query, so normal verified OFF is attempted.
Setup/state control remains PX100 and can fail. HTML/console identify the mode;
CSV adds `load_voltage_resolution_v`. All 63 tests pass, including the captured
749 mA packet and a full passive sweep. No live instrument access used.
Evidence: `evidence/auto-bench-efficiency-passive-20261115/`.

## Extraction completed; Auto Bench Efficiency and RK read recovery - 2026-11-15

Owner completed the extraction and named the public repository
https://github.com/misch2/auto-bench-efficiency. Independent local checkout is
`C:/Users/Michal/Git/my/auto-bench-efficiency`; UPS12V retains its submodule at
`hardware/v4/tools/bench-efficiency` (commit 507dacb initially). The owner changed
the submodule URL to GitHub with `git submodule set-url`; `.gitmodules` and the
initialized submodule origin were verified as the new HTTPS URL. Legacy tool
files/library are staged for removal. Do not rerun the extraction helper.

The queued trace `evidence/rk6006-atorch-20261115-191300-241323/` was reviewed:
26 completed points, then MinimalModbus NoResponseError on an RK6006 read during
15 V / 0.25 A. ATORCH had last returned 248 mA; no ATORCH request error occurred.
Cleanup immediately communicated with both instruments and verified OFF and all
source setting restoration. This was a read-timeout event, not the earlier
incoming ATORCH numeric-outlier issue.

The submodule working tree now uses the pinned RK6006 library's bounded read-only
helper (three attempts for missing/invalid replies), with explicit request/error
and duration logging. Writes remain single-shot; exhausted reads still stop and
clean up. The README uses the new project name and concrete GitHub clone command.
Tests import the complete pinned library with a simulated Modbus boundary; no
source-text assertions or function extraction are used. All 54 tests pass.
Changes were made in the UPS12V submodule checkout; the owner was concurrently
committing them (dea63b1 observed). The agent did not commit/push or edit the
separate sibling checkout. Evidence: `evidence/auto-bench-efficiency-rk-read-20261115/`.

## Bench Efficiency extraction prepared - 2026-11-15

Independent local repository prepared at `tools/bench-efficiency/`, commit
`507dacb0bea284231b0578d8ee7c3d9690be2fd4`. It contains the tool, its tests,
requirements, inherited MIT license, practical English user README and the
pinned RK6006 interface as a nested submodule. Default results are now local
to that project's `results/`; historical evidence stays here. All 49 offline
behavioral tests pass. No remote repository was requested or created.

Parent registration is pending the owner running
`evidence/bench-efficiency-extraction-20261115/Finish-Extraction.ps1` from a
normal PowerShell session: this agent's writable boundary excludes the parent
`.git` and `.gitmodules`. The helper validates reviewed file hashes/commits,
backs up legacy files/library, moves the independent repository to sibling
`C:/Users/Michal/Git/my/bench-efficiency`, adds its local-path submodule here,
initializes the nested dependency and stages only the migration's Git paths.
It does not commit the parent. Existing measurement evidence is preserved.
The helper passed an isolated Git integration test, including preservation of
an untracked library file and unrelated parent staged changes.

After actual registration, review the owner's queued communication failure
at `evidence/rk6006-atorch-20261115-191300-241323/debug.jsonl` (15 V / 0.25 A).
The owner explicitly requested that review after the extraction.

## Sweep progress and ETA - 2026-11-15

Console output now shows completed/total points, remaining points, elapsed
sweep time and estimated remaining duration at point start, completion and
retry. Initial ETA uses measurement + minimum settle + 2 s allowance per point;
after a completed point it uses actual sweep throughput, including rejected
attempt time. Retries do not count as completed points. Debug point events
include grid index/total and completed sweep duration. The owner-expanded
default current list (0.1/0.2/0.25/0.5/0.75/1/1.5/2 A) is preserved, giving
40 default points. The full behavioral suite passes 48 tests, including
whole-point retry and progress/ETA. No live instrument access was used.
Evidence: `evidence/efficiency-point-retry-20261115/`.

## Whole-point retry for isolated reading deviations - 2026-11-15

Full owner run `evidence/rk6006-atorch-20261115-185551-639599/` completed 23
points, then rejected 20 V / 1 A. The raw PX100 reply to query 0x12 was
`ca cb 00 03 28 ce cf`, i.e. 808 mA; the Python decoder is correct for those
bytes. Previous load readings were 998/1003 mA, while RK6006 reported
999/1000 mA. No logged timeout, malformed frame or protection trip occurred.
The source of the incoming outlier remains unconfirmed; the reads are
sequential and PX100 has no payload checksum. See that run's `ANALYSIS.md`.

The tool now retries a rejected operating-point window once by default:
verified OFF, repeat setting/settling, fresh full measurement window. No bad
sample is silently dropped or spliced over. `--point-retries 0` disables the
retry; persistent deviations and all communication/protection/OFF errors
still stop the run. CSV/HTML include `attempts`; debug retains every rejection.
Offline tests cover the 998/1003/808 mA sequence, clean retry energy accounting,
progression to the next point, retry bounds and failure to verify OFF. No live
instrument control was used. Evidence: `evidence/efficiency-point-retry-20261115/`.

## First owner debug trace reviewed - 2026-11-15

Run `evidence/rk6006-atorch-20261115-185331-863896/` completed 5 V / 0.1 A
with the ZT-703S explicitly disconnected. Nineteen measurement pairs show
ATORCH 97-103 mA and RK6006 96-98 mA; no 187 mA anomaly or logged communication
error occurred. Final OFF and settings restoration were verified in the trace.
The reported voltage difference is now about 153.5 mV (RK6006 4.9894 V versus
ATORCH 4.8359 V), versus about 5.1 mV in the earlier successful owner run.
The 99.7241% ratio combines lower reported load voltage with higher reported
load current; it does not establish accuracy. A DMM check of voltage at both
sets of terminals is the next useful distinction between real interconnect/
sense drop and voltage readout disagreement. The intermittent spike remains
unexplained. Details: the run's `ANALYSIS.md`. Saved-file analysis only.

## Diagnostic raw trace - 2026-11-15

An owner run settled near 0.1 A then rejected a 0.187 A load reading; the next
run completed that point at 102.4147%. Its saved CSV has RK6006 97.5787 mA versus
ATORCH 100.0373 mA with nearly equal voltages. This establishes instrument
disagreement, not its cause; raw traffic/samples were absent from those runs.
No tolerance was relaxed and no anomalous sample is silently discarded.

Measurement runs now create `debug.jsonl` beside CSV/HTML before initialization,
with flushed UTC/elapsed events: raw RK6006 registers, ATORCH TX/RX and parsed
frames/query values, all paired readings before validation, phases, errors,
shutdown/restoration and session outcome. PX100 framing-only validation is
explicitly distinguished from ATORCH report checksum validation. Errors also
show the paired RK6006/ATORCH readings in the console. A debug write failure
does not block OFF. `--probe` creates no debug folder and sends no control.
The intermittent spike's source remains unconfirmed pending a real trace;
offline tests cover a 187 mA reply and preservation of the rejected sample,
initialization failure, invalid checksum and a simulated full disk.
Evidence: `evidence/efficiency-debug-20261115/`. No live instrument access used.

## Diagnostic instrument settling - 2026-11-15

The owner observed ATORCH reading 0.086 A for the 0.1 A point after the former
fixed 2 s wait. This alone does not establish whether load regulation or its
measurement/reporting had settled. Before each energy window, the tool now
waits at least `--settle` (default 2 s), then requires three consecutive pairs
in operating-point tolerance, spaced at least 0.5 s apart. Total wait is bounded
by `--settle-timeout` (default 15 s, including the minimum wait). Only readable
out-of-tolerance operating points are retried; source protection and serial
errors remain fatal. Settling samples are excluded from the 10 s energy window;
measurement tolerances remain enforced during that window. Simulated delayed
readings, count reset, timeout, temporary CC and fatal errors are covered by
the offline tests. No live instrument commands were sent.

## RK6006 / ATORCH diagnostic tool fixes - 2026-11-15

`tools/measure_efficiency.py` now verifies temporary RK6006 OVP/OCP and CC
limits (full default sweep: 22 V, 2.31 A and 2.1 A), rejects samples outside
the configured source-voltage/load-current tolerances or outside source CV
mode, and rejects stale/partial PX100 replies. ATORCH timeouts stop the run
without retry; after lost synchronization only an unverified emergency OFF
is attempted. Initialization failures shut down identified instruments before
port closure. Original source voltage/current/OVP/OCP are restored only after
verified source OFF; outputs stay off. `--probe` remains read-only.

The restored `RK6006-Python-Module` submodule remains the source interface;
`tools/requirements.txt` lists `pyserial` and `minimalmodbus`. Usage and
diagnostic tolerances are in `tools/README.md`. Behavioral verification uses
simulated registers, serial traffic and time; no physical COM ports or output
controls were used. Evidence: `evidence/efficiency-tool-fixes-20261115/`.
Matching-instrument validation remains pending.

## Source-code test cleanup - 2026-11-13

Removed the three Python source-check scripts, their dependent input-detection
and telemetry C++ fixtures, and their usage references at the owner's request.
Standalone charge-profile and current-limit behavioral tests remain. AGENTS.md
now prohibits source-text assertions and function-extraction test harnesses.
Historical evidence is retained. No firmware behavior changed; no target build
or hardware validation was performed for this cleanup.

## Priority 3D models - 2026-11-13

Added the KiCad JST XH STEP models to J4/J6 and the official Espressif
ESP32-C3-MINI-1 STEP to U1 on the board and in the project footprint library.
The U1 model uses project-relative storage and a local offset of
(-6.6, -5.5, 0) mm. The rendered antenna extends over the board edge in the
existing RF keepout direction. Source: [Espressif module downloads](https://www.espressif.com/en/products/modules/esp32-c3-series).

KiCad 10 rendered all three models from the saved board. DRC reported 0 errors,
0 unconnected items, 0 schematic parity differences and 18 library mismatch
warnings, the same count as before the edit. Saved schematic ERC reported
0 errors and 4 warnings. The J4/J6 IPC model update dropped their PCB-side
single-unit metadata; the saved diff has no changes to pads, nets, placement or
routing. Reports and preview: `evidence/priority-3d-models-20261113/`.
J1/J2/J3/J8 and L1 remain open; the models referenced by those footprints are
absent from the installed library.

## Temporary power-test controls and battery capacity - 2026-11-12

Added acknowledged HA/MQTT switches `charge_inhibit` (EN_CHG=0, V4
CHARGE_ARM LOW) and `force_battery_supply` (EN_HIZ=1, also inhibits charge).
HiZ test is available only with VSYS_UNINTERRUPTED, including UPS4/5; PMID/OTG
backup is unchanged. Independent requests coexist and survive MQTT reconnect,
but are RAM-only and do not survive ESP32 restart. SYS initialization explicitly
clears retained HiZ and restarts ADC on the first connection after boot, even
with VAC2_ADC_DIS already set; this also retries a pre-existing HiZ condition.
Runtime tests do not adopt an existing protection HiZ.

Both requests require valid continuous VBAT measurement and average cell voltage
>=3700 mV to start; both cancel at <=3600 mV, invalid measurements or I2C loss.
Defaults are `battery.overrideLimits.{startCell_mV,stopCell_mV}`. Cancellation
does not auto-restart tests after voltage recovery. This is pack-average test
guarding, not individual-cell/BMS protection. HiZ re-enables/verifies ADC, input
detection pauses during test/cleanup, and owned HiZ exit retries after I2C
recovery. Charge profiles, battery current ceilings, marker/reset paths and V4
charge-arm readback respect inhibition. Legacy charge control resumes on its
normal 30-second check. Ending a test without input cannot stop normal discharge.

Split brand/name and nominal pack capacity: `battery.name = "Liitokala"`,
`battery.capacity_mAh = 3400` in UPS4 and local UPS5; local GeB UPS1-3 use
`"GeB"` / 3200. Existing current/profile values are preserved, including current
owner-local edits. `battery_capacity` is a retained diagnostic mAh sensor,
published initially and after discovery/reconnect, retrying failed sends without
a periodic refresh. Zero means unknown. Capacity does not affect charge limits.

Native charge-profile/current-limit tests passed. Actual override/startup code
compiled against installed BQ25798Core API; six board profiles passed Config/metadata smoke checks using
dummy transport and a credential-free secret fixture. No firmware target build,
upload, live MQTT command/register write or hardware validation was performed;
owner target builds and matching-hardware tests remain pending. Details:
`evidence/firmware-power-overrides-20261112/VALIDATION.md` and firmware README.

## CHARGE_ARM GPIO startup fix - 2026-11-12

`setupChargeArm()` now preloads LOW through native `gpio_set_level()` before
`pinMode(OUTPUT)`. The ESP32 Arduino core rejected the former early
`digitalWrite()`, producing the GPIO0 boot error and skipping the latch preload.
Subsequent arm/disarm writes and charger setup sequencing are unchanged.

Firmware builds, upload and hardware confirmation remain owner checks;
no live device changes made.

## Production Grafana series preserved - 2026-11-11

Owner supplied 25 Grafana series: 18 register-backed, four calculated firmware
sensors and three owner-confirmed Grafana templates/older definitions
(`esp_internal_chip_temperature`, `internal_chip_temperature`, `ts_zone_numeric`).
Added DIS_ACDRV and EN_ACDRV1 to production periodic telemetry; moved TS_ADC and
VINDPM_STAT from change-only to periodic. All 22 firmware-backed series remain
available without DEBUG_BQ25798_SETTINGS, with fixed 60-second refresh.
Production now selects 74 registers: 20 periodic, 54 change-only.

Static checks passed for library-name validity, uniqueness, coverage of all 18
Grafana registers and four calculated periodic sensors, plus Python test syntax.
No builds or compiled tests were run, per owner instruction;
target/live checks remain pending.

## Optional full-register MQTT debug flag - 2026-11-11

`-DDEBUG_BQ25798_SETTINGS` enables all library settings. Registers outside the
production allowlist publish initially/reconnect and on change only; core
60-second refresh remains unchanged. Read-cleared interrupt flags are sampled
ON/OFF values, not guaranteed event history. Production discovery also deletes
flag entities when switching back from debug. Charger control is unchanged.
README shows a flag-preserving optional UPS4 debug environment example.

No builds or compiled tests were run for this follow-up, per owner instruction;
static checks only.
Target compilation and live debug/production discovery migration remain pending.

## MQTT telemetry selection and publication - 2026-11-11

`software/ups/include/telemetry_policy.h` selects 72 of the installed library's
230 registers: 16 core measurement/state registers have a fixed 60-second
refresh; 56 useful configuration/limiting/fault registers publish on change.
Calculated battery temperature/percent, PBAT/PBUS and uptime also refresh at
60 seconds. Other custom diagnostics publish on change. MPPT/VOC, interrupt
flags/masks and other excluded registers have no discovery/state traffic;
discovery removes their old retained HA configs. Existing selected IDs/topics
and auxiliary enum views are preserved. No time jitter (owner correction).

State delivery compares with the last successful payload, retries failures and
resends after discovery/reconnect/recovery. State payloads are retained for HA
restart. Only periodically refreshed entities have force_update and 300-second
expiry; change-only values do not expire. Battery percent uses whole-percent
payloads and suggested_display_precision=0. Charger control/polling is unchanged.

All allowlist names matched the installed library at this checkpoint.
The ups1-4 target build command stopped before compilation on sandbox-denied
global `platforms.lock`; target builds and live MQTT/HA validation remain pending.
No upload, live MQTT publish or register write was performed.

## Battery-specific reduced charge voltage moved - 2026-11-10

Moved `power.charger.chargeProfile.approx80Cell_mV` to
`battery.approx80PercentCapacity_mV`. This remains a per-cell voltage; zero is
rejected for APPROX_80. Runtime application, startup/readback validation, README
and all four configured UPS board profiles use the new field; their 3920 mV
values are preserved. Profile mode, full voltage and recharge offset stay in
the charger profile. Native charge-profile tests passed, plus actual Config
compile/runtime checks for all five board profiles. Target build attempt stopped
before compilation on sandbox-denied
global `platforms.lock`; affected target builds remain pending. Logs:
`software/ups/.pio/approx80-config-{host,boards,build}.log`.
No upload or live hardware validation.

## Battery type MQTT sensor added - 2026-11-10

Read-only diagnostic sensor `battery_type` / "Battery type" reports
`config.battery.name`. Its value is forced after discovery/reconnect and
refreshed every 60 seconds independently of charger availability. No units,
device class or state class. Focused source/diff checks passed; target build
attempt stopped before compilation on sandbox-denied `platforms.lock`.
Log: `software/ups/.pio/battery-type-build.log`. No upload/live MQTT writes.

## Battery identity and current ceiling implemented - 2026-11-10

`Config::battery` owns `name` and `maxChargeCurrent_mA`. Every firmware ICHG
write now uses the lower of requested ICHG, battery maximum and the IC's 5000 mA
maximum, rounded down to 10 mA. Independent IPRECHG is reduced if necessary,
rounded down to 40 mA. Missing/invalid limits inhibit charging; battery limits
below the fixed 100 mA trickle current and requested ICHG below 50 mA are
rejected. Saved-marker initialization, forced/reset setup, legacy/managed
enabling and runtime recovery all enforce the ceiling. Changed registers are
freshly verified; errors disable EN_CHG as a best effort and revoke V4 CHARGE_ARM.
This limits programmed settings; analog tolerance and autonomous charger-only
resets while the MCU is not in control remain outside the software guarantee.

Owner specified UPS1-3 GeB 3200 mAh / 3000 mA; requested ICHG remains
500/500/1000 mA. Owner concurrently changed UPS4's maximum to 700 mA for
Liitokala 3400 mAh; preserved, with requested ICHG still 500 mA. Cell limits
were not independently qualified. Native current-limit and charge-profile
tests passed. Actual Config and installed BQ25798Core API compile checks passed;
all five saved board profiles compiled and passed identity/current checks.
Target build attempt stopped before compilation on sandbox-denied global
`platforms.lock`. No upload, live register write or hardware validation.
Evidence: `evidence/battery-current-limit-20261110/`.

## Firmware hardware-version enum - 2026-11-10

`Config::hardwareVersion` now uses `Config::HardwareVersion` (`V1_0`,
`V3_3B_SYS_MOD`, `V4_0`). `hardwareVersionName()` preserves the existing
log/Home Assistant strings. All five board profiles, including ignored local
UPS1-3 profiles, were migrated. Native MSVC compile/runtime checks passed for
all five profiles using the actual Config and installed BQ25798Core headers
with a dummy transport. Target build attempt stopped before compilation on
sandbox-denied global `platforms.lock`; target builds remain pending. Logs:
`software/ups/.pio/hardware-version-check/check.log` and
`software/ups/.pio/hardware-version-build.log`. No hardware upload performed.

## V4 delayed input classification retry implemented - 2026-11-10

Owner approved FORCE_INDET after PD-trigger settling, including after each input
return. Only V4 enables `power.input.retryUnqualifiedAdapter` (default false).
The nonblocking helper waits 60 seconds of VAC1 presence, then starts detection
only for VBUS_STAT=8, Power Good, outside OTG/backup, with no detection in progress.
Attempts are separated by at least 60 seconds; source loss, charger unavailability
or explicit reconfiguration restart the settling wait. A different classification
stops new attempts. FORCE_INDET and DPDM_STAT must both become idle before the
configured positive IINDPM is reapplied, freshly read and logged. EN_EXTILIM
remains unchanged; a hardware-clamped readback below the request is logged.
Pending IINDPM restoration survives a source interruption or I2C recovery.
VAC2_ADC_DIS and the one-time initialization body are unchanged. No additional
charge-enable, CE, HIZ, VINDPM, ICO or USB-PD controls were added.

Existing charge-profile tests passed. The runtime function compiled against
installed BQ25798Core and Config using a dummy transport. PlatformIO ups1-4 build attempts,
including after the owner stopped a concurrent build, still fail before compilation
on sandbox PermissionError for the global `platforms.lock`. Target builds and
hardware behavior of forced detection remain pending. No firmware upload or live
register/MQTT command was performed. Existing owner version/staging edits retained.
Evidence: `evidence/input-detection-retry-20261110/`.

**Owner runtime confirmation:** owner subsequently built/uploaded UPS4 and supplied
syslog: Ready 17:42:57.259, FORCE_INDET start 17:43:57.297, finished
17:43:57.843 with VBUS_STAT=5 and detected/configured/readback IINDPM=3000 mA.
The read-only MQTT recorder independently confirmed state 5, IINDPM=3000 mA,
ICHG=500 mA, watchdog Disabled, EN_CHG=ON, CC charging and IBAT=506 mA.
First-start behavior is confirmed; actual source-loss/return hardware validation
and the original cause of code 8 remain open. Owner success confirms their UPS4
build, not new local/all-target builds. See OWNER_RUNTIME.md and
post-upload-mqtt.json in the evidence directory.

Owner later connected a phone charger to the UPS output, explaining increased
draw. The earlier idle-output description no longer applies after that load
change; exact connection time and load power were not recorded. See the load
note in OWNER_RUNTIME.md when interpreting the continuing MQTT trace.

## V4 charge-arm uploaded by owner, live charging observed - 2026-11-10

Owner reported firmware upload and confirmed the previous 4S/20 V PD-trigger,
idle SYS PD module and MF52 B3950 setup. Read-only MQTT capture started
17:21:02 Prague for 30 minutes, PID 55808; scheduled end 17:51:02.
`tools/capture_mqtt.py` runs independently between turns, without publishing
application messages or providing automatic alerts. At 89 seconds it had 562
non-retained messages across all 286 state topics. Two register refreshes showed
ICHG=500 mA, watchdog Disabled, EN_CHG=ON, CHG_STAT=Fast Charge (CC), CELL=4S,
VREG=15680 mV, IBAT=505/504 mA, VBAT=14.211/14.352 V and VBUS=19.829/19.838 V.
TDIE=25/27 degC; calculated battery temperature=23.8 degC. No asserted sampled
fault/TS statuses observed. VBUS_STAT=8 (`Not qualified adaptor`) is recorded
as an unresolved classification alongside Power Good and measured charging.
GPIO0/CE_N waveforms and full charge-cycle validation remain unverified.
Evidence and current logger status: `evidence/mqtt-ups4-charge-arm-20261110-172102/`.
See ASSESSMENT.md; a STOP file there ends logging early. The logger's status,
not this historical note, determines whether recording is still active.

Subsequent read-only 65-second comparison found UPS2/UPS3 VBUS_STAT=5 (Unknown
adaptor 3A), while all three units have AUTO_INDET_EN=OFF, BC12_DONE_STAT=OFF,
Power Good and EN_HIZ=OFF. Thus disabled auto detection alone does not explain
V4's code 8; the specific startup/hardware cause remains unverified. UPS2 VBUS
was 5.113 V and UPS3 19.976 V; actual IINDPM is 1.5 A / 1 A / 1 A for UPS2/3/4.
Same reported PN=BQ25798 and DEV_REV=1. Evidence:
`evidence/mqtt-adapter-compare-20261110-172743/ASSESSMENT.md`.

## V4 charge-arm startup implemented - 2026-11-10

Owner approved GPIO0 CHARGE_ARM startup sequencing and explicitly retained
`VAC2_ADC_DIS` as the existing already-configured marker. V4 declares GPIO0;
older board profiles explicitly declare no CHARGE_ARM pin. Firmware preloads
LOW and enables the output before Serial/I2C/network initialization. Existing
one-time configuration, CELL handling and charge-profile application are retained.
After either marker path, V4 sets configured ICHG, ensures watchdog disabled,
freshly verifies ICHG/watchdog/CELL/profile, writes EN_CHG=1, freshly verifies
again and only then drives GPIO0 HIGH. Reset/reconfigure first drives LOW;
detected charger errors also revoke permission, including repeated not-ready state.
This does not add independent MCU-liveness or charger-reset protection.

Existing charge-profile tests passed. The actual pin constructor and used APIs
also compiled against installed BQ25798Core with a dummy transport; the original
initializer body matched HEAD unchanged. Frozen fixture, logs and verification:
`evidence/charge-arm-startup-20261110/`. PlatformIO build attempt for ups1-4
stopped before compilation on denied global `platforms.lock` access; log:
`software/ups/.pio/charge-arm-build.log`. Target builds and on-board GPIO0/CE_N
waveform/charging validation remain pending. No firmware upload, MQTT commands
or CAD changes were performed. Owner's existing ICHG/profile/version/dependency
and unrelated hardware edits were preserved.

## UPS4 live MQTT checks - 2026-11-10

Read-only startup/input captures received all 286 state topics. Owner setup:
4S battery, idle USB-PD source module on SYS, MF52-103 10K B3950 NTC touching
battery, ambient about 22 degC. Battery-only operation showed VBAT about
13.91 V, small discharge current and no active reported faults. TDIE reported
16-16.5 degC despite the owner's approximately 28 degC package-camera reading;
a fresh cross-check still reported 16.5 degC. NTC-derived temperature was
24.2-24.3 degC. Source default beta 3435 differs from the fitted 3950, but
explains only about 0.1 degC here. Temperature accuracy remains unresolved.

Owner corrected PD-trigger input from nominal 12 V to **20 V**. Input settled
at 19.90 V and SYS at 14.57 V, but CHG_STAT remained Not Charging and IBAT=0
with EN_CHG=ON. Owner measured **TP14 (CE_N) = 4.5 V relative to GND**;
the BOM/assembly records confirm TP14 is CE_N. CE is HIGH and inhibits
charging even with EN_CHG=ON. Current firmware source has no explicit
CE/CHG_REQ GPIO drive. No charge-enable action or firmware fix was authorized
or performed; confirm the actual control-path mapping before implementation.

Evidence and assessments:
`evidence/mqtt-ups4-battery-only-20261110-160805/` and
`evidence/mqtt-ups4-pd12v-20261110-161616/` (directory retains initial input
description; assessment records corrected 20 V). No MQTT application publish,
firmware/CAD change, upload or charging qualification was performed.

## MQTT discovery sensor categories fixed - 2026-11-09

`software/ups/src/homeassistant_mqtt.cpp` maps `config` to `diagnostic`
when serializing discovery for `sensor` and `binary_sensor`. This covers
register enum labels, numeric and binary views, and manually defined sensors.
Buttons and other domains retain their configured categories; unset categories
remain omitted. BQ25798 register metadata is unchanged.

`pio run -d software/ups -e ups1 -e ups2 -e ups3 -e ups4` passed for all four
environments. Build log: `software/ups/.pio/ha-category-build.log`.
Live HA validation remains pending; no firmware upload was performed.

## Library HA component integrated, firmware builds pending - 2026-11-09

Register discovery now uses BQ25798 v1.5.2 `HomeAssistantInfo::component`
for primary BOOL, enum-label and numeric entities. Null/empty values retain
the type-based default (`binary_sensor` for BOOL, otherwise `sensor`).
Auxiliary numeric/binary enum views retain their fixed domains. The owner's
existing ^1.5.2 dependency update is preserved.

`git diff --check` passed.
Attempted `pio run -d software/ups -e ups1 -e ups2 -e ups3 -e ups4` stopped
before compilation on sandbox denial of `C:\Users\Michal\.platformio\platforms.lock`;
log: `software/ups/.pio/ha-component-build.log`. Firmware builds and live HA
validation remain pending. No upload, CAD or charging behavior changes.

## Library Home Assistant metadata integrated, firmware builds pending - 2026-11-09

Shared register discovery now reads category, icon and applicable device/state
classes from BQ25798 v1.5.1 `getHomeAssistantInfo(i)`. Null metadata is omitted,
including entity category. Units still use `Setting::unit` with degC normalization.
Enum label sensors keep their enum class/options; auxiliary numeric/binary
views keep generic classes. Binary sensors omit units/state class and unsupported
legacy status/control classes. Existing entity keys/topics, flag exclusions and
reconnect allocation reuse are preserved. Application sensors retain their metadata.
The owner's existing platformio.ini update to ^1.5.1 is preserved.

Host MSVC check compiled the actual discovery function and configuration structs
against the exact 1.5.1 release (60cc996), with mocked String/MQTT: all 230 settings,
57 enum sensors, 22 numeric registers, 140 binary sensors and 39 skipped flags
passed metadata, options, topics and repeat-publication checks. Fixture and
compile log: `software/ups/.pio/ha-metadata-check/`.
`pio run -e ups1 -e ups2 -e ups3 -e ups4` stopped before compilation because the
sandbox cannot access `C:\Users\Michal\.platformio\platforms.lock`; log:
`software/ups/.pio/ha-metadata-build.log`. Firmware builds and live HA validation
remain pending. No upload, CAD or charging behavior changes.

## MQTT enum sensors implemented, build/runtime validation pending - 2026-11-09

Shared UPS firmware now exposes each register ENUM's labels as a read-only
`sensor` with `device_class: enum`, deduplicated `options` from the library's
`Setting::strings_vector`, and no unit or state class. Discovery keys, unique
ID suffixes and state topic keys use `_enum` (owner requested no compatibility
layer). Existing numeric and binary representations are preserved. Discovery
republication deletes former retained `text` entries before publishing the
replacement. Library `ha_device_class` metadata remains unused.

MQTT buffer increased to 2 KiB for option lists. Offline data checks passed for
all 57 library enums; estimated largest MQTT discovery packet with deliberately
long device metadata is 1263/2048 bytes. `git diff --check` passed. Attempted
`pio run -e ups4 -e ups3` stopped before compilation because sandbox access to
`C:\Users\Michal\.platformio\platforms.lock` was denied; see
`software/ups/.pio/enum-build.log`. Builds, upload and live HA discovery/state
validation remain pending. No CAD or charging behavior changed.

## UPS3 reduced-charge profile readback confirmed — 2026-11-08

Owner tested APPROX_80 on existing esp19/ups3 with approx80Cell_mV=3920.
Supplied syslog at 21:55 confirms successful charger connection and VREG=15680
mV/pack (4 x 3920), recharge offset=200 mV/pack. The old VAC2_ADC_DIS marker was
already set, confirming the new profile was applied despite skipped legacy
initialization. This owner report confirms deployment/startup and register
readback on an older board, not measured 80% SOC or charge termination/recharge.
3920 mV/cell is the owner's selected setting, not a project-wide calibrated
80% voltage. Other board builds and physical charging validation remain open.

## Configurable charge profiles implemented, hardware validation pending — 2026-11-08

Owner approved shared LEGACY/FULL/APPROX_80 profiles for old and V4 boards,
configured in board_config.h, with read-only HA mode display. Added
`Config::Power::Charger::chargeProfile`; all existing profiles default to LEGACY
and keep their behavior. FULL uses explicit per-cell full voltage (default
4200 mV); APPROX_80 requires explicit calibrated cell voltage, default zero
rejected. No guessed 80%-to-voltage mapping and no board switched automatically.

Managed BQ25798 profiles set pack VREG from existing CELL (1–4S), round down to
10 mV, verify readback and use native termination/recharge instead of legacy
thresholds. Optional pack-level recharge offset 50–800 mV/50 mV; zero preserves
existing setting. Old initialization marker cannot skip the new profile, and
fresh snapshots trigger reapplication after register drift/reset. No charge
enable in battery/OTG/backup; failed configuration/readback requests EN_CHG off
and marks charger unavailable. I2C failure can prevent delivery of disable.
HA adds Charge profile and actual pack Charge voltage limit sensors.

Basis: TI SLUSDV2C rev. C, June 2026, sections 7.5.1.2 and 7.5.1.8. Volatile
registers can revert to defaults before firmware recovers: no persistent hardware
ceiling is claimed. CELL, ICHG, CE hardware control and temperature protection
are not changed by this feature. V4 CE/pack authorization and BQ25792 remain
deferred. SOC estimate is unchanged. See software/ups/README.md for settings,
manufacturer links and tests.

Host C++11 tests with undefined-behavior sanitizer passed: 1–4S conversion,
rounding, invalid settings, legacy preservation, full/reduced transitions,
reset recovery, recharge offsets, battery/backup gating and injected I2C/write/
readback failures. Owner retains manual firmware builds; no new firmware build,
upload or charging measurement performed. No CAD changes. Next checkpoint:
manual builds and pack-specific reduced-voltage selection/termination testing.

## V4 charger communication after main-power connection confirmed — 2026-11-08

Owner connected main power after USB-only operation. Supplied serial log shows
automatic transition from charger-not-detected retries to successful IC reset,
configuration in VSYS mode, charger-ready state and HA discovery republication.
HA screenshot shows live register states and model reported as BQ25798,
4-cell configuration, 750 kHz. This is register/profile readback, not evidence
of a connected four-cell battery. Battery was previously reported disconnected;
no subsequent battery connection or charging measurement was reported.

Owner-confirmed scope now includes initial charger discovery after main power
is applied and MQTT/HA register telemetry. Loss/reconnection after an established
charger session, battery operation, charging and source-failure UPS behavior
remain unverified; CE/charging implementation remains deferred. No firmware or
CAD changes in this confirmation step. Source voltage, load, ambient and full
measurement logs were not supplied for electrical qualification.

## V4 OTA and Home Assistant discovery confirmed — 2026-11-08

Owner confirms actual OTA update works and the V4 device appears correctly in
Home Assistant. Supplied HA log shows entity registration; owner subsequently
found the device and confirmed no discovery defect. Screenshot shows expected
unavailable charger entities while ESP reports charger not detected. No HA
discovery fix required. USB startup, captive portal, Wi-Fi, MQTT, OTA and HA
discovery are owner-confirmed; charger communication/telemetry, recovery and V4
charging remain separate unverified work. CE/charging changes remain deferred.

## V4 portal and network startup confirmed by owner — 2026-11-08

After toolchain restoration and partition-layout update, owner reports working
captive portal: network scan, credential submission, Wi-Fi connection and portal
exit succeed. Supplied serial log confirms OTA service startup, syslog hostname
resolution/client creation and MQTT broker connection. HA discovery starts;
completion is not included in the excerpt. Actual OTA upload, charger telemetry,
charger loss/reconnection and charging behavior remain unverified. This confirms
the reported portal crash and app-partition boot rejection no longer prevent
this startup. No additional firmware/CAD changes in this confirmation step.

## V4 firmware exceeds default app partition — 2026-11-08

After toolchain repair, owner reports boot rejection: firmware length 1313904
bytes exceeds default app slot 1310720 by 3184 bytes. Local firmware.bin agrees.
Selected bundled min_spiffs.csv in owner's ESP32-C3-MINI-1-H4X base environment:
two 0x1E0000 (1920 KiB) OTA app slots, 128 KiB filesystem, unchanged NVS/otadata
positions and coredump; 4 MB total. Current source does not use a filesystem.
Legacy boards unaffected. Owner must rebuild and perform normal USB/esptool
upload including partition table; OTA alone cannot apply the layout change.
No build/upload or board retest by Codex. Portal runtime retest remains pending.

## V4 captive portal crash: local toolchain repaired — 2026-11-08

Owner confirms build/flash/startup and reports Illegal instruction in captive
portal. Existing ELF resolves the exact failing opcode to amoadd.w in default
libstdc++ atomicity, reached via WebServer/shared_ptr. All 48 newlib C3 runtime
files were missing; compiler fell back to the default library. Restored missing
files from the cached original same-version archive after SHA256 verification.
Compiler now selects the C3 runtime; its atomicity object contains no amoadd.
No firmware workaround or WiFiManager change. Cause/time of incomplete install
remains unknown. Owner's new ESP32-C3-MINI-1-H4X environment inheritance checked
and preserved. Owner must clean/rebuild/flash and retest the portal; Codex has
not rebuilt/uploaded or verified runtime after repair.
[Diagnosis and verification](evidence/firmware-c3-portal-2026-11-08/RESULT.md).

## Application firmware V4 adaptation — 2026-11-08

Owner subsequently reports the V4 firmware build passed. No build log or
legacy-environment results supplied; upload and hardware runtime remain unverified.

Owner authorized adapting `software/ups` for ESP32-C3, mandatory explicit pins
on all board profiles, optional LED and operation without a charger. V4 uses
SDA GPIO4/SCL GPIO5, no fitted MCU LED (exported netlist). Legacy local profiles
explicitly retain SDA21/SCL22/LED2. `ups4` uses native USB serial and esptool;
`ups4_ota` provides routine OTA. Missing charger/I2C failure no longer leaves
setup waiting indefinitely: service continues, telemetry/commands are gated,
HA charger availability is published and reconnection is retried.

Owner explicitly deferred CE/charging changes and will perform builds manually.
Existing V4 ICHG=1000 mA and other charger settings are unchanged. This checkpoint
does not implement or validate V4 charge authorization, battery/profile checks
or BQ25792 compatibility. No firmware build, upload or hardware test performed.
Local V1–V3 profiles remain Git-ignored; credentials are unchanged. See
[firmware instructions](../../software/ups/README.md) for build and upload commands.
PlatformIO configuration resolution checked: V1–V3 retain esp32dev; both V4
environments select C3 with native USB serial flags. Focused diff review and
`git diff --check` passed; firmware compilation/runtime remain owner checks.
CAD unchanged. Continue with manual build/runtime feedback; handle charging in a
separate checkpoint.

## PCB update diagnosis: R19 pad nets exchanged — 2026-11-08

Owner updated PCB from SCH. Saved DRC: 12 errors, all R19 (4 shorts, 2 hole
clearances, 4 mask bridges, 2 opens), 18 original library warnings, 0 parity.
Native read-only comparison confirms all 1497 track/via geometries, 154 footprint
placements and 473 pad geometries unchanged. Only net assignments changed:
30 tracks/vias, 14 pads. R19.1 at x83.99 now MCU_SCL; R19.2 at x85.01 now MCU3V3.
Proposed owner repair: rotate PCB R19 180 degrees about (84.50,82.00), no move,
then refill/save/DRC. No repair performed or verified yet.
[Diagnosis](evidence/pcb-update-check-20261108-142617/RESULT.md).

## Latest saved schematic checkpoint — 2026-11-08

Full exported netlist equivalent to preceding repair check: 154 components /
104 nets / 445 memberships; MCU_SCL intact. ERC 0 errors / 7 warnings:
4 original GPIO labels + 3 remaining off-grid wires near MCU_SCL
(779.7309,97.79 and 781.0009,101.60); no dangling labels/endpoints.
Saved PCB DRC 0 errors / 0 opens / 18 library + 14 parity warnings unchanged.
No CAD edits/refill. [Latest evidence](evidence/saved-check-20261108-141721/RESULT.md).

## MCU_SCL repair confirmed — 2026-11-08

Saved check confirms MCU_SCL joins R19.1/U1.19/U6.7 again; 154 components /
104 nets / 445 memberships. Pin groups match pre-defect state; NEN -> /NEN is
only a name change. ERC 0 errors / 10 warnings (6 off-grid wires, 4 original
GPIO labels), no dangling endpoints/labels. Saved PCB DRC 0 errors / 0 opens /
18 library + 14 parity (9 F5 name, 3 NEN name, 2 R19). Synchronization pending.
No CAD changes/refill. [Latest evidence](evidence/saved-check-20261108-141146/RESULT.md).

## New MCU_SCL disconnect found — 2026-11-08

Latest saved review: U1.19 remains on MCU_SCL but U6.7/R19.1 split onto
Net-(U6-SCLB). Global label at (781.05,97.79) misses wire endpoint
(781.0009,97.79) by 0.0491 mm. ERC 1 error / 11 warnings (6 off-grid wires,
1 free endpoint, 4 original GPIO warnings). 154 components / 105 nets / 445
memberships. NEN -> /NEN is a name change only. DRC 0 errors / 0 opens /
18 library + 15 parity warnings. Repair MCU_SCL before propagating to PCB.
No CAD changes. [Latest review](evidence/saved-check-20261108-140900/RESULT.md).

## Owner repair recheck — 2026-11-08

Saved SCH ERC now 0 errors / 4 original GPIO warnings: five power errors and
mixed local/global F5 label warning resolved. Complete native netlist equivalent
to preceding review: 154 components / 104 nets / 445 memberships. Saved PCB
still has 11 parity warnings (9 F5 name, 2 R19); DRC 0 errors / 0 unconnected /
18 original library warnings. SCH-to-PCB synchronization remains outstanding.
No CAD changes/refill. [Latest evidence](evidence/saved-check-20261108-135813/RESULT.md).

## Owner saved schematic recheck — 2026-11-08

Read-only check: physical pin groups unchanged from power-symbol checkpoint
(154 components / 104 nets / 445 memberships), but F5_5V_OUT is now global
instead of /F5_5V_OUT. ERC 5 errors / 5 warnings: undriven power declarations
on PGND, GND, VBUS, USB_VBUS and F5_5V_OUT; mixed local/global F5_5V_OUT plus
4 original GPIO warnings. Five earlier flags absent; USB3V3 needs no flag now.
DRC 0 errors / 0 opens / 18 library warnings + 11 parity (9 F5 name, 2 R19).
No CAD changes. [Latest review](evidence/saved-check-20261108-134946/RESULT.md).

## Global power labels converted — 2026-11-08

Owner-authorized Konnect edit replaced 90 global labels: 30 PGND + 2 GND with
the established power:GND/Value convention; 58 supply labels with power:VCC
arrows retaining exact rail names. New #PWR023–#PWR112. All targeted labels gone;
full native netlist equivalent before/after (154 components / 104 nets / 445
pin memberships). ERC 0 errors / 4 original warnings. Saved-PCB DRC 0 errors /
0 unconnected / 18 library warnings + 2 R19 net-conflict parity warnings.
R19 pin assignments already differed from v4.0.0 in this task's input; preserved.
PCB/project unchanged. New symbol text positions inspected/adjusted; no refill.
[Change and verification](evidence/power-symbols-2026-11-08/RESULT.md).
For the next substantially different milestone prefer a fresh chat.

## Implicit net-name connections inventoried — 2026-11-08

Read-only Konnect geometry + native netlist/SVG analysis found 46 nets joining
physically separate pin groups: 33 signal/local nets, 13 supply/ground nets.
All 445 native pin memberships covered; every separated group has a label or
power symbol. Fresh connectivity still equals v4.0.0. No CAD changes/check rerun.
Owner will draw connections manually; keep at least one existing name per net
for stable naming, and keep labels on any groups not joined by wires.
Full pin-group inventory: [implicit connections](evidence/implicit-nets-2026-11-08/RESULT.md).
Reusable helper: tools/find_implicit_connections.py. After this checkpoint,
prefer a fresh chat for a substantially different task.

## Final saved connectivity checkpoint passed — 2026-11-08

Owner's U8/J8 corrections verified: full netlist connectivity equals v4.0.0 at
154 components / 104 nets / 445 pin memberships; U8.6 on /F5_RAW and J8 extra
endpoint warning gone. ERC 0 errors / 4 original label warnings. Completed
saved-PCB DRC 0 errors / 0 unconnected / 0 parity / 18 original library warnings;
ERC/DRC warning identities match tag. Sources stable; no CAD changes/refill.
[Final evidence](evidence/netlist-final-2026-11-08/RESULT.md).

## Owner repaired U8 ANODE — verification 2026-11-08

Fresh saved-file Konnect check confirms U8.6 restored to /F5_RAW and full
connectivity equal to v4.0.0: 154 components / 104 nets / 445 pin memberships.
ERC 0 errors / 5 warnings: four original labels and an excess wire stub at
J8.3, from (398.78,502.92) to (402.59,502.92) mm. DRC 0 errors / 0 unconnected /
0 parity / 18 original library warnings. No CAD changes or zone refill.
[Repair verification and remaining stub](evidence/netlist-recheck-fixed-2026-11-08/RESULT.md).

## New saved schematic regression — 2026-11-08

Owner-requested recheck found U8.6 ANODE disconnected from /F5_RAW; this is the
only changed pin assignment versus v4.0.0. Current SCH SHA256 starts 476870f6,
different from preceding review's 16b6e6f4. Independent fresh CLI and Konnect
exports agree: 154 components / 105 nets / 445 pin memberships. ERC: 3 errors /
7 warnings, including the disconnected ANODE and adjacent dangling wire. Saved
PCB retains correct /F5_RAW at U8.6: DRC 0 errors / 0 unconnected / 18 original
library warnings plus 1 net-conflict parity warning. No CAD changes made.
Repair target: U8.6 -> /F5_RAW; keep /F5_GATE separate, then rerun checks before
updating PCB. [Evidence](evidence/netlist-recheck-2026-11-08/RESULT.md).

## Saved netlist review against v4.0.0 — 2026-11-08

Fresh Konnect netlist/ERC/DRC checkpoint: connectivity unchanged at 154 components,
104 nets / 445 pin memberships; exported library definitions identical. ERC:
0 errors / same 4 single-pin label warnings. DRC: 0 errors / 0 unconnected /
0 schematic parity / same 18 library-footprint warnings as the tag. Existing
tag SCH/PCB/project snapshots verified against Git blob identities. No CAD
changes, editor saves or zone refill. Unsaved editor state unavailable because
Konnect editor-state observation returned stale_target. Findings and scope:
[netlist review](evidence/compare-v4.0.0-2026-11-08/NETLIST_REVIEW.md).

## Tool consolidation and cleanup - 2026-11-08

All four former root tools/kicad helpers now live directly in hardware/v4/tools.
Their capability/usage list is merged into tools/README.md; imports and references
are updated. Empty root tools/kicad and tools directories removed. Nine obsolete
files deleted: exact F5 migration/proof branch, exact stencil production wrapper,
fixed supply/USB review scripts and their two exclusive tests. Retained historical
modules remain where their shared helpers are dependencies of reusable tools;
the README module index records those dependencies. No CAD changes performed.
Validation: retained Python syntax/local import targets and helper inventory pass.
Full offline suite: 183 tests, 14 errors from missing CAM dependencies
(shapely/gerbonara) and one historical source/snapshot metadata comparison.

## Selected PCB fields synchronized - 2026-11-08

Owner-authorized direct S-expression field synchronization completed: 79 Purpose,
25 PopulationGroup, 4 Description values added/updated on PCB from current SCH.
Existing field geometry preserved; newly added fields hidden on F.Fab. Targeted
readback found no remaining differences in these selected fields; no new full
ERC/DRC run requested. Earlier DNP mismatches had already been cleared by owner.
Reusable helper: `hardware/v4/tools/sync_pcb_fields.py`; report:
`evidence/compare-v4.0.0-2026-11-08/field-sync.json`.
F8: enable "Update footprint fields from symbols" for future synchronization.

## Owner-updated PCB check against v4.0.0 - 2026-11-08

Saved-file check: connectivity unchanged (104 nets / 445 pin memberships).
ERC 0 errors / 4 original warnings. DRC 0 errors / 0 unconnected / 18 original
library warnings; SCH/PCB parity warnings reduced 228 -> 110. Remaining custom
fields: 76 Purpose, 25 PopulationGroup, 4 Description; native DNP differs for
C20, C22, C24, C25 and R11. No design changes or zone refill performed.
See [updated check](evidence/compare-v4.0.0-2026-11-08/UPDATED_RESULT.md).

## Native DNP fields and tooling - 2026-11-08

Removed legacy custom DNP properties from the schematic. Native schematic DNP
is now set for C20, C22, C24, C25 and R11 (R11 was already checked by the owner).
The completed schematic migration preserved 104 nets / 445 pin memberships;
ERC remained 0 errors / 4 warnings. Separately removed 20 redundant `DNP=NO`
property blocks from the PCB by owner-authorized S-expression removal; native
PCB DNP attributes were not synchronized. This later PCB metadata cleanup did
not trigger another full validation run. Evidence: `evidence/native-dnp-2026-11-08/`.
Reusable read-only helpers now live in `hardware/v4/tools/`, documented in its README.
One-off baseline-specific migration scripts remain historical evidence.
Owner requests proportionate, batched checks and reuse of Git comparison points.

## Schematic Value/Purpose fields - 2026-11-08

Owner-authorized field separation completed on the current saved schematic.
All 178 symbols reviewed; 118 have planned Value/field changes and 83 now have
a separate visible Purpose. Values retain electrical ratings; capacitance units
are consistent. The prior wired functional-block layout is retained, with text
placement adjustments only. Symbol positions, wires, labels and all 104 nets /
445 connected pin memberships are unchanged. ERC: 0 errors / same 4 warnings.
PCB/project are hash-identical to this task's baseline. PCB Value/custom-field
metadata has not been synchronized; a later normal SCH-to-PCB metadata update
is required before using PCB BOM fields or claiming fresh metadata parity.
Approved assembly/sourcing decisions and hardware boundaries remain unchanged.
Final schematic SHA256: `32ca33ac8a161dd014890f61869f5c20733134706b4301ac60bfda2eb6e14a97`.
See [field migration, previews and verification](evidence/symbol-fields-2026-11-08/RESULT.md).

## Owner-replaced mounting holes — DRC checkpoint 2026-11-07

Owner installed the project mounting-hole footprints. Fresh live-IPC refill,
save and project-context DRC completed: **4 errors**, 0 unconnected, 18 original
library-mismatch warnings plus 4 schematic-parity warnings. Each H1–H4 rule area
forbids its own NPTH pad because the prepared library enabled pad keepout without
excluding the hole. This is a defect in the prepared footprint, not an owner
placement error. Each H1–H4 also lacks the schematic `Bought` field. No corrective
CAD changes performed during this check; resolution and fresh DRC remain pending.
Full report: [owner-final-drc.json](evidence/mounting-hole-2026-11-07/owner-final-drc.json).

## PCB reference readability checkpoint — 2026-11-07

Owner-authorized label-only update completed on the open production V4 board:
121 visible reference positions/angles changed through native KiCad IPC; no
font-size, footprint placement/definition, copper or connectivity changes.
All 151 visible references checked without glyph-box overlaps against other
references, physical footprint envelopes, pads or fixed board silk. Orientations
are 0°/90°; SW1/SW2/C24 preserved. Exact native preservation and focused Git diff
verified. DRC: 0 errors/opens/parity, same 18 existing warning identities;
schematic/project/rules hash-identical. No ERC rerun or manufacturing regeneration.
Saved board SHA256: `80c8bc9b413de26d61cd1de42df50f0c1ce5ce6036e430e7f900b8de1c105459`.
See [result and evidence](evidence/silkscreen-2026-11-07/RESULT.md).
The historical Phase4.24W baseline below predates this silkscreen-only update.
The hardware bring-up boundary remains as recorded below.

## Active checkpoint — hardware bring-up Phase 1, 2026-11-06

Owner reports the first PCB manufactured and fully assembled as F5, passive
electrical checks passed. USB-only observations: USB3V3=3.3 V, MCU3V3=3.3 V,
MAIN_3V3=0 V, approximately 8 mA from 5 V USB before application firmware.
Native USB Serial/JTAG is stable; owner's esptool 5.1.0 identifies ESP32-C3
revision 1.1 and XMC 4 MB flash. These observations were not repeated by Codex.
This explicit owner task supersedes the earlier purchase-preparation stop only
for preparing/building the minimal diagnostic; it does not authorize flashing.

Current branch: `v4-with-mcp-help`. Diagnostic prepared on the earlier bring-up branch;
pre-existing edits retained. Existing project `software/i2c_test` now has a
separate default `v4_usb_bringup` environment. Production `software/ups` and
legacy Arduino charger-test source are preserved. The Arduino diagnostic source
is selected by build_src_filter, with no external libraries. Owner explicitly
requested plain `platform = espressif32`, no pinned versions, no ESP-IDF/CMake
project, and accepted default serial-port behavior. Native USB Serial/JTAG uses
ARDUINO_USB_MODE=1 and ARDUINO_USB_CDC_ON_BOOT=1. Target: compatible C3-MINI,
160 MHz CPU, DIO/40 MHz/4 MB flash. No application GPIO/LED/I2C/charger/CE/power
or radio initialization. BOOT/RESET remain available. Earlier IDF/CMake attempt
was abandoned and its project files removed; old build logs are historical.

See [firmware and upload procedure](../../software/i2c_test/V4_USB_BRINGUP.md).
Build/configuration evidence: `evidence/phase1-usb-bringup/`.
Arduino build PASSED (14.08 s), using plain `pio run -d software/i2c_test
-e v4_usb_bringup`. Local nested RISC-V toolchain layout repaired with directory
junctions; original tool files retained in `_original_layout`. No PATH override
or project build scripts are required. Platform/library versions are unpinned.
Hardware runtime, application current, USB/recovery and back-power validation
remain pending. No COM4 access, upload, CAD change, UPS-function implementation,
hardware measurement, purchase, commit or push is authorized/performed here.
**STOP before flashing: await explicit owner approval.** Use a fresh session
for the next substantive hardware bring-up checkpoint.

## First main-input power preparation

Use the [first-main-power procedure](evidence/FIRST_MAIN_POWER_F5_REVIEW_2026-11-06.md)
and [technical rationale](evidence/FIRST_MAIN_POWER_F5_TECHNICAL_NOTES_2026-11-06.md).
These are preparation/review records, not evidence of main-input energizing.
Confirm the actual assembled population against the final assembly BOM; approved
purchasing substitutions do not prove which components were physically fitted.
No cleanup operation authorizes flashing, energizing or hardware changes.

## Engineering and accepted production references

- [Requirements and owner decisions](V4_REQUIREMENTS.md),
  [architecture](V4_ARCHITECTURE.md), [variants](V4_VARIANTS.md),
  [BOM review](V4_BOM_REVIEW.md), [charger package map](V4_CHARGER_PACKAGE_MAP.md).
- [Safety/design decisions](evidence/v4-safety-design-review-2026-10-11.md).
- [Accepted Phase4.24W production result](evidence/phase4-24w-production-native-adoption/RESULT.md)
  and [installed baseline](evidence/phase4-24w-production-native-adoption/accepted-installed-baseline.json).
  Accepted PCB SHA256: `d0a8c95a1b8cfbeff1f4f7fa4a95abf297a86d9c95551ed5b7b3050f42b8ac2b`.
  Recorded final checks: DRC 0 errors/opens/parity, 18 accepted warning identities;
  ERC 0 errors/4 accepted warnings. These are historical CAD checks, not hardware
  qualification or a fresh validation of subsequent edits.
- [Recorded manufacturing configuration](evidence/phase4-24-owner-gerber-review/ORDER_CONFIGURATION.md)
  and [manufacturer notes](evidence/phase4-24-owner-gerber-review/MANUFACTURER_NOTES.md).
  These document reviewed settings, not a supplier's as-manufactured certificate.
- [Reusable guarded tools](tools/README.md). Historical migration plans and
  accepted manifests are not permission to replay completed transactions.

## Final purchasing and assembly references

Owner approved all Phase5.5 substitutions and the final five-F5 quantities,
including both inductors, both resistor pairs, all three R5 profiles, wires,
additional C32 stock and MOQ excess. Final reference files:

- [LCSC order](sourcing/FINAL_LCSC_ORDER.csv), [TME order](sourcing/FINAL_TME_ORDER.csv).
- [Assembly BOM](sourcing/FINAL_ASSEMBLY_BOM.csv) and
  [purchase/assembly checklist](sourcing/FINAL_PURCHASE_CHECKLIST.md).
- [Sourcing guide](sourcing/README.md) and
  [substitution electrical/fit review](sourcing/PHASE5_5_SUBSTITUTION_REVIEW.md).

The approved assembly plan pairs R60=16k with R61=3.01k despite unchanged 53k/10k
schematic metadata, and R32 Viking with R33 RESI. R5 profiles are alternative
stock: fit only the selected profile per board. Consult the final CSVs for exact
MPNs, DNP exclusions and quantities. Historical supplier prices/stock are dated
observations, not current availability, reservations or delivered quotations.

## Repository cleanup - 2026-11-07

Owner authorized removing obsolete evidence, temporary outputs and session notes.
The first pass removed repeated exports, scratch copies, caches and logs; the
second removed superseded checkpoints/STOP records, old execution summaries and
their unused illustrations. This handover replaces the former session diary.
[Evidence index](evidence/README.md) describes the retained material.

Keep source tools, downloaded documentation/dependencies, raw sourcing inputs,
electrical calculations, accepted production proofs, hardware/bring-up records
and offline regression fixtures. Removed operational artifacts are in Git
history; some historical scripts require their matching old context to reproduce
an old run. Do not weaken hash guards or overwrite final purchasing files by
replaying old builders. Use fresh authorized contexts for further CAD changes.

Production CAD, libraries, manufacturing/order data, firmware and final sourcing
files were not changed by cleanup. No hardware measurements or fresh ERC/DRC
were performed. The authorized hardware checkpoint remains unchanged.
