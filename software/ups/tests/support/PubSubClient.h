#pragma once

#include <vector>
#include "WiFi.h"

constexpr int MQTT_CONNECTION_TIMEOUT = -4;
constexpr int MQTT_CONNECTION_LOST = -3;
constexpr int MQTT_CONNECT_FAILED = -2;
constexpr int MQTT_DISCONNECTED = -1;
constexpr int MQTT_CONNECTED = 0;
constexpr int MQTT_CONNECT_BAD_PROTOCOL = 1;
constexpr int MQTT_CONNECT_BAD_CLIENT_ID = 2;
constexpr int MQTT_CONNECT_UNAVAILABLE = 3;
constexpr int MQTT_CONNECT_BAD_CREDENTIALS = 4;
constexpr int MQTT_CONNECT_UNAUTHORIZED = 5;

class PubSubClient {
 public:
  struct Packet { std::string topic; std::string payload; bool retained; };
  bool online = false;
  bool acceptConnection = true;
  bool acceptPublish = true;
  int accesses = 0;
  std::vector<Packet> packets;
  std::string clientId;
  std::string willTopic;
  bool connected() { ++accesses; return online; }
  int state() { ++accesses; return online ? MQTT_CONNECTED : MQTT_CONNECT_FAILED; }
  void setServer(IPAddress, int) { ++accesses; }
  bool connect(const char* id, const char*, const char*, const char* topic, uint8_t qos, bool retain, const char* will) {
    ++accesses;
    clientId = id;
    willTopic = topic;
    online = acceptConnection && qos == 0 && retain && std::string(will) == "offline";
    return online;
  }
  bool publish(const char* topic, const char* payload, bool retained) {
    ++accesses;
    if (!online || !acceptPublish) return false;
    packets.push_back(Packet{topic, payload, retained});
    return true;
  }
};
