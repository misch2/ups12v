#include "homeassistant_mqtt.h"

#include <cstring>
#include <utility>

namespace HomeAssistant {

bool MQTT::beginDevice(const char* name, const char* version) {
  if (!DeviceIdentity::validStored(name) || !version) return false;
  if (identity.ready()) return deviceName == name && hwVersion == version;
  String ownedName = name;
  String ownedVersion = version;
  if (ownedName.length() != std::strlen(name) || ownedVersion.length() != std::strlen(version)) return false;
  if (!identity.bind(name)) return false;
  deviceName = std::move(ownedName);
  hwVersion = std::move(ownedVersion);
  return true;
}

const char* mqttStateDescription(int state) {
  switch (state) {
    case MQTT_CONNECTION_TIMEOUT:
      return "response timeout";
    case MQTT_CONNECTION_LOST:
      return "connection lost";
    case MQTT_CONNECT_FAILED:
      return "TCP connection failed";
    case MQTT_DISCONNECTED:
      return "disconnected";
    case MQTT_CONNECTED:
      return "connected";
    case MQTT_CONNECT_BAD_PROTOCOL:
      return "protocol rejected";
    case MQTT_CONNECT_BAD_CLIENT_ID:
      return "client ID rejected";
    case MQTT_CONNECT_UNAVAILABLE:
      return "broker unavailable";
    case MQTT_CONNECT_BAD_CREDENTIALS:
      return "credentials rejected";
    case MQTT_CONNECT_UNAUTHORIZED:
      return "not authorized";
    default:
      return "unknown state";
  }
}

String MQTT::getConfigTopic(EntityConfig* config) {
  if (config == nullptr || !identity.ready()) {
    return "";
  };
  return "homeassistant/" + config->base.component + "/" + deviceName + "/" + config->base.config_key + "/config";
};

String MQTT::getStateTopic(EntityConfig* config) {
  if (config == nullptr || !identity.ready()) {
    return "";
  };
  return "bq25798ups/" + deviceName + "/state/" + config->base.state_key;
};

String MQTT::getCommandTopic(EntityConfig* config) {
  if (config == nullptr || !identity.ready()) {
    return "";
  };
  return "bq25798ups/" + deviceName + "/command/" + config->base.state_key;
};

String MQTT::getChargerAvailabilityTopic() { return identity.ready() ? "bq25798ups/" + deviceName + "/charger/availability" : String(); }
String MQTT::getAvailabilityTopic() { return identity.ready() ? "bq25798ups/" + deviceName + "/availability" : String(); }
bool MQTT::publishAvailability(bool available) {
  return readyToPublish() && mqttClient->connected() && mqttClient->publish(getAvailabilityTopic().c_str(), available ? "online" : "offline", true);
}

bool MQTT::publishChargerAvailability(bool available) {
  return readyToPublish() && mqttClient->connected() && mqttClient->publish(getChargerAvailabilityTopic().c_str(), available ? "online" : "offline", true);
}

bool MQTT::_publish(bool isConfiguration, EntityConfig* config, String value, const char* payloadInstall) {
  if (!readyToPublish()) return false;
  if (config == nullptr || mqttClient == nullptr || logger == nullptr) {
    if (logger != nullptr) {
      logger->log(LOG_ERR, "Invalid parameters for MQTT publish");
    }
    return false;
  }

  String config_topic = getConfigTopic(config);
  String state_topic = getStateTopic(config);
  String command_topic = getCommandTopic(config);

  const EntityBaseConfig& base = config->base;

  if (isConfiguration) {
    // create HomeAssistant config JSON
    if (base.component == "") {
      logger->log(LOG_ERR, "Component is empty for %s, cannot publish HomeAssistant config", base.config_key.c_str());
      return false;
    }

    JsonDocument doc;
    doc["state_topic"] = state_topic;
    auto availability = doc["availability"].to<JsonArray>();
    availability.add<JsonObject>()["topic"] = getAvailabilityTopic();
    if (!base.independentOfCharger) availability.add<JsonObject>()["topic"] = getChargerAvailabilityTopic();
    if (base.component == "update") {
      auto checked = availability.add<JsonObject>();
      checked["topic"] = state_topic;
      checked["value_template"] = "{{ 'online' if value_json.details.checked else 'offline' }}";
    }
    doc["availability_mode"] = "all";
    doc["device"]["manufacturer"] = "Michal Schwarz";
    doc["device"]["model"] = deviceModel;
    doc["device"]["hw_version"] = hwVersion;
    doc["device"]["sw_version"] = FIRMWARE_VERSION;

    JsonArray identifiers = doc["device"]["identifiers"].to<JsonArray>();
    identifiers.add(deviceName);
    doc["device"]["name"] = deviceName;
    doc["enabled_by_default"] = true;
    if (base.entity_category != "") {
      // Read-only entities may expose configuration values, but HA only accepts diagnostic here.
      const bool isSensor = base.component == "sensor" || base.component == "binary_sensor";
      doc["entity_category"] = isSensor && base.entity_category == "config" ? "diagnostic" : base.entity_category;
    }
    if (base.device_class != "") {
      doc["device_class"] = base.device_class;
    }
    if (base.device_class == "enum") {
      JsonArray options = doc["options"].to<JsonArray>();
      for (const String& option : config->options) {
        options.add(option);
      }
    }
    if (base.device_class != "enum" && base.state_class != "") {
      doc["state_class"] = base.state_class;
    }
    if (base.device_class != "enum" && base.unit_of_measurement != "") {
      doc["unit_of_measurement"] = base.unit_of_measurement;
    }
    if (base.icon != "") {
      doc["icon"] = base.icon;
    }
    if (base.component != "update") doc["force_update"] = config->refreshInterval > 0;
    if (config->refreshInterval > 0) {
      doc["expire_after"] = 300;
    }
    if (config->suggestedDisplayPrecision >= 0) {
      doc["suggested_display_precision"] = config->suggestedDisplayPrecision;
    }
    if (base.name != "") {
      doc["name"] = base.name;  // use the provided name if available
    } else {
      doc["name"] = base.config_key;  // otherwise use the config key as the name
    }
    doc["unique_id"] = deviceName + "_" + base.config_key;
    // Keep initial HA entity IDs independent of display names; existing registry IDs are preserved.
    String entityId = deviceName + "_" + base.config_key;
    entityId.toLowerCase();
    for (unsigned int i = 0; i < entityId.length(); i++) {
      const char c = entityId[i];
      if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_')) {
        entityId[i] = '_';
      }
    }
    doc["default_entity_id"] = base.component + "." + entityId;

    if (base.component == "binary_sensor" || base.component == "switch") {
      doc["payload_on"] = "ON";
      doc["payload_off"] = "OFF";
      if (base.component == "switch") {
        doc["command_topic"] = command_topic;
        doc["retain"] = false;
        doc["optimistic"] = false;
      }
    } else if (base.component == "text") {
      doc["command_topic"] = command_topic;
    } else if (base.component == "update") {
      doc["value_template"] = "{{ value_json.update | to_json }}";
      doc["json_attributes_topic"] = state_topic;
      doc["json_attributes_template"] = "{{ value_json.details | to_json }}";
      doc["retain"] = false;
      if (payloadInstall && *payloadInstall) {
        doc["command_topic"] = command_topic;
        doc["payload_install"] = payloadInstall;
      }
    } else if (base.component == "button") {
      doc["command_topic"] = command_topic;
      doc["payload_press"] = "PRESS";  // payload to send when the button is pressed
    }

    String serialized;
    serializeJson(doc, serialized);
    if (!mqttClient->publish(config_topic.c_str(), serialized.c_str(),
                             true))  // publish as retained, to survive HA restart
    {
      logger->log(LOG_ERR, "Failed to publish HomeAssistant config for %s: state=%d (%s)", config_topic.c_str(), mqttClient->state(),
                  mqttStateDescription(mqttClient->state()));
      return false;
    }
  } else {
    // Just publish the state value
    // Keep change-only values available after an HA restart without periodic traffic.
    if (!mqttClient->publish(state_topic.c_str(), value.c_str(), true)) {
      logger->log(LOG_ERR, "Failed to publish HomeAssistant state for %s: state=%d (%s)", state_topic.c_str(), mqttClient->state(),
                  mqttStateDescription(mqttClient->state()));
      return false;
    }
  }
  return true;
}

void MQTT::setDeviceModel(String model) { this->deviceModel = model; }

bool MQTT::removeConfiguration(String component, String configKey) {
  if (!readyToPublish()) return false;
  const String topic = "homeassistant/" + component + "/" + deviceName + "/" + configKey + "/config";
  if (!mqttClient->publish(topic.c_str(), "", true)) {
    logger->log(LOG_ERR, "Failed to remove HomeAssistant config for %s", topic.c_str());
    return false;
  }
  return true;
}

bool MQTT::publishConfiguration(EntityConfig* config, const char* payloadInstall) {
  if (config != nullptr) {
    if (_publish(true, config, "", payloadInstall)) {
      config->hasSentState = false;  // Repopulate all states after reconnect/recovery.
      return true;
    }
  }
  return false;
}
void MQTT::publishStateIfNeeded(EntityConfig* config, String value, bool force) {
  if (readyToPublish() && config != nullptr && mqttClient != nullptr && mqttClient->connected()) {
    const unsigned long now = millis();
    const bool refreshDue = config->refreshInterval > 0 && now - config->lastSentMillis >= config->refreshInterval;
    if (force || !config->hasSentState || value != config->lastSentValue || refreshDue) {
      if (_publish(false, config, value)) {
        config->lastSentMillis = millis();  // Update only after a successful publish.
        config->lastSentValue = value;
        config->hasSentState = true;
      }
    }
  }
}

}  // namespace HomeAssistant
