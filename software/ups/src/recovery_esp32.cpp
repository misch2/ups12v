#include "recovery_esp32.h"

#include <WiFi.h>
#include <esp_random.h>

#include <cstdio>

namespace Recovery {
std::string Esp32Driver::newPassword() {
  char password[17];
  for (int i = 0; i < 2; ++i) std::snprintf(password + 8 * i, 9, "%08lx", static_cast<unsigned long>(esp_random()));
  return password;
}
bool Esp32Driver::start(const char* ssid, const char* password) {
  // Keep STA and its retry logic alive; no wait-for-connection loop or reboot.
  if (WiFi.mode(WIFI_AP_STA) && WiFi.softAP(ssid, password) &&
      WiFi.softAPConfig(IPAddress(192, 168, 4, 1), IPAddress(192, 168, 4, 1), IPAddress(255, 255, 255, 0))) return true;
  WiFi.softAPdisconnect(true);  // A failed start must not leave a default/unprotected AP running.
  return false;
}
bool Esp32Driver::stop() { return WiFi.softAPdisconnect(true); }
}  // namespace Recovery
