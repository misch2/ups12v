#include "settings_store.h"

namespace Settings {
namespace {
const std::string kCommissioningMarker = "{\"schema\":1,\"setup_required\":true}";
}
Result Store::load(RuntimeSettings& output) {
  std::string record;
  const auto result = backend.read(record);
  if (!result.ok()) return result;
  if (record == kCommissioningMarker) return {Status::UNCONFIGURED};
  return decodePrivate(record, hardware, output);
}

Result Store::writeVerified(const RuntimeSettings& settings) {
  std::string record;
  const auto encoded = encodePrivate(settings, hardware, record);
  if (!encoded.ok()) return encoded;
  const auto written = backend.write(record);
  if (!written.ok()) return written;
  std::string actual;
  const auto read = backend.read(actual);
  if (!read.ok()) return {Status::STORAGE_ERROR, "readback"};
  if (actual != record) return {Status::STORAGE_ERROR, "readback mismatch"};
  return {Status::OK};
}

Result Store::seedIfMissing(const RuntimeSettings& compiledSettings) {
  RuntimeSettings existing;
  const auto result = load(existing);
  if (result.status == Status::OK) {
    if (existing.network.mqtt.haDeviceName != compiledSettings.network.mqtt.haDeviceName) return {Status::IDENTITY_MISMATCH};
    return result;  // Never replace an existing record with defaults, even if adapter settings changed.
  }
  if (result.status != Status::MISSING) return result;
  const auto written = writeVerified(compiledSettings);
  if (!written.ok()) return written;
  return {Status::SEEDED};
}

Result Store::save(const RuntimeSettings& settings) {
  RuntimeSettings existing;
  const auto result = load(existing);
  if (result.status != Status::OK && result.status != Status::MISSING && result.status != Status::UNCONFIGURED) return result;
  if (result.status == Status::OK && existing.network.mqtt.haDeviceName != settings.network.mqtt.haDeviceName) {
    return {Status::IDENTITY_MISMATCH};
  }
  return writeVerified(settings);
}

Result Store::resetForCommissioning() {
  const auto written = backend.write(kCommissioningMarker);
  if (!written.ok()) return written;
  std::string actual;
  const auto read = backend.read(actual);
  if (!read.ok() || actual != kCommissioningMarker) return {Status::STORAGE_ERROR, "commissioning marker readback"};
  return {Status::OK};
}
}  // namespace Settings
