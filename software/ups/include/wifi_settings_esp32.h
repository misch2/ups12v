#pragma once

#include "wifi_settings.h"

namespace Settings {
class Esp32WifiDriver : public WifiDriver {
 public:
  Result read(WifiCredentials& credentials) override;
  Result write(const WifiCredentials& credentials) override;
  Result clear() override;
};
}  // namespace Settings
