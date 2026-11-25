#pragma once

#include "hardware_profile.h"
#include "secret/michal_config.h"

#define BOARD_NAME "esp27"
#define DEVICE_NAME "bq25798-ups2"
#define HOSTNAME BOARD_NAME "-" DEVICE_NAME

constexpr Hardware::Profile hardware = Hardware::kV3SysEsp32;

RuntimeSettings config = []() {
  RuntimeSettings cfg = michal_config;

  cfg.battery.cell.name = "GeB";
  cfg.battery.pack.capacity_mAh = 3200;
  cfg.battery.pack.maxChargeCurrent_mA = 700;          // Standard charge current for GeB 3200 mAh cells (fast is 0.5C, i.e., 1600 mA)
  cfg.battery.cell.approx80PercentCapacity_mV = 3920;  // Replace with the verified voltage for your cells. Zero is rejected.

  cfg.network.syslog.myHostname = BOARD_NAME;
  cfg.network.syslog.myAppname = DEVICE_NAME;
  cfg.network.mqtt.haDeviceName = HOSTNAME;

  cfg.power.charger.chargeProfile.mode = ChargeControl::Mode::APPROX_80;
  cfg.power.charger.ICHG_mA = 500;

  cfg.power.input.VINDPM_mV = 4700;  // Input voltage DPM threshold in mV - because anything below this causes the charger to stop charging etc. so we don't
                                     // want minor VAC oscillations to cause this. On the other hand, setting it too low means that the IC won't mind pulling
                                     // the voltage down during high load (e.g. charging) to this limit.
  cfg.power.input.IINDPM_mA = 1500;  // Input current limit (DPM threshold) in mA -- this should reflect the max current the power source can provide

  return cfg;
}();
