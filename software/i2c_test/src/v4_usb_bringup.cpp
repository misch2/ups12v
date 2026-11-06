#include <Arduino.h>
#include <esp_chip_info.h>
#include <esp_system.h>

#if !CONFIG_IDF_TARGET_ESP32C3 || ARDUINO_USB_MODE != 1 || ARDUINO_USB_CDC_ON_BOOT != 1
  #error "Requires ESP32-C3 native USB Serial/JTAG"
#endif

namespace {
constexpr char kVersion[] = "ups-v4-usb-bringup/0.1.0";
uint32_t lastHeartbeat = 0;
uint32_t heartbeat = 0;

const char* resetName(esp_reset_reason_t reason) {
  switch (reason) {
    case ESP_RST_POWERON:
      return "POWERON";
    case ESP_RST_EXT:
      return "EXT";
    case ESP_RST_SW:
      return "SW";
    case ESP_RST_PANIC:
      return "PANIC";
    case ESP_RST_INT_WDT:
      return "INT_WDT";
    case ESP_RST_TASK_WDT:
      return "TASK_WDT";
    case ESP_RST_WDT:
      return "WDT";
    case ESP_RST_DEEPSLEEP:
      return "DEEPSLEEP";
    case ESP_RST_BROWNOUT:
      return "BROWNOUT";
    default:
      return "OTHER";
  }
}

void printInfo() {
  esp_chip_info_t chip;
  esp_chip_info(&chip);
  const esp_reset_reason_t reason = esp_reset_reason();
  Serial.printf("\nFirmware: %s\n", kVersion);
  Serial.printf("Chip: %s revision=%u cores=%u\n", ESP.getChipModel(), chip.revision, chip.cores);
  Serial.printf("CPU: %lu MHz; flash: %lu bytes\n", static_cast<unsigned long>(ESP.getCpuFreqMHz()), static_cast<unsigned long>(ESP.getFlashChipSize()));
  Serial.printf("Reset: %s (%d)\n", resetName(reason), static_cast<int>(reason));
  Serial.println("USB Serial/JTAG; no Wi-Fi/BT, GPIO, I2C or charger initialization");
}
}  // namespace

void setup() {
  Serial.begin(115200);
  Serial.setTxTimeoutMs(10);
  // No wait for a monitor, GPIO/LED setup or UPS libraries.
  printInfo();
}

void loop() {
  const uint32_t now = millis();
  if (now - lastHeartbeat >= 1000) {
    lastHeartbeat = now;
    ++heartbeat;
    if (heartbeat % 10 == 0) printInfo();  // Identification for late-opened monitors.
    Serial.printf("uptime_ms=%lu free_heap=%lu heartbeat=%lu\n", static_cast<unsigned long>(now), static_cast<unsigned long>(ESP.getFreeHeap()),
                  static_cast<unsigned long>(heartbeat));
  }
  delay(10);
}
