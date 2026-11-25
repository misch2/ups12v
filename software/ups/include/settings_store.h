#pragma once

#include <string>

#include "hardware_profile.h"
#include "runtime_settings.h"

namespace Settings {
constexpr int kSchemaVersion = 1;
constexpr size_t kMaxRecordBytes = 8192;  // Bound parsing/allocation of damaged or imported data.

enum class Status {
  OK,
  SEEDED,
  MISSING,
  MALFORMED,
  INVALID_SETTINGS,
  OLDER_SCHEMA,
  NEWER_SCHEMA,
  HARDWARE_MISMATCH,
  IDENTITY_MISMATCH,
  STORAGE_ERROR,
  TOO_LARGE,
};

struct Result {
  constexpr Result(Status status, const char* detail = nullptr) : status(status), detail(detail) {}
  const Status status;
  const char* const detail;  // Static field/operation name only; never a setting value or password.
  bool ok() const { return status == Status::OK || status == Status::SEEDED; }
};

const char* statusName(Status status);
Result validate(const RuntimeSettings& settings);

// Private records contain MQTT credentials. Normal exports omit both user and password.
// Decoders change their output only on success. Export import preserves output's credentials.
Result encodePrivate(const RuntimeSettings& settings, const Hardware::Profile& hardware, std::string& output);
Result decodePrivate(const std::string& record, const Hardware::Profile& hardware, RuntimeSettings& output);
Result encodeExport(const RuntimeSettings& settings, const Hardware::Profile& hardware, std::string& output);
Result decodeExport(const std::string& record, const Hardware::Profile& hardware, RuntimeSettings& output);

class Backend {
 public:
  virtual ~Backend() = default;
  virtual Result read(std::string& output) = 0;
  // Replace the complete record as one storage value, never field-by-field.
  virtual Result write(const std::string& record) = 0;
};

class Store {
 public:
  Store(Backend& backend, const Hardware::Profile& hardware) : backend(backend), hardware(hardware) {}
  Result load(RuntimeSettings& output);
  Result seedIfMissing(const RuntimeSettings& compiledSettings);
  // Preserve damaged/unsupported records and the commissioned identity. One application writer.
  Result save(const RuntimeSettings& settings);

 private:
  Result writeVerified(const RuntimeSettings& settings);
  Backend& backend;
  const Hardware::Profile hardware;
};
}  // namespace Settings
