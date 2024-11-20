#include "bq25798.h"
#include <Wire.h>

BQ25798::BQ25798() {
  for (int i = 0; i < registersCount; i++) {
    _regs[i + MIN_REGISTER_NUMBER] = 0;
  }
}

void BQ25798::readAll() {
  Wire.beginTransmission(I2C_ADDR);
  Wire.write(MIN_REGISTER_NUMBER);
  Wire.endTransmission();
  Wire.requestFrom(I2C_ADDR, registersCount);

  for (int i = 0; i < registersCount; i++) {
    _regs[i + MIN_REGISTER_NUMBER] = Wire.read();
  }
}

void BQ25798::writeByte(int reg) {
  Wire.beginTransmission(I2C_ADDR);
  Wire.write(reg);
  Wire.write(_regs[reg]);
  Wire.endTransmission();
}

void BQ25798::writeWord(int reg) {
  Wire.beginTransmission(I2C_ADDR);
  Wire.write(reg);
  Wire.write(_regs[reg]);
  Wire.write(_regs[reg + 1]);
  Wire.endTransmission();
}

uint8_t BQ25798::getreg8(int reg, int bitMask, int bitShift) {
  return (_regs[reg] >> bitShift) & bitMask;
}

void BQ25798::setreg8(int reg, uint8_t value, int bitMask, int bitShift) {
  uint8_t shiftedMask = bitMask << bitShift;
  uint8_t shiftedValue = (value & bitMask) << bitShift;

  _regs[reg] &= shiftedMask;
  _regs[reg] |= (shiftedValue & shiftedMask);
}

uint16_t BQ25798::getreg16(int widereg, int bitMask, int bitShift) {
  return ((_regs[widereg] << 8) | _regs[widereg + 1]) >> bitShift & bitMask;
}

void BQ25798::setreg16(int widereg, uint16_t value, int bitMask, int bitShift) {
  uint16_t shiftedMask = bitMask << bitShift;
  uint16_t shiftedValue = (value & bitMask) << bitShift;

  _regs[widereg] &= shiftedMask >> 8;
  _regs[widereg + 1] &= shiftedMask & 0xFF;
  _regs[widereg] |= (shiftedValue & shiftedMask) >> 8;
  _regs[widereg + 1] |= (shiftedValue & shiftedMask) & 0xFF;
}

//
// REG00_Minimal_System_Voltage
//
int BQ25798::getVSYSMIN() {
  return getreg8(REG00_Minimal_System_Voltage, 0x3F, 0);
};
void BQ25798::setVSYSMIN(int value) {
  setreg8(REG00_Minimal_System_Voltage, value, 0x3F, 0);
  writeByte(REG00_Minimal_System_Voltage);
}

//
// REG01_Charge_Voltage_Limit
//
int BQ25798::getVREG() {
  return getreg16(REG01_Charge_Voltage_Limit, 0x7FF, 0);
}
void BQ25798::setVREG(int value) {
  setreg16(REG01_Charge_Voltage_Limit, value, 0x7FF, 0);
  writeWord(REG01_Charge_Voltage_Limit);
}

//
// REG03_Charge_Current_Limit
//
int BQ25798::getICHG() {
  return getreg16(REG03_Charge_Current_Limit, 0x1FF, 0);
}
void BQ25798::setICHG(int value) {
  setreg16(REG03_Charge_Current_Limit, value, 0x1FF, 0);
  writeWord(REG03_Charge_Current_Limit);
}

//
// REG05_Input_Voltage_Limit
//
int BQ25798::getVINDPM() {
  return getreg8(REG05_Input_Voltage_Limit, 0xFF, 0);
}
void BQ25798::setVINDPM(int value) {
  setreg8(REG05_Input_Voltage_Limit, value, 0xFF, 0);
  writeByte(REG05_Input_Voltage_Limit);
}

//
// REG06_Input_Current_Limit
//
int BQ25798::getIINDPM() {
  return getreg16(REG06_Input_Current_Limit, 0x1FF, 0);
}
void BQ25798::setIINDPM(int value) {
  setreg16(REG06_Input_Current_Limit, value, 0x1FF, 0);
  writeWord(REG06_Input_Current_Limit);
}

//
// REG08_Precharge_Control
//
int BQ25798::getVBAT_LOWV() {
  return getreg8(REG08_Precharge_Control, 0x3, 6);
}
void BQ25798::setVBAT_LOWV(int value) {
  setreg8(REG08_Precharge_Control, value, 0x3, 6);
  writeByte(REG08_Precharge_Control);
}

int BQ25798::getIPRECHG() {
  return getreg8(REG08_Precharge_Control, 0x3F, 0);
}
void BQ25798::setIPRECHG(int value) {
  setreg8(REG08_Precharge_Control, value, 0x3F, 0);
  writeByte(REG08_Precharge_Control);
}

//
// REG09_Termination_Control
//
int BQ25798::getREG_RST() {
  return getreg8(REG09_Termination_Control, 0x01, 6);
}
void BQ25798::setREG_RST(int value) {
  setreg8(REG09_Termination_Control, value, 0x01, 6);
  writeByte(REG09_Termination_Control);
}

int BQ25798::getSTOP_WD_CHG() {
  return getreg8(REG09_Termination_Control, 0x01, 5);
}
void BQ25798::setSTOP_WD_CHG(int value) {
  setreg8(REG09_Termination_Control, value, 0x01, 5);
  writeByte(REG09_Termination_Control);
}

int BQ25798::getITERM() {
  return getreg8(REG09_Termination_Control, 0x1F, 0);
}
void BQ25798::setITERM(int value) {
  setreg8(REG09_Termination_Control, value, 0x1F, 0);
  writeByte(REG09_Termination_Control);
}

//
// REG0A_Recharge_Control
//
int BQ25798::getCELL() {
  return getreg8(REG0A_Recharge_Control, 0x03, 6);
}
void BQ25798::setCELL(int value) {
  setreg8(REG0A_Recharge_Control, value, 0x03, 6);
  writeByte(REG0A_Recharge_Control);
}
int BQ25798::getTRECHG() {
  return getreg8(REG0A_Recharge_Control, 0x03, 4);
}
void BQ25798::setTRECHG(int value) {
  setreg8(REG0A_Recharge_Control, value, 0x03, 4);
  writeByte(REG0A_Recharge_Control);
}
int BQ25798::getVRECHG() {
  return getreg8(REG0A_Recharge_Control, 0x0F, 0);
}
void BQ25798::setVRECHG(int value) {
  setreg8(REG0A_Recharge_Control, value, 0x0F, 0);
  writeByte(REG0A_Recharge_Control);
}

// ADCs
uint16_t BQ25798::getIBUS_ADC() {
  return getreg16(REG31_IBUS_ADC, 0xFFFF, 0);
}

uint16_t BQ25798::getIBAT_ADC() {
  return getreg16(REG33_IBAT_ADC, 0xFFFF, 0);
}

uint16_t BQ25798::getVBUS_ADC() {
  return getreg16(REG35_VBUS_ADC, 0xFFFF, 0);
}

uint16_t BQ25798::getVAC1_ADC() {
  return getreg16(REG37_VAC1_ADC, 0xFFFF, 0);
}

uint16_t BQ25798::getVAC2_ADC() {
  return getreg16(REG39_VAC2_ADC, 0xFFFF, 0);
}

uint16_t BQ25798::getVBAT_ADC() {
  return getreg16(REG3B_VBAT_ADC, 0xFFFF, 0);
}

uint16_t BQ25798::getVSYS_ADC() {
  return getreg16(REG3D_VSYS_ADC, 0xFFFF, 0);
}

uint16_t BQ25798::getTS_ADC() {
  return getreg16(REG3F_TS_ADC, 0xFFFF, 0);
}

uint16_t BQ25798::getTDIE_ADC() {
  return getreg16(REG41_TDIE_ADC, 0xFFFF, 0);
}

uint16_t BQ25798::getDPLUS_ADC() {
  return getreg16(REG43_DPLUS_ADC, 0xFFFF, 0);
}

uint16_t BQ25798::getDMINUS_ADC() {
  return getreg16(REG45_DMINUS_ADC, 0xFFFF, 0);
}

//
// REG47_DPDM_Driver
//
int BQ25798::getDPLUS_DAC() {
  return getreg8(REG47_DPDM_Driver, 0x07, 5);
}
void BQ25798::setDPLUS_DAC(int value) {
  setreg8(REG47_DPDM_Driver, value, 0x07, 5);
  writeByte(REG47_DPDM_Driver);
}
int BQ25798::getDMINUS_DAC() {
  return getreg8(REG47_DPDM_Driver, 0x07, 2);
}
void BQ25798::setDMINUS_DAC(int value) {
  setreg8(REG47_DPDM_Driver, value, 0x07, 2);
  writeByte(REG47_DPDM_Driver);
}

//
// REG48_Part_Information
//
int BQ25798::getPN() {
  return getreg8(REG48_Part_Information, 0x07, 3);
}
int BQ25798::getDEV_REV() {
  return getreg8(REG48_Part_Information, 0x07, 0);
}
