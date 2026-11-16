// Example board configuration file

#pragma once

#include <BQ25798.h>

#include "config.h"

#define BOARD_NAME "board01-test"
#define DEVICE_NAME "bq25798-ups1"
#define HOSTNAME BOARD_NAME "-" DEVICE_NAME

constexpr Config::Pins boardPins{21, 22, 2, true, -1};

// Example board-specific configuration
// Start with default config and override specific values
Config config = []() {
  Config cfg;
  cfg.pins = boardPins;

  cfg.hardwareVersion = Config::HardwareVersion::V1_0;

  cfg.battery.name = "Example battery";
  cfg.battery.maxChargeCurrent_mA = 500;  // Replace with a qualified limit for the fitted pack.

  cfg.network.syslog.serverHostname = "logs.lan";
  cfg.network.syslog.myHostname = BOARD_NAME;
  cfg.network.syslog.myAppname = DEVICE_NAME;

  cfg.network.mqtt.serverHostname = "mqtt.lan";
  cfg.network.mqtt.user = "mqtt_user";
  cfg.network.mqtt.password = "secret_password";
  cfg.network.mqtt.haDeviceName = HOSTNAME;

  cfg.power.charger.vbatChgEnableIfCellBelow_mV = 4150;
  cfg.power.charger.vbatChgDisableIfCellAbove_mV = 4155;
  cfg.power.charger.ICHG_mA = 500;

  cfg.power.input.VINDPM_mV = 12000;
  cfg.power.input.IINDPM_mA = 3000;

  cfg.power.output.IOTG_mA = 3200;

  return cfg;
}();
