# Universal firmware checkpoint 6 verification

Date: 2026-11-25. Baseline: `46adb3e`, branch `universal-firmware`.

Owner decisions: protected WPA2 setup AP with device-specific password shown on
LAN/USB; immediate AP on unconfigured units; manual web/USB entry; automatic AP
after two minutes offline, stopping when Wi-Fi returns. Implemented the shared
form on AP, distinct confirmed reset actions, commissioning marker, WiFiManager
removal and credential-free setup-v1/v3/v4 targets. Existing environments remain.

## Native verification

MSYS2 UCRT64 g++, C++11, `-Wall -Wextra -Werror`, real cached ArduinoJson. Tests
compile actual production modules; platform/SDK, storage, sockets, clock and charger
dependencies are simulated. No source-text assertions or extracted-function harness.
Results: [native-tests.log](native-tests.log).

- Recovery: immediate setup/no-SSID AP, two-minute delay, return-to-STA, manual
  control, stop/postponed fallback, retry failures, rollover, persistent password,
  fail-closed storage/corrupt-record handling; production AP adapter cleanup.
- Reset: Wi-Fi-only preserves identity/settings; explicit reset can clear damaged
  pending Wi-Fi; settings marker prevents bridge reseeding and supports a new ID;
  a blank generic configuration remains unconfigured. Bounded USB command parser
  rejects missing confirmations and overlong lines.
- Web: AP details, exact reset confirmations, delayed actions after the reply,
  AP-interface host handling without STA, existing save/import/export/credential/
  request-protection/slow-client tests. Actual SDK Wi-Fi clear/readback is tested
  with substituted SDK calls, including already-disconnected status.
- Regression: service/power, persistence/NVS and boot/network suites.

Reproduce recovery suite from the repository root:

```powershell
$env:PATH = 'C:\msys64\ucrt64\bin;' + $env:PATH
$jsonInclude = (Resolve-Path software/ups/.pio/libdeps/ups8/ArduinoJson/src).Path
New-Item -ItemType Directory -Force .tmp/universal-firmware-step6 | Out-Null
& 'C:/msys64/ucrt64/bin/g++.exe' -std=c++11 -Wall -Wextra -Werror -Isoftware/ups/tests/support -Isoftware/ups/include -I $jsonInclude software/ups/tests/recovery_test.cpp software/ups/src/recovery.cpp software/ups/src/recovery_esp32.cpp software/ups/src/boot_settings.cpp software/ups/src/wifi_settings.cpp software/ups/src/settings_service.cpp software/ups/src/settings_codec.cpp software/ups/src/settings_store.cpp -o .tmp/universal-firmware-step6/recovery_test.exe
& ./.tmp/universal-firmware-step6/recovery_test.exe
```

The web suite's checkpoint-5 compile command now also needs `src/recovery.cpp`.
Installed core API review confirmed WPA2/CCMP AP defaults, AP+STA support, interface
localIP, AP shutdown and SDK station-config clearing. No fixed recovery GPIO or
power-cycle heuristic. AP mode/configuration and NVS calls remain synchronous;
host tests do not establish ESP32 loop latency or RF/stack/heap behavior.

No target firmware build, upload, live network operation or power test was run by
the agent. Owner checks: matching setup/device targets and installed OTA-slot size;
blank setup/password discovery, valid reboot, manual recovery, wrong credentials,
AP correction/restart, two-minute outage/return, reset identity behavior, OTA and
charger service during AP use. Record hardware/BOM, cells, source and load for
power validation. Checkpoint 7 is not implemented.
