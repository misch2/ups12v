#include "settings_service.h"

#include <utility>

namespace Settings {
namespace {
bool inSteps(int value, int minimum, int maximum, int step) {
  return value <= 0 || (value >= minimum && value <= maximum && (value - minimum) % step == 0);
}
bool networkDifferent(const RuntimeSettings& a, const RuntimeSettings& b) {
  return a.network.mqtt.serverHostname != b.network.mqtt.serverHostname || a.network.mqtt.serverPort != b.network.mqtt.serverPort ||
         a.network.mqtt.user != b.network.mqtt.user || a.network.mqtt.password != b.network.mqtt.password ||
         a.network.syslog.serverHostname != b.network.syslog.serverHostname || a.network.syslog.serverPort != b.network.syslog.serverPort ||
         a.network.syslog.myHostname != b.network.syslog.myHostname || a.network.syslog.myAppname != b.network.syslog.myAppname;
}
bool powerDifferent(const RuntimeSettings& a, const RuntimeSettings& b) {
  return a.battery.pack.maxChargeCurrent_mA != b.battery.pack.maxChargeCurrent_mA ||
         a.battery.cell.approx80PercentCapacity_mV != b.battery.cell.approx80PercentCapacity_mV ||
         a.power.charger.chargeProfile.mode != b.power.charger.chargeProfile.mode ||
         a.power.charger.chargeProfile.fullCell_mV != b.power.charger.chargeProfile.fullCell_mV ||
         a.power.charger.chargeProfile.rechargeOffset_mV != b.power.charger.chargeProfile.rechargeOffset_mV ||
         a.power.charger.ICHG_mA != b.power.charger.ICHG_mA ||
         a.power.charger.vbatChgEnableIfCellBelow_mV != b.power.charger.vbatChgEnableIfCellBelow_mV ||
         a.power.charger.vbatChgDisableIfCellAbove_mV != b.power.charger.vbatChgDisableIfCellAbove_mV ||
         a.power.input.IINDPM_mA != b.power.input.IINDPM_mA || a.power.input.VINDPM_mV != b.power.input.VINDPM_mV ||
         a.power.input.retryUnqualifiedAdapter != b.power.input.retryUnqualifiedAdapter ||
         a.power.input.VBUSBackupPercentage != b.power.input.VBUSBackupPercentage ||
         a.power.output.IOTG_mA != b.power.output.IOTG_mA || a.power.output.VOTG_mV != b.power.output.VOTG_mV;
}
}  // namespace

Result validateForHardware(const RuntimeSettings& settings, const Hardware::Profile& hardware) {
  const auto valid = validate(settings);
  if (!valid.ok()) return valid;
  if (!DeviceIdentity::validStored(settings.network.mqtt.haDeviceName.c_str())) return {Status::INVALID_SETTINGS, "device identifier"};
  // TI SLUSDV2C rev. C, 7.5.1.4/.5/.9/.10. Nonpositive values retain the old skip-write semantics.
  if (!inSteps(settings.power.input.IINDPM_mA, 100, 3300, 10)) return {Status::INVALID_SETTINGS, "power.input.IINDPM_mA"};
  if (!inSteps(settings.power.input.VINDPM_mV, 3600, 22000, 100)) return {Status::INVALID_SETTINGS, "power.input.VINDPM_mV"};
  if (hardware.powerPath() == Hardware::PowerPath::PMID_WITH_SWITCHOVER) {
    if (!inSteps(settings.power.output.VOTG_mV, 2800, 22000, 10)) return {Status::INVALID_SETTINGS, "power.output.VOTG_mV"};
    // Intersection of datasheet 120..3320 and installed library 160..3360; do not silently clamp either end.
    if (!inSteps(settings.power.output.IOTG_mA, 160, 3320, 40)) return {Status::INVALID_SETTINGS, "power.output.IOTG_mA"};
  }
  if (settings.power.input.retryUnqualifiedAdapter && hardware.version != Hardware::Version::V4_0) {
    return {Status::INVALID_SETTINGS, "power.input.retryUnqualifiedAdapter"};
  }
  return {Status::OK};
}

void copyPowerSettings(const RuntimeSettings& source, RuntimeSettings& target) {
  target.battery.pack.maxChargeCurrent_mA = source.battery.pack.maxChargeCurrent_mA;
  target.battery.cell.approx80PercentCapacity_mV = source.battery.cell.approx80PercentCapacity_mV;
  target.power.input = source.power.input;
  target.power.output = source.power.output;
  target.power.charger.chargeProfile = source.power.charger.chargeProfile;
  target.power.charger.ICHG_mA = source.power.charger.ICHG_mA;
  target.power.charger.vbatChgEnableIfCellBelow_mV = source.power.charger.vbatChgEnableIfCellBelow_mV;
  target.power.charger.vbatChgDisableIfCellAbove_mV = source.power.charger.vbatChgDisableIfCellAbove_mV;
}

Result Service::begin() {
  RuntimeSettings loaded;
  const auto result = store.load(loaded);
  if (!result.ok()) return result;
  const auto valid = validateForHardware(loaded, hardware);
  if (!valid.ok()) return valid;
  if (loaded.network.mqtt.haDeviceName != active.network.mqtt.haDeviceName) return {Status::IDENTITY_MISMATCH};
  desiredSettings = std::move(loaded);
  initialized = true;
  report.desiredRevision = 1;
  invalidatePower();  // Also verifies settings that the IC's old initialization marker may skip.
  metadataPending = true;
  return {Status::OK};
}

Result Service::propose(const RuntimeSettings& candidate) {
  if (writesLocked) return {Status::INVALID_SETTINGS, "firmware installation in progress"};
  const auto valid = validateForHardware(candidate, hardware);
  if (!valid.ok()) return valid;
  if (initialized && candidate.network.mqtt.haDeviceName != active.network.mqtt.haDeviceName) return {Status::IDENTITY_MISMATCH};
  if (!initialized && !DeviceIdentity::validNew(candidate.network.mqtt.haDeviceName.c_str())) return {Status::INVALID_SETTINGS, "new device identifier"};
  if (initialized && hardware.powerPath() == Hardware::PowerPath::VSYS_UNINTERRUPTED &&
      (candidate.power.output.IOTG_mA != desiredSettings.power.output.IOTG_mA ||
       candidate.power.output.VOTG_mV != desiredSettings.power.output.VOTG_mV ||
       candidate.power.input.VBUSBackupPercentage != desiredSettings.power.input.VBUSBackupPercentage)) {
    return {Status::INVALID_SETTINGS, "PMID settings are inactive on SYS hardware"};
  }
  // Prepare an owned candidate before saving; a failed save leaves all RAM state and active policy unchanged.
  std::string encoded;
  const auto encoding = encodePrivate(candidate, hardware, encoded);
  if (!encoding.ok()) return encoding;
  RuntimeSettings prepared;
  const auto decoding = decodePrivate(encoded, hardware, prepared);
  if (!decoding.ok()) return decoding;
  const auto saved = store.save(prepared);
  if (!saved.ok()) return saved;
  const bool changedPower = initialized && powerDifferent(desiredSettings, prepared);
  report.restartRequired = !initialized || networkDifferent(active, prepared);
  desiredSettings = std::move(prepared);
  if (++report.desiredRevision == 0) ++report.desiredRevision;
  if (changedPower) invalidatePower();
  metadataPending = initialized;
  attempted = false;
  report.detail = nullptr;
  return {Status::OK};
}

void Service::invalidatePower() {
  if (!initialized) return;
  pendingPower = true;
  attempted = false;
  report.powerState = ApplyState::PENDING;
  report.appliedRevision = 0;
}

bool Service::tick(Application& application, uint32_t now) {
  if (!initialized) return false;  // Commissioning/network changes activate only on a later restart.
  if (metadataPending) {
    String name = desiredSettings.battery.cell.name;
    if (name.length() != desiredSettings.battery.cell.name.length()) {
      report.detail = "metadata allocation";
      return false;
    }
    active.battery.cell.name = std::move(name);
    active.battery.pack.capacity_mAh = desiredSettings.battery.pack.capacity_mAh;
    active.battery.cell.approx20PercentCapacityUnderMaxLoad_mV = desiredSettings.battery.cell.approx20PercentCapacityUnderMaxLoad_mV;
    active.battery.cell.overrideLimits = desiredSettings.battery.cell.overrideLimits;
    active.temperatureSensor = desiredSettings.temperatureSensor;
    active.power.charger.minCellVoltage_mV = desiredSettings.power.charger.minCellVoltage_mV;
    active.power.charger.maxCellVoltage_mV = desiredSettings.power.charger.maxCellVoltage_mV;
    active.ACRecoveryPeriodSeconds = desiredSettings.ACRecoveryPeriodSeconds;
    metadataPending = false;
  }
  if (!pendingPower) {
    if (!report.restartRequired) report.appliedRevision = report.desiredRevision;
    return false;
  }
  if (attempted && uint32_t(now - lastAttempt) < 5000) return false;
  const auto result = application.apply(desiredSettings);
  attempted = true;
  lastAttempt = now;
  report.powerState = result.state;
  report.detail = result.detail;
  report.actualInput_mA = result.actualInput_mA;
  report.inputClamped = result.inputClamped;
  if (result.state != ApplyState::APPLIED) return false;
  pendingPower = false;
  if (!report.restartRequired) report.appliedRevision = report.desiredRevision;
  return true;
}
}  // namespace Settings
