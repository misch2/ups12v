# ESP32 migration bridge size correction - 2026-11-25

Owner version 20261125.11 is preserved. The reported bridge failures were
1,358,373 ELF program bytes for UPS1 and 1,356,737 for UPS2 against 1,310,720-byte
slots. These are the owner's reported build summaries, not final binary sizes.

## Cause and change

The shared V1/V3 environments enabled `-flto -fno-exceptions` and removed the
framework defaults `-fno-lto -fexceptions`. Their legacy ESP32 bridge environments
did not inherit that policy. UPS3 has the same omission as UPS1/UPS2.

Moved the policy to `hw_esp32` and referenced its flags from shared V1/V3 plus
the three ESP32 bridge environments. Their individual board include paths,
upload destinations, partitions, flash settings and private settings are preserved.
ESP32-C3 environments are unchanged. Exceptions were already unsupported by the
shared ESP32 images; this applies the same established policy to their bridges.

Resolved PlatformIO configuration was compared before/after, using the actual
extra-config inheritance. Both shared environments have identical resolved
options. The three bridges gain only these compiler/unflag changes; their
board/layout settings match. This is a configuration/runtime build check, not
a source-spelling test. No application code or persistent settings schema changed.

## Validation boundary

Bridge compilation uses private local per-device configuration. No credential
values or bridge binaries are included in this public evidence directory. Full
build output remains in the ignored local `.tmp/bridge-size-fix/build.log`.
No upload, device write or installed partition read was performed by the agent.
Generated partitions verify the build's capacity, not the actual device layout.

## Final verification

All three bridge builds pass in an isolated local project snapshot, FW 20261125.11.
Final binary capacity checks pass for both generated OTA slots. Shared-tree
verification initially lost dependency/SCons output files; the isolated rerun
avoids interference with other builds. Only size/hash/configuration metadata
and the sanitized result summary are retained here, not private bridge binaries.

| Bridge | Final bytes | OTA slot bytes | Spare bytes |
| --- | ---: | ---: | ---: |
| ups1 | 1297200 | 1310720 | 13520 |
| ups2 | 1295664 | 1310720 | 15056 |
| ups3 | 1295648 | 1310720 | 15072 |

Owner reports the bridge workflow now works for UPS1?UPS8. This confirms the
reported size/migration issue; it is not a claim that every firmware feature was
validated. Subsequent owner logs report HTTPS allocation failures on UPS1/UPS2,
a separate RAM issue now under investigation. No agent upload was performed.
