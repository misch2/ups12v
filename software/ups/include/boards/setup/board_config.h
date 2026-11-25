#pragma once

#include "hardware_profile.h"
#include "runtime_settings.h"

// Blank commissioning images contain no installed-device presets, identifiers or secrets.
#if defined(UPS_SETUP_V1)
constexpr Hardware::Profile hardware = Hardware::kV1Esp32;
#elif defined(UPS_SETUP_V3)
constexpr Hardware::Profile hardware = Hardware::kV3SysEsp32;
#elif defined(UPS_SETUP_V4)
constexpr Hardware::Profile hardware = Hardware::kV4Esp32C3;
#else
  #error "Select one hardware version for the setup image"
#endif

RuntimeSettings config;
