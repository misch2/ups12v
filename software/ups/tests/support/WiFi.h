#pragma once

#include "Arduino.h"

// Arduino ESP32 also exposes this global; helpers must not reuse Network as a namespace.
class NetworkManager {};
extern NetworkManager Network;

class IPAddress {
 public:
  explicit IPAddress(uint32_t value = 0) : address(value) {}
  operator uint32_t() const { return address; }
  String toString() const { return "192.0.2.4"; }
 private:
  uint32_t address;
};

class WiFiClient {
 public:
  int stops = 0;
  int descriptor = -1;
  int fd() const { return descriptor; }
  void stop() { ++stops; descriptor = -1; }
};

class WiFiServer {
 public:
  explicit WiFiServer(int) {}
  static int nextClient;
  void begin() {}
  void end() {}
  void setNoDelay(bool) {}
  WiFiClient accept() { WiFiClient client; client.descriptor = nextClient; nextClient = -1; return client; }
};

constexpr int WL_CONNECTED = 3;

class WiFiClass {
 public:
  bool resolve = true;
  int calls = 0;
  int connectionStatus = WL_CONNECTED;
  int status() const { return connectionStatus; }
  IPAddress localIP() const { return IPAddress(1); }
  bool hostByName(const char*, IPAddress& address) {
    ++calls;
    address = IPAddress(resolve ? 0x01020304 : 0);
    return resolve;
  }
};
extern WiFiClass WiFi;
