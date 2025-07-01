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

#include "version.h"

// dynamically include board-specific config
// clang-format off
#define STRINGIFY(x) STR(x)
#define STR(x) #x
#define EXPAND(x) x
#define CONCAT3(a, b, c) STRINGIFY(EXPAND(a)EXPAND(b)EXPAND(c))
#include CONCAT3(boards/,BOARD_CONFIG,.h)
// clang-format on

#ifdef SYSLOG_SERVER_HOSTNAME
// A UDP instance to let us send and receive packets over UDP
WiFiUDP udpClient;
Syslog* syslog = nullptr;
  #define SYSLOG_PRINT(pri, fmt, ...)                         \
    Serial.printf(fmt, ##__VA_ARGS__);                        \
    Serial.print('\n');                                       \
    Serial.flush();                                           \
    if (syslog != nullptr && WiFi.status() == WL_CONNECTED) { \
      syslog->logf(pri, fmt, ##__VA_ARGS__);                  \
    } else {                                                  \
      Serial.println(" (no syslog or WiFi not connected)");   \
    }
#else
  #define SYSLOG_PRINT(pri, fmt, ...)  \
    Serial.printf(fmt, ##__VA_ARGS__); \
    Serial.print('\n')
#endif

constexpr int minimum_single_cell_voltage = 2900;
constexpr int maximum_single_cell_voltage = 4200;

// Battery temperature reporting:
// Resistor divider network for the NTC sensor:
constexpr double ts_R_vregn = 5600.0;  // resistor connected to REGN
constexpr double ts_R_gnd = 33000.0;   // resistor connected to GND
constexpr double temperature_sensor_resistance_25degC = 10000.0;
constexpr double temperature_sensor_beta = 3435.0;

constexpr int LED_PIN = 2;  // GPIO pin for the LED

WiFiManager wifiManager;

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

BQ25798 bq25798 = BQ25798();

std::array<int, BQ25798::SETTINGS_COUNT> oldRawValues;
std::array<int, BQ25798::SETTINGS_COUNT> newRawValues;
std::array<long, BQ25798::SETTINGS_COUNT> lastSentMillis;

auto ledTimer = timer_create_default();  // create a timer with default settings
unsigned long ledBlinkSpeed = 100;       // LED toggle speed in milliseconds
bool toggle_led(void*) {
  digitalWrite(LED_PIN, !digitalRead(LED_PIN));  // toggle the LED
  ledTimer.in(ledBlinkSpeed / 2, &toggle_led);   // rearm the timer
  return false;                                  // keep existing timer active?
}

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

void publish_homeassistant_value(bool startup,                // true if the device is starting up, false if the value is
                                                              // changing
                                 String component,            // component type e.g. "sensor", "text", "switch", etc.
                                 String device_topic,         // device topic name, e.g. "energy_monitor" or "monitor1"
                                 String config_key,           // sensor name, e.g. "backlight_status"
                                 String state_key,            // sensor state topic name, e.g. "backlight_status" or "backlight_status_number"
                                 String value,                // initial value
                                 String entity_category,      // "diagnostic", "config", etc.
                                 String device_class,         // see
                                                              // https://www.home-assistant.io/integrations/sensor/#device-class
                                 String state_class,          // usually "measurement"
                                 String unit_of_measurement,  // e.g. "W", "V", "A", "kWh", etc.
                                 String icon                  // "mdi:battery" etc.
) {
  // use "sensor" if component is empty
  if (component == "") {
    component = "sensor";
  }

  String config_topic = "homeassistant/" + component + "/" + device_topic + "/" + config_key + "/config";
  String state_topic = "bq25798ups/" + device_topic + "/state/" + state_key;

  if (startup) {
    // create HomeAssistant config JSON
    JsonDocument doc;
    doc["state_topic"] = state_topic;
    doc["device"]["manufacturer"] = "Michal";
    doc["device"]["model"] = "UPS";
    doc["device"]["hw_version"] = "1.0";
    doc["device"]["sw_version"] = FIRMWARE_VERSION;

    JsonArray identifiers = doc["device"]["identifiers"].to<JsonArray>();
    identifiers.add(device_topic);
    doc["device"]["name"] = device_topic;
    doc["enabled_by_default"] = true;
    doc["entity_category"] = entity_category;
    if (device_class != "") {
      doc["device_class"] = device_class;
    }
    doc["state_class"] = state_class;
    doc["unit_of_measurement"] = unit_of_measurement;
    if (icon != "") {
      doc["icon"] = icon;
    }
    doc["force_update"] = true;   // force update the entity state on every publish
    doc["expire_after"] = "300";  // expire after 5 minutes
    doc["name"] = config_key;
    doc["unique_id"] = device_topic + "_" + config_key;

    if (component == "binary_sensor") {
      doc["payload_on"] = "ON";
      doc["payload_off"] = "OFF";
    } else if (component == "text") {
      doc["command_topic"] = state_topic;  // use the same topic for command and state
    }

    String serialized;
    serializeJson(doc, serialized);
    if (!mqttClient.publish(config_topic.c_str(), serialized.c_str(),
                            true))  // publish as retained, to survive HA restart
    {
      SYSLOG_PRINT(LOG_ERR, "Failed to publish initial HomeAssistant config for %s", config_topic.c_str());
    }
  }
  mqttClient.publish(state_topic.c_str(), value.c_str(), false);
}

long last_uptime = -1;
void publish_homeassistant_value_uptime_if_needed(bool startup) {
  long uptime = millis() / 1000;
  if ((uptime - last_uptime >= 60) || (uptime < last_uptime) || startup) {  // publish every minute or if the value overflowed
    publish_homeassistant_value(startup, "sensor", MQTT_HA_DEVICENAME, "uptime", "uptime", String(uptime), "diagnostic", "duration", "measurement", "s",
                                "mdi:chart-box-outline");
    last_uptime = uptime;
  }
}

void patWatchdog() {
  // To keep the device in host mode, the host has  to reset the watchdog timer
  // by writing 1 to WD_RST bit before the watchdog timer expires
  bq25798.setWD_RST(true);  // reset the watchdog timer
}

bool checkForError() {
  if (bq25798.lastError()) {
    SYSLOG_PRINT(LOG_ERR, "Error: %d\n", bq25798.lastError());
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
      SYSLOG_PRINT(LOG_ERR, "Error reading setting %d (%s)\n", i, setting.name);
      return;  // stop tracking changes if there is an error
    }
  }

  if (firstRun) {
    SYSLOG_PRINT(LOG_INFO, "First time reading BQ25798 settings...");
    for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
      oldRawValues[i] = newRawValues[i];
      lastSentMillis[i] = 0;  // reset the last sent time for each setting
    }
    firstRun = false;
  }

  // every next time check if the values changed
  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    bool homeAssistantTimerExpired =
        ((now - lastSentMillis[i]) >= 60 * 1000L) || ((now - lastSentMillis[i]) < 0);  // send every 60 seconds even if the value did not change

    if (oldRawValues[i] != newRawValues[i] || homeAssistantTimerExpired) {
      BQ25798::Setting setting = bq25798.getSetting(i);

      // exception: do not notify about flags set to FALSE because any read
      // operation will reset them to FALSE
      if (setting.is_flag && newRawValues[i] == 0) {
        continue;
      }

      if (setting.type == BQ25798::settings_type_t::FLOAT) {
        // Float and int values are sent only on HA timeout, not on every tiny change
        if (homeAssistantTimerExpired) {
          float float_val = bq25798.rawToFloat(newRawValues[i], setting);
          publish_homeassistant_value(false, "sensor", MQTT_HA_DEVICENAME, setting.name, setting.name, String(float_val), "diagnostic", "", "measurement",
                                      fix_unit(setting.unit), "");
          lastSentMillis[i] = now;

          if (setting.name == "TS_ADC") {
            // Temperature sensor value changed, so let's calculate the temperature in Celsius
            // and publish it as a separate sensor

            double ts_adc = float_val / 100.0;  // convert from percent to 0.0-1.0 range
            // SYSLOG_PRINT(LOG_INFO, "TS_ADC changed: %.2f %%", ts_adc * 100.0);

            double ts_combo_resistance = ts_adc * ts_R_vregn / (1.0 - ts_adc);
            // SYSLOG_PRINT(LOG_INFO, "TS combo resistance: %.2f Ohm", ts_combo_resistance);

            double ts_resistance = 1.0 / (1.0 / ts_combo_resistance - 1.0 / ts_R_gnd);
            // SYSLOG_PRINT(LOG_INFO, "TS resistance: %.2f Ohm", ts_resistance);

            double ts_temperature = 1.0 / (1.0 / 298.15 + log(ts_resistance / temperature_sensor_resistance_25degC) / temperature_sensor_beta) - 273.15;
            // SYSLOG_PRINT(LOG_INFO, "TS temperature: %.2f °C", ts_temperature);

            publish_homeassistant_value(false, "sensor", MQTT_HA_DEVICENAME, "battery_temperature", "battery_temperature", String(ts_temperature, 1),
                                        "diagnostic", "temperature", "measurement", "°C", "mdi:thermometer");
          }
        }
      } else if (setting.type == BQ25798::settings_type_t::BOOL) {
        if (!setting.is_flag) {
          bool bool_val = bq25798.rawToBool(newRawValues[i], setting);
          publish_homeassistant_value(false, "binary_sensor", MQTT_HA_DEVICENAME, setting.name, setting.name, bool_val ? "ON" : "OFF", "diagnostic", "",
                                      "measurement", fix_unit(setting.unit), "");
          // numeric too, for Grafana (influx database only handles numeric values)
          publish_homeassistant_value(false, "sensor", MQTT_HA_DEVICENAME, setting.name, String(setting.name) + "_numeric", bool_val ? "1" : "0", "diagnostic",
                                      "", "measurement", fix_unit(setting.unit), "");
          lastSentMillis[i] = now;
        }
      } else if (setting.type == BQ25798::settings_type_t::ENUM) {
        publish_homeassistant_value(false, "sensor", MQTT_HA_DEVICENAME, setting.name, String(setting.name) + "_numeric", String(newRawValues[i]), "diagnostic",
                                    "", "measurement", fix_unit(setting.unit), "");
        publish_homeassistant_value(false, "text", MQTT_HA_DEVICENAME, setting.name, String(setting.name) + "_string",
                                    String(bq25798.rawToString(newRawValues[i], setting)), "diagnostic", "", "measurement", fix_unit(setting.unit), "");
        lastSentMillis[i] = now;
      } else if (setting.type == BQ25798::settings_type_t::INT) {
        // Float and int values are sent only on HA timeout, not on every tiny change
        if (homeAssistantTimerExpired) {
          int int_val = bq25798.rawToInt(newRawValues[i], setting);
          publish_homeassistant_value(false, "sensor", MQTT_HA_DEVICENAME, setting.name, setting.name, String(int_val), "diagnostic", "", "measurement",
                                      fix_unit(setting.unit), "");
          lastSentMillis[i] = now;

          if (setting.name == "VBAT_ADC") {
            double vbat_percent =
                100 * ((int_val / 1000.0) / BATTERY_CELL_COUNT - minimum_single_cell_voltage) / (maximum_single_cell_voltage - minimum_single_cell_voltage);
            publish_homeassistant_value(false, "sensor", MQTT_HA_DEVICENAME, "battery_percent", "battery_percent", String(vbat_percent), "diagnostic",
                                        "battery", "measurement", "%", "");
          } else if (setting.name == "IBAT_ADC") {
            double current = int_val / 1000.0;                          // convert from mA to A
            double power = current * (bq25798.getVBAT_ADC() / 1000.0);  // convert from mV to V
            publish_homeassistant_value(false, "sensor", MQTT_HA_DEVICENAME, "PBAT", "PBAT", String(power), "diagnostic", "power", "measurement", "W", "");
          } else if (setting.name == "IBUS_ADC") {
            double current = int_val / 1000.0;                          // convert from mA to A
            double power = current * (bq25798.getVBUS_ADC() / 1000.0);  // convert from mV to V
            publish_homeassistant_value(false, "sensor", MQTT_HA_DEVICENAME, "PBUS", "PBUS", String(power), "diagnostic", "power", "measurement", "W", "");
          }
        }
      }
      // SYSLOG_PRINT(LOG_INFO, "%s%s", message_new, message_old);
    }
  }

  // update the old values
  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    oldRawValues[i] = newRawValues[i];
  }
}

void toggleCharger() {
  // Toggle the charger state
  if (bq25798.getEN_CHG()) {
    SYSLOG_PRINT(LOG_INFO, "Disabling charger...");
    bq25798.setEN_CHG(false);
  } else {
    SYSLOG_PRINT(LOG_INFO, "Enabling charger...");
    bq25798.setEN_CHG(true);
  }
}

void onetimeSetup() {
  SYSLOG_PRINT(LOG_INFO, "Resetting the IC completely...");
  bq25798.setREG_RST(true);  // reset the IC
  while (bq25798.getREG_RST()) {
    ledTimer.tick();
    delay(10);
    bq25798.readAllRegisters();
  }
  SYSLOG_PRINT(LOG_INFO, "Reset successful.");

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

  bq25798.setVBUS_BACKUP(VBUS_BACKUP_SWICHOVER);

  // Enable BACKUP mode:
  bq25798.setEN_BACKUP(true);

  SYSLOG_PRINT(LOG_INFO, "One-time setup complete.");
}

bool waitForBQCondition(bool (*condition)(), int timeoutMillis = 5000) {
  long startTime = millis();
  bq25798.readAllRegisters();
  trackChanges();
  while (!condition()) {
    ledTimer.tick();
    if (millis() - startTime > timeoutMillis) {
      return false;
    }
    delay(10);
    bq25798.readAllRegisters();
    trackChanges();
  }
  return true;
}

void rearmBackupMode() {
  // Re-arm the backup mode by setting EN_BACKUP to false and then true again
  bq25798.readAllRegisters();
  trackChanges();

  SYSLOG_PRINT(LOG_INFO, "Exiting backup mode and re-arming UPS...");

  // When a backup mode is entered automatically, the following happens:
  // DIS_ACDRV is set to TRUE, EN_OTG is set to TRUE, EN_ACDRV1 is set to FALSE,
  // PG is set to FALSE and VBUS_STAT is set to "Backup"
  //
  // So let's check if we are still in backup mode:

  if (bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    SYSLOG_PRINT(LOG_ERR, "Error: VBUS_STAT is not BACKUP_MODE");
    return;
  }
  if (!bq25798.getDIS_ACDRV()) {
    SYSLOG_PRINT(LOG_ERR, "In backup mode Error: ACDRV is not globally disabled, cannot re-arm.");
    return;
  }
  if (!bq25798.getEN_OTG()) {
    SYSLOG_PRINT(LOG_ERR, "In backup mode Error: OTG is not active, cannot re-arm.");
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
    SYSLOG_PRINT(LOG_ERR, "Error: AC1 is not present, cannot re-arm.");
    return;
  }

  // Disable charger to prevent any charging while we are in the OTG mode
  SYSLOG_PRINT(LOG_INFO, "Disabling charger...");
  bq25798.setEN_CHG(false);  // disable the charger
  trackChanges();

  // BKUP_ACFET1_ON does the following:
  // - set DIS_ACDRV to 0 && set EN_ACDRV1 to 1 (enable ACDRV1)
  // - set EN_BACKUP to 0 (disable backup mode) -- why does it do this???
  // - set BKUP_ACFET1_ON to 1
  // it also sets the VBUS_STAT to OTG
  SYSLOG_PRINT(LOG_INFO, "Setting BKUP_ACFET1_ON to 1...");
  bq25798.setBKUP_ACFET1_ON(true);  // turn on the ACFET1-RBFET1 to connect the adapter to VBUS
  trackChanges();

  SYSLOG_PRINT(LOG_INFO, "Waiting for a confirmation of ACFET1 enabled...");
  if (!waitForBQCondition([]() { return bq25798.getEN_ACDRV1() == true; })) {
    SYSLOG_PRINT(LOG_ERR, "Error: failed to turn ACDRV1 on.");
    return;
  }

  // EN_OTG should do the following when BKUP_ACFET1_ON is active:
  // - set EN_OTG to 0 (exit OTG mode)
  // - set EN_BACKUP to 1 (re-arm backup mode -- that's because BKUP_ACFET1_ON
  // is still set to 1)
  // - set BKUP_ACFET1_ON to 0
  // it also sets VBUS_STAT to normal input mode
  SYSLOG_PRINT(LOG_INFO, "Proceeding to exit OTG mode...");
  bq25798.setEN_OTG(false);  // exit OTG mode and enter the forward charging
                             // mode without PMID voltage crash
  trackChanges();

  SYSLOG_PRINT(LOG_INFO, "Waiting for a confirmation of OTG disabled and backup re-enabled...");
  if (!waitForBQCondition([]() { return bq25798.getEN_OTG() == false && bq25798.getEN_BACKUP() == true; })) {
    SYSLOG_PRINT(LOG_ERR, "Error: failed to exit OTG mode and re-arm.");
    return;
  }

  SYSLOG_PRINT(LOG_INFO, "Waiting for PG_STAT to be GOOD...");
  if (!waitForBQCondition([]() { return bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_GOOD; })) {
    SYSLOG_PRINT(LOG_ERR, "Error: failed to re-arm backup mode, PG_STAT is not GOOD.");
    return;
  }

  SYSLOG_PRINT(LOG_INFO, "Backup mode re-armed.");
}

void MQTTcallback(char* topic, byte* payload, unsigned int length) {
  String topicString = String(topic);

  String payloadString = "";
  for (int i = 0; i < length; i++) {
    payloadString += (char)payload[i];
  }

  SYSLOG_PRINT(LOG_INFO, "Message arrived on topic %s, payload %s", topicString.c_str(), payloadString.c_str());
}

void setup() {
  Serial.begin(115200);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);                   // turn off the LED
  ledTimer.in(ledBlinkSpeed / 2, &toggle_led);  // start the timer

  // Connect to WiFi
  wifiManager.setHostname(HOSTNAME);
  wifiManager.setConnectRetries(5);
  wifiManager.setConnectTimeout(15);           // 15 seconds
  wifiManager.setConfigPortalTimeout(3 * 60);  // Stay 3 minutes max in the AP web portal, then reboot
  bool res = wifiManager.autoConnect();
  if (!res) {
    SYSLOG_PRINT(LOG_ERR, "Failed to connect to wifi, rebooting...");
    ESP.restart();
  }
  if (WiFi.localIP() == IPAddress(0, 0, 0, 0)) {
    SYSLOG_PRINT(LOG_ERR, "Failed to get local IP address.");
    Serial.println("Failed to get IP address, rebooting...");
    ESP.restart();
  }

  SYSLOG_PRINT(LOG_INFO, "Connected to WiFi: %s (%s)\n", WiFi.SSID().c_str(), WiFi.localIP().toString().c_str());

  SYSLOG_PRINT(LOG_INFO, "Starting OTA service...");
  ArduinoOTA.setHostname(HOSTNAME);
  ArduinoOTA.begin();
  ArduinoOTA.onStart([]() { SYSLOG_PRINT(LOG_INFO, "OTA Start"); });
  ArduinoOTA.onEnd([]() { SYSLOG_PRINT(LOG_INFO, "OTA End"); });

  SYSLOG_PRINT(LOG_INFO, "Resolving syslog server hostname: %s", SYSLOG_SERVER_HOSTNAME);
  IPAddress syslogServer;
  if (WiFi.hostByName(SYSLOG_SERVER_HOSTNAME, syslogServer)) {
    SYSLOG_PRINT(LOG_INFO, "Syslog server IP: %s", syslogServer.toString().c_str());
    // Create a new syslog instance with LOG_KERN facility
    syslog = new Syslog(udpClient, syslogServer, 514, SYSLOG_MYHOSTNAME, SYSLOG_MYAPPNAME, LOG_DAEMON);
    if (syslog != nullptr) {
      SYSLOG_PRINT(LOG_INFO, "Syslog instance created successfully, firmware version: %s", FIRMWARE_VERSION);
    } else {
      SYSLOG_PRINT(LOG_ERR, "Failed to create syslog instance.");
    }
  } else {
    SYSLOG_PRINT(LOG_ERR, "Failed to resolve syslog server hostname: %s", SYSLOG_SERVER_HOSTNAME);
  };

  SYSLOG_PRINT(LOG_INFO, "Starting MQTT client...");
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setBufferSize(1024);  // set the MQTT buffer size to 1 KB
  mqttClient.setKeepAlive(60);     // set the keep-alive interval to 60 seconds
  mqttClient.setCallback(MQTTcallback);
  if (mqttClient.connect("UPS/1.0", MQTT_USER, MQTT_PASSWORD)) {
    SYSLOG_PRINT(LOG_INFO, "Connected to MQTT broker %s:%d", MQTT_SERVER, MQTT_PORT);
  } else {
    SYSLOG_PRINT(LOG_ERR, "Failed to connect to MQTT broker %s:%d, ignoring it", MQTT_SERVER, MQTT_PORT);
  }
  SYSLOG_PRINT(LOG_INFO, "MQTT connected status: %s", mqttClient.state() == MQTT_CONNECTED ? "connected" : "disconnected");
  // mqttClient.publish("foo", "bar", true);  // publish a test message to check if the MQTT broker is working
  publish_homeassistant_value_uptime_if_needed(true);
  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    BQ25798::Setting setting = bq25798.getSetting(i);
    if (setting.type == BQ25798::settings_type_t::BOOL) {
      if (!setting.is_flag) {
        publish_homeassistant_value(true, "binary_sensor", MQTT_HA_DEVICENAME, setting.name, setting.name, "", "diagnostic", "", "measurement",
                                    fix_unit(setting.unit), "");
        publish_homeassistant_value(true, "sensor", MQTT_HA_DEVICENAME, setting.name, String(setting.name) + "_numeric", "", "diagnostic", "", "measurement",
                                    fix_unit(setting.unit), "");
      }
    } else if (setting.type == BQ25798::settings_type_t::ENUM) {
      publish_homeassistant_value(true, "text", MQTT_HA_DEVICENAME, setting.name, String(setting.name) + "_string", "", "diagnostic", "", "measurement",
                                  fix_unit(setting.unit), "");
      publish_homeassistant_value(true, "sensor", MQTT_HA_DEVICENAME, setting.name, String(setting.name) + "_numeric", "", "diagnostic", "", "measurement",
                                  fix_unit(setting.unit), "");
    } else {
      publish_homeassistant_value(true, "sensor", MQTT_HA_DEVICENAME, setting.name, setting.name, "", "diagnostic", "", "measurement", fix_unit(setting.unit),
                                  "");
    }
  };
  publish_homeassistant_value(true, "sensor", MQTT_HA_DEVICENAME, "battery_temperature", "battery_temperature", "", "diagnostic", "temperature", "measurement",
                              "°C", "mdi:thermometer");
  publish_homeassistant_value(true, "sensor", MQTT_HA_DEVICENAME, "battery_percent", "battery_percent", "", "diagnostic", "battery", "measurement", "%", "");
  publish_homeassistant_value(true, "sensor", MQTT_HA_DEVICENAME, "PBAT", "PBAT", "", "diagnostic", "power", "measurement", "W", "");
  publish_homeassistant_value(true, "sensor", MQTT_HA_DEVICENAME, "PBUS", "PBUS", "", "diagnostic", "power", "measurement", "W", "");

  SYSLOG_PRINT(LOG_INFO, "Connecting to I2C...");
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  // Wire.setClock(1000);  // set I2C clock to 1 kHz // FIXME test only
  SYSLOG_PRINT(LOG_INFO, "I2C initialized on SDA=GPIO%d, SCL=GPIO%d", I2C_SDA_PIN, I2C_SCL_PIN);

  SYSLOG_PRINT(LOG_INFO, "Looking for BQ25798 on I2C bus...");
  while (!bq25798.begin()) {
    ledTimer.tick();
    delay(100);
  }
  bq25798.clearError();

  if (bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    // Reset and set up the IC if it's safe to do it
    onetimeSetup();
  }

  SYSLOG_PRINT(LOG_INFO, "Setup finished, ready.");
}

long backupRecoveryStartMillis = 0;
void loop() {
  ledTimer.tick();
  ArduinoOTA.handle();
  mqttClient.loop();
  bq25798.readAllRegisters();
  // patWatchdog();  // reset the watchdog timer
  trackChanges();
  checkForError();

  if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    ledBlinkSpeed = 200;  // blink faster in backup mode
  } else if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_OTG_MODE) {
    ledBlinkSpeed = 50;  // blink even faster in OTG mode
  } else {
    ledBlinkSpeed = 1000;  // slow blink speed in normal mode
  }

  // If in full auto mode, re-arm backup mode if needed
  if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    // check if the power source is OK for sufficient time
    if (bq25798.getAC1_PRESENT_STAT() == BQ25798::AC1_PRESENT_STAT_t::AC1_PRESENT_STAT_PRESENT) {
      if (backupRecoveryStartMillis == 0) {
        backupRecoveryStartMillis = millis();
        SYSLOG_PRINT(LOG_INFO,
                     "AC1 detected (power OK?) in backup mode, waiting for "
                     "it to be present for at least 5 seconds...");
      } else if (millis() - backupRecoveryStartMillis >= 5000) {
        SYSLOG_PRINT(LOG_INFO,
                     "AC1 is present for 5 seconds, exiting backup mode and "
                     "re-arming...");
        rearmBackupMode();
        backupRecoveryStartMillis = 0;  // reset the timer
      }
    } else {
      // AC1 is not present, reset the timer
      if (backupRecoveryStartMillis != 0) {
        SYSLOG_PRINT(LOG_WARNING, "AC1 is not present, resetting backup recovery timer.");
        backupRecoveryStartMillis = 0;
      }
    }

    // Enable the charger if VBUS is present and not in backup mode
    if (bq25798.getVBUS_PRESENT_STAT() == BQ25798::VBUS_PRESENT_STAT_t::VBUS_PRESENT_STAT_PRESENT && bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_GOOD &&
        bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
      int bat_mV = bq25798.getVBAT_ADC();
      if (bat_mV > VBAT_CHG_DISABLE_ABOVE_mV) {
        if (bq25798.getEN_CHG()) {
          SYSLOG_PRINT(LOG_INFO,
                       "Disabling charger, power is good and battery (%d) is "
                       "above limit (%d) ...",
                       bat_mV, VBAT_CHG_DISABLE_ABOVE_mV);
          bq25798.setEN_CHG(false);  // disable the charger
        }
      } else if (bat_mV < VBAT_CHG_ENABLE_BELOW_mV) {
        if (!bq25798.getEN_CHG()) {
          SYSLOG_PRINT(LOG_INFO,
                       "Enabling charger, power is good and battery (%d) is "
                       "below limit (%d)...",
                       bat_mV, VBAT_CHG_ENABLE_BELOW_mV);
          bq25798.setEN_CHG(true);  // enable the charger
        }
      }
    }

    // Enable the BACKUP mode if it accidentally got disabled (e.g. by enabling
    // the charger)
    if (!bq25798.getEN_BACKUP() && bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_GOOD &&
        bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_OTG_MODE) {
      SYSLOG_PRINT(LOG_CRIT, "BACKUP mode is disabled (why?) but shouldn't be. Re-enabling it...");
      bq25798.setEN_BACKUP(true);  // re-enable BACKUP mode
    }
  }

  publish_homeassistant_value_uptime_if_needed(false);
  delay(10);  // not too long to not interfere with the LED blinking
}
