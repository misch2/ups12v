# First setup and recovery

The same configuration form works on the LAN and the device's WPA2 setup AP.
Join it from a laptop or phone, keep the connection even though it has no Internet,
then browse directly to **http://192.168.4.1/**. No captive portal or WiFiManager
is required. The AP does not route traffic to the LAN.

## AP name and password

Each unit has an `ups-setup-<12 hex digits>` AP name and a random 16-character WPA2
password, saved once in `ups-settings/recovery-ap`. Find both on the LAN page under
**Setup and recovery**, or through USB serial at 115200 baud: send `recovery` plus
a newline. They are also printed directly to USB at boot. Keep the password or
make a label before installing the unit. First setup needs USB serial or that label.

The AP password is intentionally displayed as authorized by the owner. Saved
station Wi-Fi and MQTT passwords remain hidden and are not exported or logged.
The AP password is not sent to syslog/MQTT or included in settings exports.
An unreadable AP-password record disables protected recovery rather than starting
an open AP; storage repair then requires USB/NVS intervention.

## When the AP runs

| Situation | Behavior |
| --- | --- |
| Unconfigured unit, or no saved station SSID | AP starts immediately and stays available until setup and restart. |
| Configured unit without Wi-Fi/IP for two minutes | AP starts automatically; STA reconnection continues. |
| Wi-Fi returns after automatic fallback | Automatic AP closes; normal LAN services resume. |
| Start recovery AP from web or `recovery on` on USB | AP stays on, including while Wi-Fi is connected, until stopped or restarted. |
| Stop manual recovery AP / `recovery off` | AP stops if setup does not require it; offline fallback can reopen it after another two minutes. |

Power control continues; no settings are erased because of a network outage.
MQTT/discovery requires the provisioned ID and a station connection. A setup
hostname is never an MQTT identity. OTA is available through station or AP; use
the actual IP as the upload destination. The setup AP has no Internet access.

## Blank commissioning images

From `software/ups`, build only the target matching the physical hardware:

```text
pio run -e setup-v1
pio run -e setup-v3
pio run -e setup-v4
```

These contain no installed-device identifier, credentials or battery presets.
Existing device targets remain for migration until checkpoint 8. Both 2S/4S use
the same hardware target. CELL is read from the charger, never inferred from
voltage or changed by setup. Check the binary against installed OTA slots before
upload; changing the partition table requires USB.

On a blank device, save the device ID and appropriate battery/operating settings
through the AP form, stage station Wi-Fi separately, then restart. The ID becomes
fixed; display names stay HA-managed. A valid saved record remains authoritative
if a setup image is installed on an existing unit. Zero battery current inhibits
charging; unconfigured V4 ARM stays LOW. Legacy hardware has only best-effort I2C
charge disable when communication fails.

## Deliberate resets

Web actions require the exact confirmation and execute after the reply:

- **Forget Wi-Fi** (`FORGET WIFI`) clears saved/staged station Wi-Fi. It preserves
  operating settings, MQTT/syslog, device ID and AP password, then restarts into
  immediate AP setup because no station SSID is saved.
- **Reset settings** (`RESET SETTINGS`) removes operating settings, MQTT credentials,
  device ID and station Wi-Fi. It keeps the AP password. A commissioning marker
  prevents compiled adapter defaults from reseeding the erased ID. Restart requires
  commissioning again. Existing HA entities are not deleted.

Neither erases the entire NVS partition. Settings and SDK Wi-Fi reset is not a
cross-store atomic transaction. Errors appear on serial/available syslog; a
committed commissioning marker takes effect on restart even if Wi-Fi clearing
fails. A failed storage acknowledgement can leave an old or complete new record.
Check the resulting setup state before proceeding.

USB alternatives (newline-terminated, case-sensitive):

```text
help
recovery
recovery on
recovery off
wifi reset FORGET WIFI
settings reset RESET SETTINGS
```

For UPS4, test manual AP access first while preserving LAN settings. Then test a
two-minute Wi-Fi outage and restoration, followed by wrong credentials and AP
correction. Full reset is only for intentional recommissioning. Native simulations
pass; target builds, actual WPA2/STA coexistence, browser/OTA, heap/latency and power
validation remain owner-run. See
[checkpoint 6 evidence](../../hardware/v4/evidence/universal-firmware-step6-20261125/RESULT.md).
