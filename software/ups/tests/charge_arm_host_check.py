"""Extract real UPS startup functions for a native C++ fault-injection check.

Run: python software/ups/tests/charge_arm_host_check.py
Then compile .pio/charge-arm-check/check.cpp with a C++17 compiler and run it.
No board configuration, credentials, network or hardware is used.
"""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "src/UPS.ino").read_text(encoding="utf-8")


def function(signature):
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end] + "\n"


# Verify the integration points as well as compiling the actual helper bodies.
assert source.split("void setup() {", 1)[1].lstrip().startswith("setupChargeArm();")
assert source.split("void setChargerReady(bool ready) {", 1)[1].lstrip().startswith("if (!ready) {\n    setChargeArm(false);")
assert 'Config::Pins boardPins{4, 5, -1, true, 0}' in (root / "include/boards/v4/ups4_esp76/board_config.h").read_text()
for board in ("example", "ups1_esp18", "ups2_esp27", "ups3_esp19"):
    assert 'Config::Pins boardPins{21, 22, 2, true, -1}' in (root / f"include/boards/{board}/board_config.h").read_text()

preamble = r'''
#include <cassert>
#include <cstdio>
#include <vector>
#include "charge_profile.h"
#include "charge_current.h"
#include "input_detection.h"
InputDetection::Retry inputDetectionRetry;
constexpr int HIGH=1, LOW=0, OUTPUT=2, LOG_ERR=3, LOG_INFO=6;
std::vector<char> actions;
int arm=LOW;
bool gpioOutput=true;
bool allowArmedIO=false;
struct { int CHARGE_ARM=0; } boardPins;
enum gpio_num_t { GPIO_NUM_0=0 };
int gpio_set_level(gpio_num_t pin, unsigned int value) { assert(pin==GPIO_NUM_0 && value==LOW); arm=value; actions.push_back('l'); return 0; }
void digitalWrite(int pin, int value) { assert(pin==0 && gpioOutput); arm=value; actions.push_back(value ? 'H' : 'L'); }
void pinMode(int pin, int mode) { assert(pin==0 && mode==OUTPUT && arm==LOW); gpioOutput=true; actions.push_back('P'); }
struct { template<class... T> void log(T...) {} } logger;
struct { void loop() {} } ledBlinker;
struct { void handle() {} } ArduinoOTA;
unsigned long millis() { return 0; }
void delay(int) {}
struct BQ25798 {
  enum class PN_t { PN_BQ25798 };
  enum class CELL_t { CELL_1S, CELL_2S, CELL_3S, CELL_4S };
  enum class PG_STAT_t { PG_STAT_GOOD };
  enum class VBUS_STAT_t { VBUS_STAT_NO_INPUT, VBUS_STAT_BACKUP_MODE, VBUS_STAT_OTG_MODE };
  enum class WATCHDOG_t { WATCHDOG_DISABLE, ENABLED };
  enum class ADC_RATE_t { ADC_RATE_CONTINUOUS };
  enum class ADC_SAMPLE_t { ADC_SAMPLE_15BIT };
  struct Registers {
    bool marker=true, enabled=true;
    int current=1000, precharge=120, voltage=16800, recharge=400, cells=4;
    WATCHDOG_t watchdog=WATCHDOG_t::ENABLED;
  } hw, cache;
  int error=0, writes=0, reads=0, failWrite=0, failRead=0, mutateRead=0, mutateField=0, ignored=0, resets=0;
  bool write(char action) { assert(arm==LOW || allowArmedIO); actions.push_back(action); if (++writes==failWrite) { error=1; return false; } return true; }
  int lastError() { return error; }
  bool getVAC2_ADC_DIS() { return cache.marker; }
  bool getREG_RST() { return false; }
  PN_t getPN() { return PN_t::PN_BQ25798; }
  CELL_t getCELL() { return static_cast<CELL_t>(cache.cells-1); }
  PG_STAT_t getPG_STAT() { return PG_STAT_t::PG_STAT_GOOD; }
  VBUS_STAT_t getVBUS_STAT() { return VBUS_STAT_t::VBUS_STAT_NO_INPUT; }
  WATCHDOG_t getWATCHDOG() { return cache.watchdog; }
  int getICHG() { return cache.current; }
  int getIPRECHG() { return cache.precharge; }
  int getVREG() { return cache.voltage; }
  int getVRECHG() { return cache.recharge; }
  bool getEN_CHG() { return cache.enabled; }
  void setICHG(int v) { if (write('I') && ignored!=1) hw.current=v; cache.current=v; }
  void setIPRECHG(int v) { if (write('p') && ignored!=4) hw.precharge=v; cache.precharge=v; }
  void setWATCHDOG(WATCHDOG_t v) { if (write('W') && ignored!=2) hw.watchdog=v; cache.watchdog=v; }
  void setEN_CHG(bool v) { if (write(v ? 'E' : 'D') && ignored!=3) hw.enabled=v; cache.enabled=v; }
  void setVREG(int v) { if (write('V')) hw.voltage=v; cache.voltage=v; }
  void setVRECHG(int v) { if (write('R')) hw.recharge=v; cache.recharge=v; }
  void setVAC2_ADC_DIS(bool v) { if (write('M')) hw.marker=v; cache.marker=v; }
  void setREG_RST(bool) { if (write('X')) { ++resets; hw=Registers{}; hw.marker=false; cache=hw; } }
  void readAllRegisters() {
    assert(arm==LOW || allowArmedIO); actions.push_back('r');
    if (++reads==failRead) { error=1; return; }
    if (reads==mutateRead) {
      switch (mutateField) {
        case 0: hw.current=2000; break;
        case 1: hw.watchdog=WATCHDOG_t::ENABLED; break;
        case 2: hw.cells=2; break;
        case 3: hw.voltage=16800; break;
        case 4: hw.recharge=400; break;
        case 5: hw.enabled=false; break;
        case 6: hw.precharge=2000; break;
      }
    }
    cache=hw;
  }
  // Unrelated one-time configuration writes remain observable.
  template<class T> void setADC_RATE(T) { write('a'); }
  template<class T> void setADC_SAMPLE(T) { write('a'); }
  void setADC_EN(bool) { write('a'); }
  void setIBUS_ADC_DIS(bool) { write('a'); }
  void setIBAT_ADC_DIS(bool) { write('a'); }
  void setEN_IBAT(bool) { write('a'); }
  void setEN_HIZ(bool) { write('a'); }
  void setAUTO_INDET_EN(bool) { write('a'); }
  void setVOTG(int) { write('a'); }
  void setIOTG(int) { write('a'); }
  void setVBUS_BACKUP(int) { write('a'); }
  void setVINDPM(int) { write('a'); }
  void setIINDPM(int) { write('a'); }
  void setEN_BACKUP(bool) { write('a'); }
} bq25798;
struct Config {
  struct { const char* name="Test pack"; int maxChargeCurrent_mA=500; int approx80PercentCapacity_mV=0; } battery;
  struct Power {
    enum class BackupMode { VSYS_UNINTERRUPTED, PMID_WITH_SWITCHOVER };
    BackupMode backupMode=BackupMode::VSYS_UNINTERRUPTED;
    struct { int ICHG_mA=500; ChargeControl::Profile chargeProfile; } charger;
    struct { int VOTG_mV=0, IOTG_mA=0; } output;
    struct { int VBUSBackupPercentage=0, VINDPM_mV=0, IINDPM_mA=0; } input;
  } power;
} config;
bool chargerReady=false;
void setChargeArm(bool);
void setChargerReady(bool ready) { if (!ready) setChargeArm(false); chargerReady=ready; }
bool checkForError() { if (!bq25798.lastError()) return false; setChargerReady(false); bq25798.error=0; return true; }
'''

checks = r'''
void reset(bool marked=true, bool legacy=false) {
  bq25798=BQ25798{}; config=Config{}; boardPins.CHARGE_ARM=0; arm=LOW; gpioOutput=true; allowArmedIO=false; actions.clear();
  bq25798.hw.marker=marked;
  auto &p=config.power.charger.chargeProfile;
  p.mode=legacy ? ChargeControl::Mode::LEGACY : ChargeControl::Mode::APPROX_80;
  config.battery.approx80PercentCapacity_mV=3920; p.rechargeOffset_mV=200;
  if (marked) { bq25798.hw.voltage=15680; bq25798.hw.recharge=200; }
  bq25798.cache=bq25798.hw;
}
int main() {
  // Startup must clear a stale HIGH latch before enabling GPIO output, without Arduino digitalWrite.
  reset(); arm=HIGH; gpioOutput=false; setupChargeArm();
  assert(arm==LOW && gpioOutput && (actions==std::vector<char>{'l','P'}));
  // Marked startup skips full configuration/reset, but still verifies charge permission.
  reset(); arm=HIGH; assert(onetimeSetupIfNeeded(false,true));
  assert((actions==std::vector<char>{'L','I','r','W','r','E','r','H'}));
  assert(bq25798.resets==0 && arm==HIGH);
  // An already disabled watchdog does not need rewriting.
  reset(); bq25798.hw.watchdog=bq25798.cache.watchdog=BQ25798::WATCHDOG_t::WATCHDOG_DISABLE;
  assert(onetimeSetupIfNeeded()); assert(bq25798.writes==2);
  // Fresh/forced initialization keeps hardware permission LOW throughout.
  for (bool marked : {false,true}) {
    reset(marked); assert(onetimeSetupIfNeeded(marked,true));
    assert(bq25798.resets==1 && bq25798.hw.marker && arm==HIGH);
  }
  // Exercise every register write/read failure on both marker paths.
  for (bool marked : {false,true}) {
    reset(marked); assert(onetimeSetupIfNeeded());
    int writes=bq25798.writes, reads=bq25798.reads;
    for (int i=1; i<=writes; ++i) {
      reset(marked); bq25798.failWrite=i; assert(!onetimeSetupIfNeeded()); assert(arm==LOW);
    }
    for (int i=1; i<=reads; ++i) {
      reset(marked); bq25798.failRead=i; assert(!onetimeSetupIfNeeded()); assert(arm==LOW);
    }
  }
  // Successful bus transfers with ignored writes must also leave the gate inhibited.
  for (int field=1; field<=3; ++field) {
    reset(true,field==3);
    if (field==3) bq25798.hw.enabled=bq25798.cache.enabled=false;
    bq25798.ignored=field; assert(!onetimeSetupIfNeeded()); assert(arm==LOW);
  }
  for (int read=2; read<=3; ++read) {
    for (int field=0; field<=6; ++field) {
      if (read==2 && field==5) continue; // EN_CHG has not been enabled yet.
      reset(); bq25798.mutateRead=read; bq25798.mutateField=field;
      assert(!onetimeSetupIfNeeded()); assert(arm==LOW);
    }
  }
  reset(); config.battery.approx80PercentCapacity_mV=0;
  assert(!onetimeSetupIfNeeded()); assert(arm==LOW);
  // V4 LEGACY still explicitly establishes ICHG, watchdog and EN_CHG.
  reset(true,true); assert(onetimeSetupIfNeeded()); assert(arm==HIGH && bq25798.hw.enabled);
  // Older boards must also apply the battery limit despite the saved marker.
  reset(true,true); boardPins.CHARGE_ARM=-1; setupChargeArm();
  assert(onetimeSetupIfNeeded(false,true)); assert((actions==std::vector<char>{'I','r'}));
  reset(true,false); boardPins.CHARGE_ARM=-1;
  assert(onetimeSetupIfNeeded()); assert((actions==std::vector<char>{'I','r'}));
  // Clamping is mandatory on both generations, in both profiles and all setup paths.
  for (int pin : {-1,0}) for (bool marked : {false,true}) for (bool legacy : {false,true}) {
    reset(marked,legacy); boardPins.CHARGE_ARM=pin; config.power.charger.ICHG_mA=2000;
    assert(onetimeSetupIfNeeded()); assert(bq25798.hw.current==500);
    reset(marked,legacy); boardPins.CHARGE_ARM=pin; config.power.charger.ICHG_mA=2000;
    assert(onetimeSetupIfNeeded(true,true)); assert(bq25798.hw.current==500);
  }
  // A changed request/pack limit is reapplied without depending on full setup.
  reset(); boardPins.CHARGE_ARM=-1; config.power.charger.ICHG_mA=2000;
  assert(applyChargeProfile()); assert(bq25798.hw.current==500);
  config.battery.maxChargeCurrent_mA=255;
  assert(applyChargeProfile()); assert(bq25798.hw.current==250);
  bq25798.hw.current=bq25798.cache.current=2000;
  assert(applyChargeProfile()); assert(bq25798.hw.current==250);
  // Missing/invalid limits are rejected before a requested reset or any enable.
  for (int limit : {-1,0,49,99}) {
    reset(); config.battery.maxChargeCurrent_mA=limit;
    assert(!onetimeSetupIfNeeded(true,true));
    assert(arm==LOW && !bq25798.hw.enabled && bq25798.resets==0);
  }
  reset(); bq25798.hw.precharge=bq25798.cache.precharge=2000;
  config.power.charger.ICHG_mA=2000;
  assert(onetimeSetupIfNeeded()); assert(bq25798.hw.current==500 && bq25798.hw.precharge==480);
  reset(); bq25798.hw.precharge=bq25798.cache.precharge=2000; bq25798.ignored=4;
  assert(!onetimeSetupIfNeeded()); assert(arm==LOW && !bq25798.hw.enabled);
  // An ignored runtime correction revokes an already raised V4 permission.
  reset(); assert(onetimeSetupIfNeeded()); assert(arm==HIGH);
  allowArmedIO=true; chargerReady=true;
  bq25798.hw.current=bq25798.cache.current=2000; bq25798.ignored=1;
  assert(!applyBatteryChargeCurrent()); assert(arm==LOW && !bq25798.hw.enabled && !chargerReady);
  std::puts("charge_arm: startup ordering, marker/force paths, legacy boards and injected faults passed");
}
'''

functions = "\n".join(function(signature) for signature in (
    "int batteryCellCount() {", "bool applyBatteryChargeCurrent() {", "bool applyChargeProfile() {", "void setChargeArm(bool armed) {",
    "void setupChargeArm() {", "bool configureChargerIfNeeded(bool force, bool reset) {",
    "bool onetimeSetupIfNeeded(bool force = false, bool reset = false) {",
))
output = root / ".pio/charge-arm-check"
output.mkdir(parents=True, exist_ok=True)
(output / "check.cpp").write_text(preamble + functions + checks, encoding="utf-8")
print(f"Generated {output / 'check.cpp'} from UPS.ino")
