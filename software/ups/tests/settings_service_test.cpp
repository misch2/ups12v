#include <cassert>
#include <cstdio>
#include "settings_apply.h"

using Settings::ApplyState;
using Settings::Status;

struct Backend : Settings::Backend {
  std::string record;
  bool failWrite = false;
  int writes = 0;
  Settings::Result read(std::string& output) override {
    if (record.empty()) return {Status::MISSING};
    output = record;
    return {Status::OK};
  }
  Settings::Result write(const std::string& value) override {
    ++writes;
    if (failWrite) return {Status::STORAGE_ERROR};
    record = value;
    return {Status::OK};
  }
};

RuntimeSettings configuration() {
  RuntimeSettings settings;
  settings.network.mqtt.haDeviceName = "test-ups";
  settings.network.mqtt.password = "TEST_ONLY_PASSWORD";
  settings.battery.cell.approx80PercentCapacity_mV = 3955;
  settings.battery.pack.maxChargeCurrent_mA = 700;
  settings.power.charger.chargeProfile.mode = ChargeControl::Mode::APPROX_80;
  settings.power.charger.ICHG_mA = 1000;
  return settings;
}

struct Application : Settings::Application {
  int calls = 0;
  ApplyState result = ApplyState::APPLIED;
  Settings::ApplyResult apply(const RuntimeSettings&) override { ++calls; return {result, "simulated hardware outcome"}; }
};

void proposalsAndPersistence() {
  auto active = configuration();
  Backend backend;
  Settings::Store store(backend, Hardware::kV4Esp32C3);
  assert(store.seedIfMissing(active).ok());
  Settings::Service service(store, Hardware::kV4Esp32C3, active);
  assert(service.begin().ok());
  Application application;
  assert(service.tick(application, 0));
  assert(service.status().appliedRevision == 1 && !service.powerPending());
  auto candidate = service.desired();
  candidate.battery.cell.name = "Replacement cell";
  const int calls = application.calls;
  const int writes = backend.writes;
  backend.failWrite = true;
  assert(service.propose(candidate).status == Status::STORAGE_ERROR);
  assert(active.battery.cell.name != "Replacement cell" && service.desired().battery.cell.name != "Replacement cell");
  assert(service.status().desiredRevision == 1 && application.calls == calls);
  backend.failWrite = false;
  assert(service.propose(candidate).ok() && application.calls == calls && backend.writes == writes + 2);
  assert(active.battery.cell.name != "Replacement cell");
  assert(!service.tick(application, 1) && application.calls == calls && active.battery.cell.name == "Replacement cell");
  assert(service.status().appliedRevision == service.status().desiredRevision);
  candidate = service.desired();
  candidate.network.mqtt.password = "NEW_TEST_PASSWORD";
  assert(service.propose(candidate).ok());
  service.tick(application, 2);
  assert(service.status().restartRequired && active.network.mqtt.password == "TEST_ONLY_PASSWORD");
  assert(service.desired().network.mqtt.password == "NEW_TEST_PASSWORD" && application.calls == calls);
  candidate.network.mqtt.haDeviceName = "different-ups";
  assert(service.propose(candidate).status == Status::IDENTITY_MISMATCH);
  candidate = service.desired();
  candidate.power.input.IINDPM_mA = 3301;
  assert(service.propose(candidate).status == Status::INVALID_SETTINGS);
  candidate = service.desired();
  candidate.power.output.VOTG_mV = 13000;
  assert(service.propose(candidate).status == Status::INVALID_SETTINGS);
  candidate = service.desired();
  candidate.power.charger.chargeProfile.fullCell_mV = 3900;
  assert(service.propose(candidate).status == Status::INVALID_SETTINGS);
  candidate.battery.cell.approx80PercentCapacity_mV = 3800;
  assert(service.propose(candidate).ok() && service.powerPending());
  application.result = ApplyState::DEFERRED;
  assert(!service.tick(application, 3) && service.status().powerState == ApplyState::DEFERRED);
  assert(!service.tick(application, 5002));
  application.result = ApplyState::FAILED;
  assert(!service.tick(application, 5003) && service.status().appliedRevision == 0);
  application.result = ApplyState::APPLIED;
  assert(service.tick(application, 10003) && !service.powerPending() && service.status().restartRequired);
  service.invalidatePower();
  assert(service.powerPending() && service.status().appliedRevision == 0);
  std::puts("service: validate/save/apply separation, failed save, metadata, immutable network, identity, dependent fields and retry passed");
}

struct IC {
  enum class PG { PG_STAT_GOOD, BAD };
  enum class Vbus { FORWARD, VBUS_STAT_BACKUP_MODE, VBUS_STAT_OTG_MODE };
  enum class PN { PN_BQ25798, OTHER };
  enum class Detection { DPDM_STAT_NOT_STARTED, DPDM_STAT_IN_PROGRESS };
  enum class Cells { TWO = 1, FOUR = 3 };
  struct Registers {
    int current = 2000, precharge = 120, voltage = 16800, recharge = 100;
    int inputCurrent = 1000, inputVoltage = 4700, otgCurrent = 1200, otgVoltage = 12000;
    bool enabled = true, externalLimit = false, hiz = false, otg = false, detecting = false;
    PG pg = PG::PG_STAT_GOOD;
    Vbus vbus = Vbus::FORWARD;
    PN pn = PN::PN_BQ25798;
    Cells cells = Cells::FOUR;
    BQ25798::VBUS_BACKUP_t ratio = BQ25798::VBUS_BACKUP_t::PCT_VBUS_BACKUP_80;
  } actual, cached;
  bool readError = false, writeError = false, ignoreVoltage = false, ignoreInput = false, ignoreDisable = false;
  int clampInput = 0, error = 0, writes = 0;
  void readAllRegisters() { if (readError) error = 7; else cached = actual; }
  int lastError() { return error; }
  template <typename T> void set(T& cache, T& hardware, T value) {
    ++writes;
    cache = value;
    if (writeError) error = 8;
    else hardware = value;
  }
  void setEN_CHG(bool value) { if (!(ignoreDisable && !value)) set(cached.enabled, actual.enabled, value); }
  void setICHG(int value) { set(cached.current, actual.current, value); }
  void setIPRECHG(int value) { set(cached.precharge, actual.precharge, value); }
  void setVREG(int value) {
    if (ignoreVoltage) cached.voltage = value;
    else set(cached.voltage, actual.voltage, value);
  }
  void setVRECHG(int value) { set(cached.recharge, actual.recharge, value); }
  void setIINDPM(int value) {
    if (ignoreInput) cached.inputCurrent = value;
    else set(cached.inputCurrent, actual.inputCurrent, clampInput && value > clampInput ? clampInput : value);
  }
  void setVINDPM(int value) { set(cached.inputVoltage, actual.inputVoltage, value); }
  void setIOTG(int value) { set(cached.otgCurrent, actual.otgCurrent, value); }
  void setVOTG(int value) { set(cached.otgVoltage, actual.otgVoltage, value); }
  void setVBUS_BACKUP(BQ25798::VBUS_BACKUP_t value) { set(cached.ratio, actual.ratio, value); }
  bool getEN_CHG() { return cached.enabled; }
  int getICHG() { return cached.current; }
  int getIPRECHG() { return cached.precharge; }
  int getVREG() { return cached.voltage; }
  int getVRECHG() { return cached.recharge; }
  int getIINDPM() { return cached.inputCurrent; }
  int getVINDPM() { return cached.inputVoltage; }
  int getIOTG() { return cached.otgCurrent; }
  int getVOTG() { return cached.otgVoltage; }
  BQ25798::VBUS_BACKUP_t getVBUS_BACKUP() { return cached.ratio; }
  bool getEN_EXTILIM() { return cached.externalLimit; }
  bool getEN_HIZ() { return cached.hiz; }
  bool getEN_OTG() { return cached.otg; }
  bool getFORCE_INDET() { return cached.detecting; }
  Detection getDPDM_STAT() { return cached.detecting ? Detection::DPDM_STAT_IN_PROGRESS : Detection::DPDM_STAT_NOT_STARTED; }
  PG getPG_STAT() { return cached.pg; }
  Vbus getVBUS_STAT() { return cached.vbus; }
  PN getPN() { return cached.pn; }
  Cells getCELL() { return cached.cells; }
};

void powerApplication() {
  auto settings = configuration();
  for (const auto cells : {IC::Cells::TWO, IC::Cells::FOUR}) {
    IC ic;
    ic.actual.cells = cells;
    const auto result = Settings::applyPowerSettings(settings, Hardware::kV4Esp32C3, ic, false);
    assert(result.state == ApplyState::APPLIED);
    assert(ic.actual.current == 700 && ic.actual.precharge <= 700 && ic.actual.enabled);
    assert(ic.actual.voltage == (3955 * (static_cast<int>(cells) + 1) / 10 * 10));
    assert(ic.actual.inputVoltage == 11500 && ic.actual.inputCurrent == 1000);  // No initialization-marker shortcut.
  }
  IC inhibited;
  assert(Settings::applyPowerSettings(settings, Hardware::kV4Esp32C3, inhibited, true).state == ApplyState::APPLIED && !inhibited.actual.enabled);
  IC hiZ;
  hiZ.actual.hiz = true;
  assert(Settings::applyPowerSettings(settings, Hardware::kV4Esp32C3, hiZ, false).state == ApplyState::DEFERRED && hiZ.writes == 0);
  IC backup;
  backup.actual.vbus = IC::Vbus::VBUS_STAT_BACKUP_MODE;
  assert(Settings::applyPowerSettings(settings, Hardware::kV1Esp32, backup, false).state == ApplyState::DEFERRED && backup.writes == 0);
  for (int failure = 0; failure < 5; ++failure) {
    IC ic;
    ic.readError = failure == 0;
    ic.writeError = failure == 1;
    ic.ignoreVoltage = failure == 2;
    ic.ignoreInput = failure == 3;
    ic.ignoreDisable = failure == 4;
    settings.power.input.IINDPM_mA = 1500;
    assert(Settings::applyPowerSettings(settings, Hardware::kV4Esp32C3, ic, false).state == ApplyState::FAILED);
  }
  IC limited;
  limited.actual.externalLimit = true;
  limited.clampInput = 1500;
  settings.power.input.IINDPM_mA = 3000;
  const auto clamped = Settings::applyPowerSettings(settings, Hardware::kV4Esp32C3, limited, false);
  assert(clamped.state == ApplyState::APPLIED && clamped.inputClamped && clamped.actualInput_mA == 1500);
  IC zero;
  settings.battery.pack.maxChargeCurrent_mA = 0;
  assert(Settings::applyPowerSettings(settings, Hardware::kV4Esp32C3, zero, false).state == ApplyState::APPLIED && !zero.actual.enabled);
  settings = configuration();
  settings.power.charger.chargeProfile.mode = ChargeControl::Mode::LEGACY;
  settings.power.output.VOTG_mV = 11900;
  settings.power.output.IOTG_mA = 1600;
  IC legacy;
  legacy.actual.enabled = false;
  legacy.actual.voltage = 15680;
  assert(Settings::applyPowerSettings(settings, Hardware::kV1Esp32, legacy, false).state == ApplyState::APPLIED);
  assert(legacy.actual.voltage == 15680 && !legacy.actual.enabled && legacy.actual.otgVoltage == 11900 && legacy.actual.otgCurrent == 1600);
  std::puts("power: 2S/4S, current ceiling, marker bypass, overrides, unsafe-state deferral, real readback, clamp reporting and legacy passed");
}

int main() {
  proposalsAndPersistence();
  powerApplication();
  std::puts("settings_service: all behavioral checks passed (storage and charger dependencies simulated)");
}
