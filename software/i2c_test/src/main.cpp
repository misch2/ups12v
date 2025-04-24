#include <Arduino.h>
#include <BQ25798.h>
#include <Wire.h>

#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22

BQ25798 bq25798 = BQ25798();

void setupForBackup() {
  if (!bq25798.readAll()) {
    Serial.println("Failed to read BQ25798 registers.");
    return;
  }

  Serial.println("Setting up BQ25798 for backup mode...");
  bq25798.setInt(bq25798.EN_BACKUP, 1);  // Enable backup mode
}

void DumpBQ25798() {
  Serial.print("\033[2J\033[H");  // an attempt to clear the screen
  Serial.println("Dumping BQ25798 registers:");

  if (!bq25798.readAll()) {
    Serial.println("Failed to read BQ25798 registers.");
    return;
  }

  Serial.printf("VSYSMIN: %5.2f V (minimal system voltage; init=R_PROG)\n", bq25798.getInt(bq25798.VSYSMIN) / 1000.0);
  Serial.printf("VREG:    %5.2f V (battery voltage regulation limit; init=R_PROG)\n", bq25798.getInt(bq25798.VREG) / 1000.0);
  Serial.printf("ICHG:    %5.2f A (charge current limit; init=R_PROG)\n", bq25798.getInt(bq25798.ICHG) / 1000.0);
  Serial.printf("VINDPM:  %5.2f V (Input Voltage Limit)\n", bq25798.getInt(bq25798.VINDPM) / 1000.0);
  Serial.printf("IINDPM:  %5.2f A (Input Current Limit)\n", bq25798.getInt(bq25798.IINDPM) / 1000.0);

  Serial.println();
  Serial.printf(
      "VBAT_LOWV: %s (Battery voltage thresholds for the transition from "
      "precharge to fast charge)\n",
      bq25798.toString(bq25798.getInt(bq25798.VBAT_LOWV), bq25798.VBAT_LOWV_strings));
  Serial.printf("IPRECHG: %5.2f mA (Precharge current limit)\n", bq25798.getInt(bq25798.IPRECHG) / 1000.0);
  Serial.printf("ITERM:   %5.2f mA   (Termination Current)\n", bq25798.getInt(bq25798.ITERM) / 1000.0);
  Serial.printf("TRECHG: %s   (Battery recharge deglich time)\n", bq25798.toString(bq25798.getInt(bq25798.TRECHG), bq25798.TRECHG_strings));
  Serial.printf("VRECHG: %5d mV  (Battery Recharge Threshold Offset (Below VREG))\n", bq25798.getInt(bq25798.VRECHG));
  Serial.printf("PRECHG_TMR: %s\n", bq25798.toString(bq25798.getInt(bq25798.PRECHG_TMR), bq25798.PRECHG_TMR_strings));
  Serial.printf("CELL: %s          (Cell Configuration read at POR)\n", bq25798.toString(bq25798.getInt(bq25798.CELL), bq25798.CELL_strings));

  Serial.printf("VBUS_BACKUP: %s  (VBUS Backup Mode)\n", bq25798.toString(bq25798.getInt(bq25798.VBUS_BACKUP), bq25798.VBUS_BACKUP_strings));
  Serial.printf("WATCHDOG: %s     (Watchdog Timer)\n", bq25798.toString(bq25798.getInt(bq25798.WATCHDOG), bq25798.WATCHDOG_strings));

  Serial.println();
  Serial.println("ADCs:");
  Serial.printf("\tADC_RATE: %s\n", bq25798.toString(bq25798.getInt(bq25798.ADC_RATE), bq25798.ADC_RATE_strings));
  Serial.printf("\tADC_SAMPLE: %s\n", bq25798.toString(bq25798.getInt(bq25798.ADC_SAMPLE), bq25798.ADC_SAMPLE_strings));
  Serial.printf("\tADC_AVG: %d\n", bq25798.getInt(bq25798.ADC_AVG));
  Serial.printf("\tADC_AVG_INIT: %d\n", bq25798.getInt(bq25798.ADC_AVG_INIT));

  Serial.println();
  Serial.printf(
      "\tBUS: %5.2f A * %5.2f V = %.3f W (Charger input; + = VBUS -> PMID, - = "
      "reverse)\n",
      bq25798.getInt(bq25798.IBUS_ADC) / 1000.0, bq25798.getInt(bq25798.VBUS_ADC) / 1000.0,
      bq25798.getInt(bq25798.IBUS_ADC) * bq25798.getInt(bq25798.VBUS_ADC) / 1000000.0);
  Serial.printf(
      "\tBAT: %5.2f A * %5.2f V = %.3f W (signbit=0 for charging, 1 for "
      "discharging)\n",
      bq25798.getInt(bq25798.IBAT_ADC) / 1000.0, bq25798.getInt(bq25798.VBAT_ADC) / 1000.0,
      bq25798.getInt(bq25798.IBAT_ADC) * bq25798.getInt(bq25798.VBAT_ADC) / 1000000.0);
  Serial.printf(
      "\tSYS: %5.2f V                     (The Charger Output Voltage to "
      "System)\n",
      bq25798.getInt(bq25798.VSYS_ADC) / 1000.0);
  Serial.printf(
      "\tAC1: %5.2f V                     (=VBUS if ACFET1/RBFET1 not "
      "installed)\n",
      bq25798.getInt(bq25798.VAC1_ADC) / 1000.0);
  Serial.printf(
      "\tAC2: %5.2f V                     (=VBUS if ACFET2/RBFET2 not "
      "installed)\n",
      bq25798.getInt(bq25798.VAC2_ADC) / 1000.0);
  Serial.printf(
      "\tTS:  %5.2f %%                     (Temperature Qualification Voltage "
      "Input)\n",
      bq25798.getFloat(bq25798.TS_ADC));
  Serial.printf("\tTDIE: %5.2f degC\n", bq25798.getFloat(bq25798.TDIE_ADC));
  Serial.printf("\tDPLUS / DMINUS: %.2f V / %.2f V\n", bq25798.getInt(bq25798.DPLUS_ADC) / 1000.0, bq25798.getInt(bq25798.DMINUS_ADC) / 1000.0);

  Serial.println("");
  Serial.println("Backup mode settings:");
  Serial.printf("\tEN_BACKUP: %d", bq25798.getInt(bq25798.EN_BACKUP));
  Serial.printf(", EN_CHG: %d", bq25798.getInt(bq25798.EN_CHG));
  Serial.printf(", EN_ICO: %d", bq25798.getInt(bq25798.EN_ICO));
  Serial.printf(", EN_TERM: %d", bq25798.getInt(bq25798.EN_TERM));
  Serial.printf(", EN_HIZ: %d\n", bq25798.getInt(bq25798.EN_HIZ));
  Serial.printf("\tCHG_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.CHG_STAT), bq25798.CHG_STAT_strings));
  Serial.printf("\tVBUS_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.VBUS_STAT), bq25798.VBUS_STAT_strings));

  Serial.println();
  Serial.printf("PN=%d (%s), DEV_REV=%d (%s)\n", bq25798.getInt(bq25798.PN), bq25798.toString(bq25798.getInt(bq25798.PN), bq25798.PN_strings),
                bq25798.getInt(bq25798.DEV_REV), bq25798.toString(bq25798.getInt(bq25798.DEV_REV), bq25798.DEV_REV_strings));

  Serial.println("====================================================");
}

void resetWatchdog() {
  // FIXME is this needed and does it do what we want?
  bq25798.setInt(bq25798.WATCHDOG, static_cast<int>(BQ25798::watchdog_t::WATCHDOG_DISABLE));
}

void enableADC() {
  // FIXME is this needed? ADC should be enabled by default
  bq25798.setInt(bq25798.ADC_ENABLE, 1);
}

void setup() {
  Serial.begin(115200);
  Serial.println("Serial port initialized");
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Serial.printf("I2C initialized on SDA=GPIO%d, SCL=GPIO%d\n", I2C_SDA_PIN, I2C_SCL_PIN);
  if (!bq25798.begin()) {
    Serial.println("Failed to initialize BQ25798, stopping here.");
    while (1) {
      delay(1000);
    }
  }

  resetWatchdog();
  enableADC();
  setupForBackup();
}

void loop() {
  DumpBQ25798();
  resetWatchdog();
  delay(10000);
}
