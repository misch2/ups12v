# UPS V4 handover — final schematic verification checkpoint

Updated 2026-10-10. Read `AGENTS.md` and this file first.

## Latest completed checkpoint — Phase 3.7 minimal emergency UART

2026-10-10 owner clarification implemented. This section supersedes all earlier six-pad/pogo-programming and RESET/BOOT/I2C-pad requirements. **Native USB Serial/JTAG is the primary and sufficient programming, serial-log and debug interface; USB-C powers USB-only MCU service.** No PCB/layout, firmware build, commit/push or hardware activity.

Only optional emergency UART group remains: TP5 ESP_TX(GPIO21), TP6 ESP_RX(GPIO20), TP7 GND, top-side pin order in that sequence,2.54mm pitch near a board edge, triangle atTP5, orientation/keying provision. Bare1.5mm copper pads only, no fitted header and no supply contact. Keep mounting-hole/routing/antenna keepouts. TP8 MCU3V3 and TP13 MAIN_3V3 are separate labeled voltage-measurement pads elsewhere, outside the UART fixture; no supply input. Removed TP9 RESET,TP10 BOOT,TP11 SDA,TP12 SCL and dedicated stubs/labels. Existing BOOT/RESET buttons remain. TP14 CE_N is retained only as a separate passive charger-domain charging-inhibit/enable bring-up probe; not part of UART. Power probes TP4 SYS,TP15 VIN1,TP16 BATTERY remain separated from logic/UART; TP17 nearJ8.

UART uses3.3V logic on an already powered target, ESP_TX→adapterRX / ESP_RX←adapterTX; adapterVCC stays disconnected, external outputs highZ while target off. Use established main/USB power. Direct GPIO pads do not add automatic powered-off injection isolation; enforce this operating constraint. No charger-domain signal or rail is added to UART, and existing isolation/power topology is unchanged.

Saved schematic SHA256 `16fbf0aa5000f4b312559aa22c4c59705b9ed9f2a34af95d4009dfc8d4ce4cb2`. Fresh KiCad10.0.7 ERC **0 errors /4 unchanged warnings**. Independent XML:152 components, all439 remaining exported pin entries preserved; exactly four pads removed. Non-pad properties and all power/USB/F5/button connections preserved. Original375 accepted Phase3.5 pins remain unchanged through the Phase3.6 baseline. F0/F5 remain one PCB and19 F5-only fitted parts. NoPCB: DRC/parity not applicable yet, required before release.

Read [current review](evidence/phase3-7-review.md), [PDF](evidence/phase3-7-final.pdf), [PNG](evidence/phase3-7-final.png), [XML](evidence/phase3-7-final.net.xml), [ERC](evidence/phase3-7-final-erc.json), [verification/hashes](evidence/phase3-7-verification.json), [population](evidence/phase3-7-population.csv). Reproduce using `python hardware/v4/evidence/verify_phase3_7.py`. BOM/variants/requirements/architecture updated. Reuse Phase3.6 power calculations and accepted footprint evidence; no power redesign occurred. The old Phase3.6 verification script describes its historical export, not the latest schematic.

Ready for owner review and a separately authorized PCB milestone in a fresh session. Existing footprint-defining harness/NTC/connector choices, Q10 courtyard and provisional sourcing remain before freeze. **VAC1 hot-plug fabrication/power-up block and BQ25792 2S default2A risk remain OPEN**. Hardware ripple/dropout/thermal/reverse-current qualification remains unperformed.

## Historical Phase 3.6 checkpoint — service-pad group superseded below

2026-10-10. This section supersedes the historical missing-F5/UART and U3 setpoint statements below. **STOP for owner review before PCB layout.** No PCB, commit/push, staging, firmware build or hardware activity performed; pre-existing project edits preserved. Title block deliberately unchanged.

- Added F5 TPS62933DRLR buck, LM74700QDBVRQ1/AON7528 reverse blocker and Phoenix1757242 output J8. SYS6–18V; nominalRAW5.04V. All19 fitted references U7/U8/Q10/L3/R60–R63/C60–C69/J8 are DNP inF0. One PCB still supports all8 charger/cell/F0/F5 plans. No F5 connection to USB/MCU; joins existing circuit only atSYS/PGND.
- Owner authorized choosing feedback by complete tolerance budget: R32 now31.6k, R33 10k, both0.1%10ppm or better, nominal3.328V. C33/C45 remain22uF but change to exact35VX5R TDK1206 parts; BOM records this footprint change. Calculated MCU1A envelope3.1416–3.4359V includes explicit assumptions; only6.6mV lower reserve. F5 calculated J8 envelope4.7871–5.2146V includes blocker/ripple/trace/regulation allocations. Neither is measured or an unconditional production guarantee.
- Added physical1.5mm copper-only TP5–TP17. Proposed top-side PCB-edge2.54mm-pitch service row TP5 TX,TP6 RX,TP7 PGND,TP8 MCU3V3 sense,TP9 RESET,TP10 BOOT; triangle atTP5 and asymmetric fixture key. TP11 SDA/TP12 SCL/TP13 MAIN3V3 form secondary group. TP14 CE_N is separate charger-domain passive access. TP15 VIN1/TP16 BATTERY/existingTP4 SYS must be separated from logic pads; TP17 nearJ8. Near-board-edge access is required; final edge setback/probe keepouts must account for routing, mounting holes and ESP32 antenna keepout during layout. No pad is a power input; fixture stays highZ until MCU3V3 valid and uses existingmain/USB supply. Do not drive unpowered MCU pins.

Saved schematic SHA256 `4b53fa435f88b5aab99067b64ff83778d152d60264b3dd2ea7cb19cba5996c47`. Fresh KiCad10.0.7 ERC **0 errors /4 existing isolated-label warnings** (MCU_STATUS_LED,MCU_GPIO1/7/10). Independent trueXML comparison:156 components; all375 retained pin nets preserved vs entry and acceptedPhase3.5. Retained property changes restricted toR32/R33/C33/C45; F5 pinmap and F0 assembly projection pass. F0 projection is not a separate ERC schematic. New area renders visually inspected, direct local wiring used. Footprint pad mappings read back; inherited Q10 external footprint lacks courtyard, to be corrected/qualified throughKonnect before footprint freeze. NoPCB: DRC/parity not applicable yet, mandatory before design release.

Read [Phase3.6 review with datasheet revisions, calculations and limitations](evidence/phase3-6-review.md), [verification/hashes](evidence/phase3-6-verification.json), [XML](evidence/phase3-6-final.net.xml), [ERC](evidence/phase3-6-final-erc.json), [footprints](evidence/phase3-6-footprints.json), [population CSV](evidence/phase3-6-population.csv), [PDF](evidence/phase3-6-final.pdf), [PNG](evidence/phase3-6-final.png), [BOM](V4_BOM_REVIEW.md), [variants](V4_VARIANTS.md). Reproduce XML checks with `python hardware/v4/evidence/verify_phase3_6.py`; no CAD source mutation.

**Recommendation:** ready for provisional schematic owner review and, once authorized, a fresh session for PCB planning/layout. Resolve footprint-defining harness/NTC/connector choices and missing Q10 courtyard before freeze. Ordinary sourcing remains PROPOSED; critical buck/controller preferred-source observations recorded, L3 preferred-source availability and feedback resistor exact orders still OPEN. Validate Ceff,6V dropout, ripple/stability, thermal/reverse-current and complete-interruption/service behavior on matching hardware after safe fabrication is authorized. Do not promote calculations to hardware evidence. **VAC1 hot-plug fabrication/power-up block and BQ25792 2S default2A risk remain OPEN.** No extra supervisor/latch/protection stage was introduced.

## Historical Phase 3.5 checkpoint — superseded where noted above

Owner provisionally accepted the simplified Phase 3.2 MCU/service-USB architecture and reviewed the preceding render. The bounded final checkpoint is complete; **STOP before PCB layout**. No commit/push, staging, firmware build or hardware activity was performed. Existing staged/unstaged work is preserved.

Final saved schematic SHA256: `9328c3cd7825f250258df43db23a69781e8b8233100587716aab51cebf4cc6ae`.
Fresh KiCad 10.0.7 ERC: **0 errors / 6 existing isolated-label warnings**. True KiCad XML: **124 components / 375 exported pin entries**, all electrical component properties and pin nets identical to the preceding LDO checkpoint. F01 VBUS bank independently asserted; 18 critical footprint identities pass, U1 footprint readback is 61 physical pads / 53 unique numbers with courtyard. No real V4 PCB: DRC/parity not applicable yet, mandatory before release.

Read [final owner-review report](evidence/phase3-5-final-review.md) for the six-state CE truth table, electrical calculations, precise limitations and small manual presentation tasks. Fresh [verification/hashes](evidence/phase3-5-verification.json), [XML](evidence/phase3-5-final.net.xml), [ERC](evidence/phase3-5-final-erc.json), [connectivity](evidence/phase3-5-connectivity.json), [footprint identities](evidence/phase3-5-footprints.json), [PDF](evidence/phase3-5-final.pdf), [PNG](evidence/phase3-5-final.png). BOM inventory refreshed from final XML, 104 groups; procurement approvals unchanged.

Presentation: seven obsolete notes removed, fourteen current headings/notes added, eleven IC/transistor field pairs repositioned through Konnect. Electrical objects unchanged. PNG visually inspected; some passive/USB label density remains. Konnect has no title-block edit: manually set title `UPS V4 - charger, power paths and ESP32-C3`, revision `V4-PROTOTYPE-P3.2-R1`, date `2026-10-10` in KiCad Page Settings. Saved title/revision are still the explicitly stale `BQ25798 UPS module` / `2.1`. Repeat ERC/XML/render/hash after manual edits.

**Recommendation:** ready for owner review, with concrete completeness items before common-PCB freeze: decide whether F5 must be included (the independent 5V converter/blocker/connector is absent; F0-only narrows documented scope), add physical UART recovery access (labels alone are insufficient), settle footprint-defining connector/NTC/harness choices and normal-buck capacitor voltage/Ceff grades. Plan power/control test access and assembly identity markings in the schematic/PCB milestone. No substantial block was silently added.

Electrical follow-up: U3 is 3.376 V nominal, calculated full-temperature static 3.299–3.454 V; only ~11 mV upper margin remains to the +5% steady requirement before ripple. Resolve that budget before supply freeze. U5 MAIN-priority boundary is nominal 2.745 V, corners ~2.493–3.003 V; regulated MAIN has static margin, dynamic no-oscillation is not measured. Q6 is an analog main-presence gate, not a precise voltage-valid comparator; MAIN decay/reset CE timing remains qualification. USB-only cold flashing, complete-interruption recovery, leakage/reverse-current and LDO thermals are not physically verified. No redesign/latch/supervisor/hold-up was added. **VAC1 fabrication/power-up block and BQ25792 2S default-2A risk remain OPEN.**

The following sections preserve the preceding electrical checkpoint and its history; the final evidence above supersedes their source hash/render/freshness claims. Recommend a fresh session for the separately authorized next milestone.

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

Current source SHA256 `9e9843a91ae49ff0df7625c0071d784ef94c42b1d690216c4c363f65051aee48`. The pre-LDO source, XML, ERC and render are preserved under `evidence/phase3-4-pre-ldo-baseline*`; its handover is [archived](evidence/phase3-4-pre-ldo-handover.md). The `phase3-4` artifact prefix distinguishes this follow-up's evidence; the approved project milestone remains Phase 3.2.

- Removed 18 candidate refs: U7/U8/U9/U10/U11/U12, Q10, D5, C41/C42/C49/C50/C51/C52, R54/R55/R56/R57. No charge latch/Schmitt/live-arm, external MAIN/MCU supervisor, TPS22975 or 470 uF hold-up remains.
- Retained U3 TPS62933 normal buck, U5 TPS2116, original non-A U6 TCA9517, isolated I2C/INT/CE, ESP32 native USB/BOOT/RESET and local bypass. U4 is now Diodes AP7361C-33E-13, SOT-223 E, with pins 1 USB_VBUS / 2 PGND / 3 USB3V3. See [bounded selection and thermal screen](evidence/phase3-4-usb-ldo-selection.md).
- Removed USB buck-only C34/C38/C44/C46/L3/R34/R38/R39 and BST_USB/SW_USB/USB_EN/USB_FB/USB_SS nets. C27 is 4.7 uF/10 V input bypass; C35 remains 22 uF output; C40 is repurposed as 100 nF output bypass. R35 is repurposed as a 10k USB3V3 bleeder (0.33 mA); it provides discharge without proving all dynamic reverse-current limits. U5/R50 stale supervisor metadata was corrected.
- U5 MODE/VIN1 stay MAIN-referenced, VIN2 USB3V3, output directly MCU3V3. R23 8.2k / new R24 4.7k (1%) feed PR1 only. Q8 gate and Q6/R50 bias now derive directly from MAIN_3V3, retaining full gate drive and keeping the comparator unloaded. Q8/Q9 isolate TCA9517 EN from its MCU-side internal pull-up.
- GPIO0 charge request passes through R46 to the distinct MCU_CHG_BASE/Q7 node with R47 pull-down. Q5/Q6/Q7 retain default-off/main-domain isolation without stored authorization. R11.2 remains service no-connect.
- Fresh ERC: **0 errors / 6 deferred isolated-label warnings** (UART RX/TX, status LED, GPIO1/7/10). Fresh true KiCad XML: 124 components. Connectivity checks found no orphan/floating/short findings or unconnected pins in the selected supply block; four existing I2C pull-up advisories remain.
- Preservation PASS against the pre-LDO baseline and accepted Phase 3.1; independent Phase 2.6 check passes all 33 projected power-stage partitions / 154 connected pins. Independent follow-up comparison checks 372 retained exported pin nets, with only C40.1 USB_SS → USB3V3, R35.1 USB_FB → USB3V3 and the declared U4 replacement map changing. No unexpected retained value, footprint or pin-net change is accepted.
- XML footprint identity check passes for 18 active references. Exact AP7361C E symbol pin map and SOT-223 duplicate pad 2/tab were read back and a disposable package fixture rendered. Existing physical land-pattern qualification limits remain; no manufactured fit claim.
- Fresh render inspected. Inherited dense label/value overlaps, Phase 3.1-only note and title/revision remain presentation issues; drawing/physical-land freeze is not granted. Documentation whitespace checks pass; the staged full diff reports three whitespace-only serialized CAD lines (two in the immutable original baseline, one in current Konnect output), retained without hand-editing CAD. No real PCB exists, so PCB DRC/parity is not applicable at this checkpoint; both remain release requirements.

Current evidence: [review report](evidence/phase3-4-usb-ldo-review.md), [true XML](evidence/phase3-4-usb-ldo.net.xml), [ERC](evidence/phase3-4-usb-ldo-erc.json), [baseline verification](evidence/phase3-4-usb-ldo-verification.json), [Phase 3.1 preservation](evidence/phase3-4-usb-ldo-preservation.json), [Phase 2.6 preservation](evidence/phase3-4-phase2-6-preservation.json), [independent final check](evidence/phase3-4-independent-review.json), [render](evidence/phase3-4-usb-ldo.png). BOM regenerated from this XML (104 groups); procurement statuses remain provisional. The [prior charge/reset simplification report](evidence/phase3-3-simplified-review.md) records that earlier intentional net delta; its USB-buck state is historical.

## Scope and remaining tests

Stop at the simplified MCU/power-domain schematic review checkpoint. No PCB layout, fabrication, purchase or power-up approval is implied.

Future matching-prototype tests: USB-only ROM flash with Wi-Fi disabled and BOOT/RESET recovery; normal and USB current/inrush and actual port current allowance; source transition/restart and recovery; main VSYS continuity during MCU reset under supported supply/load; CE startup/reset/charger-only reset and actual pack charge-current limits; I2C/GPIO partial-power leakage and transition pulses; normal buck, USB LDO and mux thermal/voltage behavior; USB unplug capacitor discharge, TPS2116 leakage and LDO reverse-current limits. The LDO screen predicts about 116.6 °C junction at 300 mA, 5.25 V input and 50 °C ambient using 110 °C/W; this is a calculation, not measured ROM demand or a new product requirement. Sustained 500 mA hot operation requires better copper/measurement; 1 A continuous USB operation is not claimed. Record exact revision/BOM, cells, adapter/cable, load, ambient and logs. These are tests to perform later, not verified behavior.

Before later PCB work, resolve the owner's phase approval and exact live board path gate. Real-board DRC/parity and ERC remain mandatory before release. Schematic ERC does not establish thermal/electrical hardware correctness.

## Earlier verified evidence and open procurement

- Phase 2.6 established F01/VBUS, charger pins 1–29 and the R12/C26 RC shunt; final ERC was 0 errors/0 warnings for that historical state. R12 2 ohm Vishay CRCW12062R00JNEAHP; C26 2.2 uF/100 V KEMET C1210C225K1RACTU; F1 Littelfuse 0451005.MRL with corrected lands. These remain provisional, not measured hot-plug protection.
- Original non-A TCA9517 revision and ESP32-C3-MINI-1-N4X footprint work are documented in the earlier evidence. Reuse only checks that remain applicable to the final netlist/footprint identity; no blanket acceptance of later CAD is inferred.
- Procurement freeze is later: exact passives/connectors/NTC/harness identities, critical-part stock and any footprint-changing alternatives remain open. Preserve valid TME/LCSC records; ordinary sourcing need not block this prototype schematic checkpoint. Konnect component catalog previously lacked its database.
- Title/revision and inherited annotation cleanup may need supported KiCad editing if Konnect lacks an operation. Do not hand-edit serialized CAD or conceal stale annotations.

Historical detail: [pre-simplification handover](evidence/phase3-2-pre-simplification-handover.md), [stopped-state snapshot](evidence/phase3-2-state-snapshot-2026-10-10.md). These describe prior states and are not current requirements or fresh acceptance evidence.
