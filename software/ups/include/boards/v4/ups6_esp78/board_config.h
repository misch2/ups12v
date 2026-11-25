#pragma once

#include "hardware_profile.h"
#include "secret/michal_config.h"

#define BOARD_NAME "esp78"
#define DEVICE_NAME "bq25798-ups6"
#define HOSTNAME BOARD_NAME "-" DEVICE_NAME

// U1 GPIO4 = MCU_SDA, GPIO5 = MCU_SCL. MCU_STATUS_LED is an unconnected GPIO3 net.
constexpr Hardware::Profile hardware = Hardware::kV4Esp32C3;

// Transitional device settings; hardware is selected independently above.
RuntimeSettings config = []() {
  RuntimeSettings cfg = michal_config;

  cfg.battery.cell.name = "Liitokala";
  cfg.battery.pack.capacity_mAh = 3400;
  // see https://www.mdpi.com/2313-0105/9/4/214 and https://passionelectronique.fr/wp-content/uploads/NCR18650B_datasheet.pdf?pseSrc=pgAlimUsb18650v2
  cfg.battery.pack.maxChargeCurrent_mA = 700;  // Standard 0.25C charge current (fast/max is 0.5 C = 1625 mA)
  cfg.battery.cell.approx80PercentCapacity_mV = 3955;
  cfg.battery.cell.approx20PercentCapacityUnderMaxLoad_mV = 3300;

  cfg.network.syslog.myHostname = BOARD_NAME;
  cfg.network.syslog.myAppname = DEVICE_NAME;
  cfg.network.mqtt.haDeviceName = HOSTNAME;

  cfg.power.input.retryUnqualifiedAdapter = true;  // Enable retry for USB-PD trigger which changes the input detection state

  cfg.power.charger.chargeProfile.mode = ChargeControl::Mode::APPROX_80;
  cfg.power.charger.ICHG_mA = 500;

  // Don't restrict input current too aggressively, allow up to 3A for the input
  cfg.power.input.IINDPM_mA = 3000;

  return cfg;
}();
