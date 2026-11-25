#pragma once

#include "device_identity.h"
#include "settings_store.h"

namespace Settings {
// Stored settings are authoritative. Only missing storage can use the legacy adapter as a bridge.
// On failure, identity remains unbound and callers keep power/MQTT inhibited. An explicit commissioning
// marker also clears active adapter defaults, so an erased identity/credentials cannot reappear.
Result loadForBoot(Store& store, const RuntimeSettings& bridgeDefaults, RuntimeSettings& active, DeviceIdentity& identity);
}  // namespace Settings
