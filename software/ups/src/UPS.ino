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

#include "homeassistant_mqtt.h"
#include "led_blinker.h"
#include "logger.h"
#include "version.h"

// dynamically include board-specific config
// clang-format off
#define STRINGIFY(x) STR(x)
#define STR(x) #x
#define EXPAND(x) x
#define CONCAT3(a, b, c) STRINGIFY(EXPAND(a)EXPAND(b)EXPAND(c))
#include CONCAT3(boards/,BOARD_CONFIG,.h)
// clang-format on

constexpr int minimum_single_cell_voltage = 2900;
constexpr int maximum_single_cell_voltage = 4200;

// Battery temperature reporting:
// Resistor divider network for the NTC sensor:
constexpr double ts_R_vregn = 5600.0;  // resistor connected to REGN
constexpr double ts_R_gnd = 33000.0;   // resistor connected to GND
constexpr double temperature_sensor_resistance_25degC = 10000.0;
constexpr double temperature_sensor_beta = 3435.0;

constexpr int LED_PIN = 2;  // GPIO pin for the LED

Logger logger(nullptr, &Serial);  // create a logger instance with Serial as the output stream
WiFiUDP udpClient;
WiFiManager wifiManager;
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
BQ25798 bq25798 = BQ25798();
HomeAssistant_MQTT haClient(mqttClient, logger);
Syslog* syslog = nullptr;
LEDBlinker ledBlinker(LED_PIN);

std::array<int, BQ25798::SETTINGS_COUNT> oldRawValues;
std::array<int, BQ25798::SETTINGS_COUNT> newRawValues;
std::array<HomeAssistant_MQTT::EntityMultiConfig, BQ25798::SETTINGS_COUNT> haConfig;

auto timers = timer_create_default();  // create a timer for tracking changes and other tasks with fixed periods

HomeAssistant_MQTT::EntityConfig haConfigUptime = {
    .component = "sensor",
    .device_topic = MQTT_HA_DEVICENAME,
    .config_key = "uptime",
    .state_key = "uptime",
    .entity_category = "diagnostic",
    .device_class = "duration",
    .state_class = "measurement",
    .unit_of_measurement = "s",
    .icon = "mdi:chart-box-outline",
};
HomeAssistant_MQTT::EntityConfig haConfigBatteryTemperature = {
    .component = "sensor",
    .device_topic = MQTT_HA_DEVICENAME,
    .config_key = "battery_temperature",
    .state_key = "battery_temperature",
    .entity_category = "diagnostic",
    .device_class = "temperature",
    .state_class = "measurement",
    .unit_of_measurement = "°C",
    .icon = "mdi:thermometer",
};
HomeAssistant_MQTT::EntityConfig haConfigBatteryPercent = {
    .component = "sensor",
    .device_topic = MQTT_HA_DEVICENAME,
    .config_key = "battery_percent",
    .state_key = "battery_percent",
    .entity_category = "diagnostic",
    .device_class = "battery",
    .state_class = "measurement",
    .unit_of_measurement = "%",
    .icon = "",
};
HomeAssistant_MQTT::EntityConfig haConfigPBAT = {
    .component = "sensor",
    .device_topic = MQTT_HA_DEVICENAME,
    .config_key = "PBAT",
    .state_key = "PBAT",
    .entity_category = "diagnostic",
    .device_class = "power",
    .state_class = "measurement",
    .unit_of_measurement = "W",
    .icon = "",
};
HomeAssistant_MQTT::EntityConfig haConfigPBUS = {
    .component = "sensor",
    .device_topic = MQTT_HA_DEVICENAME,
    .config_key = "PBUS",
    .state_key = "PBUS",
    .entity_category = "diagnostic",
    .device_class = "power",
    .state_class = "measurement",
    .unit_of_measurement = "W",
    .icon = "",
};

const char* fix_unit(const char* unit) {
  // fix the unit string for Home Assistant compatibility
  if (unit == nullptr || strlen(unit) == 0) {
    return unit;
  }

  if (strcmp(unit, "degC") == 0) {
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
    newRawValues[i] = bq25798.getRaw(setting);
    if (checkForError()) {
      logger.log(LOG_ERR, "Error reading setting %d (%s)\n", i, setting.name);
      return;  // stop tracking changes if there is an error
    }
  }

  if (firstRun) {
    for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
      oldRawValues[i] = newRawValues[i];
    }
  }

  // every next time check if the values changed
  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    BQ25798::Setting setting = bq25798.getSetting(i);

    // exception: do not notify about flags set to FALSE because any read
    // operation will reset them to FALSE
    if (setting.is_flag && newRawValues[i] == 0) {
      continue;
    }

    if (setting.type == BQ25798::settings_type_t::FLOAT) {
      // Float and int values are sent only on HA timeout, not on every tiny change
      float float_val = bq25798.rawToFloat(newRawValues[i], setting);
      haClient.publishStateIfNeeded(haConfig[i].configSensor, String(float_val), firstRun);

    } else if (setting.type == BQ25798::settings_type_t::BOOL) {
      if (!setting.is_flag) {
        bool bool_val = bq25798.rawToBool(newRawValues[i], setting);
        haClient.publishStateIfNeeded(haConfig[i].configBinarySensor, bool_val ? "ON" : "OFF", firstRun || oldRawValues[i] != newRawValues[i]);
      }

    } else if (setting.type == BQ25798::settings_type_t::ENUM) {
      haClient.publishStateIfNeeded(haConfig[i].configText, bq25798.rawToString(newRawValues[i], setting), firstRun || oldRawValues[i] != newRawValues[i]);
      haClient.publishStateIfNeeded(haConfig[i].configSensor, String(bq25798.rawToInt(newRawValues[i], setting)),
                                    firstRun || oldRawValues[i] != newRawValues[i]);

    } else if (setting.type == BQ25798::settings_type_t::INT) {
      // Float and int values are sent only on HA timeout, not on every tiny change
      int int_val = bq25798.rawToInt(newRawValues[i], setting);
      haClient.publishStateIfNeeded(haConfig[i].configSensor, String(int_val), firstRun);
    }
  }

  // update the old values
  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    oldRawValues[i] = newRawValues[i];
  }
  firstRun = false;
}

void sendCalculatedValues() {
  // Send calculated values
  double ts_adc = bq25798.getTS_ADC() / 100.0;  // convert from percent to 0.0-1.0 range
  double ts_combo_resistance = ts_adc * ts_R_vregn / (1.0 - ts_adc);
  double ts_resistance = 1.0 / (1.0 / ts_combo_resistance - 1.0 / ts_R_gnd);
  double ts_temperature = 1.0 / (1.0 / 298.15 + log(ts_resistance / temperature_sensor_resistance_25degC) / temperature_sensor_beta) - 273.15;
  haClient.publishStateIfNeeded(&haConfigBatteryTemperature, String(ts_temperature, 1));

  double vbat_percent =
      100 * (bq25798.getVBAT_ADC() / BATTERY_CELL_COUNT - minimum_single_cell_voltage) / (maximum_single_cell_voltage - minimum_single_cell_voltage);
  vbat_percent = constrain(vbat_percent, 0.0, 100.0);  // constrain to 0-100%
  haClient.publishStateIfNeeded(&haConfigBatteryPercent, String(vbat_percent), firstRun);

  double bat_current = bq25798.getIBAT_ADC() / 1000.0;                // convert from mA to A
  double bat_power = bat_current * (bq25798.getVBAT_ADC() / 1000.0);  // convert from mV to V
  haClient.publishStateIfNeeded(&haConfigPBAT, String(bat_power), firstRun);

  double bus_current = bq25798.getIBUS_ADC() / 1000.0;                // convert from mA to A
  double bus_power = bus_current * (bq25798.getVBUS_ADC() / 1000.0);  // convert from mV to V
  haClient.publishStateIfNeeded(&haConfigPBUS, String(bus_power), firstRun);

  haClient.publishStateIfNeeded(&haConfigUptime, String(millis() / 1000));  // publish uptime in seconds
}

bool trackChangesWrapper(void*) {
  trackChanges();
  sendCalculatedValues();
  return true;  // keep the timer active
}

bool checkChargerStatus(void*) {
  // Enable the charger if everything is normal
  if (bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_GOOD  //
      && bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    int cell_mV = bq25798.getVBAT_ADC() / BATTERY_CELL_COUNT;
    if (cell_mV > VBAT_CHG_DISABLE_ABOVE_CELL_mV) {
      if (bq25798.getEN_CHG() == true) {
        logger.log(LOG_INFO,
                   "Disabling charger, power is good and battery cell (%d) is "
                   "above limit (%d) ...",
                   cell_mV, VBAT_CHG_DISABLE_ABOVE_CELL_mV);
        bq25798.setEN_CHG(false);  // disable the charger
      }
    } else if (cell_mV < VBAT_CHG_ENABLE_BELOW_CELL_mV) {
      if (bq25798.getEN_CHG() == false) {
        logger.log(LOG_INFO,
                   "Enabling charger, power is good and battery cell (%d) is "
                   "below limit (%d)...",
                   cell_mV, VBAT_CHG_ENABLE_BELOW_CELL_mV);
        bq25798.setEN_CHG(true);  // enable the charger
      }
    }
  }

  return true;  // keep the timer active
}

void onetimeSetupIfNeeded() {
  if (bq25798.getVAC2_ADC_DIS()) {
    // VAC2_ADC_DIS is false by default, so if it is true, it means the IC has already been initialized by us
    logger.log(LOG_INFO, "Full IC reset not needed, it seems to be already initialized.");
    return;
  }

  logger.log(LOG_INFO, "Resetting the IC completely...");
  bq25798.setREG_RST(true);  // reset the IC
  while (bq25798.getREG_RST()) {
    ledBlinker.loop();
    delay(100);
    bq25798.readAllRegisters();
  }
  logger.log(LOG_INFO, "Reset successful.");

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

  bq25798.setVOTG(VOTG_mV);
  bq25798.setIOTG(IOTG_mA);
  bq25798.setVINDPM(VINDPM_mV);
  bq25798.setIINDPM(IINDPM_mA);
  bq25798.setICHG(ICHG_mA);

  bq25798.setVBUS_BACKUP(BQ25798::VBUS_BACKUP_t::PCT_VBUS_BACKUP_80);  // VBUS backup percentage (80 % of 12 V = 9.6 V, etc.);

  // Enable BACKUP mode:
  bq25798.setEN_BACKUP(true);

  logger.log(LOG_INFO, "One-time setup complete.");
}

bool waitForBQCondition(bool (*condition)(), int timeoutMillis = 5000) {
  long startTime = millis();
  bq25798.readAllRegisters();
  while (!condition()) {
    ledBlinker.loop();
    timers.tick();
    if (millis() - startTime > timeoutMillis) {
      return false;
    }
    delay(100);
    bq25798.readAllRegisters();
  }
  timers.tick();
  return true;
}

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
    logger.log(LOG_ERR, "Error: VBUS_STAT is not BACKUP_MODE");
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
}

void setupWiFi() {
  logger.log(LOG_INFO, "Starting WiFi manager...");
  // Connect to WiFi
  wifiManager.setHostname(HOSTNAME);
  wifiManager.setConnectRetries(5);
  wifiManager.setConnectTimeout(15);           // 15 seconds
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
  logger.log(LOG_INFO, "OTA service started successfully.");
}

void setupSyslog() {
  logger.log(LOG_INFO, "Resolving syslog server hostname: %s", SYSLOG_SERVER_HOSTNAME);
  IPAddress syslogServer;
  if (WiFi.hostByName(SYSLOG_SERVER_HOSTNAME, syslogServer)) {
    logger.log(LOG_INFO, "Syslog server IP: %s", syslogServer.toString().c_str());
    // Create a new syslog instance with LOG_KERN facility
    syslog = new Syslog(udpClient, syslogServer, 514, SYSLOG_MYHOSTNAME, SYSLOG_MYAPPNAME, LOG_DAEMON);
    if (syslog != nullptr) {
      logger.setSyslog(syslog);  // set the syslog instance in the logger
      logger.log(LOG_INFO, "Syslog instance created successfully, firmware version: %s", FIRMWARE_VERSION);
    } else {
      logger.log(LOG_ERR, "Failed to create syslog instance.");
    }
  } else {
    logger.log(LOG_ERR, "Failed to resolve syslog server hostname: %s", SYSLOG_SERVER_HOSTNAME);
  };
}

void setupMQTT() {
  logger.log(LOG_INFO, "Starting MQTT client...");
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setBufferSize(1024);  // set the MQTT buffer size to 1 KB
  mqttClient.setKeepAlive(60);     // set the keep-alive interval to 60 seconds
  mqttClient.setCallback(MQTTcallback);
  if (mqttClient.connect("UPS/1.0", MQTT_USER, MQTT_PASSWORD)) {
    logger.log(LOG_INFO, "Connected to MQTT broker %s:%d", MQTT_SERVER, MQTT_PORT);
  } else {
    logger.log(LOG_ERR, "Failed to connect to MQTT broker %s:%d, ignoring it", MQTT_SERVER, MQTT_PORT);
  }
  logger.log(LOG_INFO, "MQTT connected status: %s", mqttClient.state() == MQTT_CONNECTED ? "connected" : "disconnected");

  haClient.publishConfiguration(&haConfigUptime);
  haClient.publishConfiguration(&haConfigBatteryTemperature);
  haClient.publishConfiguration(&haConfigBatteryPercent);
  haClient.publishConfiguration(&haConfigPBAT);
  haClient.publishConfiguration(&haConfigPBUS);

  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    BQ25798::Setting setting = bq25798.getSetting(i);
    if (setting.type == BQ25798::settings_type_t::BOOL) {
      if (!setting.is_flag) {
        haConfig[i].configBinarySensor = new HomeAssistant_MQTT::EntityConfig{
            .component = "binary_sensor",
            .device_topic = MQTT_HA_DEVICENAME,
            .config_key = setting.name,
            .state_key = setting.name,
            .entity_category = "diagnostic",
            .device_class = "",
            .state_class = "measurement",
            .unit_of_measurement = fix_unit(setting.unit),
            .icon = "",
        };
      }
    } else if (setting.type == BQ25798::settings_type_t::ENUM) {
      haConfig[i].configSensor = new HomeAssistant_MQTT::EntityConfig{
          .component = "sensor",
          .device_topic = MQTT_HA_DEVICENAME,
          .config_key = setting.name,
          .state_key = String(setting.name) + "_numeric",
          .entity_category = "diagnostic",
          .device_class = "",
          .state_class = "measurement",
          .unit_of_measurement = fix_unit(setting.unit),
          .icon = "",
      };
      haConfig[i].configText = new HomeAssistant_MQTT::EntityConfig{
          .component = "text",
          .device_topic = MQTT_HA_DEVICENAME,
          .config_key = setting.name,
          .state_key = String(setting.name) + "_string",
          .entity_category = "diagnostic",
          .device_class = "",
          .state_class = "measurement",
          .unit_of_measurement = fix_unit(setting.unit),
          .icon = "",
      };
    } else {
      haConfig[i].configSensor = new HomeAssistant_MQTT::EntityConfig{
          .component = "sensor",
          .device_topic = MQTT_HA_DEVICENAME,
          .config_key = setting.name,
          .state_key = setting.name,
          .entity_category = "diagnostic",
          .device_class = "",
          .state_class = "measurement",
          .unit_of_measurement = fix_unit(setting.unit),
          .icon = "",
      };
    }
  };
}

void setupCommunication() {
  setupWiFi();
  setupOTA();
  setupSyslog();
  setupMQTT();
}

void setup() {
  Serial.begin(115200);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);  // turn off the LED
  ledBlinker.start();          // start the timer

  setupCommunication();

  logger.log(LOG_INFO, "Connecting to I2C...");
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  // Wire.setClock(1000);  // set I2C clock to 1 kHz // FIXME test only
  logger.log(LOG_INFO, "I2C initialized on SDA=GPIO%d, SCL=GPIO%d", I2C_SDA_PIN, I2C_SCL_PIN);

  logger.log(LOG_INFO, "Looking for BQ25798 on I2C bus...");
  while (!bq25798.begin()) {
    ledBlinker.loop();
    delay(100);
  }
  bq25798.clearError();

  if (bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    // Reset and set up the IC if it's safe to do it
    onetimeSetupIfNeeded();
  }

  timers.every(5000, &trackChangesWrapper);  // start the tracker timer and check for changes every 5 seconds
  timers.every(30000, &checkChargerStatus);  // check the charger status every 30 seconds

  logger.log(LOG_INFO, "Ready.");
}

long backupRecoveryStartMillis = 0;
int lastVBUS_STAT = -1;  // last VBUS_STAT value to detect changes
void loop() {
  ledBlinker.loop();

  bq25798.readAllRegisters();
  checkForError();
  timers.tick();

  ArduinoOTA.handle();
  mqttClient.loop();

  int newVBUS_STAT = static_cast<int>(bq25798.getVBUS_STAT());
  if (lastVBUS_STAT != newVBUS_STAT) {
    logger.log(LOG_INFO, "VBUS_STAT changed from %d to %d (%s)", lastVBUS_STAT, newVBUS_STAT, bq25798.getVBUS_STAT_enum_string());
    if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
      ledBlinker.setSpeed(200);  // blink faster in backup mode
    } else if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_OTG_MODE) {
      ledBlinker.setSpeed(50);  // blink even faster in OTG mode
    } else {
      ledBlinker.setSpeed(1000);  // slow blink speed in normal mode
    }
    lastVBUS_STAT = newVBUS_STAT;
  }

  // If in full auto mode, re-arm backup mode if needed
  if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    // check if the power source is OK for sufficient time
    if (bq25798.getAC1_PRESENT_STAT() == BQ25798::AC1_PRESENT_STAT_t::AC1_PRESENT_STAT_PRESENT) {
      if (backupRecoveryStartMillis == 0) {
        backupRecoveryStartMillis = millis();
        logger.log(LOG_INFO,
                   "AC1 detected (power OK?) in backup mode, waiting for "
                   "it to be present for at least 30 seconds...");
      } else if (millis() - backupRecoveryStartMillis >= 30000) {
        logger.log(LOG_INFO,
                   "AC1 is present for 30 seconds, exiting backup mode and "
                   "re-arming...");
        rearmBackupMode();
        backupRecoveryStartMillis = 0;  // reset the timer
      }
    } else {
      // AC1 is not present, reset the timer
      if (backupRecoveryStartMillis != 0) {
        logger.log(LOG_WARNING, "AC1 is not present, resetting backup recovery timer.");
        backupRecoveryStartMillis = 0;
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

  delay(10);  // not too long to not interfere with the LED blinking
}
