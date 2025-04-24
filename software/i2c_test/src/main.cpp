#include <Arduino.h>
#include <BQ25798.h>
#include <Wire.h>

#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22

BQ25798 bq25798 = BQ25798();

void DumpBQ25798() {
  // Serial.print("\033[2J\033[H");  // an attempt to clear the screen
  Serial.println();
  Serial.println("Dumping BQ25798 registers:");

  if (!bq25798.readAll()) {
    Serial.println("Failed to read BQ25798 registers.");
    return;
  }

  Serial.printf("VSYSMIN: %6.3f V (minimal system voltage; init=R_PROG)\n", bq25798.getInt(bq25798.VSYSMIN) / 1000.0);
  Serial.printf("VREG:    %6.3f V (battery voltage regulation limit; init=R_PROG)\n", bq25798.getInt(bq25798.VREG) / 1000.0);
  Serial.printf("ICHG:    %6.3f A (charge current limit; init=R_PROG)\n", bq25798.getInt(bq25798.ICHG) / 1000.0);

  Serial.println();
  Serial.printf("VINDPM:  %6.3f V (input voltage limit)\n", bq25798.getInt(bq25798.VINDPM) / 1000.0);
  Serial.printf("IINDPM:  %6.3f A (input current limit)\n", bq25798.getInt(bq25798.IINDPM) / 1000.0);

  Serial.println();
  // Serial.printf("IPRECHG: %5.3f mA (Precharge current limit)\n", bq25798.getInt(bq25798.IPRECHG) / 1000.0);
  // Serial.printf("ITERM:   %5.3f mA   (Termination Current)\n", bq25798.getInt(bq25798.ITERM) / 1000.0);
  // Serial.printf("TRECHG:  %s   (Battery recharge deglich time)\n", bq25798.toString(bq25798.getInt(bq25798.TRECHG), bq25798.TRECHG_strings));
  // Serial.printf("VRECHG:  %5d mV  (Battery Recharge Threshold Offset (Below VREG))\n", bq25798.getInt(bq25798.VRECHG));
  // Serial.printf("PRECHG_TMR: %s\n", bq25798.toString(bq25798.getInt(bq25798.PRECHG_TMR), bq25798.PRECHG_TMR_strings));
  // Serial.printf("CELL: %s          (Cell Configuration read at POR)\n", bq25798.toString(bq25798.getInt(bq25798.CELL), bq25798.CELL_strings));
  Serial.printf("  VBAT_LOWV: %s\n",  //
                bq25798.toString(bq25798.getInt(bq25798.VBAT_LOWV), bq25798.VBAT_LOWV_strings));

  Serial.printf("VBUS_BACKUP: %s\n",  //
                bq25798.toString(bq25798.getInt(bq25798.VBUS_BACKUP), bq25798.VBUS_BACKUP_strings));

  Serial.printf("   Watchdog: %s, %s\n",  //
                bq25798.toString(bq25798.getInt(bq25798.WATCHDOG), bq25798.WATCHDOG_strings),
                bq25798.toString(bq25798.getInt(bq25798.WD_STAT), bq25798.WD_STAT_strings));

  Serial.printf("      Power: %s, %s\n",  //
                bq25798.toString(bq25798.getInt(bq25798.PG_STAT), bq25798.PG_STAT_strings),
                bq25798.toString(bq25798.getInt(bq25798.VBUS_PRESENT_STAT), bq25798.VBUS_PRESENT_STAT_strings));

  Serial.printf(" ADCs setup: %s, %s, %s\n",  //
                bq25798.toString(bq25798.getInt(bq25798.ADC_RATE), bq25798.ADC_RATE_strings),
                bq25798.toString(bq25798.getInt(bq25798.ADC_SAMPLE), bq25798.ADC_SAMPLE_strings),
                bq25798.toString(bq25798.getInt(bq25798.ADC_AVG), bq25798.ADC_AVG_strings));

  // Serial.printf("\tIBUS=%s", bq25798.getInt(bq25798.IBUS_ADC_DIS) ? "DISABLED" : "ENABLED");
  // Serial.printf(", IBAT=%s", bq25798.getInt(bq25798.IBAT_ADC_DIS) ? "DISABLED" : "ENABLED");
  // Serial.printf(", VBUS=%s", bq25798.getInt(bq25798.VBUS_ADC_DIS) ? "DISABLED" : "ENABLED");
  // Serial.printf(", VBAT=%s", bq25798.getInt(bq25798.VBAT_ADC_DIS) ? "DISABLED" : "ENABLED");
  // Serial.printf(", VSYS=%s", bq25798.getInt(bq25798.VSYS_ADC_DIS) ? "DISABLED" : "ENABLED");
  // Serial.printf(", TS=%s", bq25798.getInt(bq25798.TS_ADC_DIS) ? "DISABLED" : "ENABLED");
  // Serial.printf(", TDIE=%s", bq25798.getInt(bq25798.TDIE_ADC_DIS) ? "DISABLED" : "ENABLED");
  // Serial.printf(", D+=%s", bq25798.getInt(bq25798.DPLUS_ADC_DIS) ? "DISABLED" : "ENABLED");
  // Serial.printf(", D-=%s", bq25798.getInt(bq25798.DMINUS_ADC_DIS) ? "DISABLED" : "ENABLED");
  // Serial.printf(", VAC1=%s", bq25798.getInt(bq25798.VAC1_ADC_DIS) ? "DISABLED" : "ENABLED");
  // Serial.printf(", VAC2=%s", bq25798.getInt(bq25798.VAC2_ADC_DIS) ? "DISABLED" : "ENABLED");
  // Serial.println();

  Serial.println();
  Serial.printf("    ADC BUS: %5.3f A * %6.3f V = %6.3f W (Charger input; + = VBUS -> PMID, - = reverse)\n", bq25798.getInt(bq25798.IBUS_ADC) / 1000.0,
                bq25798.getInt(bq25798.VBUS_ADC) / 1000.0, bq25798.getInt(bq25798.IBUS_ADC) * bq25798.getInt(bq25798.VBUS_ADC) / 1000000.0);
  Serial.printf("    ADC BAT: %5.3f A * %6.3f V = %6.3f W (+ = charging, - = discharging)\n", bq25798.getInt(bq25798.IBAT_ADC) / 1000.0,
                bq25798.getInt(bq25798.VBAT_ADC) / 1000.0, bq25798.getInt(bq25798.IBAT_ADC) * bq25798.getInt(bq25798.VBAT_ADC) / 1000000.0);
  Serial.printf("    ADC SYS:           %6.3f V            (The Charger Output Voltage to System)\n", bq25798.getInt(bq25798.VSYS_ADC) / 1000.0);
  Serial.printf("       TDIE: %.1f °C\n", bq25798.getFloat(bq25798.TDIE_ADC));
  // Serial.printf(
  //     "\tAC1: %5.3f V                     (=VBUS if ACFET1/RBFET1 not "
  //     "installed)\n",
  //     bq25798.getInt(bq25798.VAC1_ADC) / 1000.0);
  // Serial.printf(
  //     "\tAC2: %5.3f V                     (=VBUS if ACFET2/RBFET2 not "
  //     "installed)\n",
  //     bq25798.getInt(bq25798.VAC2_ADC) / 1000.0);
  // Serial.printf(
  //     "\tTS:  %5.3f %%                     (Temperature Qualification Voltage "
  //     "Input)\n",
  //     bq25798.getFloat(bq25798.TS_ADC));
  // Serial.printf("\tDPLUS / DMINUS: %.3f V / %.3f V\n", bq25798.getInt(bq25798.DPLUS_ADC) / 1000.0, bq25798.getInt(bq25798.DMINUS_ADC) / 1000.0);

  Serial.println();
  Serial.println("Backup mode settings:");
  Serial.printf("\tEN_BACKUP: %d", bq25798.getInt(bq25798.EN_BACKUP));
  Serial.printf(", EN_CHG: %d", bq25798.getInt(bq25798.EN_CHG));
  Serial.printf(", EN_OTG: %d", bq25798.getInt(bq25798.EN_OTG));
  Serial.printf(", EN_ICO: %d", bq25798.getInt(bq25798.EN_ICO));
  Serial.printf(", EN_TERM: %d", bq25798.getInt(bq25798.EN_TERM));
  Serial.printf(", EN_HIZ: %d", bq25798.getInt(bq25798.EN_HIZ));
  Serial.println();
  Serial.printf("\tCHG_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.CHG_STAT), bq25798.CHG_STAT_strings));
  Serial.printf("\tVBUS_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.VBUS_STAT), bq25798.VBUS_STAT_strings));
  Serial.printf("\tBKUP_ACFET1_ON: %s\n", bq25798.toString(bq25798.getInt(bq25798.BKUP_ACFET1_ON), bq25798.BKUP_ACFET1_ON_strings));

  Serial.println();
  if (bq25798.getInt(bq25798.DIS_ACDRV)) {
    Serial.println("ACDRV: disabled (both AC1 and AC2)");
  } else {
    // Serial.println("ACDRV: enabled");
    if (bq25798.getInt(bq25798.EN_ACDRV1)) {
      Serial.println("AC1: enabled");
      Serial.printf("\tAC1_PRESENT_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.AC1_PRESENT_STAT), bq25798.AC1_PRESENT_STAT_strings));
      Serial.printf("\tVAC1: %5.3f V\n", bq25798.getInt(bq25798.VAC1_ADC) / 1000.0);
      Serial.printf("\tEN_ACDRV1: %d\n", bq25798.getInt(bq25798.EN_ACDRV1));
    } else {
      Serial.println("AC1: disabled");
    }
    if (bq25798.getInt(bq25798.EN_ACDRV2)) {
      Serial.println("AC2: enabled");
      Serial.printf("\tAC2_PRESENT_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.AC2_PRESENT_STAT), bq25798.AC2_PRESENT_STAT_strings));
      Serial.printf("\tVAC2: %5.3f V\n", bq25798.getInt(bq25798.VAC2_ADC) / 1000.0);
      Serial.printf("\tEN_ACDRV2: %d\n", bq25798.getInt(bq25798.EN_ACDRV2));
    } else {
      Serial.println("AC2: disabled");
    }
  };

  Serial.println();
  // REG1B_Charger_Status_0
  Serial.printf("IINDPM_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.IINDPM_STAT), bq25798.IINDPM_STAT_strings));
  Serial.printf("VINDPM_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.VINDPM_STAT), bq25798.VINDPM_STAT_strings));
  Serial.printf("WD_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.WD_STAT), bq25798.WD_STAT_strings));
  Serial.printf("PG_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.PG_STAT), bq25798.PG_STAT_strings));
  Serial.printf("AC2_PRESENT_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.AC2_PRESENT_STAT), bq25798.AC2_PRESENT_STAT_strings));
  Serial.printf("AC1_PRESENT_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.AC1_PRESENT_STAT), bq25798.AC1_PRESENT_STAT_strings));
  Serial.printf("VBUS_PRESENT_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.VBUS_PRESENT_STAT), bq25798.VBUS_PRESENT_STAT_strings));

  // REG1C_Charger_Status_1
  Serial.printf("CHG_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.CHG_STAT), bq25798.CHG_STAT_strings));
  Serial.printf("VBUS_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.VBUS_STAT), bq25798.VBUS_STAT_strings));
  Serial.printf("BC12_DONE_STAT: %s\n", bq25798.getInt(bq25798.BC12_DONE_STAT));

  // REG1D_Charger_Status_2
  Serial.printf("ICO_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.ICO_STAT), bq25798.ICO_STAT_strings));
  Serial.printf("TREG_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.TREG_STAT), bq25798.TREG_STAT_strings));
  Serial.printf("DPDM_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.DPDM_STAT), bq25798.DPDM_STAT_strings));
  Serial.printf("VBAT_PRESENT_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.VBAT_PRESENT_STAT), bq25798.VBAT_PRESENT_STAT_strings));

  // REG1E_Charger_Status_3
  Serial.printf("ACRB2_STAT: %s\n", bq25798.getInt(bq25798.ACRB2_STAT));
  Serial.printf("ACRB1_STAT: %s\n", bq25798.getInt(bq25798.ACRB1_STAT));
  Serial.printf("ADC_DONE_STAT: %s\n", bq25798.getInt(bq25798.ADC_DONE_STAT));
  Serial.printf("VSYS_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.VSYS_STAT), bq25798.VSYS_STAT_strings));
  Serial.printf("CHG_TMR_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.CHG_TMR_STAT), bq25798.CHG_TMR_STAT_strings));
  Serial.printf("TRICHG_TMR_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.TRICHG_TMR_STAT), bq25798.TRICHG_TMR_STAT_strings));
  Serial.printf("PRECHG_TMR_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.PRECHG_TMR_STAT), bq25798.PRECHG_TMR_STAT_strings));

  // REG1F_Charger_Status_4
  Serial.printf("VBATOTG_LOW_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.VBATOTG_LOW_STAT), bq25798.VBATOTG_LOW_STAT_strings));
  Serial.printf("TS_COLD_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.TS_COLD_STAT), bq25798.TS_COLD_STAT_strings));
  Serial.printf("TS_COOL_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.TS_COOL_STAT), bq25798.TS_COOL_STAT_strings));
  Serial.printf("TS_WARM_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.TS_WARM_STAT), bq25798.TS_WARM_STAT_strings));
  Serial.printf("TS_HOT_STAT: %s\n", bq25798.toString(bq25798.getInt(bq25798.TS_HOT_STAT), bq25798.TS_HOT_STAT_strings));

  Serial.println();
  Serial.printf("Fault detected: %s\n", bq25798.faultDetected() ? "YES" : "NO");
  if (bq25798.faultDetected()) {
    Serial.println("Fault stats:");
    Serial.printf("\tIBAT_REG_STAT: %d\n", bq25798.getInt(bq25798.IBAT_REG_STAT));
    Serial.printf("\tVBUS_OVP_STAT: %d\n", bq25798.getInt(bq25798.VBUS_OVP_STAT));
    Serial.printf("\tVBAT_OVP_STAT: %d\n", bq25798.getInt(bq25798.VBAT_OVP_STAT));
    Serial.printf("\tIBUS_OCP_STAT: %d\n", bq25798.getInt(bq25798.IBUS_OCP_STAT));
    Serial.printf("\tIBAT_OCP_STAT: %d\n", bq25798.getInt(bq25798.IBAT_OCP_STAT));
    Serial.printf("\tCONV_OCP_STAT: %d\n", bq25798.getInt(bq25798.CONV_OCP_STAT));
    Serial.printf("\tVAC2_OVP_STAT: %d\n", bq25798.getInt(bq25798.VAC2_OVP_STAT));
    Serial.printf("\tVAC1_OVP_STAT: %d\n", bq25798.getInt(bq25798.VAC1_OVP_STAT));
    Serial.printf("\tVSYS_SHORT_STAT: %d\n", bq25798.getInt(bq25798.VSYS_SHORT_STAT));
    Serial.printf("\tVSYS_OVP_STAT: %d\n", bq25798.getInt(bq25798.VSYS_OVP_STAT));
    Serial.printf("\tOTG_OVP_STAT: %d\n", bq25798.getInt(bq25798.OTG_OVP_STAT));
    Serial.printf("\tOTG_UVP_STAT: %d\n", bq25798.getInt(bq25798.OTG_UVP_STAT));
    Serial.printf("\tTSHUT_STAT: %d\n", bq25798.getInt(bq25798.TSHUT_STAT));

    Serial.println("Fault flags:");
    Serial.printf("\tIBAT_REG_FLAG: %d\n", bq25798.getInt(bq25798.IBAT_REG_FLAG));
    Serial.printf("\tVBUS_OVP_FLAG: %d\n", bq25798.getInt(bq25798.VBUS_OVP_FLAG));
    Serial.printf("\tVBAT_OVP_FLAG: %d\n", bq25798.getInt(bq25798.VBAT_OVP_FLAG));
    Serial.printf("\tIBUS_OCP_FLAG: %d\n", bq25798.getInt(bq25798.IBUS_OCP_FLAG));
    Serial.printf("\tIBAT_OCP_FLAG: %d\n", bq25798.getInt(bq25798.IBAT_OCP_FLAG));
    Serial.printf("\tCONV_OCP_FLAG: %d\n", bq25798.getInt(bq25798.CONV_OCP_FLAG));
    Serial.printf("\tVAC2_OVP_FLAG: %d\n", bq25798.getInt(bq25798.VAC2_OVP_FLAG));
    Serial.printf("\tVAC1_OVP_FLAG: %d\n", bq25798.getInt(bq25798.VAC1_OVP_FLAG));
    Serial.printf("\tVSYS_SHORT_FLAG: %d\n", bq25798.getInt(bq25798.VSYS_SHORT_FLAG));
    Serial.printf("\tVSYS_OVP_FLAG: %d\n", bq25798.getInt(bq25798.VSYS_OVP_FLAG));
    Serial.printf("\tOTG_OVP_FLAG: %d\n", bq25798.getInt(bq25798.OTG_OVP_FLAG));
    Serial.printf("\tOTG_UVP_FLAG: %d\n", bq25798.getInt(bq25798.OTG_UVP_FLAG));
    Serial.printf("\tTSHUT_FLAG: %d\n", bq25798.getInt(bq25798.TSHUT_FLAG));
  };

  // Serial.println();
  // Serial.printf("PN=%d (%s), DEV_REV=%d (%s)\n", bq25798.getInt(bq25798.PN), bq25798.toString(bq25798.getInt(bq25798.PN), bq25798.PN_strings),
  //               bq25798.getInt(bq25798.DEV_REV), bq25798.toString(bq25798.getInt(bq25798.DEV_REV), bq25798.DEV_REV_strings));

  Serial.println("====================================================");
}

void patWatchdog() {
  // 9.4.1:
  // To keep the device in host mode, the host has
  // to reset the watchdog timer by writing 1 to WD_RST bit before the watchdog timer expires (WD_STAT bit is set),
  // or disable watchdog timer by setting WATCHDOG bits = 00
  bq25798.setInt(bq25798.WD_RST, 1);
}

void enableADC() {
  bq25798.setInt(bq25798.ADC_EN, 1);
  // Not needed, these are default values
  bq25798.setInt(bq25798.ADC_RATE, static_cast<int>(BQ25798::adc_rate_t::ADC_RATE_CONTINUOUS));
  bq25798.setInt(bq25798.ADC_SAMPLE, static_cast<int>(BQ25798::adc_sample_t::ADC_SAMPLE_15BIT));
  bq25798.setInt(bq25798.ADC_AVG, static_cast<int>(BQ25798::adc_avg_t::NO_AVERAGING));
}

void enableWatchdog() {
  bq25798.setInt(bq25798.WATCHDOG, static_cast<int>(BQ25798::watchdog_t::WATCHDOG_20S));
  bq25798.setInt(bq25798.WD_STAT, 0);  // Clear the watchdog status
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

  Serial.println("Resetting BQ25798...");
  bq25798.setInt(bq25798.REG_RST, 1);  // Reset the device
  delay(200);                          // Wait for the device to reset
  while (bq25798.getInt(bq25798.REG_RST) == 1) {
    bq25798.readAll();
    delay(100);
  }
  Serial.println("BQ25798 reset successful.");

  // VAC1 = direct VIN (wall charger output)
  // VAC2 = VBUS (=either VAC1 or 0V if wall charger not connected)

  bq25798.setInt(bq25798.VSYSMIN, 12000);  // Set minimal system voltage to 12V
  // bq25798.setInt(bq25798.VREG, 16800);     // Set battery voltage regulation limit to 16.8V (4S Li-ion)
  bq25798.setInt(bq25798.ICHG, 500);      // Set charge current limit to 0.5A
  bq25798.setInt(bq25798.VINDPM, 11500);  // Set input voltage limit to 11.5V
  bq25798.setInt(bq25798.IINDPM, 3000);   // Set input current limit to 3A
  bq25798.setInt(bq25798.VBAT_LOWV,
                 static_cast<int>(BQ25798::vbat_lowv_t::PCT_71));  // Set battery low voltage to 71.4% of VREG (for single 4.2V cell it would be 2.99V)
  bq25798.setInt(bq25798.VOTG, 11800);                             // Set OTG voltage to 11.8V
  bq25798.setInt(bq25798.IOTG, 3000);                              // Set OTG current limit to 3A

  bq25798.setInt(bq25798.EN_CHG, 1);     // Enable charging
  bq25798.setInt(bq25798.EN_ICO, 1);     // Enable ICO (Input Current Optimization)
  bq25798.setInt(bq25798.EN_TERM, 1);    // Enable termination
  bq25798.setInt(bq25798.EN_HIZ, 0);     // Disable high impedance mode
  bq25798.setInt(bq25798.EN_BACKUP, 1);  // Enable backup mode

  // When to trigger backup mode:
  bq25798.setInt(bq25798.VBUS_BACKUP,
                 static_cast<int>(BQ25798::vbus_backup_t::PCT_VBUS_BACKUP_100));  // Set VBUS backup to 100% of VINDPM

  enableADC();
  // enableWatchdog();
}

void loop() {
  DumpBQ25798();

  if (bq25798.getInt(bq25798.EN_OTG)) {
    Serial.println("OTG enabled, probably in backup mode, enabling backup mode again");
    // See page 37

    // 1.
    bq25798.setInt(bq25798.BKUP_ACFET1_ON, 1);  // Enable ACFET1 in backup mode

    //     Setting BKUP_ACFET1 _ON = 1 will cause the
    // device to set DIS_ACDRV = 0 and EN_ACDRV1 = 1. After that, backup mode is disabled, however, the
    // charger remains in the normal OTG mode. The ACFET1-RBFET1 is turned on to connect the adapter to
    // VBUS.
    // ❗❗❗The user must ensure the adapter voltage is equal to or higher than the charger VOTG voltage
    // setting, otherwise, the charger OTG output might back drive the adapter connected to VBUS.

    // 2. Determine the source at ACIN1 is valid (is not in overvoltage and did not fail poor source detection) by
    // reading back EN_ACDRV1 as 1.
    int en_acdrv1 = bq25798.getInt(bq25798.EN_ACDRV1);
    Serial.printf("EN_ACDRV1: %d\n", en_acdrv1);
    if (en_acdrv1) {
      Serial.println("EN_ACDRV1 is 1, enabling backup mode again");
      // 3. Set EN_OTG = 0, in order to exit OTG mode and enter the forward charging mode without PMID voltage
      // crash. Setting BKUP_ACFET1_ON = 1, also clears BKUP_ACFET1_ON to 0 and sets EN_BACKUP to 1
      bq25798.setInt(bq25798.EN_OTG, 0);
    }
  }

  patWatchdog();
  delay(10000);
}
