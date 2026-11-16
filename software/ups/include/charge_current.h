#pragma once

namespace ChargeControl {
// TI BQ25798 SLUSDV2C rev. C, sections 7.3.9.1, 7.5.1.3 and 7.5.1.6:
// ICHG is 50..5000 mA in 10 mA steps; trickle current is fixed at 100 mA.
// Never round a battery limit up or support a pack below that fixed current.
inline int currentLimit_mA(int requested_mA, int batteryMax_mA) {
  if (requested_mA < 50 || batteryMax_mA < 100) return 0;
  int limit_mA = requested_mA < batteryMax_mA ? requested_mA : batteryMax_mA;
  if (limit_mA > 5000) limit_mA = 5000;
  return limit_mA / 10 * 10;
}

// Requires a fresh register snapshot. All ICHG writes go through this helper,
// including the already-initialized marker path and runtime recovery.
template <typename IC>
const char* applyCurrentLimit(int requested_mA, int batteryMax_mA, IC& ic) {
  const int desired_mA = currentLimit_mA(requested_mA, batteryMax_mA);
  auto fail = [&](const char* error) {
    ic.setEN_CHG(false);  // Best effort; GPIO CHARGE_ARM is also revoked by the caller.
    return error;
  };
  if (desired_mA == 0) return fail("Battery limit must be at least 100 mA; requested ICHG at least 50 mA");
  if (ic.lastError()) return fail("Charger communication error");
  bool changed = false;
  if (ic.getICHG() != desired_mA) {
    ic.setICHG(desired_mA);
    if (ic.lastError()) return fail("Cannot write battery charge current limit");
    changed = true;
  }
  // Precharge is independent of ICHG. Preserve it unless it exceeds the pack
  // limit, then round down to its 40 mA step (REG08).
  const int maxPrecharge_mA = batteryMax_mA / 40 * 40;
  if (ic.getIPRECHG() > maxPrecharge_mA) {
    ic.setIPRECHG(maxPrecharge_mA);
    if (ic.lastError()) return fail("Cannot write battery precharge current limit");
    changed = true;
  }
  if (changed) {
    ic.readAllRegisters();
    if (ic.lastError()) return fail("Cannot read battery charge current limit");
    if (ic.getICHG() != desired_mA || ic.getIPRECHG() > maxPrecharge_mA) return fail("Battery charge current limit readback mismatch");
  }
  return nullptr;
}
}  // namespace ChargeControl
