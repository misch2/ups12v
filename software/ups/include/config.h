#pragma once

#include <BQ25798.h>

// Main configuration class containing all board-specific settings
class Config {
 public:
  struct Pins {
    int I2C_SDA;  // GPIO pin for I2C SDA
    int I2C_SCL;  // GPIO pin for I2C SCL
    int LED;      // GPIO pin for the LED
  };

  struct Network {
    struct Syslog {
      const char* serverHostname;
      int serverPort;
      const char* myHostname;
      const char* myAppname;
    };

    struct MQTT {
      const char* serverHostname;
      int serverPort;
      const char* user;
      const char* password;
      const char* haDeviceName;  // Home Assistant device name
    };

    Syslog syslog;
    MQTT mqtt;
  };

  struct TemperatureSensor {
    double R_vregn;            // resistor connected to REGN
    double R_gnd;              // resistor connected to GND
    double resistance_25degC;  // resistance of the NTC sensor at 25 degrees Celsius
    double beta;               // beta value of the NTC sensor
  };

  struct Power {
    // Power management settings
    enum BackupMode {
      PMID_WITH_SWITCHOVER = 0,
      VSYS_UNINTERRUPTED = 1,
    };

    struct Input {
      int IINDPM_mA;                                // Input current limit (DPM threshold) in mA
      int VINDPM_mV;                                // Input voltage DPM threshold in mV
      BQ25798::VBUS_BACKUP_t VBUSBackupPercentage;  // Backup mode setting
    };

    struct Charger {
      int minCellVoltage_mV;             // Minimum voltage of a single cell in mV for calculations of charge %
      int maxCellVoltage_mV;             // Maximum voltage of a single cell in mV for calculations of charge %
      int vbatChgEnableIfCellBelow_mV;   // Lower voltage at which the charger is enabled in mV
      int vbatChgDisableIfCellAbove_mV;  // Higher Voltage at which the charger is disabled in mV
      int ICHG_mA;                       // Charge current in mA (max)
    };

    struct Output {
      int IOTG_mA;  // Output current for OTG mode in mA
      int VOTG_mV;  // Output voltage for OTG mode
    };

    BackupMode backupMode;
    Input input;
    Charger charger;
    Output output;
  };

  // Hardware version
  const char* hardwareVersion;

  Pins pins;
  Network network;
  TemperatureSensor temperatureSensor;
  Power power;

  // Backup mode settings
  int ACRecoveryPeriodSeconds;  // time to wait for AC to be present and stable
};
