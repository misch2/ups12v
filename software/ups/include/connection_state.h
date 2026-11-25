#pragma once

#include <cstdint>

namespace UpsNetwork {
// Main-loop ownership token for a single connection attempt. The worker never touches this object.
class ConnectionState {
 public:
  bool mayStart(uint32_t now, bool wifiReady, bool commissioned, bool force = false) const {
    return commissioned && wifiReady && !busy && !ready && (force || !attempted || uint32_t(now - lastAttempt) >= 60000);
  }
  void started(uint32_t now) {
    busy = true;
    ready = false;
    attempted = true;
    lastAttempt = now;
  }
  void completed(uint32_t now, bool connected) {
    busy = false;
    ready = connected;
    lastAttempt = now;
  }
  void disconnected() { ready = false; }
  bool workerOwnsClient() const { return busy; }
  bool mainOwnsConnectedClient() const { return ready && !busy; }

 private:
  bool busy = false;
  bool ready = false;
  bool attempted = false;
  uint32_t lastAttempt = 0;
};
}  // namespace UpsNetwork
