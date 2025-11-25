// Example file

#include "config_structs.h"
#include <BQ25798.h>

#define BOARD_NAME "board01-test"
#define DEVICE_NAME "bq25798-ups1"
#define HOSTNAME BOARD_NAME "-" DEVICE_NAME

namespace config {
constexpr char HW_VERSION[] = "1.0";

constexpr Pins pins{.I2C_SDA = 21, .I2C_SCL = 22, .LED = 2};
constexpr Syslog syslog{.serverHostname = "logs.lan", .serverPort = 514, .myHostname = BOARD_NAME, .myAppname = DEVICE_NAME};
constexpr MQTT mqtt{.serverHostname = "mqtt.lan", .serverPort = 1883, .user = "mqtt_user", .password = "secret_password", .haDeviceName = HOSTNAME};

constexpr int AC_RECOVERY_PERIOD_SECONDS = 30;  // time to wait for AC to be present and stable before exiting backup mode

constexpr int VINDPM_mV = 12000;  // Input voltage DPM threshold in mV
constexpr int IINDPM_mA = 3000;   // Input current DPM threshold in mA

// The falling threshold to trigger the backup power mode.
// It is defined as a ratio of VINDPM. When VBUS is lower than this threshold,
// the charger turns to OTG mode to hold up VBUS voltage from dropping.
// (80 % of 12 V = 9.6 V, etc.);
constexpr BQ25798::VBUS_BACKUP_t VBUS_BACKUP_PERCENTAGE = BQ25798::VBUS_BACKUP_t::PCT_VBUS_BACKUP_80;

constexpr int VOTG_mV = 12000;  // Output voltage for OTG mode
constexpr int IOTG_mA = 3200;   // Output current for OTG mode in mA

constexpr Charger charger{.vbatChgEnableIfCellBelow_mV = 4150, .vbatChgDisableIfCellAbove_mV = 4155, .ichg_mA = 500};

}  // namespace config
