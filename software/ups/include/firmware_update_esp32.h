#pragma once

#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include <freertos/task.h>

#include "firmware_update.h"

namespace FirmwareUpdate {
class Esp32Backend : public Backend {
 public:
  explicit Esp32Backend(const Hardware::Profile& hardware) : hardware(hardware) {}
  bool begin();
  bool check() override;
  bool install(const Candidate& candidate) override;
  bool poll(Result& result) override;
  bool progress(Progress& progress) override;
  uint32_t capacity() const override;

 private:
  struct Job {
    JobKind kind;
    Candidate candidate;
  };
  static void task(void* context);
  Result execute(const Job& job);
  const Hardware::Profile hardware;
  QueueHandle_t jobs = nullptr, results = nullptr, progressQueue = nullptr;
};
}  // namespace FirmwareUpdate
