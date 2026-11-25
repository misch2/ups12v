#include "wifi_settings.h"

#include <cstring>
#include <utility>

namespace Settings {
namespace {
const std::string kEmpty("UPSW\1\0\0", 7);
bool noNul(const std::string& value) { return value.find('\0') == std::string::npos; }
}  // namespace

Result WifiStore::validate(const WifiCredentials& credentials) {
  if (credentials.ssid.empty() || credentials.ssid.size() > 32 || !noNul(credentials.ssid)) return {Status::INVALID_SETTINGS, "Wi-Fi SSID"};
  const auto& password = credentials.password;
  if (!noNul(password)) return {Status::INVALID_SETTINGS, "Wi-Fi password"};
  if (password.empty() || (password.size() >= 8 && password.size() <= 63)) return {Status::OK};
  if (password.size() == 64 && password.find_first_not_of("0123456789abcdefABCDEF") == std::string::npos) return {Status::OK};
  return {Status::INVALID_SETTINGS, "Wi-Fi password length / PSK"};
}

Result WifiStore::pending(WifiCredentials& credentials) {
  std::string record;
  const auto result = backend.read(record);
  if (!result.ok()) return result;
  if (record == kEmpty) return {Status::MISSING};
  if (record.size() < 7 || record.compare(0, 5, kEmpty, 0, 5) != 0) return {Status::MALFORMED, "pending Wi-Fi"};
  const size_t ssidLength = static_cast<unsigned char>(record[5]);
  const size_t passwordLength = static_cast<unsigned char>(record[6]);
  if (record.size() != 7 + ssidLength + passwordLength) return {Status::MALFORMED, "pending Wi-Fi length"};
  WifiCredentials candidate{record.substr(7, ssidLength), record.substr(7 + ssidLength, passwordLength)};
  const auto valid = validate(candidate);
  if (!valid.ok()) return valid;
  credentials = std::move(candidate);
  return {Status::OK};
}

Result WifiStore::writeVerified(const std::string& record) {
  const auto result = backend.write(record);
  if (!result.ok()) return result;
  std::string readback;
  const auto read = backend.read(readback);
  if (!read.ok() || readback != record) return {Status::STORAGE_ERROR, "pending Wi-Fi readback"};
  return {Status::OK};
}

Result WifiStore::stage(const WifiCredentials& credentials) {
  const auto valid = validate(credentials);
  if (!valid.ok()) return valid;
  // Do not replace an unreadable/protected pending record.
  WifiCredentials previous;
  const auto existing = pending(previous);
  if (!existing.ok() && existing.status != Status::MISSING) return existing;
  std::string record = kEmpty;
  record[5] = static_cast<char>(credentials.ssid.size());
  record[6] = static_cast<char>(credentials.password.size());
  record += credentials.ssid;
  record += credentials.password;
  return writeVerified(record);
}

Result WifiStore::cancel() {
  WifiCredentials previous;
  const auto existing = pending(previous);
  if (existing.status == Status::MISSING) return {Status::OK};
  if (!existing.ok()) return existing;
  return writeVerified(kEmpty);
}

Result WifiStore::applyAtBoot() {
  WifiCredentials credentials;
  const auto result = pending(credentials);
  if (result.status == Status::MISSING) return {Status::OK};
  if (!result.ok()) return result;
  const auto written = driver.write(credentials);
  if (!written.ok()) return written;  // Retain the pending record for an explicit recovery/retry.
  WifiCredentials actual;
  const auto read = driver.read(actual);
  if (!read.ok() || actual.ssid != credentials.ssid || actual.password != credentials.password) {
    return {Status::STORAGE_ERROR, "Wi-Fi SDK readback"};
  }
  return writeVerified(kEmpty);
}
}  // namespace Settings
