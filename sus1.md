```
[T+  1.433s]        VBUS_ADC (int, mV) = 5213                     (was  5215)
Main stats: +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+  1.636s]        VBUS_ADC (int, mV) = 5211                     (was  5213)
Main stats: +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+  2.229s]        IINDPM_FLAG (bool) = TRUE                                                   (was false)
[T+  2.229s]        VBUS_ADC (int, mV) = 5216                     (was  5211)
Main stats: +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+  2.832s]        IINDPM_FLAG (bool) = TRUE                                                   (was false)
[T+  2.832s]        VBUS_ADC (int, mV) = 5213                     (was  5216)
Main stats: +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+  3.240s]        VBUS_ADC (int, mV) = 5209                     (was  5213)
Main stats: +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+  3.443s]             EN_HIZ (bool) = TRUE                                                   (was false)
[T+  3.443s]        ICO_ILIM (int, mA) = 500                      (was  3000)
[T+  3.443s]        IINDPM_FLAG (bool) = TRUE                                                   (was false)
[T+  3.443s]        IBAT_ADC (int, mA) = 0                        (was    -1)
[T+  3.443s]        VBUS_ADC (int, mV) = 5215                     (was  5209)
[T+  3.443s]        VAC1_ADC (int, mV) = 5200                     (was  5203)
[T+  3.443s]        VBAT_ADC (int, mV) = 16384                    (was 16378)
[T+  3.443s]        VSYS_ADC (int, mV) = 16421                    (was 16418)
Main stats: HIZ_EN! +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"
```

Čím to může být, že se sám od sebe zapnul EN_HIZ?

No, jelikož se sám od sebe změnil i ICO_ILIM (ale ICO_STAT zůstal v \[0] "ICO disabled"), tak ...???

Doc:

Reset to 0:

> (EN_HIZ) This bit will be also reset to 0, when the adapter is plugged in at VBUS

> The EN_HIZ bit is cleared automatically when the adapter is plugged in, so cycling the adapter will also force an
> immediate retry of the poor source qualification.

Set to 1:

> Alternatively, some of the faults, like VSYS_SHORT and IBUS_OCP, force the charger into HIZ mode by setting EN_HIZ=1.

> If a poor source is detected (when pulling IPOORSRC, the VBUS voltage drops below VPOORSRC), the EN_HIZ bit
> is set to 1, PG_STAT bit remains low, PG_FLAG will be set to 1, and an INT pulse will be asserted if PG_MASK
> = 0. The device will repeat the poor source qualification routine every 7 minutes until either the adapter is
> removed or the source is qualified. Each failed poor source qualification will cause EN_HIZ and PG_FLAG to
> be set to 1, and an INT pulse will be asserted if PG_MASK = 0. In the 7 minute interim between poor source
> qualification attempts, the host may set EN_HIZ = 0 to force an immediate retry of the poor source qualification.

