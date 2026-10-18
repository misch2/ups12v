# Top-view assembly and harness documentation outline — REVIEW ONLY

2026-10-18. Proposed external assembly sheet for the accepted 96×70 mm PCB. No silkscreen changes. **Component/top view**, board coordinates X30–126 increasing right, Y30–100 increasing down. Print the PCB hash, F0/F5, charger/cell profile and assembly date on the eventual sheet. Pin numbers below are the contract; a mating-face drawing must be separately labeled and checked for mirroring. Never infer cable cavity order from a flipped PCB image.

## Sheet 1: top-view locator and connector contract

Top edge, left to right: J1, J2, J3, J8, J6, J4. J7 is at the right edge; SW2 RESET is lower-left of SW1 BOOT. Keep U1 antenna/enclosure/harness keepout visible. [Pin-map CSV](assembly-pinmap-review.csv) transcribes all accepted connector pad numbers/nets and top-view coordinates, including J7 and testpoints; no CAD export was regenerated.

| Connector / top-view anchor | Exact pin contract / polarity | Keying and mate |
|---|---|---|
| J1 ADAPTER IN, pin1(43,40.38) | **1 PGND (−), 2 adapter positive before F1 (+)** at(45.5,40.38); retained 4.75–21 V input envelope, profile/power limits still apply | Molex1053131102, black/keyA, 2 positions; mate1053071202 |
| J2 SYS OUT, pin1(58,40.38) | **1 PGND (−), 2 NC, 3 SYS (+)** atX58/60.5/63; no center crimp; SYS is not a fixed12V output | Molex1053131103, black/keyA, 3 positions; mate1053071203 |
| J3 BATTERY, pin1(73,40.38) | **1 PGND (−), 2 BATTERY (+)** atX75.5; only approved2S1P/4S1P pack profile; no battery connection during assembly | Molex1053132102, natural/keyB, 2 positions; mate1053072202; XT30 only on the short pack cable |
| J8 F5 5V OUT, pin1(89,40.38) | **1 PGND (−), 2 NC, 3 F5_OUT (+)** atX89/91.5/94; no center crimp | Molex1053132103, natural/keyB, 3 positions; mate1053072203. **F0 header/harness DNP** |
| J6 NTC, pin1(104,38.5) | **1 GND, 2 TS** at(101.5,38.5). Sense-ground return, not a power return; passive NTC circuit, not a power inlet | JST S2B-XH-A-1(LF)(SN); XHP-2 mate |
| J4 INTERFACE, pin1(122.5,40) | **1 MAIN_3V3, 2 PGND, 3 I2C_SDA, 4 I2C_SCL, 5 CHG_REQ, 6 ~INT**; X122.5/120/117.5/115/112.5/110. MAIN_3V3 positive supply, not battery/SYS/5V; CHG_REQ is not direct charge authorization | JST S6B-XH-A(LF)(SN); XHP-6 mate. Exact contact/wire basket pending |
| J7 USB SERVICE, origin(117.39,83.975) | **A1/A12/B1/B12 PGND; A4/A9/B4/B9 USB_VBUS; A5 CC1; B5 CC2; A6/B6 D+; A7/B7 D−; A8/B8 NC; SH PGND** | GCT USB4085-GF-A. Native USB/ROM service; USB alone does not energize/authorize main power charging |

Use 1053002100 **tin** contacts, proposed20AWG stranded wire subject to actual OD/crimp qualification, **two contacts per power harness**: six F0 or eight F5. Do not parallel contacts, fit a center contact on J2/J8, mix tin/gold, interchange keys/colors/circuit count, or invent a common cable polarity by visual left/right. Label both cable ends with reference, rail, polarity and cell/assembly profile. The manufacturer connector current reference is not a qualified cable or protection rating.

## Sheet 2: controls and probe map

| Control/probe | Location, net and use |
|---|---|
| SW1 BOOT / DOWNLOAD | (55,94), pin1 MCU_BOOT, pin2 PGND; pulls boot strap low. Hold BOOT and pulse RESET for ROM recovery as applicable to the approved firmware/service procedure |
| SW2 RESET | (45,94), pin1 MCU_EN, pin2 PGND; resets MCU; not a battery isolation or main-power switch |
| TP5 / TP6 / TP7 | (32.5,82)/(32.5,84.54)/(32.5,87.08): UART_TX / UART_RX / PGND; 2.54mm pitch, no UART power pin. Adapter RX connects TP5 TX, adapter TX connects TP6 RX; verify3.3V logic adapter before connection |
| TP8 / TP13 | (69.5,88) MCU3V3 / (59,85) MAIN_3V3; distinct domains, measurement only |
| TP14 | (73.4,72) CE_N; passive bring-up probe, not a force-charge instruction |
| TP15 / TP16 / TP4 | (34,58) VIN1 / (76,46) BATTERY / (76,51) SYS; label positive probe points explicitly |
| TP1 / TP3 / TP7 | (72.5,81)/(58,71.5)/(32.5,87.08): PGND reference points. J6 pin1 GND is a sense-domain connection, not an alternate load return |
| TP17 | (115.5,44.5) F5_OUT; **unfed in F0**, retained copper/test pad in both |

Accessibility is accepted 2D layout evidence, not a tool/enclosure fit measurement. Do not place metal, a battery or harness over the U1 antenna region. Keep probe reach/labels visible after fitting connector bodies; TP17 identification is close to J4 artwork.

## Sheet 3: population and assembly sequence

1. Use the chosen [review population](POPULATION_REVIEW.md); always leave C20/C22/C24/C25 empty. F0 omits the19 F5 parts and J8 harness; F5 fits the19 once identities/process are resolved.
2. Review [open-via/pad cases](VIA_PAD_ASSEMBLY.md). Assemble and inspect small SMD/QFN/SOT583/AON/module joints before bulky THT connectors. Flux/hot-air/reflow and hidden-joint inspection are needed; iron-only assembly is not qualified. No paste-volume/reflow profile is frozen here.
3. Fit connectors/buttons/loop probes, check pin1/polarity/keying and unpowered mechanical seating. Owner accepted standard Nano-Fit prototype tolerance risk; do not force locating pegs, enlarge holes or treat a seating trial as manufacturer tolerance compliance.
4. Record the actual F0/F5, IC1/cell profile, exact parts/harness and inspections. Continuity/short/polarity and later powered qualification require their own approved procedure. This document does not authorize power-up.
