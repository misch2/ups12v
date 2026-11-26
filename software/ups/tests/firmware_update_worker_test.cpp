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

// SDK adapter test only: real trust-bundle data is covered by the offline asset tests.
esp_err_t esp_crt_bundle_attach(void*) { return ESP_OK; }

using namespace FirmwareUpdate;
unsigned long now = 0;
unsigned long millis() { return now; }
UpdateClass Update;
esp_partition_t slot{0x1e0000, 0x1f0000};
esp_partition_t running{0x1e0000, 0x10000};
const esp_partition_t* esp_ota_get_next_update_partition(const esp_partition_t*) { return &slot; }
const esp_partition_t* esp_ota_get_running_partition() { return &running; }
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
  std::string requestTarget = "/";
  HttpResponse(int status, const std::string& body, int64_t length = -1, bool https = true) : status(status), body(body), length(length), https(https) {}
};
std::vector<HttpResponse> responses;
int opens = 0, clients = 0;
int connectionDelay = 0;
int openError = ESP_OK, tlsSdkError = 0, tlsError = 0, verifyFlags = 0, socketError = 0, readError = 0;
int readTimeoutsAfterData = 0;
struct Http {
  size_t response = 0, position = 0;
  int timeout = 0, txBufferSize = 0;
};
esp_http_client_handle_t esp_http_client_init(const esp_http_client_config_t* config) {
  assert(config->cert_pem == nullptr && config->crt_bundle_attach == esp_crt_bundle_attach && !config->skip_cert_common_name_check);
  assert(config->transport_type == HTTP_TRANSPORT_OVER_SSL && config->disable_auto_redirect);
  assert(std::strncmp(config->url, "https://", 8) == 0 && config->timeout_ms > 0);
  ++clients;
  auto client = new Http;
  client->timeout = config->timeout_ms;
  client->txBufferSize = config->buffer_size_tx;
  return client;
}
esp_err_t esp_http_client_cleanup(esp_http_client_handle_t handle) {
  delete static_cast<Http*>(handle);
  --clients;
  return ESP_OK;
}
esp_err_t esp_http_client_open(esp_http_client_handle_t handle, int length) {
  assert(length == 0);
  ++opens;
  const auto& client = *static_cast<Http*>(handle);
  const int timeout = client.timeout;
  now += std::min(connectionDelay, timeout);
  if (connectionDelay > timeout) return ESP_ERR_TIMEOUT;
  // ESP-IDF must fit the path, signed query and HTTP framing in its transmit buffer.
  const auto& target = responses.at(client.response).requestTarget;
  if (target.size() + sizeof("GET  HTTP/1.1\r\n") > size_t(client.txBufferSize)) return ESP_FAIL;
  return openError;
}
esp_err_t esp_http_client_set_timeout_ms(esp_http_client_handle_t handle, int timeout) {
  static_cast<Http*>(handle)->timeout = timeout;
  return ESP_OK;
}
int esp_http_client_get_errno(esp_http_client_handle_t) { return socketError; }
esp_err_t esp_http_client_get_and_clear_last_tls_error(esp_http_client_handle_t, int* error, int* flags) {
  *error = tlsError;
  *flags = verifyFlags;
  return tlsSdkError;
}
int64_t esp_http_client_fetch_headers(esp_http_client_handle_t handle) {
  assert(static_cast<Http*>(handle)->timeout <= 5000);
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
  assert(client.timeout > 0 && client.timeout <= 5000);
  if (readError) return readError;
  if (client.position > 24 && readTimeoutsAfterData) {
    if (readTimeoutsAfterData > 0) --readTimeoutsAfterData;
    now += client.timeout;
    return -ESP_ERR_HTTP_EAGAIN;
  }
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
  // A healthy slow connection, including one after redirect, may take more than five seconds.
  connectionDelay = 7000;
  responses = {HttpResponse(302, ""), HttpResponse(200, manifest())};
  assert(backend.check());
  runTask();
  assert(backend.poll(result) && result.error == Error::NONE && clients == 0);
  responses = {HttpResponse(302, ""), HttpResponse(302, ""), HttpResponse(200, manifest())};
  assert(backend.check());
  runTask();
  assert(backend.poll(result) && result.error == Error::NETWORK && result.network.stage == NetworkStage::CONNECT && clients == 0);
  connectionDelay = 16000;
  responses = {HttpResponse(200, manifest())};
  assert(backend.check());
  runTask();
  assert(backend.poll(result) && result.error == Error::NETWORK && result.network.stage == NetworkStage::CONNECT && clients == 0);
  connectionDelay = 0;
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
    responses.back().requestTarget = "/github-production-release-asset/file?sig=" + std::string(830, 'a');
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
  responses = {HttpResponse(200, image, image.size())};
  for (const bool resumes : {true, false}) {
    Update = UpdateClass{};
    readTimeoutsAfterData = resumes ? 2 : -1;
    const auto started = now;
    opens = 0;
    assert(backend.install(candidate()));
    runTask();
    assert(backend.poll(result) && opens == 1 && clients == 0);
    if (resumes) {
      assert(result.error == Error::NONE && Update.selected && digested == image.size());
    } else {
      assert(result.error == Error::NETWORK && result.network.stage == NetworkStage::DEADLINE && now - started == 180000);
      assert(!Update.selected && Update.aborts == 1);
    }
  }
  readTimeoutsAfterData = 0;
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
  responses = {HttpResponse(0, "")};
  openError = 0x7002;
  tlsSdkError = 0x801a;
  tlsError = -0x2700;
  verifyFlags = 0x200;
  socketError = 104;
  assert(backend.check());
  runTask();
  assert(backend.poll(result) && result.error == Error::NETWORK && result.network.stage == NetworkStage::CONNECT);
  assert(result.network.sdkError == openError && result.network.tlsSdkError == tlsSdkError && result.network.tlsError == tlsError &&
         result.network.verifyFlags == verifyFlags && result.network.socketError == 104 && result.network.httpStatus == 0 && clients == 0);
  assert(result.network.heapBefore == 64000 && result.network.largestBefore == 32000);
  assert(result.network.heapAtFailure == 64000 && result.network.largestAtFailure == 32000);
  openError = ESP_OK;
  tlsSdkError = tlsError = verifyFlags = socketError = 0;
  responses = {HttpResponse(404, "missing")};
  assert(backend.check());
  runTask();
  assert(backend.poll(result) && result.network.stage == NetworkStage::STATUS && result.network.httpStatus == 404);
  responses = {HttpResponse(200, "incomplete")};
  readError = -1;
  assert(backend.check());
  runTask();
  assert(backend.poll(result) && result.network.stage == NetworkStage::READ && result.network.httpStatus == 200);
  readError = 0;
  for (auto queue : queues) delete queue;
  std::puts("ESP worker: queued execution, TLS roots/hostname checks, HTTPS redirects, 404/bounds, Update/SHA adapters, progress and failure cleanup passed");
  std::puts("firmware_update_worker: behavioral checks passed (SDK/RTOS/crypto/flash substituted; no live HTTPS or flash)");
}
