#pragma once

#include <cstdint>

// BQ25798 SLUSDV2C rev. C, sections 7.3.4.5 and 7.3.6.1:
// FORCE_INDET reruns D+/D- detection and may overwrite IINDPM. It does not
// renegotiate the external PD trigger's USB-PD contract.
namespace InputDetection {
enum class Action { NONE, START, RESTORE_LIMIT };

class Retry {
 public:
  // Called on communication loss or explicit charger reconfiguration. Keep a
  // pending limit restore across recovery, including the VAC2_ADC_DIS skip path.
  void resetInput() {
    present_ = false;
    attempted_ = false;
  }

  Action update(uint32_t now, bool present, bool powerGood, bool forwardMode, bool notQualified, bool detectionBusy) {
    if (!present) {
      resetInput();
    } else if (!present_) {
      present_ = true;
      presentSince_ = now;
    }

    // Finish restoring even if the source disappeared during our detection.
    // Writing IINDPM does not enable charging or bypass the hardware ILIM.
    if (pending_) return detectionBusy ? Action::NONE : Action::RESTORE_LIMIT;
    if (!present || !powerGood || !forwardMode || !notQualified || detectionBusy) return Action::NONE;
    if (static_cast<uint32_t>(now - presentSince_) < INTERVAL_MS || (attempted_ && static_cast<uint32_t>(now - lastAttempt_) < INTERVAL_MS)) {
      return Action::NONE;
    }

    attempted_ = true;
    lastAttempt_ = now;
    pending_ = true;
    return Action::START;
  }

  void limitRestored() { pending_ = false; }

 private:
  static constexpr uint32_t INTERVAL_MS = 60000;
  uint32_t presentSince_ = 0;
  uint32_t lastAttempt_ = 0;
  bool present_ = false;
  bool attempted_ = false;
  bool pending_ = false;
};
}  // namespace InputDetection
