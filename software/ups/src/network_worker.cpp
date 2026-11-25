#include "network_worker.h"

#include <cstring>

namespace UpsNetwork {
bool ConnectionWorker::begin(const char* id, const char* topic) {
  if (jobs || !id || !id[0] || !topic || !topic[0]) return false;
  clientId = id;
  availabilityTopic = topic;
  if (clientId.length() != std::strlen(id) || availabilityTopic.length() != std::strlen(topic)) return false;
  jobs = xQueueCreate(1, sizeof(bool));
  results = xQueueCreate(1, sizeof(ConnectResult));
  if (jobs && results && xTaskCreate(task, "ups-connect", 4096, this, 1, nullptr) == pdPASS) return true;
  if (jobs) vQueueDelete(jobs);
  if (results) vQueueDelete(results);
  jobs = results = nullptr;
  return false;
}

bool ConnectionWorker::start(bool resolveSyslog) { return jobs && xQueueSend(jobs, &resolveSyslog, 0) == pdTRUE; }
bool ConnectionWorker::poll(ConnectResult& result) { return results && xQueueReceive(results, &result, 0) == pdTRUE; }

void ConnectionWorker::task(void* context) {
  auto& worker = *static_cast<ConnectionWorker*>(context);
  for (;;) {
    bool resolveSyslog;
    if (xQueueReceive(worker.jobs, &resolveSyslog, portMAX_DELAY) == pdTRUE) {
      const auto result = worker.connect(resolveSyslog);
      xQueueSend(worker.results, &result, portMAX_DELAY);
    }
  }
}

ConnectResult ConnectionWorker::connect(bool resolveSyslog) {
  ConnectResult result = {};
  const uint32_t started = millis();
  IPAddress address;
  // No application logger, I2C, HA publisher, callbacks or mutable settings in this task.
  if (resolveSyslog && settings.network.syslog.serverHostname.length() &&
      WiFi.hostByName(settings.network.syslog.serverHostname.c_str(), address)) {
    result.syslogIP = static_cast<uint32_t>(address);
  }
  address = IPAddress();
  if (WiFi.hostByName(settings.network.mqtt.serverHostname.c_str(), address) && static_cast<uint32_t>(address) != 0) {
    result.brokerResolved = true;
    result.brokerIP = static_cast<uint32_t>(address);
    mqtt.setServer(address, settings.network.mqtt.serverPort);
    result.connected = mqtt.connect(clientId.c_str(), settings.network.mqtt.user.c_str(), settings.network.mqtt.password.c_str(),
                                    availabilityTopic.c_str(), 0, true, "offline");
  }
  result.mqttState = mqtt.state();
  if (!result.connected) socket.stop();
  result.elapsed = uint32_t(millis() - started);
  return result;
}
}  // namespace UpsNetwork
