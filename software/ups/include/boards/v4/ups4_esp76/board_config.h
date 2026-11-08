#pragma once

#include "secret/michal_config.h"

#define BOARD_NAME "esp76"
#define DEVICE_NAME "bq25798-ups4"
#define HOSTNAME BOARD_NAME "-" DEVICE_NAME

// U1 GPIO4 = MCU_SDA, GPIO5 = MCU_SCL. MCU_STATUS_LED is an unconnected GPIO3 net.
constexpr Config::Pins boardPins{4, 5, -1, true};

// Start with default config and override specific values
Config config = []() {
  Config cfg = michal_config;
  cfg.pins = boardPins;

  cfg.hardwareVersion = "4.0";

  cfg.network.syslog.myHostname = BOARD_NAME;
  cfg.network.syslog.myAppname = DEVICE_NAME;
  cfg.network.mqtt.haDeviceName = HOSTNAME;

  cfg.power.backupMode = Config::Power::BackupMode::VSYS_UNINTERRUPTED;
  cfg.power.charger.ICHG_mA = 1000;

  // Just a test, comment out if needed to use default values:
  cfg.power.charger.vbatChgEnableIfCellBelow_mV = 9999;   // let the IC control the charger
  cfg.power.charger.vbatChgDisableIfCellAbove_mV = 9999;  // let the IC control the charger

  return cfg;
}();
