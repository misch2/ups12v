#pragma once

namespace Hardware {
enum class Version { V1_0, V3_3B_SYS_MOD, V4_0 };
enum class MCU { ESP32, ESP32_C3 };
enum class PowerPath { PMID_WITH_SWITCHOVER, VSYS_UNINTERRUPTED };

struct Pins {
  // All five arguments are mandatory; -1 explicitly means an absent LED or ARM.
  constexpr Pins(int sda, int scl, int led, bool ledActiveHigh, int chargeArm)
      : I2C_SDA(sda), I2C_SCL(scl), LED(led), LED_ACTIVE_HIGH(ledActiveHigh), CHARGE_ARM(chargeArm) {}

  const int I2C_SDA;
  const int I2C_SCL;
  const int LED;
  const bool LED_ACTIVE_HIGH;
  const int CHARGE_ARM;  // Active HIGH permission; LOW inhibits the V4 CE_N driver.
};

struct Profile {
  constexpr Profile(Version version, Pins pins) : version(version), pins(pins) {}

  const Version version;
  const Pins pins;

  // Version selects its MCU and power path together; neither is a runtime setting.
  constexpr MCU mcu() const { return version == Version::V4_0 ? MCU::ESP32_C3 : MCU::ESP32; }
  constexpr PowerPath powerPath() const {
    return version == Version::V1_0 ? PowerPath::PMID_WITH_SWITCHOVER : PowerPath::VSYS_UNINTERRUPTED;
  }
  constexpr const char* versionName() const {
    return version == Version::V1_0 ? "1.0" : version == Version::V3_3B_SYS_MOD ? "3.3b-SYSmod" : version == Version::V4_0 ? "4.0" : "Unknown";
  }
};

constexpr Profile kV1Esp32{Version::V1_0, Pins{21, 22, 2, true, -1}};
constexpr Profile kV3SysEsp32{Version::V3_3B_SYS_MOD, Pins{21, 22, 2, true, -1}};
// U1 GPIO4/5 = MCU_SDA/SCL, GPIO0 = MCU_CHG_ARM; no fitted status LED.
constexpr Profile kV4Esp32C3{Version::V4_0, Pins{4, 5, -1, true, 0}};

// The TS resistor divider is identical on all supported revisions.
constexpr double kTsRegnResistanceOhm = 5600.0;
constexpr double kTsGroundResistanceOhm = 33000.0;
}  // namespace Hardware
