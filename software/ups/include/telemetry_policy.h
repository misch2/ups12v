#pragma once

#include <cstring>

namespace Telemetry {
enum class Policy { Disabled, ChangeOnly, Periodic };

// Production allowlist. Debug exposes all other registers on change only.
inline Policy registerPolicy(const char* name) {
  static const char* const periodic[] = {
      "IBUS_ADC",
      "IBAT_ADC",
      "VBUS_ADC",
      "VAC1_ADC",
      "VBAT_ADC",
      "VSYS_ADC",
      "TDIE_ADC",
      "PG_STAT",
      "AC1_PRESENT_STAT",
      "VBUS_PRESENT_STAT",
      "VBAT_PRESENT_STAT",
      "CHG_STAT",
      "VBUS_STAT",
      "EN_CHG",
      "EN_BACKUP",
      "EN_OTG",
      // Owner's Grafana series: retain these in production with periodic samples.
      "DIS_ACDRV",
      "EN_ACDRV1",
      "TS_ADC",
      "VINDPM_STAT",
  };
  static const char* const changeOnly[] = {
      // Applied limits, battery configuration and useful operating controls.
      "VSYSMIN",
      "VREG",
      "ICHG",
      "VINDPM",
      "IINDPM",
      "IPRECHG",
      "ITERM",
      "CELL",
      "VRECHG",
      "TRECHG",
      "VOTG",
      "IOTG",
      "VBUS_BACKUP",
      "EN_HIZ",
      "EN_TERM",
      "EN_AUTO_IBATDIS",
      "FORCE_IBATDIS",
      "WATCHDOG",
      "EN_ICO",
      "ICO_ILIM",
      "EN_EXTILIM",
      "EN_IINDPM",
      "EN_IBAT",
      "IBAT_REG",
      "TREG",
      "TSHUT",
      "TS_IGNORE",
      // Live limiting/fault states. Read-cleared interrupt flags and masks are excluded.
      "IINDPM_STAT",
      "WD_STAT",
      "ICO_STAT",
      "TREG_STAT",
      "DPDM_STAT",
      "VSYS_STAT",
      "CHG_TMR_STAT",
      "TRICHG_TMR_STAT",
      "PRECHG_TMR_STAT",
      "VBATOTG_LOW_STAT",
      "TS_COLD_STAT",
      "TS_COOL_STAT",
      "TS_WARM_STAT",
      "TS_HOT_STAT",
      "IBAT_REG_STAT",
      "VBUS_OVP_STAT",
      "VBAT_OVP_STAT",
      "IBUS_OCP_STAT",
      "IBAT_OCP_STAT",
      "CONV_OCP_STAT",
      "VAC1_OVP_STAT",
      "VAC2_OVP_STAT",
      "VSYS_SHORT_STAT",
      "VSYS_OVP_STAT",
      "OTG_OVP_STAT",
      "OTG_UVP_STAT",
      "TSHUT_STAT",
  };
  for (const char* entry : periodic) {
    if (std::strcmp(name, entry) == 0) return Policy::Periodic;
  }
  for (const char* entry : changeOnly) {
    if (std::strcmp(name, entry) == 0) return Policy::ChangeOnly;
  }
#ifdef DEBUG_BQ25798_SETTINGS
  return Policy::ChangeOnly;
#else
  return Policy::Disabled;
#endif
}
}  // namespace Telemetry
