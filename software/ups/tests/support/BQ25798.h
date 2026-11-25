#pragma once

#include <cstdint>

// RuntimeSettings only needs this enum. Values match BQ25798's generated definition.
class BQ25798 {
 public:
  enum class VBUS_BACKUP_t : uint8_t { PCT_VBUS_BACKUP_40 = 0, PCT_VBUS_BACKUP_60 = 1, PCT_VBUS_BACKUP_80 = 2, PCT_VBUS_BACKUP_100 = 3 };
};
