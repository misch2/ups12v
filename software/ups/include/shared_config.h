#include "config_structs.h"

namespace config {

// Battery temperature reporting + resistor divider network for the NTC sensor:
constexpr TemperatureSensor temperatureSensor{.R_vregn = 5600, .R_gnd = 33000, .resistance_25degC = 10000.0, .beta = 3435.0};

}  // namespace config