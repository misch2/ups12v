# 1 "C:\\Users\\Michal\\AppData\\Local\\Temp\\tmp80zvyfpb"
#include <Arduino.h>
# 1 "C:/Users/Michal/Git/my/ups12v/software/ups/src/UPS.ino"
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



#define STRINGIFY(x) STR(x)
#define STR(x) #x
#define EXPAND(x) x
#define CONCAT3(a,b,c) STRINGIFY(EXPAND(a)EXPAND(b)EXPAND(c))
#include CONCAT3(boards/,BOARD_CONFIG,.h)


constexpr int LED_PIN = 2;

constexpr int minimum_single_cell_voltage = 2900;
constexpr int maximum_single_cell_voltage = 4200;



constexpr double ts_R_vregn = 5600.0;
constexpr double ts_R_gnd = 33000.0;
constexpr double temperature_sensor_resistance_25degC = 10000.0;
constexpr double temperature_sensor_beta = 3435.0;

Logger logger(nullptr, &Serial);
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

auto timers = timer_create_default();

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
const char* fix_unit(const char* unit);
void patWatchdog();
bool checkForError();
void trackChanges();
void sendCalculatedValues();
bool trackChangesWrapper(void*);
bool checkChargerStatus(void*);
void onetimeSetupIfNeeded();
void rearmBackupMode();
void MQTTcallback(char* topic, byte* payload, unsigned int length);
void setupWiFi();
void setupOTA();
void setupSyslog();
void setupMQTT();
void setupCommunication();
void setup();
void loop();
#line 112 "C:/Users/Michal/Git/my/ups12v/software/ups/src/UPS.ino"
const char* fix_unit(const char* unit) {

  if (unit == nullptr || strlen(unit) == 0) {
    return unit;
  }

  if (strcmp(unit, "degC") == 0) {
    return "°C";
  }

  return unit;
}

void patWatchdog() {


  bq25798.setWD_RST(true);
}

bool checkForError() {
  if (bq25798.lastError()) {
    logger.log(LOG_ERR, "Error: %d\n", bq25798.lastError());
    bq25798.clearError();
    return true;
  }
  return false;
}

bool firstRun = true;
void trackChanges() {
  long now = millis();

  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    BQ25798::Setting setting = bq25798.getSetting(i);
    newRawValues[i] = bq25798.getRaw(setting);
    if (checkForError()) {
      logger.log(LOG_ERR, "Error reading setting %d (%s)\n", i, setting.name);
      return;
    }
  }

  if (firstRun) {
    for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
      oldRawValues[i] = newRawValues[i];
    }
  }


  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    BQ25798::Setting setting = bq25798.getSetting(i);



    if (setting.is_flag && newRawValues[i] == 0) {
      continue;
    }

    if (setting.type == BQ25798::settings_type_t::FLOAT) {

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

      int int_val = bq25798.rawToInt(newRawValues[i], setting);
      haClient.publishStateIfNeeded(haConfig[i].configSensor, String(int_val), firstRun);
    }
  }


  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    oldRawValues[i] = newRawValues[i];
  }
  firstRun = false;
}

void sendCalculatedValues() {

  double ts_adc = bq25798.getTS_ADC() / 100.0;
  double ts_combo_resistance = ts_adc * ts_R_vregn / (1.0 - ts_adc);
  double ts_resistance = 1.0 / (1.0 / ts_combo_resistance - 1.0 / ts_R_gnd);
  double ts_temperature = 1.0 / (1.0 / 298.15 + log(ts_resistance / temperature_sensor_resistance_25degC) / temperature_sensor_beta) - 273.15;
  haClient.publishStateIfNeeded(&haConfigBatteryTemperature, String(ts_temperature, 1));

  double vbat_percent =
      100 * (bq25798.getVBAT_ADC() / BATTERY_CELL_COUNT - minimum_single_cell_voltage) / (maximum_single_cell_voltage - minimum_single_cell_voltage);
  vbat_percent = constrain(vbat_percent, 0.0, 100.0);
  haClient.publishStateIfNeeded(&haConfigBatteryPercent, String(vbat_percent), firstRun);

  double bat_current = bq25798.getIBAT_ADC() / 1000.0;
  double bat_power = bat_current * (bq25798.getVBAT_ADC() / 1000.0);
  haClient.publishStateIfNeeded(&haConfigPBAT, String(bat_power), firstRun);

  double bus_current = bq25798.getIBUS_ADC() / 1000.0;
  double bus_power = bus_current * (bq25798.getVBUS_ADC() / 1000.0);
  haClient.publishStateIfNeeded(&haConfigPBUS, String(bus_power), firstRun);

  haClient.publishStateIfNeeded(&haConfigUptime, String(millis() / 1000));
}

bool trackChangesWrapper(void*) {
  trackChanges();
  sendCalculatedValues();
  return true;
}

bool checkChargerStatus(void*) {

  if (bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_GOOD
      && bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    int cell_mV = bq25798.getVBAT_ADC() / BATTERY_CELL_COUNT;
    if (cell_mV > VBAT_CHG_DISABLE_ABOVE_CELL_mV) {
      if (bq25798.getEN_CHG() == true) {
        logger.log(LOG_INFO,
                   "Disabling charger, power is good and battery cell (%d) is "
                   "above limit (%d) ...",
                   cell_mV, VBAT_CHG_DISABLE_ABOVE_CELL_mV);
        bq25798.setEN_CHG(false);
      }
    } else if (cell_mV < VBAT_CHG_ENABLE_BELOW_CELL_mV) {
      if (bq25798.getEN_CHG() == false) {
        logger.log(LOG_INFO,
                   "Enabling charger, power is good and battery cell (%d) is "
                   "below limit (%d)...",
                   cell_mV, VBAT_CHG_ENABLE_BELOW_CELL_mV);
        bq25798.setEN_CHG(true);
      }
    }
  }

  return true;
}

void onetimeSetupIfNeeded() {
  if (bq25798.getVAC2_ADC_DIS()) {

    logger.log(LOG_INFO, "Full IC reset not needed, it seems to be already initialized.");
    return;
  }

  logger.log(LOG_INFO, "Resetting the IC completely...");
  bq25798.setREG_RST(true);
  while (bq25798.getREG_RST()) {
    ledBlinker.loop();
    delay(100);
    bq25798.readAllRegisters();
  }
  logger.log(LOG_INFO, "Reset successful.");



  bq25798.setWATCHDOG(BQ25798::WATCHDOG_t::WATCHDOG_DISABLE);


  bq25798.setADC_RATE(BQ25798::ADC_RATE_t::ADC_RATE_CONTINUOUS);
  bq25798.setADC_SAMPLE(BQ25798::ADC_SAMPLE_t::ADC_SAMPLE_15BIT);
  bq25798.setADC_EN(true);

  bq25798.setIBUS_ADC_DIS(false);
  bq25798.setIBAT_ADC_DIS(false);
  bq25798.setVAC2_ADC_DIS(true);


  bq25798.setEN_HIZ(false);


  bq25798.setAUTO_INDET_EN(false);

  bq25798.setVOTG(VOTG_mV);
  bq25798.setIOTG(IOTG_mA);
  bq25798.setVINDPM(VINDPM_mV);
  bq25798.setIINDPM(IINDPM_mA);
  bq25798.setICHG(ICHG_mA);

  bq25798.setVBUS_BACKUP(BQ25798::VBUS_BACKUP_t::PCT_VBUS_BACKUP_80);


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

  bq25798.readAllRegisters();

  logger.log(LOG_INFO, "Exiting backup mode and re-arming UPS...");







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
# 364 "C:/Users/Michal/Git/my/ups12v/software/ups/src/UPS.ino"
  if (bq25798.getAC1_PRESENT_STAT() != BQ25798::AC1_PRESENT_STAT_t::AC1_PRESENT_STAT_PRESENT) {
    logger.log(LOG_ERR, "Error: AC1 is not present, cannot re-arm.");
    return;
  }


  logger.log(LOG_INFO, "Disabling charger...");
  bq25798.setEN_CHG(false);






  logger.log(LOG_INFO, "Setting BKUP_ACFET1_ON to 1...");
  bq25798.setBKUP_ACFET1_ON(true);

  logger.log(LOG_INFO, "Waiting for a confirmation of ACFET1 enabled...");
  if (!waitForBQCondition([]() { return bq25798.getEN_ACDRV1() == true; })) {
    logger.log(LOG_ERR, "Error: failed to turn ACDRV1 on.");
    return;
  }







  logger.log(LOG_INFO, "Proceeding to exit OTG mode...");
  bq25798.setEN_OTG(false);


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

  wifiManager.setHostname(HOSTNAME);
  wifiManager.setConnectRetries(5);
  wifiManager.setConnectTimeout(15);
  wifiManager.setConfigPortalTimeout(3 * 60);
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

    syslog = new Syslog(udpClient, syslogServer, 514, SYSLOG_MYHOSTNAME, SYSLOG_MYAPPNAME, LOG_DAEMON);
    if (syslog != nullptr) {
      logger.setSyslog(syslog);
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
  mqttClient.setBufferSize(1024);
  mqttClient.setKeepAlive(60);
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
  digitalWrite(LED_PIN, LOW);
  ledBlinker.loop();

  setupCommunication();

  logger.log(LOG_INFO, "Connecting to I2C...");
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);

  logger.log(LOG_INFO, "I2C initialized on SDA=GPIO%d, SCL=GPIO%d", I2C_SDA_PIN, I2C_SCL_PIN);

  logger.log(LOG_INFO, "Looking for BQ25798 on I2C bus...");
  while (!bq25798.begin()) {
    ledBlinker.loop();
    delay(100);
  }
  bq25798.clearError();

  if (bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {

    onetimeSetupIfNeeded();
  }

  timers.every(5000, &trackChangesWrapper);
  timers.every(30000, &checkChargerStatus);

  logger.log(LOG_INFO, "Ready.");
}

long backupRecoveryStartMillis = 0;
void loop() {
  ledBlinker.loop();

  bq25798.readAllRegisters();
  checkForError();
  timers.tick();

  ArduinoOTA.handle();
  mqttClient.loop();

  if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    ledBlinker.setSpeed(200);
  } else if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_OTG_MODE) {
    ledBlinker.setSpeed(50);
  } else {
    ledBlinker.setSpeed(1000);
  }


  if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {

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
        backupRecoveryStartMillis = 0;
      }
    } else {

      if (backupRecoveryStartMillis != 0) {
        logger.log(LOG_WARNING, "AC1 is not present, resetting backup recovery timer.");
        backupRecoveryStartMillis = 0;
      }
    }



    if (!bq25798.getEN_BACKUP() && bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_GOOD &&
        bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_OTG_MODE) {
      logger.log(LOG_CRIT, "BACKUP mode is disabled (why?) but shouldn't be. Re-enabling it...");
      bq25798.setEN_BACKUP(true);
    }
  }

  delay(10);
}