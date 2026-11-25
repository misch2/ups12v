#pragma once

#include "secret/michal_config.h"

#define BOARD_NAME "esp18"
#define DEVICE_NAME "bq25798-ups1"
#define HOSTNAME BOARD_NAME "-" DEVICE_NAME

constexpr Config::Pins boardPins{21, 22, 2, true, -1};

// Board-specific configuration for UPS1 ESP18
// Start with default config and override specific values
Config config = []() {
  Config cfg = michal_config;
  cfg.pins = boardPins;

  cfg.hardwareVersion = Config::HardwareVersion::V1_0;

  cfg.battery.cell.name = "GeB";
  cfg.battery.pack.capacity_mAh = 3200;
  cfg.battery.pack.maxChargeCurrent_mA = 700;          // Standard charge current for GeB 3200 mAh cells (fast is 0.5C, i.e., 1600 mA)
  cfg.battery.cell.approx80PercentCapacity_mV = 3920;  // Replace with the verified voltage for your cells. Zero is rejected.

  cfg.network.syslog.myHostname = BOARD_NAME;
  cfg.network.syslog.myAppname = DEVICE_NAME;
  cfg.network.mqtt.haDeviceName = HOSTNAME;

  cfg.power.backupMode = Config::Power::BackupMode::PMID_WITH_SWITCHOVER;

  cfg.power.charger.chargeProfile.mode = ChargeControl::Mode::APPROX_80;
  cfg.power.charger.ICHG_mA = 500;

  cfg.power.input.IINDPM_mA = 3000;

  cfg.power.output.IOTG_mA = 3200;

  return cfg;
}();
