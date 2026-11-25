#include <ArduinoJson.h>

#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <limits>

#include "nvs.h"
#include "settings_nvs.h"

using Settings::Status;

struct MemoryBackend : Settings::Backend {
  bool present = false;
  bool failRead = false;
  bool failWrite = false;
  bool failReadback = false;
  bool corruptWrite = false;
  bool errorAfterWrite = false;
  int writes = 0;
  std::string record;
  Settings::Result read(std::string& output) override {
    if (failRead) return {Status::STORAGE_ERROR};
    if (!present) return {Status::MISSING};
    output = record;
    return {Status::OK};
  }
  Settings::Result write(const std::string& value) override {
    ++writes;
    if (failWrite) return {Status::STORAGE_ERROR};
    record = corruptWrite ? "{}" : value;
    present = true;
    if (failReadback) failRead = true;
    return {errorAfterWrite ? Status::STORAGE_ERROR : Status::OK};
  }
};

RuntimeSettings exampleSettings() {
  RuntimeSettings settings;
  settings.network.syslog.serverHostname = "log.example.test";
  settings.network.syslog.serverPort = 1514;
  settings.network.syslog.myHostname = "test-board";
  settings.network.syslog.myAppname = "test-app";
  settings.network.mqtt.serverHostname = "broker.example.test";
  settings.network.mqtt.serverPort = 2883;
  settings.network.mqtt.user = "TEST_ONLY_USER";
  settings.network.mqtt.password = "TEST_ONLY_PASSWORD";
  settings.network.mqtt.haDeviceName = "test-ups";
  settings.temperatureSensor.resistance_25degC = 9840.5;
  settings.temperatureSensor.beta = 3970.5;
  settings.battery.cell.name = "Test cell \"quoted\" \\ Unicode \xC2\xB0";
  settings.battery.cell.approx80PercentCapacity_mV = 3905;
  settings.battery.cell.approx20PercentCapacityUnderMaxLoad_mV = 3255;
  settings.battery.cell.overrideLimits.stopCell_mV = 3500;
  settings.battery.cell.overrideLimits.startCell_mV = 3650;
  settings.battery.pack.capacity_mAh = 5000;
  settings.battery.pack.maxChargeCurrent_mA = 900;
  settings.power.input.retryUnqualifiedAdapter = true;
  settings.power.input.IINDPM_mA = 1700;
  settings.power.input.VINDPM_mV = 4800;
  settings.power.input.VBUSBackupPercentage = BQ25798::VBUS_BACKUP_t::PCT_VBUS_BACKUP_60;
  settings.power.charger.chargeProfile.mode = ChargeControl::Mode::APPROX_80;
  settings.power.charger.chargeProfile.fullCell_mV = 4150;
  settings.power.charger.chargeProfile.rechargeOffset_mV = 150;
  settings.power.charger.minCellVoltage_mV = 3100;
  settings.power.charger.maxCellVoltage_mV = 4150;
  settings.power.charger.vbatChgEnableIfCellBelow_mV = 4050;
  settings.power.charger.vbatChgDisableIfCellAbove_mV = 4100;
  settings.power.charger.ICHG_mA = 850;
  settings.power.output.IOTG_mA = 1400;
  settings.power.output.VOTG_mV = 11900;
  settings.ACRecoveryPeriodSeconds = 45;
  return settings;
}

// Compare the public configuration contract, including fields unused by this hardware path.
void sameSettings(const RuntimeSettings& a, const RuntimeSettings& b) {
  assert(a.network.syslog.serverHostname == b.network.syslog.serverHostname);
  assert(a.network.syslog.serverPort == b.network.syslog.serverPort);
  assert(a.network.syslog.myHostname == b.network.syslog.myHostname);
  assert(a.network.syslog.myAppname == b.network.syslog.myAppname);
  assert(a.network.mqtt.serverHostname == b.network.mqtt.serverHostname);
  assert(a.network.mqtt.serverPort == b.network.mqtt.serverPort);
  assert(a.network.mqtt.user == b.network.mqtt.user && a.network.mqtt.password == b.network.mqtt.password);
  assert(a.network.mqtt.haDeviceName == b.network.mqtt.haDeviceName);
  assert(a.temperatureSensor.resistance_25degC == b.temperatureSensor.resistance_25degC && a.temperatureSensor.beta == b.temperatureSensor.beta);
  assert(a.battery.cell.name == b.battery.cell.name);
  assert(a.battery.cell.approx80PercentCapacity_mV == b.battery.cell.approx80PercentCapacity_mV);
  assert(a.battery.cell.approx20PercentCapacityUnderMaxLoad_mV == b.battery.cell.approx20PercentCapacityUnderMaxLoad_mV);
  assert(a.battery.cell.overrideLimits.stopCell_mV == b.battery.cell.overrideLimits.stopCell_mV);
  assert(a.battery.cell.overrideLimits.startCell_mV == b.battery.cell.overrideLimits.startCell_mV);
  assert(a.battery.pack.capacity_mAh == b.battery.pack.capacity_mAh && a.battery.pack.maxChargeCurrent_mA == b.battery.pack.maxChargeCurrent_mA);
  assert(a.power.input.retryUnqualifiedAdapter == b.power.input.retryUnqualifiedAdapter);
  assert(a.power.input.IINDPM_mA == b.power.input.IINDPM_mA && a.power.input.VINDPM_mV == b.power.input.VINDPM_mV);
  assert(a.power.input.VBUSBackupPercentage == b.power.input.VBUSBackupPercentage);
  assert(a.power.charger.chargeProfile.mode == b.power.charger.chargeProfile.mode);
  assert(a.power.charger.chargeProfile.fullCell_mV == b.power.charger.chargeProfile.fullCell_mV);
  assert(a.power.charger.chargeProfile.rechargeOffset_mV == b.power.charger.chargeProfile.rechargeOffset_mV);
  assert(a.power.charger.minCellVoltage_mV == b.power.charger.minCellVoltage_mV && a.power.charger.maxCellVoltage_mV == b.power.charger.maxCellVoltage_mV);
  assert(a.power.charger.vbatChgEnableIfCellBelow_mV == b.power.charger.vbatChgEnableIfCellBelow_mV);
  assert(a.power.charger.vbatChgDisableIfCellAbove_mV == b.power.charger.vbatChgDisableIfCellAbove_mV);
  assert(a.power.charger.ICHG_mA == b.power.charger.ICHG_mA);
  assert(a.power.output.IOTG_mA == b.power.output.IOTG_mA && a.power.output.VOTG_mV == b.power.output.VOTG_mV);
  assert(a.ACRecoveryPeriodSeconds == b.ACRecoveryPeriodSeconds);
}

template <typename Edit>
std::string edited(const std::string& record, Edit edit) {
  JsonDocument document;
  assert(!deserializeJson(document, record));
  edit(document);
  std::string output;
  serializeJson(document, output);
  return output;
}

void roundTrips() {
  const auto settings = exampleSettings();
  const Hardware::Profile profiles[] = {Hardware::kV1Esp32, Hardware::kV3SysEsp32, Hardware::kV4Esp32C3};
  for (const auto& hardware : profiles) {
    std::string record;
    assert(Settings::encodePrivate(settings, hardware, record).ok());
    RuntimeSettings output;
    assert(Settings::decodePrivate(record + " \n\t", hardware, output).ok());
    sameSettings(settings, output);
  }
  RuntimeSettings unset;
  std::string record;
  assert(Settings::encodePrivate(unset, Hardware::kV4Esp32C3, record).ok());  // Zero pack limit still represents inhibited charging.
  RuntimeSettings output = settings;
  assert(Settings::decodePrivate(record, Hardware::kV4Esp32C3, output).ok());
  sameSettings(unset, output);
  std::printf("round trips: all fields, 3 profiles, defaults, escaping; sample private record %zu bytes\n", record.size());
}

void malformedRecords() {
  const auto expected = exampleSettings();
  std::string good;
  assert(Settings::encodePrivate(expected, Hardware::kV4Esp32C3, good).ok());
  auto reject = [&](const std::string& record, Status status) {
    RuntimeSettings output = expected;
    assert(Settings::decodePrivate(record, Hardware::kV4Esp32C3, output).status == status);
    sameSettings(output, expected);
  };
  reject("", Status::MALFORMED);
  reject(good.substr(0, good.size() - 1), Status::MALFORMED);
  reject(good + "x", Status::MALFORMED);
  reject(good + "{}", Status::MALFORMED);
  reject(good + std::string(1, '\0'), Status::MALFORMED);
  reject(std::string(Settings::kMaxRecordBytes + 1, 'x'), Status::TOO_LARGE);
  reject(edited(good, [](JsonDocument& d) { d["schema"] = 0; }), Status::OLDER_SCHEMA);
  reject(edited(good, [](JsonDocument& d) { d["schema"] = 2; }), Status::NEWER_SCHEMA);
  reject(edited(good, [](JsonDocument& d) { d["schema"] = "1"; }), Status::MALFORMED);
  reject(edited(good, [](JsonDocument& d) { d["hardware"]["sda"] = 21; }), Status::HARDWARE_MISMATCH);
  reject(edited(good, [](JsonDocument& d) { d["settings"].remove("battery.cell.name"); }), Status::MALFORMED);
  reject(edited(good, [](JsonDocument& d) { d["settings"]["unknown"] = 1; }), Status::MALFORMED);
  reject(edited(good, [](JsonDocument& d) { d["settings"]["power.charger.ICHG_mA"] = "850"; }), Status::MALFORMED);
  reject(edited(good, [](JsonDocument& d) { d["settings"]["power.charger.ICHG_mA"] = 1.5; }), Status::MALFORMED);
  reject(edited(good, [](JsonDocument& d) { d["settings"]["power.charger.ICHG_mA"] = 2147483648LL; }), Status::MALFORMED);
  reject(edited(good, [](JsonDocument& d) { d["settings"]["power.input.retryUnqualifiedAdapter"] = 1; }), Status::MALFORMED);
  reject(edited(good, [](JsonDocument& d) { d["settings"]["power.input.VBUSBackupPercentage"] = 256; }), Status::MALFORMED);
  reject(edited(good, [](JsonDocument& d) { d["settings"]["power.charger.chargeProfile.mode"] = -1; }), Status::MALFORMED);
  reject(edited(good, [](JsonDocument& d) { d["settings"]["battery.pack.maxChargeCurrent_mA"] = 99; }), Status::INVALID_SETTINGS);
  reject(edited(good, [](JsonDocument& d) { d["settings"]["battery.cell.name"] = JsonString("abc\0def", 7); }), Status::MALFORMED);
  std::puts("invalid input: types, fields, trailing data, schemas, hardware, enums and unchanged output passed");
}

void exportsAndValidation() {
  auto settings = exampleSettings();
  std::string record;
  assert(Settings::encodeExport(settings, Hardware::kV4Esp32C3, record).ok());
  assert(record.find("TEST_ONLY_USER") == std::string::npos && record.find("TEST_ONLY_PASSWORD") == std::string::npos);
  RuntimeSettings target;
  target.network.mqtt.user = "other-user";
  target.network.mqtt.password = "other-password";
  assert(Settings::decodeExport(record, Hardware::kV4Esp32C3, target).ok());
  settings.network.mqtt.user = target.network.mqtt.user;
  settings.network.mqtt.password = target.network.mqtt.password;
  sameSettings(settings, target);
  assert(Settings::decodePrivate(record, Hardware::kV4Esp32C3, target).status == Status::MALFORMED);
  const auto injection = edited(record, [](JsonDocument& d) { d["settings"]["network.mqtt.password"] = "injected"; });
  assert(Settings::decodeExport(injection, Hardware::kV4Esp32C3, target).status == Status::MALFORMED);
  sameSettings(settings, target);
  for (int cells : {2, 4}) {
    const auto plan = ChargeControl::plan(target.power.charger.chargeProfile, cells, target.battery.cell.approx80PercentCapacity_mV);
    assert(!plan.error && plan.pack_mV <= cells * 3905);
  }
  settings.temperatureSensor.beta = std::numeric_limits<double>::infinity();
  assert(Settings::validate(settings).status == Status::INVALID_SETTINGS);
  assert(Settings::encodePrivate(settings, Hardware::kV4Esp32C3, record).status == Status::INVALID_SETTINGS);
  settings = exampleSettings();
  settings.ACRecoveryPeriodSeconds = std::numeric_limits<int>::max();
  assert(!Settings::validate(settings).ok());
  settings = exampleSettings();
  settings.power.input.VINDPM_mV = -1;  // Preserve existing nonpositive "do not write" semantics.
  assert(Settings::validate(settings).ok());
  settings.battery.cell.name = std::string(Settings::kMaxRecordBytes, 'x').c_str();
  const std::string previous = record;
  assert(Settings::encodePrivate(settings, Hardware::kV4Esp32C3, record).status == Status::TOO_LARGE && record == previous);
  std::puts("exports: no credentials, preserved local credentials, no injection; validation and size limits passed");
}

void storeBehaviour() {
  const auto settings = exampleSettings();
  {
    MemoryBackend unavailable;
    unavailable.failWrite = true;
    Settings::Store firstBoot(unavailable, Hardware::kV4Esp32C3);
    assert(firstBoot.seedIfMissing(settings).status == Status::STORAGE_ERROR && !unavailable.present);
    unavailable.failWrite = false;
    assert(firstBoot.seedIfMissing(settings).status == Status::SEEDED && unavailable.writes == 2);
  }
  MemoryBackend backend;
  Settings::Store store(backend, Hardware::kV4Esp32C3);
  RuntimeSettings output;
  assert(store.load(output).status == Status::MISSING);
  assert(store.seedIfMissing(settings).status == Status::SEEDED && backend.writes == 1);
  assert(store.load(output).ok());
  sameSettings(settings, output);
  auto changed = settings;
  changed.battery.cell.name = "new source defaults";
  assert(store.seedIfMissing(changed).ok() && backend.writes == 1);
  assert(store.load(output).ok());
  sameSettings(settings, output);
  assert(store.save(changed).ok() && backend.writes == 2);
  Settings::Store afterReboot(backend, Hardware::kV4Esp32C3);
  assert(afterReboot.load(output).ok());
  sameSettings(changed, output);
  changed.network.mqtt.haDeviceName = "different-ups";
  assert(store.save(changed).status == Status::IDENTITY_MISMATCH && backend.writes == 2);
  assert(store.seedIfMissing(changed).status == Status::IDENTITY_MISMATCH && backend.writes == 2);
  const std::string saved = backend.record;
  const std::string protectedRecords[] = {"{", "{\"schema\":0}", "{\"schema\":2}", std::string(Settings::kMaxRecordBytes + 1, 'x')};
  for (const auto& record : protectedRecords) {
    backend.record = record;
    assert(!store.seedIfMissing(settings).ok() && !store.save(settings).ok());
    assert(backend.record == record && backend.writes == 2);
  }
  backend.record = saved;
  Settings::Store wrongHardware(backend, Hardware::kV1Esp32);
  assert(wrongHardware.seedIfMissing(settings).status == Status::HARDWARE_MISMATCH && backend.writes == 2);
  backend.failRead = true;
  assert(store.seedIfMissing(settings).status == Status::STORAGE_ERROR && backend.writes == 2);
  backend.failRead = false;
  backend.failWrite = true;
  assert(store.save(settings).status == Status::STORAGE_ERROR && backend.record == saved);
  backend.failWrite = false;
  backend.corruptWrite = true;
  assert(store.save(settings).status == Status::STORAGE_ERROR);
  backend.record = saved;
  backend.corruptWrite = false;
  backend.failReadback = true;
  assert(store.save(settings).status == Status::STORAGE_ERROR);
  backend.failRead = false;
  backend.failReadback = false;
  backend.errorAfterWrite = true;
  assert(store.save(settings).status == Status::STORAGE_ERROR);
  assert(store.load(output).ok());  // A reported failure may leave a complete new record; do not pretend it rolled back.
  sameSettings(settings, output);
  std::puts("store: seed once, reboot, guarded save, protected records, write/readback/commit uncertainty passed");
}

struct NvsSimulation {
  bool exists = false;
  bool failOpen = false;
  bool wrongType = false;
  bool failGet = false;
  bool failSet = false;
  bool failCommit = false;
  int closes = 0;
  nvs_open_mode_t mode = NVS_READONLY;
  std::string blob;
} nvs;

esp_err_t nvs_open(const char* name, nvs_open_mode_t mode, nvs_handle_t* handle) {
  assert(std::strcmp(name, "ups-settings") == 0);
  if (nvs.failOpen) return ESP_FAIL;
  if (!nvs.exists && mode == NVS_READONLY) return ESP_ERR_NVS_NOT_FOUND;
  nvs.mode = mode;
  *handle = 1;
  return ESP_OK;
}
esp_err_t nvs_get_blob(nvs_handle_t handle, const char* key, void* output, size_t* length) {
  assert(handle == 1 && std::strcmp(key, "config") == 0);
  if (!nvs.exists) return ESP_ERR_NVS_NOT_FOUND;
  if (nvs.wrongType) return ESP_ERR_NVS_TYPE_MISMATCH;
  if (nvs.failGet) return ESP_FAIL;
  if (output) {
    assert(*length >= nvs.blob.size());
    std::memcpy(output, nvs.blob.data(), nvs.blob.size());
  }
  *length = nvs.blob.size();
  return ESP_OK;
}
esp_err_t nvs_set_blob(nvs_handle_t handle, const char* key, const void* data, size_t length) {
  assert(handle == 1 && std::strcmp(key, "config") == 0 && nvs.mode == NVS_READWRITE);
  if (nvs.failSet) return ESP_FAIL;
  nvs.blob.assign(static_cast<const char*>(data), length);
  nvs.exists = true;
  return ESP_OK;
}
esp_err_t nvs_commit(nvs_handle_t handle) {
  assert(handle == 1 && nvs.mode == NVS_READWRITE);
  return nvs.failCommit ? ESP_FAIL : ESP_OK;
}
void nvs_close(nvs_handle_t handle) {
  assert(handle == 1);
  ++nvs.closes;
}

void nvsAdapter() {
  Settings::NvsBackend backend;
  std::string value = "unchanged";
  assert(backend.read(value).status == Status::MISSING && !nvs.exists && nvs.closes == 0);
  assert(backend.write("private-test-record").ok() && nvs.closes == 1);
  assert(backend.read(value).ok() && value == "private-test-record" && nvs.closes == 2);
  nvs.failOpen = true;
  assert(backend.read(value).status == Status::STORAGE_ERROR);
  nvs.failOpen = false;
  nvs.wrongType = true;
  assert(backend.read(value).status == Status::MALFORMED);
  nvs.wrongType = false;
  nvs.failGet = true;
  assert(backend.read(value).status == Status::STORAGE_ERROR);
  nvs.failGet = false;
  nvs.failSet = true;
  assert(backend.write("replacement").status == Status::STORAGE_ERROR && nvs.blob == "private-test-record");
  nvs.failSet = false;
  nvs.failCommit = true;
  assert(backend.write("replacement").status == Status::STORAGE_ERROR);
  nvs.failCommit = false;
  nvs.blob.clear();
  assert(backend.read(value).status == Status::MALFORMED);
  nvs.blob.assign(Settings::kMaxRecordBytes + 1, 'x');
  assert(backend.read(value).status == Status::TOO_LARGE);
  std::puts("NVS adapter: isolated namespace, missing/type/size/I/O handling, closure and commit errors passed");
}

int main() {
  roundTrips();
  malformedRecords();
  exportsAndValidation();
  storeBehaviour();
  nvsAdapter();
  std::puts("settings_store: all behavioral checks passed (platform dependencies simulated)");
}
