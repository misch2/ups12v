# Final-byte OTA capacity correction - 2026-11-25

Run: https://github.com/misch2/ups12v/actions/runs/45667258533
Baseline: e240bfc; version 20261125.6 preserved.

| Variant | Job | Observed result |
| --- | --- | --- |
| V1 | 139392863617 | ELF usage 1303482 / 1310720; final-byte staging failed. |
| V3 | 139392863610 | ELF usage 1302418 / 1310720; final-byte staging failed. |
| V4 | 139392863677 | Build/tests/staging passed. |

V1 artifact 15047478306 contains the actual CI-built ELF/map. Recreated its
application image using installed esptool 5.3.0, esp32, dio/40m/4MB, application
ELF SHA offset 0xb0. Result: 1328896 bytes, excess 18176 against 1310720. No source
compilation was involved. The ELF usage total alone is insufficient for OTA fit.
Original archive, ELF/map and recreated binary remain in ignored
`.tmp/firmware-final-size/`. V3 final bytes have not been independently reproduced.

Trialled -Oz alongside LTO: it saved only 32 bytes and was removed. Final V1/V3
flags use -Os, LTO and -fno-exceptions, unflagging the framework's -fno-lto and
-fexceptions. Compiled firmware/core/library code requires no exception handlers;
the existing return-code error handling remains. Exception-based recovery is
unsupported in those two images. V4's compiler flags remain unchanged.

## Completed verification after owner authorization

The owner explicitly authorized verification builds as the agent decides.
All three targets built with pinned PlatformIO platform 55.03.311, Arduino 3.3.11,
GCC 14.2.0 and the pinned BQ25798 00c12a2 dependency. The final build includes the
new firmware/hardware/MCU banner at serial boot and first syslog attachment.

| Variant | Final firmware.bin | Minimum generated OTA slot | Spare |
| --- | ---: | ---: | ---: |
| ups_v1_esp32 | 1285952 | 1310720 | 24768 |
| ups_v3_sys_esp32 | 1284384 | 1310720 | 26336 |
| ups_v4_esp32c3 | 1472496 | 1966080 | 493584 |

The production release stage function accepts all three actual images against
both generated slots, and full bundle assembly succeeds. Local verification
metadata uses a synthetic all-zero source commit marker because changes are
uncommitted; nothing was published. Final image hashes and slot capacities are
recorded in final-sizes.json. Full successful compiler log is build-final.log.

Global PlatformIO state is read-only in this sandbox. The initial platforms.lock
failure was resolved with an ignored writable .tmp/pio-verify-core. Tool wrapper
executables and writable SDK script/flag files were copied locally; immutable SDK
data were reused through workspace junctions. Public Git dependency fetch used a
process-local http.sslBackend=openssl override, retaining TLS verification. Global
Git/PlatformIO configuration and production dependency source were not modified.

No partition layout, TLS check, charger behavior or telemetry feature was removed.
Installed-device slots, serial/syslog timing and actual OTA boot remain hardware
checks; no upload was performed. CI still needs to verify the committed changes.

Packaging diagnostics now report actual image length, failing slot capacities and
overages. Behavioral fixture checks the one-byte-over case for both slots. Failed
CI artifacts now include final firmware.bin and partitions.bin as well as ELF/map.
Thirteen Python tests and actionlint v1.7.7 pass (optional ShellCheck/Pyflakes
integrations disabled). No firmware upload, tag change, push or deployment.

GCC option reference:
https://gcc.gnu.org/onlinedocs/gcc-14.2.0/gcc/Optimize-Options.html#index-Oz
