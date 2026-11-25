#pragma once

#include <cstddef>
#include <cstring>

// The installed ESP32 NetworkManager copies hostnames into a 32-byte buffer.
class DeviceIdentity {
 public:
  static constexpr size_t kMaxLength = 31;

  static bool validStored(const char* value) {
    if (!value || !value[0] || value[0] == '-') return false;
    size_t length = 0;
    bool placeholder = true;
    const char* reserved = "default-ups";
    for (; value[length]; ++length) {
      if (length >= kMaxLength) return false;
      const char c = value[length];
      if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '-')) return false;
      const char lower = c >= 'A' && c <= 'Z' ? c - 'A' + 'a' : c;
      if (length >= 11 || lower != reserved[length]) placeholder = false;
    }
    return value[length - 1] != '-' && !(placeholder && length == 11);
  }

  // Canonical new IDs avoid case/underscore collisions in default_entity_id normalization.
  static bool validNew(const char* value) {
    if (!validStored(value)) return false;
    for (const char* p = value; *p; ++p) {
      if (*p >= 'A' && *p <= 'Z') return false;
    }
    return true;
  }

  bool bind(const char* value) {
    if (!validStored(value)) return false;
    if (ready()) return std::strcmp(identifier, value) == 0;
    std::memcpy(identifier, value, std::strlen(value) + 1);
    return true;
  }
  bool ready() const { return identifier[0] != '\0'; }
  const char* value() const { return identifier; }

 private:
  char identifier[kMaxLength + 1] = {};
};
