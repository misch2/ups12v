#pragma once
#include <cstdint>
using BaseType_t = int;
using TickType_t = uint32_t;
constexpr BaseType_t pdTRUE = 1;
constexpr BaseType_t pdPASS = 1;
constexpr TickType_t portMAX_DELAY = UINT32_MAX;
