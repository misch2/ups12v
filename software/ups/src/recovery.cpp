#include "recovery.h"

namespace Recovery {
namespace {
const std::string kPrefix("UPSA\1", 5);
bool validPassword(const std::string& value) {
  return value.size() == 16 && value.find_first_not_of("0123456789abcdef") == std::string::npos;
}
}  // namespace

Settings::Result Manager::begin(const std::string& deviceSuffix, bool configured, uint32_t now, bool hasSavedWifi) {
  if (deviceSuffix.size() != 12 || deviceSuffix.find_first_not_of("0123456789abcdef") != std::string::npos) {
    return {Settings::Status::INVALID_SETTINGS, "recovery identifier"};
  }
  std::string record;
  const auto loaded = backend.read(record);
  if (loaded.status == Settings::Status::MISSING) {
    const auto generated = driver.newPassword();
    if (!validPassword(generated)) return {Settings::Status::STORAGE_ERROR, "AP password generation"};
    record = kPrefix + generated;
    const auto saved = backend.write(record);
    if (!saved.ok()) return saved;
    std::string actual;
    const auto verified = backend.read(actual);
    if (!verified.ok() || actual != record) return {Settings::Status::STORAGE_ERROR, "AP password readback"};
  } else if (!loaded.ok()) return loaded;
  if (record.size() != 21 || record.compare(0, 5, kPrefix) != 0 || !validPassword(record.substr(5))) {
    return {Settings::Status::MALFORMED, "AP password record"};
  }
  apSsid = "ups-setup-" + deviceSuffix;
  apPassword = record.substr(5);
  commissioned = configured;
  missingWifi = !hasSavedWifi;
  offlineAt = now;
  initialized = true;
  return {Settings::Status::OK};
}

void Manager::request(bool enabled, uint32_t now) {
  manual = enabled;
  if (!enabled) offlineAt = now;  // Deliberate stop postpones an automatic reopen for two minutes.
  attempted = false;
}

void Manager::tick(bool wifiReady, uint32_t now) {
  if (!initialized) return;  // Never fall back to an open AP on a storage failure.
  if (wifiReady) offlineAt = now;
  else if (online) offlineAt = now;
  online = wifiReady;
  const Reason wanted = (!commissioned || missingWifi) ? Reason::SETUP : manual ? Reason::MANUAL :
                        !wifiReady && uint32_t(now - offlineAt) >= kFallbackDelayMs ? Reason::WIFI_LOST : Reason::NONE;
  const bool shouldRun = wanted != Reason::NONE;
  if (shouldRun == running) { activeReason = wanted; operationFailed = false; return; }
  if (attempted && uint32_t(now - lastAttempt) < 5000) return;
  attempted = true;
  lastAttempt = now;
  const bool success = shouldRun ? driver.start(apSsid.c_str(), apPassword.c_str()) : driver.stop();
  operationFailed = !success;
  if (!success) return;
  running = shouldRun;
  activeReason = wanted;
  attempted = false;
}
}  // namespace Recovery
