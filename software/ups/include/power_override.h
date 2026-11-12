#pragma once

namespace PowerOverride {
enum class Kind { CHARGE_INHIBIT, BATTERY_SUPPLY };

// Test guard, not a cell undervoltage protector. Pack voltage / CELL is an average.
struct Limits {
  int stopCell_mV = 3600;
  int startCell_mV = 3700;

  bool valid() const { return stopCell_mV > 0 && startCell_mV > stopCell_mV && startCell_mV <= 4200; }
};

struct State {
  bool chargeInhibit = false;
  bool batterySupply = false;

  bool inhibitsCharging() const { return chargeInhibit || batterySupply; }
  void clear() { chargeInhibit = batterySupply = false; }
  void set(Kind kind, bool enabled) { (kind == Kind::CHARGE_INHIBIT ? chargeInhibit : batterySupply) = enabled; }

  bool canStart(const Limits& limits, int pack_mV, int cells, bool validSample) const {
    return limits.valid() && validSample && cells >= 1 && cells <= 4 && pack_mV >= limits.startCell_mV * cells;
  }

  bool cancelIfLow(const Limits& limits, int pack_mV, int cells, bool validSample) {
    if (!inhibitsCharging()) return false;
    if (!limits.valid() || !validSample || cells < 1 || cells > 4 || pack_mV <= limits.stopCell_mV * cells) {
      clear();
      return true;
    }
    return false;
  }
};
}  // namespace PowerOverride
