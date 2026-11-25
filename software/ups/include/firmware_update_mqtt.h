#pragma once

#include "firmware_update.h"
#include "homeassistant_mqtt.h"

namespace FirmwareUpdate {
class Mqtt {
 public:
  Mqtt(Service& service, Control& control, HomeAssistant::MQTT& mqtt)
      : service(service),
        control(control),
        mqtt(mqtt),
        entity({"update", "firmware_update", "firmware_update", "config", "firmware", "", "", "Firmware", "", true}) {}
  void connected(const char* nonce);
  String commandTopic() { return mqtt.getCommandTopic(&entity); }
  bool handleCommand(const char* topic, const uint8_t* payload, size_t length);
  void publish();

 private:
  Service& service;
  Control& control;
  HomeAssistant::MQTT& mqtt;
  HomeAssistant::EntityConfig entity;
  String nonce, advertisedVersion, payloadInstall;
  bool configured = false;
  struct Snapshot {
    State state = State::IDLE;
    Error error = Error::NONE, commandError = Error::NONE;
    bool pending = false, available = false, installable = false;
    uint32_t offer = 0;
    Progress progress;
  } last;
  bool haveSnapshot = false;
  uint32_t lastPublished = 0;
};
}  // namespace FirmwareUpdate
