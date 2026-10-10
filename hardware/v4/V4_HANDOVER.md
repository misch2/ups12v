# UPS V4 handover — final schematic verification checkpoint

Updated 2026-10-10. Read `AGENTS.md` and this file first.

## Latest completed checkpoint — final verification and presentation

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
