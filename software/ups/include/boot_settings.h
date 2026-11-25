#pragma once

#include "device_identity.h"
#include "settings_store.h"

namespace Settings {
// Stored settings are authoritative. Only missing storage can use the legacy adapter as a bridge.
// On failure, active settings and session identity remain unchanged; callers keep power/MQTT inhibited.
Result loadForBoot(Store& store, const RuntimeSettings& bridgeDefaults, RuntimeSettings& active, DeviceIdentity& identity);
}  // namespace Settings
