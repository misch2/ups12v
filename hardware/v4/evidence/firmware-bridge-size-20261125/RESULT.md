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
