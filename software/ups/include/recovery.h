#pragma once

#include <cstdint>

#include "settings_store.h"

namespace Recovery {
constexpr uint32_t kFallbackDelayMs = 120000;
enum class Reason { NONE, SETUP, MANUAL, WIFI_LOST };

class Driver {
 public:
  virtual ~Driver() = default;
  virtual std::string newPassword() = 0;
  virtual bool start(const char* ssid, const char* password) = 0;
  virtual bool stop() = 0;
};

class Manager {
 public:
  Manager(Settings::Backend& backend, Driver& driver) : backend(backend), driver(driver) {}
  Settings::Result begin(const std::string& deviceSuffix, bool configured, uint32_t now, bool hasSavedWifi = true);
  void request(bool enabled, uint32_t now);
  void tick(bool wifiReady, uint32_t now);
  bool active() const { return running; }
  bool available() const { return initialized; }
  const std::string& ssid() const { return apSsid; }
  const std::string& password() const { return apPassword; }
  Reason reason() const { return activeReason; }
  bool failed() const { return operationFailed; }

 private:
  Settings::Backend& backend;
  Driver& driver;
  std::string apSsid, apPassword;
  bool initialized = false, commissioned = false, manual = false, running = false;
  bool missingWifi = false;
  bool online = false, attempted = false, operationFailed = false;
  uint32_t offlineAt = 0, lastAttempt = 0;
  Reason activeReason = Reason::NONE;
};
}  // namespace Recovery
