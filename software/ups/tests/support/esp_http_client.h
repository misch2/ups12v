#pragma once
#include <cstdint>

#include "nvs.h"
using esp_http_client_handle_t = void*;
enum esp_http_client_transport_t { HTTP_TRANSPORT_OVER_TCP, HTTP_TRANSPORT_OVER_SSL };
struct esp_http_client_config_t {
  const char* url = nullptr;
  const char* cert_pem = nullptr;
  esp_err_t (*crt_bundle_attach)(void*) = nullptr;
  bool skip_cert_common_name_check = false;
  esp_http_client_transport_t transport_type = HTTP_TRANSPORT_OVER_TCP;
  bool disable_auto_redirect = false;
  int timeout_ms = 0, buffer_size = 0, buffer_size_tx = 0;
  const char* user_agent = nullptr;
};
esp_http_client_handle_t esp_http_client_init(const esp_http_client_config_t* config);
esp_err_t esp_http_client_cleanup(esp_http_client_handle_t client);
esp_err_t esp_http_client_open(esp_http_client_handle_t client, int length);
int64_t esp_http_client_fetch_headers(esp_http_client_handle_t client);
int esp_http_client_get_status_code(esp_http_client_handle_t client);
int64_t esp_http_client_get_content_length(esp_http_client_handle_t client);
esp_err_t esp_http_client_set_redirection(esp_http_client_handle_t client);
esp_err_t esp_http_client_close(esp_http_client_handle_t client);
esp_http_client_transport_t esp_http_client_get_transport_type(esp_http_client_handle_t client);
bool esp_http_client_is_complete_data_received(esp_http_client_handle_t client);
int esp_http_client_read(esp_http_client_handle_t client, char* bytes, int count);
