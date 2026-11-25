#pragma once

#include "settings_store.h"

namespace Settings {
struct WifiCredentials {
  std::string ssid;
  std::string password;
};

class WifiDriver {
 public:
  virtual ~WifiDriver() = default;
  virtual Result read(WifiCredentials& credentials) = 0;
  virtual Result write(const WifiCredentials& credentials) = 0;
  virtual Result clear() = 0;
};

// Wi-Fi remains SDK-owned. This separate record stages an explicit change until restart.
class WifiStore {
 public:
  WifiStore(Backend& pendingBackend, WifiDriver& driver) : backend(pendingBackend), driver(driver) {}
  Result current(WifiCredentials& credentials) { return driver.read(credentials); }
  Result pending(WifiCredentials& credentials);
  Result stage(const WifiCredentials& credentials);
  Result cancel();
  Result applyAtBoot();  // Call after enabling STA, before WiFi.begin().
  Result reset();  // Explicit owner action; also replaces an invalid pending record.
  static Result validate(const WifiCredentials& credentials);

 private:
  Result writeVerified(const std::string& record);
  Backend& backend;
  WifiDriver& driver;
};
}  // namespace Settings
