#include <ArduinoJson.h>
#include <ArduinoOTA.h>
#include <BQ25798.h>
#include <PubSubClient.h>
#include <Syslog.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <arduino-timer.h>

#include <array>

#include "board_config.h"
#include "homeassistant_mqtt.h"
#include "led_blinker.h"
#include "logger.h"
#include "version.h"

constexpr long ONE_SECOND_IN_MILLIS = 1000;
constexpr double ONE_VOLT_IN_MILLIVOLTS = 1000.0;
constexpr double ONE_AMP_IN_MILLIAMPS = 1000.0;
constexpr double ZERO_DEGC_IN_KELVINS = 273.15;

constexpr int min_cell_voltage_mV = 2900;
constexpr int max_cell_voltage_mV = 4200;

Logger logger(nullptr, &Serial);  // create a logger instance with Serial as the output stream
WiFiUDP udpClient;
WiFiManager wifiManager;
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
BQ25798 bq25798 = BQ25798();
HomeAssistant::MQTT haClient(mqttClient, logger, config::mqtt.haDeviceName);
Syslog* syslog = nullptr;
LEDBlinker ledBlinker(config::pins.LED);
Timer<10> timers;

std::array<int, BQ25798::SETTINGS_COUNT> oldRawValue;
std::array<int, BQ25798::SETTINGS_COUNT> newRawValue;
std::array<HomeAssistant::EntityMultiConfig, BQ25798::SETTINGS_COUNT> haConfig;

HomeAssistant::EntityConfig haConfigUptime{HomeAssistant::EntityBaseConfig{
    .component = "sensor",
    .config_key = "uptime",
    .state_key = "uptime",
    .entity_category = "diagnostic",
    .device_class = "duration",
    .state_class = "measurement",
    .unit_of_measurement = "s",
    .name = "Uptime",
    .icon = "mdi:chart-box-outline",
}};

HomeAssistant::EntityConfig haConfigBatteryTemperature{HomeAssistant::EntityBaseConfig{
    .component = "sensor",
    .config_key = "battery_temperature",
    .state_key = "battery_temperature",
    .entity_category = "diagnostic",
    .device_class = "temperature",
    .state_class = "measurement",
    .unit_of_measurement = "°C",
    .name = "Battery Temperature",
    .icon = "mdi:thermometer",
}};
HomeAssistant::EntityConfig haConfigBatteryPercent{HomeAssistant::EntityBaseConfig{
    .component = "sensor",
    .config_key = "battery_percent",
    .state_key = "battery_percent",
    .entity_category = "diagnostic",
    .device_class = "battery",
    .state_class = "measurement",
    .unit_of_measurement = "%",
    .name = "Battery Percent",
    .icon = "",
}};
HomeAssistant::EntityConfig haConfigPBAT{HomeAssistant::EntityBaseConfig{
    .component = "sensor",
    .config_key = "PBAT",
    .state_key = "PBAT",
    .entity_category = "diagnostic",
    .device_class = "power",
    .state_class = "measurement",
    .unit_of_measurement = "W",
    .name = "",
    .icon = "",
}};
HomeAssistant::EntityConfig haConfigPBUS{HomeAssistant::EntityBaseConfig{
    .component = "sensor",
    .config_key = "PBUS",
    .state_key = "PBUS",
    .entity_category = "diagnostic",
    .device_class = "power",
    .state_class = "measurement",
    .unit_of_measurement = "W",
    .name = "",
    .icon = "",
}};
HomeAssistant::EntityConfig haConfigResetButton{HomeAssistant::EntityBaseConfig{
    .component = "button",
    .config_key = "reset_button",
    .state_key = "reset_button",
    .entity_category = "config",
    .device_class = "",
    .state_class = "",
    .unit_of_measurement = "",
    .name = "Reset BQ25798",
    .icon = "mdi:restart",
}};

HomeAssistant::EntityConfig haConfigReconfigureButton{HomeAssistant::EntityBaseConfig{
    .component = "button",
    .config_key = "reconfigure_button",
    .state_key = "reconfigure_button",
    .entity_category = "config",
    .device_class = "",
    .state_class = "",
    .unit_of_measurement = "",
    .name = "Reconfigure BQ25798",
    .icon = "mdi:reload",
}};

String fix_unit(String unit) {
  if (unit == "degC") {
    return "°C";
  }
  return unit;
}

void patWatchdog() {
  // To keep the device in host mode, the host has  to reset the watchdog timer
  // by writing 1 to WD_RST bit before the watchdog timer expires
  bq25798.setWD_RST(true);  // reset the watchdog timer
}

bool checkForError() {
  if (bq25798.lastError()) {
    logger.log(LOG_ERR, "Error: %d\n", bq25798.lastError());
    bq25798.clearError();
    return true;
  }
  return false;
}

bool firstRun = true;  // flag to indicate if this is the first run of the loop
void trackChanges() {
  long now = millis();

  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    BQ25798::Setting setting = bq25798.getSetting(i);
    newRawValue[i] = bq25798.getRaw(setting);
    if (checkForError()) {
      logger.log(LOG_ERR, "Error reading setting %d (%s)\n", i, setting.name);
      return;  // stop tracking changes if there is an error
    }
  }

  if (firstRun) {
    for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
      oldRawValue[i] = newRawValue[i];
    }
  }

  // every next time check if the values changed
  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    BQ25798::Setting setting = bq25798.getSetting(i);

    // exception: do not notify about flags set to FALSE because any read
    // operation will reset them to FALSE
    if (setting.is_flag && newRawValue[i] == 0) {
      continue;
    }

    if (setting.type == BQ25798::settings_type_t::BOOL) {
      if (!setting.is_flag) {
        bool old_val = bq25798.rawToBool(oldRawValue[i], setting);
        bool new_val = bq25798.rawToBool(newRawValue[i], setting);
        haClient.publishStateIfNeeded(haConfig[i].configBinarySensor, new_val ? "ON" : "OFF", firstRun || oldRawValue[i] != newRawValue[i]);

        if (oldRawValue[i] != newRawValue[i]) {
          logger.log(LOG_INFO, "%s changed to %s (from %s)", setting.name, new_val ? "ON" : "OFF", old_val ? "ON" : "OFF");
        }
      }

    } else if (setting.type == BQ25798::settings_type_t::ENUM) {
      const char* old_val_string = bq25798.rawToString(oldRawValue[i], setting);
      const char* new_val_string = bq25798.rawToString(newRawValue[i], setting);
      int old_val_int = bq25798.rawToInt(oldRawValue[i], setting);
      int new_val_int = bq25798.rawToInt(newRawValue[i], setting);

      haClient.publishStateIfNeeded(haConfig[i].configText, new_val_string, firstRun || oldRawValue[i] != newRawValue[i]);
      haClient.publishStateIfNeeded(haConfig[i].configSensor, String(new_val_int), firstRun || oldRawValue[i] != newRawValue[i]);
      haClient.publishStateIfNeeded(haConfig[i].configBinarySensor, String(new_val_int ? "ON" : "OFF"), firstRun || oldRawValue[i] != newRawValue[i]);

      if (oldRawValue[i] != newRawValue[i]) {
        logger.log(LOG_INFO, "%s changed to \"%s\" (%d), was \"%s\" (%d)", setting.name, new_val_string, new_val_int, old_val_string, old_val_int);
      }

    } else if (setting.type == BQ25798::settings_type_t::INT) {
      // Float and int values are sent only on HA timeout, not on every tiny change
      int old_val = bq25798.rawToInt(oldRawValue[i], setting);
      int new_val = bq25798.rawToInt(newRawValue[i], setting);
      haClient.publishStateIfNeeded(haConfig[i].configSensor, String(new_val),
                                    firstRun || (abs(old_val - new_val) > abs(old_val * 0.1)));  // 10% change is enough to notify

    } else if (setting.type == BQ25798::settings_type_t::FLOAT) {
      // Float and int values are sent only on HA timeout, not on every tiny change
      float old_val = bq25798.rawToFloat(oldRawValue[i], setting);
      float new_val = bq25798.rawToFloat(newRawValue[i], setting);
      haClient.publishStateIfNeeded(haConfig[i].configSensor, String(new_val),
                                    firstRun || (abs(old_val - new_val) > abs(old_val * 0.1)));  // 10% change is enough to notify
    }
  }

  // update the old values
  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    oldRawValue[i] = newRawValue[i];
  }
  firstRun = false;
}

void sendCalculatedValues() {
  // Send calculated values
  double ts_adc = bq25798.getTS_ADC() / 100.0;  // convert from percent to 0.0-1.0 range
  double ts_combo_resistance = ts_adc * config::temperatureSensor.R_vregn / (1.0 - ts_adc);
  double ts_resistance = 1.0 / (1.0 / ts_combo_resistance - 1.0 / config::temperatureSensor.R_gnd);
  double ts_temperature =
      1.0 / (1.0 / (ZERO_DEGC_IN_KELVINS + 25.0) + log(ts_resistance / config::temperatureSensor.resistance_25degC) / config::temperatureSensor.beta) -
      ZERO_DEGC_IN_KELVINS;
  haClient.publishStateIfNeeded(&haConfigBatteryTemperature, String(ts_temperature, 1));

  double vbat_percent = 100 * (bq25798.getVBAT_ADC() / config::charger.batteryCellCount - min_cell_voltage_mV) / (max_cell_voltage_mV - min_cell_voltage_mV);
  vbat_percent = constrain(vbat_percent, 0.0, 100.0);  // constrain to 0-100%
  haClient.publishStateIfNeeded(&haConfigBatteryPercent, String(vbat_percent), firstRun);

  double bat_power = (bq25798.getIBAT_ADC() / ONE_AMP_IN_MILLIAMPS) * (bq25798.getVBAT_ADC() / ONE_VOLT_IN_MILLIVOLTS);
  haClient.publishStateIfNeeded(&haConfigPBAT, String(bat_power), firstRun);

  // FIXME debug only to find out why negative IBAT_ADC values are incorrectly reported
  if (0) {  // bat_power < 0) {
    auto setting = bq25798.IBAT_ADC;
    int ibat_raw = bq25798.getRaw(setting);
    logger.log(LOG_INFO, "IBAT_ADC raw value: 0x%04x, decoded=%d", ibat_raw, bq25798.rawToInt(ibat_raw, setting));

    //     // Vrací 0x???? -> , ale mělo by to být okolo -1000 mA cca
    //     IBAT_ADC raw value: 0xfffa, decoded=-6
    // 2025-07-03T15:01:30.002658+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿IBAT_ADC raw value: 0xfff7, decoded=-9
    // 2025-07-03T15:01:35.004086+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿IBAT_ADC raw value: 0xfff5, decoded=-11
    // 2025-07-03T15:01:40.010096+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿IBAT_ADC raw value: 0xfff9, decoded=-7
    // 2025-07-03T15:01:45.004500+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿IBAT_ADC raw value: 0xfffb, decoded=-5
    // 2025-07-03T15:01:50.009417+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿IBAT_ADC raw value: 0xfffa, decoded=-6
    // 2025-07-03T15:01:55.037778+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿IBAT_ADC raw value: 0xfffe, decoded=-2

    // 2025-07-03T15:04:08.397442+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿IBAT_ADC raw value: 0x011e, decoded=286
    // 2025-07-03T15:04:13.213636+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿IBAT_ADC raw value: 0x0119, decoded=281
    // 2025-07-03T15:04:18.216433+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿IBAT_ADC raw value: 0x0110, decoded=272
    // 2025-07-03T15:04:23.218511+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿IBAT_ADC raw value: 0x010c, decoded=268
    // 2025-07-03T15:04:28.220905+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿IBAT_ADC raw value: 0x0104, decoded=260
  }

  double bus_power = (bq25798.getIBUS_ADC() / ONE_AMP_IN_MILLIAMPS) * (bq25798.getVBUS_ADC() / ONE_VOLT_IN_MILLIVOLTS);
  haClient.publishStateIfNeeded(&haConfigPBUS, String(bus_power), firstRun);

  haClient.publishStateIfNeeded(&haConfigUptime, String(millis() / ONE_SECOND_IN_MILLIS));

  haClient.publishStateIfNeeded(&haConfigResetButton, "available");        // maybe not needed, but just in case
  haClient.publishStateIfNeeded(&haConfigReconfigureButton, "available");  // maybe not needed, but just in case
}

void checkChargerStatus() {
  // Enable the charger if everything is normal
  if (bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_GOOD  //
      && bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    int cell_mV = bq25798.getVBAT_ADC() / config::charger.batteryCellCount;
    if (cell_mV > config::charger.vbatChgDisableIfCellAbove_mV &&  //
        (bq25798.getCHG_STAT() == BQ25798::CHG_STAT_t::CHG_STAT_NOT_CHARGING || bq25798.getCHG_STAT() == BQ25798::CHG_STAT_t::CHG_STAT_TERMINATED)) {
      if (bq25798.getEN_CHG() == true) {
        logger.log(LOG_INFO,
                   "Disabling charger, power is good, charger is not charging and battery cell (%d) is "
                   "above limit (%d) ...",
                   cell_mV, config::charger.vbatChgDisableIfCellAbove_mV);
        bq25798.setEN_CHG(false);  // disable the charger
      }
    } else if (cell_mV < config::charger.vbatChgEnableIfCellBelow_mV) {
      if (bq25798.getEN_CHG() == false) {
        logger.log(LOG_INFO,
                   "Enabling charger, power is good and battery cell (%d mV) is "
                   "below limit (%d mV)...",
                   cell_mV, config::charger.vbatChgEnableIfCellBelow_mV);
        bq25798.setEN_CHG(true);  // enable the charger
      }
    }
  }
}

void onetimeSetupIfNeeded(bool force = false, bool reset = false) {
  if (bq25798.getVAC2_ADC_DIS() && !force) {
    // VAC2_ADC_DIS is false by default, so if it is true, it means the IC has already been initialized by us
    logger.log(LOG_INFO, "IC already initialized, skipping full reset.");
    return;
  }

  if (reset) {
    logger.log(LOG_INFO, "Resetting the IC completely...");
    bq25798.setREG_RST(true);  // reset the IC
    while (bq25798.getREG_RST()) {
      ledBlinker.loop();
      ArduinoOTA.handle();
      delay(10);
      bq25798.readAllRegisters();
    }
    logger.log(LOG_INFO, "Reset successful.");
  }

  logger.log(LOG_INFO, "Configuring BQ25798...");
  // FIXME to prevent chip reset when the host controller is disconnected
  // temporarily
  bq25798.setWATCHDOG(BQ25798::WATCHDOG_t::WATCHDOG_DISABLE);  // disable watchdog timer

  // enable continuous ADC readout
  bq25798.setADC_RATE(BQ25798::ADC_RATE_t::ADC_RATE_CONTINUOUS);
  bq25798.setADC_SAMPLE(BQ25798::ADC_SAMPLE_t::ADC_SAMPLE_15BIT);
  bq25798.setADC_EN(true);  // trigger ADC one-shot mode

  bq25798.setIBUS_ADC_DIS(false);  // enable IBUS ADC
  bq25798.setIBAT_ADC_DIS(false);  // enable IBAT ADC
  bq25798.setVAC2_ADC_DIS(true);   // disable VAC2 ADC (not used)

  // Disable HIZ mode (high impedance mode):
  bq25798.setEN_HIZ(false);

  // Disable input type detection:
  bq25798.setAUTO_INDET_EN(false);

  bq25798.setVOTG(config::VOTG_mV);
  bq25798.setIOTG(config::IOTG_mA);
  bq25798.setVINDPM(config::VINDPM_mV);
  bq25798.setIINDPM(config::IINDPM_mA);
  bq25798.setICHG(config::charger.ichg_mA);

  bq25798.setVBUS_BACKUP(BQ25798::VBUS_BACKUP_t::PCT_VBUS_BACKUP_80);  // VBUS backup percentage (80 % of 12 V = 9.6 V, etc.);

  // Enable BACKUP mode:
  bq25798.setEN_BACKUP(true);

  logger.log(LOG_INFO, "Configuration complete.");
}

bool waitForBQCondition(bool (*condition)(), int timeoutMillis = 5000) {
  long startTime = millis();
  bq25798.readAllRegisters();
  while (!condition()) {
    ledBlinker.loop();
    ArduinoOTA.handle();
    // timers.tick(); // NO, do not use timers.tick() here, we do not want any side effects here, it might asynchronously change the state of IC in
    // readmBackupMode() etc.
    if (millis() - startTime > timeoutMillis) {
      return false;
    }
    delay(10);
    bq25798.readAllRegisters();
  }
  // timers.tick();
  return true;
}

// FIXME crossover?
// 2025-07-03T15:03:03.547072+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿AC1 is present and stable, exiting backup mode and re-arming...
// 2025-07-03T15:03:03.562858+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿Exiting backup mode and re-arming UPS...
// 2025-07-03T15:03:03.563680+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿Disabling charger...
// 2025-07-03T15:03:03.579323+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿Setting BKUP_ACFET1_ON to 1...
// 2025-07-03T15:03:03.582061+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿Waiting for a confirmation of ACFET1 enabled...

// This is new invocation:!!!
//    2025-07-03T15:03:03.583070+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿AC1 is present and stable, exiting backup mode and re-arming...
//    2025-07-03T15:03:03.588912+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿Exiting backup mode and re-arming UPS...
//    2025-07-03T15:03:03.593663+02:00 10.52.4.16 (esp18) daemon.err bq25798-ups1:﻿Error: VBUS_STAT is not BACKUP_MODE

// An we continue:
// 2025-07-03T15:03:03.596559+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿Proceeding to exit OTG mode...
// 2025-07-03T15:03:03.613001+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿Waiting for a confirmation of OTG disabled and backup re-enabled...
// 2025-07-03T15:03:03.624057+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿Waiting for PG_STAT to be GOOD...
// 2025-07-03T15:03:03.740538+02:00 10.52.4.16 (esp18) daemon.info bq25798-ups1:﻿Backup mode re-armed.

void rearmBackupMode() {
  // Re-arm the backup mode by setting EN_BACKUP to false and then true again
  bq25798.readAllRegisters();

  logger.log(LOG_INFO, "Exiting backup mode and re-arming UPS...");

  // When a backup mode is entered automatically, the following happens:
  // DIS_ACDRV is set to TRUE, EN_OTG is set to TRUE, EN_ACDRV1 is set to FALSE,
  // PG is set to FALSE and VBUS_STAT is set to "Backup"
  //
  // So let's check if we are still in backup mode:

  if (bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    logger.log(LOG_ERR, "Error: VBUS_STAT is not BACKUP_MODE, is: %d", bq25798.getVBUS_STAT());
    return;
  }
  if (!bq25798.getDIS_ACDRV()) {
    logger.log(LOG_ERR, "In backup mode Error: ACDRV is not globally disabled, cannot re-arm.");
    return;
  }
  if (!bq25798.getEN_OTG()) {
    logger.log(LOG_ERR, "In backup mode Error: OTG is not active, cannot re-arm.");
    return;
  }

  // See page 37 of the BQ25798 datasheet:
  // If there is an adapter reconnected while the charger is in backup mode, the
  // user may transition the source which powers the PMID load from the battery
  // back to the adapter. The following sequence is used to switch from the
  // battery power back to ACIN1 while simultaneously re-arming the backup mode:
  // 1. Write BKUP_ACFET1_ON (REG0x16[0]) register bit to 1. Setting BKUP_ACFET1
  // _ON = 1 will cause the device to set DIS_ACDRV = 0 and EN_ACDRV1 = 1. After
  // that, backup mode is disabled, however, the charger remains in the normal
  // OTG mode. The ACFET1-RBFET1 is turned on to connect the adapter to VBUS.
  // The user must ensure the adapter voltage is equal to or higher than the
  // charger VOTG voltage setting, otherwise, the charger OTG output might back
  // drive the adapter connected to VBUS.
  // 2. Determine the source at ACIN1 is valid (is not in overvoltage and did
  // not fail poor source detection) by reading back EN_ACDRV1 as 1.
  // 3. Set EN_OTG = 0, in order to exit OTG mode and enter the forward charging
  // mode without PMID voltage crash. Setting BKUP_ACFET1_ON = 1, also clears
  // BKUP_ACFET1_ON to 0 and sets EN_BACKUP to 1.

  if (bq25798.getAC1_PRESENT_STAT() != BQ25798::AC1_PRESENT_STAT_t::AC1_PRESENT_STAT_PRESENT) {
    logger.log(LOG_ERR, "Error: AC1 is not present, cannot re-arm.");
    return;
  }

  // Disable charger to prevent any charging while we are in the OTG mode
  logger.log(LOG_INFO, "Disabling charger...");
  bq25798.setEN_CHG(false);  // disable the charger

  // BKUP_ACFET1_ON does the following:
  // - set DIS_ACDRV to 0 && set EN_ACDRV1 to 1 (enable ACDRV1)
  // - set EN_BACKUP to 0 (disable backup mode) -- why does it do this???
  // - set BKUP_ACFET1_ON to 1
  // it also sets the VBUS_STAT to OTG
  logger.log(LOG_INFO, "Setting BKUP_ACFET1_ON to 1...");
  bq25798.setBKUP_ACFET1_ON(true);  // turn on the ACFET1-RBFET1 to connect the adapter to VBUS

  logger.log(LOG_INFO, "Waiting for a confirmation of ACFET1 enabled...");
  if (!waitForBQCondition([]() { return bq25798.getEN_ACDRV1() == true; })) {
    logger.log(LOG_ERR, "Error: failed to turn ACDRV1 on.");
    return;
  }

  // EN_OTG should do the following when BKUP_ACFET1_ON is active:
  // - set EN_OTG to 0 (exit OTG mode)
  // - set EN_BACKUP to 1 (re-arm backup mode -- that's because BKUP_ACFET1_ON
  // is still set to 1)
  // - set BKUP_ACFET1_ON to 0
  // it also sets VBUS_STAT to normal input mode
  logger.log(LOG_INFO, "Proceeding to exit OTG mode...");
  bq25798.setEN_OTG(false);  // exit OTG mode and enter the forward charging
                             // mode without PMID voltage crash

  logger.log(LOG_INFO, "Waiting for a confirmation of OTG disabled and backup re-enabled...");
  if (!waitForBQCondition([]() { return bq25798.getEN_OTG() == false && bq25798.getEN_BACKUP() == true; })) {
    logger.log(LOG_ERR, "Error: failed to exit OTG mode and re-arm.");
    return;
  }

  logger.log(LOG_INFO, "Waiting for PG_STAT to be GOOD...");
  if (!waitForBQCondition([]() { return bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_GOOD; })) {
    logger.log(LOG_ERR, "Error: failed to re-arm backup mode, PG_STAT is not GOOD.");
    return;
  }

  logger.log(LOG_INFO, "Backup mode re-armed.");
}

void MQTTcallback(char* topic, byte* payload, unsigned int length) {
  String topicString = String(topic);

  String payloadString = "";
  for (int i = 0; i < length; i++) {
    payloadString += (char)payload[i];
  }

  logger.log(LOG_INFO, "Message arrived on topic %s, payload %s", topicString.c_str(), payloadString.c_str());

  if (topicString == haClient.getCommandTopic(&haConfigResetButton)) {
    onetimeSetupIfNeeded(true, true);  // force reset the IC and re-initialize it
    return;
  } else if (topicString == haClient.getCommandTopic(&haConfigReconfigureButton)) {
    onetimeSetupIfNeeded(true, false);  // reinitialize the IC without resetting it
    publishHAConfigurations();
    return;
  }
}

void setupWiFi() {
  logger.log(LOG_INFO, "Starting WiFi manager...");
  // Connect to WiFi
  wifiManager.setHostname(HOSTNAME);
  wifiManager.setConnectRetries(5);
  wifiManager.setConnectTimeout(15);           // in seconds
  wifiManager.setConfigPortalTimeout(3 * 60);  // Stay 3 minutes max in the AP web portal, then reboot
  bool res = wifiManager.autoConnect();
  if (!res) {
    logger.log(LOG_ERR, "Failed to connect to wifi, rebooting.");
    ESP.restart();
  }
  if (WiFi.localIP() == IPAddress(0, 0, 0, 0)) {
    logger.log(LOG_ERR, "Failed to get an IP address, rebooting.");
    ESP.restart();
  }
  logger.log(LOG_INFO, "Connected to WiFi: %s (%s)\n", WiFi.SSID().c_str(), WiFi.localIP().toString().c_str());
}

void setupOTA() {
  logger.log(LOG_INFO, "Starting OTA service...");
  ArduinoOTA.setHostname(HOSTNAME);
  ArduinoOTA.begin();
  ArduinoOTA.onStart([]() { logger.log(LOG_INFO, "OTA Start"); });
  ArduinoOTA.onEnd([]() { logger.log(LOG_INFO, "OTA End"); });
  ArduinoOTA.onError([](ota_error_t error) {
    if (error == OTA_AUTH_ERROR) {
      logger.log(LOG_ERR, "OTA Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      logger.log(LOG_ERR, "OTA Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      logger.log(LOG_ERR, "OTA Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      logger.log(LOG_ERR, "OTA Receive Failed");
    } else if (error == OTA_END_ERROR) {
      logger.log(LOG_ERR, "OTA End Failed");
    }
  });
  logger.log(LOG_INFO, "OTA service started successfully.");
}

void setupSyslog() {
  logger.log(LOG_INFO, "Resolving syslog server hostname: %s", config::syslog.serverHostname);
  IPAddress syslogServer;
  if (WiFi.hostByName(config::syslog.serverHostname, syslogServer)) {
    logger.log(LOG_INFO, "Syslog server IP: %s", syslogServer.toString().c_str());
    // Create a new syslog instance with LOG_KERN facility
    syslog = new Syslog(udpClient, syslogServer, config::syslog.serverPort, config::syslog.myHostname, config::syslog.myAppname, LOG_DAEMON);
    if (syslog != nullptr) {
      logger.setSyslog(syslog);  // set the syslog instance in the logger
      logger.log(LOG_INFO, "Syslog instance created successfully, firmware version: %s", FIRMWARE_VERSION);
    } else {
      logger.log(LOG_ERR, "Failed to create syslog instance.");
    }
  } else {
    logger.log(LOG_ERR, "Failed to resolve syslog server hostname: %s", config::syslog.serverHostname);
  };
}

void setupMQTT() {
  logger.log(LOG_INFO, "Starting MQTT client...");
  mqttClient.setServer(config::mqtt.serverHostname, config::mqtt.serverPort);
  mqttClient.setBufferSize(1024);  // set the MQTT buffer size to 1 KB
  mqttClient.setKeepAlive(60);     // set the keep-alive interval to 60 seconds
  mqttClient.setCallback(MQTTcallback);

  reconnectMQTTIfNeeded();
}

void publishHAConfigurations() {
  logger.log(LOG_INFO, "Publishing Home Assistant configurations...");
  haClient.publishConfiguration(&haConfigUptime);
  haClient.publishConfiguration(&haConfigBatteryTemperature);
  haClient.publishConfiguration(&haConfigBatteryPercent);
  haClient.publishConfiguration(&haConfigPBAT);
  haClient.publishConfiguration(&haConfigPBUS);
  haClient.publishConfiguration(&haConfigResetButton);

  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    BQ25798::Setting setting = bq25798.getSetting(i);
    if (setting.type == BQ25798::settings_type_t::BOOL) {
      if (!setting.is_flag) {
        haConfig[i].configBinarySensor = new HomeAssistant::EntityConfig{HomeAssistant::EntityBaseConfig{
            .component = "binary_sensor",
            .config_key = setting.name,
            .state_key = setting.name,
            .entity_category = "diagnostic",
            .device_class = "",
            .state_class = "measurement",
            .unit_of_measurement = fix_unit(setting.unit),
            .name = setting.name,
            .icon = "",
        }};
      }
    } else if (setting.type == BQ25798::settings_type_t::ENUM) {
      haConfig[i].configText = new HomeAssistant::EntityConfig{HomeAssistant::EntityBaseConfig{
          .component = "text",
          .config_key = setting.name,
          .state_key = String(setting.name) + "_string",
          .entity_category = "diagnostic",
          .device_class = "",
          .state_class = "measurement",
          .unit_of_measurement = fix_unit(setting.unit),
          .name = setting.name,
          .icon = "",
      }};
      haConfig[i].configSensor = new HomeAssistant::EntityConfig{HomeAssistant::EntityBaseConfig{
          .component = "sensor",
          .config_key = setting.name,
          .state_key = String(setting.name) + "_numeric",
          .entity_category = "diagnostic",
          .device_class = "",
          .state_class = "measurement",
          .unit_of_measurement = fix_unit(setting.unit),
          .name = setting.name,
          .icon = "",
      }};
      if (setting.range_low == 0 && setting.range_high == 1) {
        // If the enum is a boolean, create a binary sensor too
        haConfig[i].configBinarySensor = new HomeAssistant::EntityConfig{HomeAssistant::EntityBaseConfig{
            .component = "binary_sensor",
            .config_key = setting.name,
            .state_key = String(setting.name) + "_bool",
            .entity_category = "diagnostic",
            .device_class = "",
            .state_class = "measurement",
            .unit_of_measurement = fix_unit(setting.unit),
            .name = setting.name,
            .icon = "",
        }};
      }
    } else {
      haConfig[i].configSensor = new HomeAssistant::EntityConfig{HomeAssistant::EntityBaseConfig{
          .component = "sensor",
          .config_key = setting.name,
          .state_key = setting.name,
          .entity_category = "diagnostic",
          .device_class = "",
          .state_class = "measurement",
          .unit_of_measurement = fix_unit(setting.unit),
          .name = setting.name,
          .icon = "",
      }};
    }
    haClient.publishConfiguration(haConfig[i].configBinarySensor);
    haClient.publishConfiguration(haConfig[i].configSensor);
    haClient.publishConfiguration(haConfig[i].configText);
  };
}

void reconnectMQTTIfNeeded() {
  if (mqttClient.connected()) {
    return;
  }

  int tryCount = 1;
  while (!mqttClient.connected() && tryCount > 0) {
    ArduinoOTA.handle();
    logger.log(LOG_INFO, "Attempting MQTT connection...");
    if (mqttClient.connect("UPS/1.0", config::mqtt.user, config::mqtt.password)) {
      logger.log(LOG_INFO, "Connected to MQTT broker %s:%d", config::mqtt.serverHostname, config::mqtt.serverPort);
      mqttClient.subscribe(haClient.getCommandTopic(&haConfigResetButton).c_str());
      mqttClient.subscribe(haClient.getCommandTopic(&haConfigReconfigureButton).c_str());
      break;
    } else {
      logger.log(LOG_ERR, "Failed to connect to MQTT broker %s:%d", config::mqtt.serverHostname, config::mqtt.serverPort);
      delay(5 * ONE_SECOND_IN_MILLIS);  // wait before retrying
      tryCount--;
    }
  }
  logger.log(LOG_INFO, "MQTT connected status: %s", mqttClient.state() == MQTT_CONNECTED ? "connected" : "disconnected");

  if (mqttClient.connected()) {
    publishHAConfigurations();
  }
}

void setupCommunication() {
  setupWiFi();
  setupOTA();
  setupSyslog();
  setupMQTT();
}

void setup() {
  Serial.begin(115200);

  pinMode(config::pins.LED, OUTPUT);
  digitalWrite(config::pins.LED, LOW);  // turn off the LED
  ledBlinker.start();                   // start the timer

  setupCommunication();

  logger.log(LOG_INFO, "Connecting to I2C...");
  Wire.begin(config::pins.I2C_SDA, config::pins.I2C_SCL);
  logger.log(LOG_INFO, "I2C initialized on SDA=GPIO%d, SCL=GPIO%d", config::pins.I2C_SDA, config::pins.I2C_SCL);

  logger.log(LOG_INFO, "Looking for BQ25798 on I2C bus...");
  while (!bq25798.begin()) {
    ArduinoOTA.handle();
    ledBlinker.loop();
    delay(10);
  }
  bq25798.clearError();

  if (bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    // Reset and set up the IC if it's safe to do it
    onetimeSetupIfNeeded(false, true);  // force reset the IC and re-initialize it
  }

  timers.every(5 * ONE_SECOND_IN_MILLIS, [](void*) -> bool {
    trackChanges();
    sendCalculatedValues();
    return true;  // keep the timer active
  });
  timers.every(30 * ONE_SECOND_IN_MILLIS, [](void*) -> bool {
    checkChargerStatus();
    return true;  // keep the timer active
  });
  timers.every(60 * ONE_SECOND_IN_MILLIS, [](void*) -> bool {
    reconnectMQTTIfNeeded();
    return true;  // keep the timer active
  });

  logger.log(LOG_INFO, "Ready.");
}

int lastVBUS_STAT = -1;  // last VBUS_STAT value to detect changes
void adjustBlinkSpeed() {
  int newVBUS_STAT = static_cast<int>(bq25798.getVBUS_STAT());
  if (lastVBUS_STAT != newVBUS_STAT) {
    if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
      ledBlinker.setSpeed(ONE_SECOND_IN_MILLIS * 1 / 5);  // blink faster in backup mode
    } else if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_OTG_MODE) {
      ledBlinker.setSpeed(ONE_SECOND_IN_MILLIS * 1 / 20);  // blink even faster in OTG mode
    } else {
      ledBlinker.setSpeed(ONE_SECOND_IN_MILLIS);  // slow blink speed in normal mode
    }
    lastVBUS_STAT = newVBUS_STAT;
  }
}

Timer<>::Task backupRecoveryTask = nullptr;  // task to handle backup mode recovery
void checkForUPSModeChange() {
  // If in full auto mode, re-arm backup mode if needed
  if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    // check if the power source is OK for sufficient time
    if (bq25798.getAC1_PRESENT_STAT() == BQ25798::AC1_PRESENT_STAT_t::AC1_PRESENT_STAT_PRESENT) {
      // AC1 is present
      if (backupRecoveryTask == nullptr) {
        logger.log(LOG_INFO, "AC1 detected (power OK?) in backup mode, waiting for it to be present and stable...");
        backupRecoveryTask = timers.in(30 * ONE_SECOND_IN_MILLIS, [](void*) -> bool {
          logger.log(LOG_INFO, "AC1 is present and stable, exiting backup mode and re-arming...");
          rearmBackupMode();
          return false;  // stop the task after execution
        });
      }
    } else {
      // power source is not OK, cancel the backup recovery task
      if (backupRecoveryTask != nullptr) {
        logger.log(LOG_WARNING, "AC1 is not present, resetting backup recovery timer.");
        timers.cancel(backupRecoveryTask);  // cancel the task if AC1 is not present
      }
    }

    // Enable the BACKUP mode if it accidentally got disabled (e.g. by enabling
    // the charger)
    if (!bq25798.getEN_BACKUP() && bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_GOOD &&
        bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_OTG_MODE) {
      logger.log(LOG_CRIT, "BACKUP mode is disabled (why?) but shouldn't be. Re-enabling it...");
      bq25798.setEN_BACKUP(true);  // re-enable BACKUP mode
    }
  }
}

void loop() {
  // Read all registers to update the state
  bq25798.readAllRegisters();
  checkForError();

  // Process the timers and event handlers
  adjustBlinkSpeed();
  ledBlinker.loop();
  timers.tick();  // DO NOT call timers.tick() from anywhere else! It might cause side effects lika a recursion or overlaps in the code flow.
  ArduinoOTA.handle();
  mqttClient.loop();

  checkForUPSModeChange();  // check if the UPS mode has changed

  delay(20);  // not too long to not interfere with the fastest possible LED blinking
}
