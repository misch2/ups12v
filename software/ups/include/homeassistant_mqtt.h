#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

#include "logger.h"
#include "version.h"

namespace HomeAssistant {
struct EntityBaseConfig {
  String component;            // component type e.g. "sensor", "text", "switch", etc.
  String config_key;           // sensor name, e.g. "backlight_status"
  String state_key;            // sensor state topic name, e.g. "backlight_status" or "backlight_status_number"
  String entity_category;      // "diagnostic", "config", etc.
  String device_class;         // see
  String state_class;          // usually "measurement"
  String unit_of_measurement;  // e.g. "W", "V", "A", "kWh", etc.
  String name;                 // optional name for the entity
  String icon;                 // "mdi:battery" etc.
};

class EntityConfig {
 public:
  EntityConfig(const EntityBaseConfig base) : base(base), refreshInterval(60 * 1000L), lastSentMillis(0) {};
  EntityConfig(const EntityBaseConfig base, long refreshInterval) : base(base), refreshInterval(refreshInterval), lastSentMillis(0) {};

  const EntityBaseConfig base;
  long refreshInterval;  // how often to refresh the entity state in milliseconds
  long lastSentMillis;   // last time this entity was sent to Home Assistant
};

class EntityMultiConfig {
 public:
  EntityMultiConfig() : configSensor(nullptr), configBinarySensor(nullptr), configText(nullptr) {}
  EntityConfig* configSensor;
  EntityConfig* configBinarySensor;
  EntityConfig* configText;
};

class MQTT {
 public:
  MQTT(PubSubClient& mqttClient, Logger& logger, String deviceName) {
    this->mqttClient = &mqttClient;
    this->logger = &logger;
    this->deviceName = deviceName;
  }
  void publishConfiguration(EntityConfig* config);
  void publishStateIfNeeded(EntityConfig* config, String value, bool force = false);
  String getConfigTopic(EntityConfig* config);
  String getStateTopic(EntityConfig* config);
  String getCommandTopic(EntityConfig* config);

 private:
  void _publish(bool isConfiguration, EntityConfig* config, String value);
  PubSubClient* mqttClient;
  Logger* logger;
  String deviceName;  // device name, e.g. "energy_monitor" or "monitor1"
};

};  // namespace HomeAssistant
