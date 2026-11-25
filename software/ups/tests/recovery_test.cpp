#include <cassert>
#include <cstdio>

#include <WiFi.h>

#include "boot_settings.h"
#include "recovery_commands.h"
#include "recovery_esp32.h"
#include "settings_service.h"
#include "wifi_settings.h"

WiFiClass WiFi;
NetworkManager Network;
uint32_t esp_random() { return 0x12345678; }

struct Backend : Settings::Backend {
  std::string record;
  bool fail = false;
  int writes = 0;
  Settings::Result read(std::string& output) override {
    if (record.empty()) return {Settings::Status::MISSING};
    output = record;
    return {Settings::Status::OK};
  }
  Settings::Result write(const std::string& value) override {
    if (fail) return {Settings::Status::STORAGE_ERROR};
    record = value;
    ++writes;
    return {Settings::Status::OK};
  }
};
struct Driver : Recovery::Driver {
  int starts = 0, stops = 0;
  bool success = true;
  std::string newPassword() override { return "0123456789abcdef"; }
  bool start(const char* ssid, const char* password) override {
    assert(std::string(ssid) == "ups-setup-001122334455" && std::string(password) == "0123456789abcdef");
    ++starts;
    return success;
  }
  bool stop() override { ++stops; return success; }
};

void transitions() {
  Backend backend;
  Driver driver;
  Recovery::Manager manager(backend, driver);
  assert(manager.begin("001122334455", true, 0).ok());
  const auto saved = backend.record;
  manager.tick(false, 119999);
  assert(!manager.active());
  manager.tick(false, 120000);
  assert(manager.active() && manager.reason() == Recovery::Reason::WIFI_LOST);
  manager.tick(true, 120001);
  assert(!manager.active() && driver.stops == 1);
  manager.tick(false, 120002);
  manager.tick(false, 240001);
  assert(!manager.active());
  manager.tick(false, 240002);
  assert(manager.active());
  manager.request(false, 240003);
  manager.tick(false, 240003);
  assert(!manager.active());
  manager.request(true, 240004);
  manager.tick(true, 240004);
  assert(manager.active() && manager.reason() == Recovery::Reason::MANUAL);
  manager.tick(true, 500000);
  assert(manager.active());
  manager.request(false, 500001);
  manager.tick(true, 500001);
  assert(!manager.active() && backend.record == saved && backend.writes == 1);
  Driver secondDriver;
  Recovery::Manager second(backend, secondDriver);
  assert(second.begin("001122334455", false, 0).ok() && backend.writes == 1);
  second.tick(true, 0);
  assert(second.active() && second.password() == manager.password());  // Setup AP remains even with saved STA credentials.
  Recovery::Manager missingWifi(backend, secondDriver);
  assert(missingWifi.begin("001122334455", true, 0, false).ok());
  missingWifi.tick(false, 0);
  assert(missingWifi.active());
  Recovery::Manager rollover(backend, driver);
  assert(rollover.begin("001122334455", true, UINT32_MAX - 50000).ok());
  rollover.tick(false, 69998);
  assert(!rollover.active());
  rollover.tick(false, 69999);
  assert(rollover.active());
  Backend protectedBackend;
  protectedBackend.record = "damaged";
  Recovery::Manager protectedManager(protectedBackend, driver);
  assert(!protectedManager.begin("001122334455", false, 0).ok());
  protectedManager.tick(false, 1000000);
  assert(!protectedManager.active() && protectedBackend.record == "damaged");
  Backend failedBackend;
  failedBackend.fail = true;
  Recovery::Manager failed(failedBackend, driver);
  assert(!failed.begin("001122334455", false, 0).ok());
  failed.tick(false, 0);
  assert(!failed.active());
  Backend retryBackend;
  Driver retryDriver;
  retryDriver.success = false;
  Recovery::Manager retry(retryBackend, retryDriver);
  assert(retry.begin("001122334455", false, 0).ok());
  retry.tick(false, 0);
  retry.tick(false, 4999);
  assert(retryDriver.starts == 1 && retry.failed() && !retry.active());
  retryDriver.success = true;
  retry.tick(false, 5000);
  assert(retry.active() && !retry.failed());
  std::puts("recovery: setup/missing Wi-Fi, two-minute fallback, return-to-STA, manual control, retry, rollover and stable private AP password passed");
}

struct WifiDriver : Settings::WifiDriver {
  Settings::WifiCredentials saved{"old-network", "old-password"};
  Settings::Result read(Settings::WifiCredentials& output) override { output = saved; return {Settings::Status::OK}; }
  Settings::Result write(const Settings::WifiCredentials& value) override { saved = value; return {Settings::Status::OK}; }
  Settings::Result clear() override { saved = {}; return {Settings::Status::OK}; }
};

void resetAndCommissioning() {
  Backend backend, wifiBackend;
  WifiDriver driver;
  Settings::WifiStore wifi(wifiBackend, driver);
  RuntimeSettings original;
  original.network.mqtt.haDeviceName = "original-ups";
  original.network.mqtt.password = "PRIVATE_OLD_PASSWORD";
  original.battery.pack.maxChargeCurrent_mA = 700;
  Settings::Store store(backend, Hardware::kV4Esp32C3);
  assert(store.seedIfMissing(original).ok());
  const auto originalRecord = backend.record;
  assert(wifi.stage({"new-network", "new-password"}).ok());
  assert(wifi.reset().ok() && driver.saved.ssid.empty() && backend.record == originalRecord);
  assert(wifi.pending(driver.saved).status == Settings::Status::MISSING);
  wifiBackend.record = "damaged";
  assert(wifi.reset().ok());  // Only an explicit reset can replace a protected pending record.
  backend.fail = true;
  assert(!store.resetForCommissioning().ok() && backend.record == originalRecord);
  backend.fail = false;
  assert(store.resetForCommissioning().ok() && backend.record.find("PRIVATE_OLD_PASSWORD") == std::string::npos);
  assert(store.seedIfMissing(original).status == Settings::Status::UNCONFIGURED);
  auto active = original;
  DeviceIdentity identity;
  assert(Settings::loadForBoot(store, original, active, identity).status == Settings::Status::UNCONFIGURED);
  assert(!identity.ready() && active.network.mqtt.password.length() == 0 && active.battery.pack.maxChargeCurrent_mA == 0);
  Settings::Service service(store, Hardware::kV4Esp32C3, active);
  active.network.mqtt.haDeviceName = "new-ups";
  assert(service.propose(active).ok() && service.status().restartRequired);
  DeviceIdentity newIdentity;
  assert(Settings::loadForBoot(store, original, active, newIdentity).ok());
  assert(std::string(newIdentity.value()) == "new-ups");
  Backend blank;
  Settings::Store blankStore(blank, Hardware::kV4Esp32C3);
  RuntimeSettings generic;
  DeviceIdentity blankIdentity;
  assert(!Settings::loadForBoot(blankStore, generic, generic, blankIdentity).ok() && blank.record.empty() && !blankIdentity.ready());
  std::puts("reset: Wi-Fi-only preserves identity/settings; commissioning marker prevents bridge reseed, "
            "supports a new identity and leaves a blank image unconfigured");
}

void driverAndUsb() {
  Recovery::Esp32Driver driver;
  assert(driver.newPassword() == "1234567812345678");
  WiFi.apSuccess = true;
  assert(driver.start("test-ap", "0123456789abcdef"));
  assert(WiFi.selectedMode == WIFI_AP_STA && WiFi.apPassword == "0123456789abcdef");
  const int stops = WiFi.apStops;
  WiFi.apSuccess = false;
  assert(!driver.start("test-ap", "0123456789abcdef") && WiFi.apStops == stops + 1);
  WiFi.apSuccess = true;
  Recovery::Commands commands;
  auto line = [&](const std::string& text) {
    Recovery::Command result = Recovery::Command::NONE;
    for (char c : text) result = commands.feed(c);
    return result;
  };
  assert(line("recovery on\r\n") == Recovery::Command::START);
  assert(line("recovery off\n") == Recovery::Command::STOP);
  assert(line("wifi reset\n") == Recovery::Command::INVALID);
  assert(line("wifi reset FORGET WIFI\n") == Recovery::Command::RESET_WIFI);
  assert(line("settings reset RESET SETTINGS\n") == Recovery::Command::RESET_SETTINGS);
  assert(line(std::string(100, 'x') + "\n") == Recovery::Command::INVALID);
  assert(line("recovery\n") == Recovery::Command::SHOW);
  std::puts("platform: production AP driver cleanup and bounded USB parser with explicit reset confirmation passed");
}

int main() {
  transitions();
  resetAndCommissioning();
  driverAndUsb();
  std::puts("recovery: behavioral checks passed (storage, Wi-Fi platform and clock simulated)");
}
