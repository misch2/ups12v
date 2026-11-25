#pragma once
#include <cstdint>
struct esp_partition_t {
  uint32_t size;
  uint32_t address;
};
const esp_partition_t* esp_ota_get_next_update_partition(const esp_partition_t* partition);
const esp_partition_t* esp_ota_get_running_partition();
