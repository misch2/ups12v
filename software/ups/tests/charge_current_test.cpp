#include <cassert>
#include <climits>
#include <cstdio>

#include "charge_current.h"

struct IC {
  int current = 2000;
  int cachedCurrent = 2000;
  int precharge = 120;
  int cachedPrecharge = 120;
  int prechargeWrites = 0;
  int error = 0;
  int writes = 0;
  int reads = 0;
  bool enabled = true;
  bool ignoreWrite = false;
  bool ignorePrecharge = false;
  bool failWrite = false;
  bool failRead = false;
  int lastError() { return error; }
  int getICHG() { return cachedCurrent; }
  int getIPRECHG() { return cachedPrecharge; }
  void setIPRECHG(int value) {
    ++prechargeWrites;
    cachedPrecharge = value;
    if (failWrite) error = 1;
    if (!ignorePrecharge && !failWrite) precharge = value;
  }
  void setICHG(int value) {
    ++writes;
    cachedCurrent = value;  // A setter cache alone must not prove a successful write.
    if (failWrite) error = 1;
    if (!ignoreWrite && !failWrite) current = value;
  }
  void readAllRegisters() {
    ++reads;
    if (failRead) error = 1;
    cachedCurrent = current;
    cachedPrecharge = precharge;
  }
  void setEN_CHG(bool value) { enabled = value; }
};

int main() {
  const int values[] = {INT_MIN, -1, 0, 1, 49, 50, 51, 59, 60, 99, 100, 119, 120, 255, 499, 500, 501, 1000, 2000, 4999, 5000, 5001, INT_MAX};
  for (int request : values) {
    for (int maximum : values) {
      const int result = ChargeControl::currentLimit_mA(request, maximum);
      IC ic;
      const char* error = ChargeControl::applyCurrentLimit(request, maximum, ic);
      if (request < 50 || maximum < 100) {
        assert(result == 0 && error && !ic.enabled && ic.writes == 0);
      } else {
        assert(!error && result >= 50 && result <= 5000 && result % 10 == 0);
        assert(result <= request && result <= maximum && ic.current == result);
        assert(ic.precharge <= maximum && ic.precharge % 40 == 0);
        assert(result + 10 > request || result + 10 > maximum || result == 5000);
      }
    }
  }
  IC ic;
  assert(!ChargeControl::applyCurrentLimit(2000, 500, ic));
  assert(ic.current == 500 && ic.reads == 1);
  assert(!ChargeControl::applyCurrentLimit(2000, 500, ic));
  assert(ic.writes == 1 && ic.reads == 1);  // No bus writes when already correct.
  ic = IC{};
  ic.current = ic.cachedCurrent = 500;
  ic.precharge = ic.cachedPrecharge = 2000;
  assert(!ChargeControl::applyCurrentLimit(2000, 500, ic));
  assert(ic.current == 500 && ic.precharge == 480 && ic.writes == 0 && ic.prechargeWrites == 1 && ic.reads == 1);
  for (int failure = 0; failure < 3; ++failure) {
    ic = IC{};
    ic.current = ic.cachedCurrent = 500;
    ic.precharge = ic.cachedPrecharge = 2000;
    ic.ignorePrecharge = failure == 0;
    ic.failWrite = failure == 1;
    ic.failRead = failure == 2;
    assert(ChargeControl::applyCurrentLimit(2000, 500, ic));
    assert(!ic.enabled);
  }
  for (int failure = 0; failure < 4; ++failure) {
    ic = IC{};
    ic.ignoreWrite = failure == 0;
    ic.failWrite = failure == 1;
    ic.failRead = failure == 2;
    ic.error = failure == 3;
    assert(ChargeControl::applyCurrentLimit(2000, 500, ic));
    assert(!ic.enabled);
  }
  std::puts("charge_current: limits, rounding, invalid config, cached writes and I2C failures passed");
}
