#pragma once

struct SyslogConfig {
  const char* serverHostname;
  int serverPort;
  const char* myHostname;
  const char* myAppname;
};

struct TemperatureSensorConfig {
  double R_vregn;            // resistor connected to REGN
  double R_gnd;              // resistor connected to GND
  double resistance_25degC;  // resistance of the NTC sensor at 25 degrees Celsius
  double beta;               // beta value of the NTC sensor
};