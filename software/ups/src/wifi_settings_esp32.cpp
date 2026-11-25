#include "wifi_settings_esp32.h"

#include <esp_wifi.h>

#include <cstring>

namespace Settings {
Result Esp32WifiDriver::read(WifiCredentials& credentials) {
  wifi_config_t config{};
  if (esp_wifi_get_config(WIFI_IF_STA, &config) != ESP_OK) return {Status::STORAGE_ERROR, "Wi-Fi SDK read"};
  credentials.ssid.assign(reinterpret_cast<const char*>(config.sta.ssid), strnlen(reinterpret_cast<const char*>(config.sta.ssid), 32));
  credentials.password.assign(reinterpret_cast<const char*>(config.sta.password), strnlen(reinterpret_cast<const char*>(config.sta.password), 64));
  return {Status::OK};
}

Result Esp32WifiDriver::write(const WifiCredentials& credentials) {
  const auto valid = WifiStore::validate(credentials);
  if (!valid.ok()) return valid;
  wifi_config_t config{};
  if (esp_wifi_get_config(WIFI_IF_STA, &config) != ESP_OK) return {Status::STORAGE_ERROR, "Wi-Fi SDK read"};
  std::memset(config.sta.ssid, 0, sizeof(config.sta.ssid));
  std::memset(config.sta.password, 0, sizeof(config.sta.password));
  std::memcpy(config.sta.ssid, credentials.ssid.data(), credentials.ssid.size());
  std::memcpy(config.sta.password, credentials.password.data(), credentials.password.size());
  config.sta.bssid_set = false;  // A new SSID must not remain pinned to the previous AP.
  if (credentials.password.empty()) config.sta.threshold.authmode = WIFI_AUTH_OPEN;
  if (esp_wifi_set_storage(WIFI_STORAGE_FLASH) != ESP_OK || esp_wifi_set_config(WIFI_IF_STA, &config) != ESP_OK) {
    return {Status::STORAGE_ERROR, "Wi-Fi SDK write"};
  }
  return {Status::OK};
}
}  // namespace Settings
