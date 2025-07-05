#pragma once

namespace config {
struct Pins {
  int I2C_SDA;  // GPIO pin for I2C SDA
  int I2C_SCL;  // GPIO pin for I2C SCL
  int LED;     // GPIO pin for the LED
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
  int batteryCellCount;              // Number of battery cells in series
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
}  // namespace config