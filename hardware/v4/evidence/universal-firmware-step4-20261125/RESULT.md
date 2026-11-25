# Universal firmware checkpoint 4 verification

Date: 2026-11-25. Baseline: `981d1fc`, branch `universal-firmware`.

Implemented production configuration service and templated power transaction,
integrated into UPS startup/main-loop/recovery. See
[service guide](../../../../software/ups/SETTINGS_SERVICE.md).

Native C++11 tests use MSYS2 UCRT64 g++, `-Wall -Wextra -Werror`, cached real
ArduinoJson and simulated storage/platform/charger dependencies. The new service
suite and checkpoint 2 persistence / checkpoint 3 startup-network regressions pass.
Console results are saved in [native-tests.log](native-tests.log).

Coverage: whole-candidate validation, save failure without RAM mutation, dependent
fields, immediate metadata, restart-only network edits, identity lock, deferred and
failed retries, fresh hardware readback, 2S/4S voltage/current limits, zero-current
inhibition, ignored writes, diagnostic inhibition, unsafe input deferral, external
input limiting and LEGACY VREG preservation. No source-text assertions or extracted
production functions are used.

Register validation references TI SLUSDV2C rev. C, sections 7.5.1.4/.5/.9/.10;
external input clamp handling references 7.3.4.3. IOTG accepts the shared
160..3320 mA range of the datasheet and installed library. No dependency modification.

These are host simulations, not ESP32 or power validation. No target firmware
build, upload, live NVS/RTOS/network operation or electrical test was run. Owner
build/live validation remains pending. Checkpoint 5 is not implemented.
