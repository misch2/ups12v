# Universal firmware checkpoint 5 verification

Date: 2026-11-25. Baseline: `f8960ee`, branch `universal-firmware`.

Implemented server-rendered LAN forms, typed service proposals, redacted export/
import, deferred restart and separate private Wi-Fi staging. Owner selected LAN
access plus request-token protection. No AP, recovery policy, HA configuration
entities or environment consolidation are implemented in this checkpoint.

## Host behavioral verification

Native C++11, MSYS2 UCRT64 g++, `-Wall -Wextra -Werror`, cached real ArduinoJson.
The web suite compiles production controller, incremental HTTP parser, LAN server,
Wi-Fi staging and SDK adapter, service, codec and store. Only sockets, platform SDK,
storage and charger dependencies are simulated. It checks emitted HTTP and rendered
HTML, not source text; no production function extraction.

Coverage: escaped values, applicable PMID/SYS/V4 fields, one-time commissioning,
full-candidate/dependent validation, failed saves, metadata/application status,
credential preserve/replace/clear, redacted import/export, unchanged active network
settings, stale forms, token/host/origin rejection, restart only after response,
Wi-Fi staging/cancel/SDK activation/readback/failures, protected records, incremental
request limits, partial sends, backpressure and abandoned-client timeout while loop
turns continue. Previous service/power, storage/NVS and boot/network suites also pass.
Console results: [native-tests.log](native-tests.log).

Reproduce the web suite from repository root:

```powershell
$env:PATH = 'C:\msys64\ucrt64\bin;' + $env:PATH
$jsonInclude = (Resolve-Path software/ups/.pio/libdeps/ups8/ArduinoJson/src).Path
New-Item -ItemType Directory -Force .tmp/universal-firmware-step5 | Out-Null
& 'C:/msys64/ucrt64/bin/g++.exe' -std=c++11 -Wall -Wextra -Werror -Isoftware/ups/tests/support -Isoftware/ups/include -I $jsonInclude software/ups/tests/config_web_test.cpp software/ups/src/config_http.cpp software/ups/src/config_web.cpp software/ups/src/config_web_server.cpp software/ups/src/wifi_settings.cpp software/ups/src/wifi_settings_esp32.cpp software/ups/src/settings_service.cpp software/ups/src/settings_codec.cpp software/ups/src/settings_store.cpp -o .tmp/universal-firmware-step5/config_web_test.exe
& ./.tmp/universal-firmware-step5/config_web_test.exe
```

## Installed-core review and live evidence

Reviewed installed core WebServer.cpp/Parsing.cpp: request/header reads and POST
body parsing can wait for data; NetworkClient::write has a retry/select loop.
The new transport uses NetworkServer::accept (nonblocking listener), at most 1024
bytes per recv/send using MSG_DONTWAIT per loop, 2048 header bytes, 28672 body bytes
and a five-second total connection deadline. NVS save/render operations are still
synchronous; this is not a hard real-time guarantee. No new HTTP task or client
sharing with the MQTT worker. Check ESP32 heap and actual loop latency on device.

Owner reported page operation but Save/Restart rejected requests carrying
`Origin: null`. Original `Referrer-Policy: no-referrer` causes opaque origins for
form POSTs according to the [Fetch standard](https://fetch.spec.whatwg.org/#append-a-request-origin-header).
Changed the emitted policy to `same-origin` and retained origin/token checks.
Native transport regression verifies the corrected emitted response header.
Owner confirmed Save/Restart now work after the correction. Other browser cases
and electrical checks remain separate validation.

Owner previously confirmed checkpoint 4 UPS4 build, OTA/boot, Wi-Fi, syslog, MQTT,
HA identity, telemetry and existing controls. These are owner reports, not agent
live measurements. No target build/upload, live NVS/RTOS/network/power test or browser
interaction was performed by the agent. Owner staged/version edits were preserved.
