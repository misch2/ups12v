#include "settings_nvs.h"

#include <nvs.h>

namespace Settings {
namespace {
constexpr const char* kNamespace = "ups-settings";

struct Handle {
  nvs_handle_t value = 0;
  ~Handle() {
    if (value) nvs_close(value);
  }
};
}  // namespace

Result NvsBackend::read(std::string& output) {
  Handle handle;
  const auto opened = nvs_open(kNamespace, NVS_READONLY, &handle.value);
  if (opened == ESP_ERR_NVS_NOT_FOUND) return {Status::MISSING};
  if (opened != ESP_OK) return {Status::STORAGE_ERROR, "nvs_open"};
  size_t length = 0;
  const auto sized = nvs_get_blob(handle.value, key, nullptr, &length);
  if (sized == ESP_ERR_NVS_NOT_FOUND) return {Status::MISSING};
  if (sized == ESP_ERR_NVS_TYPE_MISMATCH) return {Status::MALFORMED, "NVS type"};
  if (sized != ESP_OK) return {Status::STORAGE_ERROR, "nvs_get_blob size"};
  if (length == 0) return {Status::MALFORMED, "empty NVS blob"};
  if (length > kMaxRecordBytes) return {Status::TOO_LARGE};
  std::string record(length, '\0');
  const auto read = nvs_get_blob(handle.value, key, &record[0], &length);
  if (read != ESP_OK || length != record.size()) return {Status::STORAGE_ERROR, "nvs_get_blob"};
  output.swap(record);
  return {Status::OK};
}

Result NvsBackend::write(const std::string& record) {
  if (record.empty()) return {Status::MALFORMED};
  if (record.size() > kMaxRecordBytes) return {Status::TOO_LARGE};
  Handle handle;
  if (nvs_open(kNamespace, NVS_READWRITE, &handle.value) != ESP_OK) return {Status::STORAGE_ERROR, "nvs_open write"};
  if (nvs_set_blob(handle.value, key, record.data(), record.size()) != ESP_OK) return {Status::STORAGE_ERROR, "nvs_set_blob"};
  if (nvs_commit(handle.value) != ESP_OK) return {Status::STORAGE_ERROR, "nvs_commit"};
  return {Status::OK};
}
}  // namespace Settings
