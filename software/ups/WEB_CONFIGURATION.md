# LAN configuration

Open `http://<device-IP>/` in a normal browser. For UPS4 this is currently
`http://10.52.4.125/`; its hostname is `esp76-bq25798-ups4.local`. The IP address can
change. Configuration is served directly by the firmware on port 80; no filesystem
image or frontend assets are needed.

The owner selected **LAN access plus a request token**. Anyone who can reach this
page can read operating settings and configure the UPS. There is no password login
or HTTPS. Forms have a random per-boot token, origin/host checks and stale-settings
protection. Use the device IP or hostname directly, rather than a reverse proxy.

## Save and verify

1. Review the hardware version, power path and charger-reported cell count at the
   top. These are read-only; cell count is unavailable when the charger is not ready.
2. Edit the battery, charging, input, sensor or service settings and select **Save
   settings**. Dependent fields can be changed together. The device ID is editable
   only before commissioning; display names remain Home Assistant-managed.
3. Check the returned result, then select **Refresh status**. Metadata applies in
   the main loop; power settings can remain pending, deferred or failed/retrying.
   A successful save alone does not establish that charger registers changed.
4. For MQTT/syslog changes, select **Restart device** when ready. The reply is sent
   before restart is scheduled. Reload the page after restarting, because the old
   request token is no longer valid.

Only applicable controls are shown: PMID output/backup settings on PMID hardware,
and the input-detection retry option on V4. Limits use the existing configuration
service. A zero battery charge-current ceiling inhibits charging. LEGACY leaves
VREG unchanged. Read actual charger telemetry to confirm the result.

MQTT username/password fields are intentionally blank. Blank means **preserve**;
enter a replacement or select the corresponding **Clear** checkbox. Entering a
replacement and selecting Clear together is rejected. Saved MQTT/station Wi-Fi
passwords are never returned in forms or status; request bodies are not logged.
The recovery AP password is deliberately shown under Setup and recovery.

## Wi-Fi changes

Wi-Fi has a separate **Stage Wi-Fi change** form. Blank password preserves the
staged password, or the current saved password if nothing is staged. The Clear
checkbox explicitly selects an open network. SSIDs support up to 32 bytes;
passwords are empty, 8..63 bytes, or a 64-digit hexadecimal PSK.

Staging saves a private pending record without changing the active connection.
You can cancel it before restart. On the next restart the firmware writes and
verifies the SDK credentials before connecting, then clears the pending record.
Wi-Fi is still SDK-owned. A storage acknowledgement/readback failure can leave an
old or complete new pending record; inspect the displayed staged network before
restarting after an error. Corrupt pending records are preserved, not overwritten.

Checkpoint 6 adds [protected AP recovery](RECOVERY.md). Save its password before
changing Wi-Fi. After two minutes without a station connection/IP, join the AP and
correct credentials at `http://192.168.4.1/`. Web/USB can also start recovery on
demand. Reflashing alone does not replace saved credentials/settings. Explicit
Forget Wi-Fi clears even an invalid staged Wi-Fi record while preserving the ID.

## Export and import

**Export settings** downloads the existing redacted JSON format. Paste that record
into **Import settings** to validate and save it through the same service. Hardware
compatibility and the provisioned device ID must match. MQTT credentials are
preserved locally; Wi-Fi and MQTT credentials are excluded from export/import.

## UPS4 validation

Owner-reported checkpoint 4 checks passed: target build, OTA/boot, saved Wi-Fi,
syslog, MQTT, HA identity, fresh telemetry and existing controls. These are distinct
from checkpoint 5 browser validation.

For this checkpoint, verify page loading; a harmless metadata change and reboot;
an invalid value leaving saved settings unchanged; dependent-field changes; blank
credentials staying unchanged; export/import; and power application/status with the
existing battery/source/load setup. Confirm OTA, MQTT and charger service continue
while browsing. Check free heap under repeated page loads and abandoned requests.
Test service/Wi-Fi changes last, with USB recovery available.

The first owner browser test exposed POSTs with `Origin: null` under the original
`no-referrer` response policy. It is corrected to `same-origin`; reload the form
after updating. Cross-site submissions are still rejected. See the
[Fetch origin-header rules](https://fetch.spec.whatwg.org/#append-a-request-origin-header).

Implementation and host-test scope are recorded in the
[checkpoint 5 evidence](../../hardware/v4/evidence/universal-firmware-step5-20261125/RESULT.md).
