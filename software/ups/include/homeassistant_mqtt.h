#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

#include "logger.h"
#include "version.h"

namespace HomeAssistant {
class EntityConfig {
 public:
  EntityConfig(String component, String config_key, String state_key, String entity_category, String device_class, String state_class = "",
               String unit_of_measurement = "", String name = "", String icon = "", long refreshInterval = 60 * 1000L) {
    this->component = component;
    this->config_key = config_key;
    this->state_key = state_key;
    this->entity_category = entity_category;
    this->device_class = device_class;
    this->state_class = state_class;
    this->unit_of_measurement = unit_of_measurement;
    this->name = name;
    this->icon = icon;
    this->refreshInterval = refreshInterval;  // set the refresh interval
    this->lastSentMillis = 0;                 // initialize the last sent time to 0
  }

  String component;            // component type e.g. "sensor", "text", "switch", etc.
  String config_key;           // sensor name, e.g. "backlight_status"
  String state_key;            // sensor state topic name, e.g. "backlight_status" or "backlight_status_number"
  String entity_category;      // "diagnostic", "config", etc.
  String device_class;         // see
  String state_class;          // usually "measurement"
  String unit_of_measurement;  // e.g. "W", "V", "A", "kWh", etc.
  String name;                 // optional name for the entity
  String icon;                 // "mdi:battery" etc.

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
