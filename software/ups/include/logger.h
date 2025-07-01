#ifndef LOGGER_H
#define LOGGER_H

#include <Syslog.h>

class Logger {
 public:
  Logger(Syslog* syslog, Stream* serial);
  void log(uint16_t pri, const char* fmt, ...);
  void setSyslog(Syslog* syslog);

 private:
  Syslog* syslog = nullptr;  // Pointer to Syslog instance
  Stream* serial = nullptr;  // Pointer to Stream instance (e.g., Serial)
};

#endif  // LOGGER_H