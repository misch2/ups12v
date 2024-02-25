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

# Hardware

https://oshwlab.com/michalschwarz/12v-ups

# Development progress

Replaced AMS1117 with a buck converter due to a large voltage difference and therefore large heat dissipation with LDO.

# TODO

Find out if XL6009 is OK under all circumstances, especially when powering on or with low input voltage. I measured more than 12 V on it's output in these situations!
