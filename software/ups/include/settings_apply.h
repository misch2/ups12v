#pragma once

#include "charge_current.h"
#include "settings_service.h"

namespace Settings {
template <typename IC>
bool inputReady(IC& ic) {
  using PG = decltype(ic.getPG_STAT());
  using Vbus = decltype(ic.getVBUS_STAT());
  using Detection = decltype(ic.getDPDM_STAT());
  return ic.getPG_STAT() == PG::PG_STAT_GOOD && ic.getVBUS_STAT() != Vbus::VBUS_STAT_BACKUP_MODE &&
         ic.getVBUS_STAT() != Vbus::VBUS_STAT_OTG_MODE && !ic.getEN_OTG() && !ic.getEN_HIZ() &&
         !ic.getFORCE_INDET() && ic.getDPDM_STAT() == Detection::DPDM_STAT_NOT_STARTED;
}

// Caller revokes ARM before calling. No reset, CELL, HiZ or topology/backup-enable writes.
template <typename IC>
ApplyResult applyPowerSettings(const RuntimeSettings& settings, const Hardware::Profile& hardware, IC& ic, bool inhibitCharging) {
  auto fail = [&](const char* reason) {
    ic.setEN_CHG(false);  // Best effort; the caller keeps ARM LOW and revokes charger readiness.
    return ApplyResult(ApplyState::FAILED, reason);
  };
  ic.readAllRegisters();
  if (ic.lastError()) return fail("charger read");
  if (!inputReady(ic)) return {ApplyState::DEFERRED, "waiting for forward input / detection / HiZ"};
  const bool wasEnabled = ic.getEN_CHG();
  const int cells = static_cast<int>(ic.getCELL()) + 1;
  using PN = decltype(ic.getPN());
  if (settings.power.charger.chargeProfile.mode != ChargeControl::Mode::LEGACY && ic.getPN() != PN::PN_BQ25798) {
    return fail("managed profile requires BQ25798");
  }
  ic.setEN_CHG(false);
  if (ic.lastError()) return fail("disable charging");
  ic.readAllRegisters();
  if (ic.lastError() || ic.getEN_CHG()) return fail("disable charging readback");
  if (!inputReady(ic)) return {ApplyState::DEFERRED, "input changed before application"};
  if (settings.battery.pack.maxChargeCurrent_mA > 0) {
    const auto error = ChargeControl::applyCurrentLimit(settings.power.charger.ICHG_mA, settings.battery.pack.maxChargeCurrent_mA, ic);
    if (error) return fail(error);
  }
  const auto error = ChargeControl::apply(settings.power.charger.chargeProfile, cells, settings.battery.cell.approx80PercentCapacity_mV, ic, false);
  if (error) return fail(error);
  if (settings.power.input.VINDPM_mV > 0) ic.setVINDPM(settings.power.input.VINDPM_mV);
  if (settings.power.input.IINDPM_mA > 0) ic.setIINDPM(settings.power.input.IINDPM_mA);
  if (hardware.powerPath() == Hardware::PowerPath::PMID_WITH_SWITCHOVER) {
    if (settings.power.output.VOTG_mV > 0) ic.setVOTG(settings.power.output.VOTG_mV);
    if (settings.power.output.IOTG_mA > 0) ic.setIOTG(settings.power.output.IOTG_mA);
    ic.setVBUS_BACKUP(settings.power.input.VBUSBackupPercentage);
  }
  if (ic.lastError()) return fail("input/output write");
  ic.readAllRegisters();
  if (ic.lastError()) return fail("input/output readback");
  const int actualInput = ic.getIINDPM();
  const int expectedCurrent = ChargeControl::currentLimit_mA(settings.power.charger.ICHG_mA, settings.battery.pack.maxChargeCurrent_mA);
  const auto voltage = ChargeControl::plan(settings.power.charger.chargeProfile, cells, settings.battery.cell.approx80PercentCapacity_mV);
  const bool clamped = settings.power.input.IINDPM_mA > 0 && actualInput < settings.power.input.IINDPM_mA &&
                       actualInput >= 100 && ic.getEN_EXTILIM();
  const auto matches = [&]() {
    return static_cast<int>(ic.getCELL()) + 1 == cells &&
           (settings.battery.pack.maxChargeCurrent_mA == 0 ||
            (ic.getICHG() == expectedCurrent && ic.getIPRECHG() <= settings.battery.pack.maxChargeCurrent_mA / 40 * 40)) &&
           (settings.power.charger.chargeProfile.mode == ChargeControl::Mode::LEGACY ||
            (!voltage.error && ic.getVREG() == voltage.pack_mV &&
             (settings.power.charger.chargeProfile.rechargeOffset_mV == 0 ||
              ic.getVRECHG() == settings.power.charger.chargeProfile.rechargeOffset_mV))) &&
           (settings.power.input.VINDPM_mV <= 0 || ic.getVINDPM() == settings.power.input.VINDPM_mV) &&
           (settings.power.input.IINDPM_mA <= 0 || ic.getIINDPM() == settings.power.input.IINDPM_mA ||
            (clamped && ic.getIINDPM() == actualInput && ic.getEN_EXTILIM())) &&
           (hardware.powerPath() == Hardware::PowerPath::VSYS_UNINTERRUPTED ||
            ((settings.power.output.VOTG_mV <= 0 || ic.getVOTG() == settings.power.output.VOTG_mV) &&
             (settings.power.output.IOTG_mA <= 0 || ic.getIOTG() == settings.power.output.IOTG_mA) &&
             ic.getVBUS_BACKUP() == settings.power.input.VBUSBackupPercentage));
  };
  if (!matches()) return fail("input/output readback mismatch");
  if (!inputReady(ic)) return {ApplyState::DEFERRED, "input changed during application"};
  const bool enable = !inhibitCharging && settings.battery.pack.maxChargeCurrent_mA > 0 &&
                      (settings.power.charger.chargeProfile.mode != ChargeControl::Mode::LEGACY || wasEnabled);
  ic.setEN_CHG(enable);
  if (ic.lastError()) return fail("charge enable write");
  ic.readAllRegisters();
  if (ic.lastError() || ic.getEN_CHG() != enable || !matches()) return fail("final readback mismatch");
  if (!inputReady(ic)) {
    ic.setEN_CHG(false);
    return {ApplyState::DEFERRED, "input changed during charge enable"};
  }
  return {ApplyState::APPLIED, nullptr, ic.getIINDPM(), clamped};
}
}  // namespace Settings
