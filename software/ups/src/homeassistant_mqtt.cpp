#include "homeassistant_mqtt.h"

String HomeAssistant_MQTT::getConfigTopic(HomeAssistant_MQTT::EntityConfig* config) {
  if (config == nullptr || config->device_topic == "" || config->config_key == "") {
    return "";
  };
  return "homeassistant/" + config->component + "/" + config->device_topic + "/" + config->config_key + "/config";
};

String HomeAssistant_MQTT::getStateTopic(HomeAssistant_MQTT::EntityConfig* config) {
  if (config == nullptr || config->device_topic == "" || config->state_key == "") {
    return "";
  };
  return "bq25798ups/" + config->device_topic + "/state/" + config->state_key;
};

String HomeAssistant_MQTT::getCommandTopic(HomeAssistant_MQTT::EntityConfig* config) {
  if (config == nullptr || config->device_topic == "" || config->state_key == "") {
    return "";
  };
  return "bq25798ups/" + config->device_topic + "/command/" + config->state_key;
};

void HomeAssistant_MQTT::_publish(bool isConfiguration, HomeAssistant_MQTT::EntityConfig* config, String value) {
  if (config == nullptr || mqttClient == nullptr || logger == nullptr) {
    logger->log(LOG_ERR, "Invalid parameters for HomeAssistant_MQTT publish");
    return;
  }

  String config_topic = getConfigTopic(config);
  String state_topic = getStateTopic(config);
  String command_topic = getCommandTopic(config);

  if (isConfiguration) {
    // create HomeAssistant config JSON
    if (config->component == "") {
      logger->log(LOG_ERR, "Component is empty for %s, cannot publish HomeAssistant config", config->config_key.c_str());
      return;
    }

    JsonDocument doc;
    doc["state_topic"] = state_topic;
    doc["device"]["manufacturer"] = "Michal";
    doc["device"]["model"] = "UPS";
    doc["device"]["hw_version"] = "1.0";
    doc["device"]["sw_version"] = FIRMWARE_VERSION;

    JsonArray identifiers = doc["device"]["identifiers"].to<JsonArray>();
    identifiers.add(config->device_topic);
    doc["device"]["name"] = config->device_topic;
    doc["enabled_by_default"] = true;
    doc["entity_category"] = config->entity_category;
    if (config->device_class != "") {
      doc["device_class"] = config->device_class;
    }
    if (config->state_class != "") {
      doc["state_class"] = config->state_class;
    }
    if (config->unit_of_measurement != "") {
      doc["unit_of_measurement"] = config->unit_of_measurement;
    }
    if (config->icon != "") {
      doc["icon"] = config->icon;
    }
    doc["force_update"] = true;   // force update the entity state on every publish
    doc["expire_after"] = "300";  // expire after 5 minutes
    if (config->name != "") {
      doc["name"] = config->name;  // use the provided name if available
    } else {
      doc["name"] = config->config_key;  // otherwise use the config key as the name
    }
    doc["unique_id"] = config->device_topic + "_" + config->config_key;

    if (config->component == "binary_sensor") {
      doc["payload_on"] = "ON";
      doc["payload_off"] = "OFF";
    } else if (config->component == "text") {
      doc["command_topic"] = command_topic;
    } else if (config->component == "button") {
      doc["command_topic"] = command_topic;
      doc["payload_press"] = "PRESS";  // payload to send when the button is pressed
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
    _publish(true, config, "");
  }
}
void HomeAssistant_MQTT::publishStateIfNeeded(HomeAssistant_MQTT::EntityConfig* config, String value, bool force) {
  if (config != nullptr) {
    long now = millis();
    if (force || (now - config->lastSentMillis >= config->refreshInterval) || (now - config->lastSentMillis < 0)) {
      // publish the state only if the value changed or the refresh interval has expired
      // or if the last sent time is in the past (which can happen after a reset)
      _publish(false, config, value);
      config->lastSentMillis = millis();  // update the last sent time
    }
  }
}
