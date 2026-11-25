#pragma once

#include <cstdint>
#include "device_identity.h"
#include "settings_store.h"

namespace Settings {
enum class ApplyState { UNCONFIGURED, PENDING, APPLIED, DEFERRED, FAILED };
struct ApplyResult {
  ApplyResult(ApplyState state, const char* detail = nullptr, int actualInput_mA = 0, bool inputClamped = false)
      : state(state), detail(detail), actualInput_mA(actualInput_mA), inputClamped(inputClamped) {}
  ApplyState state;
  const char* detail;
  int actualInput_mA;
  bool inputClamped;
};
struct ApplicationStatus {
  uint32_t desiredRevision = 0;
  uint32_t appliedRevision = 0;
  ApplyState powerState = ApplyState::UNCONFIGURED;
  bool restartRequired = false;
  const char* detail = nullptr;
  int actualInput_mA = 0;
  bool inputClamped = false;
};
class Application {
 public:
  virtual ~Application() = default;
  virtual ApplyResult apply(const RuntimeSettings& desired) = 0;
};

Result validateForHardware(const RuntimeSettings& settings, const Hardware::Profile& hardware);
void copyPowerSettings(const RuntimeSettings& source, RuntimeSettings& target);

class Service {
 public:
  Service(Store& store, const Hardware::Profile& hardware, RuntimeSettings& active) : store(store), hardware(hardware), active(active) {}
  Result begin();
  // Full desired candidate; no IC/network mutations from this operation or its caller's callback.
  Result propose(const RuntimeSettings& candidate);
  void setLocked(bool locked) { writesLocked = locked; }
  bool tick(Application& application, uint32_t now);  // True only after a newly verified power application.
  void invalidatePower();
  bool powerPending() const { return pendingPower; }
  const RuntimeSettings& desired() const { return desiredSettings; }
  const ApplicationStatus& status() const { return report; }

 private:
  Store& store;
  const Hardware::Profile hardware;
  RuntimeSettings& active;
  RuntimeSettings desiredSettings;
  ApplicationStatus report;
  bool initialized = false;
  bool writesLocked = false;
  bool metadataPending = false;
  bool pendingPower = false;
  bool attempted = false;
  uint32_t lastAttempt = 0;
};
}  // namespace Settings
