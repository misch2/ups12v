#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

#include <utility>
#include <vector>

#include "device_identity.h"
#include "logger.h"
#include "version.h"

namespace HomeAssistant {
const char* mqttStateDescription(int state);

struct EntityBaseConfig {
  // Borrow literals or immutable charger metadata; they must outlive the entity.
  const char* component;        // component type e.g. "sensor", "text", "switch", etc.
  String config_key;            // sensor name, e.g. "backlight_status"
  String state_key;             // sensor state topic name, e.g. "backlight_status" or "backlight_status_number"
  const char* entity_category;  // "diagnostic", "config", etc.
  const char* device_class;
  const char* state_class;          // usually "measurement"
  const char* unit_of_measurement;  // e.g. "W", "V", "A", "kWh", etc.
  const char* name;                 // optional name for the entity
  const char* icon;                 // "mdi:battery" etc.
  bool independentOfCharger;        // Omitted aggregate fields initialize to false.
};

class EntityConfig {
 public:
  EntityConfig(EntityBaseConfig base, unsigned long refreshInterval = 0) : base(std::move(base)), refreshInterval(refreshInterval) {};

  const EntityBaseConfig base;
  std::vector<const char*> options;  // Borrowed immutable enum labels, with the same lifetime rule as base metadata.
  unsigned long refreshInterval;     // Zero: startup/reconnect and changes only. Otherwise fixed periodic refresh.
  unsigned long lastSentMillis = 0;
  bool hasSentState = false;
  String lastSentValue;
  int suggestedDisplayPrecision = -1;
};

class EntityMultiConfig {
 public:
  EntityMultiConfig() : configSensor(nullptr), configBinarySensor(nullptr), configEnum(nullptr) {}
  EntityConfig* configSensor;
  EntityConfig* configBinarySensor;
  EntityConfig* configEnum;
};

class MQTT {
 public:
  MQTT(PubSubClient& mqttClient, Logger& logger) {
    this->mqttClient = &mqttClient;
    this->logger = &logger;
    this->deviceModel = "Unknown Model";
  }
  bool beginDevice(const char* deviceName, const char* hwVersion);
  void setTransportAvailable(bool available) { transportAvailable = available; }
  bool readyToPublish() const { return identity.ready() && transportAvailable; }
  bool publishConfiguration(EntityConfig* config, const char* payloadInstall = nullptr);
  bool removeConfiguration(String component, String configKey);
  void publishStateIfNeeded(EntityConfig* config, String value, bool force = false);
  void setDeviceModel(String model);
  String getConfigTopic(EntityConfig* config);
  String getStateTopic(EntityConfig* config);
  String getCommandTopic(EntityConfig* config);
  String getChargerAvailabilityTopic();
  String getAvailabilityTopic();
  bool publishAvailability(bool available);
  bool publishChargerAvailability(bool available);

 private:
  bool _publish(bool isConfiguration, EntityConfig* config, String value, const char* payloadInstall = nullptr);
  PubSubClient* mqttClient;
  Logger* logger;
  String deviceName;   // device name, e.g. "energy_monitor" or "monitor1"
  String hwVersion;    // hardware version, e.g. "1.0"
  String deviceModel;  // device model, e.g. "BQ25798 UPS - 4S"
  DeviceIdentity identity;
  bool transportAvailable = false;
};

};  // namespace HomeAssistant
