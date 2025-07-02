#include <Arduino.h>
#include <arduino-timer.h>

class LEDBlinker {
 public:
  LEDBlinker(int ledPin, unsigned long blinkSpeed = 1000) : blinkSpeed(blinkSpeed) {
    this->ledPin = ledPin;
    this->blinkSpeed = blinkSpeed;
    this->timer = timer_create_default();  // create a timer with default settings
  }

  void setSpeed(unsigned long speed) {
    blinkSpeed = speed;
    timer.cancel();
    timer.every(blinkSpeed / 2, callback, this);
  }

  void loop() {
    timer.tick();  // call this in your loop to keep the timer active
  }

 private:
  Timer<> timer;
  int ledPin;
  long blinkSpeed;  // in milliseconds

  static bool callback(void *p) {
    LEDBlinker *ptr = (LEDBlinker *)p;
    if (ptr == nullptr) {
      return false;  // safety check
    }
    return ptr->toggle_led();
  }

  bool toggle_led() {
    digitalWrite(ledPin, !digitalRead(ledPin));  // toggle the LED
    return true;
  }
};
