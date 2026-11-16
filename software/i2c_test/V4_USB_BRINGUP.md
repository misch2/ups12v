# V4 F5 — USB MCU diagnostic

Arduino project in the existing `software/i2c_test` PlatformIO project.
Environment `v4_usb_bringup` is the default; `platform = espressif32`, with no
pinned platform/tool/library versions and no external diagnostic libraries.
Target: ESP32-C3-MINI-1-H4X, compatible `esp32-c3-devkitm-1` definition,
160 MHz CPU, 4 MB flash, DIO / 40 MHz.

Native USB Serial/JTAG uses `ARDUINO_USB_MODE=1` and
`ARDUINO_USB_CDC_ON_BOOT=1`. `Serial` is USB, not an external UART adapter.
Application code does not initialize GPIO, LED, I2C, charger, CE, power outputs,
Wi-Fi or Bluetooth. Default ROM/framework serial behavior is accepted by the
owner's revised instruction. No custom ESP-IDF/CMake project or sdkconfig is used.
BOOT/RESET remain untouched. Serial writes have a short timeout; there is no
wait for a monitor. The startup banner repeats every ten heartbeats.

From Windows PowerShell:

```powershell
Set-Location 'C:\Users\Michal\Git\my\ups12v\software\i2c_test'
pio run -e v4_usb_bringup
```

After owner approval, connect only USB-C with a data cable, without main adapter,
battery or loads. Close other programs using COM4. Upload and monitor:

```powershell
pio run -e v4_usb_bringup -t upload --upload-port COM4
pio device monitor -e v4_usb_bringup --port COM4 --baud 115200
```

If automatic download entry fails: hold BOOT, press/release RESET, release BOOT,
then retry upload. If necessary after upload, press RESET with BOOT released.
Windows may reassign the COM number. Monitor DTR/RTS are configured to zero;
exit the monitor with Ctrl+C before another upload.

Illustrative output (not a hardware capture; reset/heap/timing vary):

```text
Firmware: ups-v4-usb-bringup/0.1.0
Chip: ESP32-C3 revision=101 cores=1
CPU: 160 MHz; flash: 4194304 bytes
Reset: POWERON (1)
USB Serial/JTAG; no Wi-Fi/BT, GPIO, I2C or charger initialization
uptime_ms=1000 free_heap=300000 heartbeat=1
uptime_ms=2000 free_heap=300000 heartbeat=2
```

Revision encoding comes from the installed Arduino core. Uptime uses `millis()`
and wraps after about 49.7 days; interval arithmetic remains valid. Output may
be dropped without an open monitor. This diagnostic does not test domain
isolation or UPS behavior. Hardware runtime/current/USB recovery remain pending.
Legacy `esp32dev` is a charger test and must not be uploaded to V4 in this phase.
Production `software/ups` and CAD are unchanged. Preparation does not flash or
open COM4. Build evidence: `hardware/v4/evidence/phase1-usb-bringup/build.log`.

Build passed on 2026-11-06 (14.08 s). The installed platform resolved to
Pioarduino 55.03.311 / Arduino 3.3.11; these are observations, not version pins.
The local RISC-V toolchain had an extra directory level. Directory junctions
repair its expected layout; original files are preserved in `_original_layout`.
Ordinary `pio` commands work without a PATH override or extra project scripts.
