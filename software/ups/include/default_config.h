#pragma once

#include "config.h"

// Default configuration with common values shared across all boards
// Board-specific configurations can override these values
Config default_config = {
    //
    .HW_VERSION = "1.0",
    .pins =
        {
            //
            .I2C_SDA = 21,
            .I2C_SCL = 22,
            .LED = 2
            //
        },
    .syslog =
        {
            //
            .serverHostname = "",
            .serverPort = 514,
            .myHostname = "host",
            .myAppname = "ups"
            //
        },
    .mqtt =
        {
            //
            .serverHostname = "",
            .serverPort = 1883,
            .user = "",
            .password = "",
            .haDeviceName = "ups"
            //
        },
    .charger =
        {
            //
            .vbatChgEnableIfCellBelow_mV = 4100,
            .vbatChgDisableIfCellAbove_mV = 4155,
            .ichg_mA = 1000
            //
        },
    .temperatureSensor =
        {
            //
            .R_vregn = 5600,
            .R_gnd = 33000,
            .resistance_25degC = 10000.0,
            .beta = 3435.0
            //
        },
    .AC_RECOVERY_PERIOD_SECONDS = 30,  // time to wait for AC to be present and stable
    .VBUS_BACKUP_PERCENTAGE = BQ25798::VBUS_BACKUP_t::PCT_VBUS_BACKUP_80
    //
};
