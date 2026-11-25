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
| ups_v1_esp32 | 1285952 | 1310720 | 24768 |
| ups_v3_sys_esp32 | 1284384 | 1310720 | 26336 |
| ups_v4_esp32c3 | 1472496 | 1966080 | 493584 |

These are cross-compiled local images, not hardware upload or timing validation.
Evidence and V4 results are in the
[verification record](../../hardware/v4/evidence/firmware-final-size-fix-20261125/RESULT.md).

## Recommended follow-ups, not implemented

1. **Avoid copies of charger metadata.** `getSetting()` already returns
   `const Setting&`, but three loops in `UPS.ino` copy the returned object.
   Bind a const reference instead. Each Setting owns a const vector of enum
   labels, so copying can allocate/copy the vector repeatedly. This should reduce
   heap churn and may shrink code; measure the binary delta before claiming savings.
   In the library, `toString(int, strings_vector_t)` also takes that vector by
   value; change it to a const reference in a separate library update.
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
