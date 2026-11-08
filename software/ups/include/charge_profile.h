#pragma once

// BQ25798, SLUSDV2C rev. C: sections 7.5.1.2 (VREG), 7.5.1.8 (VRECHG).
// Project scope: 1-4 series cells rated for a maximum 4.2 V charge voltage.
namespace ChargeControl {
enum class Mode { LEGACY, FULL, APPROX_80 };

struct Profile {
  Mode mode = Mode::LEGACY;
  int fullCell_mV = 4200;
  int approx80Cell_mV = 0;    // Required for APPROX_80; calibrate for the actual cells.
  int rechargeOffset_mV = 0;  // Pack voltage below VREG; 0 preserves the IC setting.
};

inline const char* name(Mode mode) {
  switch (mode) {
    case Mode::LEGACY:
      return "Legacy";
    case Mode::FULL:
      return "Full";
    case Mode::APPROX_80:
      return "Approx. 80%";
    default:
      return "Invalid";
  }
}

struct Plan {
  int pack_mV;
  const char* error;
};

inline Plan plan(const Profile& profile, int cells) {
  if (profile.mode == Mode::LEGACY) return {0, nullptr};
  if (profile.mode != Mode::FULL && profile.mode != Mode::APPROX_80) return {0, "Unknown charge profile"};
  if (cells < 1 || cells > 4) return {0, "Invalid cell count"};
  if (profile.fullCell_mV < 3000 || profile.fullCell_mV > 4200) return {0, "Full-charge voltage must be 3000..4200 mV/cell"};
  const int cell_mV = profile.mode == Mode::FULL ? profile.fullCell_mV : profile.approx80Cell_mV;
  if (cell_mV < 3000 || cell_mV > profile.fullCell_mV || (profile.mode == Mode::APPROX_80 && cell_mV == profile.fullCell_mV)) {
    return {0, "Approx. 80% requires an explicit lower cell voltage"};
  }
  if (profile.rechargeOffset_mV != 0 && (profile.rechargeOffset_mV < 50 || profile.rechargeOffset_mV > 800 || profile.rechargeOffset_mV % 50 != 0)) {
    return {0, "Recharge offset must be 50..800 mV/pack in 50 mV steps, or 0"};
  }
  // VREG is a PACK voltage with 10 mV steps; round down, never above the request.
  return {cell_mV * cells / 10 * 10, nullptr};
}

// IC must have a fresh register snapshot. Does not touch CELL, OTG/backup, CE,
// current limits, temperature protection or the legacy SOC estimate.
template <typename IC>
const char* apply(const Profile& profile, int cells, IC& ic, bool forwardPower) {
  if (profile.mode == Mode::LEGACY) return nullptr;
  const Plan desired = plan(profile, cells);
  auto fail = [&](const char* error) {
    ic.setEN_CHG(false);  // Best effort on I2C failure; not an independent hardware cutoff.
    return error;
  };
  if (desired.error) return fail(desired.error);
  if (ic.lastError()) return fail("Charger communication error");
  const bool voltageChanged = ic.getVREG() != desired.pack_mV;
  const bool rechargeChanged = profile.rechargeOffset_mV != 0 && ic.getVRECHG() != profile.rechargeOffset_mV;
  if (voltageChanged || rechargeChanged) {
    ic.setEN_CHG(false);
    if (ic.lastError()) return fail("Cannot disable charging before configuration");
    ic.setVREG(desired.pack_mV);
    if (ic.lastError()) return fail("Cannot write charge voltage");
    if (profile.rechargeOffset_mV != 0) ic.setVRECHG(profile.rechargeOffset_mV);
    ic.readAllRegisters();
    if (ic.lastError()) return fail("Cannot read charge configuration");
  }
  if (ic.getVREG() != desired.pack_mV || static_cast<int>(ic.getCELL()) + 1 != cells ||
      (profile.rechargeOffset_mV != 0 && ic.getVRECHG() != profile.rechargeOffset_mV)) {
    return fail("Charge configuration readback mismatch");
  }
  // The IC performs CC/CV termination and recharge hysteresis. Do not enable
  // charging in battery-only, OTG or backup operation.
  if (forwardPower && !ic.getEN_CHG()) {
    ic.setEN_CHG(true);
    ic.readAllRegisters();
    if (ic.lastError() || !ic.getEN_CHG() || ic.getVREG() != desired.pack_mV || static_cast<int>(ic.getCELL()) + 1 != cells ||
        (profile.rechargeOffset_mV != 0 && ic.getVRECHG() != profile.rechargeOffset_mV)) {
      return fail("Cannot verify charge enable");
    }
  }
  return nullptr;
}
}  // namespace ChargeControl
