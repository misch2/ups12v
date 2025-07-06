#include "homeassistant_mqtt.h"

namespace HomeAssistant {

String MQTT::getConfigTopic(EntityConfig* config) {
  if (config == nullptr) {
    return "";
  };
  return "homeassistant/" + config->base.component + "/" + deviceName + "/" + config->base.config_key + "/config";
};

String MQTT::getStateTopic(EntityConfig* config) {
  if (config == nullptr) {
    return "";
  };
  return "bq25798ups/" + deviceName + "/state/" + config->base.state_key;
};

String MQTT::getCommandTopic(EntityConfig* config) {
  if (config == nullptr) {
    return "";
  };
  return "bq25798ups/" + deviceName + "/command/" + config->base.state_key;
};

void MQTT::_publish(bool isConfiguration, EntityConfig* config, String value) {
  if (config == nullptr || mqttClient == nullptr || logger == nullptr) {
    logger->log(LOG_ERR, "Invalid parameters for MQTT publish");
    return;
  }

  String config_topic = getConfigTopic(config);
  String state_topic = getStateTopic(config);
  String command_topic = getCommandTopic(config);

  const EntityBaseConfig& base = config->base;

  if (isConfiguration) {
    // create HomeAssistant config JSON
    if (base.component == "") {
      logger->log(LOG_ERR, "Component is empty for %s, cannot publish HomeAssistant config", base.config_key.c_str());
      return;
    }

    JsonDocument doc;
    doc["state_topic"] = state_topic;
    doc["device"]["manufacturer"] = "Michal";
    doc["device"]["model"] = "UPS";
    doc["device"]["hw_version"] = "1.0";
    doc["device"]["sw_version"] = FIRMWARE_VERSION;

    JsonArray identifiers = doc["device"]["identifiers"].to<JsonArray>();
    identifiers.add(deviceName);
    doc["device"]["name"] = deviceName;
    doc["enabled_by_default"] = true;
    doc["entity_category"] = base.entity_category;
    if (base.device_class != "") {
      doc["device_class"] = base.device_class;
    }
    if (base.state_class != "") {
      doc["state_class"] = base.state_class;
    }
    if (base.unit_of_measurement != "") {
      doc["unit_of_measurement"] = base.unit_of_measurement;
    }
    if (base.icon != "") {
      doc["icon"] = base.icon;
    }
    doc["force_update"] = true;   // force update the entity state on every publish
    doc["expire_after"] = "300";  // expire after 5 minutes
    if (base.name != "") {
      doc["name"] = base.name;  // use the provided name if available
    } else {
      doc["name"] = base.config_key;  // otherwise use the config key as the name
    }
    doc["unique_id"] = deviceName + "_" + base.config_key;

    if (base.component == "binary_sensor") {
      doc["payload_on"] = "ON";
      doc["payload_off"] = "OFF";
    } else if (base.component == "text") {
      doc["command_topic"] = command_topic;
    } else if (base.component == "button") {
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

void MQTT::publishConfiguration(EntityConfig* config) {
  if (config != nullptr) {
    _publish(true, config, "");
  }
}
void MQTT::publishStateIfNeeded(EntityConfig* config, String value, bool force) {
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

}  // namespace HomeAssistant