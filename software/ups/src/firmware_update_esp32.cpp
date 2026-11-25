#include "firmware_update_esp32.h"

#include <Arduino.h>
#include <Update.h>
#include <esp_http_client.h>
#include <esp_ota_ops.h>
#include <mbedtls/sha256.h>

#include <algorithm>
#include <cstdio>
#include <cstring>

#include "firmware_tls_roots.h"
#include "version.h"

namespace FirmwareUpdate {
namespace {
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
    if (!url || std::strncmp(url, "https://", 8) != 0) return false;
    deadline = deadlineMs;
    started = millis();
    esp_http_client_config_t config{};
    config.url = url;
    config.cert_pem = kTlsRootCertificates;
    config.skip_cert_common_name_check = false;
    config.transport_type = HTTP_TRANSPORT_OVER_SSL;
    config.disable_auto_redirect = true;
    config.timeout_ms = 5000;
    config.buffer_size = 1024;
    config.buffer_size_tx = 512;
    config.user_agent = "ups12v/" FIRMWARE_VERSION;
    client = esp_http_client_init(&config);
    if (!client) return false;
    for (int redirects = 0; redirects <= 5; ++redirects) {
      if (uint32_t(millis() - started) >= deadline || esp_http_client_get_transport_type(client) != HTTP_TRANSPORT_OVER_SSL) return false;
      if (esp_http_client_open(client, 0) != ESP_OK || esp_http_client_fetch_headers(client) < 0) return false;
      const int status = esp_http_client_get_status_code(client);
      if (status == 200) return true;
      if (status != 301 && status != 302 && status != 303 && status != 307 && status != 308) return false;
      // The IDF updates transport type for each Location; never follow an HTTPS downgrade.
      if (esp_http_client_set_redirection(client) != ESP_OK) return false;
      esp_http_client_close(client);
    }
    return false;
  }
  int64_t length() const override { return esp_http_client_get_content_length(client); }
  int read(uint8_t* bytes, size_t count) override {
    if (uint32_t(millis() - started) >= deadline) return -1;
    if (esp_http_client_is_complete_data_received(client)) return 0;
    const int received = esp_http_client_read(client, reinterpret_cast<char*>(bytes), count);
    return received == 0 && !esp_http_client_is_complete_data_received(client) ? -1 : received;
  }

 private:
  esp_http_client_handle_t client = nullptr;
  uint32_t started = 0, deadline = 0;
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
  if (job.kind == JobKind::CHECK) {
    if (!source.open(kManifestUrl, 20000)) {
      result.error = Error::NETWORK;
      return result;
    }
    if (source.length() > static_cast<int64_t>(kMaxManifestBytes)) {
      result.error = Error::MANIFEST;
      return result;
    }
    std::string json;
    uint8_t buffer[512];
    int count;
    while ((count = source.read(buffer, sizeof(buffer))) > 0) {
      if (json.size() + count > kMaxManifestBytes) {
        result.error = Error::MANIFEST;
        return result;
      }
      json.append(reinterpret_cast<char*>(buffer), count);
    }
    result.error = count < 0 ? Error::NETWORK : parseManifest(json, hardware, result.candidate);
  } else {
    if (job.candidate.size > capacity()) {
      result.error = Error::CAPACITY;
      return result;
    }
    if (!source.open(job.candidate.url, 180000)) {
      result.error = Error::NETWORK;
      return result;
    }
    Sha256 digest;
    UpdateFlash flash;
    QueueReporter reporter(progressQueue);
    result.error = transfer(job.candidate, hardware, source, flash, digest, reporter);
  }
  return result;
}
}  // namespace FirmwareUpdate
