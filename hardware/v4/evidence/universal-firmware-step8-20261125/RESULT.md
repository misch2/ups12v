# Universal firmware checkpoint 8 verification

Date: 2026-11-25. Baseline: `1409d63`, branch `universal-firmware`.

Owner intentionally skipped checkpoint 7's HA/MQTT configuration controls and
declined additional checkpoint-6 hardware checks. Existing HA telemetry and
diagnostic controls are preserved. No application runtime logic was changed here.

Normal builds expose exactly three credential-free hardware variants. The OTA
overlay selects espota with identical board/compile settings. Shared hardware
selection replaces setup-only target names. Eight device bridge targets and
their adapters remain available in the optional migration config; migration
records/private rollback bundles are not confirmed. No physical device is
claimed migrated and no private credential/backup was accessed.

## Configuration verification

The installed PlatformIO ProjectConfig parser resolved all configs:

- `platformio.ini`: three hardware environments; no per-device upload address.
- `platformio.ota.ini`: the same three environments, all using espota.
- `platformio.migration.ini`: eight preserved bridge targets plus imported shared
  targets; excluded from normal builds.

Resolved values are saved in [resolved-configs.json](resolved-configs.json).
[Comparison](config-comparison.log) against the baseline confirms preserved board,
framework/dependencies, CPU/flash/partition/USB settings. USB and OTA compile
settings match; eight bridge targets retain their old flags/destinations. This
checks configuration, not compiled firmware or bit-for-bit image equivalence.

## Capacity checker

`software/ups/tools/check_ota_size.py` reads the final image length and a supplied
installed partition-table binary. It validates the table checksum when present,
range overlap/alignment, and the presence/capacity of both OTA slots. It rejects
empty images, corrupt tables, missing/duplicate slots and oversized images.
It does not prove that the supplied table came from the target device.

Four behavioral tests cover exact fit/overflow, a smaller second slot, malformed/
overlapping/truncated/checksum tables, and older tables without checksums:

```powershell
python software/ups/tests/test_ota_size.py -v
```

Results: [capacity-tests.log](capacity-tests.log). No source-text assertions or
extracted-function harness. Existing C++ runtime modules were not modified and
their checkpoint-6 results are not presented as fresh target validation.

## Limits and rollout

No target firmware build, upload, installed-table capture, final binary-size check,
private backup, live network or electrical test was performed by the agent. The
owner's earlier UPS4 observations apply to the tested device-specific build, not
all three shared images. Per-device evidence/backup/rollback and future upload
steps are in [MIGRATION.md](../../../../software/ups/MIGRATION.md). Source/build
consolidation and migration documentation are complete; fleet rollout is not.
