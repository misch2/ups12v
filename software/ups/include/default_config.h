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
    .network =
        {
            //
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
    .power =
        {
            //
            .backupMode = Config::Power::BackupMode::PMID_WITH_SWITCHOVER,
            .input =
                {
                    //
                    .IINDPM_mA = 500,
                    .VINDPM_mV = 5000,
                    .VBUSBackupPercentage = BQ25798::VBUS_BACKUP_t::PCT_VBUS_BACKUP_80
                    //
                },
            .charger =
                {
                    //
                    .minCellVoltage_mV = 3200,
                    .maxCellVoltage_mV = 4200,
                    .vbatChgEnableIfCellBelow_mV = 99999,   // always enabled
                    .vbatChgDisableIfCellAbove_mV = 99999,  // never disabled
                    .ICHG_mA = 1000
                    //
                },
            .output =
                {
                    //
                    .IOTG_mA = 500,
                    .VOTG_mV = 5000
                    //
                }
            //
        },
    .ACRecoveryPeriodSeconds = 30  // time to wait for AC to be present and stable
                                   //
};
