#include <cassert>
#include <iostream>

#include "homeassistant_mqtt.h"
#include "telemetry_policy.h"

unsigned long testMillis = 0;
Logger::Logger(Syslog*, Stream*) {}
void Logger::log(uint16_t, const char*, ...) {}

int main() {
  using namespace HomeAssistant;
  PubSubClient transport;
  Logger logger(nullptr, nullptr);
  MQTT mqtt(transport, logger, "host-test", "4.0");
  EntityBaseConfig base{};
  base.component = "sensor";
  base.config_key = base.state_key = "test";
  EntityConfig changeOnly(base);

  mqtt.publishStateIfNeeded(&changeOnly, "100");
  assert(transport.messages.size() == 1 && transport.messages.back().retained);
  testMillis = 600000;
  mqtt.publishStateIfNeeded(&changeOnly, "100");
  assert(transport.messages.size() == 1);  // No expiry/heartbeat for unchanged config.
  mqtt.publishStateIfNeeded(&changeOnly, "101");
  assert(transport.messages.size() == 2);  // Small changes are not suppressed.
  transport.failNext = true;
  mqtt.publishStateIfNeeded(&changeOnly, "102");
  assert(changeOnly.lastSentValue == "101");
  mqtt.publishStateIfNeeded(&changeOnly, "102");
  assert(changeOnly.lastSentValue == "102" && transport.messages.size() == 3);

  transport.online = false;
  mqtt.publishStateIfNeeded(&changeOnly, "103");
  assert(changeOnly.lastSentValue == "102");
  transport.online = true;
  mqtt.publishStateIfNeeded(&changeOnly, "103");
  assert(transport.messages.size() == 4);

  mqtt.publishConfiguration(&changeOnly);
  assert(transport.messages.back().fields.at("force_update") == "false");
  assert(transport.messages.back().fields.count("expire_after") == 0);
  assert(!changeOnly.hasSentState);
  mqtt.publishStateIfNeeded(&changeOnly, "103");
  assert(transport.messages.back().value == "103");  // Resend after discovery/reconnect.
  transport.failNext = true;
  mqtt.publishConfiguration(&changeOnly);
  assert(changeOnly.hasSentState);  // Failed config must not disturb delivery cache.

  EntityConfig periodic(base, 60000);
  periodic.suggestedDisplayPrecision = 0;
  mqtt.publishConfiguration(&periodic);
  const auto& fields = transport.messages.back().fields;
  assert(fields.at("force_update") == "true" && fields.at("expire_after") == "300");
  assert(fields.at("suggested_display_precision") == "0");
  mqtt.publishStateIfNeeded(&periodic, "50");
  const auto count = transport.messages.size();
  testMillis += 59999;
  mqtt.publishStateIfNeeded(&periodic, "50");
  assert(transport.messages.size() == count);
  testMillis++;
  transport.failNext = true;
  mqtt.publishStateIfNeeded(&periodic, "50");
  assert(transport.messages.size() == count);
  mqtt.publishStateIfNeeded(&periodic, "50");
  assert(transport.messages.size() == count + 1);  // Retry at fixed 60s, no jitter.

  testMillis = 0xfffffff0UL;
  mqtt.publishStateIfNeeded(&periodic, "51");
  const auto beforeWrap = transport.messages.size();
  testMillis += 60000UL;
  mqtt.publishStateIfNeeded(&periodic, "51");
  assert(transport.messages.size() == beforeWrap + 1);
  mqtt.publishStateIfNeeded(nullptr, "ignored");

  using Telemetry::Policy;
  assert(Telemetry::registerPolicy("VBAT_ADC") == Policy::Periodic);
  assert(Telemetry::registerPolicy("CHG_STAT") == Policy::Periodic);
  // Register-backed series used by the owner's Grafana dashboards must never require debug.
  for (const char* name : {"AC1_PRESENT_STAT", "CHG_STAT", "DIS_ACDRV", "EN_ACDRV1", "EN_BACKUP", "EN_CHG", "EN_OTG", "IBAT_ADC", "IBUS_ADC", "PG_STAT",
                           "TDIE_ADC", "TS_ADC", "VAC1_ADC", "VBAT_ADC", "VBUS_ADC", "VBUS_STAT", "VINDPM_STAT", "VSYS_ADC"}) {
    assert(Telemetry::registerPolicy(name) == Policy::Periodic);
  }
  assert(Telemetry::registerPolicy("VREG") == Policy::ChangeOnly);
  assert(Telemetry::registerPolicy("TS_HOT_STAT") == Policy::ChangeOnly);
  for (const char* name : {"EN_MPPT", "VOC_PCT", "VBAT_OVP_MASK", "VBAT_OVP_FLAG", "WD_RST", "UNKNOWN_FUTURE_SETTING"}) {
#ifdef DEBUG_BQ25798_SETTINGS
    assert(Telemetry::registerPolicy(name) == Policy::ChangeOnly);
#else
    assert(Telemetry::registerPolicy(name) == Policy::Disabled);
#endif
  }
  std::cout << "PASS: MQTT changes, retention, discovery, reconnect, retries, fixed refresh and millis rollover\n";
}
