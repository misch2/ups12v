#include <ArduinoOTA.h>
#include <BQ25798.h>
#include <Syslog.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include <WiFiUdp.h>
#include <Wire.h>

// #include <Timer.h>
#include <arduino-timer.h>

#include <array>

#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22

#define HOSTNAME "esp18-bq25798-ups1"

// -----------------------------------------------------------------------

#define SYSLOG_SERVER IPAddress(10, 52, 7, 101) // "logserver.localnet"  // FIXME better use IP
#define SYSLOG_PORT 514
#define SYSLOG_MYHOSTNAME "esp18" /* a board number, not a chip ID */
#define SYSLOG_MYAPPNAME "bq25798-ups1"

#ifdef SYSLOG_SERVER
// A UDP instance to let us send and receive packets over UDP
WiFiUDP udpClient;
// Create a new syslog instance with LOG_KERN facility
Syslog syslog(udpClient, SYSLOG_SERVER, SYSLOG_PORT, SYSLOG_MYHOSTNAME, SYSLOG_MYAPPNAME, LOG_KERN);
  #define SYSLOG_PRINT(fmt, ...)                          \
    Serial.printf(fmt, ##__VA_ARGS__);                    \
    Serial.print('\n');                                   \
    Serial.flush();                                       \
    if (WiFi.status() == WL_CONNECTED) {                  \
      for (int i = 0; i < 3; i++) {                       \
        if (syslog.logf(LOG_INFO, fmt, ##__VA_ARGS__)) {  \
          break;                                          \
        } else {                                          \
          delay(100);                                     \
        }                                                 \
      }                                                   \
    } else {                                              \
      Serial.println(" (no syslog, WiFi not connected)"); \
    }
#else
  #define SYSLOG_PRINT(fmt, ...)       \
    Serial.printf(fmt, ##__VA_ARGS__); \
    Serial.print('\n')
#endif

// -----------------------------------------------------------------------

constexpr int VINDPM_mV = 12000;  // Input voltage DPM threshold in mV
constexpr int IINDPM_mA = 3000;   // Input current DPM threshold in mA

constexpr int VOTG_mV = 12000;  // Output voltage for OTG mode
constexpr int IOTG_mA = 3200;   // Output current for OTG mode in mA

constexpr int VBAT_CHG_ENABLE_BELOW_mV = 16000;   // Voltage at which the charger is enabled in mV
constexpr int VBAT_CHG_DISABLE_ABOVE_mV = 16600;  // Voltage at which the charger is disabled in mV
constexpr int ICHG_mA = 500;                      // Charge current in mA (max)

constexpr BQ25798::VBUS_BACKUP_t VBUS_BACKUP_SWICHOVER = BQ25798::VBUS_BACKUP_t::PCT_VBUS_BACKUP_80;  // VBUS backup percentage (80 % of 12 V = 9.6 V)

// constexpr int VOTG_mV = 5000;             // Output voltage for OTG mode
// constexpr int IOTG_mA = 1000;             // Output current for OTG mode in mA
// constexpr int VINDPM_mV = VOTG_mV - 500;  // Input voltage DPM threshold in mV

constexpr int LED_PIN = 2;  // GPIO pin for the LED

// 5 * 60 * 1000L;  // 5 minutes
const long ADC_readout_time_millis = 30 * 1000L; // 30 seconds

WiFiManager wifiManager;

BQ25798 bq25798 = BQ25798();

std::array<int, BQ25798::SETTINGS_COUNT> oldRawValues;
std::array<int, BQ25798::SETTINGS_COUNT> newRawValues;
long startMillis = 0;
long lastADCReadMillis = 0;

bool fullAutoMode = true;  // Set to false to disable full auto mode and use manual settings

auto ledTimer = timer_create_default();  // create a timer with default settings
unsigned long ledBlinkSpeed = 100;       // LED toggle speed in milliseconds
bool toggle_led(void *) {
  digitalWrite(LED_PIN, !digitalRead(LED_PIN));  // toggle the LED
  ledTimer.in(ledBlinkSpeed / 2, &toggle_led);   // rearm the timer
  return false;                                  // keep existing timer active?
}

void patWatchdog() {
  // To keep the device in host mode, the host has  to reset the watchdog timer by writing 1 to WD_RST bit before the watchdog timer expires
  bq25798.setWD_RST(true);  // reset the watchdog timer
}

bool checkForError() {
  if (bq25798.lastError()) {
    SYSLOG_PRINT("Error: %d\n", bq25798.lastError());
    bq25798.clearError();
    return true;
  }
  return false;
}

void printMostImportantStats() {
  Serial.printf("Main stats: ");

  if (bq25798.getIINDPM_STAT() == BQ25798::IINDPM_STAT_t::IINDPM_STAT_REGULATION ||
      bq25798.getVINDPM_STAT() == BQ25798::VINDPM_STAT_t::VINDPM_STAT_REGULATION) {
    Serial.printf("IN_DPM! ");
  };
  if (bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_BAD) {
    Serial.printf("NOT_PG! ");
  };
  if (bq25798.getEN_HIZ()) {
    Serial.printf("HIZ_EN! ");
  };
  if (bq25798.getVSYS_STAT() == BQ25798::VSYS_STAT_t::VSYS_STAT_IN_VSYSMIN_REGULATION) {
    Serial.printf("VSYS_REG! ");
  };
  if (bq25798.getVBUS_PRESENT_STAT() == BQ25798::VBUS_PRESENT_STAT_t::VBUS_PRESENT_STAT_NOT_PRESENT) {
    Serial.printf("NO_VBUS! ");
  };
  if (bq25798.getAC1_PRESENT_STAT() == BQ25798::AC1_PRESENT_STAT_t::AC1_PRESENT_STAT_NOT_PRESENT) {
    Serial.printf("NO_AC1! ");
  };
  if (bq25798.getVBAT_PRESENT_STAT() == BQ25798::VBAT_PRESENT_STAT_t::VBAT_PRESENT_STAT_NOT_PRESENT) {
    Serial.printf("NO_VBAT! ");
  };

  if (bq25798.getTS_IGNORE()) {
    Serial.printf("+TS_IGNORE ");
  };
  if (bq25798.getEN_BACKUP()) {
    Serial.printf("+EN_BACKUP ");
  };
  if (bq25798.getEN_OTG()) {
    Serial.printf("+EN_OTG ");
  };
  if (bq25798.getEN_CHG()) {
    Serial.printf("+EN_CHG ");
  };
  if (bq25798.getEN_ACDRV1()) {
    Serial.printf("+EN_ACDRV1 ");
  };
  Serial.printf("CHG=[%d]\"%s\" ", bq25798.getInt(bq25798.CHG_STAT), bq25798.getString(bq25798.CHG_STAT));

  Serial.println();
}

void trackChanges() {
  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    BQ25798::Setting setting = bq25798.getSetting(i);
    newRawValues[i] = bq25798.getRaw(setting);
    if (checkForError()) {
      SYSLOG_PRINT("Error reading setting %d (%s)\n", i, setting.name);
      return;  // stop tracking changes if there is an error
    }
  }

  bool justStarted = false;
  if (startMillis == 0) {
    justStarted = true;
    startMillis = millis();
    lastADCReadMillis = startMillis;

    for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
      oldRawValues[i] = 0xFFFF;  // set to invalid value
    }

    // First time just copy the values
    // Serial.println("First time reading BQ25798 settings...");
    // for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    //   oldRawValues[i] = newRawValues[i];
    // }
    // Serial.println("Waiting for changes...");
    // return;
  }

  // every next time check if the values changed
  long elapsedMillis = millis() - startMillis;
  bool changed = false;
  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    if (oldRawValues[i] != newRawValues[i]) {
      BQ25798::Setting setting = bq25798.getSetting(i);

      // exception: do not notify about flags set to FALSE because any read operation will reset them to FALSE
      if (setting.is_flag && newRawValues[i] == 0) {
        continue;
      }

      char message_new[250] = "";
      char message_old[250] = "";
      char type_info[100] = "";

      changed = true;

      if (setting.type == BQ25798::settings_type_t::FLOAT) {
        snprintf(type_info, sizeof(type_info), "%s (%s, %s)", setting.name, "float", setting.unit);
        snprintf(message_new, sizeof(message_new), "%25s = %-20.3f    ",  //
                 type_info, bq25798.rawToFloat(newRawValues[i], setting));
        if (!justStarted) {
          snprintf(message_old, sizeof(message_old), "(was %.3f)",  //
                   bq25798.rawToFloat(oldRawValues[i], setting));
        }
      } else if (setting.type == BQ25798::settings_type_t::BOOL) {
        if (setting.is_flag) {  // if this is a flag, it can only be TRUE, see the skip for false above
          snprintf(type_info, sizeof(type_info), "%s (%s)", setting.name, "flag");
          snprintf(message_new, sizeof(message_new), "%25s = %-50s     ",  //
                   type_info, bq25798.rawToBool(newRawValues[i], setting) ? "TRIGGERED" : "");
        } else {
          snprintf(type_info, sizeof(type_info), "%s (%s)", setting.name, "bool");
          snprintf(message_new, sizeof(message_new), "%25s = %-50s     ",  //
                   type_info, bq25798.rawToBool(newRawValues[i], setting) ? "TRUE" : "false");
          if (!justStarted) {
            snprintf(message_old, sizeof(message_old), "(was %s)",  //
                     bq25798.rawToBool(oldRawValues[i], setting) ? "TRUE" : "false");
          }
        }
      } else if (setting.type == BQ25798::settings_type_t::ENUM) {
        snprintf(type_info, sizeof(type_info), "%s (%s)", setting.name, "enum");
        snprintf(message_new, sizeof(message_new), "%25s = [%d] \"%s\"%*s",  //
                 type_info, newRawValues[i], bq25798.rawToString(newRawValues[i], setting), 50 - 1 - strlen(bq25798.rawToString(newRawValues[i], setting)), "");
        if (!justStarted) {
          snprintf(message_old, sizeof(message_old), "(was [%d] \"%s\")",  //
                   oldRawValues[i], bq25798.rawToString(oldRawValues[i], setting));
        };
      } else if (setting.type == BQ25798::settings_type_t::INT) {
        snprintf(type_info, sizeof(type_info), "%s (%s, %s)", setting.name, "int", setting.unit);
        snprintf(message_new, sizeof(message_new), "%25s = %-50d     ",  //
                 type_info, bq25798.rawToInt(newRawValues[i], setting));
        if (!justStarted) {
          snprintf(message_old, sizeof(message_old), "(was %5d)",  //
                   bq25798.rawToInt(oldRawValues[i], setting));
        }
      }
      SYSLOG_PRINT("%s%s", message_new, message_old);
    }
  }
  // if (changed) {
  //   printMostImportantStats();
  //   Serial.println();  // group the changes
  // }

  // update the old values
  for (int i = 0; i < BQ25798::SETTINGS_COUNT; i++) {
    oldRawValues[i] = newRawValues[i];
  }

  // // Every N seconds read the ADC values in one-shot mode
  if (fullAutoMode) {
    long elapsedADCMillis = millis() - lastADCReadMillis;
    if (elapsedADCMillis >= ADC_readout_time_millis) {
      Serial.printf("ADC readout elapsed time: %ld ms\n", elapsedADCMillis);
      lastADCReadMillis = millis();
      bq25798.setADC_EN(true);  // trigger ADC one-shot mode
    }
  }
}

void toggleCharger() {
  // Toggle the charger state
  if (bq25798.getEN_CHG()) {
    SYSLOG_PRINT("Disabling charger...");
    bq25798.setEN_CHG(false);
  } else {
    SYSLOG_PRINT("Enabling charger...");
    bq25798.setEN_CHG(true);
  }
}

void onetimeSetup() {
  SYSLOG_PRINT("Resetting the IC completely...");
  bq25798.setREG_RST(true);  // reset the IC
  while (bq25798.getREG_RST()) {
    ledTimer.tick();
    delay(10);
    bq25798.readAllRegisters();
  }
  SYSLOG_PRINT("Reset successful.");

  // FIXME to prevent chip reset when the host controller is disconnected temporarily
  bq25798.setWATCHDOG(BQ25798::WATCHDOG_t::WATCHDOG_DISABLE);  // disable watchdog timer

  // enable one-time ADC readout
  bq25798.setADC_RATE(BQ25798::ADC_RATE_t::ADC_RATE_ONESHOT);
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
  // bq25798.setEN_OTG(1);  // no, this is not the same as EN_BACKUP. EN_OTG would provide power back to the input without disabling the ACFET/RBFET
  bq25798.setEN_BACKUP(true);

  SYSLOG_PRINT("One-time setup complete.");
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

  SYSLOG_PRINT("Exiting backup mode and re-arming UPS...");

  // When a backup mode is entered automatically, the following happens:
  // DIS_ACDRV is set to TRUE, EN_OTG is set to TRUE, EN_ACDRV1 is set to FALSE, PG is set to FALSE and VBUS_STAT is set to "Backup"
  //
  // So let's check if we are still in backup mode:

  if (bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    SYSLOG_PRINT("Error: VBUS_STAT is not BACKUP_MODE");
    return;
  }
  if (!bq25798.getDIS_ACDRV()) {
    SYSLOG_PRINT("In backup mode Error: ACDRV is not globally disabled, cannot re-arm.");
    return;
  }
  if (!bq25798.getEN_OTG()) {
    SYSLOG_PRINT("In backup mode Error: OTG is not active, cannot re-arm.");
    return;
  }

  // See page 37 of the BQ25798 datasheet:
  // If there is an adapter reconnected while the charger is in backup mode, the user may transition the source which
  // powers the PMID load from the battery back to the adapter. The following sequence is used to switch from the
  // battery power back to ACIN1 while simultaneously re-arming the backup mode:
  // 1. Write BKUP_ACFET1_ON (REG0x16[0]) register bit to 1. Setting BKUP_ACFET1 _ON = 1 will cause the
  // device to set DIS_ACDRV = 0 and EN_ACDRV1 = 1. After that, backup mode is disabled, however, the
  // charger remains in the normal OTG mode. The ACFET1-RBFET1 is turned on to connect the adapter to
  // VBUS. The user must ensure the adapter voltage is equal to or higher than the charger VOTG voltage
  // setting, otherwise, the charger OTG output might back drive the adapter connected to VBUS.
  // 2. Determine the source at ACIN1 is valid (is not in overvoltage and did not fail poor source detection) by
  // reading back EN_ACDRV1 as 1.
  // 3. Set EN_OTG = 0, in order to exit OTG mode and enter the forward charging mode without PMID voltage
  // crash. Setting BKUP_ACFET1_ON = 1, also clears BKUP_ACFET1_ON to 0 and sets EN_BACKUP to 1.

  if (bq25798.getAC1_PRESENT_STAT() != BQ25798::AC1_PRESENT_STAT_t::AC1_PRESENT_STAT_PRESENT) {
    SYSLOG_PRINT("Error: AC1 is not present, cannot re-arm.");
    return;
  }

  // Disable charger to prevent any charging while we are in the OTG mode
  SYSLOG_PRINT("Disabling charger...");
  bq25798.setEN_CHG(false);  // disable the charger
  trackChanges();

  // BKUP_ACFET1_ON does the following:
  // - set DIS_ACDRV to 0 && set EN_ACDRV1 to 1 (enable ACDRV1)
  // - set EN_BACKUP to 0 (disable backup mode) -- why does it do this???
  // - set BKUP_ACFET1_ON to 1
  // it also sets the VBUS_STAT to OTG
  SYSLOG_PRINT("Setting BKUP_ACFET1_ON to 1...");
  bq25798.setBKUP_ACFET1_ON(true);  // turn on the ACFET1-RBFET1 to connect the adapter to VBUS
  trackChanges();

  SYSLOG_PRINT("Waiting for a confirmation of ACFET1 enabled...");
  if (!waitForBQCondition([]() { return bq25798.getEN_ACDRV1() == true; })) {
    SYSLOG_PRINT("Error: failed to turn ACDRV1 on.");
    return;
  }

  // EN_OTG should do the following when BKUP_ACFET1_ON is active:
  // - set EN_OTG to 0 (exit OTG mode)
  // - set EN_BACKUP to 1 (re-arm backup mode -- that's because BKUP_ACFET1_ON is still set to 1)
  // - set BKUP_ACFET1_ON to 0
  // it also sets VBUS_STAT to normal input mode
  SYSLOG_PRINT("Proceeding to exit OTG mode...");
  bq25798.setEN_OTG(false);  // exit OTG mode and enter the forward charging mode without PMID voltage crash
  trackChanges();

  SYSLOG_PRINT("Waiting for a confirmation of OTG disabled and backup re-enabled...");
  if (!waitForBQCondition([]() { return bq25798.getEN_OTG() == false && bq25798.getEN_BACKUP() == true; })) {
    SYSLOG_PRINT("Error: failed to exit OTG mode and re-arm.");
    return;
  }

  SYSLOG_PRINT("Waiting for PG_STAT to be GOOD...");
  if (!waitForBQCondition([]() { return bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_GOOD; })) {
    SYSLOG_PRINT("Error: failed to re-arm backup mode, PG_STAT is not GOOD.");
    return;
  }

  SYSLOG_PRINT("Backup mode re-armed.");
}

void setup() {
  Serial.begin(115200);
  Serial.println("Serial port initialized");

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);                   // turn off the LED
  ledTimer.in(ledBlinkSpeed / 2, &toggle_led);  // start the timer

  // Connect to WiFi
  wifiManager.setHostname(HOSTNAME);
  wifiManager.setConnectRetries(3);
  wifiManager.setConnectTimeout(15);            // 15 seconds
  wifiManager.setConfigPortalTimeout(10 * 60);  // Stay 10 minutes max in the AP web portal, then reboot
  bool res = wifiManager.autoConnect();
  if (!res) {
    Serial.println("Failed to connect to wifi");
  }

  SYSLOG_PRINT("Connected to WiFi: %s (%s)\n", WiFi.SSID().c_str(), WiFi.localIP().toString().c_str());

  ArduinoOTA.setHostname(HOSTNAME);
  ArduinoOTA.begin();

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  // Wire.setClock(1000);  // set I2C clock to 1 kHz // FIXME test only
  SYSLOG_PRINT("I2C initialized on SDA=GPIO%d, SCL=GPIO%d", I2C_SDA_PIN, I2C_SCL_PIN);

  SYSLOG_PRINT("Looking for BQ25798 on I2C bus...");
  while (!bq25798.begin()) {
    ledTimer.tick();
    delay(100);
  }
  bq25798.clearError();

  SYSLOG_PRINT("Connected.");

  SYSLOG_PRINT("Setting up BQ25798...");

  // Disable watchdog timer (it would otherwise reset the chip if not cleared in time):
  // bq25798.setWATCHDOG(BQ25798::WATCHDOG_t::WATCHDOG_DISABLE);
  // ^we are reading values in loop() so it should not be needed

  // // Disable thermal sensor (not connected):
  // bq25798.setTS_IGNORE(true);

  // Enable ADC one shot mode. ADC_EN will be set to 0 after the readout is done.
  // A continuous ADC would otherwise produce too much visual noise (a lot of changes).
  bq25798.setADC_RATE(BQ25798::ADC_RATE_t::ADC_RATE_ONESHOT);
  bq25798.setADC_SAMPLE(BQ25798::ADC_SAMPLE_t::ADC_SAMPLE_15BIT);
  delay(100);

  // onetimeSetup();  // for the first time
  // rearmBackupMode();

  SYSLOG_PRINT("BQ25798 basic setup complete.");

  if (fullAutoMode && bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
    SYSLOG_PRINT("Full auto mode enabled, one-time setup done.");
    onetimeSetup();  // for the first time
  }

  SYSLOG_PRINT("Setup finished, ready.");
}

long backupRecoveryStartMillis = 0;
void loop() {
  ledTimer.tick();
  ArduinoOTA.handle();
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

  if (fullAutoMode) {
    // If in full auto mode, re-arm backup mode if needed
    if (bq25798.getVBUS_STAT() == BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
      // check if the power source is OK for sufficient time
      if (bq25798.getAC1_PRESENT_STAT() == BQ25798::AC1_PRESENT_STAT_t::AC1_PRESENT_STAT_PRESENT) {
        if (backupRecoveryStartMillis == 0) {
          backupRecoveryStartMillis = millis();
          SYSLOG_PRINT("AC1 detected (power OK?) in backup mode, waiting for it to be present for at least 5 seconds...");
        } else if (millis() - backupRecoveryStartMillis >= 5000) {
          SYSLOG_PRINT("AC1 is present for 5 seconds, exiting backup mode and re-arming...");
          rearmBackupMode();
          backupRecoveryStartMillis = 0;  // reset the timer
        }
      } else {
        // AC1 is not present, reset the timer
        if (backupRecoveryStartMillis != 0) {
          SYSLOG_PRINT("AC1 is not present, resetting backup recovery timer.");
          backupRecoveryStartMillis = 0;
        }
      }
    }

    // Enable the charger if VBUS is present and not in backup mode
    if (bq25798.getVBUS_PRESENT_STAT() == BQ25798::VBUS_PRESENT_STAT_t::VBUS_PRESENT_STAT_PRESENT && bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_GOOD &&
        bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_BACKUP_MODE) {
      int bat_mV = bq25798.getVBAT_ADC();
      if (bat_mV > VBAT_CHG_DISABLE_ABOVE_mV) {
        if (bq25798.getEN_CHG()) {
          SYSLOG_PRINT("Disabling charger, power is good and battery (%d) is above limit (%d) ...", bat_mV, VBAT_CHG_DISABLE_ABOVE_mV);
          bq25798.setEN_CHG(false);  // disable the charger
        }
      } else if (bat_mV < VBAT_CHG_ENABLE_BELOW_mV) {
        if (!bq25798.getEN_CHG()) {
          SYSLOG_PRINT("Enabling charger, power is good and battery (%d) is below limit (%d)...", bat_mV, VBAT_CHG_ENABLE_BELOW_mV);
          bq25798.setEN_CHG(true);  // enable the charger
        }
      }
    }

    // Enable the BACKUP mode if it accidentally got disabled (e.g. by enabling the charger)
    if (!bq25798.getEN_BACKUP() && bq25798.getPG_STAT() == BQ25798::PG_STAT_t::PG_STAT_GOOD &&
        bq25798.getVBUS_STAT() != BQ25798::VBUS_STAT_t::VBUS_STAT_OTG_MODE) {
      SYSLOG_PRINT("BACKUP mode is disabled (why?) but shouldn't be. Re-enabling it...");
      bq25798.setEN_BACKUP(true);  // re-enable BACKUP mode
    }
  }

  // If user pressed the 'p' (poke) key, try to re-arm backup mode again
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 'r' || c == 'R') {
      rearmBackupMode();
    } else if (c == 'c' || c == 'C') {
      toggleCharger();  // toggle the charger state
    } else if (c == 'x' || c == 'X') {
      onetimeSetup();  // re-setup the BQ25798
    } else if (c == 'a' || c == 'A') {
      bq25798.setADC_EN(true);  // trigger ADC one-shot mode
    } else if (c == '1') {
      bq25798.setBKUP_ACFET1_ON(!bq25798.getBKUP_ACFET1_ON());  // toggle BKUP_ACFET1_ON
      Serial.printf("BKUP_ACFET1_ON set to %d\n", bq25798.getBKUP_ACFET1_ON());
    } else if (c == '2') {
      bq25798.setEN_ACDRV1(!bq25798.getEN_ACDRV1());  // toggle ACDRV1
      Serial.printf("ACDRV1 set to %d\n", bq25798.getEN_ACDRV1());
    } else if (c == '3') {
      bq25798.setEN_OTG(!bq25798.getEN_OTG());  // toggle OTG
      Serial.printf("OTG set to %d\n", bq25798.getEN_OTG());
    } else if (c == '4') {
      bq25798.setEN_BACKUP(!bq25798.getEN_BACKUP());  // toggle BACKUP
      Serial.printf("BACKUP set to %d\n", bq25798.getEN_BACKUP());
    } else if (c == '5') {
      bq25798.setFORCE_INDET(!bq25798.getFORCE_INDET());  // toggle FORCE_INDET
      Serial.printf("FORCE_INDET set to %d\n", bq25798.getFORCE_INDET());
    } else if (c == '\r' || c == '\n') {
      // Ignore new line characters
      Serial.println();
    } else {
      Serial.printf("Unknown command: '%c'\n", c);
      Serial.println("Press 'r' to re-arm backup mode, 'c' to toggle charger state, 'a' to trigger ADC read or 'x' to reset.");
      Serial.println("Toggles: 1=BKUP_ACFET1, 2=ACDRV1, 3=OTG, 4=BACKUP, 5=FORCE_INDET");
    }
  }

  delay(100);
}
