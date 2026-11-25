#include <ArduinoJson.h>
#include <esp_wifi.h>
#include <lwip/sockets.h>

#include <algorithm>
#include <cassert>
#include <cerrno>
#include <cstdio>
#include <cstring>

#include "config_web_server.h"
#include "wifi_settings_esp32.h"

using Settings::Status;
const std::string kToken = "0123456789abcdef0123456789abcdef";
uint32_t clockNow = 0;
unsigned long millis() { return clockNow; }
uint32_t esp_random() { return 0x12345678; }
NetworkManager Network;
WiFiClass WiFi;
int WiFiServer::nextClient = -1;

wifi_config_t sdkConfig;
bool failSdk = false;
int sdkWrites = 0;
esp_err_t esp_wifi_get_config(int interface, wifi_config_t* config) {
  assert(interface == WIFI_IF_STA);
  if (failSdk) return ESP_FAIL;
  *config = sdkConfig;
  return ESP_OK;
}
esp_err_t esp_wifi_set_config(int interface, wifi_config_t* config) {
  assert(interface == WIFI_IF_STA);
  if (failSdk) return ESP_FAIL;
  sdkConfig = *config;
  ++sdkWrites;
  return ESP_OK;
}
esp_err_t esp_wifi_set_storage(int storage) { assert(storage == WIFI_STORAGE_FLASH); return failSdk ? ESP_FAIL : ESP_OK; }

std::string incoming, outgoing;
int socketCalls = 0, backpressure = 0;
int recv(int socket, char* buffer, size_t length, int flags) {
  assert(socket == 42 && flags == MSG_DONTWAIT);
  ++socketCalls;
  if (incoming.empty()) { errno = EAGAIN; return -1; }
  const auto count = std::min(length, incoming.size());
  std::memcpy(buffer, incoming.data(), count);
  incoming.erase(0, count);
  return static_cast<int>(count);
}
int send(int socket, const char* buffer, size_t length, int flags) {
  assert(socket == 42 && flags == MSG_DONTWAIT && length <= 1024);
  ++socketCalls;
  if (backpressure > 0) { --backpressure; errno = EAGAIN; return -1; }
  const auto count = std::min(length, size_t(512));
  outgoing.append(buffer, count);
  return static_cast<int>(count);
}

struct Backend : Settings::Backend {
  std::string record;
  bool fail = false;
  Settings::Result read(std::string& output) override {
    if (record.empty()) return {Status::MISSING};
    output = record;
    return {Status::OK};
  }
  Settings::Result write(const std::string& value) override {
    if (fail) return {Status::STORAGE_ERROR};
    record = value;
    return {Status::OK};
  }
};

RuntimeSettings example() {
  RuntimeSettings config;
  config.network.mqtt.haDeviceName = "test-ups";
  config.network.mqtt.user = "PRIVATE_MQTT_USERNAME";
  config.network.mqtt.password = "PRIVATE_MQTT_PASSWORD";
  config.battery.cell.name = "Cell \"quoted\" <script>alert(1)</script> & test";
  config.battery.cell.approx80PercentCapacity_mV = 3955;
  config.battery.pack.maxChargeCurrent_mA = 700;
  config.power.charger.chargeProfile.mode = ChargeControl::Mode::APPROX_80;
  return config;
}
struct Application : Settings::Application {
  int calls = 0;
  Settings::ApplyState outcome = Settings::ApplyState::APPLIED;
  Settings::ApplyResult apply(const RuntimeSettings&) override { ++calls; return {outcome, "simulated charger outcome"}; }
};
struct Fixture {
  const Hardware::Profile hardware;
  RuntimeSettings active = example();
  Backend backend, pendingBackend;
  Settings::Store store{backend, hardware};
  Settings::Service service{store, hardware, active};
  Settings::Esp32WifiDriver driver;
  Settings::WifiStore wifi{pendingBackend, driver};
  ConfigWeb::Controller controller{service, hardware, active, wifi};
  Application application;
  explicit Fixture(const Hardware::Profile& profile = Hardware::kV4Esp32C3) : hardware(profile) {
    sdkConfig = wifi_config_t{};
    std::memcpy(sdkConfig.sta.ssid, "OLD_NETWORK", 11);
    std::memcpy(sdkConfig.sta.password, "PRIVATE_WIFI_PASSWORD", 21);
    failSdk = false;
    sdkWrites = 0;
    assert(store.seedIfMissing(active).ok() && service.begin().ok());
    service.tick(application, 0);
    controller.begin(kToken);
  }
  ConfigWeb::Response get(const char* path = "/") {
    ConfigWeb::Request request;
    request.method = "GET"; request.path = path; request.host = "test-ups.local";
    return controller.handle(request, "test-ups", "192.0.2.4", {4, true});
  }
};

std::string url(const std::string& text) {
  const char* digits = "0123456789ABCDEF";
  std::string encoded;
  for (unsigned char c : text) {
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '.' || c == '_') encoded += c;
    else { encoded += '%'; encoded += digits[c >> 4]; encoded += digits[c & 15]; }
  }
  return encoded;
}
ConfigWeb::Request post(Fixture& fixture, const std::string& path, const std::string& fields = "") {
  ConfigWeb::Request request;
  request.method = "POST"; request.path = path; request.host = "test-ups.local";
  request.origin = "http://test-ups.local";
  request.contentType = "application/x-www-form-urlencoded";
  request.body = "token=" + kToken + "&revision=" + std::to_string(fixture.service.status().desiredRevision) + fields;
  return request;
}
ConfigWeb::Response submit(Fixture& fixture, const std::string& path, const std::string& fields = "") {
  return fixture.controller.handle(post(fixture, path, fields), "test-ups", "192.0.2.4", {4, true});
}
void noCredentials(const ConfigWeb::Response& response) {
  for (const auto secret : {"PRIVATE_MQTT_USERNAME", "PRIVATE_MQTT_PASSWORD", "PRIVATE_WIFI_PASSWORD", "REPLACEMENT_PASSWORD"}) {
    assert(response.body.find(secret) == std::string::npos);
  }
}

void forms() {
  Fixture f;
  auto page = f.get();
  assert(page.code == 200);
  noCredentials(page);
  assert(page.body.find("<script>") == std::string::npos && page.body.find("&lt;script&gt;") != std::string::npos);
  assert(page.body.find("name=\"power.output.VOTG_mV\"") == std::string::npos);
  assert(page.body.find("name=\"power.input.retryUnqualifiedAdapter\"") != std::string::npos);
  auto exported = f.get("/export");
  noCredentials(exported);
  assert(exported.attachment && exported.body.find("network.mqtt.password") == std::string::npos);
  assert(submit(f, "/save", "&battery.cell.name=Replacement").code == 200);
  assert(f.service.desired().battery.cell.name == "Replacement" && f.active.battery.cell.name != "Replacement");
  f.service.tick(f.application, 1);
  assert(f.active.battery.cell.name == "Replacement");
  const auto revision = f.service.status().desiredRevision;
  f.backend.fail = true;
  assert(submit(f, "/save", "&battery.cell.name=Failed").code == 400);
  assert(f.service.desired().battery.cell.name == "Replacement" && f.service.status().desiredRevision == revision);
  f.backend.fail = false;
  assert(submit(f, "/save", "&power.charger.chargeProfile.fullCell_mV=3900").code == 400);
  assert(submit(f, "/save", "&power.charger.chargeProfile.fullCell_mV=3900&battery.cell.approx80PercentCapacity_mV=3800").code == 200);
  f.application.outcome = Settings::ApplyState::DEFERRED;
  f.service.tick(f.application, 2);
  assert(f.get().body.find("Waiting for suitable") != std::string::npos);
  f.application.outcome = Settings::ApplyState::APPLIED;
  f.service.tick(f.application, 5002);
  assert(f.get().body.find("Applied and verified") != std::string::npos);
  assert(submit(f, "/save", "&mqtt_user=&mqtt_password=").code == 200);
  assert(f.service.desired().network.mqtt.password == "PRIVATE_MQTT_PASSWORD");
  auto changed = submit(f, "/save", "&mqtt_password=REPLACEMENT_PASSWORD");
  noCredentials(changed);
  assert(changed.code == 200 && f.service.status().restartRequired);
  assert(f.active.network.mqtt.password == "PRIVATE_MQTT_PASSWORD" && f.service.desired().network.mqtt.password == "REPLACEMENT_PASSWORD");
  assert(submit(f, "/save", "&mqtt_password=filled&clear_mqtt_password=1").code == 400);
  exported = f.get("/export");
  assert(submit(f, "/import", "&settings_json=" + url(exported.body)).code == 200);
  assert(f.service.desired().network.mqtt.password == "REPLACEMENT_PASSWORD");
  JsonDocument record;
  assert(!deserializeJson(record, exported.body));
  record["settings"]["network.mqtt.haDeviceName"] = "different-id";
  std::string wrong;
  serializeJson(record, wrong);
  assert(submit(f, "/import", "&settings_json=" + url(wrong)).code == 400);
  assert(submit(f, "/save", "&clear_mqtt_password=1").code == 200 && f.service.desired().network.mqtt.password.empty());
  for (const auto field : {"&power.input.IINDPM_mA=1501", "&power.charger.ICHG_mA=500x", "&temperatureSensor.beta=nan",
                           "&battery.pack.capacity_mAh=999999999999999", "&power.output.VOTG_mV=12000",
                           "&network.mqtt.haDeviceName=different-id", "&unknown=1", "&mqtt_password=%00", "&battery.cell.name=%Q0"}) {
    assert(submit(f, "/save", field).code == 400);
  }
  auto request = post(f, "/save");
  request.origin = "http://attacker.example";
  assert(f.controller.handle(request, "test-ups", "192.0.2.4", {}).code == 403);
  request = post(f, "/save"); request.fetchSite = "cross-site";
  assert(f.controller.handle(request, "test-ups", "192.0.2.4", {}).code == 403);
  request = post(f, "/save"); request.body += "&token=duplicate";
  assert(f.controller.handle(request, "test-ups", "192.0.2.4", {}).code == 400);
  request = post(f, "/save"); request.body.replace(6, 32, std::string(32, '0'));
  assert(f.controller.handle(request, "test-ups", "192.0.2.4", {}).code == 403);
  request = post(f, "/save"); request.host = "attacker.example";
  assert(f.controller.handle(request, "test-ups", "192.0.2.4", {}).code == 403);
  request = post(f, "/save"); request.body = "token=" + kToken + "&revision=0";
  assert(f.controller.handle(request, "test-ups", "192.0.2.4", {}).code == 409);
  request = post(f, "/save"); request.contentType = "application/json";
  assert(f.controller.handle(request, "test-ups", "192.0.2.4", {}).code == 415);
  const auto restart = submit(f, "/restart");
  assert(restart.restart && !f.controller.restartDue(1000));
  f.controller.responseSent(true, UINT32_MAX - 100);
  assert(!f.controller.restartDue(198) && f.controller.restartDue(199));
  std::puts("web: forms, escaping, export/import, credentials, validation, save/apply status, stale forms, "
            "token/origin/host checks and delayed restart passed");
}

void variantsAndCommissioning() {
  Fixture pmid(Hardware::kV1Esp32);
  const auto page = pmid.get();
  assert(page.body.find("name=\"power.output.VOTG_mV\"") != std::string::npos);
  assert(page.body.find("name=\"power.input.retryUnqualifiedAdapter\"") == std::string::npos);
  assert(submit(pmid, "/save", "&power.output.VOTG_mV=11900").code == 200);
  Backend backend;
  Settings::Store store(backend, Hardware::kV4Esp32C3);
  auto defaults = example();
  defaults.network.mqtt.haDeviceName = "default-ups";
  Settings::Service service(store, Hardware::kV4Esp32C3, defaults);
  ConfigWeb::Controller controller(service, Hardware::kV4Esp32C3, defaults, pmid.wifi);
  controller.begin(kToken);
  ConfigWeb::Request request;
  request.method = "POST"; request.path = "/save"; request.host = "192.0.2.4";
  request.contentType = "application/x-www-form-urlencoded";
  request.body = "token=" + kToken + "&revision=0&network.mqtt.haDeviceName=new-ups";
  assert(controller.handle(request, "ups-setup-example", "192.0.2.4", {}).code == 200);
  assert(service.desired().network.mqtt.haDeviceName == "new-ups" && service.status().restartRequired);
  request.method = "GET"; request.path = "/";
  const auto saved = controller.handle(request, "ups-setup-example", "192.0.2.4", {});
  assert(saved.body.find("value=\"new-ups\" readonly") != std::string::npos);
  std::puts("variants: applicable PMID/SYS fields and one-time LAN commissioning before restart passed");
}

void wifiChanges() {
  Fixture f;
  assert(submit(f, "/wifi", "&ssid=NEW_NETWORK&wifi_password=").code == 200 && sdkWrites == 0);
  Settings::WifiCredentials pending;
  assert(f.wifi.pending(pending).ok() && pending.ssid == "NEW_NETWORK" && pending.password == "PRIVATE_WIFI_PASSWORD");
  noCredentials(f.get());
  assert(submit(f, "/wifi/cancel").code == 200 && f.wifi.pending(pending).status == Status::MISSING);
  assert(submit(f, "/wifi", "&ssid=NEW_NETWORK&wifi_password=short").code == 400);
  assert(submit(f, "/wifi", "&ssid=NEW_NETWORK&wifi_password=REPLACEMENT_PASSWORD").code == 200);
  failSdk = true;
  assert(!f.wifi.applyAtBoot().ok() && f.wifi.pending(pending).ok());
  failSdk = false;
  assert(f.wifi.applyAtBoot().ok() && sdkWrites == 1 && f.wifi.pending(pending).status == Status::MISSING);
  assert(f.driver.read(pending).ok() && pending.ssid == "NEW_NETWORK" && pending.password == "REPLACEMENT_PASSWORD");
  assert(submit(f, "/wifi", "&ssid=OPEN_NETWORK&clear_wifi_password=1").code == 200);
  assert(f.wifi.applyAtBoot().ok() && f.driver.read(pending).ok() && pending.password.empty());
  f.pendingBackend.fail = true;
  assert(submit(f, "/wifi", "&ssid=NOT_SAVED&clear_wifi_password=1").code == 400);
  f.pendingBackend.fail = false;
  f.pendingBackend.record = "damaged";
  assert(!f.wifi.stage({"TEST", "password"}).ok() && f.pendingBackend.record == "damaged");
  assert(!f.wifi.cancel().ok());
  Backend backend;
  Settings::WifiStore store(backend, f.driver);
  assert(store.stage({std::string(32, 'S'), std::string(64, 'a')}).ok());
  assert(store.applyAtBoot().ok() && f.driver.read(pending).ok() && pending.ssid.size() == 32 && pending.password.size() == 64);
  assert(!Settings::WifiStore::validate({std::string(33, 'S'), "password"}).ok());
  std::puts("wifi: staging and SDK adapter, preserve/clear credentials, restart activation, readback, "
            "failed storage/SDK and protected records passed");
}

void requestsAndTransport() {
  ConfigWeb::RequestParser parser;
  const std::string get = "GET / HTTP/1.1\r\nHost: test-ups.local\r\n\r\n";
  for (char c : get) parser.append(&c, 1);
  assert(parser.complete() && parser.value().host == "test-ups.local");
  for (const auto wire : {"GET / HTTP/1.1\r\nHost: a\r\nHost: b\r\n\r\n", "POST /save HTTP/1.1\r\nHost: a\r\n\r\n",
                          "POST /save HTTP/1.1\r\nHost: a\r\nContent-Length: 30000\r\n\r\n",
                          "POST /save HTTP/1.1\r\nHost: a\r\nTransfer-Encoding: chunked\r\n\r\n",
                          "GET / HTTP/1.1\r\nHost: a\r\nContent-Length: 0\r\n\r\nextra"}) {
    parser.reset(); parser.append(wire, std::strlen(wire)); assert(parser.error());
  }
  parser.reset();
  const auto huge = "GET / HTTP/1.1\r\nHost: a\r\nX: " + std::string(2048, 'a');
  parser.append(huge.data(), huge.size()); assert(parser.error() == 431);
  Fixture f;
  ConfigWeb::LanServer server(f.controller);
  server.begin();
  WiFiServer::nextClient = 42;
  incoming = "GET / HTTP/1.1\r\nHost: 192.0.2.4\r\n\r\n";
  outgoing.clear(); backpressure = 4; clockNow = 0;
  int chargerTurns = 0;
  for (; clockNow < 4000; clockNow += 20) {
    socketCalls = 0;
    server.loop("test-ups", {4, true});
    assert(socketCalls <= 1);
    ++chargerTurns;
  }
  assert(outgoing.find("HTTP/1.1 200") == 0 && outgoing.find("</html>") != std::string::npos && chargerTurns == 200);
  assert(outgoing.find("Cache-Control: no-store") != std::string::npos);
  assert(outgoing.find("Referrer-Policy: same-origin\r\n") != std::string::npos);
  ConfigWeb::Response received;
  received.body = outgoing;
  noCredentials(received);
  outgoing.clear(); incoming = "GET / HTTP/1.1\r\nHost:"; WiFiServer::nextClient = 42;
  for (; clockNow < 10000; clockNow += 20) { socketCalls = 0; server.loop("test-ups", {}); assert(socketCalls <= 1); }
  assert(outgoing.empty());  // Incomplete client timed out while the owner loop kept running.
  incoming = "GET / HTTP/1.1\r\nHost: 192.0.2.4\r\n\r\n"; WiFiServer::nextClient = 42;
  for (; clockNow < 14000; clockNow += 20) server.loop("test-ups", {});
  assert(outgoing.find("HTTP/1.1 200") == 0);  // Next browser works after the abandoned request.
  std::puts("http: parser, bounds, malformed requests, LAN transport, backpressure, slow-client timeout and continued loop turns passed");
}

int main() {
  forms();
  variantsAndCommissioning();
  wifiChanges();
  requestsAndTransport();
  std::puts("config_web: all behavioral checks passed (network, Wi-Fi SDK, storage and charger dependencies simulated)");
}
