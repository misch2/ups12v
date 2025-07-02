#include "led_blinker.h"

LEDBlinker::LEDBlinker(int ledPin, unsigned long blinkSpeed) {
  this->ledPin = ledPin;
  this->blinkSpeed = blinkSpeed;
  this->timer = timer_create_default();  // create a timer with default settings
}

void LEDBlinker::setSpeed(unsigned long speed) {
  blinkSpeed = speed;
  start();
};

void LEDBlinker::start() {
  timer.cancel();
  timer.every(blinkSpeed / 2, callbackWrapper, this);
}

void LEDBlinker::loop() {
  timer.tick();  // call this in your loop to keep the timer active
}

bool LEDBlinker::toggle_led() {
  digitalWrite(ledPin, !digitalRead(ledPin));  // toggle the LED
  return true;
}

bool LEDBlinker::callbackWrapper(void *p) {
  LEDBlinker *ptr = (LEDBlinker *)p;
  if (ptr == nullptr) {
    return false;  // safety check
  }
  return ptr->toggle_led();
}
