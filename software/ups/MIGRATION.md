# Universal firmware migration

Normal builds now produce three hardware binaries. Each is shared by 2S/4S and
contains no installed-device identifier, credentials, battery presets or upload
destination. Configuration stays in NVS; CELL stays chip-reported.

| Environment | Hardware / power path | Devices |
| --- | --- | --- |
| `ups_v1_esp32` | V1.0 ESP32 / PMID switchover | UPS1 |
| `ups_v3_sys_esp32` | V3.3b SYS modification / ESP32 | UPS2, UPS3 |
| `ups_v4_esp32c3` | V4.0 ESP32-C3 / SYS | UPS4-8 |

## Build and upload

Run from `software/ups`, selecting the intended environment:

```powershell
pio run -e ups_v4_esp32c3
```

Before upload, check the final image against **both installed OTA slots**. Obtain
`installed-partitions.bin` from the device or a verified matching backup; a build's
generated table does not establish the installed layout:

```powershell
python tools/check_ota_size.py --firmware .pio/build/ups_v4_esp32c3/firmware.bin --installed-partitions .migration-backups/UPS4/installed-partitions.bin
```

The tool validates table ranges/checksum and checks all OTA app slots. It does not
establish table provenance, choose the MCU or qualify hardware. An oversized image
needs a separate partition-migration decision and USB upload; application OTA cannot
replace a partition table. This change preserves board/flash settings, including
V4 `min_spiffs.csv` (1920 KiB slots). Installed legacy slot sizes are unconfirmed.

USB and OTA use the same environment names/build flags. The OTA config only selects
the uploader. After size/layout checks, supply the actual destination:

```powershell
pio run -e ups_v4_esp32c3 -t upload --upload-port COMx
pio run -c platformio.ota.ini -e ups_v4_esp32c3 -t upload --upload-port esp76-bq25798-ups4.local
```

Replace the environment/destination for other units. For a new/reset device follow
[first setup](RECOVERY.md). A shared image cannot recover old operating settings
from a unit without a migration record: it enters commissioning.

## Per-device prerequisites

1. Keep the exact working firmware/USB recovery bundle, source commit and build
   environment. Record its effective compiled settings for rollback.
2. Confirm the NVS identifier/hardware below. Older installations need their own
   bridge image first; its saved record must survive restart. Never use another
   unit's adapter or guess battery limits.
3. Download the redacted settings export. Keep private credentials, Wi-Fi/NVS and
   the AP password separately. Export/import excludes Wi-Fi and MQTT credentials
   and is not a complete restore backup.
4. Retain a verified installed partition table and matching bootloader/partition/
   NVS or full-flash backup where required for USB recovery. Use detected flash
   size and installed offsets. Keep credential-containing backups private.
5. Build the matching shared target, check final size, then owner-select the upload.
   Preserve NVS: do not erase flash or use Reset settings during migration.

An ignored local location is `.migration-backups/<UPS-number>/`. No private backup
or credential was read, copied or created here. Local `secret/michal_config.h`
remains available for bridge rebuilds and must never be committed.

| Unit | Exact existing ID | Shared environment | Saved record evidence | Export / private rollback bundle |
| --- | --- | --- | --- | --- |
| UPS1 | `esp18-bq25798-ups1` | `ups_v1_esp32` | Not confirmed | Not supplied |
| UPS2 | `esp27-bq25798-ups2` | `ups_v3_sys_esp32` | Not confirmed | Not supplied |
| UPS3 | `esp19-bq25798-ups3` | `ups_v3_sys_esp32` | Not confirmed | Not supplied |
| UPS4 | `esp76-bq25798-ups4` | `ups_v4_esp32c3` | Owner confirmed boot, identity and checkpoint-5 saves | Not supplied |
| UPS5 | `esp77-bq25798-ups5` | `ups_v4_esp32c3` | Not confirmed | Not supplied |
| UPS6 | `esp78-bq25798-ups6` | `ups_v4_esp32c3` | Not confirmed | Not supplied |
| UPS7 | `esp79-bq25798-ups7` | `ups_v4_esp32c3` | Not confirmed | Not supplied |
| UPS8 | `esp80-bq25798-ups8` | `ups_v4_esp32c3` | Not confirmed | Not supplied |

The ID/hardware mapping comes from tracked adapters, not live inventory. For each
unit record battery/cells, source/load, limits, installed slots, backup paths,
old/new image hashes and migration result privately. No unit is marked migrated
to a shared image here.

## Bridge and rollback

The eight adapters/settings remain in the separate [migration config](platformio.migration.ini):

```powershell
pio run -c platformio.migration.ini -e ups4
```

Select the matching unit. Retained targets preserve their previous default/USB
uploader behavior and destinations; an explicit port overrides the destination.
They are absent from normal USB/OTA configs. Keep them until device migration
records and rollback bundles are confirmed.

A newer bridge honors valid saved settings: rebuilding alone does not restore its
compiled defaults. Pre-persistence firmware may ignore NVS and immediately use its
compiled ID, credentials, limits and profile. Keep those exact values with the
rollback image. Do not erase an unknown/newer record to make rollback boot. USB
restore must use matching offsets and preserve or deliberately restore private NVS.

## Validation status

Checkpoint 7 is intentionally skipped: web configuration is sufficient. Existing
HA telemetry and diagnostic controls remain. The owner declined additional
checkpoint-6 hardware checks; host results do not establish RF/power behavior.

PlatformIO resolution confirms three normal/OTA targets, identical build settings
between upload modes and preserved bridge board settings. The capacity tool has
behavioral fixture tests. Target builds, final sizes, private backups and physical
rollout are not performed/verified by the agent. No device adapter/bridge target
has been permanently removed. See
[checkpoint 8 evidence](../../hardware/v4/evidence/universal-firmware-step8-20261125/RESULT.md).
