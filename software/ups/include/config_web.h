#pragma once

#include "config_http.h"
#include "settings_service.h"
#include "recovery.h"
#include "wifi_settings.h"

namespace ConfigWeb {
struct Observation {
  Observation(int cells = 0, bool chargerReady = false) : cells(cells), chargerReady(chargerReady) {}
  int cells;  // Zero means unavailable; never infer cells from voltage.
  bool chargerReady;
};

class Controller {
 public:
  Controller(Settings::Service& settings, const Hardware::Profile& hardware, const RuntimeSettings& bootDefaults, Settings::WifiStore& wifi)
      : settings(settings), hardware(hardware), defaults(bootDefaults), wifi(wifi) {}
  void begin(const std::string& requestToken) { token = requestToken; }
  void setRecovery(const Recovery::Manager* manager) { recovery = manager; }
  void setWritesLocked(bool locked) { writesLocked = locked; }
  bool actionPending() const { return restarting || pendingAction != DeviceAction::NONE; }
  Response handle(const Request& request, const std::string& hostname, const std::string& ip, Observation observation);
  void responseSent(bool restart, uint32_t now);
  void responseSent(const Response& response, uint32_t now);
  DeviceAction takeAction(uint32_t now);
  bool restartDue(uint32_t now) const;

 private:
  const RuntimeSettings& desired() const;
  Response page(Observation observation, int code = 200, const std::string& message = "");
  Settings::Service& settings;
  const Hardware::Profile hardware;
  const RuntimeSettings& defaults;
  Settings::WifiStore& wifi;
  std::string token;
  bool restarting = false;
  bool writesLocked = false;
  uint32_t restartAt = 0;
  const Recovery::Manager* recovery = nullptr;
  DeviceAction pendingAction = DeviceAction::NONE;
  uint32_t actionAt = 0;
};
}  // namespace ConfigWeb
