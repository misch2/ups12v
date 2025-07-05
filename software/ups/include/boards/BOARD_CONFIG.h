// Example file

#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22
#define LED_PIN 2  // GPIO pin for the LED

#define HOSTNAME "ups1"

constexpr SyslogConfig syslogConfig{.serverHostname = "logs.lan", .serverPort = 514, .myHostname = HOSTNAME, .myAppname = "bq25798"};

#define MQTT_SERVER "mqtt.lan"
#define MQTT_PORT 1883
#define MQTT_USER "mqtt_user"
#define MQTT_PASSWORD "secret_password"
#define MQTT_HA_DEVICENAME HOSTNAME

#define VINDPM_mV 12000  // Input voltage DPM threshold in mV
#define IINDPM_mA 3000   // Input current DPM threshold in mA

#define VOTG_mV 12000  // Output voltage for OTG mode
#define IOTG_mA 3200   // Output current for OTG mode in mA

#define BATTERY_CELL_COUNT 4                 // Number of battery cells in series
#define VBAT_CHG_ENABLE_BELOW_CELL_mV 4150   // Lower voltage at which the charger is enabled in mV
#define VBAT_CHG_DISABLE_ABOVE_CELL_mV 4155  // Higher Voltage at which the charger is disabled in mV
#define ICHG_mA 500                          // Charge current in mA (max)

// Battery temperature reporting + resistor divider network for the NTC sensor:
constexpr TemperatureSensorConfig temperatureSensorConfig{.R_vregn = 5600, .R_gnd = 33000, .resistance_25degC = 10000.0, .beta = 3435.0};
