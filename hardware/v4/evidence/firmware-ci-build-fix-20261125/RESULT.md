# First self-hosted build failures - 2026-11-25

GitHub run: https://github.com/misch2/ups12v/actions/runs/45652188841
Commit: 3456bbf; local baseline includes owner's d927195 version bump to 20261125.6.

| Job | ID | Observed failure |
| --- | --- | --- |
| ups_v4_esp32c3 | 139339437904 | Firmware compiled; native settings_store compilation failed on GCC 9 deprecated-copy warning in String test substitute. |
| ups_v1_esp32 | 139339438088 | Reported program size 1411181 exceeds 1310720 by 100461 bytes. |
| ups_v3_sys_esp32 | 139339438168 | Reported program size 1409693 exceeds 1310720 by 98973 bytes. |

Fetched actual job logs through the GitHub connector. The runner is registered and
working: ups12v-runner-1, Linux x64, runner software 2.337.0. Checks job passed.
V4 reported program size 1487371 / 1966080 and built firmware.bin successfully.
These are PlatformIO program-size reports, not final downloaded-byte measurements
or evidence of installed device partitions. Publication/deployment were skipped.

## Changes and verification

- Explicit default copy/move special members in the String host substitute address
  the GCC 9 deprecated-copy diagnostic. Compiler warnings remain errors.
- Both classic ESP32 targets now use -flto with -fno-lto removed. Installed board
  layouts, TLS verification and final image/inactive-slot capacity checks remain.
- CI retains failed-build ELF/maps and native logs in diagnostics artifacts.
- All nine native suites pass with local MSYS2 UCRT64 GCC 16.2. GCC 9 rerun is
  pending; this machine's compiler is a different version.
- PlatformIO's effective config confirms the two target optimization flags and
  unchanged V4 settings. actionlint v1.7.7 passes (ShellCheck/Pyflakes integrations
  disabled). No target firmware build/upload or new GitHub run was performed.

**The optimized V1/V3 image sizes are unmeasured.** Their next CI builds must pass
both normal program-size and final-byte OTA checks. LTO is a focused first size
reduction; no claim is made that it has already recovered the required space.
If still oversized, use the retained maps to choose the next reduction. Do not
silently enlarge partitions or weaken TLS. Native logs are retained here; original
downloaded job logs are retained in ignored .tmp/firmware-ci-build-fix/.
