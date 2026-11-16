// Host-only tests: no Arduino, I2C hardware or firmware toolchain required.
#include "charge_profile.h"

#include <cassert>
#include <cstdio>
#include <vector>

using ChargeControl::Mode;
using ChargeControl::Profile;

struct FakeCharger {
  int cells = 4;
  int voltage = 16800;
  int recharge = 400;
  bool enabled = true;
  int error = 0;
  bool failWrite = false;
  bool failRead = false;
  bool ignoreVoltage = false;
  bool ignoreEnable = false;
  bool changeCellsOnRead = false;
  int reads = 0;
  std::vector<int> actions;

  int lastError() { return error; }
  int getVREG() { return voltage; }
  int getVRECHG() { return recharge; }
  int getCELL() { return cells - 1; }
  bool getEN_CHG() { return enabled; }
  void setEN_CHG(bool value) {
    actions.push_back(value ? 1 : 0);
    if (!value || !ignoreEnable) enabled = value;
  }
  void setVREG(int value) {
    assert(!enabled);  // Never configure voltage while requesting charge.
    actions.push_back(2);
    if (failWrite) error = 1;
    if (!failWrite && !ignoreVoltage) voltage = value;
  }
  void setVRECHG(int value) {
    assert(!enabled);
    actions.push_back(3);
    recharge = value;
  }
  void readAllRegisters() {
    ++reads;
    if (failRead) error = 1;
    if (changeCellsOnRead) cells = 2;
  }
};

int main() {
  Profile profile;
  int approx80PercentCapacity_mV = 0;
  FakeCharger ic;
  // Legacy must leave registers and EN_CHG exactly alone, even on battery.
  assert(!ChargeControl::apply(profile, 0, approx80PercentCapacity_mV, ic, false));
  assert(ic.actions.empty() && ic.reads == 0 && ic.enabled);
  profile.mode = Mode::FULL;
  for (int cells = 1; cells <= 4; ++cells) {
    assert(ChargeControl::plan(profile, cells, approx80PercentCapacity_mV).pack_mV == 4200 * cells);
  }
  profile.mode = Mode::APPROX_80;
  assert(ChargeControl::plan(profile, 4, approx80PercentCapacity_mV).error);  // No invented 80%-to-voltage mapping.
  approx80PercentCapacity_mV = 4003;  // Synthetic test value, not a recommended cell setting.
  assert(ChargeControl::plan(profile, 2, approx80PercentCapacity_mV).pack_mV == 8000);
  assert(ChargeControl::plan(profile, 4, approx80PercentCapacity_mV).pack_mV == 16010);
  assert(ChargeControl::plan(profile, 0, approx80PercentCapacity_mV).error && ChargeControl::plan(profile, 5, approx80PercentCapacity_mV).error);
  approx80PercentCapacity_mV = 4200;
  assert(ChargeControl::plan(profile, 4, approx80PercentCapacity_mV).error);
  profile.fullCell_mV = 4300;
  assert(ChargeControl::plan(profile, 4, approx80PercentCapacity_mV).error);
  profile.fullCell_mV = 4200;
  approx80PercentCapacity_mV = 4000;
  profile.rechargeOffset_mV = 125;
  assert(ChargeControl::plan(profile, 4, approx80PercentCapacity_mV).error);
  profile.rechargeOffset_mV = 50;
  assert(!ChargeControl::plan(profile, 4, approx80PercentCapacity_mV).error);
  profile.rechargeOffset_mV = 800;
  assert(!ChargeControl::plan(profile, 4, approx80PercentCapacity_mV).error);
  profile.rechargeOffset_mV = 850;
  assert(ChargeControl::plan(profile, 4, approx80PercentCapacity_mV).error);
  profile.rechargeOffset_mV = 0;

  assert(!ChargeControl::apply(profile, 4, approx80PercentCapacity_mV, ic, true));
  assert(ic.voltage == 16000 && ic.recharge == 400 && ic.enabled);
  assert((ic.actions == std::vector<int>{0, 2, 1}));
  ic.actions.clear();
  int reads = ic.reads;
  assert(!ChargeControl::apply(profile, 4, approx80PercentCapacity_mV, ic, true));
  assert(ic.actions.empty() && ic.reads == reads);  // No continuous register rewrites.

  // IC reset while the MCU is alive: profile must be restored, not skipped.
  ic.voltage = 16800;
  assert(!ChargeControl::apply(profile, 4, approx80PercentCapacity_mV, ic, true));
  assert(ic.voltage == 16000 && ic.enabled);
  profile.mode = Mode::FULL;
  assert(!ChargeControl::apply(profile, 4, approx80PercentCapacity_mV, ic, true));
  assert(ic.voltage == 16800 && ic.enabled);  // Explicit return to full charge.

  profile.mode = Mode::APPROX_80;
  ic = FakeCharger{};
  assert(!ChargeControl::apply(profile, 4, approx80PercentCapacity_mV, ic, false));
  assert(ic.voltage == 16000 && !ic.enabled);  // Battery-only/backup cannot arm charging.
  assert(!ChargeControl::apply(profile, 4, approx80PercentCapacity_mV, ic, true));
  assert(ic.enabled);  // Adapter returns; hardware termination/recharge is enabled.

  profile.rechargeOffset_mV = 300;
  ic = FakeCharger{};
  assert(!ChargeControl::apply(profile, 4, approx80PercentCapacity_mV, ic, true));
  assert(ic.recharge == 300 && ic.enabled);

  // Configuration/readback/communication failures must never enable charging.
  for (int fault = 0; fault < 6; ++fault) {
    ic = FakeCharger{};
    if (fault == 0) ic.failWrite = true;
    if (fault == 1) ic.failRead = true;
    if (fault == 2) ic.ignoreVoltage = true;
    if (fault == 3) ic.ignoreEnable = true;
    if (fault == 4) ic.changeCellsOnRead = true;
    if (fault == 5) ic.error = 1;
    assert(ChargeControl::apply(profile, 4, approx80PercentCapacity_mV, ic, true));
    assert(!ic.enabled);
  }
  ic = FakeCharger{};
  approx80PercentCapacity_mV = 0;
  assert(ChargeControl::apply(profile, 4, approx80PercentCapacity_mV, ic, true));
  assert(!ic.enabled && ic.voltage == 16800);
  std::puts("charge_profile: all host checks passed");
}
