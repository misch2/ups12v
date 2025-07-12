// Example file

#include "config_structs.h"

#define HOSTNAME "ups1"

namespace config {

constexpr Pins pins{.I2C_SDA = 21, .I2C_SCL = 22, .LED = 2};
constexpr Syslog syslog{.serverHostname = "logs.lan", .serverPort = 514, .myHostname = HOSTNAME, .myAppname = "bq25798"};
constexpr MQTT mqtt{.serverHostname = "mqtt.lan", .serverPort = 1883, .user = "mqtt_user", .password = "secret_password", .haDeviceName = HOSTNAME};

constexpr int VINDPM_mV = 12000;  // Input voltage DPM threshold in mV
constexpr int IINDPM_mA = 3000;   // Input current DPM threshold in mA

constexpr int VOTG_mV = 12000;  // Output voltage for OTG mode
constexpr int IOTG_mA = 3200;   // Output current for OTG mode in mA

constexpr Charger charger{.vbatChgEnableIfCellBelow_mV = 4150, .vbatChgDisableIfCellAbove_mV = 4155, .ichg_mA = 500};

}  // namespace config
