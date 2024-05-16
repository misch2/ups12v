# Goal

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

# Inspiration
* https://www.hackster.io/news/a-diy-mini-ups-for-wi-fi-router-9b8f11540294
* https://digitalab.org/2021/08/router-ups/
* Lithium battery charger module (12W, 3A) with 5V to 12V booster from Aliexpress:
https://vi.aliexpress.com/item/1005005742927465.html?gatewayAdapt=glo2vnm

# Version 1

Deployed to production, used for a backup of my Archer C6 router only. 
But it's mostly a proof of concept, with power limitations and without a proper PCB (components are just wired up together).

Schema: [schema_v1.pdf](hardware/v1/schema.pdf)

Some photos: [photo1](hardware/v1/IMG_20240301_100945.jpg), [photo2](hardware/v1/IMG_20240302_140645.jpg), [photo3](hardware/v1/IMG_20240302_140731.jpg).

The limitations were caused by:
 - BMS module for 18650 batteries can handle only 2A (FIXME?) of current. This is not enough for the mini PC.
 - INA219 module can handle only 3.2A of current. Again, this is not enough for the mini PC (especially not for the battery side of the UPS where the max current can easily be larger).
 - The specific XL6009 booster module doesn't have an undervoltage protection and it can produce more than 12 V on it's output when the input voltage is low. This is not good!

Anyway, this works well for the router. It can run for more than 2 hours from batteries because the router consumes only about 3 watts and the output current is therefore mostly below 300 mA. So I might call this a success ✅!

# Version 2

I wanted to overcome the limitations of the first version and to make it handle larger current to power the mini PC which might need up to 3 A. This higher current would also require something better than the INA219.

I also added relays to allow the UPS to be powered off completely when running on batteries. This is to allow the mini PC to power on automatically after a power outage. And a 2nd relay allows to power cycle the UPS or to run calibration.

ACS712 sensors paired with an ADS1115 ADC are used for current and voltage monitoring. It can handle up to 20 A. 

A pair of XL74610 ideal diodes is used instead of Schottky diodes in v1, to achieve a lower voltage drop and to allow for higher currents.

TP5100 charger module is used for charging the batteries, combined with BMS for 2S 8.4V/20A.

Alas, while everything looked good on the paper, reality was different ❌. The "better" booster module ([LM2587 version](https://www.laskakit.cz/step-up-boost-menic-lm2587--4-30v-30w/)) advertises up to 5A and 30W, but something might be wrong with it. I'm not able to pull more than 1 A from the UPS, the voltage drastically drops if I try to pull more.

Possible causes (investigating ⌛):
 - Batteries don't provide enough current? Not very probable, I'm using 3000 mAh cells from a reputable manufacturer.
 - BMS module can't handle the current? It should be able to handle 20 A but does it?
 - Booster module can't handle the current? It should be able to handle 5 A but does it?
 - Something else?

An idea: disconnect the LM2587 booster and attach an electronic load to the battery instead of it. Then try to pull whatever it takes to see if the batteries can provide the current. If they can, then the problem is with the booster. If they can't, then the problem is with the batteries or BMS.

Result: ⌛




# FIXME TODO 

---

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

Q1 is there to prevent overload of TP5100 charger. Without Q1 this charger would not only charge the batteries but it would also provide current for the output. This might overload it and/or disrupt it's charging logic.

"boosterEnable" input is there not to save power but to prevent running the XL6009 booster in an undervoltage condition. This could have been implemented using a voltage comparator (LM311?) + schmitt trigger for hysteresis. I used software solution because tbne undervoltage condition doesn't occur "suddenly" but it's only a startup condition. And using software to control it allows me to use it for powering off the UPS when it runs on battery.

# Development progress

Replaced AMS1117 with a buck converter due to a large voltage difference and therefore large heat dissipation with LDO.

Added XL6009 "EN" pin control (initial pull down + software control from ESP32).

Used Schottky diodes.

Added a diode between battery power line and XL6009 to prevent backpropagation of voltage when XL6009 is powered down.

WIP additional steps BEFORE you start soldering the modules:
 - cut ??? on the buck module and short the 3V3 pads with a solder
 - set the output voltage on LM2596 to 5V
 - set the output voltage on ??? to 12V

# TODO (obstacles)

## Hardware

~~Find out if XL6009 is OK under all circumstances, especially when powering on or with low input voltage. I measured more than 12 V on it's output in these situations!~~
Resolved by using "EN" input on XL6009 and turning it on only when measured voltage exceeds allowed threshold. 

~~Replace current defining resistors on TP5100 from 2x parallel 0.1R (resulting in 2000 mA charging current) to 2x1R (resulting in 200 mA current). This is to prevent overloading of the power source.~~
Done.

~~Disconnect XL6009 output if main power is sufficient, to prevent situations when TP5100 not only charges the batteries but it's output is also used for powering the device via booster. We don't want to overload the charger (nor the main power source).~~
Implemented by adding the Q1 which is controlled by the input voltage and is therefore closed by default.

~~Add a diode between the battery and XL6009 to prevent any voltage from the output to connect to battery.~~
Done.

Add a "reset" button for ESP (if possible).

Add a fuse to the input too.

Move the output switch behind the INA219 so that its state doesn't affect readings?

Allow to turn off the output power completely and to power cycle the device. Power P-MOSFET at the output, probably? The existing "enable" pin on the booster is not sufficient, there's always the input voltage (~8 V)present on the output if the booster is turned off. Also turning off the power completely, including the ESP32, would be great.

## Software

Fix the "booster enable", it doesn't get enabled after startup, why?

~~Report states like "charging/discharging" etc.~~
Done, in the text "state" entity.
