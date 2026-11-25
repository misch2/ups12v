#pragma once

#include <Arduino.h>
#include <BQ25798.h>

#include "charge_profile.h"
#include "power_override.h"

// Mutable settings only. Hardware identity, power path and pins live in Hardware::Profile.
// Text values own their storage so future persistence does not introduce dangling pointers.
class RuntimeSettings {
 public:
  struct Network {
    struct Syslog {
      String serverHostname = "logserver.localnet";
      int serverPort = 514;
      String myHostname = "default";
      String myAppname = "ups";
    };

    struct MQTT {
      String serverHostname = "mqtt.localnet";
      int serverPort = 1883;
      String user;
      String password;
      String haDeviceName = "default-ups";  // Stable device identifier, not an editable display name.
    };

    Syslog syslog;
    MQTT mqtt;
  };

  struct TemperatureSensor {
    double resistance_25degC = 10000.0;  // NTC resistance at 25 degrees Celsius.
    double beta = 3435.0;
  };

  struct Battery {
    struct Cell {
      String name = "Unspecified";
      int approx80PercentCapacity_mV = 0;              // APPROX_80 voltage for the fitted cells. Zero is rejected.
      int approx20PercentCapacityUnderMaxLoad_mV = 0;  // Warning voltage under maximum load; 0 means unspecified.
      PowerOverride::Limits overrideLimits;           // Per-cell thresholds applied to the pack's average cell voltage.
    };

    struct Pack {
      int capacity_mAh = 0;         // Nominal pack capacity; 0 means unspecified. Informational only.
      int maxChargeCurrent_mA = 0;  // Pack limit, >=100 mA; must be configured. Zero inhibits charging.
    };

    Cell cell;
    Pack pack;
  };

  struct Power {
    struct Input {
      bool retryUnqualifiedAdapter = false;  // V4-only opt-in: deferred FORCE_INDET and IINDPM restore.
      int IINDPM_mA = 1000;                  // Input current limit (DPM threshold) in mA.
      int VINDPM_mV = 11500;                 // Input voltage DPM threshold in mV.
      BQ25798::VBUS_BACKUP_t VBUSBackupPercentage = BQ25798::VBUS_BACKUP_t::PCT_VBUS_BACKUP_80;
    };

    struct Charger {
      ChargeControl::Profile chargeProfile;  // LEGACY preserves existing board behavior.
      int minCellVoltage_mV = 3200;          // Voltage endpoints for the legacy percent estimate.
      int maxCellVoltage_mV = 4200;
      int vbatChgEnableIfCellBelow_mV = 4100;
      int vbatChgDisableIfCellAbove_mV = 4155;
      int ICHG_mA = 1000;  // Requested current; capped by battery.pack.maxChargeCurrent_mA.
    };

    struct Output {
      int IOTG_mA = 1200;   // Output current for OTG mode in mA.
      int VOTG_mV = 12000;  // Output voltage for OTG mode.
    };

    Input input;
    Charger charger;
    Output output;
  };

  Network network;
  TemperatureSensor temperatureSensor;
  Battery battery;
  Power power;
  int ACRecoveryPeriodSeconds = 30;
};
