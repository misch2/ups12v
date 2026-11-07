# V4 CE control review — Phase 2 preparation

> Current authority (2026-10-11): owner accepts possible BQ25792 default2 A charging with a qualified2S1P pack of two18650 cells, including individual cells/BMS/wiring, positive current tolerance and allowed temperatures. Four cells mean4S1P, not2S2P. Retain nominal0.5 A firmware and existing hardware-default-disabled CE/domain isolation; no added0.5 A limiter, supervisor or watchdog. Architecture is CLOSED, actual pack and sequencing qualification OPEN. [Current safety report](evidence/v4-safety-design-review-2026-10-11.md) verifies SLUSDG1D April2026 reset tables and the present Q3/Q5/Q6/Q7 circuit. The Stage2.2 circuit and GPIO references below are historical; follow V4_HANDOVER.md for current CAD.

2026-10-10. Stage2.2 now implements the simple CE circuit in the saved schematic; see [current handover](V4_HANDOVER.md) and [component acceptance](V4_STAGE2_PARTS.md). The full charger/power-stage checkpoint is unfinished and **not suitable for powering hardware**. Owner direction selects default-off/open-drain control, without an external250ms watchdog/lease.

## Manufacturer basis

| Item | BQ25792 | BQ25798 |
| --- | --- | --- |
| Source | TI SLUSDG1C, Aug 2022, Rev C: §7, §8.1/8.5, §9.3.2–9.3.4.1 | TI SLUSDV2C, Jun 2026, Rev C: §5, §6.1/6.5, §7.3.2–7.3.4.1 |
| CE pin13 | HIGH disables charge; LOW requires EN_CHG enabled; must not float | Same |
| CE logic | VIH≥1.3V; VIL≤0.4V; high-level leakage≤1µA specified at1.8V | Same |
| CE absolute limit | −0.3…6V; not an operating design target | Same |
| Adapter startup | REGN starts before source qualification/converter switching | Same |
| Battery-only | REGN normally off; BATFET supplies SYS | Same |
| Reset/cell setting | 2S ICHG default2A; register reset/watchdog can restore defaults | Different defaults; must use the798 register profile |

Sources: [BQ25792 datasheet](https://www.ti.com/lit/gpn/BQ25792), [BQ25798 datasheet](https://www.ti.com/lit/ds/symlink/bq25798.pdf). BQ792 direct PDF downloads returned404; the relevant TI-indexed datasheet sections were available through search. Full downloadable BQ792 package/register comparison remains pending. Do not infer a physical pin/land match from this CE comparison.

## Candidate simple bias and sink

Candidate: diode-OR REGN and **normal main-domain3V3**, then a CE pull-up; one normally-off NMOS pulls CE to common ground. Gate driven by a non-strapping MCU charge-request GPIO, with a gate-to-ground pull-down. USB/MCU3V3 must not supply the CE pull-up. No series hardware permit or heartbeat circuit is selected. Select exact diode/FET MPNs and verify their physical pin maps before placement.

Reasoning: REGN can bias CE before adapter charging starts; normal3V3 holds CE high during battery-only operation when REGN sleeps. The OR prevents REGN feeding the normal buck output and normal3V3 feeding REGN. CE is charge control, not SYS power-path enable; SYS must start without enabling the sink. This is an engineering proposal, not measured sequencing evidence.

Calculation example, not final values:10kΩ CE pull-up gives0.52mA at5.2V before diode drop. If bias after the diode is≥2.5V and total off-state leakage is≤10µA, CE≥2.4V, above1.3V. This10µA is a proposed local bias budget, not a proven CE leakage specification at5V and not the separate USB injection budget. Select devices using maximum leakage versus voltage/temperature; confirm CE≤0.4V with the sink on and comfortable margin below6V when off.

## Required checks before CE implementation approval

- Adapter-only with absent pack: scope REGN, CE, SYS and BAT current; CE must be HIGH before charging becomes possible. Datasheet sequence supports the concept but typical delays do not prove every ramp/reset corner.
- Battery-only, then adapter insertion: normal3V3 keeps CE biased with REGN off; demonstrate no charge pulse or bootstrap deadlock. Verify both diode leakage directions and startup into a discharged normal rail.
- MCU unpowered/reset/brownout/ROM/blank firmware: gate pull-down releases sink. Verify GPIO7/module reset state and discharge timing; do not assume every software reset tristates it.
- USB-only and mixed-source removal: no DC main-domain injection through CE, gate protection, mux or other signals. A USB-powered MCU must not arm charge without a validated main source/profile.
- Software register reset/CELL change: release sink first. I²C failure or detected charger reset: release, configure/read back, then re-enable.

## Residual risk

A charger-only reset can leave the MCU sink on while BQ7922S restores2A. There is no independent250ms expiry; actual detection/recovery latency and cell current tolerance must be recorded. A hung MCU may also hold the sink until its own watchdog/reset recovery. Neither the nominal0.5A host setting nor a generic BMS proves a0.5A hardware limit. Resolve qualification against the actual pack; introduce extra hardware only if a demonstrated battery-safety need cannot be met simply.

## Saved stage2.2 implementation and limits

D3/D4 BAS116H diode-OR REGN and MAIN_3V3 into CE_BIAS. R9=10kΩ pulls CE_N HIGH; Q3 PMV16UN pulls CE_N LOW only with a gate request. R11=1kΩ feeds the gate; R10=10kΩ holds it LOW when the request floats. J4.1 is now a MAIN_3V3 input from the future normal-domain buck, J4.5 is CHG_REQ, and J2.2 is SYS. This interface is incompatible with the old V3 header. No main buck or MCU is integrated yet. Do not use USB3V3 as MAIN_3V3.

At a3.0V request, the1k/10k divider gives2.73V nominal gate drive, above the2.5V characterization point. Maximum CE pull-up current at5.2V/9.9kΩ is0.526mA. At25°C, 23mΩ gives negligible sink drop; this is a calculation, not a guaranteed full-temperature CE measurement. A conservative21µA off-state budget (20µA Q3 drain leakage plus1µA CE) drops0.212V across10.1kΩ. With3.0V main bias and0.90V diode drop, the calculated CE level is1.888V, above1.3V; this combines datasheet conditions and **does not establish a full-temperature bound**. CE leakage is specified at1.8V, diode VF here at25°C, and REGN min/max depend on operating conditions. Cold ramps, leakage at actual CE bias, GPIO reset state, rail collapse and any startup charge pulse require prototype verification. CE absolute6V is not the operating target; REGN's cited maximum5.2V leaves nominal margin.

The passive gate pull-down provides the disconnected/unpowered request default. Software/MCU reset safety still depends on the future selected GPIO and actual reset type; no GPIO7/module claim has been verified in this stage. Firmware must release CHG_REQ before reconfiguration, verify the exact charger/cell profile and read back settings before enabling. A USB-powered MCU must not assert it without a valid main source/profile.

Status: exported pin sets and ERC checked; component pins/footprints read back and disposable renders inspected. Hardware sequencing, CE thresholds across temperature and reset timing are **unverified**. BQ792 charger-only2S reset risk above remains unchanged. Ground topology is still the inherited GND/PGND split at this stopping point; its revision is pending.
