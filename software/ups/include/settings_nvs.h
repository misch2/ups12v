#pragma once

#include "settings_store.h"

namespace Settings {
// Uses the already initialized Arduino NVS partition; never initializes, clears or erases it.
class NvsBackend : public Backend {
 public:
  // Key must outlive this backend (production callers use string literals).
  explicit NvsBackend(const char* key = "config") : key(key) {}
  Result read(std::string& output) override;
  Result write(const std::string& record) override;
 private:
  const char* key;
};
}  // namespace Settings
