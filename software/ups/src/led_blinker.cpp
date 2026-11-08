#include "led_blinker.h"

LEDBlinker::LEDBlinker(int ledPin, unsigned long blinkSpeed, bool activeHigh) {
  this->ledPin = ledPin;
  this->blinkSpeed = blinkSpeed;
  this->activeHigh = activeHigh;
}

void LEDBlinker::begin() {
  if (ledPin < 0) {
    return;
  }
  isOn = false;
  digitalWrite(ledPin, activeHigh ? LOW : HIGH);
  pinMode(ledPin, OUTPUT);
  start();
}

void LEDBlinker::setSpeed(unsigned long speed) {
  blinkSpeed = speed;
  start();
};

void LEDBlinker::start() {
  timer.cancel();
  if (ledPin < 0) {
    return;
  }
  timer.every(blinkSpeed / 2, callbackWrapper, this);
}

void LEDBlinker::loop() {
  timer.tick();  // call this in your loop to keep the timer active
}

bool LEDBlinker::toggle_led() {
  if (ledPin < 0) {
    return false;
  }
  isOn = !isOn;
  digitalWrite(ledPin, isOn == activeHigh ? HIGH : LOW);
  return true;
}

bool LEDBlinker::callbackWrapper(void *p) {
  LEDBlinker *ptr = (LEDBlinker *)p;
  if (ptr == nullptr) {
    return false;  // safety check
  }
  return ptr->toggle_led();
}
