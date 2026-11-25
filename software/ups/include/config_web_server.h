#pragma once

#include <WiFi.h>

#include "config_web.h"

namespace ConfigWeb {
// One client, at most one nonblocking socket operation per loop, bounded request lifetime.
class LanServer {
 public:
  explicit LanServer(Controller& controller) : controller(controller), listener(80) {}
  void begin();
  void loop(const char* hostname, Observation observation, bool apReady = false);
  bool actionPending() const { return sending && (response.restart || response.action != DeviceAction::NONE); }

 private:
  void close();
  Controller& controller;
  WiFiServer listener;
  WiFiClient client;
  RequestParser parser;
  Response response;
  std::string headers;
  size_t sent = 0;
  uint32_t acceptedAt = 0;
  bool listening = false;
  bool sending = false;
};
}  // namespace ConfigWeb
