#include <Arduino.h>
#include <Wire.h>

#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22

#define I2C_ADDR 0x6B  // BQ25798

#include "bq25798/bq25798.h"

BQ25798 bq25798 = BQ25798();

void ScanI2C() {
  byte error, address;
  int nDevices;

  Serial.println("Scanning...");

  nDevices = 0;
  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
    if (error == 0) {
      Serial.print("I2C device found at address 0x");
      if (address < 16) {
        Serial.print("0");
      }
      Serial.print(address, HEX);
      Serial.println("  !");
      nDevices++;
    } else if (error == 4) {
      Serial.print("Unknown error at address 0x");
      if (address < 16) {
        Serial.print("0");
      }
      Serial.println(address, HEX);
    }
  }
  if (nDevices == 0) {
    Serial.println("No I2C devices found\n");
  } else {
    Serial.println("done\n");
  }
}

uint8_t I2CReadByte(uint8_t reg) {
  Wire.beginTransmission(I2C_ADDR);
  Wire.write(reg);
  Wire.endTransmission();
  Wire.requestFrom(I2C_ADDR, 1);
  return Wire.read();
}

void I2CWriteByte(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(I2C_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

uint16_t I2CReadWordMSBFirst(uint8_t reg) {
  Wire.beginTransmission(I2C_ADDR);
  Wire.write(reg);
  Wire.endTransmission();
  Wire.requestFrom(I2C_ADDR, 2);
  uint16_t val = Wire.read();
  val <<= 8;
  val |= Wire.read();
  return val;
}

uint16_t I2CReadWordLSBFirst(uint8_t reg) {
  Wire.beginTransmission(I2C_ADDR);
  Wire.write(reg);
  Wire.endTransmission();
  Wire.requestFrom(I2C_ADDR, 2);
  uint16_t val = Wire.read();
  val |= (int)(Wire.read()) << 8;
  return val;
}

void DumpBQ25798() {
  Serial.println("Dumping BQ25798 registers:");

  bq25798.readAll();

  Serial.printf("VSYSMIN: %5dmV\n", bq25798.getVSYSMIN());
  Serial.printf("VREG: %5d mV\n", bq25798.getVREG());
  Serial.printf("ICHG: %5d mA\n", bq25798.getICHG());
  Serial.printf("VINDPM: %5d mV\n", bq25798.getVINDPM());
  Serial.printf("IINDPM: %5d mA\n", bq25798.getIINDPM());

  Serial.println();
  Serial.printf("VBAT_LOWV: %5d\n", bq25798.getVBAT_LOWV());
  Serial.printf("IPRECHG: %5d mA\n", bq25798.getIPRECHG());

  Serial.println();
  Serial.println("ADCs:");
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
  Serial.printf("PN=%d [3=BQ25798], DEV_REV=%d [1=BQ25798]\n", bq25798.getPN(),
                bq25798.getDEV_REV());

  uint8_t byte = I2CReadByte(0x1B);
  Serial.printf(
      "REG1B_Charger_Status_0: \n\tIINDPM_STAT=%s, \n\tVINDPM_STAT=%s, "
      "\n\tWD_STAT=%s, \n\tPG_STAT=%s, \n\tAC2_PRESENT_STAT=%s, "
      "\n\tAC1_PRESENT_STAT=%s, \n\tVBUS_PRESENT_STAT=%s\n",
      (byte & 0x80) ? "In IINDPM regulation or IOTG regulation" : "Normal",
      (byte & 0x40) ? "In VINDPM regulation or VOTG regulation" : "Normal",
      (byte & 0x20) ? "Watchdog timer expired" : "Normal",
      (byte & 0x08) ? "Power good" : "NOT in power good status",
      (byte & 0x04) ? "VAC2 present" : "VAC2 not present",
      (byte & 0x02) ? "VAC1 present" : "VAC1 not present",
      (byte & 0x01) ? "VBUS present" : "VBUS not present");

  byte = I2CReadByte(0x1C);
  Serial.println("REG1C_Charger_Status_1:");
  Serial.print("\tCharge status: ");
  switch ((byte & 0xe0) >> 5) {
    case 0:
      Serial.println("Not Charging");
      break;
    case 1:
      Serial.println("Trickle Charge");
      break;
    case 2:
      Serial.println("Pre-charge");
      break;
    case 3:
      Serial.println("Fast charge (CC mode)");
      break;
    case 4:
      Serial.println("Taper Charge (CV mode)");
      break;
    case 5:
      Serial.println("Reserved");
      break;
    case 6:
      Serial.println("Top-off Timer Active Charging");
      break;
    case 7:
      Serial.println("Charge Termination Done");
      break;
  };
  Serial.print("\tVBUS status: ");
  switch ((byte & 0x1e) >> 1) {
    case 0:
      Serial.println("No Input or BHOT or BCOLD in OTG mode");
      break;
    case 1:
      Serial.println("USB SDP (500mA)");
      break;
    case 2:
      Serial.println("USB CDP (1.5A)");
      break;
    case 3:
      Serial.println("USB DCP (3.25A)");
      break;
    case 4:
      Serial.println("Adjustable High Voltage DCP (HVDCP) (1.5A)");
      break;
    case 5:
      Serial.println("Unknown adaptor (3A)");
      break;
    case 6:
      Serial.println("Non-Standard Adapter (1A/2A/2.1A/2.4A)");
      break;
    case 7:
      Serial.println("In OTG mode");
      break;
    case 8:
      Serial.println("Not qualified adaptor");
      break;
    case 9:
      Serial.println("Reserved");
      break;
    case 0xA:
      Serial.println("Reserved");
      break;
    case 0xB:
      Serial.println("Device directly powered from VBUS");
      break;
    case 0xC:
      Serial.println("Backup Mode");
      break;
    case 0xD:
      Serial.println("Reserved");
      break;
    case 0xE:
      Serial.println("Reserved");
      break;
    case 0xF:
      Serial.println("Reserved");
      break;
  };
  Serial.printf("\tBC1.2_DONE_STAT=%s\n",
                (byte & 0x01) ? "BC1.2 or non-standard detection complete"
                              : "BC1.2 or non-standard detection NOT complete");
}

void resetWatchdog() {
  uint8_t byte = I2CReadByte(0x10);
  byte |= 0x08;   // set WD_RST bit
  byte &= ~0x07;  // clear WATCHDOG timer
  I2CWriteByte(0x10, byte);
}

void enableADC() {
  uint8_t byte = I2CReadByte(0x2E);
  byte |= 0x80;   // set ADC_EN bit
  byte &= ~0x40;  // clear ADC_RATE bit
  byte &= ~0x30;  // clear ADC_SAMPLE bits
  byte &= ~0x08;  // clear ADC_AVG bit
  I2CWriteByte(0x2E, byte);
}

void setup() {
  Serial.begin(115200);
  Serial.println("Serial port initialized");
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Serial.printf("I2C initialized on SDA=GPIO%d, SCL=GPIO%d\n", I2C_SDA_PIN,
                I2C_SCL_PIN);

  ScanI2C();
  resetWatchdog();
  enableADC();
}

void loop() {
  DumpBQ25798();
  resetWatchdog();
  delay(10000);
}
