# UPS V4 handover

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

The source-extracted MSVC host check against the installed 1.5.2 library passed
all 230 settings and nine component override/null/empty fallback cases, plus
metadata, enum options, entity keys and reconnect allocation reuse. Fixture:
`software/ups/.pio/ha-metadata-check/`. `git diff --check` passed.
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
