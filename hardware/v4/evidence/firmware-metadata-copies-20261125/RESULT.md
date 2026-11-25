# Avoid firmware metadata copies - 2026-11-25

Baseline: 40d2db9; version 20261125.6 preserved.

Changed the three Setting locals in UPS.ino to const auto&. These are both
trackChanges loops and the HA register-discovery loop. The pinned BQ25798 library
already returns const Setting& backed by its owned settings list; the global
charger object outlives all uses. No metadata fields are modified. This avoids
copying Setting and its owning const enum-label vector at these call sites.
The library's separate toString() vector-by-value parameter remains unchanged.

## Actual verification

All three normal targets compile with the existing pinned toolchain/dependencies,
using the previously prepared ignored .tmp/pio-verify-core cache. Full compiler
output is build.log; build durations were 28.7 / 24.0 / 16.5 seconds.

| Target | Previous bytes | Final bytes | Saved | Generated slot | Spare |
| --- | ---: | ---: | ---: | ---: | ---: |
| ups_v1_esp32 | 1285952 | 1285888 | 64 | 1310720 | 24832 |
| ups_v3_sys_esp32 | 1284384 | 1284352 | 32 | 1310720 | 26368 |
| ups_v4_esp32c3 | 1472496 | 1472128 | 368 | 1966080 | 493952 |

Production release staging accepts every final image against both generated OTA
slots. Complete three-variant bundle assembly also passes. Local staging uses an
all-zero synthetic commit marker because this is uncommitted verification, not a
published release. sizes.json records measured deltas, capacities and SHA-256.
Baseline sizes were captured from the actual binaries before the source change.

No unrelated host tests or source-text assertions were introduced. This is a
read-only reference change with unchanged control flow/values; target compilation
checks const-correct use at all sites. No hardware heap/runtime measurements,
firmware upload, release or deployment was performed. Installed-slot provenance
and live operation remain hardware checks.
