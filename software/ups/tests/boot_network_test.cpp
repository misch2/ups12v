#include <ArduinoJson.h>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <deque>
#include <vector>

#include "boot_settings.h"
#include "connection_state.h"
#include "homeassistant_mqtt.h"
#include "network_worker.h"

static unsigned long now = 0;
unsigned long millis() { return now; }
WiFiClass WiFi;
Logger::Logger(Syslog*, Stream*) {}
void Logger::log(uint16_t, const char*, ...) {}
void Logger::setSyslog(Syslog*) {}

struct Backend : Settings::Backend {
  bool missing = true;
  bool fail = false;
  int writes = 0;
  std::string record;
  Settings::Result read(std::string& output) override {
    if (fail) return {Settings::Status::STORAGE_ERROR};
    if (missing) return {Settings::Status::MISSING};
    output = record;
    return {Settings::Status::OK};
  }
  Settings::Result write(const std::string& value) override {
    ++writes;
    record = value;
    missing = false;
    return {Settings::Status::OK};
  }
};

RuntimeSettings configured(const char* id) {
  RuntimeSettings settings;
  settings.network.mqtt.haDeviceName = id;
  settings.battery.pack.maxChargeCurrent_mA = 700;
  settings.power.charger.ICHG_mA = 500;
  return settings;
}

void identityAndBoot() {
  const char* installed[] = {"esp18-bq25798-ups1", "esp27-bq25798-ups2", "esp19-bq25798-ups3", "esp76-bq25798-ups4",
                             "esp77-bq25798-ups5", "esp78-bq25798-ups6", "esp79-bq25798-ups7", "esp80-bq25798-ups8"};
  for (const auto* id : installed) assert(DeviceIdentity::validNew(id));
  for (const auto* id : {"", "default-ups", "DEFAULT-UPS", "-ups", "ups-", "ups/name", "ups+", "ups#", "ups name", "ups_name"}) {
    assert(!DeviceIdentity::validNew(id) && !DeviceIdentity::validStored(id));
  }
  assert(DeviceIdentity::validNew(std::string(31, 'a').c_str()));
  assert(!DeviceIdentity::validStored(std::string(32, 'a').c_str()));
  assert(!DeviceIdentity::validNew("UPS-Legacy") && DeviceIdentity::validStored("UPS-Legacy"));
  DeviceIdentity locked;
  assert(locked.bind(installed[0]) && locked.bind(installed[0]) && !locked.bind(installed[1]));
  assert(std::string(locked.value()) == installed[0]);

  Backend backend;
  Settings::Store store(backend, Hardware::kV4Esp32C3);
  RuntimeSettings defaults = configured(installed[4]);
  RuntimeSettings active = defaults;
  DeviceIdentity identity;
  assert(Settings::loadForBoot(store, defaults, active, identity).status == Settings::Status::SEEDED && backend.writes == 1);
  assert(std::string(identity.value()) == installed[4]);
  auto saved = configured("stored-ups");
  saved.power.input.IINDPM_mA = 1500;
  assert(Settings::encodePrivate(saved, Hardware::kV4Esp32C3, backend.record).ok());
  DeviceIdentity afterReboot;
  assert(Settings::loadForBoot(store, defaults, active, afterReboot).ok());
  assert(active.network.mqtt.haDeviceName == "stored-ups" && active.power.input.IINDPM_mA == 1500 && backend.writes == 1);
  assert(std::string(afterReboot.value()) == "stored-ups");

  for (const auto* invalid : {"default-ups", "invalid+id"}) {
    auto invalidSettings = configured(invalid);
    assert(Settings::encodePrivate(invalidSettings, Hardware::kV4Esp32C3, backend.record).ok());
    const std::string original = backend.record;
    DeviceIdentity rejected;
    assert(Settings::loadForBoot(store, defaults, active, rejected).status == Settings::Status::INVALID_SETTINGS);
    assert(!rejected.ready() && backend.record == original && backend.writes == 1);
  }

  const std::string blocked[] = {"{", "{\"schema\":2}", "{\"schema\":0}"};
  for (const auto& record : blocked) {
    backend.record = record;
    DeviceIdentity unconfigured;
    assert(!Settings::loadForBoot(store, defaults, active, unconfigured).ok());
    assert(!unconfigured.ready() && active.network.mqtt.haDeviceName == "stored-ups" && backend.record == record && backend.writes == 1);
  }
  assert(Settings::encodePrivate(defaults, Hardware::kV1Esp32, backend.record).ok());
  DeviceIdentity wrongHardware;
  assert(Settings::loadForBoot(store, defaults, active, wrongHardware).status == Settings::Status::HARDWARE_MISMATCH);
  backend.missing = true;
  RuntimeSettings blank;
  DeviceIdentity blankIdentity;
  assert(!Settings::loadForBoot(store, blank, active, blankIdentity).ok() && backend.writes == 1 && !blankIdentity.ready());
  backend.fail = true;
  assert(Settings::loadForBoot(store, defaults, active, blankIdentity).status == Settings::Status::STORAGE_ERROR && backend.writes == 1);
  std::puts("boot: saved settings authoritative, seed once, immutable identity, protected/blank/error paths passed");
}

HomeAssistant::EntityConfig voltage() {
  HomeAssistant::EntityBaseConfig base = {};
  base.component = "sensor";
  base.config_key = base.state_key = "VBAT_ADC";
  base.name = "Battery voltage";
  return HomeAssistant::EntityConfig(base);
}

void discovery() {
  Logger logger(nullptr, nullptr);
  PubSubClient transport;
  transport.online = true;
  HomeAssistant::MQTT client(transport, logger);
  auto entity = voltage();
  client.setTransportAvailable(true);
  client.publishConfiguration(&entity);
  client.publishStateIfNeeded(&entity, "12.3");
  assert(!client.publishChargerAvailability(true) && !client.removeConfiguration("sensor", "VBAT_ADC"));
  assert(transport.accesses == 0 && transport.packets.empty() && client.getConfigTopic(&entity).empty());
  assert(!client.beginDevice("default-ups", "4.0"));
  const char* ids[] = {"esp77-bq25798-ups5", "esp80-bq25798-ups8"};
  for (const auto* id : ids) {
    PubSubClient mqtt;
    mqtt.online = true;
    HomeAssistant::MQTT device(mqtt, logger);
    assert(device.beginDevice(id, "4.0"));
    device.publishConfiguration(&entity);
    assert(mqtt.accesses == 0);  // No client access during a connection attempt, despite a valid identity.
    device.setTransportAvailable(true);
    device.publishConfiguration(&entity);
    assert(mqtt.packets.size() == 1);
    assert(mqtt.packets.back().topic == std::string("homeassistant/sensor/") + id + "/VBAT_ADC/config");
    JsonDocument payload;
    assert(!deserializeJson(payload, mqtt.packets.back().payload));
    assert(payload["unique_id"].as<std::string>() == std::string(id) + "_VBAT_ADC");
    std::string prefix = id;
    for (char& c : prefix) if (c == '-') c = '_';
    assert(payload["default_entity_id"].as<std::string>() == "sensor." + prefix + "_vbat_adc");
    assert(payload["device"]["identifiers"][0].as<std::string>() == id);
    assert(payload["state_topic"].as<std::string>() == std::string("bq25798ups/") + id + "/state/VBAT_ADC");
    assert(payload["availability_mode"] == "all");
    assert(payload["availability"][0]["topic"].as<std::string>() == std::string("bq25798ups/") + id + "/availability");
    assert(payload["availability"][1]["topic"].as<std::string>() == std::string("bq25798ups/") + id + "/charger/availability");
    assert(!device.beginDevice("different-ups", "4.0") && device.beginDevice(id, "4.0"));
    device.setTransportAvailable(false);
    const int before = mqtt.accesses;
    device.publishConfiguration(&entity);
    device.publishStateIfNeeded(&entity, "13.0", true);
    device.removeConfiguration("sensor", "old");
    device.publishChargerAvailability(false);
    assert(mqtt.accesses == before);
  }
  std::puts("discovery: actual serializer preserves legacy topics/unique/default IDs; unconfigured and worker gates passed");
}

struct NativeQueue { unsigned itemSize; unsigned capacity; std::deque<std::vector<unsigned char>> messages; };
struct TaskWouldWait {};
static TaskFunction_t taskFunction = nullptr;
static void* taskContext = nullptr;
static bool rejectTask = false;
QueueHandle_t xQueueCreate(unsigned length, unsigned size) {
  auto* queue = new NativeQueue;
  queue->itemSize = size;
  queue->capacity = length;
  return queue;
}
BaseType_t xQueueSend(QueueHandle_t handle, const void* value, TickType_t) {
  auto& queue = *static_cast<NativeQueue*>(handle);
  if (queue.messages.size() >= queue.capacity) return 0;
  const auto* bytes = static_cast<const unsigned char*>(value);
  queue.messages.emplace_back(bytes, bytes + queue.itemSize);
  return pdTRUE;
}
BaseType_t xQueueReceive(QueueHandle_t handle, void* value, TickType_t wait) {
  auto& queue = *static_cast<NativeQueue*>(handle);
  if (queue.messages.empty()) {
    if (wait) throw TaskWouldWait();  // Host scheduler pauses a task waiting for its next job.
    return 0;
  }
  std::memcpy(value, queue.messages.front().data(), queue.itemSize);
  queue.messages.pop_front();
  return pdTRUE;
}
void vQueueDelete(QueueHandle_t handle) { delete static_cast<NativeQueue*>(handle); }
BaseType_t xTaskCreate(TaskFunction_t function, const char*, uint32_t, void* context, unsigned, void*) {
  if (rejectTask) return 0;
  taskFunction = function;
  taskContext = context;
  return pdPASS;
}
void runWorker() {
  try { taskFunction(taskContext); } catch (const TaskWouldWait&) {}
}

void cooperativeConnect() {
  UpsNetwork::ConnectionState state;
  assert(!state.mayStart(0, false, true) && !state.mayStart(0, true, false));
  assert(state.mayStart(0, true, true));
  PubSubClient mqtt;
  WiFiClient socket;
  auto settings = configured("stored-ups");
  Logger logger(nullptr, nullptr);
  HomeAssistant::MQTT publisher(mqtt, logger);
  assert(publisher.beginDevice("stored-ups", "4.0"));
  UpsNetwork::ConnectionWorker worker(mqtt, socket, settings);
  assert(worker.begin("stored-ups", publisher.getChargerAvailabilityTopic().c_str()));
  assert(!worker.begin("another-ups", "other/topic"));
  state.started(0);
  publisher.setTransportAvailable(false);
  assert(worker.start(true));
  auto entity = voltage();
  UpsNetwork::ConnectResult result;
  int chargerTicks = 0;
  for (now = 0; now < 10000; now += 20) {
    ++chargerTicks;
    assert(!state.mayStart(now, true, true, true) && !worker.poll(result));
    publisher.publishStateIfNeeded(&entity, "12.3", true);
  }
  assert(chargerTicks == 500 && mqtt.accesses == 0);  // Main work progresses while no connection result is available.
  runWorker();
  assert(worker.poll(result) && result.connected && result.brokerResolved && result.syslogIP != 0);
  state.completed(now, result.connected);
  publisher.setTransportAvailable(state.mainOwnsConnectedClient());
  publisher.publishStateIfNeeded(&entity, "12.3", true);
  assert(mqtt.clientId == "stored-ups" && mqtt.willTopic == "bq25798ups/stored-ups/charger/availability" && mqtt.packets.size() == 1);
  assert(!state.mayStart(now, true, true, true));
  state.disconnected();
  publisher.setTransportAvailable(false);
  assert(state.mayStart(now, true, true, true));
  state.started(now);
  WiFi.resolve = false;
  assert(worker.start(false));
  runWorker();
  assert(worker.poll(result) && !result.brokerResolved && !result.connected && socket.stops == 1);
  state.completed(0xfffff000U, false);
  assert(!state.mayStart(uint32_t(0xfffff000U + 59999U), true, true));
  assert(state.mayStart(uint32_t(0xfffff000U + 60000U), true, true));
  rejectTask = true;
  UpsNetwork::ConnectionWorker unavailable(mqtt, socket, settings);
  assert(!unavailable.begin("stored-ups", "availability") && !unavailable.start(false));
  std::puts("connection: production worker/queue handoff, continued main ticks, DNS failure, retry rollover and task failure passed");
}

int main() {
  identityAndBoot();
  discovery();
  cooperativeConnect();
  std::puts("boot_network: behavioral checks passed (platform services and scheduling simulated)");
}
