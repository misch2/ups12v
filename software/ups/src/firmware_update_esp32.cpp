#include "firmware_update_esp32.h"

#include <Arduino.h>
#include <Update.h>
#include <esp_crt_bundle.h>
#include <esp_heap_caps.h>
#include <esp_http_client.h>
#include <esp_ota_ops.h>
#include <mbedtls/sha256.h>

#include <algorithm>
#include <cstdio>
#include <cstring>

#include "version.h"

namespace FirmwareUpdate {
namespace {
constexpr uint32_t kConnectTimeoutMs = 15000;
constexpr uint32_t kReadTimeoutMs = 5000;

uint32_t inactiveCapacity() {
  const auto next = esp_ota_get_next_update_partition(nullptr);
  const auto running = esp_ota_get_running_partition();
  return next && running && next->address != running->address ? next->size : 0;
}
class HttpsSource : public Source {
 public:
  ~HttpsSource() {
    if (client) esp_http_client_cleanup(client);
  }
  bool open(const char* url, uint32_t deadlineMs) {
    details.heapBefore = heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    details.largestBefore = heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    if (!url || std::strncmp(url, "https://", 8) != 0) return fail(NetworkStage::SECURITY);
    deadline = deadlineMs;
    started = millis();
    esp_http_client_config_t config{};
    config.url = url;
    config.crt_bundle_attach = esp_crt_bundle_attach;
    config.skip_cert_common_name_check = false;
    config.transport_type = HTTP_TRANSPORT_OVER_SSL;
    config.disable_auto_redirect = true;
    config.timeout_ms = kConnectTimeoutMs;
    config.buffer_size = 1024;
    config.buffer_size_tx = 512;
    config.user_agent = "ups12v/" FIRMWARE_VERSION;
    client = esp_http_client_init(&config);
    if (!client) return fail(NetworkStage::INIT, ESP_ERR_NO_MEM);
    for (int redirects = 0; redirects <= 5; ++redirects) {
      const uint32_t elapsed = millis() - started;
      if (elapsed >= deadline) return fail(NetworkStage::DEADLINE, ESP_ERR_TIMEOUT);
      if (esp_http_client_get_transport_type(client) != HTTP_TRANSPORT_OVER_SSL) return fail(NetworkStage::SECURITY);
      esp_http_client_set_timeout_ms(client, std::min(kConnectTimeoutMs, deadline - elapsed));
      attemptedOpen = true;
      const auto opened = esp_http_client_open(client, 0);
      if (opened != ESP_OK) return fail(NetworkStage::CONNECT, opened);
      esp_http_client_set_timeout_ms(client, kReadTimeoutMs);
      if (esp_http_client_fetch_headers(client) < 0) return fail(NetworkStage::HEADERS, ESP_FAIL);
      const int status = esp_http_client_get_status_code(client);
      details.httpStatus = status;
      if (status == 200) return true;
      if (status != 301 && status != 302 && status != 303 && status != 307 && status != 308) return fail(NetworkStage::STATUS);
      // The IDF updates transport type for each Location; never follow an HTTPS downgrade.
      const auto redirected = esp_http_client_set_redirection(client);
      if (redirected != ESP_OK) return fail(NetworkStage::REDIRECT, redirected);
      esp_http_client_close(client);
    }
    return fail(NetworkStage::REDIRECT);
  }
  int64_t length() const override { return esp_http_client_get_content_length(client); }
  int read(uint8_t* bytes, size_t count) override {
    if (uint32_t(millis() - started) >= deadline) {
      fail(NetworkStage::DEADLINE, ESP_ERR_TIMEOUT);
      return -1;
    }
    if (esp_http_client_is_complete_data_received(client)) {
      details.stage = NetworkStage::COMPLETE;
      return 0;
    }
    const int received = esp_http_client_read(client, reinterpret_cast<char*>(bytes), count);
    if (received < 0 || (received == 0 && !esp_http_client_is_complete_data_received(client))) {
      fail(NetworkStage::READ, received < 0 ? received : ESP_FAIL);
      return -1;
    }
    if (received == 0) details.stage = NetworkStage::COMPLETE;
    return received;
  }
  const NetworkDiagnostics& diagnostics() const { return details; }

 private:
  esp_http_client_handle_t client = nullptr;
  uint32_t started = 0, deadline = 0;
  NetworkDiagnostics details;
  bool attemptedOpen = false;
  bool fail(NetworkStage stage, int sdkError = 0) {
    details.heapAtFailure = heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    details.largestAtFailure = heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    details.stage = stage;
    details.sdkError = sdkError;
    if (client && attemptedOpen) {
      details.httpStatus = esp_http_client_get_status_code(client);
      details.socketError = esp_http_client_get_errno(client);
      details.tlsSdkError = esp_http_client_get_and_clear_last_tls_error(client, &details.tlsError, &details.verifyFlags);
    }
    return false;
  }
};

class Sha256 : public Digest {
 public:
  Sha256() { mbedtls_sha256_init(&context); }
  ~Sha256() { mbedtls_sha256_free(&context); }
  bool begin() override { return mbedtls_sha256_starts(&context, 0) == 0; }
  bool update(const uint8_t* bytes, size_t count) override { return mbedtls_sha256_update(&context, bytes, count) == 0; }
  bool finish(char hex[65]) override {
    uint8_t bytes[32];
    if (mbedtls_sha256_finish(&context, bytes) != 0) return false;
    for (int i = 0; i < 32; ++i) std::snprintf(hex + 2 * i, 3, "%02x", bytes[i]);
    return true;
  }

 private:
  mbedtls_sha256_context context;
};

class UpdateFlash : public Flash {
 public:
  ~UpdateFlash() { abort(); }
  uint32_t capacity() const override { return inactiveCapacity(); }
  bool begin(uint32_t size) override {
    if (Update.isRunning()) return false;
    Update.onProgress(nullptr);  // No callback inherited from a previous ArduinoOTA attempt in this worker.
    owned = Update.begin(size, U_FLASH);
    return owned;
  }
  bool write(uint8_t* bytes, size_t count) override { return owned && Update.write(bytes, count) == count; }
  bool finish() override {
    if (!owned || !Update.end(false)) return false;
    owned = false;
    return true;
  }
  void abort() override {
    if (owned) {
      Update.abort();
      owned = false;
    }
  }

 private:
  bool owned = false;
};

class QueueReporter : public Reporter {
 public:
  explicit QueueReporter(QueueHandle_t queue) : queue(queue) {}
  void progress(uint32_t bytes, uint32_t total) override {
    Progress value;
    value.bytes = bytes;
    value.total = total;
    xQueueOverwrite(queue, &value);  // Drop intermediate progress; final result has a separate reliable queue.
    vTaskDelay(1);                   // Give the main loop a scheduling opportunity even on a single-core C3.
  }

 private:
  QueueHandle_t queue;
};
}  // namespace

bool Esp32Backend::begin() {
  if (jobs) return false;
  jobs = xQueueCreate(1, sizeof(Job));
  results = xQueueCreate(1, sizeof(Result));
  progressQueue = xQueueCreate(1, sizeof(Progress));
  if (jobs && results && progressQueue && xTaskCreate(task, "ups-update", 12288, this, 1, nullptr) == pdPASS) return true;
  if (jobs) vQueueDelete(jobs);
  if (results) vQueueDelete(results);
  if (progressQueue) vQueueDelete(progressQueue);
  jobs = results = progressQueue = nullptr;
  return false;
}
bool Esp32Backend::check() {
  Job job{};
  job.kind = JobKind::CHECK;
  return jobs && xQueueSend(jobs, &job, 0) == pdTRUE;
}
bool Esp32Backend::install(const Candidate& candidate) {
  Job job{};
  job.kind = JobKind::INSTALL;
  job.candidate = candidate;
  return jobs && xQueueSend(jobs, &job, 0) == pdTRUE;
}
bool Esp32Backend::poll(Result& result) { return results && xQueueReceive(results, &result, 0) == pdTRUE; }
bool Esp32Backend::progress(Progress& progress) { return progressQueue && xQueueReceive(progressQueue, &progress, 0) == pdTRUE; }
uint32_t Esp32Backend::capacity() const { return inactiveCapacity(); }

void Esp32Backend::task(void* context) {
  auto& worker = *static_cast<Esp32Backend*>(context);
  for (;;) {
    Job job;
    if (xQueueReceive(worker.jobs, &job, portMAX_DELAY) == pdTRUE) {
      const auto result = worker.execute(job);
      xQueueSend(worker.results, &result, portMAX_DELAY);
    }
  }
}
Result Esp32Backend::execute(const Job& job) {
  Result result;
  result.kind = job.kind;
  HttpsSource source;
  auto finish = [&](Error error) {
    result.error = error;
    result.network = source.diagnostics();
    return result;
  };
  if (job.kind == JobKind::CHECK) {
    if (!source.open(kManifestUrl, 20000)) {
      return finish(Error::NETWORK);
    }
    if (source.length() > static_cast<int64_t>(kMaxManifestBytes)) {
      return finish(Error::MANIFEST);
    }
    std::string json;
    uint8_t buffer[512];
    int count;
    while ((count = source.read(buffer, sizeof(buffer))) > 0) {
      if (json.size() + count > kMaxManifestBytes) {
        return finish(Error::MANIFEST);
      }
      json.append(reinterpret_cast<char*>(buffer), count);
    }
    return finish(count < 0 ? Error::NETWORK : parseManifest(json, hardware, result.candidate));
  } else {
    if (job.candidate.size > capacity()) {
      return finish(Error::CAPACITY);
    }
    if (!source.open(job.candidate.url, 180000)) {
      return finish(Error::NETWORK);
    }
    Sha256 digest;
    UpdateFlash flash;
    QueueReporter reporter(progressQueue);
    return finish(transfer(job.candidate, hardware, source, flash, digest, reporter));
  }
}
}  // namespace FirmwareUpdate
