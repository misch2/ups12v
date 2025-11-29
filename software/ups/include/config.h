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

  struct Charger {
    int vbatChgEnableIfCellBelow_mV;   // Lower voltage at which the charger is enabled in mV
    int vbatChgDisableIfCellAbove_mV;  // Higher Voltage at which the charger is disabled in mV
    int ichg_mA;                       // Charge current in mA (max)
  };

  struct TemperatureSensor {
    double R_vregn;            // resistor connected to REGN
    double R_gnd;              // resistor connected to GND
    double resistance_25degC;  // resistance of the NTC sensor at 25 degrees Celsius
    double beta;               // beta value of the NTC sensor
  };

  // Hardware version
  const char* HW_VERSION;

  // Pin configuration
  Pins pins;

  // Network services
  Syslog syslog;
  MQTT mqtt;

  // Battery and charger settings
  Charger charger;
  TemperatureSensor temperatureSensor;

  // Power management settings
  int VINDPM_mV;  // Input voltage DPM threshold in mV
  int IINDPM_mA;  // Input current limit (DPM threshold) in mA
  int VOTG_mV;    // Output voltage for OTG mode
  int IOTG_mA;    // Output current for OTG mode in mA

  // Backup mode settings
  int AC_RECOVERY_PERIOD_SECONDS;  // time to wait for AC to be present and stable
  BQ25798::VBUS_BACKUP_t VBUS_BACKUP_PERCENTAGE;
};
