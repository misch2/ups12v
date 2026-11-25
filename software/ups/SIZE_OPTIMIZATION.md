# Firmware size: measured results and further options

The final downloadable `firmware.bin` must fit both generated OTA partitions.
PlatformIO's ELF usage summary excludes some image layout overhead; use the
release staging gate or `tools/check_ota_size.py`, not the summary alone. Installed
device layouts still require their own [migration record](MIGRATION.md).

## Applied reductions

V1/V3 retain their existing 1310720-byte app slots. They use LTO and
`-fno-exceptions`, unflagging the framework's `-fno-lto -fexceptions`. The normal
`-Os` optimization remains: a measured `-Oz` trial saved only 32 bytes.

Application errors use return codes and state machines. Compilation with
exceptions disabled also verifies that the compiled Arduino/core/library code has
no required exception handlers. Exception-based recovery is unsupported in these
two images; code added later must follow the existing error-return convention or
revisit the build flags and size. Precompiled SDK libraries are unchanged. V4
keeps its previous compiler flags.

The small [CA trust store](certs/README.md) preserves certificate/hostname checks.
Telemetry entities, charger settings, partition layouts and TLS checks are preserved.
With the FW/HW startup banner, local final images are:

| Target | Final bytes | OTA slot bytes | Spare bytes |
| --- | ---: | ---: | ---: |
| ups_v1_esp32 | 1297056 | 1310720 | 13664 |
| ups_v3_sys_esp32 | 1295504 | 1310720 | 15216 |
| ups_v4_esp32c3 | 1487168 | 1966080 | 478912 |

These are cross-compiled local images, not hardware upload or timing validation.
Evidence and V4 results are in the
[latest verification record](../../hardware/v4/evidence/firmware-update-diagnostics-20261125/RESULT.md).
These figures include B3's HA/web update controls and HTTP/TLS diagnostics.

## Charger metadata copies

Implemented: all three metadata consumers in `UPS.ino` bind the result of
`getSetting()` as `const auto&`: both telemetry tracking loops and register
discovery. The library returns a reference to its existing settings list, which
belongs to the global charger object and outlives these calls. No fields are
modified. This avoids copying each Setting and its owning enum-label vector;
the temporary allocations caused by those copies are avoided without changing
values or discovery. Rebuilding all three targets saved 64 bytes on V1, 32 on V3
and 368 on V4; the main benefit is reduced repeated heap allocation/copying.

## Recommended follow-ups, not implemented

1. **Avoid the library's enum-vector copy.** `toString(int, strings_vector_t)`
   takes the const vector by value. Change that parameter to a const reference in
   a separate library update; the pinned dependency is preserved in this firmware
   change.
2. **Generate static enum tables in the charger library.** Replace owning vectors
   with constant pointer/count views backed by generated arrays. The baseline
   V1 constructor occupied 29296 bytes, including settings initialization; that is
   evidence of a useful target, not an estimate of recoverable space. Preserve all
   setting indices, enum labels, register definitions and HA metadata. This needs a
   generator/library release and compatibility tests, rather than a firmware-only
   workaround in the dependency cache.
3. **Consider a client-only TLS SDK build if more room is needed.** The baseline
   linked server handshake function alone occupied 5633 bytes despite this client
   use case. The precompiled SDK keeps client/server branches together, so ordinary
   application flags cannot safely remove it. A supported custom SDK configuration
   could omit server support; the total saving is unmeasured and requires a separate
   dependency/build checkpoint and TLS validation.

Do not use `BQ25798_MEMORY_SAVER` as a shortcut: it removes setting names/units used
by discovery. Keep OTA/recovery, TLS verification and production telemetry unless
the owner explicitly changes those requirements.
