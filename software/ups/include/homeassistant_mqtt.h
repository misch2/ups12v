#ifndef HOMEASSISTANT_MQTT_H
#define HOMEASSISTANT_MQTT_H

#include <Arduino.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

#include "logger.h"
#include "version.h"

class HomeAssistant_MQTT {
 public:
  class EntityConfig {
   public:
    EntityConfig(String component, String device_topic, String config_key, String state_key, String entity_category, String device_class, String state_class,
                 String unit_of_measurement, String icon, long refreshInterval = 60 * 1000L) {
      this->component = (component == "") ? "sensor" : component;  // default to "sensor" if not specified
      this->device_topic = device_topic;
      this->config_key = config_key;
      this->state_key = state_key;
      this->entity_category = entity_category;
      this->device_class = device_class;
      this->state_class = state_class;
      this->unit_of_measurement = unit_of_measurement;
      this->icon = icon;
      this->refreshInterval = refreshInterval;  // set the refresh interval
    }

    String component;            // component type e.g. "sensor", "text", "switch", etc.
    String device_topic;         // device topic name, e.g. "energy_monitor" or "monitor1"
    String config_key;           // sensor name, e.g. "backlight_status"
    String state_key;            // sensor state topic name, e.g. "backlight_status" or "backlight_status_number"
    String entity_category;      // "diagnostic", "config", etc.
    String device_class;         // see
    String state_class;          // usually "measurement"
    String unit_of_measurement;  // e.g. "W", "V", "A", "kWh", etc.
    String icon;                 // "mdi:battery" etc.

    long refreshInterval;
    long lastSentMillis = 0;  // last time this entity was sent to Home Assistant
  };

  class EntityMultiConfig {
   public:
    EntityMultiConfig() : configSensor(nullptr), configBinarySensor(nullptr), configText(nullptr) {}
    EntityConfig* configSensor;
    EntityConfig* configBinarySensor;
    EntityConfig* configText;
  };

  HomeAssistant_MQTT(PubSubClient& mqttClient, Logger& logger) {
    this->mqttClient = &mqttClient;
    this->logger = &logger;
  }
  void publishConfiguration(HomeAssistant_MQTT::EntityConfig* config);
  void publishStateIfNeeded(HomeAssistant_MQTT::EntityConfig* config, String value, bool force = false);

 private:
  void _publish(bool config, String component, String device_topic, String config_key, String state_key, String value, String entity_category,
                String device_class,

                String state_class, String unit_of_measurement, String icon);
  PubSubClient* mqttClient;
  Logger* logger;
};

#endif  // HOMEASSISTANT_MQTT_H