#include "logger.h"

#include <WiFi.h>

#include <cstdarg>

Logger::Logger(Syslog* syslog, Stream* serial) {
  this->syslog = syslog;
  this->serial = serial;
};

void Logger::log(uint16_t pri, const char* fmt, ...) {
  va_list args;
  va_start(args, fmt);

  if (syslog && WiFi.status() == WL_CONNECTED) {
    syslog->vlogf(pri, fmt, args);
  }

  if (serial) {
    char buffer[256];
    vsnprintf(buffer, sizeof(buffer), fmt, args);
    serial->println(buffer);  // can't used printf() here because it doesn't support va_args!
    serial->flush();
  }
  va_end(args);
}

void Logger::setSyslog(Syslog* syslog) { this->syslog = syslog; }
