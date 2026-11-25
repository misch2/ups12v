#pragma once
#include <cstddef>
#include <cstdint>
constexpr int U_FLASH = 0;
class UpdateClass {
 public:
  bool running = false, selected = false, failWrite = false, failEnd = false;
  int writes = 0, aborts = 0;
  bool isRunning() const { return running; }
  void onProgress(std::nullptr_t) {}
  bool begin(size_t size, int command) {
    if (command != U_FLASH || size < 24) return false;
    running = true;
    return true;
  }
  size_t write(uint8_t*, size_t count) {
    ++writes;
    return failWrite ? 0 : count;
  }
  bool end(bool partial) {
    if (partial || failEnd) return false;
    selected = true;
    running = false;
    return true;
  }
  void abort() {
    ++aborts;
    running = false;
  }
};
extern UpdateClass Update;
