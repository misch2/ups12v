#include "homeassistant_mqtt.h"

#include <cassert>
#include <cstdio>
#include <cstring>
#include <fstream>

unsigned long millis() { return 1000; }
Logger::Logger(Syslog*, Stream*) {}
void Logger::log(uint16_t, const char*, ...) {}

int main(int argc, char** argv) {
  Logger logger(nullptr, nullptr);
  PubSubClient transport;
  transport.online = true;
  HomeAssistant::MQTT mqtt(transport, logger);
  assert(mqtt.beginDevice("test-ups", "3.3b"));
  mqtt.setTransportAvailable(true);
  const char* components[] = {"sensor", "binary_sensor", "sensor", "switch", "text", "button", "update"};
  for (int i = 0; i < 7; ++i) {
    // Independent character buffers catch accidental pointer comparisons of borrowed metadata.
    char component[24], category[] = "config", enumClass[] = "enum";
    std::strcpy(component, components[i]);
    HomeAssistant::EntityBaseConfig base = {};
    base.component = component;
    base.config_key = String("entity_") + std::to_string(i).c_str();
    base.state_key = base.config_key + "_state";
    base.entity_category = category;
    base.device_class = i == 2 ? enumClass : i == 0 ? "voltage" : "";
    base.state_class = "measurement";
    base.unit_of_measurement = "mV";
    base.name = "Long immutable entity label";
    base.icon = "mdi:battery-charging";
    base.independentOfCharger = i == 6;
    HomeAssistant::EntityConfig entity(base, i == 0 ? 60000 : 0);
    if (i == 2) entity.options = {"First", "Second"};
    assert(mqtt.publishConfiguration(&entity));
    JsonDocument doc;
    assert(!deserializeJson(doc, transport.packets.back().payload));
    assert(doc["unique_id"].as<std::string>() == "test-ups_entity_" + std::to_string(i));
    assert(doc["state_topic"].as<std::string>() == "bq25798ups/test-ups/state/entity_" + std::to_string(i) + "_state");
    assert(doc["entity_category"] == (i < 3 ? "diagnostic" : "config"));
    assert(doc["name"] == "Long immutable entity label" && doc["icon"] == "mdi:battery-charging");
    assert(doc["availability"].size() == 2);
    if (i == 2) {
      assert(doc["options"].size() == 2 && doc["options"][1] == "Second");
      assert(doc["state_class"].isNull() && doc["unit_of_measurement"].isNull());
    }
    if (i == 0) assert(doc["force_update"] == true && doc["expire_after"] == 300);
    if (i == 3) assert(doc["optimistic"] == false && doc["payload_on"] == "ON" && doc["retain"] == false);
    if (i == 5) assert(doc["payload_press"] == "PRESS");
    if (i == 6) assert(doc["force_update"].isNull() && doc["availability"][1]["value_template"].is<const char*>());
    const auto count = transport.packets.size();
    mqtt.publishStateIfNeeded(&entity, "first");
    mqtt.publishStateIfNeeded(&entity, "first");
    assert(transport.packets.size() == count + 1);
    mqtt.publishStateIfNeeded(&entity, "second");
    assert(transport.packets.size() == count + 2);
  }
  HomeAssistant::EntityBaseConfig minimal = {};
  minimal.component = "sensor";
  minimal.config_key = minimal.state_key = "minimal";
  HomeAssistant::EntityConfig entity(minimal);
  assert(mqtt.publishConfiguration(&entity));
  JsonDocument doc;
  assert(!deserializeJson(doc, transport.packets.back().payload));
  assert(doc["name"] == "minimal");
  for (const char* field : {"icon", "device_class", "state_class", "entity_category", "unit_of_measurement"}) assert(doc[field].isNull());
  minimal.component = "";
  HomeAssistant::EntityConfig invalid(minimal);
  const auto count = transport.packets.size();
  assert(!mqtt.publishConfiguration(&invalid) && transport.packets.size() == count);
  if (argc == 2) {
    JsonDocument wire;
    auto packets = wire.to<JsonArray>();
    for (const auto& packet : transport.packets) {
      auto output = packets.add<JsonObject>();
      output["topic"] = packet.topic;
      output["retained"] = packet.retained;
      JsonDocument payload;
      if (deserializeJson(payload, packet.payload))
        output["payload"] = packet.payload;
      else
        output["payload"] = payload;
    }
    std::ofstream output(argv[1]);
    serializeJson(wire, output);
    assert(output.good());
  }
  std::puts("HA MQTT metadata: seven components, null optional fields, enum metadata, identities/topics and retained state cache passed");
}
