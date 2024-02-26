# Target

A hobby project to create simple 12 V UPS to backup my router and mini PC. Both appliances use 12 volts on input. 
This UPS:
 - should be powered by 18650 batteries
 - does not need to run for a long time, 15 minutes is perfectly OK, 30 minutes is luxury
 - should allow some sort of monitoring, ideally with an HomeAssistant integration (for charts etc.)
 - should provide at least this amount of power
   - 1A (for router)
   - or 3A (for mini PC)
 - should run primarily from the main source and switch to the batteries only when the main voltage drops. This is to protect the batteries and charging circuit so that it doesn't need to constantly provide relatively high power for a device.
 - might allow powering off itself on request when running on batteries, to allow mini PC to automatically power on later after a shutdown.

# Inspiration / sources
- https://www.hackster.io/news/a-diy-mini-ups-for-wi-fi-router-9b8f11540294
- https://digitalab.org/2021/08/router-ups/


# Hardware

https://oshwlab.com/michalschwarz/12v-ups

How it works (or should work):
1. After the power on it produces pass through power only because the "EN" pin for XL6009 voltage booster is pulled to the ground.
    - Additional powered component are step down converter for ESP32 and battery charger TP5100
1. A moment later ESP32 finishes booting and starts periodically meeasuring battery and voltage. Once it detects that battery/charger power (which serves as an input for the booster converter) is sufficiently high it enables the XL6009 booster which starts producing 12V on it's output.
1. Because the main power is on, it keeps P-MOSFET Q1 closed so that the output is tied directly to the main power. Ouput from batteries/charger is not connected to the UPS output.
1. If a power outage occurs Q1 opens and the booster imediatelly gets connected to the output.
1. ESP32 provides monitoring of input and output voltage, current and power.
1. If input power turns on again, Q1 closes and the booster output gets disconnected.

When running on battery:
1. Software may request to turn boosterEnable off, effectively shutting down the UPS completely.
2. ESP32 monitors battery voltage (which serves as an input for the booster). If it drops under a certain threshold then the ESP32 preventively shuts down the UPS too, to prevent issues with XL6009 producing too high voltage on it's output when the input voltage is <5V.

# Development progress

Replaced AMS1117 with a buck converter due to a large voltage difference and therefore large heat dissipation with LDO.

Added XL6009 "EN" pin control (initial pull down + software control from ESP32)

# TODO (obstacles)

~Find out if XL6009 is OK under all circumstances, especially when powering on or with low input voltage. I measured more than 12 V on it's output in these situations!~
Resolved by using "EN" input on XL6009 and turning it on only when measured voltage exceeds allowed threshold. 

Disconnect XL6009 output if main power is sufficient, to prevent situations when TP5100 not only charges the batteries but it's output is also used for powering the device via booster. We don't want to overload the charger (nor the main power source). P-MOSFET to the rescue?



