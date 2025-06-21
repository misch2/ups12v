```
[T+ 90.540s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+ 90.540s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+ 90.540s]         TS_ADC (float, %) = 60.059                  (was 58.887)
[T+ 90.540s]       DPLUS_ADC (int, mV) = 4                        (was     3)
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[1]"Trickle Charge" 

[T+ 94.714s]           CHG_FLAG (bool) = TRUE                                                   (was false)
[T+ 94.714s]   VBATOTG_LOW_FLAG (bool) = TRUE                                                   (was false)
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[1]"Trickle Charge"

[T+ 96.702s]           CHG_STAT (enum) = [0] "Not Charging"                                     (was [1] "Trickle Charge")
[T+ 96.702s]          VSYS_STAT (enum) = [0] "Not in VSYSMIN regulation (VBAT > VSYSMIN)"       (was [1] "In VSYSMIN regulation (VBAT < VSYSMIN)")
[T+ 96.702s]   VBATOTG_LOW_STAT (enum) = [0] "VBAT is too low to enable OTG mode"               (was [1] "VBAT is high enough to enable OTG operation")
[T+ 96.702s]      VBAT_OVP_STAT (bool) = TRUE                                                   (was false)
[T+ 96.702s]           CHG_FLAG (bool) = TRUE                                                   (was false)
Main stats: NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+ 96.958s]           CHG_STAT (enum) = [1] "Trickle Charge"                                   (was [0] "Not Charging")
[T+ 96.958s]          VSYS_STAT (enum) = [1] "In VSYSMIN regulation (VBAT < VSYSMIN)"           (was [0] "Not in VSYSMIN regulation (VBAT > VSYSMIN)")
[T+ 96.958s]   VBATOTG_LOW_STAT (enum) = [1] "VBAT is high enough to enable OTG operation"      (was [0] "VBAT is too low to enable OTG mode")
[T+ 96.958s]      VBAT_OVP_STAT (bool) = false                                                  (was TRUE)
[T+ 96.958s]   VBATOTG_LOW_FLAG (bool) = TRUE                                                   (was false)
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[1]"Trickle Charge" 

[T+ 98.198s]           CHG_STAT (enum) = [0] "Not Charging"                                     (was [1] "Trickle Charge")
[T+ 98.198s]          VSYS_STAT (enum) = [0] "Not in VSYSMIN regulation (VBAT > VSYSMIN)"       (was [1] "In VSYSMIN regulation (VBAT < VSYSMIN)")
[T+ 98.198s]   VBATOTG_LOW_STAT (enum) = [0] "VBAT is too low to enable OTG mode"               (was [1] "VBAT is high enough to enable OTG operation")
[T+ 98.198s]      VBAT_OVP_STAT (bool) = TRUE                                                   (was false)
[T+ 98.198s]           CHG_FLAG (bool) = TRUE                                                   (was false)
Main stats: NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"
```


Tady se to po připojení baterie krásně přepnulo a drželo:
```
[T+ 99.635s]  VBAT_PRESENT_STAT (enum) = [1] "VBAT present"                                     (was [0] "VBAT NOT present")
Main stats: +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging" 

[T+120.330s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+120.330s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+120.330s]        IBUS_ADC (int, mA) = 19                       (was    58)
[T+120.330s]        VBUS_ADC (int, mV) = 4814                     (was  5025)
[T+120.330s]        VAC1_ADC (int, mV) = 4799                     (was  5010)
[T+120.330s]        VAC2_ADC (int, mV) = 4800                     (was  5009)
[T+120.330s]        VBAT_ADC (int, mV) = 7922                     (was  2014)
[T+120.330s]        VSYS_ADC (int, mV) = 16130                    (was  3397)
Main stats: +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+120.586s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+120.586s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+120.586s]         TS_ADC (float, %) = 61.816                  (was 60.059)
[T+120.586s]    TDIE_ADC (float, degC) = 61.500                  (was 18.500)
[T+120.586s]       DPLUS_ADC (int, mV) = 35                       (was     4)
[T+120.586s]      DMINUS_ADC (int, mV) = 35                       (was     3)
Main stats: +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"
```

Ale po chvíli se to přepnulo zpátky do normálního režimu, což při odpojeném napájení znamená problém:
```
[T+131.261s]          EN_BACKUP (bool) = false                                                  (was TRUE)
[T+131.261s]          EN_ACDRV1 (bool) = false                                                  (was TRUE)
[T+131.261s]        ICO_ILIM (int, mA) = 500                      (was  3000)
[T+131.261s]            PG_STAT (enum) = [0] "Not in power good status"                         (was [1] "Power good")
[T+131.261s]   AC2_PRESENT_STAT (enum) = [0] "VAC2 NOT present"                                 (was [1] "VAC2 present (above present threshold)")
[T+131.261s]   AC1_PRESENT_STAT (enum) = [0] "VAC1 NOT present"                                 (was [1] "VAC1 present (above present threshold)")
[T+131.261s]  VBUS_PRESENT_STAT (enum) = [0] "VBUS NOT present"                                 (was [1] "VBUS present (above present threshold)")
[T+131.261s]          VBUS_STAT (enum) = [0] "No Input or BHOT or BCOLD in OTG mode"            (was [5] "Unknown adaptor (3A)")
[T+131.261s]      VBAT_OVP_STAT (bool) = false                                                  (was TRUE)
Main stats: NOT_PG! NO_VBUS! NO_AC1! +EN_CHG CHG=[0]"Not Charging"

[T+150.471s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+150.471s]      VBAT_OVP_STAT (bool) = TRUE                                                   (was false)
[T+150.471s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+150.471s]        IBUS_ADC (int, mA) = 0                        (was    19)
[T+150.471s]        VBUS_ADC (int, mV) = 0                        (was  4814)
[T+150.471s]        VAC1_ADC (int, mV) = 0                        (was  4799)
[T+150.471s]        VAC2_ADC (int, mV) = 0                        (was  4800)
[T+150.471s]        VBAT_ADC (int, mV) = 7989                     (was  7922)
[T+150.471s]        VSYS_ADC (int, mV) = 16194                    (was 16130)
Main stats: NOT_PG! NO_VBUS! NO_AC1! +EN_CHG CHG=[0]"Not Charging"

[T+150.738s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+150.738s]      VBAT_OVP_STAT (bool) = false                                                  (was TRUE)
[T+150.738s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+150.738s]         TS_ADC (float, %) = 61.426                  (was 61.816)
[T+150.738s]    TDIE_ADC (float, degC) = 20.000                  (was 61.500)
[T+150.738s]       DPLUS_ADC (int, mV) = 25                       (was    35)
[T+150.738s]      DMINUS_ADC (int, mV) = 25                       (was    35)
Main stats: NOT_PG! NO_VBUS! NO_AC1! +EN_CHG CHG=[0]"Not Charging"
```


Proč? Viz VBAT_OVP_STAT. Myslelo si to, že je baterka přebitá. Důvodem bylo toto, chybná startovací konfigurace:
```
[T+  0.000s]         VSYSMIN (int, mV) = 3500
[T+  0.000s]            VREG (int, mV) = 4200
[T+  0.000s]            ICHG (int, mA) = 1000
[T+  0.000s]               CELL (enum) = [0] "1S"
[T+  0.000s]           PWM_FREQ (enum) = [1] "750 kHz"
[T+  0.000s]  VBAT_PRESENT_STAT (enum) = [0] "VBAT NOT present"
```
To odpovídá PROG rezistoru 4k7, nikoli 27k:
```
Table 9-1. PROG Pin Resistance to Set Default Switching Frequency and Battery Cell Count
SWITCHING FREQUENCY CELL COUNT TYPICAL RESISTANCE AT PROG PIN
1.5 MHz 1s 3.0 kΩ
750 kHz 1s 4.7 kΩ
1.5 MHz 2s 6.04 kΩ
750 kHz 2s 8.2 kΩ
1.5 MHz 3s 10.5 kΩ
750 kHz 3s 13.7 kΩ
1.5 MHz 4s 17.4 kΩ
750 kHz 4s 27.0 kΩ
```



!!! OK !!!

Po kontrole PCB je to už OK:
```
[T+  0.000s]         VSYSMIN (int, mV) = 12000
[T+  0.000s]            VREG (int, mV) = 16800
[T+  0.000s]            ICHG (int, mA) = 1000
[T+  0.000s]               CELL (enum) = [3] "4S"
[T+  0.000s]        VBUS_ADC (int, mV) = 5064
```

Nastavení a detekce napětí z 5V taky vypadá dobře (5 V na VAC1, 12 V na SYS -- tedy přes boost converter):
```
[T+  1.435s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+  1.435s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+  1.435s]        VAC1_ADC (int, mV) = 5068                     (was  5151)
[T+  1.435s]        VAC2_ADC (int, mV) = 5064                     (was  5151)
[T+  1.435s]        VBAT_ADC (int, mV) = 266                      (was   348)
[T+  1.435s]        VSYS_ADC (int, mV) = 12269                    (was  2893)
[T+  1.435s]    TDIE_ADC (float, degC) = 30.500                  (was 12.000)
[T+  1.435s]       DPLUS_ADC (int, mV) = 0                        (was  3388)
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"
```

Po připojení baterie se mimo jiné zvedne proud IBUS na 230 mA. Napětí VBUS i VAC1 zůstávají na 5 V, nově je detekováno 16.5 V na VBAT, a zvedne se automaticky VSYS na 17.1 V:
```
[T+ 16.824s]          VSYS_STAT (enum) = [0] "Not in VSYSMIN regulation (VBAT > VSYSMIN)"       (was [1] "In VSYSMIN regulation (VBAT < VSYSMIN)")
[T+ 16.824s]   VBATOTG_LOW_STAT (enum) = [0] "VBAT is too low to enable OTG mode"               (was [1] "VBAT is high enough to enable OTG operation")

Main stats: NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+ 18.032s]  VBAT_PRESENT_STAT (enum) = [1] "VBAT present"                                     (was [0] "VBAT NOT present")
Main stats: +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+ 30.250s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+ 30.250s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+ 30.250s]        IBUS_ADC (int, mA) = 231                      (was   155)
[T+ 30.250s]        VBUS_ADC (int, mV) = 5007                     (was  5064)
[T+ 30.250s]        VAC1_ADC (int, mV) = 5003                     (was  5068)
[T+ 30.250s]        VAC2_ADC (int, mV) = 4996                     (was  5064)
[T+ 30.250s]        VBAT_ADC (int, mV) = 16474                    (was   266)
[T+ 30.250s]        VSYS_ADC (int, mV) = 17124                    (was 12269)
Main stats: +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+ 30.506s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+ 30.506s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+ 30.506s]         TS_ADC (float, %) = 84.473                  (was 84.570)
[T+ 30.506s]    TDIE_ADC (float, degC) = 46.000                  (was 30.500)
Main stats: +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+ 60.279s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+ 60.279s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+ 60.279s]        IBUS_ADC (int, mA) = 233                      (was   231)
[T+ 60.279s]        VAC2_ADC (int, mV) = 4999                     (was  4996)
[T+ 60.279s]        VBAT_ADC (int, mV) = 16477                    (was 16474)
[T+ 60.279s]        VSYS_ADC (int, mV) = 17127                    (was 17124)
Main stats: +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+ 60.525s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+ 60.525s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+ 60.525s]    TDIE_ADC (float, degC) = 48.000                  (was 46.000)
Main stats: +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+ 90.290s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+ 90.290s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+ 90.290s]        VAC1_ADC (int, mV) = 4999                     (was  5003)
[T+ 90.290s]        VAC2_ADC (int, mV) = 4995                     (was  4999)
[T+ 90.290s]        VBAT_ADC (int, mV) = 16483                    (was 16477)
[T+ 90.290s]        VSYS_ADC (int, mV) = 17133                    (was 17127)
Main stats: +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+ 90.535s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+ 90.535s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+ 90.535s]    TDIE_ADC (float, degC) = 49.000                  (was 48.000)
Main stats: +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"
```

(PMID jsem bohužel neměřil)

Po odpojení napájení:
 
- vypne se ACDRV, to je OK
- zapne se OTG, což je taky OK
- !!! VBUS_STAT se změní na [0] "No Input or BHOT or BCOLD in OTG mode", ale má to správně být [7] "In OTG mode"
- VBUS_PRESENT_STAT se správně změní na [0] "VBUS NOT present" 

??? Proč si myslí že je BHOT či BCOLD?

Ale s napětími a proudem je to horší:
IBUS klesne na 0 A (OK), VBUS na 1.5 V (OK), VBAT zůstává na 16.4 V a VSYS zůstává na 17.1 V.

Zatím OK, ale proč nejede v OTG režimu a neposkytuje napětí na VBUS?

```
[T+136.913s]          EN_BACKUP (bool) = false                                                  (was TRUE)
[T+136.913s]          DIS_ACDRV (bool) = TRUE                                                   (was false)
[T+136.913s]             EN_OTG (bool) = TRUE                                                   (was false)
[T+136.913s]          EN_ACDRV1 (bool) = false                                                  (was TRUE)
[T+136.913s]        ICO_ILIM (int, mA) = 500                      (was  3000)
[T+136.913s]            PG_STAT (enum) = [0] "Not in power good status"                         (was [1] "Power good")
[T+136.913s]   AC1_PRESENT_STAT (enum) = [0] "VAC1 NOT present"                                 (was [1] "VAC1 present (above present threshold)")
[T+136.913s]          VBUS_STAT (enum) = [0] "No Input or BHOT or BCOLD in OTG mode"            (was [5] "Unknown adaptor (3A)")
[T+136.913s]        IINDPM_FLAG (bool) = TRUE                                                   (was false)
Main stats: NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+138.973s]  VBUS_PRESENT_STAT (enum) = [0] "VBUS NOT present"                                 (was [1] "VBUS present (above present threshold)")
Main stats: NOT_PG! NO_VBUS! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+139.187s]   AC2_PRESENT_STAT (enum) = [0] "VAC2 NOT present"                                 (was [1] "VAC2 present (above present threshold)")
Main stats: NOT_PG! NO_VBUS! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+150.431s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+150.431s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+150.431s]        IBUS_ADC (int, mA) = 0                        (was   234)
[T+150.431s]        VBUS_ADC (int, mV) = 1457                     (was  5005)
[T+150.431s]        VAC1_ADC (int, mV) = 8                        (was  4990)
[T+150.431s]        VAC2_ADC (int, mV) = 1455                     (was  4997)
[T+150.431s]        VBAT_ADC (int, mV) = 16400                    (was 16485)
[T+150.431s]        VSYS_ADC (int, mV) = 16429                    (was 17130)
Main stats: NOT_PG! NO_VBUS! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+150.687s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+150.687s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+150.687s]         TS_ADC (float, %) = 84.570                  (was 84.473)
[T+150.687s]    TDIE_ADC (float, degC) = 38.000                  (was 49.000)
Main stats: NOT_PG! NO_VBUS! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"
```

Ale:
CHG_STAT pin = 4.99 v
REGN pin = 0.1 V
PMID pin = 1.43 V
BAT pin = 16.12 V

tzn. zjevně neposílá nic na výstup. Ale proč?
A proč je REGN tak nízký?

Přitom ale funguje a komunikuje přes I2C. Tzn. napětí si z baterie bere, jen na výstup nic neposílá.

