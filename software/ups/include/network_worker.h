#pragma once

#include <PubSubClient.h>
#include <WiFi.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include <freertos/task.h>

#include "runtime_settings.h"

namespace UpsNetwork {
struct ConnectResult {
  bool brokerResolved;
  bool connected;
  uint32_t brokerIP;
  uint32_t syslogIP;
  int mqttState;
  uint32_t elapsed;
};

// Queue handoff gives the worker exclusive MQTT/socket access until poll() receives a result.
// Settings and identity remain immutable for this worker's lifetime.
class ConnectionWorker {
 public:
  ConnectionWorker(PubSubClient& mqtt, WiFiClient& socket, const RuntimeSettings& settings)
      : mqtt(mqtt), socket(socket), settings(settings) {}
  bool begin(const char* clientId, const char* availabilityTopic);
  bool start(bool resolveSyslog);
  bool poll(ConnectResult& result);

 private:
  static void task(void* context);
  ConnectResult connect(bool resolveSyslog);
  PubSubClient& mqtt;
  WiFiClient& socket;
  const RuntimeSettings& settings;
  String clientId;
  String availabilityTopic;
  QueueHandle_t jobs = nullptr;
  QueueHandle_t results = nullptr;
};
}  // namespace UpsNetwork
