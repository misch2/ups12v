#include "homeassistant_mqtt.h"

void HomeAssistant_MQTT::_publish(bool config,
                                  String component,            // component type e.g. "sensor", "text", "switch", etc.
                                  String device_topic,         // device topic name, e.g. "energy_monitor" or "monitor1"
                                  String config_key,           // sensor name, e.g. "backlight_status"
                                  String state_key,            // sensor state topic name, e.g. "backlight_status" or "backlight_status_number"
                                  String value,                // initial value
                                  String entity_category,      // "diagnostic", "config", etc.
                                  String device_class,         // see
                                                               // https://www.home-assistant.io/integrations/sensor/#device-class
                                  String state_class,          // usually "measurement"
                                  String unit_of_measurement,  // e.g. "W", "V", "A", "kWh", etc.
                                  String icon                  // "mdi:battery" etc.
) {
  String config_topic = "homeassistant/" + component + "/" + device_topic + "/" + config_key + "/config";
  String state_topic = "bq25798ups/" + device_topic + "/state/" + state_key;

  if (config) {
    // create HomeAssistant config JSON
    JsonDocument doc;
    doc["state_topic"] = state_topic;
    doc["device"]["manufacturer"] = "Michal";
    doc["device"]["model"] = "UPS";
    doc["device"]["hw_version"] = "1.0";
    doc["device"]["sw_version"] = FIRMWARE_VERSION;

    JsonArray identifiers = doc["device"]["identifiers"].to<JsonArray>();
    identifiers.add(device_topic);
    doc["device"]["name"] = device_topic;
    doc["enabled_by_default"] = true;
    doc["entity_category"] = entity_category;
    if (device_class != "") {
      doc["device_class"] = device_class;
    }
    doc["state_class"] = state_class;
    doc["unit_of_measurement"] = unit_of_measurement;
    if (icon != "") {
      doc["icon"] = icon;
    }
    doc["force_update"] = true;   // force update the entity state on every publish
    doc["expire_after"] = "300";  // expire after 5 minutes
    doc["name"] = config_key;
    doc["unique_id"] = device_topic + "_" + config_key;

    if (component == "binary_sensor") {
      doc["payload_on"] = "ON";
      doc["payload_off"] = "OFF";
    } else if (component == "text") {
      doc["command_topic"] = state_topic;  // use the same topic for command and state
    }

    String serialized;
    serializeJson(doc, serialized);
    if (!mqttClient->publish(config_topic.c_str(), serialized.c_str(),
                             true))  // publish as retained, to survive HA restart
    {
      logger->log(LOG_ERR, "Failed to publish HomeAssistant config for %s", config_topic.c_str());
    }
  } else {
    // Just publish the state value
    mqttClient->publish(state_topic.c_str(), value.c_str(), false);
  }
}

void HomeAssistant_MQTT::publishConfiguration(HomeAssistant_MQTT::EntityConfig* config) {
  if (config != nullptr) {
    _publish(true, config->component, config->device_topic, config->config_key, config->state_key, "", config->entity_category, config->device_class,
             config->state_class, config->unit_of_measurement, config->icon);
  }
}
void HomeAssistant_MQTT::publishStateIfNeeded(HomeAssistant_MQTT::EntityConfig* config, String value, bool force) {
  if (config != nullptr) {
    long now = millis();
    if (force || (now - config->lastSentMillis >= config->refreshInterval) || (now - config->lastSentMillis < 0)) {
      // publish the state only if the value changed or the refresh interval has expired
      // or if the last sent time is in the past (which can happen after a reset)
      _publish(false, config->component, config->device_topic, config->config_key, config->state_key, value, config->entity_category, config->device_class,
               config->state_class, config->unit_of_measurement, config->icon);
      config->lastSentMillis = millis();  // update the last sent time
    }
  }
}
