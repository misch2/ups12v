// Example board configuration file

#pragma once

#include <BQ25798.h>

#include "default_config.h"

#define BOARD_NAME "board01-test"
#define DEVICE_NAME "bq25798-ups1"
#define HOSTNAME BOARD_NAME "-" DEVICE_NAME

// Example board-specific configuration
// Start with default config and override specific values
Config config = []() {
  Config cfg = default_config;

  cfg.HW_VERSION = "1.0";

  cfg.syslog.serverHostname = "logs.lan";
  cfg.syslog.myHostname = BOARD_NAME;
  cfg.syslog.myAppname = DEVICE_NAME;

  cfg.mqtt.serverHostname = "mqtt.lan";
  cfg.mqtt.user = "mqtt_user";
  cfg.mqtt.password = "secret_password";
  cfg.mqtt.haDeviceName = HOSTNAME;

  cfg.charger.vbatChgEnableIfCellBelow_mV = 4150;
  cfg.charger.ichg_mA = 500;

  cfg.VINDPM_mV = 12000;
  cfg.IINDPM_mA = 3000;
  cfg.IOTG_mA = 3200;

  return cfg;
}();
