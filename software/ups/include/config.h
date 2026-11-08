#pragma once

#include <BQ25798.h>

#include "charge_profile.h"

// Main configuration class containing all board-specific settings
class Config {
 public:
  struct Pins {
    // Each board_config.h must declare constexpr Config::Pins boardPins.
    // Use -1 explicitly for an absent LED; I2C pins are mandatory.
    constexpr Pins(int sda, int scl, int led, bool ledActiveHigh) : I2C_SDA(sda), I2C_SCL(scl), LED(led), LED_ACTIVE_HIGH(ledActiveHigh) {}

    int I2C_SDA;
    int I2C_SCL;
    int LED;
    bool LED_ACTIVE_HIGH;
  };

  struct Network {
    struct Syslog {
      const char* serverHostname = "logserver.localnet";
      int serverPort = 514;
      const char* myHostname = "default";
      const char* myAppname = "ups";
    };

    struct MQTT {
      const char* serverHostname = "mqtt.localnet";
      int serverPort = 1883;
      const char* user = "ups";
      const char* password = "6534GagEWGEWgew8743g3321";
      const char* haDeviceName = "default-ups";  // Home Assistant device name
    };

    Syslog syslog;
    MQTT mqtt;
  };

  struct TemperatureSensor {
    double R_vregn = 5600;               // resistor connected to REGN
    double R_gnd = 33000;                // resistor connected to GND
    double resistance_25degC = 10000.0;  // resistance of the NTC sensor at 25 degrees Celsius
    double beta = 3435.0;                // beta value of the NTC sensor
  };

  struct Power {
    // Power management settings
    enum BackupMode {
      PMID_WITH_SWITCHOVER = 0,
      VSYS_UNINTERRUPTED = 1,
    };

    struct Input {
      int IINDPM_mA = 1000;                                                                      // Input current limit (DPM threshold) in mA
      int VINDPM_mV = 11500;                                                                     // Input voltage DPM threshold in mV
      BQ25798::VBUS_BACKUP_t VBUSBackupPercentage = BQ25798::VBUS_BACKUP_t::PCT_VBUS_BACKUP_80;  // Backup mode setting
    };

    struct Charger {
      ChargeControl::Profile chargeProfile;  // LEGACY preserves existing board behavior.
      int minCellVoltage_mV = 3200;             // Minimum voltage of a single cell in mV for calculations of charge %
      int maxCellVoltage_mV = 4200;             // Maximum voltage of a single cell in mV for calculations of charge %
      int vbatChgEnableIfCellBelow_mV = 4100;   // Lower voltage at which the charger is enabled in mV
      int vbatChgDisableIfCellAbove_mV = 4155;  // Higher Voltage at which the charger is disabled in mV
      int ICHG_mA = 1000;                       // Charge current in mA (max)
    };

    struct Output {
      int IOTG_mA = 1200;   // Output current for OTG mode in mA
      int VOTG_mV = 12000;  // Output voltage for OTG mode
    };

    BackupMode backupMode = PMID_WITH_SWITCHOVER;
    Input input;
    Charger charger;
    Output output;
  };

  // Hardware version
  const char* hardwareVersion = "1.0";

  Pins pins{-1, -1, -1, true};  // Unassigned until explicitly set by the board profile.
  Network network;
  TemperatureSensor temperatureSensor;
  Power power;

  // Backup mode settings
  int ACRecoveryPeriodSeconds = 30;  // time to wait for AC to be present and stable
};
