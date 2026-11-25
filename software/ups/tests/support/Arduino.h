#pragma once

#include <string>
#include <cstdint>
#include <utility>

// Owned text and the small String API used by production settings/discovery modules.
class String : public std::string {
 public:
  using std::string::string;
  using std::string::operator=;
  String() = default;
  String(const String&) = default;
  String(String&&) = default;
  String& operator=(const String&) = default;
  String& operator=(String&&) = default;
  String(const std::string& value) : std::string(value) {}
  String(std::string&& value) : std::string(std::move(value)) {}
  void toLowerCase() {
    for (char& c : *this) {
      if (c >= 'A' && c <= 'Z') c = c - 'A' + 'a';
    }
  }
  size_t write(uint8_t value) { push_back(static_cast<char>(value)); return 1; }
  size_t write(const uint8_t* value, size_t length) { append(reinterpret_cast<const char*>(value), length); return length; }
};

using byte = uint8_t;
unsigned long millis();
