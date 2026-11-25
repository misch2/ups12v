#include "firmware_update_mqtt.h"

#include <cassert>
#include <cstdio>
#include <cstring>

unsigned long testNow = 0;
unsigned long millis() { return testNow; }
Logger::Logger(Syslog*, Stream*) {}
void Logger::log(uint16_t, const char*, ...) {}

using namespace FirmwareUpdate;
const char* firstSession = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const char* secondSession = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";

struct BackendStub : Backend {
  Result result;
  bool ready = false;
  bool progressReady = false;
  Progress currentProgress;
  int installs = 0;
  uint32_t slot = 4096;
  bool check() override { return true; }
  bool install(const Candidate&) override {
    ++installs;
    return true;
  }
  bool poll(Result& output) override {
    if (!ready) return false;
    ready = false;
    output = result;
    return true;
  }
  bool progress(Progress& output) override {
    if (!progressReady) return false;
    progressReady = false;
    output = currentProgress;
    return true;
  }
  uint32_t capacity() const override { return slot; }
  void offer() {
    result = Result{};
    std::strcpy(result.candidate.version, "20261125.8");
    std::strcpy(result.candidate.releaseUrl, "https://github.com/misch2/ups12v/releases/tag/fw-20261125.8");
    std::strcpy(result.candidate.summary, "Firmware with \"notes\"");
    result.candidate.size = 2048;
    ready = true;
  }
};
struct Controls : Control {
  Service& service;
  bool blocked = false;
  explicit Controls(Service& service) : service(service) {}
  Error validateInstall(const char* version) const override { return blocked ? Error::BUSY : service.validateInstall(version); }
  Error requestInstall(const char* version) override { return blocked ? Error::BUSY : service.requestInstall(version); }
  Error requestCheck() override {
    service.requestCheck();
    return Error::NONE;
  }
  Error cancel() override { return service.cancelQueuedInstall() ? Error::NONE : Error::BUSY; }
};
struct Fixture {
  BackendStub backend;
  Service service{backend, "20261125.7"};
  Controls controls{service};
  PubSubClient client;
  Logger logger{nullptr, nullptr};
  HomeAssistant::MQTT ha{client, logger};
  Mqtt mqtt{service, controls, ha};
  Fixture() {
    testNow = 0;
    assert(ha.beginDevice("test-ups", "4.0"));
    client.online = true;
    ha.setTransportAvailable(true);
    mqtt.connected(firstSession);
  }
  void checked() {
    service.tick(0, true, true, true);
    backend.offer();
    service.tick(1, true, true, true);
  }
  JsonDocument packet(bool config) {
    JsonDocument doc;
    for (auto i = client.packets.rbegin(); i != client.packets.rend(); ++i) {
      if ((i->topic.find("homeassistant/") == 0) == config) {
        assert(!deserializeJson(doc, i->payload));
        return doc;
      }
    }
    assert(false);
    return doc;
  }
  std::string command() { return packet(true)["payload_install"].as<std::string>(); }
  void send(const std::string& command) {
    assert(mqtt.handleCommand(mqtt.commandTopic().c_str(), reinterpret_cast<const uint8_t*>(command.data()), command.size()));
  }
};

void discoveryAndUnknown() {
  Fixture f;
  f.ha.setTransportAvailable(false);
  const int accesses = f.client.accesses;
  f.mqtt.publish();
  assert(f.client.accesses == accesses && f.client.packets.empty());
  f.ha.setTransportAvailable(true);
  f.mqtt.publish();
  auto config = f.packet(true);
  assert(config["unique_id"] == "test-ups_firmware_update");
  assert(config["default_entity_id"] == "update.test_ups_firmware_update");
  assert(config["device"]["identifiers"][0] == "test-ups");
  assert(config["device_class"] == "firmware" && config["entity_category"] == "config");
  assert(config["availability_mode"] == "all");
  assert(config["availability"][0]["topic"] == "bq25798ups/test-ups/availability");
  assert(config["availability"][1]["topic"] == "bq25798ups/test-ups/state/firmware_update");
  assert(config["value_template"] == "{{ value_json.update | to_json }}");
  assert(!config["command_topic"].is<const char*>() && !config["force_update"].is<bool>());
  auto state = f.packet(false);
  assert(state["update"]["installed_version"] == "20261125.7");
  assert(!state["details"]["checked"].as<bool>() && !state["update"]["latest_version"].is<const char*>());
  assert(state["update"]["update_percentage"].isNull());
  assert(f.backend.installs == 0);
  assert(f.ha.publishAvailability(true));
  assert(f.client.packets.back().topic == "bq25798ups/test-ups/availability" && f.client.packets.back().payload == "online");
  assert(f.ha.publishChargerAvailability(false));
  assert(f.client.packets.back().topic == "bq25798ups/test-ups/charger/availability" && f.client.packets.back().payload == "offline");
}

void explicitVersionAndSession() {
  Fixture f;
  f.checked();
  f.mqtt.publish();
  const auto command = f.command();
  assert(command == std::string("INSTALL 20261125.8 ") + firstSession);
  assert(f.packet(true)["retain"] == false);
  const auto count = f.client.packets.size();
  f.mqtt.publish();
  assert(count == f.client.packets.size());
  f.send("INSTALL");
  f.send(command + " trailing");
  f.send(std::string("INSTALL 20261125.9 ") + firstSession);
  assert(!f.service.reserved() && f.service.commandError() == Error::VERSION);
  f.controls.blocked = true;
  f.send(command);
  assert(!f.service.reserved() && f.service.commandError() == Error::BUSY);
  f.mqtt.publish();
  assert(!f.packet(true)["command_topic"].is<const char*>());
  f.controls.blocked = false;
  f.mqtt.connected(secondSession);
  f.send(command);
  assert(!f.service.reserved());
  f.mqtt.publish();
  f.send(command);
  assert(!f.service.reserved());
  const auto fresh = f.command();
  assert(fresh == std::string("INSTALL 20261125.8 ") + secondSession);
  f.send(fresh);
  assert(f.service.state() == State::INSTALL_QUEUED && f.backend.installs == 0);
  f.send(fresh);
  assert(f.service.commandError() == Error::BUSY);
  f.service.tick(2, true, true, true);
  assert(f.backend.installs == 1);
  f.backend.currentProgress.bytes = 1024;
  f.backend.currentProgress.total = 2048;
  f.backend.progressReady = true;
  f.service.tick(3, true, true, true);
  f.mqtt.publish();
  auto state = f.packet(false);
  assert(state["update"]["in_progress"] == true && state["update"]["update_percentage"] == 50);
  const auto progressPackets = f.client.packets.size();
  f.backend.currentProgress.bytes = 1536;
  f.backend.progressReady = true;
  f.service.tick(4, true, true, true);
  testNow = 100;
  f.mqtt.publish();
  assert(f.client.packets.size() == progressPackets);
  testNow = 1000;
  f.mqtt.publish();
  assert(f.packet(false)["update"]["update_percentage"] == 75);
  f.backend.result = Result{};
  f.backend.result.kind = JobKind::INSTALL;
  f.backend.result.error = Error::HASH;
  f.backend.ready = true;
  f.service.tick(5, true, true, true);
  f.mqtt.publish();
  state = f.packet(false);
  assert(!state["update"]["in_progress"].as<bool>() && state["update"]["update_percentage"].isNull());
  assert(state["details"]["error"] == "SHA-256 mismatch" && !f.service.rebootPending());
}

void currentAndCompletion() {
  Fixture current;
  current.service.tick(0, true, true, true);
  current.backend.offer();
  std::strcpy(current.backend.result.candidate.version, "20261125.6");
  current.service.tick(1, true, true, true);
  current.mqtt.publish();
  assert(current.packet(false)["update"]["latest_version"] == "20261125.7");
  assert(!current.packet(true)["command_topic"].is<const char*>());
  Fixture unavailable;
  unavailable.service.workerUnavailable();
  unavailable.mqtt.publish();
  assert(!unavailable.packet(false)["details"]["checked"].as<bool>());
  assert(unavailable.packet(false)["details"]["error"] == "update worker unavailable");
  Fixture success;
  success.checked();
  success.mqtt.publish();
  success.send(success.command());
  success.service.tick(2, true, true, true);
  success.backend.result = Result{};
  success.backend.result.kind = JobKind::INSTALL;
  success.backend.ready = true;
  success.service.tick(3, true, true, true);
  success.mqtt.publish();
  assert(success.service.rebootPending());
  assert(success.packet(false)["update"]["in_progress"] == true && success.packet(false)["update"]["update_percentage"] == 100);
}

void retryCapacityAndStaleOffer() {
  Fixture f;
  f.checked();
  f.client.acceptPublish = false;
  f.mqtt.publish();
  assert(f.client.packets.empty());
  f.send(std::string("INSTALL 20261125.8 ") + firstSession);
  assert(!f.service.reserved());
  f.client.acceptPublish = true;
  f.mqtt.publish();
  const auto published = f.client.packets.size();
  f.client.acceptPublish = false;
  f.service.recordCommandResult(Error::BUSY);
  f.mqtt.publish();
  assert(f.client.packets.size() == published);
  f.client.acceptPublish = true;
  f.mqtt.publish();
  assert(f.packet(false)["details"]["command_error"] == "update busy");
  auto old = f.command();
  f.service.requestCheck();
  f.service.tick(5, true, true, true);
  f.backend.offer();
  std::strcpy(f.backend.result.candidate.version, "20261125.9");
  f.service.tick(6, true, true, true);
  // State advanced before discovery refresh: the advertised old version cannot install the new offer.
  f.send(old);
  assert(!f.service.reserved() && f.service.commandError() == Error::VERSION);
  f.backend.slot = 1024;
  f.mqtt.publish();
  assert(!f.packet(true)["command_topic"].is<const char*>());
  assert(f.packet(false)["update"]["latest_version"] == "20261125.9");
  f.mqtt.connected(nullptr);
  f.backend.slot = 4096;
  f.mqtt.publish();
  assert(!f.packet(true)["command_topic"].is<const char*>());
  assert(!f.mqtt.handleCommand("unrelated/topic", nullptr, 0));
}

int main() {
  discoveryAndUnknown();
  explicitVersionAndSession();
  retryCapacityAndStaleOffer();
  currentAndCompletion();
  std::puts(
      "MQTT firmware: actual discovery/state JSON, availability, exact version/session commands, reconnect replay rejection, progress/errors and retry passed");
}
