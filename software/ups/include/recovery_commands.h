#pragma once

#include <string>

namespace Recovery {
enum class Command { NONE, HELP, SHOW, START, STOP, RESET_WIFI, RESET_SETTINGS, INVALID };

// Bounded line input; no credential input/echo and no waiting for Serial data.
class Commands {
 public:
  Command feed(char c) {
    if (c == '\r') return Command::NONE;
    if (c != '\n') {
      if (line.size() >= 64) overflow = true;
      else line += c;
      return Command::NONE;
    }
    Command result = Command::INVALID;
    if (!overflow) {
      if (line.empty()) result = Command::NONE;
      else if (line == "help") result = Command::HELP;
      else if (line == "recovery") result = Command::SHOW;
      else if (line == "recovery on") result = Command::START;
      else if (line == "recovery off") result = Command::STOP;
      else if (line == "wifi reset FORGET WIFI") result = Command::RESET_WIFI;
      else if (line == "settings reset RESET SETTINGS") result = Command::RESET_SETTINGS;
    }
    line.clear();
    overflow = false;
    return result;
  }

 private:
  std::string line;
  bool overflow = false;
};
}  // namespace Recovery
