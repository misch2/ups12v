#pragma once

#include "recovery.h"

namespace Recovery {
class Esp32Driver : public Driver {
 public:
  std::string newPassword() override;
  bool start(const char* ssid, const char* password) override;
  bool stop() override;
};
}  // namespace Recovery
