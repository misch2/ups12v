#pragma once

#include "nvs.h"

constexpr int WIFI_IF_STA = 0;
constexpr int WIFI_STORAGE_FLASH = 1;
constexpr int WIFI_AUTH_OPEN = 0;
constexpr int ESP_ERR_WIFI_NOT_CONNECT = 77;
struct wifi_config_t {
  struct {
    uint8_t ssid[32] = {};
    uint8_t password[64] = {};
    bool bssid_set = false;
    struct { int authmode = 0; } threshold;
  } sta;
};
esp_err_t esp_wifi_get_config(int interface, wifi_config_t* config);
esp_err_t esp_wifi_set_config(int interface, wifi_config_t* config);
esp_err_t esp_wifi_set_storage(int storage);
esp_err_t esp_wifi_disconnect();
