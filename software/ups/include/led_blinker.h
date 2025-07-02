#ifndef LED_BLINKER_H
#define LED_BLINKER_H

#include <Arduino.h>
#include <arduino-timer.h>

class LEDBlinker {
 public:
  LEDBlinker(int ledPin, unsigned long blinkSpeed = 1000);
  void setSpeed(unsigned long speed);
  void loop();

 private:
  Timer<> timer;
  int ledPin;
  long blinkSpeed;  // in milliseconds

  static bool callbackWrapper(void *p);
  bool toggle_led();
};

#endif  // LED_BLINKER_H