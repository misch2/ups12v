#pragma once

#include "Arduino.h"

// Arduino ESP32 also exposes this global; helpers must not reuse Network as a namespace.
class NetworkManager {};
extern NetworkManager Network;

class IPAddress {
 public:
  explicit IPAddress(uint32_t value = 0) : address(value) {}
  operator uint32_t() const { return address; }
 private:
  uint32_t address;
};

class WiFiClient {
 public:
  int stops = 0;
  void stop() { ++stops; }
};

class WiFiClass {
 public:
  bool resolve = true;
  int calls = 0;
  bool hostByName(const char*, IPAddress& address) {
    ++calls;
    address = IPAddress(resolve ? 0x01020304 : 0);
    return resolve;
  }
};
extern WiFiClass WiFi;
