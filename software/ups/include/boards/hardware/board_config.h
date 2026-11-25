#pragma once

#include "hardware_profile.h"
#include "runtime_settings.h"

// Shared binaries contain no installed-device presets, identifiers or credentials.
#if defined(UPS_HW_V1)
constexpr Hardware::Profile hardware = Hardware::kV1Esp32;
#elif defined(UPS_HW_V3)
constexpr Hardware::Profile hardware = Hardware::kV3SysEsp32;
#elif defined(UPS_HW_V4)
constexpr Hardware::Profile hardware = Hardware::kV4Esp32C3;
#else
  #error "Select one hardware version for the firmware image"
#endif

RuntimeSettings config;
