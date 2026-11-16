#pragma once

#include "secret/michal_config.h"

#define BOARD_NAME "esp19"
#define DEVICE_NAME "bq25798-ups3"
#define HOSTNAME BOARD_NAME "-" DEVICE_NAME

constexpr Config::Pins boardPins{21, 22, 2, true, -1};

// Start with default config and override specific values
Config config = []() {
  Config cfg = michal_config;
  cfg.pins = boardPins;

  cfg.hardwareVersion = Config::HardwareVersion::V3_3B_SYS_MOD;

  cfg.battery.name = "GeB";
  cfg.battery.capacity_mAh = 3200;
  cfg.battery.maxChargeCurrent_mA = 700;          // Standard charge current for GeB 3200 mAh cells (fast is 0.5C, i.e., 1600 mA)
  cfg.battery.approx80PercentCapacity_mV = 3920;  // Replace with the verified voltage for your cells. Zero is rejected.

  cfg.network.syslog.myHostname = BOARD_NAME;
  cfg.network.syslog.myAppname = DEVICE_NAME;
  cfg.network.mqtt.haDeviceName = HOSTNAME;

  cfg.power.backupMode = Config::Power::BackupMode::VSYS_UNINTERRUPTED;

  cfg.power.charger.chargeProfile.mode = ChargeControl::Mode::APPROX_80;
  cfg.power.charger.ICHG_mA = 1000;

  return cfg;
}();
