#pragma once

#include "settings_store.h"

namespace Settings {
// Uses the already initialized Arduino NVS partition; never initializes, clears or erases it.
class NvsBackend : public Backend {
 public:
  Result read(std::string& output) override;
  Result write(const std::string& record) override;
};
}  // namespace Settings
