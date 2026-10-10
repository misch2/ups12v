# UPS V4 handover — simplified MCU/service-USB review checkpoint

Updated 2026-10-10. Read `AGENTS.md` and this file first.

## Authoritative owner decisions

The latest owner decisions govern over historical Phase 3.2 evidence. See [requirements](V4_REQUIREMENTS.md) and [architecture](V4_ARCHITECTURE.md).

- USB is only for initial programming, debugging and recovery; the USB-C port may be inside the enclosure. Routine updates use OTA. USB-only ROM flashing without adapter, battery or functioning application/charger remains mandatory.
- Occasional MCU restarts during source transitions are acceptable. Supported main UPS VSYS operation remains independent of MCU resets.
- Charging is hardware-disabled by default and enabled explicitly by firmware after successful charger/profile validation. No external 250 ms timeout, charge latch, D flip-flop, live-arm or fresh-edge authorization is required.
- Preserve safe power-domain isolation. The former 10 uA aggregate figure is a prototype measurement target, not an unconditional circuit-expansion gate; unsafe back-power and device-limit violations remain prohibited.
- BQ25792 2S charger-only reset/watchdog expiry can restore 2 A while CE remains low. This residual risk is unresolved; a software 0.5 A setting and generic BMS do not establish a hardware current ceiling.
- Supported adapters are regulated up to 20 V nominal, +5% = 21 V. No active 22 V OVP, 23 V protected ceiling or accidental 30 V adapter-survival requirement.
- **VAC1 hot-plug concern remains OPEN and blocks fabrication/power-up.** VAC1 has a 30 V absolute maximum; supported adapters can excite input/cable ringing. The hypothetical 39.725 V calculation is not a measured board peak. See [bounded assessment](evidence/phase3-vac1-review.md).

- Latest Phase 3.2 follow-up decision: U3 TPS62933 normal buck (approximately 1 A supply demand, 3 A IC margin), U4 simple service LDO, U5 TPS2116 normal-priority mux. U4 selected prototype candidate is Diodes AP7361C-33E-13, SOT-223. Wi-Fi is disabled for USB-only operation; no transition hold-up/reset supervision is reinstated.

## Exact baseline and preservation

Branch `codex/v4-phase2-power-stage`; baseline HEAD `8799b2f` (`phase 3-2`), following accepted Phase 3.1 `1c2d999` and Phase 2.6 `f6d1943`.
At task entry the index was empty and only `V4_REQUIREMENTS.md` had local owner edits to R07. Those edits are preserved. The saved schematic matched the stopped-state SHA256 `ac7e0d19e90848bf7f04c9c2aef9e4deadbb502559a12af42d7e5e65e83f4e1a`.

Only CAD target: `hardware/v4/ups_v4/ups12v_v4.kicad_sch` and its project/local libraries. No real V4 PCB exists. CAD changes use KiCad 10/Konnect. Production V2/V3, firmware and credentials are outside this change. No commit, push, tag or firmware build is required for this documentation/schematic task.

## Simplification and verification

**Historical pre-LDO simplification checkpoint below; USB-LDO follow-up is in progress. Fresh final evidence will replace this section before completion.** Fresh source SHA256 `9e35f7545424b1885a91c5742e38fe2b9884143f6b2a36cf0438da44647c83bd`.

- Removed 18 candidate refs: U7/U8/U9/U10/U11/U12, Q10, D5, C41/C42/C49/C50/C51/C52, R54/R55/R56/R57. No charge latch/Schmitt/live-arm, external MAIN/MCU supervisor, TPS22975 or 470 uF hold-up remains.
- Retained U3 SYS buck, U4 independent USB buck, U5 TPS2116, original non-A U6 TCA9517, isolated I2C/INT/CE, ESP32 native USB/BOOT/RESET and normal local bypass. USB buck retained after [bounded LDO/current/thermal comparison](evidence/phase3-3-usb-ldo-comparison.md).
- U5 MODE/VIN1 stay MAIN-referenced, VIN2 USB3V3, output directly MCU3V3. R23 8.2k / new R24 4.7k (1%) feed PR1 only. Q8 gate and Q6/R50 bias now derive directly from MAIN_3V3, retaining full gate drive and keeping the comparator unloaded. Q8/Q9 isolate TCA9517 EN from its MCU-side internal pull-up.
- GPIO0 charge request passes through R46 to the distinct MCU_CHG_BASE/Q7 node with R47 pull-down. Q5/Q6/Q7 retain default-off/main-domain isolation without stored authorization. R11.2 remains service no-connect.
- Fresh ERC: **0 errors / 6 deferred isolated-label warnings** (UART RX/TX, status LED, GPIO1/7/10). Fresh true KiCad XML: 132 components. Connectivity checks found no orphan/floating/unconnected/short findings.
- Preservation PASS against the captured unfinished baseline and accepted Phase 3.1; parent Phase 2.6 check passes all 33 projected power-stage partitions. All 394 retained exported pins remain; retained values/footprint fields are unchanged except the intentional R23 value. The report enumerates intended net changes; no unexpected change is accepted.
- XML footprint identity check passes for 17 active references; new R24 installed 0402 footprint readback resolves two pads. Existing physical land-pattern qualification limits remain; no manufactured fit claim.
- Fresh render inspected. Inherited dense label/value overlaps, Phase 3.1-only note and title/revision remain presentation issues; drawing/physical-land freeze is not granted. Git whitespace check passes. No real PCB exists, so PCB DRC/parity is not applicable at this checkpoint; both remain release requirements.

Evidence: [review report](evidence/phase3-3-simplified-review.md), [true XML](evidence/phase3-3-simplified.net.xml), [ERC](evidence/phase3-3-simplified-erc.json), [baseline verification](evidence/phase3-3-simplified-verification.json), [Phase 3.1 preservation](evidence/phase3-3-simplified-preservation.json), [Phase 2.6 preservation](evidence/phase3-3-phase2-6-preservation.json), [independent final check](evidence/phase3-3-final-independent-review.json), [render](evidence/phase3-3-simplified.png). BOM regenerated from this XML (112 groups); procurement statuses remain provisional. Old Phase 3.2 evidence is historical.

## Scope and remaining tests

Stop at the simplified MCU/power-domain schematic review checkpoint. No PCB layout, fabrication, purchase or power-up approval is implied.

Future matching-prototype tests: USB-only ROM flash and BOOT/RESET recovery; normal and USB current/inrush; source transition/restart and recovery; main VSYS continuity during MCU reset under supported supply/load; CE startup/reset/charger-only reset and actual pack charge-current limits; I2C/GPIO partial-power leakage and transition pulses; both bucks/mux thermal/voltage behavior. Record exact revision/BOM, cells, adapter/cable, load, ambient and logs. These are tests to perform later, not verified behavior.

Before later PCB work, resolve the owner's phase approval and exact live board path gate. Real-board DRC/parity and ERC remain mandatory before release. Schematic ERC does not establish thermal/electrical hardware correctness.

## Earlier verified evidence and open procurement

- Phase 2.6 established F01/VBUS, charger pins 1–29 and the R12/C26 RC shunt; final ERC was 0 errors/0 warnings for that historical state. R12 2 ohm Vishay CRCW12062R00JNEAHP; C26 2.2 uF/100 V KEMET C1210C225K1RACTU; F1 Littelfuse 0451005.MRL with corrected lands. These remain provisional, not measured hot-plug protection.
- Original non-A TCA9517 revision and ESP32-C3-MINI-1-N4X footprint work are documented in the earlier evidence. Reuse only checks that remain applicable to the final netlist/footprint identity; no blanket acceptance of later CAD is inferred.
- Procurement freeze is later: exact passives/connectors/NTC/harness identities, critical-part stock and any footprint-changing alternatives remain open. Preserve valid TME/LCSC records; ordinary sourcing need not block this prototype schematic checkpoint. Konnect component catalog previously lacked its database.
- Title/revision and inherited annotation cleanup may need supported KiCad editing if Konnect lacks an operation. Do not hand-edit serialized CAD or conceal stale annotations.

Historical detail: [pre-simplification handover](evidence/phase3-2-pre-simplification-handover.md), [stopped-state snapshot](evidence/phase3-2-state-snapshot-2026-10-10.md). These describe prior states and are not current requirements or fresh acceptance evidence.
