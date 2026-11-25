#pragma once
#include "FreeRTOS.h"
using QueueHandle_t = void*;
QueueHandle_t xQueueCreate(unsigned length, unsigned itemSize);
BaseType_t xQueueSend(QueueHandle_t queue, const void* value, TickType_t wait);
BaseType_t xQueueReceive(QueueHandle_t queue, void* value, TickType_t wait);
void vQueueDelete(QueueHandle_t queue);
