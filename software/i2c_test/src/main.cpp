#include <Arduino.h>
#include <Wire.h>
#include <BQ25798.h>

#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22

BQ25798 bq25798 = BQ25798();

void DumpBQ25798() {
  Serial.println("Dumping BQ25798 registers:");

  bq25798.readAll();

  Serial.printf("VSYSMIN: %5dmV\n", bq25798.getVSYSMIN());
  Serial.printf("VREG: %5d mV\n", bq25798.getVREG());
  Serial.printf("ICHG: %5d mA\n", bq25798.getICHG());
  Serial.printf("VINDPM: %5d mV\n", bq25798.getVINDPM());
  Serial.printf("IINDPM: %5d mA\n", bq25798.getIINDPM());

  Serial.println();
  Serial.printf("VBAT_LOWV: %s\n", bq25798.getVBAT_LOWVStr());
  Serial.printf("IPRECHG: %5d mA\n", bq25798.getIPRECHG());
  Serial.printf("TRECHG: %s\n", bq25798.getTRECHGStr());
  Serial.printf("PRECHG_TMR: %s\n", bq25798.getPRECHG_TMRStr());
  Serial.printf("CELL: %s\n", bq25798.getCELLStr());


  Serial.println();
  Serial.println("ADCs:");
  Serial.printf("\tADC_RATE: %s\n", bq25798.getADC_RATEStr());
  Serial.printf("\tADC_SAMPLE: %s\n", bq25798.getADC_SAMPLEStr());
  Serial.printf("\tADC_AVG: %d\n", bq25798.ADC_AVG());
  Serial.printf("\tADC_AVG_INIT: %d\n", bq25798.ADC_AVG_INIT());

  Serial.printf("\tIBUS: %5d mA * %5d mV = %.3f mW\n", bq25798.getIBUS_ADC(),
                bq25798.getVBUS_ADC(),
                bq25798.getIBUS_ADC() * bq25798.getVBUS_ADC() / 1000.0);
  Serial.printf("\tIBAT: %5d mA * %5d mV = %.3f mW\n", bq25798.getIBAT_ADC(),
                bq25798.getVBAT_ADC(),
                bq25798.getIBAT_ADC() * bq25798.getVBAT_ADC() / 1000.0);
  Serial.printf("\tVSYS: %5d mV\n", bq25798.getVSYS_ADC());
  Serial.printf("\tTS: %5d %%\n", bq25798.getTS_ADC());
  Serial.printf("\tTDIE: %5d degC\n", bq25798.getTDIE_ADC());
  Serial.printf("\tDPLUS / DMINUS: %4d mV / %4d mV\n", bq25798.getDPLUS_ADC(),
                bq25798.getDMINUS_ADC());

  Serial.println();
  Serial.printf("PN=%d (%s), DEV_REV=%d (%s)\n", bq25798.getPN(),
                bq25798.getPNStr(), bq25798.getDEV_REV(),
                bq25798.getDEV_REVStr());
}

void resetWatchdog() {
  // FIXME
  // bq25798.setWD_RST(1);
  // bq25798.set(WDT_RST, 1);
}

void enableADC() {
  // FIXME
  // bq25798.set(ADC_ENABLE, 1);
}

void setup() {
  Serial.begin(115200);
  Serial.println("Serial port initialized");
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Serial.printf("I2C initialized on SDA=GPIO%d, SCL=GPIO%d\n", I2C_SDA_PIN,
                I2C_SCL_PIN);
  if (!bq25798.begin()) {
    Serial.println("Failed to initialize BQ25798, stopping here.");
    while (1) {
      delay(1000);
    }
  }

  resetWatchdog();
  enableADC();
}

void loop() {
  DumpBQ25798();
  resetWatchdog();
  delay(10000);
}
