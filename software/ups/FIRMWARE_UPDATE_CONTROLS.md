# Firmware updates in Home Assistant and the browser

The UPS checks the public stable feed after Wi-Fi/clock startup and every six
hours. It installs only after an explicit request. Each device selects its
compiled hardware variant; 2S/4S share that variant's image. Saved settings and
identity stay in NVS.

## Home Assistant

After loading this firmware, the existing UPS device gains a standard **Firmware**
Update entity. It reports the installed/latest versions, release notes and live
progress. Home Assistant manages Install/Skip and the skipped-version marker;
there is no new firmware setting or operating-settings MQTT configuration surface.
The entity's default ID is `update.<normalized-device-id>_firmware_update`.

The entity stays unavailable until a valid manifest has been checked this boot.
A later check failure retains the previously validated offer and reports the error
in entity attributes. Older feed versions do not offer downgrades. Install is
omitted when there is no newer compatible offer, the actual inactive slot is too
small, another action is active, or installation is already reserved. A newer
release that cannot fit can still be shown with no Install capability; inspect
the error attribute and [migration requirements](MIGRATION.md).

The standard more-info view shows progress and release information. Attributes
also include `status`, `error`, `command_error`, `checked`, `check_pending`,
`available` (a newer image fits), `feed_version` and transfer byte counts. A
rejected MQTT request is reported through `command_error`; MQTT has no synchronous
install-result response to Home Assistant.

## Browser

Open `http://<UPS-IP>/firmware`, also linked from the configuration page:

- **Check for updates** requests a new manifest check.
- **Install <version>** requests exactly the displayed version. If the offer
  changes before dispatch, reload and choose again.
- **Cancel queued installation** is available while waiting to start. Flashing
  cannot be cancelled once started.
- The firmware page refreshes every three seconds during checking/installation.
  Status is also available read-only at `GET /firmware/status`.

The same LAN/Host/origin/request-token protection as settings applies to every
POST. Viewing a page never queues an installation. Installation dispatch waits
until the HTTP reply finishes. Configuration changes, push OTA and reset/recovery
actions are reserved against concurrent installation; status reads still work.
Pending power application can finish before flashing starts. The controller's
normal charger/ARM service continues during downloading and flashing.

## First real-device test

1. Use the established USB or Arduino OTA route **once** to load B3, checking the
   final image against the device's actual installed slots first. Older B2 images,
   including the initial public `20261125.7` release, have no install UI/entity.
2. Check the boot FW/HW banner, existing HA identities, telemetry and controls.
   Open `/firmware`, press Check, and confirm the installed/latest versions. A
   B3 development build labelled `.7` against stable `.7` correctly offers no
   installation; the published `.7` asset must not be replaced.
3. Confirm the Firmware entity joins the existing HA device and has the same
   versions/status. Restart HA or reconnect MQTT and verify state/discovery return.
4. To test an actual update, publish a **new matching version/tag** containing B3,
   such as `.8`, while the test unit runs the earlier B3 bootstrap. Request a web
   check (or wait for the next periodic check). Verify that HA reports it, Skip
   does not install anything, and Clear skipped update restores the offer.
5. Choose Install on the dedicated test unit. Check progress, one restart, the
   new boot version and unchanged NVS settings/HA identities. Normal telemetry
   and controls should return after reconnection.

No hardware installation, flash-interruption recovery or live HA registration has
been validated by the agent. Keep the existing [rollback/recovery record](MIGRATION.md).
The verified public feed and its three assets are recorded in B3 evidence; a
desktop HTTPS/hash check does not establish ESP32 TLS/flash operation.

## Developer protocol

| Purpose | Topic |
| --- | --- |
| Discovery | `homeassistant/update/<id>/firmware_update/config` |
| State/attributes | `bq25798ups/<id>/state/firmware_update` |
| Install command | `bq25798ups/<id>/command/firmware_update` |
| Device LWT | `bq25798ups/<id>/availability` |
| Charger readiness | `bq25798ups/<id>/charger/availability` |

The retained state envelope contains `update` (the standard HA Update JSON) and
`details` (attributes). Discovery templates select each object. Device availability
is separate from charger readiness; existing charger entities require both online,
while Firmware requires the device online and `details.checked` true. Existing
identifiers, discovery keys and telemetry/control topics are unchanged.

HA sends the exact advertised `payload_install`: `INSTALL <version> <session-token>`.
The token rotates on every device MQTT connection, preventing retained commands
from a previous session being replayed. The advertised version is checked again
at dispatch; an old request cannot install a newer offer. Commands are configured
with `retain: false`. The broker's existing authentication/ACLs remain the MQTT
authorization boundary; no arbitrary image URLs are accepted.

Protocol follows the official [MQTT Update contract](https://www.home-assistant.io/integrations/update.mqtt/)
and [Update actions](https://www.home-assistant.io/integrations/update/).
See [service internals](FIRMWARE_UPDATE_SERVICE.md) for transfer/slot/hash guards.
