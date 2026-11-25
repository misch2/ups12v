#include "boot_settings.h"

#include <utility>

namespace Settings {
Result loadForBoot(Store& store, const RuntimeSettings& bridgeDefaults, RuntimeSettings& active, DeviceIdentity& identity) {
  RuntimeSettings candidate;
  const auto loaded = store.load(candidate);
  bool seeded = false;
  if (loaded.status == Status::MISSING) {
    if (!DeviceIdentity::validNew(bridgeDefaults.network.mqtt.haDeviceName.c_str())) return {Status::INVALID_SETTINGS, "device identifier"};
    const auto seed = store.seedIfMissing(bridgeDefaults);
    if (!seed.ok()) return seed;
    const auto reloaded = store.load(candidate);
    if (!reloaded.ok()) return reloaded;
    seeded = seed.status == Status::SEEDED;
  } else if (!loaded.ok()) {
    return loaded;  // No fallback to compiled settings on malformed/newer/incompatible data.
  }
  if (!DeviceIdentity::validStored(candidate.network.mqtt.haDeviceName.c_str())) return {Status::INVALID_SETTINGS, "device identifier"};
  if (!identity.bind(candidate.network.mqtt.haDeviceName.c_str())) return {Status::IDENTITY_MISMATCH};
  active = std::move(candidate);
  return {seeded ? Status::SEEDED : Status::OK};
}
}  // namespace Settings
