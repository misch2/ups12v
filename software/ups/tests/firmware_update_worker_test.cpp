#include <ArduinoJson.h>
#include <Update.h>
#include <esp_crt_bundle.h>
#include <esp_http_client.h>
#include <esp_ota_ops.h>
#include <mbedtls/sha256.h>

#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <deque>
#include <vector>

#include "firmware_update_esp32.h"

using namespace FirmwareUpdate;
unsigned long now = 0;
unsigned long millis() { return now; }
UpdateClass Update;
esp_partition_t slot{0x1e0000, 0x1f0000};
esp_partition_t running{0x1e0000, 0x10000};
const esp_partition_t* esp_ota_get_next_update_partition(const esp_partition_t*) { return &slot; }
const esp_partition_t* esp_ota_get_running_partition() { return &running; }
esp_err_t esp_crt_bundle_attach(void*) { return ESP_OK; }
bool wrongHash = false;
size_t digested = 0;
void mbedtls_sha256_init(mbedtls_sha256_context*) {}
void mbedtls_sha256_free(mbedtls_sha256_context*) {}
int mbedtls_sha256_starts(mbedtls_sha256_context* context, int is224) {
  assert(is224 == 0);
  context->bytes = 0;
  return 0;
}
int mbedtls_sha256_update(mbedtls_sha256_context* context, const uint8_t*, size_t count) {
  context->bytes += count;
  return 0;
}
int mbedtls_sha256_finish(mbedtls_sha256_context* context, uint8_t output[32]) {
  digested = context->bytes;
  std::memset(output, wrongHash ? 0xbb : 0xaa, 32);
  return 0;
}

struct Queue {
  size_t size;
  std::deque<std::vector<uint8_t>> values;
};
std::vector<Queue*> queues;
struct Blocked {};
TaskFunction_t workerTask = nullptr;
void* workerContext = nullptr;
QueueHandle_t xQueueCreate(unsigned length, unsigned size) {
  assert(length == 1);
  auto q = new Queue{size, {}};
  queues.push_back(q);
  return q;
}
BaseType_t xQueueSend(QueueHandle_t handle, const void* data, TickType_t) {
  auto& q = *static_cast<Queue*>(handle);
  if (!q.values.empty()) return 0;
  const auto bytes = static_cast<const uint8_t*>(data);
  q.values.emplace_back(bytes, bytes + q.size);
  return pdTRUE;
}
BaseType_t xQueueReceive(QueueHandle_t handle, void* data, TickType_t wait) {
  auto& q = *static_cast<Queue*>(handle);
  if (q.values.empty()) {
    if (wait == portMAX_DELAY) throw Blocked{};
    return 0;
  }
  std::memcpy(data, q.values.front().data(), q.size);
  q.values.pop_front();
  return pdTRUE;
}
BaseType_t xQueueOverwrite(QueueHandle_t handle, const void* data) {
  auto& q = *static_cast<Queue*>(handle);
  q.values.clear();
  return xQueueSend(handle, data, 0);
}
void vQueueDelete(QueueHandle_t handle) { delete static_cast<Queue*>(handle); }
BaseType_t xTaskCreate(TaskFunction_t task, const char*, uint32_t stack, void* context, unsigned, void*) {
  assert(stack > 0);
  workerTask = task;
  workerContext = context;
  return pdPASS;
}
void vTaskDelay(TickType_t ticks) { now += ticks; }
void runTask() {
  try {
    workerTask(workerContext);
  } catch (Blocked&) {
  }
}

struct HttpResponse {
  int status;
  std::string body;
  int64_t length;
  bool https;
  HttpResponse(int status, const std::string& body, int64_t length = -1, bool https = true) : status(status), body(body), length(length), https(https) {}
};
std::vector<HttpResponse> responses;
int opens = 0, clients = 0;
struct Http {
  size_t response = 0, position = 0;
};
esp_http_client_handle_t esp_http_client_init(const esp_http_client_config_t* config) {
  assert(config->crt_bundle_attach == esp_crt_bundle_attach && !config->skip_cert_common_name_check);
  assert(config->transport_type == HTTP_TRANSPORT_OVER_SSL && config->disable_auto_redirect);
  assert(std::strncmp(config->url, "https://", 8) == 0 && config->timeout_ms > 0);
  ++clients;
  return new Http;
}
esp_err_t esp_http_client_cleanup(esp_http_client_handle_t handle) {
  delete static_cast<Http*>(handle);
  --clients;
  return ESP_OK;
}
esp_err_t esp_http_client_open(esp_http_client_handle_t, int length) {
  assert(length == 0);
  ++opens;
  return ESP_OK;
}
int64_t esp_http_client_fetch_headers(esp_http_client_handle_t handle) {
  const auto& response = responses.at(static_cast<Http*>(handle)->response);
  return std::max(int64_t(0), response.length);
}
int esp_http_client_get_status_code(esp_http_client_handle_t handle) { return responses.at(static_cast<Http*>(handle)->response).status; }
int64_t esp_http_client_get_content_length(esp_http_client_handle_t handle) { return responses.at(static_cast<Http*>(handle)->response).length; }
esp_err_t esp_http_client_set_redirection(esp_http_client_handle_t handle) {
  auto& client = *static_cast<Http*>(handle);
  ++client.response;
  client.position = 0;
  return client.response < responses.size() ? ESP_OK : ESP_FAIL;
}
esp_err_t esp_http_client_close(esp_http_client_handle_t) { return ESP_OK; }
esp_http_client_transport_t esp_http_client_get_transport_type(esp_http_client_handle_t handle) {
  return responses.at(static_cast<Http*>(handle)->response).https ? HTTP_TRANSPORT_OVER_SSL : HTTP_TRANSPORT_OVER_TCP;
}
bool esp_http_client_is_complete_data_received(esp_http_client_handle_t handle) {
  const auto& client = *static_cast<Http*>(handle);
  const auto& response = responses.at(client.response);
  const size_t expected = response.length < 0 ? response.body.size() : response.length;
  return client.position >= expected;
}
int esp_http_client_read(esp_http_client_handle_t handle, char* bytes, int requested) {
  auto& client = *static_cast<Http*>(handle);
  const auto& response = responses.at(client.response);
  const size_t count = std::min(size_t(requested), response.body.size() - client.position);
  std::memcpy(bytes, response.body.data() + client.position, count);
  client.position += count;
  return count;
}
Candidate candidate() {
  Candidate offer;
  std::strcpy(offer.version, "20261126.1");
  std::strcpy(offer.url, "https://github.com/misch2/ups12v/releases/download/fw-20261126.1/ups_v4_esp32c3.bin");
  std::memset(offer.sha256, 'a', 64);
  offer.sha256[64] = 0;
  offer.size = 2048;
  return offer;
}
std::string manifest() {
  auto offer = candidate();
  JsonDocument doc;
  doc["schema"] = 1;
  doc["version"] = offer.version;
  doc["release_url"] = "https://github.com/misch2/ups12v/releases/tag/fw-20261126.1";
  doc["release_summary"] = "Worker test";
  auto value = doc["variants"]["ups_v4_esp32c3"].to<JsonObject>();
  value["hardware"]["version"] = "4.0";
  value["hardware"]["mcu"] = "esp32c3";
  value["hardware"]["power_path"] = "sys";
  value["url"] = offer.url;
  value["size"] = offer.size;
  value["sha256"] = offer.sha256;
  std::string text;
  serializeJson(doc, text);
  return text;
}

int main() {
  Esp32Backend backend(Hardware::kV4Esp32C3);
  assert(backend.begin());
  Result result;
  responses = {HttpResponse(200, manifest())};
  assert(backend.check() && !backend.poll(result));
  runTask();
  assert(backend.poll(result) && result.error == Error::NONE && std::strcmp(result.candidate.version, "20261126.1") == 0 && clients == 0);
  responses = {HttpResponse(404, "not deployed")};
  assert(backend.check());
  runTask();
  assert(backend.poll(result) && result.error == Error::NETWORK);
  responses = {HttpResponse(200, std::string(8193, 'x'))};
  assert(backend.check());
  runTask();
  assert(backend.poll(result) && result.error == Error::MANIFEST);
  responses = {HttpResponse(302, ""), HttpResponse(200, manifest(), -1, false)};
  opens = 0;
  assert(backend.check());
  runTask();
  assert(backend.poll(result) && result.error == Error::NETWORK && opens == 1);
  std::string image(2048, 0x11);
  image[0] = char(0xe9);
  image[12] = 5;
  image[13] = 0;
  for (int scenario = 0; scenario < 8; ++scenario) {
    Update = UpdateClass{};
    wrongHash = scenario == 1;
    digested = 0;
    Update.failWrite = scenario == 2;
    Update.failEnd = scenario == 3;
    Update.running = scenario == 7;
    responses = {HttpResponse(302, ""), HttpResponse(200, scenario == 4 ? image.substr(0, 1000) : image, scenario == 5 ? 2000 : scenario == 6 ? -1 : 2048)};
    assert(backend.install(candidate()) && !Update.selected);
    runTask();
    assert(backend.poll(result) && result.kind == JobKind::INSTALL && clients == 0);
    if (scenario == 0 || scenario == 6) {
      assert(result.error == Error::NONE && Update.selected && digested == image.size());
    } else {
      assert(result.error != Error::NONE && !Update.selected);
    }
    if (scenario == 7) assert(Update.running && Update.aborts == 0);  // Never abort another updater's transaction.
  }
  slot.size = 1000;
  Update = UpdateClass{};
  assert(backend.install(candidate()));
  runTask();
  assert(backend.poll(result) && result.error == Error::CAPACITY && Update.writes == 0);
  slot.size = 0x1e0000;
  slot.address = running.address;
  assert(backend.capacity() == 0 && backend.install(candidate()));
  runTask();
  assert(backend.poll(result) && result.error == Error::CAPACITY && Update.writes == 0);
  for (auto queue : queues) delete queue;
  std::puts("ESP worker: queued execution, TLS bundle/hostname checks, HTTPS redirects, 404/bounds, Update/SHA adapters, progress and failure cleanup passed");
  std::puts("firmware_update_worker: behavioral checks passed (SDK/RTOS/crypto/flash substituted; no live HTTPS or flash)");
}
