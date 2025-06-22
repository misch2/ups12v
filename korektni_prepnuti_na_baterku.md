Po připojení teplotního čidla už funguje vše:

Otestováno:
 - připojení baterie
 - odpojení původního USB
 - připojení zátěže na výstup
     - nejprve 1 A
     - pak 2 A
     - pak 3 A
     - pak 3,2 A (simulace přetížení výstupu)
- odpojení zátěže

Všechno zafungovalo!

```
[T+  0.000s]         VSYSMIN (int, mV) = 12000
[T+  0.000s]            VREG (int, mV) = 16800
[T+  0.000s]            ICHG (int, mA) = 1000
[T+  0.000s]          VINDPM (int, mV) = 4400
[T+  0.000s]          IINDPM (int, mA) = 3000
[T+  0.000s]          VBAT_LOWV (enum) = [3] "71.4%(VREG)"
[T+  0.000s]         IPRECHG (int, mA) = 120
[T+  0.000s]            REG_RST (bool) = false
[T+  0.000s]        STOP_WD_CHG (bool) = false
[T+  0.000s]           ITERM (int, mA) = 200
[T+  0.000s]               CELL (enum) = [3] "4S"
[T+  0.000s]             TRECHG (enum) = [2] "1024 ms"
[T+  0.000s]          VRECHG (int, mV) = 200
[T+  0.000s]            VOTG (int, mV) = 12000
[T+  0.000s]         PRECHG_TMR (enum) = [0] "2 hours"
[T+  0.000s]            IOTG (int, mA) = 3000
[T+  0.000s]         TOPOFF_TMR (enum) = [0] "Disabled"
[T+  0.000s]      EN_TRICHG_TMR (bool) = TRUE
[T+  0.000s]      EN_PRECHG_TMR (bool) = TRUE
[T+  0.000s]         EN_CHG_TMR (bool) = TRUE
[T+  0.000s]            CHG_TMR (enum) = [2] "12 hours"
[T+  0.000s]           TMR2X_EN (bool) = TRUE
[T+  0.000s]    EN_AUTO_IBATDIS (bool) = TRUE
[T+  0.000s]      FORCE_IBATDIS (bool) = false
[T+  0.000s]             EN_CHG (bool) = TRUE
[T+  0.000s]             EN_ICO (bool) = false
[T+  0.000s]          FORCE_ICO (bool) = false
[T+  0.000s]             EN_HIZ (bool) = false
[T+  0.000s]            EN_TERM (bool) = TRUE                                                   
[T+  0.000s]          EN_BACKUP (bool) = TRUE
[T+  0.000s]        VBUS_BACKUP (enum) = [2] "<80%(VINDPM)"
[T+  0.000s]            VAC_OVP (enum) = [0] ">26V"
[T+  0.000s]             WD_RST (bool) = false
[T+  0.000s]           WATCHDOG (enum) = [5] "40s"
[T+  0.000s]        FORCE_INDET (bool) = false
[T+  0.000s]      AUTO_INDET_EN (bool) = TRUE
[T+  0.000s]             EN_12V (bool) = false
[T+  0.000s]              EN_9V (bool) = false                                                  
[T+  0.000s]           HVDCP_EN (bool) = false
[T+  0.000s]          SDRV_CTRL (enum) = [0] "Idle"
[T+  0.000s]           SDRV_DLY (enum) = [0] "10s"
[T+  0.000s]          DIS_ACDRV (bool) = false
[T+  0.000s]             EN_OTG (bool) = false
[T+  0.000s]        PFM_OTG_DIS (bool) = false
[T+  0.000s]        PFM_FWD_DIS (bool) = false
[T+  0.000s]           WKUP_DLY (enum) = [0] "1s"
[T+  0.000s]            DIS_LDO (bool) = false
[T+  0.000s]        DIS_OTG_OOA (bool) = false
[T+  0.000s]        DIS_FWD_OOA (bool) = false                                                  
[T+  0.000s]          EN_ACDRV2 (bool) = false
[T+  0.000s]          EN_ACDRV1 (bool) = TRUE
[T+  0.000s]           PWM_FREQ (enum) = [1] "750 kHz"
[T+  0.000s]           DIS_STAT (bool) = false
[T+  0.000s]     DIS_VSYS_SHORT (bool) = false
[T+  0.000s]       DIS_VOTG_UVP (bool) = false
[T+  0.000s]   FORCE_VINDPM_DET (bool) = false
[T+  0.000s]        EN_IBUS_OCP (bool) = TRUE
[T+  0.000s]       SFET_PRESENT (bool) = false                                                  
[T+  0.000s]            EN_IBAT (bool) = false
[T+  0.000s]           IBAT_REG (enum) = [3] "Disabled"
[T+  0.000s]          EN_IINDPM (bool) = TRUE
[T+  0.000s]         EN_EXTILIM (bool) = TRUE
[T+  0.000s]           EN_BATOC (bool) = false
[T+  0.000s]            VOC_PCT (enum) = [5] "0.875"
[T+  0.000s]            VOC_DLY (enum) = [2] "2s"
[T+  0.000s]           VOC_RATE (enum) = [2] "10min"
[T+  0.000s]            EN_MPPT (bool) = false
[T+  0.000s]               TREG (enum) = [3] "120'C"
[T+  0.000s]              TSHUT (enum) = [0] "150'C"
[T+  0.000s]         VBUS_PD_EN (bool) = false
[T+  0.000s]         VAC1_PD_EN (bool) = false
[T+  0.000s]         VAC2_PD_EN (bool) = false
[T+  0.000s]     BKUP_ACFET1_ON (enum) = [0] "Idle"
[T+  0.000s]         JEITA_VSET (enum) = [3] "Set VREG to VREG-400mV (default)"
[T+  0.000s]        JEITA_ISETH (enum) = [3] "ICHG unchanged"
[T+  0.000s]        JEITA_ISETC (enum) = [1] "Set ICHG to 20%* ICHG (default)"
[T+  0.000s]            TS_COOL (enum) = [1] "10'C (default)"
[T+  0.000s]            TS_WARM (enum) = [1] "45'C (default)"
[T+  0.000s]               BHOT (enum) = [1] "60'C (default)"
[T+  0.000s]              BCOLD (enum) = [0] "-10'C (default)"                                  
[T+  0.000s]          TS_IGNORE (bool) = false
[T+  0.000s]        ICO_ILIM (int, mA) = 3000
[T+  0.000s]        IINDPM_STAT (enum) = [0] "Normal"
[T+  0.000s]        VINDPM_STAT (enum) = [0] "Normal"
[T+  0.000s]            WD_STAT (enum) = [0] "Normal"
[T+  0.000s]            PG_STAT (enum) = [1] "Power good"
[T+  0.000s]   AC2_PRESENT_STAT (enum) = [1] "VAC2 present (above present threshold)"
[T+  0.000s]   AC1_PRESENT_STAT (enum) = [1] "VAC1 present (above present threshold)"
[T+  0.000s]  VBUS_PRESENT_STAT (enum) = [1] "VBUS present (above present threshold)"
[T+  0.000s]           CHG_STAT (enum) = [0] "Not Charging"
[T+  0.000s]          VBUS_STAT (enum) = [5] "Unknown adaptor (3A)"
[T+  0.000s]     BC12_DONE_STAT (bool) = false
[T+  0.000s]           ICO_STAT (enum) = [0] "ICO disabled"
[T+  0.000s]          TREG_STAT (enum) = [0] "Normal"
[T+  0.000s]          DPDM_STAT (enum) = [0] "D+/D- detection NOT started yet or done"          
[T+  0.000s]  VBAT_PRESENT_STAT (enum) = [0] "VBAT NOT present"
[T+  0.000s]         ACRB2_STAT (bool) = false
[T+  0.000s]         ACRB1_STAT (bool) = TRUE
[T+  0.000s]      ADC_DONE_STAT (bool) = false
[T+  0.000s]          VSYS_STAT (enum) = [1] "In VSYSMIN regulation (VBAT < VSYSMIN)"
[T+  0.000s]       CHG_TMR_STAT (enum) = [0] "Normal"
[T+  0.000s]    TRICHG_TMR_STAT (enum) = [0] "Normal"
[T+  0.000s]    PRECHG_TMR_STAT (enum) = [0] "Normal"
[T+  0.000s]   VBATOTG_LOW_STAT (enum) = [1] "VBAT is high enough to enable OTG operation"
[T+  0.000s]       TS_COLD_STAT (enum) = [1] "TS in cold range"
[T+  0.000s]       TS_COOL_STAT (enum) = [0] "TS NOT in cool range"
[T+  0.000s]       TS_WARM_STAT (enum) = [0] "TS NOT in warm range"
[T+  0.000s]        TS_HOT_STAT (enum) = [0] "TS NOT in hot range"
[T+  0.000s]      IBAT_REG_STAT (bool) = false
[T+  0.000s]      VBUS_OVP_STAT (bool) = false
[T+  0.000s]      VBAT_OVP_STAT (bool) = false
[T+  0.000s]      IBUS_OCP_STAT (bool) = false
[T+  0.000s]      IBAT_OCP_STAT (bool) = false
[T+  0.000s]      CONV_OCP_STAT (bool) = false
[T+  0.000s]      VAC2_OVP_STAT (bool) = false
[T+  0.000s]      VAC1_OVP_STAT (bool) = false
[T+  0.000s]    VSYS_SHORT_STAT (bool) = false
[T+  0.000s]      VSYS_OVP_STAT (bool) = false
[T+  0.000s]       OTG_OVP_STAT (bool) = false                                                  
[T+  0.000s]       OTG_UVP_STAT (bool) = false
[T+  0.000s]         TSHUT_STAT (bool) = false
[T+  0.000s]             ADC_EN (bool) = TRUE
[T+  0.000s]           ADC_RATE (enum) = [1] "One-shot"
[T+  0.000s]         ADC_SAMPLE (enum) = [0] "15-bit"
[T+  0.000s]            ADC_AVG (enum) = [0] "No averaging"
[T+  0.000s]       ADC_AVG_INIT (bool) = false
[T+  0.000s]       IBUS_ADC_DIS (bool) = false
[T+  0.000s]       IBAT_ADC_DIS (bool) = false
[T+  0.000s]       VBUS_ADC_DIS (bool) = false
[T+  0.000s]       VBAT_ADC_DIS (bool) = false
[T+  0.000s]       VSYS_ADC_DIS (bool) = false
[T+  0.000s]         TS_ADC_DIS (bool) = false
[T+  0.000s]       TDIE_ADC_DIS (bool) = false
[T+  0.000s]      DPLUS_ADC_DIS (bool) = false
[T+  0.000s]     DMINUS_ADC_DIS (bool) = false
[T+  0.000s]       VAC2_ADC_DIS (bool) = false
[T+  0.000s]       VAC1_ADC_DIS (bool) = false
[T+  0.000s]        IBUS_ADC (int, mA) = 160
[T+  0.000s]        IBAT_ADC (int, mA) = 0
[T+  0.000s]        VBUS_ADC (int, mV) = 5039
[T+  0.000s]        VAC1_ADC (int, mV) = 5040
[T+  0.000s]        VAC2_ADC (int, mV) = 4975
[T+  0.000s]        VBAT_ADC (int, mV) = 255
[T+  0.000s]        VSYS_ADC (int, mV) = 12268
[T+  0.000s]         TS_ADC (float, %) = 84.570
[T+  0.000s]    TDIE_ADC (float, degC) = 31.000
[T+  0.000s]       DPLUS_ADC (int, mV) = 0
[T+  0.000s]      DMINUS_ADC (int, mV) = 0
[T+  0.000s]          DPLUS_DAC (enum) = [0] "HIZ"
[T+  0.000s]         DMINUS_DAC (enum) = [0] "HIZ"
[T+  0.000s]                 PN (enum) = [3] "BQ25798"
[T+  0.000s]            DEV_REV (enum) = [1] "BQ25798"
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+  1.434s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+  1.434s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+  1.434s]        VAC1_ADC (int, mV) = 5041                     (was  5040)
[T+  1.434s]        VAC2_ADC (int, mV) = 5040                     (was  4975)
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+ 30.382s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+ 30.382s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+ 30.382s]        IBUS_ADC (int, mA) = 163                      (was   160)
[T+ 30.382s]        VBUS_ADC (int, mV) = 5048                     (was  5039)
[T+ 30.382s]        VAC1_ADC (int, mV) = 5037                     (was  5041)
[T+ 30.382s]        VAC2_ADC (int, mV) = 5033                     (was  5040)
[T+ 30.382s]        VBAT_ADC (int, mV) = 260                      (was   255)
[T+ 30.382s]        VSYS_ADC (int, mV) = 12266                    (was 12268)
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging" 

[T+ 30.640s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+ 30.640s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+ 30.640s]    TDIE_ADC (float, degC) = 33.500                  (was 31.000)
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging" 

[T+ 50.881s]           CHG_STAT (enum) = [1] "Trickle Charge"                                   (was [0] "Not Charging")
[T+ 50.881s]       TS_COLD_STAT (enum) = [0] "TS NOT in cold range"                             (was [1] "TS in cold range")
[T+ 50.881s]           CHG_FLAG (bool) = TRUE                                                   (was false)
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[1]"Trickle Charge"

[T+ 51.307s]           CHG_STAT (enum) = [0] "Not Charging"                                     (was [1] "Trickle Charge")
[T+ 51.307s]       TS_COLD_STAT (enum) = [1] "TS in cold range"                                 (was [0] "TS NOT in cold range")
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[0]"Not Charging"

[T+ 51.733s]           CHG_STAT (enum) = [1] "Trickle Charge"                                   (was [0] "Not Charging")
[T+ 51.733s]       TS_COLD_STAT (enum) = [0] "TS NOT in cold range"                             (was [1] "TS in cold range")
[T+ 51.733s]           CHG_FLAG (bool) = TRUE                                                   (was false)
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[1]"Trickle Charge"

[T+ 60.477s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+ 60.477s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+ 60.477s]        IBUS_ADC (int, mA) = 192                      (was   163)
[T+ 60.477s]        VBUS_ADC (int, mV) = 4895                     (was  5048)
[T+ 60.477s]        VAC1_ADC (int, mV) = 4877                     (was  5037)
[T+ 60.477s]        VAC2_ADC (int, mV) = 4816                     (was  5033)
[T+ 60.477s]        VBAT_ADC (int, mV) = 1902                     (was   260)
[T+ 60.477s]        VSYS_ADC (int, mV) = 12091                    (was 12266)
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[1]"Trickle Charge"

[T+ 60.735s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+ 60.735s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+ 60.735s]         TS_ADC (float, %) = 60.352                  (was 84.570)
[T+ 60.735s]    TDIE_ADC (float, degC) = 38.500                  (was 33.500)
[T+ 60.735s]       DPLUS_ADC (int, mV) = 191                      (was     0)
[T+ 60.735s]      DMINUS_ADC (int, mV) = 178                      (was     0)
Main stats: VSYS_REG! NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[1]"Trickle Charge"

[T+ 65.141s]          VSYS_STAT (enum) = [0] "Not in VSYSMIN regulation (VBAT > VSYSMIN)"       (was [1] "In VSYSMIN regulation (VBAT < VSYSMIN)")
[T+ 65.141s]   VBATOTG_LOW_STAT (enum) = [0] "VBAT is too low to enable OTG mode"               (was [1] "VBAT is high enough to enable OTG operation")
Main stats: NO_VBAT! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[1]"Trickle Charge"








✅Připojení baterie:

[T+ 66.556s]        VINDPM_STAT (enum) = [1] "In VINDPM regulation or VOTG regulation"          (was [0] "Normal")
[T+ 66.556s]           CHG_STAT (enum) = [3] "Fast Charge (CC mode)"                            (was [1] "Trickle Charge")
[T+ 66.556s]  VBAT_PRESENT_STAT (enum) = [1] "VBAT present"                                     (was [0] "VBAT NOT present")
[T+ 66.556s]           CHG_FLAG (bool) = TRUE                                                   (was false)
Main stats: IN_DPM! +EN_BACKUP +EN_CHG +EN_ACDRV1 CHG=[3]"Fast Charge (CC mode)"







✅Odpojení napájení (a automatické přepnutí na baterku):

[T+ 78.734s]          DIS_ACDRV (bool) = TRUE                                                   (was false)
[T+ 78.734s]             EN_OTG (bool) = TRUE                                                   (was false)
[T+ 78.734s]          EN_ACDRV1 (bool) = false                                                  (was TRUE)
[T+ 78.734s]        ICO_ILIM (int, mA) = 500                      (was  3000)
[T+ 78.734s]            PG_STAT (enum) = [0] "Not in power good status"                         (was [1] "Power good")
[T+ 78.734s]   AC1_PRESENT_STAT (enum) = [0] "VAC1 NOT present"                                 (was [1] "VAC1 present (above present threshold)")
[T+ 78.734s]           CHG_STAT (enum) = [0] "Not Charging"                                     (was [3] "Fast Charge (CC mode)")
[T+ 78.734s]          VBUS_STAT (enum) = [7] "In OTG mode"                                      (was [5] "Unknown adaptor (3A)")
[T+ 78.734s]        IINDPM_FLAG (bool) = TRUE                                                   (was false)
[T+ 78.734s]           CHG_FLAG (bool) = TRUE                                                   (was false)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+ 79.034s]          EN_BACKUP (bool) = false                                                  (was TRUE)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

❗Teď bych si měl začít hlídat vstup, a případně znovu zapnout EN_BACKUP aby se po opětovném připojení napájení opět přepnul provoz na AC1.








✅Správně teď platí že VSYS = VBAT = 16.4 V, přičemž VBUS (=PMID) je cca 11.9 V

[T+ 90.527s]          VINDPM (int, mV) = 10500                    (was  4400)
[T+ 90.527s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+ 90.527s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+ 90.527s]        IBUS_ADC (int, mA) = -13                      (was   192)
[T+ 90.527s]        IBAT_ADC (int, mA) = -1                       (was     0)
[T+ 90.527s]        VBUS_ADC (int, mV) = 11911                    (was  4895)
[T+ 90.527s]        VAC1_ADC (int, mV) = 19                       (was  4877)
[T+ 90.527s]        VAC2_ADC (int, mV) = 11893                    (was  4816)
[T+ 90.527s]        VBAT_ADC (int, mV) = 16414                    (was  1902)
[T+ 90.527s]        VSYS_ADC (int, mV) = 16435                    (was 12091)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+ 90.805s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+ 90.805s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+ 90.805s]         TS_ADC (float, %) = 59.082                  (was 60.352)
[T+ 90.805s]    TDIE_ADC (float, degC) = 36.000                  (was 38.500)
[T+ 90.805s]       DPLUS_ADC (int, mV) = 44                       (was   191)
[T+ 90.805s]      DMINUS_ADC (int, mV) = 35                       (was   178)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+120.556s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+120.556s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+120.556s]        IBUS_ADC (int, mA) = -10                      (was   -13)
[T+120.556s]        IBAT_ADC (int, mA) = 0                        (was    -1)
[T+120.556s]        VBUS_ADC (int, mV) = 11906                    (was 11911)
[T+120.556s]        VAC2_ADC (int, mV) = 11894                    (was 11893)
[T+120.556s]        VBAT_ADC (int, mV) = 16405                    (was 16414)
[T+120.556s]        VSYS_ADC (int, mV) = 16429                    (was 16435)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+120.814s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+120.814s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+120.814s]         TS_ADC (float, %) = 54.199                  (was 59.082)
[T+120.814s]    TDIE_ADC (float, degC) = 35.500                  (was 36.000)
[T+120.814s]       DPLUS_ADC (int, mV) = 58                       (was    44)
[T+120.814s]      DMINUS_ADC (int, mV) = 46                       (was    35)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+150.572s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+150.572s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+150.572s]        VBUS_ADC (int, mV) = 11914                    (was 11906)
[T+150.572s]        VAC1_ADC (int, mV) = 24                       (was    19)
[T+150.572s]        VAC2_ADC (int, mV) = 11893                    (was 11894)
[T+150.572s]        VBAT_ADC (int, mV) = 16407                    (was 16405)
[T+150.572s]        VSYS_ADC (int, mV) = 16423                    (was 16429)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+150.830s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+150.830s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+150.830s]         TS_ADC (float, %) = 59.473                  (was 54.199)
[T+150.830s]       DPLUS_ADC (int, mV) = 47                       (was    58)
[T+150.830s]      DMINUS_ADC (int, mV) = 38                       (was    46)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"


[T+180.768s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+180.768s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+180.768s]        IBUS_ADC (int, mA) = -13                      (was   -10)
[T+180.768s]        IBAT_ADC (int, mA) = -1                       (was     0)
[T+180.768s]        VBUS_ADC (int, mV) = 11906                    (was 11914)
[T+180.768s]        VAC1_ADC (int, mV) = 20                       (was    24)
[T+180.768s]        VAC2_ADC (int, mV) = 11888                    (was 11893)
[T+180.768s]        VBAT_ADC (int, mV) = 16406                    (was 16407)
[T+180.768s]        VSYS_ADC (int, mV) = 16425                    (was 16423)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+181.036s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+181.036s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+181.036s]         TS_ADC (float, %) = 58.984                  (was 59.473)
[T+181.036s]       DPLUS_ADC (int, mV) = 43                       (was    47)
[T+181.036s]      DMINUS_ADC (int, mV) = 33                       (was    38)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+210.776s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+210.776s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+210.776s]        IBUS_ADC (int, mA) = -12                      (was   -13)
[T+210.776s]        IBAT_ADC (int, mA) = 0                        (was    -1)
[T+210.776s]        VBUS_ADC (int, mV) = 11912                    (was 11906)
[T+210.776s]        VAC1_ADC (int, mV) = 24                       (was    20)
[T+210.776s]        VAC2_ADC (int, mV) = 11893                    (was 11888)
[T+210.776s]        VBAT_ADC (int, mV) = 16399                    (was 16406)
[T+210.776s]        VSYS_ADC (int, mV) = 16422                    (was 16425)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+211.044s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+211.044s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+211.044s]         TS_ADC (float, %) = 59.570                  (was 58.984)
[T+211.044s]    TDIE_ADC (float, degC) = 36.000                  (was 35.500)
[T+211.044s]       DPLUS_ADC (int, mV) = 38                       (was    43)
[T+211.044s]      DMINUS_ADC (int, mV) = 29                       (was    33)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+240.795s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+240.795s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+240.795s]        IBUS_ADC (int, mA) = -13                      (was   -12)
[T+240.795s]        VBUS_ADC (int, mV) = 11908                    (was 11912)
[T+240.795s]        VAC1_ADC (int, mV) = 25                       (was    24)
[T+240.795s]        VAC2_ADC (int, mV) = 11891                    (was 11893)
[T+240.795s]        VBAT_ADC (int, mV) = 16408                    (was 16399)
[T+240.795s]        VSYS_ADC (int, mV) = 16421                    (was 16422)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+241.053s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+241.053s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+241.053s]         TS_ADC (float, %) = 58.496                  (was 59.570)
[T+241.053s]    TDIE_ADC (float, degC) = 36.500                  (was 36.000)
[T+241.053s]       DPLUS_ADC (int, mV) = 34                       (was    38)
[T+241.053s]      DMINUS_ADC (int, mV) = 25                       (was    29)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+270.808s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+270.808s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+270.808s]        IBAT_ADC (int, mA) = -1                       (was     0)
[T+270.808s]        VAC1_ADC (int, mV) = 26                       (was    25)
[T+270.808s]        VAC2_ADC (int, mV) = 11893                    (was 11891)
[T+270.808s]        VBAT_ADC (int, mV) = 16399                    (was 16408)
[T+270.808s]        VSYS_ADC (int, mV) = 16422                    (was 16421)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+271.066s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+271.066s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+271.066s]         TS_ADC (float, %) = 58.008                  (was 58.496)
[T+271.066s]       DPLUS_ADC (int, mV) = 36                       (was    34)
[T+271.066s]      DMINUS_ADC (int, mV) = 29                       (was    25)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+300.866s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+300.866s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+300.866s]        IBUS_ADC (int, mA) = -14                      (was   -13)
[T+300.866s]        VBUS_ADC (int, mV) = 11907                    (was 11908)
[T+300.866s]        VAC1_ADC (int, mV) = 23                       (was    26)
[T+300.866s]        VAC2_ADC (int, mV) = 11888                    (was 11893)
[T+300.866s]        VBAT_ADC (int, mV) = 16398                    (was 16399)
[T+300.866s]        VSYS_ADC (int, mV) = 16419                    (was 16422)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+301.124s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+301.124s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+301.124s]         TS_ADC (float, %) = 53.711                  (was 58.008)
[T+301.124s]    TDIE_ADC (float, degC) = 37.000                  (was 36.500)
[T+301.124s]       DPLUS_ADC (int, mV) = 37                       (was    36)
[T+301.124s]      DMINUS_ADC (int, mV) = 27                       (was    29)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+331.008s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+331.008s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+331.008s]        IBUS_ADC (int, mA) = -49                      (was   -14)
[T+331.008s]        IBAT_ADC (int, mA) = -5                       (was    -1)
[T+331.008s]        VBUS_ADC (int, mV) = 11896                    (was 11907)
[T+331.008s]        VAC1_ADC (int, mV) = 31                       (was    23)
[T+331.008s]        VAC2_ADC (int, mV) = 11880                    (was 11888)
[T+331.008s]        VBAT_ADC (int, mV) = 15770                    (was 16398)
[T+331.008s]        VSYS_ADC (int, mV) = 15766                    (was 16419)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+331.276s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+331.276s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+331.276s]         TS_ADC (float, %) = 54.785                  (was 53.711)
[T+331.276s]    TDIE_ADC (float, degC) = 36.000                  (was 37.000)
[T+331.276s]       DPLUS_ADC (int, mV) = 325                      (was    37)
[T+331.276s]      DMINUS_ADC (int, mV) = 279                      (was    27)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+349.832s]        VAC2_ADC (int, mV) = 11985                    (was 11880)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+351.039s]            ICHG (int, mA) = 950                      (was  1000)
[T+351.039s]         IPRECHG (int, mA) = 0                        (was   120)
[T+351.039s]        VAC2_ADC (int, mV) = 11880                    (was 11985)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+351.256s]            ICHG (int, mA) = 1000                     (was   950)
[T+351.256s]         IPRECHG (int, mA) = 120                      (was     0)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+355.068s]        VBUS_BACKUP (enum) = [0] "<40%(VINDPM)"                                     (was [2] "<80%(VINDPM)")
[T+355.068s]          EN_IINDPM (bool) = false                                                  (was TRUE)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+355.284s]      EN_TRICHG_TMR (bool) = false                                                  (was TRUE)
[T+355.284s]        VBUS_BACKUP (enum) = [2] "<80%(VINDPM)"                                     (was [0] "<40%(VINDPM)")
[T+355.284s]          EN_IINDPM (bool) = TRUE                                                   (was false)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+355.511s]      EN_TRICHG_TMR (bool) = TRUE                                                   (was false)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+355.716s]      EN_TRICHG_TMR (bool) = false                                                  (was TRUE)
[T+355.716s]           IBAT_REG (enum) = [0] "3A"                                               (was [3] "Disabled")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+356.933s]          VINDPM (int, mV) = 0                        (was 10500)
[T+356.933s]      EN_TRICHG_TMR (bool) = TRUE                                                   (was false)
[T+356.933s]           IBAT_REG (enum) = [3] "Disabled"                                         (was [0] "3A")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+358.160s]          VINDPM (int, mV) = 10500                    (was     0)
[T+358.160s]        EN_IBUS_OCP (bool) = false                                                  (was TRUE)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+358.375s]        EN_IBUS_OCP (bool) = TRUE                                                   (was false)
[T+358.375s]        IBAT_ADC (int, mA) = 0                        (was    -5)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+358.592s]        IBAT_ADC (int, mA) = -5                       (was     0)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+360.196s]         TS_ADC (float, %) = 0.000                   (was 54.785)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+360.402s]         JEITA_VSET (enum) = [0] "Charge Suspend"                                   (was [3] "Set VREG to VREG-400mV (default)")
[T+360.402s]         TS_ADC (float, %) = 54.785                  (was 0.000)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+360.619s]         JEITA_VSET (enum) = [3] "Set VREG to VREG-400mV (default)"                 (was [0] "Charge Suspend")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 







✅Po zvýšení zátěže (na 3 A?) se postupně zvedla teplota čipu až na 70 °C, což je ale naprosto v pohodě.


[T+362.035s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+362.035s]        IBUS_ADC (int, mA) = -178                     (was   -49)
[T+362.035s]        IBAT_ADC (int, mA) = -122                     (was    -5)
[T+362.035s]        VBUS_ADC (int, mV) = 11841                    (was 11896)
[T+362.035s]        VAC1_ADC (int, mV) = 74                       (was    31)
[T+362.035s]        VAC2_ADC (int, mV) = 11828                    (was 11880)
[T+362.035s]        VBAT_ADC (int, mV) = 14637                    (was 15770)
[T+362.035s]        VSYS_ADC (int, mV) = 14580                    (was 15766)
[T+362.035s]         TS_ADC (float, %) = 54.297                  (was 54.785)
[T+362.035s]    TDIE_ADC (float, degC) = 68.500                  (was 36.000)
[T+362.035s]       DPLUS_ADC (int, mV) = 445                      (was   325)
[T+362.035s]      DMINUS_ADC (int, mV) = 406                      (was   279)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+364.325s]        ICO_ILIM (int, mA) = 0                        (was   500)
[T+364.325s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+366.542s]               TREG (enum) = [0] "60'C"                                             (was [3] "120'C")
[T+366.542s]        ICO_ILIM (int, mA) = 500                      (was     0)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+367.758s]      EN_TRICHG_TMR (bool) = false                                                  (was TRUE)
[T+367.758s]               TREG (enum) = [3] "120'C"                                            (was [0] "60'C")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+367.975s]      EN_TRICHG_TMR (bool) = TRUE                                                   (was false)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+369.974s]             EN_CHG (bool) = false                                                  (was TRUE)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+370.180s]             EN_CHG (bool) = TRUE                                                   (was false)
[T+370.180s]         ACRB1_STAT (bool) = false                                                  (was TRUE)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+370.396s]         ACRB1_STAT (bool) = TRUE                                                   (was false)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+374.582s]        IBAT_ADC (int, mA) = 0                        (was  -122)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+374.788s]        IBAT_ADC (int, mA) = -122                     (was     0)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+388.739s]          IINDPM (int, mA) = 0                        (was  3000)
Main stats: IN_DPM! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+396.944s]          IINDPM (int, mA) = 3000                     (was     0)
[T+396.944s]           ITERM (int, mA) = 0                        (was   200)
[T+396.944s]            CHG_TMR (enum) = [0] "5 hours"                                          (was [2] "12 hours")
[T+396.944s]            EN_IBAT (bool) = TRUE                                                   (was false)
[T+396.944s]         JEITA_VSET (enum) = [0] "Charge Suspend"                                   (was [3] "Set VREG to VREG-400mV (default)")
[T+396.944s]        JEITA_ISETH (enum) = [0] "Charge Suspend"                                   (was [3] "ICHG unchanged")
[T+396.944s]               BHOT (enum) = [0] "55'C"                                             (was [1] "60'C (default)")
[T+396.944s]      VAC1_OVP_FLAG (bool) = TRUE                                                   (was false)
[T+396.944s]        VBAT_ADC (int, mV) = 0                        (was 14637)
[T+396.944s]        VSYS_ADC (int, mV) = 0                        (was 14580)
Main stats: NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+400.231s]           ITERM (int, mA) = 200                      (was     0)
[T+400.231s]             TRECHG (enum) = [0] "64 ms"                                            (was [2] "1024 ms")
[T+400.231s]            CHG_TMR (enum) = [2] "12 hours"                                         (was [0] "5 hours")
[T+400.231s]            EN_TERM (bool) = false                                                  (was TRUE)
[T+400.231s]           PWM_FREQ (enum) = [0] "1.5 MHz"                                          (was [1] "750 kHz")
[T+400.231s]            EN_IBAT (bool) = false                                                  (was TRUE)
[T+400.231s]         EN_EXTILIM (bool) = false                                                  (was TRUE)
[T+400.231s]            VOC_PCT (enum) = [0] "0.5625"                                           (was [5] "0.875")
[T+400.231s]         JEITA_VSET (enum) = [3] "Set VREG to VREG-400mV (default)"                 (was [0] "Charge Suspend")
[T+400.231s]        JEITA_ISETH (enum) = [3] "ICHG unchanged"                                   (was [0] "Charge Suspend")
[T+400.231s]               BHOT (enum) = [1] "60'C (default)"                                   (was [0] "55'C")
[T+400.231s]        IBUS_ADC (int, mA) = -186                     (was  -178)
[T+400.231s]        IBAT_ADC (int, mA) = -124                     (was  -122)
[T+400.231s]        VBUS_ADC (int, mV) = 11850                    (was 11841)
[T+400.231s]        VAC1_ADC (int, mV) = 96                       (was    74)
[T+400.231s]        VAC2_ADC (int, mV) = 11833                    (was 11828)
[T+400.231s]        VBAT_ADC (int, mV) = 29183                    (was     0)
[T+400.231s]        VSYS_ADC (int, mV) = 14345                    (was     0)
[T+400.231s]    TDIE_ADC (float, degC) = 66.500                  (was 68.500)
[T+400.231s]       DPLUS_ADC (int, mV) = 511                      (was   445)
[T+400.231s]      DMINUS_ADC (int, mV) = 473                      (was   406)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+406.602s]            ICHG (int, mA) = 0                        (was  1000)
[T+406.602s]             TRECHG (enum) = [2] "1024 ms"                                          (was [0] "64 ms")
[T+406.602s]            VOTG (int, mV) = 2800                     (was 12000)
[T+406.602s]    EN_AUTO_IBATDIS (bool) = false                                                  (was TRUE)
[T+406.602s]            EN_TERM (bool) = TRUE                                                   (was false)
[T+406.602s]           PWM_FREQ (enum) = [1] "750 kHz"                                          (was [0] "1.5 MHz")
[T+406.602s]           IBAT_REG (enum) = [0] "3A"                                               (was [3] "Disabled")
[T+406.602s]         EN_EXTILIM (bool) = TRUE                                                   (was false)
[T+406.602s]            VOC_PCT (enum) = [5] "0.875"                                            (was [0] "0.5625")
[T+406.602s]         JEITA_VSET (enum) = [0] "Charge Suspend"                                   (was [3] "Set VREG to VREG-400mV (default)")
[T+406.602s]        JEITA_ISETH (enum) = [2] "Set ICHG to 40%* ICHG"                            (was [3] "ICHG unchanged")
[T+406.602s]        JEITA_ISETC (enum) = [0] "Charge Suspend"                                   (was [1] "Set ICHG to 20%* ICHG (default)")
[T+406.602s]        ICO_ILIM (int, mA) = 0                        (was   500)
[T+406.602s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+406.602s]        VBAT_ADC (int, mV) = 14404                    (was 29183)
[T+406.602s]        VSYS_ADC (int, mV) = 14340                    (was 14345)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+407.952s]            ICHG (int, mA) = 1000                     (was     0)
[T+407.952s]            VOTG (int, mV) = 12000                    (was  2800)
[T+407.952s]    EN_AUTO_IBATDIS (bool) = TRUE                                                   (was false)
[T+407.952s]        VBUS_BACKUP (enum) = [0] "<40%(VINDPM)"                                     (was [2] "<80%(VINDPM)")
[T+407.952s]           IBAT_REG (enum) = [3] "Disabled"                                         (was [0] "3A")
[T+407.952s]        JEITA_ISETH (enum) = [3] "ICHG unchanged"                                   (was [2] "Set ICHG to 40%* ICHG")
[T+407.952s]        JEITA_ISETC (enum) = [1] "Set ICHG to 20%* ICHG (default)"                  (was [0] "Charge Suspend")
[T+407.952s]        ICO_ILIM (int, mA) = 500                      (was     0)
[T+407.952s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+408.231s]        VBUS_BACKUP (enum) = [2] "<80%(VINDPM)"                                     (was [0] "<40%(VINDPM)")
[T+408.231s]         JEITA_VSET (enum) = [3] "Set VREG to VREG-400mV (default)"                 (was [0] "Charge Suspend")
[T+408.231s]        ICO_ILIM (int, mA) = 0                        (was   500)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+409.458s]        ICO_ILIM (int, mA) = 500                      (was     0)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+411.261s]  VBAT_PRESENT_STAT (enum) = [0] "VBAT NOT present"                                 (was [1] "VBAT present")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+412.479s]            VOC_PCT (enum) = [0] "0.5625"                                           (was [5] "0.875")
[T+412.479s]  VBAT_PRESENT_STAT (enum) = [1] "VBAT present"                                     (was [0] "VBAT NOT present")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+413.705s]            VOC_PCT (enum) = [5] "0.875"                                            (was [0] "0.5625")
[T+413.705s]               TREG (enum) = [0] "60'C"                                             (was [3] "120'C")
[T+413.705s]        VSYS_ADC (int, mV) = 0                        (was 14340)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+413.932s]               TREG (enum) = [3] "120'C"                                            (was [0] "60'C")
[T+413.932s]        VSYS_ADC (int, mV) = 14340                    (was     0)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+414.149s]            VOC_DLY (enum) = [3] "5s"                                               (was [2] "2s")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+415.355s]            VOC_DLY (enum) = [2] "2s"                                               (was [3] "5s")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+416.760s]          EN_BACKUP (bool) = TRUE                                                   (was false)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+416.966s]          EN_BACKUP (bool) = false                                                  (was TRUE)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+417.370s]     DIS_VSYS_SHORT (bool) = TRUE                                                   (was false)
[T+417.370s]            VOC_PCT (enum) = [0] "0.5625"                                           (was [5] "0.875")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+417.587s]     DIS_VSYS_SHORT (bool) = false                                                  (was TRUE)
[T+417.587s]            VOC_PCT (enum) = [5] "0.875"                                            (was [0] "0.5625")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+418.003s]        VAC1_ADC (int, mV) = 0                        (was    96)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+419.209s]        VAC1_ADC (int, mV) = 96                       (was     0)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+419.416s]        VAC2_ADC (int, mV) = 0                        (was 11833)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+422.623s]        VAC2_ADC (int, mV) = 11833                    (was     0)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+423.028s]           PWM_FREQ (enum) = [0] "1.5 MHz"                                          (was [1] "750 kHz")
[T+423.028s]        VBUS_ADC (int, mV) = 11839                    (was 11850)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+423.244s]             EN_CHG (bool) = false                                                  (was TRUE)
[T+423.244s]           PWM_FREQ (enum) = [1] "750 kHz"                                          (was [0] "1.5 MHz")
[T+423.244s]        VBUS_ADC (int, mV) = 11850                    (was 11839)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+424.471s]             EN_CHG (bool) = TRUE                                                   (was false)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+426.273s]      DMINUS_ADC (int, mV) = 0                        (was   473)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+428.479s]               TREG (enum) = [0] "60'C"                                             (was [3] "120'C")
[T+428.479s]       CHG_TMR_STAT (enum) = [1] "Safety timer expired"                             (was [0] "Normal")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+428.696s]               TREG (enum) = [3] "120'C"                                            (was [0] "60'C")
[T+428.696s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+428.696s]       CHG_TMR_STAT (enum) = [0] "Normal"                                           (was [1] "Safety timer expired")
[T+428.696s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+428.696s]        IBUS_ADC (int, mA) = -173                     (was  -186)
[T+428.696s]        IBAT_ADC (int, mA) = -117                     (was  -124)
[T+428.696s]        VBUS_ADC (int, mV) = 11841                    (was 11850)
[T+428.696s]        VAC1_ADC (int, mV) = 67                       (was    96)
[T+428.696s]        VAC2_ADC (int, mV) = 11826                    (was 11833)
[T+428.696s]        VBAT_ADC (int, mV) = 14571                    (was 14404)
[T+428.696s]        VSYS_ADC (int, mV) = 14515                    (was 14340)
[T+428.696s]      DMINUS_ADC (int, mV) = 473                      (was     0)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"






❓Myslím že teď někdy byla zátěž přepnutá na 3,2 A:

[T+428.996s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+428.996s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+428.996s]         TS_ADC (float, %) = 53.906                  (was 54.297)
[T+428.996s]    TDIE_ADC (float, degC) = 68.500                  (was 66.500)
[T+428.996s]       DPLUS_ADC (int, mV) = 453                      (was   511)
[T+428.996s]      DMINUS_ADC (int, mV) = 419                      (was   473)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+429.442s]         JEITA_VSET (enum) = [0] "Charge Suspend"                                   (was [3] "Set VREG to VREG-400mV (default)")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+429.658s]         JEITA_VSET (enum) = [3] "Set VREG to VREG-400mV (default)"                 (was [0] "Charge Suspend")
Main stats: IN_DPM! NOT_PG! NO_VBUS! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+431.073s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
Main stats: IN_DPM! NOT_PG! NO_VBUS! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+431.279s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+433.485s]         TS_ADC (float, %) = 49.902                  (was 53.906)
Main stats: NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+433.691s]         TS_ADC (float, %) = 53.906                  (was 49.902)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+433.897s]           ADC_RATE (enum) = [0] "Continuous"                                       (was [1] "One-shot")
[T+433.897s]        VAC2_ADC (int, mV) = 8191                     (was 11826)
[T+433.897s]         TS_ADC (float, %) = 53.027                  (was 53.906)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+434.124s]           ADC_RATE (enum) = [1] "One-shot"                                         (was [0] "Continuous")
[T+434.124s]        VAC2_ADC (int, mV) = 11826                    (was  8191)
[T+434.124s]         TS_ADC (float, %) = 53.906                  (was 53.027)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+434.549s]         EN_EXTILIM (bool) = false                                                  (was TRUE)
[T+434.549s]           ADC_RATE (enum) = [0] "Continuous"                                       (was [1] "One-shot")
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+435.765s]            TS_COOL (enum) = [0] "5'C"                                              (was [1] "10'C (default)")
[T+435.765s]              BCOLD (enum) = [1] "-20'C"                                            (was [0] "-10'C (default)")
[T+435.765s]           ADC_RATE (enum) = [1] "One-shot"                                         (was [0] "Continuous")
[T+435.765s]         TS_ADC (float, %) = 0.000                   (was 53.906)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+436.003s]         EN_EXTILIM (bool) = TRUE                                                   (was false)
[T+436.003s]            TS_COOL (enum) = [1] "10'C (default)"                                   (was [0] "5'C")
[T+436.003s]              BCOLD (enum) = [0] "-10'C (default)"                                  (was [1] "-20'C")
[T+436.003s]         TS_ADC (float, %) = 53.906                  (was 0.000)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+458.813s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+458.813s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+458.813s]        IBUS_ADC (int, mA) = -14                      (was  -173)
[T+458.813s]        IBAT_ADC (int, mA) = -2                       (was  -117)
[T+458.813s]        VBUS_ADC (int, mV) = 11909                    (was 11841)
[T+458.813s]        VAC1_ADC (int, mV) = 19                       (was    67)
[T+458.813s]        VAC2_ADC (int, mV) = 11894                    (was 11826)
[T+458.813s]        VBAT_ADC (int, mV) = 16192                    (was 14571)
[T+458.813s]        VSYS_ADC (int, mV) = 16204                    (was 14515)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+459.081s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+459.081s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+459.081s]         TS_ADC (float, %) = 59.082                  (was 53.906)
[T+459.081s]    TDIE_ADC (float, degC) = 41.000                  (was 68.500)
[T+459.081s]       DPLUS_ADC (int, mV) = 47                       (was   453)
[T+459.081s]      DMINUS_ADC (int, mV) = 39                       (was   419)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+488.832s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+488.832s]             ADC_EN (bool) = TRUE                                                   (was false)
[T+488.832s]        IBAT_ADC (int, mA) = 0                        (was    -2)
[T+488.832s]        VBUS_ADC (int, mV) = 11908                    (was 11909)
[T+488.832s]        VAC1_ADC (int, mV) = 23                       (was    19)
[T+488.832s]        VAC2_ADC (int, mV) = 11892                    (was 11894)
[T+488.832s]        VBAT_ADC (int, mV) = 16243                    (was 16192)
[T+488.832s]        VSYS_ADC (int, mV) = 16261                    (was 16204)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging" 

[T+489.090s]      ADC_DONE_STAT (bool) = TRUE                                                   (was false)
[T+489.090s]             ADC_EN (bool) = false                                                  (was TRUE)
[T+489.090s]         TS_ADC (float, %) = 59.570                  (was 59.082)
[T+489.090s]    TDIE_ADC (float, degC) = 40.000                  (was 41.000)
[T+489.090s]       DPLUS_ADC (int, mV) = 49                       (was    47)
[T+489.090s]      DMINUS_ADC (int, mV) = 43                       (was    39)
Main stats: IN_DPM! NOT_PG! NO_AC1! +EN_OTG +EN_CHG CHG=[0]"Not Charging"

[T+505.919s]             EN_HIZ (bool) = TRUE                                                   (was false)
[T+505.919s]             EN_OTG (bool) = false                                                  (was TRUE)
[T+505.919s]           PWM_FREQ (enum) = [0] "1.5 MHz"                                          (was [1] "750 kHz")
[T+505.919s]        EN_IBUS_OCP (bool) = false                                                  (was TRUE)
[T+505.919s]           IBAT_REG (enum) = [0] "3A"                                               (was [3] "Disabled")
[T+505.919s]          EN_IINDPM (bool) = false                                                  (was TRUE)
[T+505.919s]         EN_EXTILIM (bool) = false                                                  (was TRUE)
[T+505.919s]            VOC_PCT (enum) = [0] "0.5625"                                           (was [5] "0.875")
[T+505.919s]            VOC_DLY (enum) = [0] "50ms"                                             (was [2] "2s")
[T+505.919s]           VOC_RATE (enum) = [0] "30s"                                              (was [2] "10min")
[T+505.919s]               TREG (enum) = [0] "60'C"                                             (was [3] "120'C")
[T+505.919s]         JEITA_VSET (enum) = [0] "Charge Suspend"                                   (was [3] "Set VREG to VREG-400mV (default)")
[T+505.919s]        JEITA_ISETH (enum) = [0] "Charge Suspend"                                   (was [3] "ICHG unchanged")
[T+505.919s]        JEITA_ISETC (enum) = [0] "Charge Suspend"                                   (was [1] "Set ICHG to 20%* ICHG (default)")
[T+505.919s]            TS_COOL (enum) = [0] "5'C"                                              (was [1] "10'C (default)")
[T+505.919s]            TS_WARM (enum) = [0] "40'C"                                             (was [1] "45'C (default)")
[T+505.919s]               BHOT (enum) = [0] "55'C"                                             (was [1] "60'C (default)")
[T+505.919s]        ICO_ILIM (int, mA) = 0                        (was   500)
[T+505.919s]        VINDPM_STAT (enum) = [0] "Normal"                                           (was [1] "In VINDPM regulation or VOTG regulation")
[T+505.919s]   AC2_PRESENT_STAT (enum) = [0] "VAC2 NOT present"                                 (was [1] "VAC2 present (above present threshold)")
[T+505.919s]  VBUS_PRESENT_STAT (enum) = [0] "VBUS NOT present"                                 (was [1] "VBUS present (above present threshold)")
[T+505.919s]          VBUS_STAT (enum) = [0] "No Input or BHOT or BCOLD in OTG mode"            (was [7] "In OTG mode")
[T+505.919s]  VBAT_PRESENT_STAT (enum) = [0] "VBAT NOT present"                                 (was [1] "VBAT present")
[T+505.919s]         ACRB1_STAT (bool) = false                                                  (was TRUE)
[T+505.919s]      ADC_DONE_STAT (bool) = false                                                  (was TRUE)
[T+505.919s]           ADC_RATE (enum) = [0] "Continuous"                                       (was [1] "One-shot")
[T+505.919s]        IBUS_ADC (int, mA) = 0                        (was   -14)
[T+505.919s]        VBUS_ADC (int, mV) = 0                        (was 11908)
[T+505.919s]        VAC1_ADC (int, mV) = 0                        (was    23)
[T+505.919s]        VAC2_ADC (int, mV) = 0                        (was 11892)
[T+505.919s]        VBAT_ADC (int, mV) = 0                        (was 16243)
[T+505.919s]        VSYS_ADC (int, mV) = 0                        (was 16261)
[T+505.919s]         TS_ADC (float, %) = 0.000                   (was 59.570)
[T+505.919s]    TDIE_ADC (float, degC) = 0.000                   (was 40.000)
[T+505.919s]       DPLUS_ADC (int, mV) = 0                        (was    49)
[T+505.919s]      DMINUS_ADC (int, mV) = 0                        (was    43)
[T+505.919s]                 PN (enum) = [0] "?"                                                (was [3] "BQ25798")
[T+505.919s]            DEV_REV (enum) = [0] "?"                                                (was [1] "BQ25798")
Main stats: NOT_PG! NO_VBUS! NO_AC1! NO_VBAT! CHG=[0]"Not Charging"

[T+506.401s]         VSYSMIN (int, mV) = 2500                     (was 12000)
[T+506.401s]            VREG (int, mV) = 0                        (was 16800)
[T+506.401s]            ICHG (int, mA) = 0                        (was  1000)
[T+506.401s]          VINDPM (int, mV) = 0                        (was 10500)
[T+506.401s]          IINDPM (int, mA) = 0                        (was  3000)
[T+506.401s]          VBAT_LOWV (enum) = [0] "15%(VREG)"                                        (was [3] "71.4%(VREG)")
[T+506.401s]         IPRECHG (int, mA) = 0                        (was   120)
[T+506.401s]           ITERM (int, mA) = 0                        (was   200)
[T+506.401s]               CELL (enum) = [0] "1S"                                               (was [3] "4S")
[T+506.401s]             TRECHG (enum) = [0] "64 ms"                                            (was [2] "1024 ms")
[T+506.401s]          VRECHG (int, mV) = 50                       (was   200)
[T+506.401s]            VOTG (int, mV) = 2800                     (was 12000)
[T+506.401s]            IOTG (int, mA) = 0                        (was  3000)
[T+506.401s]      EN_TRICHG_TMR (bool) = false                                                  (was TRUE)
[T+506.401s]      EN_PRECHG_TMR (bool) = false                                                  (was TRUE)
[T+506.401s]         EN_CHG_TMR (bool) = false                                                  (was TRUE)
[T+506.401s]            CHG_TMR (enum) = [0] "5 hours"                                          (was [2] "12 hours")
[T+506.401s]           TMR2X_EN (bool) = false                                                  (was TRUE)
[T+506.401s]    EN_AUTO_IBATDIS (bool) = false                                                  (was TRUE)
[T+506.401s]             EN_CHG (bool) = false                                                  (was TRUE)
[T+506.401s]             EN_HIZ (bool) = false                                                  (was TRUE)
[T+506.401s]            EN_TERM (bool) = false                                                  (was TRUE)
[T+506.401s]        VBUS_BACKUP (enum) = [0] "<40%(VINDPM)"                                     (was [2] "<80%(VINDPM)")
[T+506.401s]           WATCHDOG (enum) = [0] "Disabled"                                         (was [5] "40s")
[T+506.401s]      AUTO_INDET_EN (bool) = false                                                  (was TRUE)
[T+506.401s]          DIS_ACDRV (bool) = false                                                  (was TRUE)
Main stats: NOT_PG! NO_VBUS! NO_AC1! NO_VBAT! CHG=[0]"Not Charging" 
```
