// Compile with include/ and generated .pio/input-detection-check/ on the include path.
#include "input_detection.h"

#include <cassert>
#include <cstdio>
#include <initializer_list>

#include "power_override.h"

using InputDetection::Action;
using InputDetection::Retry;

void checkPolicy() {
  Retry retry;
  assert(retry.update(0, true, true, true, true, false) == Action::NONE);
  assert(retry.update(59999, true, true, true, true, false) == Action::NONE);
  assert(retry.update(60000, true, true, true, true, false) == Action::START);
  assert(retry.update(60001, true, true, true, true, true) == Action::NONE);
  assert(retry.update(62000, true, true, true, true, false) == Action::RESTORE_LIMIT);
  // A failed IINDPM restore remains pending across communication recovery.
  retry.resetInput();
  assert(retry.update(63000, true, true, true, true, false) == Action::RESTORE_LIMIT);
  retry.limitRestored();
  assert(retry.update(122999, true, true, true, true, false) == Action::NONE);
  assert(retry.update(123000, true, true, true, true, false) == Action::START);
  // Source loss must not discard the limit restoration for a detection we started.
  assert(retry.update(123001, false, false, false, true, true) == Action::NONE);
  assert(retry.update(124000, false, false, false, false, false) == Action::RESTORE_LIMIT);
  retry.limitRestored();
  assert(retry.update(130000, true, true, true, true, false) == Action::NONE);
  assert(retry.update(189999, true, true, true, true, false) == Action::NONE);
  assert(retry.update(190000, true, true, true, true, false) == Action::START);

  retry = Retry{};
  retry.update(0, true, true, true, true, false);
  // Power Good, forward mode, category 8 and idle detection are all required.
  assert(retry.update(60000, true, false, true, true, false) == Action::NONE);
  assert(retry.update(60000, true, true, false, true, false) == Action::NONE);
  assert(retry.update(60000, true, true, true, false, false) == Action::NONE);
  assert(retry.update(60000, true, true, true, true, true) == Action::NONE);
  assert(retry.update(60000, true, true, true, true, false) == Action::START);
  assert(retry.update(61000, true, true, true, false, false) == Action::RESTORE_LIMIT);
  retry.limitRestored();
  assert(retry.update(120000, true, true, true, false, false) == Action::NONE);
  // Further attempts are spaced from the previous start, not every loop.
  assert(retry.update(120000, true, true, true, true, false) == Action::START);
  assert(retry.update(121000, true, true, true, true, false) == Action::RESTORE_LIMIT);
  retry.limitRestored();
  assert(retry.update(179999, true, true, true, true, false) == Action::NONE);
  assert(retry.update(180000, true, true, true, true, false) == Action::START);

  // Any interruption of source presence restarts the initial minute.
  retry = Retry{};
  retry.update(0, true, true, true, true, false);
  retry.update(59000, false, false, true, true, false);
  retry.update(60000, true, true, true, true, false);
  assert(retry.update(119999, true, true, true, true, false) == Action::NONE);
  assert(retry.update(120000, true, true, true, true, false) == Action::START);

  retry = Retry{};
  constexpr uint32_t wrapStart = UINT32_MAX - 100;
  retry.update(wrapStart, true, true, true, true, false);
  assert(retry.update(static_cast<uint32_t>(wrapStart + 59999u), true, true, true, true, false) == Action::NONE);
  assert(retry.update(static_cast<uint32_t>(wrapStart + 60000u), true, true, true, true, false) == Action::START);
}

uint32_t clockMs = 0;
uint32_t millis() { return clockMs; }
constexpr int LOG_INFO = 6;
struct {
  template <class... T>
  void log(T...) {}
} logger;
struct {
  struct {
    struct {
      bool retryUnqualifiedAdapter = true;
      int IINDPM_mA = 3000;
    } input;
  } power;
} config;
struct BQ25798 {
  enum class VBUS_STAT_t { VBUS_STAT_OTG_MODE = 7, VBUS_STAT_NOT_QUALIFIED_ADAPTOR = 8, VBUS_STAT_BACKUP_MODE = 12, UNKNOWN = 5 };
  enum class AC1_PRESENT_STAT_t { ABSENT, AC1_PRESENT_STAT_PRESENT };
  enum class PG_STAT_t { BAD, PG_STAT_GOOD };
  enum class DPDM_STAT_t { IDLE, DPDM_STAT_IN_PROGRESS };
  VBUS_STAT_t vbus = VBUS_STAT_t::VBUS_STAT_NOT_QUALIFIED_ADAPTOR;
  bool present = true, good = true, force = false, dpdm = false, error = false, hiz = false;
  bool failForce = false, failLimit = false, failRead = false;
  int inputLimit = 500, requestedLimit = 0, hardwareClamp = 1000;
  int forceWrites = 0, limitWrites = 0, reads = 0;
  VBUS_STAT_t getVBUS_STAT() { return vbus; }
  AC1_PRESENT_STAT_t getAC1_PRESENT_STAT() { return present ? AC1_PRESENT_STAT_t::AC1_PRESENT_STAT_PRESENT : AC1_PRESENT_STAT_t::ABSENT; }
  PG_STAT_t getPG_STAT() { return good ? PG_STAT_t::PG_STAT_GOOD : PG_STAT_t::BAD; }
  DPDM_STAT_t getDPDM_STAT() { return dpdm ? DPDM_STAT_t::DPDM_STAT_IN_PROGRESS : DPDM_STAT_t::IDLE; }
  bool getFORCE_INDET() { return force; }
  bool getEN_HIZ() { return hiz; }
  int getIINDPM() { return inputLimit; }
  void setFORCE_INDET(bool value) {
    ++forceWrites;
    error = failForce;
    if (!error) force = value;
  }
  void setIINDPM(int value) {
    ++limitWrites;
    requestedLimit = value;
    error = failLimit;
    if (!error) inputLimit = value < hardwareClamp ? value : hardwareClamp;
  }
  void readAllRegisters() {
    ++reads;
    error = failRead;
  }
} bq25798;
Retry inputDetectionRetry;
PowerOverride::State powerOverrides;
bool overrideHizOwned = false;
bool ready = true, armed = true;
bool checkForError() {
  if (!bq25798.error) return false;
  bq25798.error = false;
  ready = armed = false;
  inputDetectionRetry.resetInput();
  return true;
}

#include "input_detection_service.inc"

void resetService() {
  bq25798 = BQ25798{};
  inputDetectionRetry = Retry{};
  powerOverrides = {};
  overrideHizOwned = false;
  config.power.input.retryUnqualifiedAdapter = true;
  config.power.input.IINDPM_mA = 3000;
  ready = armed = true;
  clockMs = 0;
}

void startDetection() {
  assert(serviceInputDetection());
  clockMs = 59999;
  assert(serviceInputDetection() && bq25798.forceWrites == 0);
  clockMs = 60000;
  assert(serviceInputDetection() && bq25798.forceWrites == 1 && bq25798.force);
}

int main() {
  checkPolicy();
  for (int gate = 0; gate < 3; ++gate) {
    resetService();
    if (gate == 0) powerOverrides.batterySupply = true;
    if (gate == 1) overrideHizOwned = true;
    if (gate == 2) bq25798.hiz = true;
    assert(serviceInputDetection());
    clockMs = 60000;
    assert(serviceInputDetection() && bq25798.forceWrites == 0 && bq25798.limitWrites == 0);
  }
  resetService();
  startDetection();
  clockMs = 60001;
  assert(serviceInputDetection() && bq25798.limitWrites == 0);
  // Wait for both self-clearing FORCE_INDET and actual DPDM activity to finish.
  bq25798.force = false;
  bq25798.dpdm = true;
  assert(serviceInputDetection() && bq25798.limitWrites == 0);
  bq25798.dpdm = false;
  bq25798.vbus = BQ25798::VBUS_STAT_t::UNKNOWN;
  assert(serviceInputDetection());
  assert(bq25798.requestedLimit == 3000 && bq25798.inputLimit == 1000 && bq25798.reads == 1);
  assert(ready && armed);  // Normal detection does not toggle charge permission.
  clockMs = 180000;
  assert(serviceInputDetection() && bq25798.forceWrites == 1 && bq25798.limitWrites == 1);

  for (auto blocked : {BQ25798::VBUS_STAT_t::VBUS_STAT_OTG_MODE, BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE}) {
    resetService();
    bq25798.vbus = blocked;
    assert(serviceInputDetection());
    clockMs = 60000;
    assert(serviceInputDetection() && bq25798.forceWrites == 0);
  }
  resetService();
  config.power.input.retryUnqualifiedAdapter = false;
  assert(serviceInputDetection());
  clockMs = 60000;
  assert(serviceInputDetection() && bq25798.forceWrites == 0 && bq25798.limitWrites == 0 && bq25798.reads == 0);

  // Errors use the existing charge-inhibit/recovery path; pending restore survives.
  for (int fault = 0; fault < 3; ++fault) {
    resetService();
    if (fault == 0) {
      assert(serviceInputDetection());
      clockMs = 60000;
      bq25798.failForce = true;
    } else {
      startDetection();
      bq25798.force = false;
      if (fault == 1) bq25798.failLimit = true;
      if (fault == 2) bq25798.failRead = true;
    }
    assert(!serviceInputDetection() && !ready && !armed);
    bq25798.failForce = bq25798.failLimit = bq25798.failRead = false;
    ready = armed = true;  // Existing charger initialization/recovery completed.
    assert(serviceInputDetection() && bq25798.requestedLimit == 3000);
    assert(bq25798.inputLimit == 1000);
  }
  std::puts("input_detection: settling/retry timing, input loss, mode gates, wrap, hardware clamp and I2C recovery passed");
}
