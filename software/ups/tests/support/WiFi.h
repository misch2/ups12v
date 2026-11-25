#pragma once

#include "Arduino.h"

// Arduino ESP32 also exposes this global; helpers must not reuse Network as a namespace.
class NetworkManager {};
extern NetworkManager Network;

class IPAddress {
 public:
  explicit IPAddress(uint32_t value = 0) : address(value) {}
  IPAddress(uint8_t a, uint8_t b, uint8_t c, uint8_t d) : address(uint32_t(a) << 24 | uint32_t(b) << 16 | uint32_t(c) << 8 | d) {}
  operator uint32_t() const { return address; }
  String toString() const { return address == 0xc0a80401 ? "192.168.4.1" : "192.0.2.4"; }
 private:
  uint32_t address;
};

class WiFiClient {
 public:
  int stops = 0;
  int descriptor = -1;
  bool apInterface = false;
  int fd() const { return descriptor; }
  IPAddress localIP() const { return IPAddress(apInterface ? 0xc0a80401 : 1); }
  void stop() { ++stops; descriptor = -1; }
};

class WiFiServer {
 public:
  explicit WiFiServer(int) {}
  static int nextClient;
  static bool nextAPClient;
  void begin() {}
  void end() {}
  void setNoDelay(bool) {}
  WiFiClient accept() { WiFiClient client; client.descriptor = nextClient; client.apInterface = nextAPClient; nextClient = -1; return client; }
};

constexpr int WL_CONNECTED = 3;
constexpr int WIFI_AP_STA = 3;

class WiFiClass {
 public:
  bool resolve = true;
  int calls = 0;
  int connectionStatus = WL_CONNECTED;
  int status() const { return connectionStatus; }
  IPAddress localIP() const { return IPAddress(1); }
  bool apSuccess = true;
  int apStops = 0, selectedMode = 0;
  std::string apSsid, apPassword;
  bool mode(int value) { selectedMode = value; return apSuccess; }
  bool softAP(const char* ssid, const char* password) { apSsid = ssid; apPassword = password; return apSuccess; }
  bool softAPConfig(IPAddress, IPAddress, IPAddress) { return apSuccess; }
  bool softAPdisconnect(bool) { ++apStops; return true; }
  bool hostByName(const char*, IPAddress& address) {
    ++calls;
    address = IPAddress(resolve ? 0x01020304 : 0);
    return resolve;
  }
};
extern WiFiClass WiFi;
