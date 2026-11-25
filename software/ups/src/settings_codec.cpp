#include "settings_store.h"

#include <ArduinoJson.h>

#include <climits>
#include <cmath>
#include <cstring>
#include <utility>

#include "charge_current.h"

namespace Settings {
namespace {
// One field inventory serves private records and redacted exports. No raw struct storage.
template <typename Visitor, typename Config>
bool fields(Visitor& visitor, Config& config, bool credentials) {
  return visitor.field("network.syslog.serverHostname", config.network.syslog.serverHostname) &&
         visitor.field("network.syslog.serverPort", config.network.syslog.serverPort) &&
         visitor.field("network.syslog.myHostname", config.network.syslog.myHostname) &&
         visitor.field("network.syslog.myAppname", config.network.syslog.myAppname) &&
         visitor.field("network.mqtt.serverHostname", config.network.mqtt.serverHostname) &&
         visitor.field("network.mqtt.serverPort", config.network.mqtt.serverPort) &&
         (!credentials || (visitor.field("network.mqtt.user", config.network.mqtt.user) &&
                           visitor.field("network.mqtt.password", config.network.mqtt.password))) &&
         visitor.field("network.mqtt.haDeviceName", config.network.mqtt.haDeviceName) &&
         visitor.field("temperatureSensor.resistance_25degC", config.temperatureSensor.resistance_25degC) &&
         visitor.field("temperatureSensor.beta", config.temperatureSensor.beta) &&
         visitor.field("battery.cell.name", config.battery.cell.name) &&
         visitor.field("battery.cell.approx80PercentCapacity_mV", config.battery.cell.approx80PercentCapacity_mV) &&
         visitor.field("battery.cell.approx20PercentCapacityUnderMaxLoad_mV", config.battery.cell.approx20PercentCapacityUnderMaxLoad_mV) &&
         visitor.field("battery.cell.overrideLimits.stopCell_mV", config.battery.cell.overrideLimits.stopCell_mV) &&
         visitor.field("battery.cell.overrideLimits.startCell_mV", config.battery.cell.overrideLimits.startCell_mV) &&
         visitor.field("battery.pack.capacity_mAh", config.battery.pack.capacity_mAh) &&
         visitor.field("battery.pack.maxChargeCurrent_mA", config.battery.pack.maxChargeCurrent_mA) &&
         visitor.field("power.input.retryUnqualifiedAdapter", config.power.input.retryUnqualifiedAdapter) &&
         visitor.field("power.input.IINDPM_mA", config.power.input.IINDPM_mA) &&
         visitor.field("power.input.VINDPM_mV", config.power.input.VINDPM_mV) &&
         visitor.field("power.input.VBUSBackupPercentage", config.power.input.VBUSBackupPercentage) &&
         visitor.field("power.charger.chargeProfile.mode", config.power.charger.chargeProfile.mode) &&
         visitor.field("power.charger.chargeProfile.fullCell_mV", config.power.charger.chargeProfile.fullCell_mV) &&
         visitor.field("power.charger.chargeProfile.rechargeOffset_mV", config.power.charger.chargeProfile.rechargeOffset_mV) &&
         visitor.field("power.charger.minCellVoltage_mV", config.power.charger.minCellVoltage_mV) &&
         visitor.field("power.charger.maxCellVoltage_mV", config.power.charger.maxCellVoltage_mV) &&
         visitor.field("power.charger.vbatChgEnableIfCellBelow_mV", config.power.charger.vbatChgEnableIfCellBelow_mV) &&
         visitor.field("power.charger.vbatChgDisableIfCellAbove_mV", config.power.charger.vbatChgDisableIfCellAbove_mV) &&
         visitor.field("power.charger.ICHG_mA", config.power.charger.ICHG_mA) &&
         visitor.field("power.output.IOTG_mA", config.power.output.IOTG_mA) &&
         visitor.field("power.output.VOTG_mV", config.power.output.VOTG_mV) &&
         visitor.field("ACRecoveryPeriodSeconds", config.ACRecoveryPeriodSeconds);
}

struct Writer {
  JsonObject object;
  template <typename T>
  bool field(const char* key, const T& value) {
    return object[key].set(value);
  }
  bool field(const char* key, const String& value) {
    // Embedded NULs would silently change C-string settings at the API boundary.
    const char* text = value.c_str();
    return text && std::strlen(text) == value.length() && object[key].set(text);
  }
  bool field(const char* key, BQ25798::VBUS_BACKUP_t value) { return object[key].set(static_cast<int>(value)); }
  bool field(const char* key, ChargeControl::Mode value) { return object[key].set(static_cast<int>(value)); }
};

struct Reader {
  JsonObjectConst object;
  size_t count = 0;
  const char* failed = nullptr;

  explicit Reader(JsonObjectConst object) : object(object) {}
  template <typename T>
  bool field(const char* key, T& value) {
    ++count;
    if (!object[key].is<T>()) {
      failed = key;
      return false;
    }
    value = object[key].as<T>();
    return true;
  }
  bool field(const char* key, String& value) {
    ++count;
    JsonString text = object[key].as<JsonString>();
    if (text.isNull() || std::strlen(text.c_str()) != text.size()) {
      failed = key;
      return false;
    }
    value = text.c_str();
    if (value.length() != text.size()) {
      failed = key;
      return false;
    }
    return true;
  }
  template <typename Enum>
  bool enumField(const char* key, Enum& value, int maximum) {
    int raw;
    if (!field(key, raw)) return false;
    if (raw < 0 || raw > maximum) {
      failed = key;
      return false;
    }
    value = static_cast<Enum>(raw);
    return true;
  }
  bool field(const char* key, BQ25798::VBUS_BACKUP_t& value) { return enumField(key, value, 3); }
  bool field(const char* key, ChargeControl::Mode& value) { return enumField(key, value, 2); }
};

// Track consumed input so a valid JSON prefix followed by garbage is not a valid record.
struct Input {
  const std::string& data;
  size_t position = 0;
  explicit Input(const std::string& data) : data(data) {}
  int read() { return position < data.size() ? static_cast<unsigned char>(data[position++]) : -1; }
  size_t readBytes(char* destination, size_t length) {
    const size_t remaining = data.size() - position;
    if (length > remaining) length = remaining;
    std::memcpy(destination, data.data() + position, length);
    position += length;
    return length;
  }
  bool finished() const {
    for (size_t i = position; i < data.size(); ++i) {
      if (data[i] != ' ' && data[i] != '\t' && data[i] != '\r' && data[i] != '\n') return false;
    }
    return true;
  }
};

const char* mcuName(const Hardware::Profile& hardware) { return hardware.mcu() == Hardware::MCU::ESP32 ? "esp32" : "esp32c3"; }
const char* pathName(const Hardware::Profile& hardware) {
  return hardware.powerPath() == Hardware::PowerPath::PMID_WITH_SWITCHOVER ? "pmid_switchover" : "sys";
}

void writeHardware(JsonObject object, const Hardware::Profile& hardware) {
  object["version"] = hardware.versionName();
  object["mcu"] = mcuName(hardware);
  object["power_path"] = pathName(hardware);
  object["sda"] = hardware.pins.I2C_SDA;
  object["scl"] = hardware.pins.I2C_SCL;
  object["led"] = hardware.pins.LED;
  object["led_active_high"] = hardware.pins.LED_ACTIVE_HIGH;
  object["charge_arm"] = hardware.pins.CHARGE_ARM;
}

bool matchesHardware(JsonObjectConst object, const Hardware::Profile& hardware) {
  return object.size() == 8 && object["version"] == hardware.versionName() && object["mcu"] == mcuName(hardware) &&
         object["power_path"] == pathName(hardware) && object["sda"].is<int>() && object["sda"] == hardware.pins.I2C_SDA &&
         object["scl"].is<int>() && object["scl"] == hardware.pins.I2C_SCL && object["led"].is<int>() && object["led"] == hardware.pins.LED &&
         object["led_active_high"].is<bool>() && object["led_active_high"] == hardware.pins.LED_ACTIVE_HIGH &&
         object["charge_arm"].is<int>() && object["charge_arm"] == hardware.pins.CHARGE_ARM;
}

Result encode(const RuntimeSettings& settings, const Hardware::Profile& hardware, bool credentials, std::string& output) {
  const auto result = validate(settings);
  if (!result.ok()) return result;
  JsonDocument document;
  document["schema"] = kSchemaVersion;
  document["credentials_included"] = credentials;
  writeHardware(document["hardware"].to<JsonObject>(), hardware);
  Writer writer{document["settings"].to<JsonObject>()};
  if (!fields(writer, settings, credentials) || document.overflowed()) return {Status::INVALID_SETTINGS, "encoding"};
  const size_t length = measureJson(document);
  if (length > kMaxRecordBytes) return {Status::TOO_LARGE};
  std::string record;
  if (serializeJson(document, record) != length) return {Status::STORAGE_ERROR, "serialization"};
  output.swap(record);
  return {Status::OK};
}

Result decode(const std::string& record, const Hardware::Profile& hardware, bool credentials, RuntimeSettings& output) {
  if (record.size() > kMaxRecordBytes) return {Status::TOO_LARGE};
  Input input(record);
  JsonDocument document;
  if (deserializeJson(document, input) || !input.finished() || !document.is<JsonObject>()) return {Status::MALFORMED};
  if (!document["schema"].is<int>()) return {Status::MALFORMED, "schema"};
  const int schema = document["schema"].as<int>();
  if (schema > kSchemaVersion) return {Status::NEWER_SCHEMA};
  if (schema < kSchemaVersion) return {Status::OLDER_SCHEMA};  // Schema 1 is the first format; no older migration exists yet.
  if (document.size() != 4 || !document["credentials_included"].is<bool>() || document["credentials_included"].as<bool>() != credentials ||
      !document["settings"].is<JsonObject>()) {
    return {Status::MALFORMED, "record fields"};
  }
  if (!matchesHardware(document["hardware"].as<JsonObjectConst>(), hardware)) return {Status::HARDWARE_MISMATCH};
  RuntimeSettings candidate;
  if (!credentials) {
    // Copy only the omitted fields, then move the fully decoded candidate without allocating on commit.
    candidate.network.mqtt.user = output.network.mqtt.user;
    candidate.network.mqtt.password = output.network.mqtt.password;
    if (candidate.network.mqtt.user.length() != output.network.mqtt.user.length() ||
        candidate.network.mqtt.password.length() != output.network.mqtt.password.length()) {
      return {Status::STORAGE_ERROR, "credential copy"};
    }
  }
  Reader reader(document["settings"].as<JsonObjectConst>());
  if (!fields(reader, candidate, credentials)) return {Status::MALFORMED, reader.failed};
  if (reader.count != reader.object.size()) return {Status::MALFORMED, "unknown settings fields"};
  const auto result = validate(candidate);
  if (!result.ok()) return result;
  output = std::move(candidate);
  return {Status::OK};
}
}  // namespace

Result validate(const RuntimeSettings& settings) {
  if (settings.network.mqtt.haDeviceName.length() == 0) return {Status::INVALID_SETTINGS, "network.mqtt.haDeviceName"};
  if (settings.network.syslog.serverPort < 1 || settings.network.syslog.serverPort > 65535 || settings.network.mqtt.serverPort < 1 ||
      settings.network.mqtt.serverPort > 65535) {
    return {Status::INVALID_SETTINGS, "network port"};
  }
  if (!std::isfinite(settings.temperatureSensor.resistance_25degC) || settings.temperatureSensor.resistance_25degC <= 0 ||
      !std::isfinite(settings.temperatureSensor.beta) || settings.temperatureSensor.beta <= 0) {
    return {Status::INVALID_SETTINGS, "temperatureSensor"};
  }
  if (!settings.battery.cell.overrideLimits.valid() || settings.battery.cell.approx80PercentCapacity_mV < 0 ||
      settings.battery.cell.approx20PercentCapacityUnderMaxLoad_mV < 0 || settings.battery.pack.capacity_mAh < 0) {
    return {Status::INVALID_SETTINGS, "battery"};
  }
  const int maximum = settings.battery.pack.maxChargeCurrent_mA;
  if (maximum < 0 || settings.power.charger.ICHG_mA < 50 ||
      (maximum != 0 && ChargeControl::currentLimit_mA(settings.power.charger.ICHG_mA, maximum) == 0)) {
    return {Status::INVALID_SETTINGS, "battery.pack.maxChargeCurrent_mA / power.charger.ICHG_mA"};
  }
  const auto& profile = settings.power.charger.chargeProfile;
  if (profile.mode != ChargeControl::Mode::LEGACY && profile.mode != ChargeControl::Mode::FULL && profile.mode != ChargeControl::Mode::APPROX_80) {
    return {Status::INVALID_SETTINGS, "power.charger.chargeProfile.mode"};
  }
  if (ChargeControl::plan(profile, 2, settings.battery.cell.approx80PercentCapacity_mV).error ||
      ChargeControl::plan(profile, 4, settings.battery.cell.approx80PercentCapacity_mV).error) {
    return {Status::INVALID_SETTINGS, "power.charger.chargeProfile"};
  }
  const int backup = static_cast<int>(settings.power.input.VBUSBackupPercentage);
  if (backup < 0 || backup > 3) return {Status::INVALID_SETTINGS, "power.input.VBUSBackupPercentage"};
  if (settings.power.charger.minCellVoltage_mV <= 0 || settings.power.charger.maxCellVoltage_mV <= settings.power.charger.minCellVoltage_mV ||
      settings.power.charger.vbatChgEnableIfCellBelow_mV <= 0 ||
      settings.power.charger.vbatChgDisableIfCellAbove_mV <= settings.power.charger.vbatChgEnableIfCellBelow_mV) {
    return {Status::INVALID_SETTINGS, "power.charger legacy voltage thresholds"};
  }
  if (settings.ACRecoveryPeriodSeconds < 0 || settings.ACRecoveryPeriodSeconds > INT_MAX / 1000) {
    return {Status::INVALID_SETTINGS, "ACRecoveryPeriodSeconds"};
  }
  return {Status::OK};
}

Result encodePrivate(const RuntimeSettings& settings, const Hardware::Profile& hardware, std::string& output) {
  return encode(settings, hardware, true, output);
}
Result decodePrivate(const std::string& record, const Hardware::Profile& hardware, RuntimeSettings& output) {
  return decode(record, hardware, true, output);
}
Result encodeExport(const RuntimeSettings& settings, const Hardware::Profile& hardware, std::string& output) {
  return encode(settings, hardware, false, output);
}
Result decodeExport(const std::string& record, const Hardware::Profile& hardware, RuntimeSettings& output) {
  return decode(record, hardware, false, output);
}

const char* statusName(Status status) {
  switch (status) {
    case Status::OK:
      return "existing valid record";
    case Status::SEEDED:
      return "created and verified";
    case Status::MISSING:
      return "missing";
    case Status::MALFORMED:
      return "malformed record";
    case Status::INVALID_SETTINGS:
      return "invalid settings";
    case Status::OLDER_SCHEMA:
      return "unsupported older schema";
    case Status::NEWER_SCHEMA:
      return "newer schema preserved";
    case Status::HARDWARE_MISMATCH:
      return "hardware mismatch";
    case Status::IDENTITY_MISMATCH:
      return "device identifier mismatch";
    case Status::STORAGE_ERROR:
      return "storage read/write error";
    case Status::TOO_LARGE:
      return "record too large";
  }
  return "unknown status";
}
}  // namespace Settings
