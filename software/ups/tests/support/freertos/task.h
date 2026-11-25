#pragma once
#include "FreeRTOS.h"
using TaskFunction_t = void (*)(void*);
BaseType_t xTaskCreate(TaskFunction_t function, const char* name, uint32_t stackBytes, void* context, unsigned priority, void* handle);
void vTaskDelay(TickType_t ticks);
